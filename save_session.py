import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        print("[*] Membuka browser (Non-Headless)...")
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        print("[*] Membuka halaman Login Gladius...")
        await page.goto("https://gladius.telkom.co.id/internetnumber/numbercheck")

        print("\n" + "="*50)
        print("⚠️  SILAKAN LOGIN MANUAL DI BROWSER YANG TERBUKA!")
        print("1. Isi NIK, Password, CAPTCHA, dan OTP.")
        print("2. Tunggu sampai masuk ke halaman Dashboard/RadOnline.")
        print("3. Setelah masuk, balik ke terminal ini dan tekan [ENTER].")
        print("="*50)
        
        input("👉 Tekan ENTER setelah berhasil login manual...")

        # Simpan cookies & local storage ke file state.json
        await context.storage_state(path="state.json")
        print("\n[+] Session berhasil disimpan ke 'state.json'!")
        print("[+] Sekarang lu bisa jalanin gladius.py tanpa login lagi.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
