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

# Setup OpenRouter Client (Kita pake model Llama-3 yang stabil & murah)
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
    You are an expert IT Project Manager. Analyze this Upwork project using the STAR method.
    Estimate the difficulty (Easy/Medium/Hard) and the AI API cost (USD) needed.
    Return ONLY a valid JSON object:
    {{
        "level": "Hard",
        "situation": "Brief context",
        "task": "What needs to be done",
        "action": "How to do it",
        "result": "Expected outcome",
        "estimated_cost_usd": 0.50
    }}
    
    Project Title: {title}
    Description: {description[:1500]}
    """
    
    try:
        response = await client.chat.completions.create(
            model="meta-llama/llama-3.1-8b-instruct", # Model berbayar murah ($0.05/1jt token)
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.3
        )
        content = response.choices[0].message.content
        
        if not content:
            return None
            
        content = content.replace("```json", "").replace("```", "").strip()
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
    except Exception as e:
        console.print(f"[warning]AI analysis failed: {e}[/warning]")
    return None

async def main():
    async with async_playwright() as p:
        console.print("[cyan]Opening browser (Stealth Mode)...[/cyan]")
        
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-dev-shm-usage"]
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        
        try:
            with open("cookies.json", "r") as f:
                raw_cookies = json.load(f)
            await context.add_cookies(clean_cookies(raw_cookies))
            console.print("[green]✅ Cookies loaded![/green]")
        except:
            console.print("[danger]❌ Failed to load cookies.json[/danger]")
            await browser.close()
            return

        page = await context.new_page()
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        keyword = Prompt.ask("\nEnter project keyword").strip()
        if not keyword:
            await browser.close()
            return
            
        console.print(f"[cyan]Searching for '{keyword}'...[/cyan]")
        await page.goto(f"https://www.upwork.com/nx/search/jobs/?q={keyword}")
        await page.wait_for_timeout(5000)
        
        cards = page.locator("article[data-test='JobTile']")
        count = await cards.count()
        console.print(f"[cyan]Found {count} projects. Starting deep analysis...[/cyan]")
        
        data_proyek = []
        for i in range(min(5, count)):
            try:
                card = cards.nth(i)
                link = card.locator("a").first
                title = await link.inner_text()
                url = await link.get_attribute("href")
                
                if not url: continue
                if not url.startswith("http"): url = "https://www.upwork.com" + url
                    
                console.print(f"[dim]Analyzing: {title[:40]}...[/dim]")
                
                detail_page = await context.new_page()
                await detail_page.goto(url)
                await detail_page.wait_for_timeout(3000)
                
                desc_el = detail_page.locator("[data-test='job-description']").first
                desc = await desc_el.inner_text() if await desc_el.count() > 0 else "No description"
                
                try:
                    budget_el = detail_page.locator("[data-test='job-type-label'] strong").first
                    budget = await budget_el.inner_text() if await budget_el.count() > 0 else "N/A"
                except:
                    budget = "N/A"
                
                # AI Analysis pake Llama-3
                console.print("[dim]  (Waiting for AI...)[/dim]")
                ai_result = await analyze_with_ai(title, desc)
                
                if ai_result:
                    data_proyek.append({
                        "Title": title[:40] + "...",
                        "Budget": budget,
                        "Level": ai_result.get("level", "-"),
                        "Est. Cost": f"${ai_result.get('estimated_cost_usd', 0.00):.2f}",
                        "Situation": ai_result.get("situation", "-")[:50] + "...",
                        "Task": ai_result.get("task", "-")[:50] + "..."
                    })
                else:
                    console.print("[dim]  AI failed, skipping.[/dim]")
                
                await detail_page.close()
                await page.wait_for_timeout(1000)
                
            except Exception as e:
                console.print(f"[warning]Skipped: {e}[/warning]")

        if data_proyek:
            table = Table(title="Upwork Deep Analysis (AI-Powered)", header_style="bold magenta")
            table.add_column("Title", style="cyan")
            table.add_column("Budget", style="green")
            table.add_column("Level", style="yellow")
            table.add_column("Est. Cost", style="red")
            table.add_column("Situation", style="blue")
            table.add_column("Task", style="magenta")
            
            for p in data_proyek:
                table.add_row(p["Title"], p["Budget"], p["Level"], p["Est. Cost"], p["Situation"], p["Task"])

            console.print("\n", table, "\n")
            
            df = pd.DataFrame(data_proyek)
            df.to_csv("Upwork_Deep_Analysis.csv", index=False)
            console.print("[bold green]✅ Deep Analysis saved to Upwork_Deep_Analysis.csv[/bold green]")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
