import asyncio
from playwright.async_api import async_playwright
from rich.console import Console

console = Console()

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # 1. Login
        console.print("[cyan]1. Login...[/cyan]")
        await page.goto("http://10.2.113.252:8010/roc3/amel/login")
        await page.wait_for_timeout(2000)
        await page.locator("input[type='text']").first.fill("amel_tif2")
        await page.locator("input[type='password']").first.fill("telkom247") # GANTI
        await page.locator("button[type='submit']").first.click()
        await page.wait_for_timeout(3000)
        
        # 2. Buka halaman
        console.print("[cyan]2. Buka All Tiket Open...[/cyan]")
        await page.goto("http://10.2.113.252:8010/roc3/amel/all_tiket_open")
        await page.wait_for_timeout(3000)
        
        # 3. Klik angka pertama buat munculin tabel
        console.print("[cyan]3. Mencari angka pertama...[/cyan]")
        pointer_cells = page.locator("td.pointer")
        count = await pointer_cells.count()
        for i in range(count):
            cell = pointer_cells.nth(i)
            text = await cell.inner_text()
            if text.strip().isdigit() and int(text.strip()) > 0:
                console.print(f"[green]Mengklik angka '{text.strip()}'...[/green]")
                await cell.click()
                await page.wait_for_timeout(5000)
                break

        # 4. Pasang jebakan network SEBELUM klik Bandung
        console.print("[cyan]4. Memasang jebakan Network (Interceptor)...[/cyan]")
        
        async def handle_request(request):
            url = request.url
            # Filter cuma request yang bukan aset statis
            if any(k in url.lower() for k in [".js", ".css", ".png", ".jpg", ".svg", ".woff", ".ico"]):
                return
            console.print(f"[bold yellow]API DITEMUKAN:[/bold yellow] [{request.method}] {url}")
            # Kalo ada data POST, tampilin
            if request.method == "POST":
                try:
                    post_data = request.post_data
                    if post_data:
                        console.print(f"[dim]   Data: {post_data[:200]}...[/dim]")
                except: pass

        page.on("request", lambda req: asyncio.create_task(handle_request(req)))

        # 5. Klik "BANDUNG"
        console.print("[cyan]5. Mencari dan Mengklik 'BANDUNG'...[/cyan]")
        try:
            # Cari teks Bandung (bisa <a>, <button>, <td>, <span>)
            bandung_el = page.locator("text=BANDUNG").first
            if await bandung_el.count() > 0:
                await bandung_el.click()
                console.print("[success]Klik 'BANDUNG' berhasil. Menunggu API...</success>")
                await page.wait_for_timeout(8000) # Tunggu 8 detik
            else:
                console.print("[warning]Teks 'BANDUNG' gak ketemu di halaman.[/warning]")
        except Exception as e:
            console.print(f"[danger]Gagal klik Bandung: {e}[/danger]")

        # 6. Simpan HTML
        html = await page.content()
        with open("Amel/capture_bandung_after_click.html", "w", encoding="utf-8") as f:
            f.write(html)
        console.print("[bold green]✅ HTML disimpan di Amel/capture_bandung_after_click.html[/bold green]")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
