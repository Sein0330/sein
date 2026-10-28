import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
import pandas as pd
import re
import html
import json

console = Console()

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

async def main():
    async with async_playwright() as p:
        console.print("[cyan]Membuka browser (Mode Stealth)...[/cyan]")
        
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
            cookies = clean_cookies(raw_cookies)
            await context.add_cookies(cookies)
            console.print(f"[green]✅ {len(cookies)} Cookies di-load![/green]")
        except Exception as e:
            console.print(f"[danger]❌ Gagal load cookies: {e}[/danger]")
            await browser.close()
            return

        page = await context.new_page()
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        keyword = Prompt.ask("\nMasukkan keyword proyek (misal: data entry)").strip()
        if not keyword:
            await browser.close()
            return
            
        console.print(f"[cyan]Mencari proyek '{keyword}'...[/cyan]")
        await page.goto(f"https://www.upwork.com/nx/search/jobs/?q={keyword}")
        await page.wait_for_timeout(5000)
        
        html_content = await page.content()
        soup = BeautifulSoup(html_content, "html.parser")
        
        jobs = soup.find_all("article", attrs={"data-test": "JobTile"})
        console.print(f"[cyan]Menemukan {len(jobs)} card proyek.[/cyan]")
        
        data_proyek = []
        for job in jobs:
            title_tag = job.find("h2", class_="job-tile-title")
            if not title_tag: continue
            title = html.unescape(title_tag.get_text(strip=True))
            
            # --- CARI BUDGET (Anti Nyasar) ---
            budget = "N/A"
            
            # 1. Cari dari <li data-test="job-type-label">
            job_info_li = job.find("li", attrs={"data-test": "job-type-label"})
            if job_info_li:
                strong_tag = job_info_li.find("strong")
                if strong_tag:
                    budget_text = strong_tag.get_text(strip=True)
                    # Format harus $X atau $X.XX atau $X - $Y
                    m = re.search(r'\$\d{1,5}(?:[.,]\d+)?(?:\s*-\s*\$\d{1,5}(?:[.,]\d+)?)?', budget_text)
                    if m:
                        budget = m.group(0).strip()
            
            # 2. Fallback: "Fixed-price" atau "Est. budget"
            if budget == "N/A":
                text_all = job.get_text()
                m2 = re.search(r'(?:Fixed-price|Est\. budget):?\s*(\$\d{1,5}(?:[.,]\d+)?(?:\s*-\s*\$\d{1,5}(?:[.,]\d+)?)?)', text_all, re.IGNORECASE)
                if m2:
                    budget = m2.group(1).strip()
                else:
                    for strong in job.find_all("strong"):
                        txt = strong.get_text(strip=True)
                        # Cek format budget yang valid (ada desimal atau range, dan lebih dari 0)
                        if re.match(r'^\$\d{1,5}(?:[.,]\d+)?(?:\s*-\s*\$\d{1,5}(?:[.,]\d+)?)?$', txt):
                            # Cek apakah nilainya 0
                            if not txt.startswith("$0"):
                                budget = txt
                                break
                            
            # 3. Validasi akhir: Kalo gak ada desimal & bukan range, anggap N/A (kecuali > $100)
            if budget != "N/A":
                if "." not in budget and "-" not in budget:
                    # Kalo cuma "$10" (tanpa desimal), cek apakah masuk akal
                    try:
                        val = float(budget.replace("$", ""))
                        if val < 5: # Budget $1-$4 tanpa desimal biasanya ngaco
                            budget = "N/A"
                    except:
                        budget = "N/A"
                # Kalo "$0", jadi N/A
                if budget.startswith("$0"):
                    budget = "N/A"

            # Ambil deskripsi
            desc = ""
            for p_tag in job.find_all(["p", "span"]):
                txt = p_tag.get_text(strip=True)
                if len(txt) > 50:
                    desc = html.unescape(txt)
                    break

            # Logic AI
            ai_model = "GPT-4o Text"
            est_cost_val = 0.01
            if any(k in desc.lower() for k in ["image", "gambar", "extract", "photo", "ocr", "annotation"]):
                ai_model = "Gemini Vision / GPT-4o Vision"
                est_cost_val = 0.05
                
            # Hitung Profit
            if budget != "N/A":
                try:
                    clean_budget = budget.replace("$", "").replace(",", ".").replace(" ", "")
                    if "-" in clean_budget:
                        parts = clean_budget.split("-")
                        avg_budget = (float(parts[0]) + float(parts[1])) / 2
                    else:
                        avg_budget = float(clean_budget)
                    profit = avg_budget - est_cost_val
                    profit_str = f"${profit:.2f}"
                except:
                    profit_str = "N/A"
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

            for p_item in data_proyek:
                table.add_row(p_item["Judul"], p_item["Budget"], p_item["AI Model"], p_item["Modal"], p_item["Profit"])

            console.print("\n", table, "\n")
            
            df = pd.DataFrame(data_proyek)
            df.to_csv("Upwork_Analysis.csv", index=False)
            
            download_url = "https://tracker.sein.bid/download/upwork/Upwork_Analysis.csv"
            console.print("[bold green]✅ Data berhasil diambil![/bold green]")
            console.print(f"[bold cyan]🔗 Download CSV (Copy link ini):[/bold cyan]\n[underline]{download_url}[/underline]\n")
        else:
            console.print("[warning]Gak ada proyek yang ketangkep.[/warning]")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
