import asyncio
from playwright.async_api import async_playwright
from rich.console import Console
from rich.prompt import Prompt
import os

console = Console()

async def main():
    target_url = Prompt.ask("[cyan]Masukkan URL Web Target[/cyan]").strip()
    if not target_url.startswith("http"):
        target_url = "https://" + target_url

    is_login = Prompt.ask("Apakah web ini butuh login? (y/n)", choices=["y", "n"], default="y")
    username = ""
    password = ""
    
    if is_login == "y":
        username = Prompt.ask("[bold yellow]Masukkan Username[/bold yellow]")
        password = Prompt.ask("[bold yellow]Masukkan Password[/bold yellow]", password=True)

    async with async_playwright() as p:
        console.print(f"\n[cyan]Membuka browser (Headless) ke {target_url}...[/cyan]")
        
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        captured_requests = set()

        async def handle_response(response):
            try:
                url = response.url
                method = response.request.method
                # Filter aset statis
                if any(k in url.lower() for k in [".js", ".css", ".png", ".jpg", ".svg", ".woff", ".ico", ".map", ".gif"]):
                    return
                
                content_type = response.headers.get("content-type", "")
                # TANGKAP API (JSON/XHR) dan halaman HTML (buat cek redirect)
                if "json" in content_type or "xhr" in response.request.resource_type or "text/html" in content_type:
                    req_info = f"[{method}] {url} | Status: {response.status}"
                    
                    if req_info not in captured_requests:
                        captured_requests.add(req_info)
                        console.print(f"[green]DITEMUKAN:[/green] {req_info}")
                        
                        if "json" in content_type and response.status == 200:
                            try:
                                body = await response.text()
                                if body and len(body) < 800:
                                    console.print(f"[dim]{body}[/dim]\n")
                            except: pass
            except: pass

        page.on("response", lambda res: asyncio.create_task(handle_response(res)))

        # Buka URL
        try:
            await page.goto(target_url, timeout=15000)
            await page.wait_for_timeout(2000)
        except Exception as e:
            console.print(f"[danger]Gagal buka URL: {e}[/danger]")
            await browser.close()
            return

        # AUTO-LOGIN
        if is_login == "y":
            console.print("[cyan]Mencoba login otomatis...[/cyan]")
            try:
                # Cari input username (lebih agresif)
                user_field = page.locator("input[type='text'], input[name*='user'], input[id*='user'], input[name*='nik'], input[name*='email']").first
                if await user_field.count() > 0:
                    await user_field.fill(username)
                    console.print("[success]✅ Username terisi.[/success]")
                
                # Cari input password
                pass_field = page.locator("input[type='password']").first
                if await pass_field.count() > 0:
                    await pass_field.fill(password)
                    console.print("[success]✅ Password terisi.[/success]")
                
                # Cari tombol submit
                submit_btn = page.locator("button[type='submit'], input[type='submit'], button:has-text('Login'), button:has-text('Masuk')").first
                if await submit_btn.count() > 0:
                    await submit_btn.click()
                    console.print("[cyan]Menekan tombol Login...[/cyan]")
                    await page.wait_for_timeout(5000) # Tunggu sampe dashboard kebuka
                else:
                    console.print("[warning]⚠️ Tombol login gak ketemu.[/warning]")
            except Exception as e:
                console.print(f"[warning]Gagal auto-login: {e}[/warning]")

        console.print("\n[bold yellow]⚠️ Browser berjalan di background.[/bold yellow]")
        console.print("[bold yellow]Tekan ENTER di terminal ini kalau udah selesai nangkep traffic.[/bold yellow]")
        
        # --- FITUR AUTO EXPLORE ---
        console.print("\n[cyan]Mencoba Auto-Explore (klik menu-menu)...[/cyan]")
        try:
            # Cari semua link <a> yang ada di halaman, buka satu-satu
            links = await page.locator("a").all()
            for link in links[:20]: # Batasi 5 link biar gak kelamaan
                href = await link.get_attribute("href")
                if href and not href.startswith("#") and "logout" not in href.lower():
                    console.print(f"[dim]Membuka link: {href}[/dim]")
                    # Buat nama file dari URL
                    safe_name = href.replace("/", "_").replace("?", "_").replace("=", "_")
                    if not safe_name.endswith(".html"): safe_name += ".html"
                    
                    await page.goto(href if href.startswith("http") else target_url.rsplit('/', 1)[0] + "/" + href)
                    await page.wait_for_timeout(2000)
                    
                    # Simpan HTML-nya
                    html_content = await page.content()
                    with open(f"capture_{safe_name}", "w", encoding="utf-8") as f:
                        f.write(html_content)
                    console.print(f"[dim]   -> HTML disimpan: capture_{safe_name}[/dim]")
        except Exception as e:
            console.print(f"[warning]Auto-explore gagal: {e}[/warning]")

        await asyncio.to_thread(input, "")

        if captured_requests:
            with open("api_capture.txt", "w") as f:
                for req in captured_requests:
                    f.write(req + "\n")
            console.print(f"\n[bold green]✅ Selesai! {len(captured_requests)} API disimpan di 'api_capture.txt'[/bold green]")
        else:
            console.print("\n[warning]⚠️ Tidak ada API yang tertangkap. Coba cek manual pake mode headed (butuh XServer).[/warning]")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
