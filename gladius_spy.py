import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        url = "https://gladius.telkom.co.id/internetnumber/numbercheck"
        print(f"Membuka {url}...")
        await page.goto(url)
        
        # Tunggu halaman load
        await page.wait_for_timeout(3000)
        
        # Screenshot full page buat liat tampilan login
        await page.screenshot(path="gladius_login.png", full_page=True)
        print("Screenshot disimpan di gladius_login.png")
        
        # Dump HTML ke file
        html = await page.content()
        with open("gladius_login.html", "w") as f:
            f.write(html)
        print("HTML disimpan di gladius_login.html")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
