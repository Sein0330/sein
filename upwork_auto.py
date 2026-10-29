import asyncio
import json
import re
import html
import os
import pandas as pd
from playwright.async_api import async_playwright
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

def clean_cookies(cookies):
    cleaned = []
    for c in cookies:
        if not c.get("name") or not c.get("value"): continue
        new_c = {
            "name": c["name"], "value": c["value"],
            "domain": c.get("domain", ""), "path": c.get("path", "/"),
            "secure": c.get("secure", False), "httpOnly": c.get("httpOnly", False)
        }
        ss = str(c.get("sameSite", "")).lower()
        new_c["sameSite"] = ss.capitalize() if ss in ["strict", "lax", "none"] else "Lax"
        cleaned.append(new_c)
    return cleaned

async def analyze_with_ai(title, description):
    prompt = f"""
    You are a Senior IT Project Manager and Solutions Architect. 
    Analyze this Upwork project using the STAR method (Situation, Task, Action, Result).
    
    Provide a VERY detailed analysis in INDONESIAN LANGUAGE. Do not use placeholders.
    Return ONLY a valid JSON object:
    {{
        "level": "Hard",
        "situation": "Detailed context of why the client needs this.",
        "task": "Detailed technical breakdown of what needs to be built.",
        "action": "Step-by-step technical approach (libraries, APIs, architecture).",
        "result": "Expected business outcome for the client.",
        "estimated_cost_usd": 1.50,
        "reasoning": "Why this cost?"
    }}
    
    Project Title: {title}
    Description: {description[:2000]}
    """
    
    try:
        console.print("[dim]  (AI is analyzing deeply, please wait 10-20 seconds...)[/dim]")
        response = await client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800, # Token lebih banyak buat detail
            temperature=0.4
        )
        content = response.choices[0].message.content
        
        if not content: return None
            
        content = content.replace("```json", "").replace("```", "").strip()
        
        # Ambil JSON pake regex
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            raw_json = json_match.group(0)
            try:
                return json.loads(raw_json)
            except json.JSONDecodeError as e:
                console.print(f"[warning]Raw JSON Error: {e}[/warning]")
                # Coba bersihin control character
                clean_json = re.sub(r'[\x00-\x1F\x7F]', ' ', raw_json)
                try:
                    return json.loads(clean_json)
                except Exception as e2:
                    console.print(f"[danger]Failed to parse JSON: {e2}[/danger]")
                    console.print(f"[dim]Raw output: {content[:200]}...[/dim]")
        else:
            console.print("[warning]No JSON found in AI response.[/warning]")
    except Exception as e:
        console.print(f"[warning]AI analysis failed: {e}[/warning]")
    return None

async def main():
    async with async_playwright() as p:
        console.print("[cyan]Opening browser (Stealth Mode)...[/cyan]")
        browser = await p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled", "--no-sandbox"])
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            with open("cookies.json", "r") as f:
                raw_cookies = json.load(f)
            await context.add_cookies(clean_cookies(raw_cookies))
        except:
            console.print("[danger]❌ Failed to load cookies.json[/danger]")
            await browser.close()
            return

        page = await context.new_page()
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        keyword = Prompt.ask("\nEnter project keyword").strip()
        if not keyword: return
            
        console.print(f"[cyan]Searching for '{keyword}'...[/cyan]")
        await page.goto(f"https://www.upwork.com/nx/search/jobs/?q={keyword}")
        await page.wait_for_timeout(5000)
        
        # 1. Tampilin Daftar Proyek Dulu
        cards = page.locator("article[data-test='JobTile']")
        count = await cards.count()
        
        projects = []
        table = Table(title="Search Results", header_style="bold magenta")
        table.add_column("No", style="cyan")
        table.add_column("Title", style="green")
        table.add_column("Budget", style="yellow")
        
        for i in range(min(10, count)):
            card = cards.nth(i)
            link = card.locator("a").first
            title = await link.inner_text()
            url = await link.get_attribute("href")
            if not url.startswith("http"): url = "https://www.upwork.com" + url
            
            try:
                budget_el = card.locator("[data-test='job-type-label'] strong").first
                budget = await budget_el.inner_text() if await budget_el.count() > 0 else "N/A"
            except: budget = "N/A"
            
            projects.append({"title": title, "url": url})
            table.add_row(str(i+1), title[:50]+"...", budget)
            
        console.print("\n", table, "\n")
        
        # 2. Minta User Pilih
        choice = Prompt.ask("Select project number to Deep Analyze (or 'SKIP' to exit)")
        if choice.upper() == "SKIP" or not choice.isdigit(): 
            await browser.close()
            return
            
        selected = projects[int(choice)-1]
        console.print(f"\n[cyan]Opening: {selected['title']}[/cyan]")
        
        # 3. Buka Proyek & Analisa AI
        detail_page = await context.new_page()
        await detail_page.goto(selected["url"])
        await detail_page.wait_for_timeout(3000)
        
        desc_el = detail_page.locator("[data-test='job-description']").first
        desc = await desc_el.inner_text() if await desc_el.count() > 0 else "No description"
        
        ai_result = await analyze_with_ai(selected["title"], desc)
        
        if ai_result:
            # 4. Tampilin Hasil Detail
            console.print("\n" + "="*60)
            console.print(f"[bold yellow]DEEP ANALYSIS: {selected['title']}[/bold yellow]")
            console.print("="*60)
            console.print(f"[bold cyan]Level:[/bold cyan] {ai_result.get('level')}")
            console.print(f"[bold cyan]Est. Cost:[/bold cyan] ${ai_result.get('estimated_cost_usd'):.2f}")
            console.print(f"[bold cyan]Situation:[/bold cyan] {ai_result.get('situation')}")
            console.print(f"[bold cyan]Task:[/bold cyan] {ai_result.get('task')}")
            console.print(f"[bold cyan]Action:[/bold cyan] {ai_result.get('action')}")
            console.print(f"[bold cyan]Result:[/bold cyan] {ai_result.get('result')}")
            console.print("="*60 + "\n")
            
            # Simpen ke CSV
            df = pd.DataFrame([{
                "Title": selected["title"],
                "Level": ai_result.get('level'),
                "Est. Cost": f"${ai_result.get('estimated_cost_usd'):.2f}",
                "Situation": ai_result.get('situation'),
                "Task": ai_result.get('task'),
                "Action": ai_result.get('action'),
                "Result": ai_result.get('result')
            }])
            df.to_csv("Upwork_Deep_Analysis.csv", index=False)
            console.print("[green]✅ Saved to Upwork_Deep_Analysis.csv[/green]")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
