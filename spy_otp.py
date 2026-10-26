import asyncio
from playwright.async_api import async_playwright
import os
from dotenv import load_dotenv

load_dotenv()
NIK = os.getenv("GLADIUS_NIK", "")
PASSWORD = os.getenv("GLADIUS_PASS", "")

URL_LOGIN = "https://gladius.telkom.co.id/internetnumber/numbercheck"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print("[*] Membuka halaman Login...")
        await page.goto(URL_LOGIN)
        await page.wait_for_timeout(2000)

        # Bypass captcha pakai manual input
        print("\n[!] Buka captcha, isi manual:")
        os.system(f"cp /tmp/*.png captcha_temp/ 2>/dev/null") # just in case
        # (Asumsi lu udah biasa isi captcha manual, kita pake API OCR aja biar cepat)
        from gladius import solve_captcha_api # Import fungsi dari gladius.py
        captcha_id = await page.locator("#captcha-id").get_attribute("value")
        captcha_img_url = f"https://gladius.telkom.co.id/tmp/captcha/{captcha_id}.png"
        cookies = await context.cookies()
        cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
        img_response = requests.get(captcha_img_url, headers={"Cookie": cookie_str})
        
        # Kita coba pake OCR API
        import requests
        captcha_text = solve_captcha_api(img_response.content)
        print(f"[+] Captcha (OCR): {captcha_text}")
        
        # Kalo OCR gagal, minta manual
        if len(captcha_text) < 3:
            with open("captcha_temp/spy_captcha.png", "wb") as f:
                f.write(img_response.content)
            captcha_text = input("👉 Ketik CAPTCHA manual (cek captcha_temp/spy_captcha.png): ")

        print("[*] Login...")
        await page.fill("#uname", NIK)
        await page.fill("#passw", PASSWORD)
        await page.fill("#captcha-input", captcha_text)
        if not await page.is_checked("#agree"): await page.check("#agree")
        await page.click("button[type='submit']")
        
        print("[*] Menunggu halaman OTP (5 detik)...")
        await page.wait_for_timeout(5000)
        
        # --- INI BAGIAN PENTINGNYA ---
        print("[*] Menyimpan HTML halaman OTP...")
        html = await page.content()
        with open("debug_otp.html", "w") as f:
            f.write(html)
        print("[+] HTML disimpan di debug_otp.html")
        
        # Print semua elemen input yang ada
        inputs = await page.locator("input").all()
        print(f"\n[+] Ditemukan {len(inputs)} input box:")
        for i, inp in enumerate(inputs):
            name = await inp.get_attribute("name")
            id_attr = await inp.get_attribute("id")
            type_attr = await inp.get_attribute("type")
            print(f"  {i+1}. ID: {id_attr} | Name: {name} | Type: {type_attr}")
            
        buttons = await page.locator("button").all()
        print(f"\n[+] Ditemukan {len(buttons)} tombol:")
        for i, btn in enumerate(buttons):
            text = await btn.inner_text()
            print(f"  {i+1}. Text: {text}")

        await browser.close()

if __name__ == "__main__":
    import requests
    asyncio.run(main())
