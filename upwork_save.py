import asyncio
import json
import re
import os
import difflib
import glob
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()
console = Console()

client = AsyncOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY", ""),
    base_url="https://openrouter.ai/api/v1"
)

async def analyze_with_ai(title, description):
    prompt = f"""
    Analyze this Upwork project using the STAR method (Situation, Task, Action, Result).
    Provide a VERY detailed analysis in INDONESIAN LANGUAGE. Do not use placeholders.
    Return ONLY a valid JSON object:
    {{
        "level": "Hard",
        "situation": "Detailed context of why the client needs this.",
        "task": "Detailed technical breakdown of what needs to be built.",
        "action": "Step-by-step technical approach (libraries, APIs, architecture).",
        "result": "Expected business outcome for the client.",
        "estimated_cost_usd": X.XX,
        "conclusion": "Apakah proyek ini bisa dikerjakan oleh freelancer yang dibantu AI? Jelaskan bagian tersulitnya.",
        "ai_prompt": "Buatkan prompt super detail yang bisa di-copy-paste ke Claude/GPT untuk men-generate struktur kode/scaffolding proyek ini.",
        "resource_breakdown": [
            {{
                "item": "Nama Resource",
                "platform_recommendation": "Platform",
                "spec": "Spec detail",
                "estimated_cost_usd": X.XX,
                "cost_period": "monthly / yearly / one-time",
                "reason": "Alasan kenapa butuh resource ini"
            }}
        ],
        "total_operational_cost_usd": X.XX,
        "total_project_cost": X.XX
    }}
    
    Title: {title}
    Desc: {description[:1500]}
    
    ATURAN KETAT:
    1. JANGAN ngasih harga $0.00 buat VPS/Server. Minimal $5/bulan.
    2. HITUNG TOTAL PROJECT COST DARI NOL.
    3. JSON HARUS VALID. Jangan ada trailing comma.
    """
    
    try:
        response = await client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.3
        )
        content = response.choices[0].message.content
        content = content.replace("```json", "").replace("```", "").strip()
        
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            raw_json = json_match.group(0)
            raw_json = re.sub(r',\s*([\]}])', r'\1', raw_json)
            try:
                return json.loads(raw_json)
            except json.JSONDecodeError as e:
                console.print(f"[warning]JSON Parse Error: {e}[/warning]")
                return None
    except Exception as e:
        console.print(f"[warning]AI Error: {e}[/warning]")
    return None

def extract_data_from_search(soup):
    data_list = {}
    jobs = soup.find_all("article", attrs={"data-test": "JobTile"}) or soup.find_all("div", class_="job-tile")
    
    for job in jobs:
        title_tag = job.find("h2", class_="job-tile-title") or job.find("a")
        if not title_tag: continue
        title = title_tag.get_text(strip=True)
        
        budget_el = job.find("li", attrs={"data-test": "job-type-label"})
        budget = budget_el.get_text(strip=True) if budget_el else "N/A"
        
        spend_el = job.find("li", attrs={"data-test": "total-spent"})
        spend = spend_el.get_text(strip=True) if spend_el else "N/A"
        
        posted_el = job.find("small", attrs={"data-test": "job-pubilshed-date"})
        posted = posted_el.get_text(strip=True) if posted_el else "N/A"
        
        status = "SAFE TO BID"
        reason = "-"
        if "50+" in posted or "20 to 50" in posted:
            status = "SKIP"
            reason = "High Competition"
        elif spend == "N/A" or "$0spent" in spend.lower():
            status = "SKIP"
            reason = "Client UNVERIFIED"
            
        # Simpen data pake judul sebagai key (lowercase)
        data_list[title.lower()] = {
            "budget": budget, "spend": spend, "posted": posted,
            "status": status, "reason": reason
        }
    return data_list

def main():
    folder_path = "/home/almaarij/sein/Bahan Analisa HTML"
    files = glob.glob(f"{folder_path}/*.html")
    
    if not files:
        console.print("[danger]❌ No HTML files found![/danger]")
        return
        
    files.sort()

    search_data = {}
    detail_projects = []
    
    # 1. Bedah semua file
    for f in files:
        with open(f, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file.read(), "html.parser")
            
        page_title = soup.find("title")
        title_text = page_title.get_text(strip=True) if page_title else ""
        
        if "Search Freelance Jobs" in title_text or "Search Results" in title_text:
            # Update data search (jika ada 2 file search, yang terakhir di-loop akan menimpa yang pertama)
            search_data.update(extract_data_from_search(soup))
        else:
            title_tag = soup.find("h1") or soup.find("h2", class_="job-title")
            if title_tag:
                title = title_tag.get_text(strip=True)
            else:
                title = title_text.replace("- Upwork", "").strip()
                
            if title and len(title) > 3:
                detail_projects.append({"file": f, "title": title, "soup": soup})

    if not detail_projects:
        console.print("[danger]❌ Gak ada file detail proyek![/danger]")
        return

    # 2. Tampilin Tabel
    table = Table(title="Available Projects", header_style="bold magenta")
    table.add_column("No", style="cyan", justify="right")
    table.add_column("Title", style="green")
    table.add_column("Budget", style="yellow")
    table.add_column("Spend", style="blue")
    table.add_column("Posted", style="magenta")
    table.add_column("Status", style="bold")
    
    valid_projects = []
    
    for p in detail_projects:
        # COCOKIN DATA PAKE JUDUL (Fuzzy Matching)
        matched = {"budget": "N/A", "spend": "N/A", "posted": "N/A", "status": "-", "reason": "-"}
        
        # Cari judul di search_data yang mirip (Pake difflib)
        best_match_ratio = 0
        for s_title, data in search_data.items():
            ratio = difflib.SequenceMatcher(None, p["title"].lower(), s_title).ratio()
            if ratio > best_match_ratio:
                best_match_ratio = ratio
                matched = data
                
        # Kalo kemiripannya kurang dari 60%, anggap gak match
        if best_match_ratio < 0.6:
            matched = {"budget": "N/A", "spend": "N/A", "posted": "N/A", "status": "-", "reason": "-"}
                
        # Kalo gak ketemu sama sekali, tetep tampilin tapi N/A
        # (Biar lu tau kalo ada file detail yang gak ada di search)
        if matched["budget"] != "N/A":
            valid_projects.append(p)
            
            status_str = f"[green]{matched['status']}[/green]" if matched['status'] == "SAFE TO BID" else f"[red]{matched['status']}[/red]"
            if matched['reason'] != "-":
                status_str += f" ({matched['reason']})"
                
            table.add_row(str(len(valid_projects)), p["title"][:40]+"...", matched["budget"], matched["spend"], matched["posted"][:15], status_str)
        
    console.print("\n", table, "\n")
    
    choice = Prompt.ask("[bold yellow]Select project number to analyze[/bold yellow]")
    if not choice.isdigit() or int(choice) > len(valid_projects): return
    
    selected = valid_projects[int(choice)-1]
    
    # Ambil Deskripsi
    desc_el = selected["soup"].find("div", attrs={"data-test": "job-description"}) or selected["soup"].find("div", class_="job-description")
    desc = desc_el.get_text(strip=True) if desc_el else "No description"
    
    console.print(f"\n[cyan]Analyzing: {selected['title']}...[/cyan]")
    
    ai_result = asyncio.run(analyze_with_ai(selected["title"], desc))
    
    if ai_result:
        print("\n" + "="*60)
        print(f"ANALYSIS: {selected['title']}")
        print("="*60)
        print(f"Level: {ai_result.get('level')}")
        print(f"Est. Cost: ${ai_result.get('estimated_cost_usd'):.2f}")
        print(f"\nSituation:\n{ai_result.get('situation')}\n")
        print(f"Task:\n{ai_result.get('task')}\n")
        print(f"Action:\n{ai_result.get('action')}\n")
        print(f"Result:\n{ai_result.get('result')}\n")
        print("="*60)
        print(f"KESIMPULAN:\n{ai_result.get('conclusion')}\n")
        print(f"PROMPT UNTUK DEPLOY:\n{ai_result.get('ai_prompt')}\n")
        print("="*60)
        
        print("ANALISA RESOURCE:")
        resources = ai_result.get('resource_breakdown', [])
        if isinstance(resources, list):
            for res in resources:
                period = res.get("cost_period", "monthly")
                period_short = "/bln" if "month" in period else ("/thn" if "year" in period else "")
                print(f"- {res.get('item')} ({res.get('platform_recommendation')})")
                print(f"  Spec: {res.get('spec')}")
                print(f"  Cost: ${res.get('estimated_cost_usd', 0):.2f}{period_short} | Reason: {res.get('reason')}")
        else:
            print(f"{resources}")
            
        print(f"\nTOTAL BIAYA OPERASIONAL: ${ai_result.get('total_operational_cost_usd', 0):.2f}")
        print(f"TOTAL ESTIMASI BIAYA PROYEK: ${ai_result.get('total_project_cost', 0.00):.2f}")
        print("="*60)

if __name__ == "__main__":
    main()
