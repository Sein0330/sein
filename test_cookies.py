import asyncio
from playwright.async_api import async_playwright
from rich.console import Console
import json

console = Console()

def clean_cookies(cookies):
    cleaned = []
    for c in cookies:
        if not c.get("name") or not c.get("value"): continue
        new_c = {
            "name": c["name"], "value": c["value"],
            "domain": c.get("domain", ""), "path": c.get("path", "/"),
            "secure": c.get("secure", False), "httpOnly": c.get("httpOnly", False)
        }
        ss = str(c.get("sameSite", "")).lower()
        new_c["sameSite"] = ss.capitalize() if ss in ["strict", "lax", "none"] else "Lax"
        cleaned.append(new_c)
    return cleaned

async def main():
    async with async_playwright() as p:
        console.print("[cyan]Membuka browser (Mode Stealth)...[/cyan]")
        # Trik: Pake mode 'headed' (False) tapi jalanin di Xvfb (Virtual Display)
        # Atau kalo mau cepet, kita coba trik args anti-detect dulu
        browser = await p.chromium.launch(
            headless=False, # WAJIB False biar gak ke-detect headless
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )
        
        # Set User Agent jadi Chrome Windows biasa
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        
        try:
            with open("cookies.json", "r") as f:
                raw_cookies = json.load(f)
            cookies = clean_cookies(raw_cookies)
            await context.add_cookies(cookies)
            console.print(f"[green]✅ {len(cookies)} Cookies di-load![/green]")
        except Exception as e:
            console.print(f"[danger]❌ Gagal load cookies: {e}[/danger]")
            await browser.close()
            return

        page = await context.new_page()
        
        # Trik sembunyiin 'webdriver'
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        console.print("[cyan]Membuka Upwork...[/cyan]")
        await page.goto("https://www.upwork.com/nx/find-work/")
        await page.wait_for_timeout(5000)
        
        title = await page.title()
        console.print(f"[cyan]Judul halaman: {title}[/cyan]")
        
        if "Cloudflare" in title:
            console.print("[danger]❌ Kena blokir Cloudflare. Butuh solusi lebih dalem.[/danger]")
        elif "login" in page.url:
            console.print("[danger]❌ Cookies gak valid.[/danger]")
        else:
            console.print("[bold green]✅ SUKSES! Cookies Works![/bold green]")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
