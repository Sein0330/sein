import asyncio
from playwright.async_api import async_playwright
import pyotp
import requests
import os
from dotenv import load_dotenv
from PIL import Image
from bs4 import BeautifulSoup
from rich.console import Console
from rich_pixels import Pixels

load_dotenv()
NIK = os.getenv("GLADIUS_NIK", "")
PASSWORD = os.getenv("GLADIUS_PASS", "")
TOTP_SECRET = os.getenv("GLADIUS_TOTP_SECRET", "")

URL_LOGIN = "https://gladius.telkom.co.id/internetnumber/numbercheck"
URL_RADONLINE = "https://gladius.telkom.co.id/radonline/newradonline"
SAVE_DIR = "/home/almaarij/sein/captcha_temp"
console = Console()

def parse_summary(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    data = {k: "-" for k in ["Nomor", "Domain", "IP Statik", "Paket", "Status", "Port Binding", "EQN", "Rx Power", "IP OLT", "NAS IP", "Framed IP", "Status Koneksi"]}
    tds = soup.find_all("td")
    for i, td in enumerate(tds):
        text = td.get_text(strip=True)
        if text == "Nomor" and i+1 < len(tds): data["Nomor"] = tds[i+1].get_text(strip=True)
        elif text == "Domain" and i+1 < len(tds): data["Domain"] = tds[i+1].get_text(strip=True)
        elif text == "IP Statik" and i+1 < len(tds): data["IP Statik"] = tds[i+1].get_text(strip=True)
        elif text == "Paket Radius / Paket PCRF" and i+1 < len(tds): data["Paket"] = tds[i+1].get_text(strip=True)
        elif text == "Status Pelanggan" and i+1 < len(tds): data["Status"] = tds[i+1].get_text(strip=True)
        elif text == "Port Binding" and i+1 < len(tds): data["Port Binding"] = tds[i+1].get_text(strip=True)
        elif text == "EQN" and i+1 < len(tds): data["EQN"] = tds[i+1].get_text(strip=True)
        elif text == "IP OLT / Type OLT" and i+1 < len(tds): data["IP OLT"] = tds[i+1].get_text(strip=True)
        elif text == "Rx Power" and "dBm" in tds[i+2].get_text(): data["Rx Power"] = tds[i+1].get_text(strip=True) + " dBm"

    lastusage_table = soup.find("table", id="lastusage")
    if lastusage_table:
        rows = lastusage_table.find_all("tr")
        if len(rows) > 1:
            cols = rows[1].find_all("td")
            if len(cols) >= 10:
                data["NAS IP"] = cols[0].get_text(strip=True)
                data["Framed IP"] = cols[6].get_text(strip=True)
                data["Status Koneksi"] = cols[9].get_text(strip=True)
    return data

async def run_gladius(nomor_internet, domain):
    os.makedirs(SAVE_DIR, exist_ok=True)
    
    MAX_RETRIES = 3
    for attempt in range(MAX_RETRIES):
        console.print(f"\n[bold cyan]🔐 Memverifikasi keamanan ({attempt+1}/{MAX_RETRIES})...[/bold cyan]")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto(URL_LOGIN)
            await page.wait_for_timeout(2000)
            
            captcha_id = await page.locator("#captcha-id").get_attribute("value")
            captcha_img_url = f"https://gladius.telkom.co.id/tmp/captcha/{captcha_id}.png"
            cookies = await context.cookies()
            cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
            img_response = requests.get(captcha_img_url, headers={"Cookie": cookie_str})
            
            captcha_path = os.path.join(SAVE_DIR, "captcha_terbaru.png")
            with open(captcha_path, "wb") as f:
                f.write(img_response.content)
            
            console.print("\n[bold yellow]Silahkan masukan Captcha berikut :[/bold yellow]")
            try:
                img = Image.open(captcha_path)
                # Render gambar di terminal
                pixels = Pixels.from_image(img)
                console.print(pixels)
            except Exception as e:
                console.print(f"[dim](Gagal render gambar: {e})[/dim]")
                
            captcha_text = input("\nInput CAPTCHA disini : ").strip()
            
            if len(captcha_text) < 3:
                console.print("[warning]⚠️ CAPTCHA terlalu pendek, ulangi.[/warning]")
                await browser.close()
                continue # Lanjut ke percobaan berikutnya

            await page.fill("#uname", NIK)
            await page.fill("#passw", PASSWORD)
            await page.fill("#captcha-input", captcha_text)
            if not await page.is_checked("#agree"): await page.check("#agree")
            await page.click("button[type='submit']")
            await page.wait_for_timeout(3000)
            
            # Cek apakah masih di halaman login (artinya captcha/pass salah)
            if "numbercheck" in page.url or "login" in page.url:
                console.print("[bold red]❌ CAPTCHA atau Password SALAH! Ulangi.[/bold red]")
                await browser.close()
                continue # Lanjut ke percobaan berikutnya

            # Lanjut ke OTP
            totp = pyotp.TOTP(TOTP_SECRET)
            otp_code = totp.now()
            try:
                await page.fill("input[placeholder='Kode Verifikasi']", otp_code, timeout=5000)
                await page.click("button[type='submit']")
                await page.wait_for_timeout(3000)
            except:
                console.print("[warning]⚠️ Gagal masukin OTP, ulangi.[/warning]")
                await browser.close()
                continue

            # Cek apakah OTP gagal
            if "otp" in page.url:
                console.print("[bold red]❌ OTP SALAH! Ulangi.[/bold red]")
                await browser.close()
                continue

            # --- SUKSES LOGIN ---
            console.print("[bold green]Sedang memproses permintaan...[/bold green]")
            await page.goto(URL_RADONLINE)
            await page.wait_for_timeout(3000)
            
            try:
                await page.fill("input[name='no_speedy']", nomor_internet)
                await page.select_option("select[name='domain']", domain)
                await page.locator("button", has_text="Cek").click()
                await page.wait_for_timeout(8000) 

                bounding_box = await page.evaluate("""() => {
                    const tables = document.querySelectorAll('table.table-bordered, table#lastusage');
                    if (tables.length === 0) return null;
                    const firstTable = tables[0].getBoundingClientRect();
                    const lastTable = tables[tables.length - 1].getBoundingClientRect();
                    return { x: firstTable.left - 10, y: firstTable.top - 10, width: firstTable.width + 20, height: (lastTable.bottom - firstTable.top) + 20 };
                }""")
                
                output_filename = f"hasil_{nomor_internet}.png"
                if bounding_box:
                    await page.screenshot(path="temp_full.png", full_page=True)
                    img = Image.open("temp_full.png")
                    device_scale = await page.evaluate("window.devicePixelRatio")
                    crop_box = (int(bounding_box['x'] * device_scale), int(bounding_box['y'] * device_scale), int((bounding_box['x'] + bounding_box['width']) * device_scale), int((bounding_box['y'] + bounding_box['height']) * device_scale))
                    img.crop(crop_box).save(output_filename)
                    os.remove("temp_full.png")

                html_content = await page.content()
                summary_data = parse_summary(html_content)
                
                await browser.close()
                return summary_data, output_filename
                
            except Exception as e:
                await browser.close()
                return None, f"Gagal RadOnline: {str(e)}"
                
    # Kalau udah 3x tetep gagal
    return None, "Batas percobaan habis (3x gagal)."
