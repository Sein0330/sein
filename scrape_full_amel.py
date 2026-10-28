import asyncio
import pandas as pd
from playwright.async_api import async_playwright
from rich.console import Console
from bs4 import BeautifulSoup
import time

console = Console()

async def main():
    all_data = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # 1. Login
        console.print("[cyan]1. Login...[/cyan]")
        await page.goto("http://10.2.113.252:8010/roc3/amel/login")
        await page.wait_for_timeout(2000)
        await page.locator("input[type='text']").first.fill("amel_tif2")
        await page.locator("input[type='password']").first.fill("telkom247") # GANTI
        await page.locator("button[type='submit']").first.click()
        await page.wait_for_timeout(3000)
        
        # 2. Buka halaman
        console.print("[cyan]2. Buka All Tiket Open...[/cyan]")
        await page.goto("http://10.2.113.252:8010/roc3/amel/all_tiket_open")
        await page.wait_for_timeout(3000)
        
        # 3. Cari semua elemen <td> class 'pointer' yang isinya angka > 0
        console.print("[cyan]3. Mencari semua angka yang bisa diklik...[/cyan]")
        pointer_cells = page.locator("td.pointer")
        count = await pointer_cells.count()
        
        # Kita simpen index yang isinya angka > 0
        target_indices = []
        for i in range(count):
            cell = pointer_cells.nth(i)
            text = await cell.inner_text()
            if text.strip().isdigit() and int(text.strip()) > 0:
                target_indices.append((i, text.strip()))
                
        console.print(f"[green]✅ Ditemukan {len(target_indices)} sel yang bisa diklik.[/green]")
        
        # 4. Loop klik satu per satu, tarik data dari dl_table
        for idx, (cell_idx, text_val) in enumerate(target_indices):
            console.print(f"[cyan]Memproses data ke-{idx+1} (Nilai: {text_val})...[/cyan]")
            
            # Klik sel
            await pointer_cells.nth(cell_idx).click()
            await page.wait_for_timeout(4000) # Tunggu tabel dl_table muncul
            
            # Ambil HTML halaman saat ini
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            
            # Cari tabel dl_table
            dl_table = soup.find("table", id="dl_table")
            if dl_table:
                # Parse pake Pandas
                try:
                    df = pd.read_html(str(dl_table))[0]
                    # Tambahin kolom "Klik Dari" (biar tau ini data dari district mana)
                    df['Klik Dari'] = f"Cell-{cell_idx} (Val: {text_val})"
                    all_data.append(df)
                    console.print(f"   -> [success]Dapat {len(df)} baris data.[/success]")
                except Exception as e:
                    console.print(f"   -> [warning]Gagal parse tabel: {e}[/warning]")
            else:
                console.print("   -> [warning]Tabel dl_table gak ketemu.[/warning]")
                
            # Tutup modal / refresh halaman biar bisa klik sel berikutnya
            try:
                await page.locator("button:has-text('Close')").first.click()
                await page.wait_for_timeout(1000)
            except:
                await page.reload()
                await page.wait_for_timeout(3000)
                # Re-init locator karena page udah reload
                pointer_cells = page.locator("td.pointer")
        
        # 5. Gabungin semua data jadi 1 DataFrame
        if all_data:
            final_df = pd.concat(all_data, ignore_index=True)
            # Simpen ke CSV
            final_df.to_csv("Amel/data_tiket_amel.csv", index=False)
            console.print(f"[bold green]✅ SUKSES! Data disimpan di Amel/data_tiket_amel.csv ({len(final_df)} baris)[/bold green]")
        else:
            console.print("[danger]❌ Gak ada data yang berhasil ditarik.[/danger]")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
