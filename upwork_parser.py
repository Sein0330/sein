from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
import pandas as pd
import re
import html

console = Console()

def process_upwork_html(file_path):
    console.print(f"[cyan]Membaca file: {file_path}[/cyan]")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
    except FileNotFoundError:
        console.print(f"[danger]❌ File gak ketemu di path: {file_path}[/danger]")
        return

    # --- CARI CARD PROYEK (Versi Baru: Article JobTile) ---
    jobs = soup.find_all("article", attrs={"data-test": "JobTile"})
    console.print(f"[cyan]Menemukan {len(jobs)} card proyek.[/cyan]")

    data_proyek = []
    for job in jobs:
        # 1. Ekstrak Judul (h2 class="job-tile-title")
        title_tag = job.find("h2", class_="job-tile-title")
        if not title_tag: continue
        title = html.unescape(title_tag.get_text(strip=True))
        
        # 2. Ekstrak Budget (Regex)
        text_all = job.get_text()
        budget_match = re.search(r'(Hourly|Fixed-price):\s*(\$\d+(?:-\$\d+)?(?:\.\d{2})?)', text_all)
        budget = budget_match.group(2) if budget_match else "N/A"

        # 3. Ekstrak Deskripsi
        desc = ""
        for p in job.find_all(["p", "span"]):
            txt = p.get_text(strip=True)
            if len(txt) > 50:
                desc = html.unescape(txt)
                break

        # --- LOGIKA AI COST ---
        ai_model = "GPT-4o Text"
        est_cost_val = 0.01
        if any(k in desc.lower() for k in ["image", "gambar", "extract", "photo", "ocr"]):
            ai_model = "Gemini Vision / GPT-4o Vision"
            est_cost_val = 0.05
            
        # Hitung Profit
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

    if not data_proyek:
        console.print("[warning]Gak ada proyek yang ketangkep.[/warning]")
        return

    # Tampilkan Tabel
    table = Table(title="Upwork Project Analyzer", header_style="bold magenta")
    table.add_column("Judul", style="cyan")
    table.add_column("Budget", style="green")
    table.add_column("AI Model", style="yellow")
    table.add_column("Modal", style="red")
    table.add_column("Profit", style="bold green")

    for p in data_proyek:
        table.add_row(p["Judul"], p["Budget"], p["AI Model"], p["Modal"], p["Profit"])

    console.print("\n", table, "\n")

    # Simpan ke Excel
    df = pd.DataFrame(data_proyek)
    df.to_csv("Upwork_Analysis.csv", index=False)
    console.print("[bold green]✅ Data disimpan di Upwork_Analysis.csv (di folder C:\\Users\\Public)[/bold green]")

if __name__ == "__main__":
    # PATH WINDOWS: Sesuaikan dengan lokasi file dump lu
    parse_path = "C:\\Users\\Public\\upwork_dump.html"
    process_upwork_html(parse_path)
