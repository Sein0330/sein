import asyncio
import os
import time
from playwright.async_api import async_playwright
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table

console = Console()

async def run_sniffer(url):
    if not url.startswith("http"):
        url = "https://" + url
        
    async with async_playwright() as p:
        console.print(Panel(f"[bold cyan]Opening {url}...[/bold cyan]", title="Web Interceptor v3"))
        browser = await p.chromium.launch(headless=False, args=["--no-sandbox"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        captured_requests = set()
        page.on("response", lambda res: asyncio.create_task(handle_response(res, captured_requests)))

        await page.goto(url)
        await page.wait_for_timeout(3000)
        
        step = 1
        while True:
            console.clear()
            console.print(Panel(f"[bold]STEP {step}: PAGE ANALYSIS[/bold]", border_style="cyan"))
            
            # 1. Look for input forms
            fields = []
            inputs = page.locator("input[type='text'], input[type='password'], input[type='email'], select, textarea")
            for i in range(await inputs.count()):
                el = inputs.nth(i)
                if await el.is_visible():
                    tag = await el.evaluate("el => el.tagName.toLowerCase()")
                    name = await el.get_attribute("name") or await el.get_attribute("placeholder") or f"Field-{i+1}"
                    if tag == "select" or not await el.input_value():
                        fields.append({"locator": el, "tag": tag, "name": name})

            # 2. If fields found, process them
            if fields:
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("No", style="cyan")
                table.add_column("Type", style="yellow")
                table.add_column("Field Name", style="green")
                for idx, f in enumerate(fields):
                    table.add_row(str(idx+1), f["tag"], f["name"])
                console.print(table)
                
                await page.keyboard.press("Escape")
                await page.wait_for_timeout(1000)
                await page.screenshot(path="input_field.png")
                
                timestamp = int(time.time())
                download_url = f"https://tracker.sein.bid/download/input_field.png?t={timestamp}"
                console.print(f"\n[bold green]✅ Screenshot saved![/bold green]")
                console.print(f"[bold cyan]🔗 Open in browser: [underline]{download_url}[/underline][/bold cyan]\n")
                
                for idx, f in enumerate(fields):
                    val = Prompt.ask(f"Value for {f['name']}").strip()
                    if val:
                        try:
                            if f["tag"] == "select":
                                await f["locator"].select_option(label=val)
                            else:
                                await f["locator"].fill(val)
                        except: pass
                
                await page.wait_for_timeout(1000)
                await page.screenshot(path="input_field.png")
                timestamp = int(time.time())
                download_url = f"https://tracker.sein.bid/download/input_field.png?t={timestamp}"
                console.print(f"\n[bold green]✅ Form filled. Latest screenshot saved![/bold green]")
                console.print(f"[bold cyan]🔗 Open in browser to verify: [underline]{download_url}[/underline][/bold cyan]\n")
                
                confirm = Prompt.ask("[yellow]Is everything correct? (y/n)[/yellow]", default="y")
                if confirm == "n":
                    step += 1
                    continue
                
                # Submit
                console.print("[cyan]Clicking Submit...[/cyan]")
                for sel in ["button[type='submit']", "button:has-text('Login')", "button:has-text('Sign In')", "button:has-text('Submit')", "button.btn-primary"]:
                    btn = page.locator(sel).first
                    if await btn.count() > 0 and await btn.is_visible():
                        await btn.click()
                        break
                await page.wait_for_timeout(5000)
                step += 1
                continue

            # 3. No fields, look for buttons/links
            console.print("[yellow]⚠️ No input forms detected. Searching for buttons/links...[/yellow]")
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(1000)
            await page.screenshot(path="confirm_page.png")
            
            timestamp = int(time.time())
            download_url = f"https://tracker.sein.bid/download/confirm_page.png?t={timestamp}"
            console.print(f"[bold green]✅ Screenshot: confirm_page.png![/bold green]")
            console.print(f"[bold cyan]🔗 Open in browser: [underline]{download_url}[/underline][/bold cyan]\n")

            # Find buttons
            buttons = []
            clickables = page.locator("a, button, .btn, .card, [role='button']")
            count = await clickables.count()
            for i in range(count):
                el = clickables.nth(i)
                if await el.is_visible():
                    text = await el.inner_text()
                    if text.strip() and len(text.strip()) < 60:
                        buttons.append({"locator": el, "text": text.strip()})

            # If no buttons, scan text
            if not buttons:
                all_elements = page.locator("div, span, h1, h2, h3, h4, h5, h6, p")
                for i in range(await all_elements.count()):
                    el = all_elements.nth(i)
                    try:
                        if await el.is_visible():
                            text = await el.inner_text()
                            if text.strip() and 3 < len(text.strip()) < 40:
                                children = await el.locator("*").count()
                                if children == 0: 
                                    buttons.append({"locator": el, "text": text.strip()})
                    except: pass
                    
                unique_buttons = []
                seen_texts = set()
                for b in buttons:
                    if b["text"] not in seen_texts:
                        unique_buttons.append(b)
                        seen_texts.add(b["text"])
                buttons = unique_buttons

            if buttons:
                console.print(f"[bold cyan]Detected {len(buttons)} buttons/links:[/bold cyan]")
                for idx, btn in enumerate(buttons[:10]):
                    console.print(f"  [{idx+1}] {btn['text']}")
                
                choice = Prompt.ask("\nSelect button number (or 'SKIP' to finish)", default="SKIP")
                
                if choice.upper() == "SKIP":
                    console.print("[cyan]Skipping button selection. Proceeding to Auto-Explore...[/cyan]")
                    break
                elif choice.isdigit():
                    try:
                        target = buttons[int(choice)-1]["locator"]
                        await target.click()
                        console.print("[green]✅ Button clicked! Waiting for page...[/green]")
                        await page.wait_for_timeout(5000)
                        step += 1
                        continue
                    except Exception as e:
                        console.print(f"[red]Failed to click: {e}[/red]")
            else:
                console.print("[red]❌ No clickable buttons/links found.[/red]")
                ask = Prompt.ask("[yellow]Is this the final page? (y/n)[/yellow]", default="y")
                if ask == "y":
                    break

        # ================= AUTO EXPLORE =================
        console.print("\n[bold cyan]🔍 Auto-Exploring APIs...[/bold cyan]")
        links = await page.locator("a").all()
        for i, link in enumerate(links[:15]):
            try:
                href = await link.get_attribute("href")
                if not href or "javascript:" in href or "logout" in href.lower():
                    continue
                base_url = "/".join(url.split("/")[:3])
                full_url = href if href.startswith("http") else base_url + href
                await page.goto(full_url)
                await page.wait_for_timeout(3000)
            except: pass
            
        console.print(f"[green]✅ Finished! {len(captured_requests)} APIs found.[/green]")
        
        with open("api_capture.txt", "w") as f:
            for req in captured_requests:
                f.write(req + "\n")
                
        await asyncio.to_thread(input, "\nPress ENTER to close browser...\n")
        await browser.close()

async def handle_response(response, captured_set):
    try:
        url = response.url
        if any(k in url.lower() for k in [".js", ".css", ".png", ".jpg", ".svg", ".ico", ".woff"]): return
        content_type = response.headers.get("content-type", "")
        if "json" in content_type or "xhr" in response.request.resource_type:
            req_info = f"[{response.request.method}] {url} | Status: {response.status}"
            if req_info not in captured_set:
                captured_set.add(req_info)
                console.print(f"[green]API:[/green] {req_info}")
    except: pass

if __name__ == "__main__":
    url = input("URL: ")
    asyncio.run(run_sniffer(url))
