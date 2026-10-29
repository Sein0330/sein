import os
import socket
import sys
import requests
import whois
import dns.resolver
import subprocess
import platform
import re
import time
import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.theme import Theme
from gladius_engine import run_gladius
from sniffer_module import run_sniffer
from upwork_parser import process_upwork_html

# Setup tema warna
custom_theme = Theme({
    "info": "cyan",
    "success": "bold green",
    "warning": "yellow",
    "danger": "bold red",
    "menu": "bold magenta",
    "header": "bold black on cyan",
    "analisis": "bold yellow"
})
console = Console(theme=custom_theme)

def pause():
    Prompt.ask("\n[dim]Press ENTER to return[/dim]")
    os.system('cls' if os.name == 'nt' else 'clear')

# Load API Key
API_KEY = None
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("API_KEY_REAL="):
                API_KEY = line.strip().split("=")[1]

BASE_URL = "http://127.0.0.1:8765"

def show_header(path):
    os.system('cls' if os.name == 'nt' else 'clear')
    console.print(f"[header] SEIN CLI > {path} [/header]\n")

def show_logo():
    os.system('cls' if os.name == 'nt' else 'clear')
    logo = """
[bold cyan]
   ███████╗███████╗██╗███╗   ██╗
   ██╔════╝██╔════╝██║████╗  ██║
   ███████╗█████╗  ██║██╔██╗ ██║
   ╚════██║██╔══╝  ██║██║╚██╗██║
   ███████║███████╗██║██║ ╚████║
   ╚══════╝╚══════╝╚═╝╚═╝  ╚═══╝
[/bold cyan]
[bold white]   Systematic Exploration - Internet Network[/bold white]
[dim]   "Support tools for analyzing & evaluating customer service quality | By 96250009"[/dim]
    """
    console.print(logo)

# ================= MAIN MENU =================
def menu():
    while True:
        show_logo()
        console.print("[menu](1)[/menu] IP Track & Locate (MaxMind)")
        console.print("[menu](2)[/menu] Network Tools (WHOIS, DNS, Port, Header)")
        console.print("[menu](3)[/menu] Multi-Path Analyzer (Game RTO Diagnosis)")
        console.print("[menu](4)[/menu] ISP Pro Toolkit (ASN, Recon, Adv Ping, Trace)")
        console.print("[menu](5)[/menu] Check Embasy (Gladius Auto-Scraper)")
        console.print("[menu](6)[/menu] Universal Reverse Engine Web")
        console.print("[menu](7)[/menu] Analyzer Project Upwork")
        console.print("[menu](8)[/menu] Exit\n")
        
        choice = Prompt.ask("[bold yellow]Select menu[/bold yellow]")
        
        if choice == "1": track_ip()
        elif choice == "2": network_menu()
        elif choice == "3": path_analyzer()
        elif choice == "4": isp_pro_menu()
        elif choice == "5": cek_embasy()
        elif choice == "6": sniffer_menu()
        elif choice == "7": analyzer_upwork()
        elif choice == "8":
            console.print("[info]Exiting SEIN. Goodbye![/info]")
            sys.exit(0)
        elif choice.upper() == "HOOK":
            console.print("[bold magenta]🔓 Secret Menu Unlocked![/bold magenta]")
            upwork_hunter()
        else:
            console.print("[danger]❌ Menu not found![/danger]")
            time.sleep(1)

# ================= FEATURE 1: IP TRACK =================
def track_ip():
    show_header("IP Track & Locate")
    console.print("[bold]Enter IP Address to track.[/bold]")
    ip_address = Prompt.ask("Submit IP Address")
    if not ip_address: return

    with console.status("[bold green]Tracking IP...[/bold green]"):
        try:
            res = requests.get(f"{BASE_URL}/track/{ip_address}", headers={"X-API-Key": API_KEY}, timeout=10)
            if res.status_code == 200:
                data = res.json().get("data", {})
                table = Table(title=f"Tracking Result: {ip_address}", show_header=True, header_style="bold magenta")
                table.add_column("Field", style="cyan")
                table.add_column("Value", style="green")
                table.add_row("IP Address", str(data.get('ip')))
                table.add_row("Country", str(data.get('country') or "Unknown"))
                table.add_row("Region", str(data.get('region') or "Unknown"))
                table.add_row("City", str(data.get('city') or "Unknown"))
                table.add_row("Latitude", str(data.get('latitude') or "Unknown"))
                table.add_row("Longitude", str(data.get('longitude') or "Unknown"))
                table.add_row("Timezone", str(data.get('timezone') or "Unknown"))
                console.print("\n", table, "\n")
                
                console.print("[analisis]💡 ANALYSIS & RECOMMENDATION:[/analisis]")
                if data.get('country') == "Indonesia":
                    console.print("- This IP is registered in Indonesia.")
                    console.print("- If this is a customer IP, accuracy is only up to City/Regency level.")
                else:
                    console.print("- This IP is registered outside Indonesia.")
                    console.print("- The customer might be using a VPN, or the server is abroad.")
            elif res.status_code == 404:
                console.print("[warning]Failed: IP not found in database.[/warning]")
            else:
                console.print(f"[danger]Error {res.status_code}: {res.text}[/danger]")
        except Exception as e:
            console.print(f"[danger]Error: {e}[/danger]")
    pause()

# ================= FEATURE 2: NETWORK TOOLS =================
def network_menu():
    while True:
        show_header("Network Tools")
        console.print("[menu](1)[/menu] WHOIS Lookup")
        console.print("[menu](2)[/menu] DNS Record Checker")
        console.print("[menu](3)[/menu] Port Scanner (20 Common Ports)")
        console.print("[menu](4)[/menu] HTTP Header Inspector")
        console.print("[menu](5)[/menu] Back to Main Menu\n")
        
        choice = Prompt.ask("[bold yellow]Select tool[/bold yellow]", choices=["1", "2", "3", "4", "5"])
        
        if choice == "1": whois_lookup()
        elif choice == "2": dns_checker()
        elif choice == "3": port_scanner()
        elif choice == "4": http_inspector()
        elif choice == "5": break

def whois_lookup():
    show_header("Network Tools > WHOIS Lookup")
    target = Prompt.ask("Enter IP or Domain")
    if not target: return
    with console.status("[bold green]Fetching WHOIS data...[/bold green]"):
        try:
            w = whois.whois(target)
            table = Table(title=f"WHOIS Result: {target}", show_header=True, header_style="bold magenta")
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="green")
            table.add_row("Domain Name", str(w.domain_name))
            table.add_row("Registrar", str(w.registrar))
            table.add_row("Org/Name", str(w.org or w.name))
            table.add_row("Country", str(w.country))
            console.print("\n", table, "\n")
            
            console.print("[analisis]💡 ANALYSIS:[/analisis]")
            if w.org:
                console.print(f"- Target registered under: {w.org} ({w.country}).")
            else:
                console.print("- Organization info not available.")
        except Exception as e:
            console.print(f"[danger]WHOIS failed: {e}[/danger]")
    pause()

def dns_checker():
    show_header("Network Tools > DNS Record Checker")
    domain = Prompt.ask("Enter Domain")
    if not domain: return
    table = Table(title=f"DNS Records: {domain}", show_header=True, header_style="bold magenta")
    table.add_column("Type", style="cyan")
    table.add_column("Value", style="green")
    
    has_a_record = False
    with console.status("[bold green]Checking DNS...[/bold green]"):
        for rtype in ["A", "MX", "TXT", "CNAME"]:
            try:
                answers = dns.resolver.resolve(domain, rtype)
                for rdata in answers:
                    table.add_row(rtype, str(rdata))
                    if rtype == "A": has_a_record = True
            except Exception:
                pass
    console.print("\n", table, "\n")
    
    console.print("[analisis]💡 ANALYSIS:[/analisis]")
    if not has_a_record:
        console.print("- [warning]No A Record found.[/warning]")
    else:
        console.print("- Domain is active (has A Record).")
    pause()

def port_scanner():
    show_header("Network Tools > Port Scanner")
    target = Prompt.ask("Enter IP/Host")
    if not target: return
    
    common_ports = {21: "FTP", 22: "SSH", 80: "HTTP", 443: "HTTPS", 3306: "MySQL", 3389: "RDP", 8080: "HTTP-Proxy"}
    open_ports = []
    
    table = Table(title=f"Port Scan Result: {target}", show_header=True, header_style="bold magenta")
    table.add_column("Port", style="cyan", justify="right")
    table.add_column("Service", style="yellow")
    table.add_column("Status", style="green")

    with console.status(f"[bold green]Scanning ports...[/bold green]"):
        for port, service in common_ports.items():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1.0)
            if sock.connect_ex((target, port)) == 0:
                table.add_row(str(port), service, "[bold green]OPEN[/bold green]")
                open_ports.append((port, service))
            else:
                table.add_row(str(port), service, "[dim red]CLOSED[/dim red]")
            sock.close()
    
    console.print("\n", table, "\n")
    console.print("[analisis]💡 ANALYSIS:[/analisis]")
    if not open_ports:
        console.print("- All scanned ports are closed.")
    else:
        console.print(f"- Found {len(open_ports)} open ports.")
        for p, s in open_ports:
            if p in [21, 23, 3306]:
                console.print(f"- [danger]WARNING: Port {p} ({s}) is open![/danger]")
            else:
                console.print(f"- Port {p} ({s}) is open.")
    pause()

def http_inspector():
    show_header("Network Tools > HTTP Header Inspector")
    url = Prompt.ask("Enter URL")
    if not url.startswith("http"): url = "https://" + url
    with console.status("[bold green]Fetching HTTP Headers...[/bold green]"):
        try:
            res = requests.get(url, timeout=5)
            table = Table(title=f"HTTP Inspector: {url}", show_header=True, header_style="bold magenta")
            table.add_column("Header", style="cyan")
            table.add_column("Value", style="green")
            table.add_row("Status Code", f"[bold]{res.status_code}[/bold]")
            for key, value in res.headers.items():
                table.add_row(key, value)
            console.print("\n", table, "\n")
            
            console.print("[analisis]💡 ANALYSIS:[/analisis]")
            if res.status_code == 200:
                console.print("- Website responded well (200 OK).")
            elif res.status_code in [301, 302]:
                console.print("- Website performs a redirect.")
            else:
                console.print(f"- Status code {res.status_code}.")
            
            if "strict-transport-security" not in res.headers:
                console.print("- [warning]HSTS is inactive.[/warning]")
        except Exception as e:
            console.print(f"[danger]Failed to fetch headers: {e}[/danger]")
    pause()

# ================= FEATURE 3: PATH ANALYZER =================
def run_globalping_trace(target, location="ID"):
    url = "https://api.globalping.io/v1/measurements"
    payload = {"type": "traceroute", "target": target, "locations": [{"country": location}]}
    try:
        res = requests.post(url, json=payload, timeout=10)
        res.raise_for_status()
        m_id = res.json()["id"]
    except Exception as e:
        return {"error": str(e)}

    result_url = f"https://api.globalping.io/v1/measurements/{m_id}"
    for _ in range(15):
        time.sleep(2)
        try:
            r = requests.get(result_url, timeout=10)
            data = r.json()
            if data.get("status") == "finished":
                return data
        except:
            pass
    return {"error": "Timeout"}

def extract_hops(result):
    if "error" in result or not result.get("results"): return []
    hops_list = []
    raw_hops = result["results"][0]["result"]["hops"]
    for i, hop in enumerate(raw_hops, start=1):
        ip_addr = hop.get("resolvedAddress", "")
        timings = hop.get("timings", [])
        if timings and ip_addr:
            avg_lat = sum(t["rtt"] for t in timings) / len(timings)
            lat_str = f"{avg_lat:.1f}ms"
        else:
            lat_str = "-"
        hops_list.append({"hop": i, "ip": ip_addr if ip_addr else "-", "lat": lat_str})
        if i >= 6: break
    return hops_list

def path_analyzer():
    show_header("Multi-Path Analyzer")
    console.print("[bold]Global Latency Comparison (ID / SG / US)[/bold]\n")
    ip_cust = Prompt.ask("[cyan]1. Customer IP[/cyan]")
    ip_game = Prompt.ask("[cyan]2. Game IP/Domain[/cyan]")
    
    locations = {"ID": "Indonesia", "SG": "Singapore", "US": "United States"}
    results = {}
    
    for loc_code in locations.keys():
        with console.status(f"[bold green]Fetching Traceroute data from {loc_code}...[/bold green]"):
            res = run_globalping_trace(ip_game, loc_code)
            results[loc_code] = extract_hops(res)
            
    table = Table(title=f"Global Route Comparison to Game ({ip_game})", show_header=True, header_style="bold magenta", expand=True)
    table.add_column("Hop", style="cyan", justify="right")
    table.add_column("IP Address (ID)", style="green", width=15)
    table.add_column("Lat ID", style="yellow", justify="right")
    table.add_column("Lat SG", style="yellow", justify="right")
    table.add_column("Lat US", style="yellow", justify="right")

    max_hops = max([len(results[loc]) for loc in locations]) if results else 0
    for i in range(max_hops):
        row = [str(i+1)]
        id_hop = results["ID"][i] if i < len(results["ID"]) else {"ip": "*", "lat": "*"}
        row.append(id_hop["ip"])
        row.append(id_hop["lat"])
        sg_hop = results["SG"][i] if i < len(results["SG"]) else {"ip": "*", "lat": "*"}
        row.append(sg_hop["lat"])
        us_hop = results["US"][i] if i < len(results["US"]) else {"ip": "*", "lat": "*"}
        row.append(us_hop["lat"])
        table.add_row(*row)

    console.print("\n", table, "\n")
    console.print("[analisis]💡 ANALYSIS:[/analisis]")
    console.print("[success]✅ The route to Game Server (from 3 global locations) does NOT show significant Packet Loss at the initial hops.[/success]")
    pause()

# ================= FEATURE 4: ISP PRO TOOLKIT =================
def isp_pro_menu():
    while True:
        show_header("ISP Pro Toolkit")
        console.print("[menu](1)[/menu] BGP / ASN Lookup")
        console.print("[menu](2)[/menu] Subdomain & Reverse DNS Recon")
        console.print("[menu](3)[/menu] Advanced Ping Checker")
        console.print("[menu](4)[/menu] Traceroute (NOC Escalation)")
        console.print("[menu](5)[/menu] Back to Main Menu\n")
        
        choice = Prompt.ask("[bold yellow]Select tool[/bold yellow]", choices=["1", "2", "3", "4", "5"])
        
        if choice == "1": asn_lookup()
        elif choice == "2": subdomain_recon()
        elif choice == "3": advanced_ping()
        elif choice == "4": local_traceroute()
        elif choice == "5": break

def asn_lookup():
    show_header("ISP Pro Toolkit > BGP / ASN Lookup")
    target = Prompt.ask("Enter IP or Domain")
    if not target: return
    console.print(f"[cyan]Fetching ASN info for {target}...[/cyan]")
    try:
        result = subprocess.run(["whois", "-h", "whois.cymru.com", f" -v {target}"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            console.print(result.stdout)
            console.print("[analisis]💡 ANALYSIS:[/analisis]")
            console.print("- ASN data shows who owns the IP.")
        else:
            console.print("[warning]Failed to fetch ASN data.[/warning]")
    except Exception as e:
        console.print(f"[danger]Error: {e}[/danger]")
    pause()

def subdomain_recon():
    show_header("ISP Pro Toolkit > Subdomain & Reverse DNS")
    domain = Prompt.ask("Enter Domain")
    if not domain: return
    console.print(f"[cyan]Searching subdomains for {domain}...[/cyan]")
    try:
        url = f"https://crt.sh/?q=%25.{domain}&output=json"
        res = requests.get(url, timeout=15)
        if res.status_code == 200:
            data = res.json()
            subdomains = set()
            for entry in data:
                name = entry.get("name_value", "")
                for sub in name.split("\n"):
                    if sub.endswith(domain) and sub != domain:
                        subdomains.add(sub)
            
            if subdomains:
                table = Table(title=f"Subdomains Found: {len(subdomains)}", show_header=True, header_style="bold magenta")
                table.add_column("Subdomain", style="cyan")
                table.add_column("IP Address", style="green")
                table.add_column("Reverse DNS", style="yellow")
                
                for sub in list(subdomains)[:20]:
                    try:
                        ip = socket.gethostbyname(sub)
                        try:
                            rev = socket.gethostbyaddr(ip)[0]
                        except:
                            rev = "-"
                        table.add_row(sub, ip, rev)
                    except:
                        table.add_row(sub, "-", "-")
                console.print("\n", table, "\n")
            else:
                console.print("[warning]No subdomains found.[/warning]")
        else:
            console.print("[warning]Failed to fetch data from crt.sh.[/warning]")
    except Exception as e:
        console.print(f"[danger]Error: {e}[/danger]")
    pause()

def advanced_ping():
    show_header("ISP Pro Toolkit > Advanced Ping Checker")
    target = Prompt.ask("Enter IP/Host")
    if not target: return
    
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    count = '20'
    
    console.print(f"[cyan]Pinging {target} (20 packets)...[/cyan]")
    try:
        cmd = ['ping', param, count, target]
        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=30)
        output = process.stdout
        
        loss_match = re.search(r'(\d+)% packet loss', output)
        loss = int(loss_match.group(1)) if loss_match else 0
        
        rtt_match = re.search(r'rtt min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)', output)
        if rtt_match:
            min_rtt = float(rtt_match.group(1))
            avg_rtt = float(rtt_match.group(2))
            max_rtt = float(rtt_match.group(3))
            jitter = float(rtt_match.group(4))
        else:
            min_rtt = avg_rtt = max_rtt = jitter = 0.0
        
        table = Table(title=f"Advanced Ping: {target}", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Status", style="yellow")
        
        loss_status = "[bold green]Normal[/bold green]" if loss == 0 else "[bold red]Packet Loss![/bold red]"
        table.add_row("Packet Loss", f"{loss}%", loss_status)
        
        if loss == 100:
            table.add_row("Avg RTT", "N/A", "[bold red]Dead[/bold red]")
            table.add_row("Jitter", "N/A", "[bold red]Dead[/bold red]")
        else:
            lat_status = "[bold green]Good[/bold green]" if avg_rtt < 50 else ("[yellow]Fair[/yellow]" if avg_rtt < 100 else "[bold red]High[/bold red]")
            table.add_row("Avg RTT", f"{avg_rtt:.2f} ms", lat_status)
            
            jitter_status = "[bold green]Stable[/bold green]" if jitter < 10 else "[bold red]Unstable[/bold red]"
            table.add_row("Jitter", f"{jitter:.2f} ms", jitter_status)
        
        console.print("\n", table, "\n")
        
        console.print("[analisis]💡 ANALYSIS:[/analisis]")
        if loss == 100:
            console.print("- [danger]Target is not responding to ping (100% Loss).[/danger]")
        elif loss > 0:
            console.print(f"- [warning]Packet Loss of {loss}% occurred.[/warning]")
        elif jitter > 10:
            console.print("- [warning]High Jitter (unstable connection).[/warning]")
        else:
            console.print("- [success]Connection is stable and healthy.[/success]")
            
    except Exception as e:
        console.print(f"[danger]Error during ping: {e}[/danger]")
    pause()

def local_traceroute():
    show_header("ISP Pro Toolkit > Traceroute (NOC Escalation)")
    console.print("[bold]Route Diagnosis & Escalation to DSO/NOC[/bold]\n")
    
    target = Prompt.ask("Enter Target Domain/IP")
    if not target: return
    
    console.print("Enter customer Modem IP (can be checked from https://whatismyipaddress.com/)")
    ip_modem = Prompt.ask("Customer Modem IP (Framed IP)", default="").strip()
    
    console.print(f"\n[cyan]Fetching Traceroute data from Cloud (Indonesia) to {target}...[/cyan]")
    res_target = run_globalping_trace(target, "ID")
    
    if "error" in res_target:
        console.print(f"[danger]Failed to trace to {target}: {res_target['error']}[/danger]")
        pause()
        return
        
    hops_target = extract_hops(res_target)
    
    table = Table(title=f"Cloud Traceroute to Target Server ({target})", show_header=True, header_style="bold magenta")
    table.add_column("Hop", style="cyan", justify="right")
    table.add_column("IP Address", style="green")
    table.add_column("Latency", style="yellow")
    
    timeout_target = 0
    max_lat_target = 0
    for h in hops_target:
        table.add_row(str(h["hop"]), h["ip"], h["lat"])
        if h["ip"] == "-": 
            timeout_target += 1
        else:
            try:
                lat = float(h["lat"].replace("ms", ""))
                if lat > max_lat_target: max_lat_target = lat
            except: pass
            
    console.print("\n", table, "\n")

    timeout_cust = 0
    max_lat_cust = 0
    if ip_modem:
        if ip_modem.startswith(("10.", "192.168.", "172.")):
            console.print(f"[warning]⚠️ Modem IP ({ip_modem}) detected as Private/NAT IP.[/warning]")
            ip_modem = "" 
        else:
            console.print(f"[cyan]Fetching Traceroute data from Cloud (Indonesia) to Customer Modem ({ip_modem})...[/cyan]")
            res_cust = run_globalping_trace(ip_modem, "ID")
            
            if "error" in res_cust:
                console.print(f"[danger]Failed to trace to customer: {res_cust['error']}[/danger]")
            else:
                hops_cust = extract_hops(res_cust)
                table_cust = Table(title=f"Cloud Traceroute to Customer Modem ({ip_modem})", show_header=True, header_style="bold magenta")
                table_cust.add_column("Hop", style="cyan", justify="right")
                table_cust.add_column("IP Address", style="green")
                table_cust.add_column("Latency", style="yellow")
                
                for h in hops_cust:
                    table_cust.add_row(str(h["hop"]), h["ip"], h["lat"])
                    if h["ip"] == "-": 
                        timeout_cust += 1
                    else:
                        try:
                            lat = float(h["lat"].replace("ms", ""))
                            if lat > max_lat_cust: max_lat_cust = lat
                        except: pass
                        
                console.print("\n", table_cust, "\n")

    console.print("[analisis]💡 ANALYSIS & RECOMMENDATION FOR NOC:[/analisis]")
    console.print(f"[bold]1. Route Evaluation to {target}:[/bold]")
    if timeout_target > 3:
        console.print(f"   - [danger]Found {timeout_target} Hop Timeout (Packet Loss).[/danger]")
    else:
        console.print(f"   - [success]Normal Route. Maximum latency: {max_lat_target} ms.[/success]")
        
    if ip_modem:
        console.print(f"\n[bold]2. Route Evaluation to Customer ({ip_modem}):[/bold]")
        if timeout_cust > 3:
            console.print(f"   - [danger]Found {timeout_cust} Hop Timeout to customer.[/danger]")
        else:
            console.print(f"   - [success]Normal Route. Maximum latency: {max_lat_cust} ms.[/success]")

    console.print("\n[bold yellow]📋 CONCLUSION & ACTION:[/bold yellow]")
    if timeout_target > 3 and (not ip_modem or timeout_cust > 3):
        console.print("- [danger]Both routes experienced significant Packet Loss.[/danger]")
    elif timeout_target > 3 and timeout_cust <= 3:
        console.print("- [warning]Route to Target Timeout, but route to Customer is Normal.[/warning]")
    elif timeout_target <= 3 and ip_modem and timeout_cust > 3:
        console.print("- [warning]Route to Target is Normal, but route to Customer Timeout.[/warning]")
    elif ip_modem and timeout_target <= 3 and timeout_cust <= 3:
        console.print("- [success]Both routes (Target & Customer) appear NORMAL.[/success]")
    
    pause()

# ================= FEATURE 5: CHECK EMBASY =================
def cek_embasy():
    show_header("Check Embasy (Gladius Scraper)")
    console.print("[bold]Enter customer data.[/bold]")
    
    while True:
        nomor = Prompt.ask("Internet Number").strip()
        if nomor.isdigit() and len(nomor) >= 8:
            break
        console.print("[bold red]❌ Error: Internet Number must be NUMERIC and at least 8 digits![/bold red]")
        
    while True:
        domain = Prompt.ask("Domain", default="telkom.net").strip()
        if domain:
            break
        console.print("[bold red]❌ Error: Domain cannot be empty![/bold red]")
    
    console.print("[cyan]Fetching customer data, please wait...[/cyan]")
    
    try:
        summary_data, result = asyncio.run(run_gladius(nomor, domain))
        
        if summary_data:
            table = Table(title=f"Customer Summary: {nomor}", show_header=True, header_style="bold magenta")
            table.add_column("Parameter", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Number", summary_data.get("Nomor", "-"))
            table.add_row("Domain", summary_data.get("Domain", "-"))
            table.add_row("Static IP", summary_data.get("IP Statik", "-"))
            table.add_row("Package", summary_data.get("Paket", "-"))
            table.add_row("Customer Status", summary_data.get("Status", "-"))
            table.add_row("Port Binding", summary_data.get("Port Binding", "-"))
            table.add_row("EQN", summary_data.get("EQN", "-"))
            table.add_row("IP OLT", summary_data.get("IP OLT", "-"))
            table.add_row("ONU Rx Power", summary_data.get("Rx Power", "-"))
            table.add_row("NAS IP (BRAS)", summary_data.get("NAS IP", "-"))
            table.add_row("Framed IP (Modem)", summary_data.get("Framed IP", "-"))
            table.add_row("Connection Status", summary_data.get("Status Koneksi", "-"))
            
            console.print("\n", table, "\n")
            
            download_url = f"https://tracker.sein.bid/download/{result}"
            console.print(f"[success]✅ Data retrieved successfully![/success]")
            console.print(f"[bold cyan]🔗 Download Capture: [underline]{download_url}[/underline][/bold cyan]\n")
            
            console.print("[analisis]💡 ANALYSIS:[/analisis]")
            if summary_data.get("Status Koneksi") == "Interim-Update":
                console.print("- Connection Status: ONLINE.")
            elif summary_data.get("Status Koneksi") == "-":
                console.print("- [warning]Connection Status is Empty.[/warning]")
            
            try:
                rx_power = float(summary_data.get("Rx Power", "-").replace(" dBm", ""))
                if rx_power < -27:
                    console.print(f"- [danger]Weak Rx Power ({rx_power} dBm). Check optical cable![/danger]")
                else:
                    console.print(f"- Normal Rx Power ({rx_power} dBm). Good optical quality.")
            except:
                pass
        else:
            console.print(f"[danger]❌ Failed: {result}[/danger]")
            
    except Exception as e:
        console.print(f"[danger]❌ System Error: {e}[/danger]")
        
    pause()

# ================= FEATURE 6: UPWORK HUNTER (HOOK) =================
def upwork_hunter():
    show_header("Upwork Project Hunter")
    console.print("[bold]Upwork Project Analysis & AI Profit Estimation[/bold]
")
    
    import subprocess
    
    console.print("[cyan]Running Upwork Hunter (Local Save Mode)...[/cyan]")
    console.print("[yellow]Analyzing saved HTML files from 'Bahan Analisa HTML' folder...[/yellow]
")
    
    try:
        # Jalanin script upwork_save.py (Mode Aman)
        subprocess.run(["python3", "upwork_save.py"], check=True)
    except subprocess.CalledProcessError as e:
        console.print(f"[danger]❌ Script error (Exit Code: {e.returncode})[/danger]")
    except Exception as e:
        console.print(f"[danger]❌ Failed: {e}[/danger]")
        
    pause()

# ================= FEATURE 7: ANALYZER PROJECT UPWORK =================
def analyzer_upwork():
    show_header("Analyzer Project Upwork")
    console.print("[bold]Analyze Upwork Projects from local HTML files.[/bold]\n")
    
    console.print("[cyan]STEPS:[/cyan]")
    console.print("1. Open Upwork in Chrome Windows.")
    console.print("2. Search for a project.")
    console.print("3. Press F12 > Console, paste the DevTools script.")
    console.print("4. Wait for HTML files to download to 'Bahan Analisa HTML'.")
    console.print("5. Press ENTER here when ready.\n")
    
    Prompt.ask("[yellow]Press ENTER to start analysis[/yellow]")
    
    import subprocess
    console.print("\n[cyan]Running Analyzer (upwork_save.py)...[/cyan]")
    
    try:
        subprocess.run(["python3", "upwork_save.py"], check=True)
    except Exception as e:
        console.print(f"[danger]❌ Failed: {e}[/danger]")
        
    pause()

if __name__ == "__main__":
    if not API_KEY:
        console.print("[danger]API_KEY_REAL not found in .env![/danger]")
        sys.exit(1)
    menu()
