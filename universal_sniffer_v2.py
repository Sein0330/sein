import asyncio
import os
import json
from playwright.async_api import async_playwright
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table

console = Console()

async def run_universal_sniffer(url):
    if not url.startswith("http"):
        url = "https://" + url
        
    async with async_playwright() as p:
        console.print(Panel(f"[bold cyan]Membuka {url}...[/bold cyan]", title="Web Interceptor"))
        browser = await p.chromium.launch(headless=False, args=["--no-sandbox"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        page = await context.new_page()

        captured_requests = set()
        page.on("response", lambda res: asyncio.create_task(handle_response(res, captured_requests)))

        await page.goto(url)
        await page.wait_for_timeout(3000)
        
        # ================= FASE 1: STATE MACHINE LOOP =================
        step = 1
        has_logged_in = False
        
        while True:
            console.clear()
            console.print(Panel(f"[bold]STEP {step}: ANALISA HALAMAN[/bold]", border_style="cyan"))
            
            # 1. CEK APAKAH INI HALAMAN DASHBOARD
            has_auth_field = False
            auth_keywords = ["password", "otp", "captcha", "verifikasi", "token"]
            
            check_inputs = page.locator("input[type='text'], input[type='password']")
            for i in range(await check_inputs.count()):
                name = (await check_inputs.nth(i).get_attribute("name") or "").lower()
                placeholder = (await check_inputs.nth(i).get_attribute("placeholder") or "").lower()
                if any(k in name for k in auth_keywords) or any(k in placeholder for k in auth_keywords):
                    has_auth_field = True
                    break
            
            if has_logged_in and not has_auth_field:
                console.print("[green]✅ Terdeteksi Halaman Dashboard (Tidak ada form Login).[/green]")
                console.print("[green]✅ Proses Login Selesai. Lanjut ke Auto-Explore![/green]")
                break
                
            # 2. Cari field input
            fields = []
            all_elements = page.locator("input[type='text'], input[type='password'], input[type='email'], select, textarea")
            for i in range(await all_elements.count()):
                el = all_elements.nth(i)
                if await el.is_visible():
                    tag = await el.evaluate("el => el.tagName.toLowerCase()")
                    name = await el.get_attribute("name") or await el.get_attribute("placeholder") or await el.get_attribute("id") or f"Field-{i+1}"
                    
                    if tag == "select":
                        if step == 1:
                            fields.append({"locator": el, "tag": tag, "name": name})
                    else:
                        val = await el.input_value()
                        if not val:
                            fields.append({"locator": el, "tag": tag, "name": name})

            # 3. KALAU GAK ADA INPUT, CEK TOMBOL/LINK
            if not fields:
                console.print("[yellow]⚠️ Tidak ada field input yang terdeteksi.[/yellow]")
                
                await page.keyboard.press("Escape")
                await page.wait_for_timeout(500)
                
                screenshot_bytes = await page.screenshot()
                with open("confirm_page.png", "wb") as f:
                    f.write(screenshot_bytes)
                console.print("[bold green]✅ Screenshot disimpan di 'confirm_page.png'![/bold green]")
                console.print("[yellow]Silakan cek file tersebut untuk melihat halaman.[/yellow]\n")
                
                # CEK TOMBOL / LINK YANG BISA DIKLIK
                clickable_elements = []
                clickables = page.locator("a, button, [role='button'], .btn, .card")
                for i in range(await clickables.count()):
                    el = clickables.nth(i)
                    if await el.is_visible():
                        text = await el.inner_text()
                        if text.strip() and len(text.strip()) < 60: 
                            clickable_elements.append({"locator": el, "text": text.strip()})
                
                if clickable_elements:
                    console.print(f"[bold cyan]Terdeteksi {len(clickable_elements)} tombol/link yang bisa diklik:[/bold cyan]")
                    for idx, btn in enumerate(clickable_elements[:10]): # Batasin 10 aja
                        console.print(f"  [{idx+1}] {btn['text']}")
                        
                    choice = Prompt.ask("\nPilih nomor tombol yang mau diklik (atau ketik 'SKIP' untuk lanjut)", default="SKIP")
                    
                    if choice.upper() != "SKIP" and choice.isdigit():
                        try:
                            target_btn = clickable_elements[int(choice)-1]["locator"]
                            await target_btn.click()
                            console.print("[green]✅ Tombol diklik! Menunggu halaman loading...[/green]")
                            await page.wait_for_timeout(3000)
                            step += 1
                            continue
                        except Exception as e:
                            console.print(f"[danger]Gagal klik tombol: {e}[/danger]")
                
                ask = Prompt.ask("[bold yellow]Apakah ada yang perlu diinput manual (teks)? (y/n)[/bold yellow]", choices=["y", "n"], default="n")
                if ask == "n":
                    console.print("[green]✅ Lanjut ke Auto-Explore.[/green]")
                    break
                else:
                    field_name = Prompt.ask("Nama field (atau 'custom')")
                    field_val = Prompt.ask(f"Nilai untuk '{field_name}'")
                    continue

            # 4. Tampilkan Tabel Field
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("No", style="cyan")
            table.add_column("Tipe", style="yellow")
            table.add_column("Nama Field", style="green")
            for idx, f in enumerate(fields):
                table.add_row(str(idx+1), f["tag"], f["name"])
            console.print(table)

            # 5. SCREENSHOT DULU
            console.print("\n[cyan]Mengambil Screenshot Form...[/cyan]")
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(1000)
            screenshot_bytes = await page.screenshot()
            with open("input_field.png", "wb") as f:
                f.write(screenshot_bytes)
            console.print("[bold green]✅ Screenshot disimpan: 'input_field.png'![/bold green]")
            console.print("[yellow]Silakan buka file input_field.png untuk melihat form/captcha/SSO.[/yellow]")

            # 6. Minta Input Per Field
            for idx, f in enumerate(fields):
                console.print(f"\n[bold cyan]Input data '{f['name']}' ({f['tag']}):[/bold cyan]")
                user_val = Prompt.ask(f"Nilai untuk {f['name']}")
                
                if user_val:
                    try:
                        if f["tag"] == "select":
                            options = await f["locator"].locator("option").all()
                            matched = False
                            for opt in options:
                                txt = await opt.inner_text()
                                val = await opt.get_attribute("value")
                                if user_val.lower() in txt.lower() or user_val.lower() in (val or "").lower():
                                    await f["locator"].select_option(value=val)
                                    matched = True
                                    break
                            if not matched:
                                await f["locator"].select_option(label=user_val)
                        else:
                            await f["locator"].fill(user_val)
                        console.print(f"[green]✅ '{f['name']}' terisi: {user_val}[/green]")
                    except Exception as e:
                        console.print(f"[danger]Gagal isi '{f['name']}': {e}[/danger]")
            
            # 7. Screenshot Konfirmasi
            console.print("\n[cyan]Mengambil Screenshot Konfirmasi...[/cyan]")
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(1000)
            screenshot_bytes = await page.screenshot()
            with open("input_field.png", "wb") as f:
                f.write(screenshot_bytes)
            console.print("[bold green]✅ Screenshot konfirmasi disimpan: 'input_field.png'![/bold green]")
            
            # 8. Konfirmasi
            confirm = Prompt.ask("[bold yellow]Sudah benar semua? (y/n)[/bold yellow]", choices=["y", "n"], default="y")
            if confirm == "n":
                step += 1
                continue
                
            # 9. Klik Tombol Submit
            console.print("\n[cyan]Mengeksekusi klik Submit/Login...[/cyan]")
            submit_selectors = [
                "button[type='submit']", "input[type='submit']",
                "button:has-text('Login')", "button:has-text('Masuk')",
                "button:has-text('Sign In')", "button:has-text('SIGN IN')",
                "button:has-text('Submit')", "button:has-text('Verifikasi')",
                "button:has-text('VERIFIKASI')", "button:has-text('Kirim')",
                "button:has-text('Simpan')", "a:has-text('Login')",
                "button.btn-primary", "button.btn-success"
            ]
            clicked = False
            for sel in submit_selectors:
                btn = page.locator(sel).first
                if await btn.count() > 0 and await btn.is_visible():
                    await btn.click()
                    clicked = True
                    console.print(f"[green]✅ Klik tombol: {sel}[/green]")
                    break
                    
            if not clicked:
                console.print("[warning]⚠️ Gak nemu tombol submit. Coba pencet ENTER di field terakhir...[/warning]")
                try:
                    await fields[-1]["locator"].press("Enter")
                except: pass
                
            has_logged_in = True
            await page.wait_for_timeout(5000)
            step += 1

        # ================= FASE 3: AUTO-EXPLORE =================
        console.print("\n[bold cyan]🔍 Memulai Auto-Explore (Mencari API di menu)...[/bold cyan]")
        links = await page.locator("a").all()
        console.print(f"[cyan]Menemukan {len(links)} link. Memproses 15 link pertama...[/cyan]")
        
        for i, link in enumerate(links[:15]):
            try:
                href = await link.get_attribute("href")
                text = await link.inner_text()
                
                if not href or "javascript:" in href or "logout" in href.lower() or text.strip() == "":
                    continue
                    
                console.print(f"[dim]  [{i+1}] Membuka: {text.strip()}[/dim]")
                base_url = "/".join(url.split("/")[:3])
                full_url = href if href.startswith("http") else base_url + href
                
                await page.goto(full_url)
                await page.wait_for_timeout(3000)
            except: pass
                
        console.print("[bold green]✅ Auto-Explore selesai![/bold green]")
        
        # ================= FASE 4: TUNGGU MANUAL =================
        console.print("\n[bold yellow]⚠️ Browser berjalan di background.[/bold yellow]")
        console.print("[bold yellow]Tekan ENTER setelah lu yakin API selesai ditangkap.[/bold yellow]")
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
    asyncio.run(run_universal_sniffer(url))
