import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from rich.console import Console

console = Console()

async def main():
    async with async_playwright() as p:
        console.print("[cyan]Menyambung ke Chrome...[/cyan]")
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception as e:
            console.print(f"[danger]Gagal konek: {e}[/danger]")
            return
        
        contexts = browser.contexts
        if not contexts:
            console.print("[danger]Gak ada tab Chrome yang kebuka.[/danger]")
            return
            
        page = contexts[0].pages[0]
        console.print(f"[green]Tersambung ke tab: {await page.title()}[/green]")
        
        # Ambil HTML
        html = await page.content()
        
        # Simpan ke file
        with open("upwork_full.html", "w", encoding="utf-8") as f:
            f.write(html)
        console.print("[bold green]✅ HTML disimpan di upwork_full.html[/bold green]")
        
        # Parse pake BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        
        # Cari semua <article> (kemungkinan besar ini card proyeknya)
        articles = soup.find_all("article")
        console.print(f"[cyan]Menemukan {len(articles)} tag <article>.[/cyan]")
        
        # Cari semua <div> yang punya class mengandung kata 'job'
        divs = soup.find_all("div", class_=lambda c: c and "job" in c.lower())
        console.print(f"[cyan]Menemukan {len(divs)} tag <div> class 'job*'.[/cyan]")
        
        # Tampilin 3 tag pertama buat diinspeksi
        if articles:
            console.print("\n[bold yellow]Contoh 3 tag <article> pertama:[/bold yellow]")
            for i, art in enumerate(articles[:3]):
                console.print(f"[dim]--- Article {i+1} ---[/dim]")
                # Tampilin tag pembuka aja
                console.print(str(art)[:200] + "...")
                
        if divs:
            console.print("\n[bold yellow]Contoh 3 tag <div class='job*'> pertama:[/bold yellow]")
            for i, div in enumerate(divs[:3]):
                console.print(f"[dim]--- Div {i+1} ---[/dim]")
                console.print(str(div)[:200] + "...")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
