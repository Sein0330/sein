import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
import pandas as pd
import re

console = Console()

async def main():
    async with async_playwright() as p:
        console.print("[cyan]Menyambung ke Chrome di Windows (localhost:9222)...[/cyan]")
        
        try:
            # Konek ke Chrome Windows
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception as e:
            console.print(f"[danger]❌ Gagal konek ke Chrome: {e}[/danger]")
            console.print("Pastiin Chrome udah jalan pake flag --remote-debugging-port=9222")
            return

        contexts = browser.contexts
        if not contexts:
            console.print("[danger]Gak ada tab Chrome yang kebuka.[/danger]")
            return
            
        page = contexts[0].pages[0]
        console.print(f"[green]✅ Tersambung ke tab: {await page.title()}[/green]")
        
        # Ambil HTML
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        
        # Cari card proyek (sesuaikan nanti kalo gagal)
        jobs = soup.find_all("article")
        if not jobs:
            jobs = soup.find_all("div", class_=re.compile("job-tile|job-card"))
            
        console.print(f"[cyan]Menemukan {len(jobs)} card proyek.[/cyan]")
        
        data_proyek = []
        for job in jobs:
            title_tag = job.find("h2") or job.find("h4") or job.find("a", class_="job-title-link")
            if not title_tag: continue
            title = title_tag.get_text(strip=True)
            
            text_all = job.get_text()
            budget_match = re.search(r'\$\d+(?:\.\d{2})?', text_all)
            budget = budget_match.group(0) if budget_match else "N/A"
            
            desc_tag = job.find("p")
            desc = desc_tag.get_text(strip=True) if desc_tag else ""

            # AI Logic
            ai_model = "GPT-4o Text"
            est_cost_val = 0.01
            if any(k in desc.lower() for k in ["image", "gambar", "extract", "photo", "ocr"]):
                ai_model = "Gemini Vision / GPT-4o Vision"
                est_cost_val = 0.05
                
            if budget != "N/A":
                budget_val = float(re.sub(r'[^\d.]', '', budget))
                profit = budget_val - est_cost_val
                profit_str = f"${profit:.2f}"
            else:
                profit_str = "N/A"

            data_proyek.append({
                "Judul": title[:40] + "...",
                "Budget": budget,
                "AI": ai_model,
                "Modal": f"${est_cost_val:.2f}",
                "Profit": profit_str
            })

        if data_proyek:
            table = Table(title="Upwork Project Hunter", header_style="bold magenta")
            table.add_column("Judul", style="cyan", width=40)
            table.add_column("Budget", style="green")
            table.add_column("AI Model", style="yellow")
            table.add_column("Modal", style="red")
            table.add_column("Profit", style="bold green")

            for p in data_proyek:
                table.add_row(p["Judul"], p["Budget"], p["AI"], p["Modal"], p["Profit"])

            console.print("\n", table, "\n")
            
            df = pd.DataFrame(data_proyek)
            df.to_excel("Upwork_Hunter.xlsx", index=False)
            console.print("[bold green]✅ Data disimpan di Upwork_Hunter.xlsx[/bold green]")
        else:
            console.print("[warning]Gak ada proyek yang ketangkep.[/warning]")

if __name__ == "__main__":
    asyncio.run(main())
