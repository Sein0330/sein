import asyncio
import os
import json
from playwright.async_api import async_playwright
from rich.console import Console
from rich.prompt import Prompt
from rich_pixels import Pixels
from PIL import Image
import io

console = Console()

async def run_universal_sniffer(url, username, password):
    async with async_playwright() as p:
        console.print(f"[cyan]Membuka {url}...[/cyan]")
        # Headless=False + Xvfb (biar mirip browser asli)
        browser = await p.chromium.launch(headless=False, args=["--no-sandbox"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        page = await context.new_page()

        captured_requests = set()
        page.on("response", lambda res: asyncio.create_task(handle_response(res, captured_requests)))

        await page.goto(url)
        await page.wait_for_timeout(2000)
        
        # FASE 1: LOGIN
        console.print("[cyan]Mencoba mengisi form login...[/cyan]")
        try:
            user_field = page.locator("input[type='text'], input[type='email']").first
            pass_field = page.locator("input[type='password']").first
            
            if await user_field.count() > 0:
                await user_field.fill(username)
            if await pass_field.count() > 0:
                await pass_field.fill(password)
                
            submit_btn = page.locator("button[type='submit'], button:has-text('Login')").first
            if await submit_btn.count() > 0:
                await submit_btn.click()
                await page.wait_for_timeout(3000)
        except Exception as e:
            console.print(f"[warning]Gagal auto-fill: {e}[/warning]")

        # FASE 2: SCREENSHOT & MANUAL CHECK (ALa Gladius)
        console.print("\n[cyan]Mengambil Screenshot untuk analisa manual...[/cyan]")
        screenshot_bytes = await page.screenshot()
        
        # Simpen ke file (buat jaga-jaga)
        with open("current_page.png", "wb") as f:
            f.write(screenshot_bytes)
            
        # Tampilin di CLI
        try:
            img = Image.open(io.BytesIO(screenshot_bytes))
            img.thumbnail((80, 80)) # Resize biar muat terminal
            pixels = Pixels.from_image(img)
            console.print("\n[bold yellow]⚠️ CEK LAYAR DI BAWAH:[/bold yellow]")
            console.print(pixels)
        except Exception as e:
            console.print(f"[dim]Gagal render gambar: {e}. Cek file current_page.png[/dim]")
            
        console.print("\n[bold yellow]Jika di layar ada OTP/Captcha, ketik di sini.[/bold yellow]")
        console.print("[dim]Jika tidak ada (sudah masuk dashboard), kosongkan (ENTER).[/dim]")
        
        manual_input = Prompt.ask("Input OTP/Captcha (atau ENTER jika tidak ada)").strip()
        
        if manual_input:
            console.print("[cyan]Mencoba memasukkan input manual...[/cyan]")
            try:
                # Cari input apapun yang kosong (biasanya OTP/Captcha)
                inputs = page.locator("input[type='text']")
                filled = False
                for i in range(await inputs.count()):
                    inp = inputs.nth(i)
                    val = await inp.input_value()
                    if not val: # Kalo kosong, isi
                        await inp.fill(manual_input)
                        filled = True
                        break
                        
                if filled:
                    await page.locator("button[type='submit'], button:has-text('Verifikasi'), button:has-text('Submit')").first.click()
                    await page.wait_for_timeout(3000)
                    console.print("[green]✅ Input manual terkirim![/green]")
                else:
                    console.print("[warning]⚠️ Gak nemu input kosong buat diisi.[/warning]")
            except Exception as e:
                console.print(f"[danger]Gagal input manual: {e}[/danger]")

        # FASE 3: TUNGGU MANUAL
        console.print("\n[bold yellow]⚠️ Browser berjalan di background.[/bold yellow]")
        console.print("[bold yellow]Tekan ENTER setelah lu yakin udah masuk ke halaman utama (dashboard).[/bold yellow]")
        await asyncio.to_thread(input, "")
        
        if captured_requests:
            with open("api_capture.txt", "w") as f:
                for req in captured_requests:
                    f.write(req + "\n")
            console.print(f"[bold green]✅ {len(captured_requests)} API disimpan di api_capture.txt[/bold green]")
        else:
            console.print("[warning]⚠️ Gak ada API yang tertangkap.[/warning]")

        await browser.close()

async def handle_response(response, captured_set):
    try:
        url = response.url
        method = response.request.method
        if any(k in url.lower() for k in [".js", ".css", ".png", ".jpg", ".svg", ".ico", ".woff", ".map"]): return
        
        content_type = response.headers.get("content-type", "")
        if "json" in content_type or "xhr" in response.request.resource_type or "fetch" in response.request.resource_type:
            req_info = f"[{method}] {url} | Status: {response.status}"
            if req_info not in captured_set:
                captured_set.add(req_info)
                console.print(f"[green]API:[/green] {req_info}")
    except: pass

if __name__ == "__main__":
    url = input("URL: ")
    user = input("Username: ")
    pwd = input("Password: ")
    asyncio.run(run_universal_sniffer(url, user, pwd))
