import asyncio
import pandas as pd
import io
from playwright.async_api import async_playwright
from rich.console import Console

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
        
        # 3. KLIK ANGKA PERTAMA (Biar munculin tabel dl_table)
        console.print("[cyan]3. Klik angka pertama...[/cyan]")
        pointer_cells = page.locator("td.pointer")
        count = await pointer_cells.count()
        clicked = False
        for i in range(count):
            cell = pointer_cells.nth(i)
            text = await cell.inner_text()
            if text.strip().isdigit() and int(text.strip()) > 0:
                await cell.click()
                await page.wait_for_timeout(5000)
                clicked = True
                break
        
        if not clicked:
            console.print("[danger]Gak nemu angka buat diklik.[/danger]")
            await browser.close()
            return

        # 4. KLIK FILTER STO "BANDUNG"
        console.print("[cyan]4. Mencari filter STO 'BANDUNG'...[/cyan]")
        
        # Kita cari elemen <a>, <span>, atau <div> yang punya name="filter_sto" dan teksnya "BANDUNG"
        filter_bandung = page.locator("text=BANDUNG").first
        
        # Coba cari elemen yang lebih spesifik
        found = False
        
        # Opsi A: Cari berdasarkan teks di dalam tag <a> atau <span>
        sto_elements = page.locator("a, span, div").filter(has_text="BANDUNG")
        sto_count = await sto_elements.count()
        
        for i in range(sto_count):
            el = sto_elements.nth(i)
            # Cek apakah dia punya attribute name="filter_sto" atau parent-nya punya
            name_attr = await el.get_attribute("name")
            if name_attr == "filter_sto":
                console.print(f"[green]Ketemu elemen 'BANDUNG' dengan name=filter_sto![/green]")
                await el.click()
                await page.wait_for_timeout(3000)
                found = True
                break
        
        if not found:
            # Opsi B: Klik berdasarkan teks aja (kalo gak nemu name)
            console.print("[warning]Nama 'filter_sto' gak ketemu. Coba klik teks 'BANDUNG'...[/warning]")
            if await filter_bandung.count() > 0:
                await filter_bandung.click()
                await page.wait_for_timeout(3000)
                found = True
        
        if not found:
            console.print("[danger]Gak nemu elemen BANDUNG buat diklik.[/danger]")
            await browser.close()
            return

        # 5. AMBIL DATA DARI dl_table
        console.print("[cyan]5. Mengambil data tiket Bandung dari dl_table...[/cyan]")
        html_dl = await page.locator("#dl_table").inner_html()
        full_html = f"<table>{html_dl}</table>"
        
        try:
            df = pd.read_html(io.StringIO(full_html))[0]
            console.print(f"[success]Berhasil narik {len(df)} baris tiket![/success]")
            
            # Simpan ke CSV
            output_file = "Amel/Tiket_Bandung_Filtered.csv"
            df.to_csv(output_file, index=False)
            console.print(f"[bold green]Data disimpan di {output_file}[/bold green]")
            
            # Tampilin contoh data
            console.print("\n[bold yellow]Preview Data:[/bold yellow]")
            console.print(df[['INCIDENT', 'REPORTED DATE', 'WORKZONE', 'TTR']].head(5).to_string())

        except Exception as e:
            console.print(f"[danger]Gagal parse tabel: {e}[/danger]")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
