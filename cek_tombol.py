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
        
        # Login
        await page.goto("http://10.2.113.252:8010/roc3/amel/login")
        await page.wait_for_timeout(2000)
        await page.locator("input[type='text']").first.fill("amel_tif2")
        await page.locator("input[type='password']").first.fill("telkom247") # GANTI
        await page.locator("button[type='submit']").first.click()
        await page.wait_for_timeout(3000)
        
        # Buka halaman
        await page.goto("http://10.2.113.252:8010/roc3/amel/all_tiket_open")
        await page.wait_for_timeout(5000)
        
        # Dump HTML ke file
        html = await page.content()
        with open("Amel/debug_all_tiket.html", "w", encoding="utf-8") as f:
            f.write(html)
        
        # Cari semua <a> dan <button> yang ada teksnya
        soup = BeautifulSoup(html, "html.parser")
        print("\n=== DAFTAR LINK (<a>) ===")
        for a in soup.find_all("a")[:10]:
            print(f"Teks: {a.get_text(strip=True)} | Href: {a.get('href')} | Onclick: {a.get('onclick')}")
            
        print("\n=== DAFTAR BUTTON ===")
        for b in soup.find_all("button")[:10]:
            print(f"Teks: {b.get_text(strip=True)} | ID: {b.get('id')} | Onclick: {b.get('onclick')}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
