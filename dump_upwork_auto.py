import asyncio
from playwright.async_api import async_playwright
import json

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
        browser = await p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Pake fungsi pembersih
        with open("cookies.json", "r") as f:
            raw_cookies = json.load(f)
        cookies = clean_cookies(raw_cookies)
        
        await context.add_cookies(cookies)
            
        page = await context.new_page()
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        await page.goto("https://www.upwork.com/nx/search/jobs/?q=data+entry")
        await page.wait_for_timeout(5000)
        
        html = await page.content()
        with open("upwork_auto_dump.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("✅ HTML disimpan di upwork_auto_dump.html")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
