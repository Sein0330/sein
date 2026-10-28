import asyncio
import pandas as pd
import io
from playwright.async_api import async_playwright
from rich.console import Console
from bs4 import BeautifulSoup

console = Console()

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # 1. LOGIN
        console.print("[cyan]1. Login...[/cyan]")
        await page.goto("http://10.2.113.252:8010/roc3/amel/login")
        await page.wait_for_timeout(2000)
        await page.locator("input[type='text']").first.fill("amel_tif2")
        await page.locator("input[type='password']").first.fill("telkom247") # GANTI
        await page.locator("button[type='submit']").first.click()
        await page.wait_for_timeout(3000)
        
        # 2. BUKA MENU
        console.print("[cyan]2. Buka All Tiket Open...[/cyan]")
        await page.goto("http://10.2.113.252:8010/roc3/amel/all_tiket_open")
        await page.wait_for_timeout(3000)
        
        # 3. KLIK ANGKA PERTAMA
        console.print("[cyan]3. Mencari angka pertama...[/cyan]")
        pointer_cells = page.locator("td.pointer")
        count = await pointer_cells.count()
        
        clicked = False
        for i in range(count):
            cell = pointer_cells.nth(i)
            text = await cell.inner_text()
            if text.strip().isdigit() and int(text.strip()) > 0:
                console.print(f"[green]Mengklik angka '{text.strip()}'...[/green]")
                await cell.click()
                await page.wait_for_timeout(5000)
                clicked = True
                break
                
        if not clicked:
            console.print("[danger]Gak nemu angka buat diklik.[/danger]")
            await browser.close()
            return

        # 4. AMBIL SEMUA TABEL dl_table
        console.print("[cyan]4. Mengambil semua data tiket dari dl_table...[/cyan]")
        html_dl = await page.locator("#dl_table").inner_html()
        full_html = f"<table>{html_dl}</table>"
        
        try:
            df = pd.read_html(io.StringIO(full_html))[0]
            console.print(f"[success]Berhasil narik {len(df)} baris tiket![/success]")
            
            # 5. FILTER DATA BANDUNG
            console.print("[cyan]5. Memfilter data Bandung...[/cyan]")
            
            # Cari berdasarkan teks BANDUNG, GGK, atau GEGERKALONG di semua kolom
            filter_mask = df.apply(lambda row: row.astype(str).str.contains('BANDUNG|GGK|GEGERKALONG', case=False).any(), axis=1)
            df_bandung = df[filter_mask]
            
            if len(df_bandung) > 0:
                console.print(f"[bold green]Ketemu {len(df_bandung)} tiket Bandung![/bold green]")
                output_file = "Amel/Tiket_Bandung.csv"
                df_bandung.to_csv(output_file, index=False)
                console.print(f"[bold green]Data disimpan di {output_file}[/bold green]")
                
                console.print("\n[bold yellow]Preview Data:[/bold yellow]")
                console.print(df_bandung[['INCIDENT', 'REPORTED DATE', 'WORKZONE', 'TTR']].head(5).to_string())
            else:
                console.print("[warning]Gak nemu tiket Bandung di tabel ini.[/warning]")
                df.to_csv("Amel/Tiket_Semua.csv", index=False)
                console.print(f"[bold yellow]Semua data disimpan di Amel/Tiket_Semua.csv[/bold yellow]")

        except Exception as e:
            console.print(f"[danger]Gagal parse tabel: {e}[/danger]")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
