import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # 1. Buka halaman login
        await page.goto("http://10.2.113.252:8010/roc3/amel/login")
        await page.fill("input[type='text']", "amel_tif2")
        await page.fill("input[type='password']", "PASSWORD_LU") # GANTI PASSWORD
        await page.click("button[type='submit']")
        await page.wait_for_timeout(3000)
        
        # 2. Buka halaman tiket
        await page.goto("http://10.2.113.252:8010/roc3/amel/all_tiket_open")
        print("Menunggu 15 detik biar tabel loading...")
        await page.wait_for_timeout(15000) # NUNGGU LAMA
        
        # 3. Simpan HTML
        html = await page.content()
        with open("Amel/capture_all_tiket_open_LENGKAP.html", "w") as f:
            f.write(html)
        print("✅ HTML Lengkap disimpan!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
