import asyncio
import json
import re
import html
import os
import pandas as pd
from scrapling import StealthyFetcher
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
    Return ONLY a valid JSON object with this EXACT structure:
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
                "item": "Nama Resource (contoh: VPS High-Availability, Proxy Rotating)",
                "platform_recommendation": "Platform (contoh: AWS EC2, BrightData)",
                "spec": "Spec detail (contoh: 2 vCPU, 4GB RAM)",
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
    1. JANGAN PERNAH ngasih harga $0.00 buat VPS/Server. Minimal $5/bulan.
    2. HITUNG TOTAL PROJECT COST DARI NOL. Jangan asal copy angka 150.
    3. Total biaya proyek = (Estimasi Dev (Level: Easy $20-$50, Medium $50-$150, Hard $150-$500) + Operational Cost).
    4. JSON HARUS VALID. Jangan ada trailing comma di akhir array/object.
    """
    
    try:
        response = await client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.3
        )
        content = response.choices[0].message.content
        content = content.replace("```json", "").replace("```", "").strip()
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
    except Exception as e:
        console.print(f"[warning]AI Error: {e}[/warning]")
    return None

def main():
    keyword = Prompt.ask("\nEnter project keyword").strip()
    if not keyword: return
    
    # Pake Scrapling buat nembus Cloudflare
    console.print(f"[cyan]Searching for '{keyword}' (Bypassing Cloudflare)...[/cyan]")
    
    url = f"https://www.upwork.com/nx/search/jobs/?q={keyword}"
    
    try:
        # Scrapling StealthyFetcher (Bypass Cloudflare)
        page = StealthyFetcher.fetch(url)
        soup = BeautifulSoup(page.html_content, "html.parser")
    except Exception as e:
        console.print(f"[danger]Fetch Error: {e}[/danger]")
        return

    # Cari card proyek
    jobs = soup.find_all("article", attrs={"data-test": "JobTile"})
    if not jobs:
        jobs = soup.find_all("div", class_="job-tile")
        
    console.print(f"[cyan]Found {len(jobs)} projects.[/cyan]")
    
    projects = []
    table = Table(title="Search Results", header_style="bold magenta")
    table.add_column("No", style="cyan")
    table.add_column("Title", style="green")
    table.add_column("Budget", style="yellow")
    
    for i, job in enumerate(jobs[:10]):
        title_tag = job.find("h2", class_="job-tile-title") or job.find("a")
        if not title_tag: continue
        
        title = title_tag.get_text(strip=True)
        link = title_tag.get("href") or (title_tag.find("a").get("href") if title_tag.find("a") else "")
        if link and not link.startswith("http"): link = "https://www.upwork.com" + link
        
        try:
            budget_el = job.find("li", attrs={"data-test": "job-type-label"})
            budget = budget_el.get_text(strip=True) if budget_el else "N/A"
        except: budget = "N/A"
        
        projects.append({"title": title, "url": link})
        table.add_row(str(i+1), title[:50]+"...", budget)
        
    console.print("\n", table, "\n")
    
    choice = Prompt.ask("Select project number")
    if not choice.isdigit(): return
    
    selected = projects[int(choice)-1]
    console.print(f"\n[cyan]Analyzing: {selected['title']}[/cyan]")
    
    # Fetch detail pake Scrapling lagi
    try:
        detail_page = StealthyFetcher.fetch(selected["url"])
        detail_soup = BeautifulSoup(detail_page.html_content, "html.parser")
        desc_el = detail_soup.find("div", attrs={"data-test": "job-description"})
        desc = desc_el.get_text(strip=True) if desc_el else "No description"
    except:
        desc = "Failed to fetch description."
    
    ai_result = asyncio.run(analyze_with_ai(selected["title"], desc))
    
    if ai_result:
        console.print("\n" + "="*60)
        console.print(f"[bold yellow]ANALYSIS: {selected['title']}[/bold yellow]")
        console.print("="*60)
        console.print(f"[bold cyan]Level:[/bold cyan] {ai_result.get('level')}")
        console.print(f"[bold cyan]Est. Cost:[/bold cyan] ${ai_result.get('estimated_cost_usd'):.2f}")
        console.print(f"[bold cyan]Situation:[/bold cyan] {ai_result.get('situation')}")
        console.print(f"[bold cyan]Task:[/bold cyan] {ai_result.get('task')}")
        console.print(f"[bold cyan]Action:[/bold cyan] {ai_result.get('action')}")
        console.print(f"[bold cyan]Result:[/bold cyan] {ai_result.get('result')}")
        console.print("="*60)
        console.print(f"[bold green]KESIMPULAN (Feasibility):[/bold green]\n{ai_result.get('conclusion')}\n")
        console.print(f"[bold magenta]PROMPT UNTUK DEPLOY:[/bold magenta]\n{ai_result.get('ai_prompt')}")
        console.print("="*60)
        
        console.print("[bold red]ANALISA RESOURCE & BIAYA OPERASIONAL:[/bold red]")
        resources = ai_result.get('resource_breakdown', [])
        if isinstance(resources, list):
            for res in resources:
                period = res.get("cost_period", "monthly")
                period_short = "/bln" if "month" in period else ("/thn" if "year" in period else "")
                console.print(f"  - {res.get('item')} ({res.get('platform_recommendation')})")
                console.print(f"    Spec: {res.get('spec')}")
                console.print(f"    Cost: ${res.get('estimated_cost_usd', 0):.2f}{period_short} | Reason: {res.get('reason')}")
        else:
            console.print(f"  {resources}")
            
        console.print(f"\n[bold red]TOTAL BIAYA OPERASIONAL:[/bold red] ${ai_result.get('total_operational_cost_usd', 0):.2f}")
        console.print(f"[bold red]TOTAL ESTIMASI BIAYA PROYEK:[/bold red] ${ai_result.get('total_project_cost', 0.00):.2f}")

if __name__ == "__main__":
    main()
