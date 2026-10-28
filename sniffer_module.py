import asyncio
from playwright.async_api import async_playwright
from rich.console import Console
from rich.prompt import Prompt

console = Console()

async def run_sniffer(url_target, username, password):
    async with async_playwright() as p:
        console.print(f"\n[cyan]Membuka browser (Headless) ke {url_target}...[/cyan]")
        
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
                # Tangkap API (JSON/XHR)
                if "json" in content_type or "xhr" in response.request.resource_type or "fetch" in response.request.resource_type:
                    req_info = f"[{method}] {url} | Status: {response.status}"
                    
                    if req_info not in captured_requests:
                        captured_requests.add(req_info)
                        console.print(f"[green]API DITEMUKAN:[/green] {req_info}")
                        
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
            await page.goto(url_target, timeout=15000)
            await page.wait_for_timeout(2000)
        except Exception as e:
            console.print(f"[danger]Gagal buka URL: {e}[/danger]")
            await browser.close()
            return

        # AUTO-LOGIN
        if username and password:
            console.print("[cyan]Mencoba auto-fill form login...[/cyan]")
            try:
                user_field = page.locator("input[type='text'], input[type='email'], input[name*='user'], input[id*='user'], input[name*='email']").first
                if await user_field.count() > 0:
                    await user_field.fill(username)
                    console.print("[success]✅ Username terisi.[/success]")
                
                pass_field = page.locator("input[type='password']").first
                if await pass_field.count() > 0:
                    await pass_field.fill(password)
                    console.print("[success]✅ Password terisi.[/success]")
                
                submit_btn = page.locator("button[type='submit'], input[type='submit'], button:has-text('Login'), button:has-text('Masuk')").first
                if await submit_btn.count() > 0:
                    await submit_btn.click()
                    console.print("[cyan]Menekan tombol Login...[/cyan]")
                    await page.wait_for_timeout(5000)
            except Exception as e:
                console.print(f"[warning]Gagal auto-login: {e}[/warning]")

        console.print("\n[bold yellow]⚠️ Browser berjalan di background (Headless).[/bold yellow]")
        console.print("[bold yellow]Tekan ENTER di terminal ini kalo udah selesai nangkep traffic.[/bold yellow]")
        
        await asyncio.to_thread(input, "")

        if captured_requests:
            with open("api_capture.txt", "w") as f:
                for req in captured_requests:
                    f.write(req + "\n")
            console.print(f"\n[bold green]✅ Selesai! {len(captured_requests)} API disimpan di 'api_capture.txt'[/bold green]")
        else:
            console.print("\n[warning]⚠️ Tidak ada API yang tertangkap.[/warning]")

        await browser.close()
