import asyncio
import pandas as pd
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
        
        # 3. KLIK ANGKA PERTAMA (Biar muncul menu Area)
        console.print("[cyan]3. Mencari angka pertama yang bisa diklik...[/cyan]")
        # Klik sel pertama yang punya class 'pointer' dan > 0
        pointer_cells = page.locator("td.pointer")
        count = await pointer_cells.count()
        clicked = False
        for i in range(count):
            cell = pointer_cells.nth(i)
            text = await cell.inner_text()
            if text.strip().isdigit() and int(text.strip()) > 0:
                console.print(f"[green]✅ Mengklik angka '{text.strip()}'...[/green]")
                await cell.click()
                await page.wait_for_timeout(4000) # Tunggu loading
                clicked = True
                break
                
        if not clicked:
            console.print("[danger]❌ Gak nemu angka buat diklik.[/danger]")
            await browser.close()
            return

        # 4. KLIK "AREA 2"
        console.print("[cyan]4. Mencari 'AREA 2'...[/cyan]")
        try:
            # Cari teks "AREA 2" (bisa <a>, <button>, <td>, atau <span>)
            await page.locator("text=AREA 2").first.click(timeout=5000)
            await page.wait_for_timeout(3000)
            console.print("[success]✅ Klik 'AREA 2' berhasil.[/success]")
        except:
            console.print("[warning]⚠️ Gak nemu 'AREA 2'. Mungkin namanya beda.[/warning]")

        # 5. KLIK "JABAR" ATAU "JAWA BARAT"
        console.print("[cyan]5. Mencari 'JABAR' / 'JAWA BARAT'...[/cyan]")
        try:
            # Coba klik JABAR dulu
            try:
                await page.locator("text=JABAR").first.click(timeout=3000)
            except:
                # Kalau gak nemu, coba JAWA BARAT
                await page.locator("text=JAWA BARAT").first.click(timeout=3000)
            await page.wait_for_timeout(3000)
            console.print("[success]✅ Klik Region Jabar berhasil.[/success]")
        except:
            console.print("[warning]⚠️ Gak nemu 'JABAR' atau 'JAWA BARAT'.[/warning]")

        # 6. KLIK "BANDUNG"
        console.print("[cyan]6. Mencari 'BANDUNG'...[/cyan]")
        try:
            await page.locator("text=BANDUNG").first.click(timeout=5000)
            await page.wait_for_timeout(10000) # Tunggu tabel detail Bandung muncul
            console.print("[success]✅ Klik 'BANDUNG' berhasil.[/success]")
        except:
            console.print("[warning]⚠️ Gak nemu 'BANDUNG'.[/warning]")

        # 7. SIMPAN HTML HASIL
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await page.wait_for_timeout(2000)
        html = await page.content()
        with open("Amel/capture_bandung_detail.html", "w", encoding="utf-8") as f:
            f.write(html)
        console.print("[bold green]✅ HTML disimpan di Amel/capture_bandung_detail.html[/bold green]")
        
        # 8. TAMPILKAN HASIL TABLE
        soup = BeautifulSoup(html, "html.parser")
        tables = soup.find_all("table")
        console.print("\n[bold yellow]Hasil Tabel Akhir:[/bold yellow]")
        for i, t in enumerate(tables):
            rows = t.find_all("tr")
            if len(rows) > 2: # Cuma tampilin yang ada datanya
                cols = rows[0].find_all(["th", "td"])
                print(f"Tabel ke-{i+1} (ID: {t.get('id')}): {len(rows)} baris")
                print(f"   Header: {[c.get_text(strip=True) for c in cols]}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
