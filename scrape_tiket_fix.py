import asyncio
from playwright.async_api import async_playwright
from rich.console import Console

console = Console()

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        console.print("[cyan]1. Membuka halaman login...[/cyan]")
        await page.goto("http://10.2.113.252:8010/roc3/amel/login")
        await page.wait_for_timeout(2000)
        
        # Auto-fill
        await page.locator("input[type='text']").first.fill("amel_tif2")
        await page.locator("input[type='password']").first.fill("telkom247") # GANTI DISINI
        await page.locator("button[type='submit'], input[type='submit']").first.click()
        await page.wait_for_timeout(3000)
        
        console.print("[cyan]2. Membuka halaman All Tiket Open...[/cyan]")
        await page.goto("http://10.2.113.252:8010/roc3/amel/all_tiket_open")
        
        console.print("[yellow]3. Menunggu 15 detik biar tabel selesai loading...[/yellow]")
        await page.wait_for_timeout(15000)
        
        # Save HTML
        html = await page.content()
        with open("Amel/capture_all_tiket_open_LENGKAP.html", "w", encoding="utf-8") as f:
            f.write(html)
        console.print("[bold green]✅ HTML Lengkap disimpan di Amel/capture_all_tiket_open_LENGKAP.html[/bold green]")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
