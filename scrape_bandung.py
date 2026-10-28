import asyncio
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
        console.print("[cyan]1. Login ke ROC3...[/cyan]")
        await page.goto("http://10.2.113.252:8010/roc3/amel/login")
        await page.wait_for_timeout(2000)
        await page.locator("input[type='text']").first.fill("amel_tif2")
        await page.locator("input[type='password']").first.fill("telkom247") # GANTI
        await page.locator("button[type='submit']").first.click()
        await page.wait_for_timeout(3000)
        
        # 2. BUKA MENU ALL TIKET OPEN
        console.print("[cyan]2. Buka All Tiket Open...[/cyan]")
        await page.goto("http://10.2.113.252:8010/roc3/amel/all_tiket_open")
        await page.wait_for_timeout(3000)
        
        # 3. KLIK "AREA" DI TABEL
        console.print("[cyan]3. Mencari tombol/link 'AREA'...[/cyan]")
        try:
            # Cari link/teks yang isinya "AREA" (biasanya di header tabel)
            area_btn = page.locator("text=AREA").first
            await area_btn.click()
            await page.wait_for_timeout(3000)
            console.print("[success]✅ Klik 'AREA' berhasil.[/success]")
        except:
            console.print("[warning]⚠️ Gak nemu teks 'AREA'. Mungkin harus klik angka tertentu dulu.[/warning]")

        # 4. KLIK "JAWA BARAT"
        console.print("[cyan]4. Mencari 'JAWA BARAT'...[/cyan]")
        try:
            jabar_btn = page.locator("text=JAWA BARAT").first
            await jabar_btn.click()
            await page.wait_for_timeout(3000)
            console.print("[success]✅ Klik 'JAWA BARAT' berhasil.[/success]")
        except:
            console.print("[warning]⚠️ Gak nemu 'JAWA BARAT'.[/warning]")

        # 5. KLIK "BANDUNG"
        console.print("[cyan]5. Mencari 'BANDUNG'...[/cyan]")
        try:
            bandung_btn = page.locator("text=BANDUNG").first
            await bandung_btn.click()
            await page.wait_for_timeout(5000) # Tunggu data detail tiket muncul
            console.print("[success]✅ Klik 'BANDUNG' berhasil.[/success]")
        except:
            console.print("[warning]⚠️ Gak nemu 'BANDUNG'.[/warning]")

        # 6. SIMPAN HTML HASIL AKHIR
        html = await page.content()
        with open("Amel/capture_tiket_bandung.html", "w", encoding="utf-8") as f:
            f.write(html)
        console.print("[bold green]✅ HTML Detail Bandung disimpan![/bold green]")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
