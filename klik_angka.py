import asyncio
from playwright.async_api import async_playwright
from rich.console import Console

console = Console()

async def main():
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
        
        # 3. Cari elemen dengan class 'pointer' dan klik
        console.print("[cyan]3. Mencari angka dengan class 'pointer'...[/cyan]")
        
        # Kita cari <td> yang punya class 'pointer' dan isinya angka > 0
        # Kita ambil baris ke-4 (BEKASI) kolom ke-2 (INDIHOME)
        pointer_cells = page.locator("td.pointer")
        count = await pointer_cells.count()
        console.print(f"Total elemen <td> dengan class 'pointer': {count}")
        
        clicked = False
        for i in range(count):
            cell = pointer_cells.nth(i)
            text = await cell.inner_text()
            if text.strip().isdigit() and int(text.strip()) > 0:
                console.print(f"[green]✅ Menemukan angka '{text.strip()}'. Mengklik...[/green]")
                await cell.click()
                await page.wait_for_timeout(8000) # Tunggu 8 detik buat loading detail
                clicked = True
                break
                
        if not clicked:
            console.print("[warning]⚠️ Gak nemu angka yang bisa diklik.[/warning]")

        # 4. Simpan HTML hasil
        html = await page.content()
        with open("Amel/capture_detail_bekasi.html", "w", encoding="utf-8") as f:
            f.write(html)
        console.print("[bold green]✅ HTML Detail disimpan di Amel/capture_detail_bekasi.html[/bold green]")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
