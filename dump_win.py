import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        print("Menyambung ke Chrome...")
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        
        contexts = browser.contexts
        if not contexts:
            print("Gak ada tab Chrome yang kebuka.")
            return
            
        page = contexts[0].pages[0]
        print(f"Tersambung ke tab: {await page.title()}")
        
        # Ambil HTML
        html = await page.content()
        
        with open("upwork_dump.html", "w", encoding="utf-8") as f:
            f.write(html)
        
        print("✅ HTML disimpan di upwork_dump.html")
        
        # Cek beberapa kemungkinan tag
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        
        print("\n--- CEK TAG ---")
        print(f"data-test='job-tile' : {len(soup.find_all('div', attrs={'data-test': 'job-tile'}))}")
        print(f"class='job-tile' : {len(soup.find_all('div', class_='job-tile'))}")
        print(f"data-ev-label='search_result' : {len(soup.find_all(attrs={'data-ev-label': 'search_result'}))}")
        print(f"h3 data-test='job-title' : {len(soup.find_all('h3', attrs={'data-test': 'job-title'}))}")
        print(f"h2 : {len(soup.find_all('h2'))}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
