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
SESSION_FILE = "/home/almaarij/sein/gladius_session.json"
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

async def login_gladius(page, context):
    MAX_RETRIES = 3
    for attempt in range(MAX_RETRIES):
        console.print(f"\n[bold cyan]🔐 Memverifikasi identitas ({attempt+1}/{MAX_RETRIES})...[/bold cyan]")
        
        await page.goto(URL_LOGIN)
        await page.wait_for_timeout(2000)
        
        captcha_id = await page.locator("#captcha-id").get_attribute("value")
        captcha_img_url = f"https://gladius.telkom.co.id/tmp/captcha/{captcha_id}.png"
        cookies = await context.cookies()
        cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
        img_response = requests.get(captcha_img_url, headers={"Cookie": cookie_str})
        
        captcha_path = os.path.join(SAVE_DIR, "captcha_terbaru.png")
        os.makedirs(SAVE_DIR, exist_ok=True)
        with open(captcha_path, "wb") as f:
            f.write(img_response.content)
        
        console.print("\n[bold yellow]Silahkan masukan Captcha berikut :[/bold yellow]")
        try:
            img = Image.open(captcha_path)
            pixels = Pixels.from_image(img)
            console.print(pixels)
        except:
            pass
            
        captcha_text = input("\nInput CAPTCHA disini : ").strip()
        
        if len(captcha_text) < 3:
            console.print("[warning]⚠️ CAPTCHA terlalu pendek, ulangi.[/warning]")
            continue

        await page.fill("#uname", NIK)
        await page.fill("#passw", PASSWORD)
        await page.fill("#captcha-input", captcha_text)
        if not await page.is_checked("#agree"): await page.check("#agree")
        await page.click("button[type='submit']")
        await page.wait_for_timeout(3000)
        
        if "numbercheck" in page.url or "login" in page.url:
            console.print("[bold red]❌ CAPTCHA atau Password SALAH! Ulangi.[/bold red]")
            continue 

        totp = pyotp.TOTP(TOTP_SECRET)
        otp_code = totp.now()
        try:
            await page.fill("input[placeholder='Kode Verifikasi']", otp_code, timeout=5000)
            await page.click("button[type='submit']")
            await page.wait_for_timeout(3000)
        except:
            console.print("[warning]⚠️ Gagal memasukkan kode verifikasi, ulangi.[/warning]")
            continue

        if "otp" in page.url:
            console.print("[bold red]❌ Kode verifikasi SALAH! Ulangi.[/bold red]")
            continue

        await context.storage_state(path=SESSION_FILE)
        console.print("[bold green]✅ Identitas terverifikasi. Token disimpan.[/bold green]")
        return True
        
    return False

async def run_gladius(nomor_internet, domain):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # 1. Cek File Session
        session_exists = os.path.exists(SESSION_FILE)
        
        if session_exists:
            console.print("[cyan]Menyiapkan koneksi ke server...[/cyan]")
            context = await browser.new_context(storage_state=SESSION_FILE)
        else:
            console.print("[cyan]Memuat modul keamanan...[/cyan]")
            context = await browser.new_context()
            
        page = await context.new_page()

        # 2. Validasi Session (Kalo gak ada file, langsung paksa login)
        is_valid = False
        if session_exists:
            await page.goto(URL_RADONLINE)
            await page.wait_for_timeout(3000)
            if not ("numbercheck" in page.url or "login" in page.url):
                is_valid = True
                console.print("[bold green]✅ Koneksi aman. Mengambil data pelanggan...[/bold green]")
        
        # 3. Kalo Session Gak Valid / Gak Ada, Login
        if not is_valid:
            if session_exists:
                console.print("[warning]⚠️ Sesi keamanan berakhir, memperbarui token...[/warning]")
                os.remove(SESSION_FILE)
            
            login_success = await login_gladius(page, context)
            if not login_success:
                await browser.close()
                return None, "Verifikasi gagal setelah 3x percobaan."
                
            await page.goto(URL_RADONLINE)
            await page.wait_for_timeout(3000)

        # ================= PROCESS RADONLINE =================
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
