import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
import pandas as pd
import re
import html

console = Console()

async def main():
    async with async_playwright() as p:
        console.print("[cyan]Menyambung ke Chrome Debug di Windows...[/cyan]")
        
        try:
            # Konek ke Chrome yang udah jalan di port 9222
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception as e:
            console.print(f"[danger]❌ Gagal konek: {e}[/danger]")
            console.print("Pastiin Chrome udah jalan pake flag --remote-debugging-port=9222")
            return

        contexts = browser.contexts
        if not contexts:
            console.print("[danger]Gak ada tab Chrome yang kebuka.[/danger]")
            return
            
        page = contexts[0].pages[0]
        console.print(f"[green]✅ Tersambung ke tab: {await page.title()}[/green]")
        
        # Minta keyword ke user
        keyword = input("\nMasukkan keyword proyek (contoh: data entry): ").strip()
        if not keyword: return
        
        console.print(f"[cyan]Mencari proyek '{keyword}'...[/cyan]")
        await page.goto(f"https://www.upwork.com/nx/search/jobs/?q={keyword}")
        await page.wait_for_timeout(5000)
        
        # Ambil HTML
        html_content = await page.content()
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Parse card proyek
        jobs = soup.find_all("div", attrs={"data-test": "job-tile"})
        console.print(f"[cyan]Menemukan {len(jobs)} card proyek.[/cyan]")
        
        data_proyek = []
        for job in jobs:
            title_tag = job.find("h3", attrs={"data-test": "job-title"})
            if not title_tag: continue
            title = html.unescape(title_tag.get_text(strip=True))
            
            text_all = job.get_text()
            budget_match = re.search(r'(Hourly|Fixed-price):\s*(\$\d+(?:-\$\d+)?(?:\.\d{2})?)', text_all)
            budget = budget_match.group(2) if budget_match else "N/A"

            desc_tag = job.find("p", class_="body-medium line-clamp")
            desc = html.unescape(desc_tag.get_text(strip=True)) if desc_tag else ""

            ai_model = "GPT-4o Text"
            est_cost_val = 0.01
            if any(k in desc.lower() for k in ["image", "gambar", "extract", "photo", "ocr"]):
                ai_model = "Gemini Vision / GPT-4o Vision"
                est_cost_val = 0.05
                
            if budget != "N/A":
                if "-" in budget:
                    parts = budget.replace("$", "").split("-")
                    avg_budget = (float(parts[0]) + float(parts[1])) / 2
                else:
                    avg_budget = float(budget.replace("$", ""))
                profit = avg_budget - est_cost_val
                profit_str = f"${profit:.2f}"
            else:
                profit_str = "N/A"

            data_proyek.append({
                "Judul": title[:45] + "..." if len(title) > 45 else title,
                "Budget": budget,
                "AI Model": ai_model,
                "Modal": f"${est_cost_val:.2f}",
                "Profit": profit_str
            })

        if data_proyek:
            table = Table(title="Upwork Project Analyzer", header_style="bold magenta")
            table.add_column("Judul", style="cyan")
            table.add_column("Budget", style="green")
            table.add_column("AI Model", style="yellow")
            table.add_column("Modal", style="red")
            table.add_column("Profit", style="bold green")

            for p in data_proyek:
                table.add_row(p["Judul"], p["Budget"], p["AI Model"], p["Modal"], p["Profit"])

            console.print("\n", table, "\n")
            
            df = pd.DataFrame(data_proyek)
            df.to_excel("Upwork_Analysis.xlsx", index=False)
            console.print("[bold green]✅ Data disimpan di Upwork_Analysis.xlsx (cek folder Windows lu)[/bold green]")
        else:
            console.print("[warning]Gak ada proyek yang ketangkep.[/warning]")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
