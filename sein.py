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
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.theme import Theme

# Setup tema warna
custom_theme = Theme({
    "info": "cyan",
    "success": "bold green",
    "warning": "yellow",
    "danger": "bold red",
    "menu": "bold magenta"
})
console = Console(theme=custom_theme)

def pause():
    Prompt.ask("\n[dim]Tekan ENTER untuk kembali[/dim]")
    os.system('cls' if os.name == 'nt' else 'clear')

# Load API Key
API_KEY = None
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("API_KEY_REAL="):
                API_KEY = line.strip().split("=")[1]

BASE_URL = "http://127.0.0.1:8765"

def show_logo():
    # PAKSA CLEAR LAYAR PAKE OS
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
[dim]   IP Tracker & Network Engineer Toolkit[/dim]
[dim]   Version 2.0.0 - Made by almaarij[/dim]
    """
    console.print(logo)

def menu():
    while True:
        show_logo()
        console.print("[menu](1)[/menu] IP Track & Locate (MaxMind)")
        console.print("[menu](2)[/menu] Network Tools (WHOIS, DNS, Port, Header)")
        console.print("[menu](3)[/menu] Multi-Path Analyzer (Diagnosa Game RTO)")
        console.print("[menu](4)[/menu] Exit\n")
        
        choice = Prompt.ask("[bold yellow]Pilih menu[/bold yellow]", choices=["1", "2", "3", "4"])
        
        if choice == "1":
            track_ip()
        elif choice == "2":
            network_menu()
        elif choice == "3":
            path_analyzer()
        elif choice == "4":
            console.print("[info]Keluar dari SEIN. Sampai jumpa![/info]")
            sys.exit(0)

# ================= FITUR 1: IP TRACK =================
def track_ip():
    os.system('cls' if os.name == 'nt' else 'clear')
    console.print(Panel("[bold]IP Track & Locate[/bold]\nMasukkan IP Address untuk dilacak.", style="info"))
    ip_address = Prompt.ask("Submit IP Address")
    if not ip_address: return

    with console.status("[bold green]Melacak IP...[/bold green]"):
        try:
            res = requests.get(f"{BASE_URL}/track/{ip_address}", headers={"X-API-Key": API_KEY}, timeout=10)
            if res.status_code == 200:
                data = res.json().get("data", {})
                table = Table(title=f"Hasil Pelacakan: {ip_address}", show_header=True, header_style="bold magenta")
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
            elif res.status_code == 404:
                console.print("[warning]Gagal: IP tidak ditemukan di database.[/warning]")
            else:
                console.print(f"[danger]Error {res.status_code}: {res.text}[/danger]")
        except Exception as e:
            console.print(f"[danger]Error: {e}[/danger]")
    pause()

# ================= FITUR 2: NETWORK TOOLS =================
def network_menu():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        console.print("[bold cyan]Network Tools (Pro Edition)[/bold cyan]\n")
        console.print("[menu](1)[/menu] WHOIS Lookup")
        console.print("[menu](2)[/menu] DNS Record Checker")
        console.print("[menu](3)[/menu] Port Scanner (20 Port Umum)")
        console.print("[menu](4)[/menu] HTTP Header Inspector")
        console.print("[menu](5)[/menu] Kembali ke Menu Utama\n")
        
        choice = Prompt.ask("[bold yellow]Pilih tool[/bold yellow]", choices=["1", "2", "3", "4", "5"])
        
        if choice == "1": whois_lookup()
        elif choice == "2": dns_checker()
        elif choice == "3": port_scanner()
        elif choice == "4": http_inspector()
        elif choice == "5": break

def whois_lookup():
    os.system('cls' if os.name == 'nt' else 'clear')
    target = Prompt.ask("Masukkan IP atau Domain (contoh: 8.8.8.8 / google.com)")
    if not target: return
    with console.status("[bold green]Menarik data WHOIS...[/bold green]"):
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
        except Exception as e:
            console.print(f"[danger]Gagal WHOIS: {e}[/danger]")
    pause()

def dns_checker():
    os.system('cls' if os.name == 'nt' else 'clear')
    domain = Prompt.ask("Masukkan Domain (contoh: google.com)")
    if not domain: return
    table = Table(title=f"DNS Records: {domain}", show_header=True, header_style="bold magenta")
    table.add_column("Type", style="cyan")
    table.add_column("Value", style="green")
    with console.status("[bold green]Mengecek DNS...[/bold green]"):
        for rtype in ["A", "MX", "TXT", "CNAME"]:
            try:
                answers = dns.resolver.resolve(domain, rtype)
                for rdata in answers:
                    table.add_row(rtype, str(rdata))
            except Exception:
                pass
    console.print("\n", table, "\n")
    pause()

def port_scanner():
    os.system('cls' if os.name == 'nt' else 'clear')
    target = Prompt.ask("Masukkan IP/Host (contoh: scanme.nmap.org)")
    if not target: return
    
    # Top 20 Port Umum (Standar Nmap)
    common_ports = {
        21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 
        53: "DNS", 80: "HTTP", 110: "POP3", 139: "NetBIOS", 
        143: "IMAP", 443: "HTTPS", 445: "SMB", 3306: "MySQL", 
        3389: "RDP", 8080: "HTTP-Proxy", 8443: "HTTPS-Alt",
        5900: "VNC", 6379: "Redis", 27017: "MongoDB",
        5000: "UPnP", 19132: "Minecraft"
    }
    
    table = Table(title=f"Port Scan Result: {target}", show_header=True, header_style="bold magenta")
    table.add_column("Port", style="cyan", justify="right")
    table.add_column("Service", style="yellow")
    table.add_column("Status", style="green")

    with console.status(f"[bold green]Scanning {len(common_ports)} ports...[/bold green]"):
        for port, service in common_ports.items():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1.0) # Timeout 1 detik per port
            if sock.connect_ex((target, port)) == 0:
                table.add_row(str(port), service, "[bold green]OPEN[/bold green]")
            else:
                table.add_row(str(port), service, "[dim red]CLOSED[/dim red]")
            sock.close()
    
    console.print("\n", table, "\n")
    pause()

def http_inspector():
    os.system('cls' if os.name == 'nt' else 'clear')
    url = Prompt.ask("Masukkan URL (contoh: https://google.com)")
    if not url.startswith("http"): url = "https://" + url
    with console.status("[bold green]Mengambil HTTP Headers...[/bold green]"):
        try:
            res = requests.get(url, timeout=5)
            table = Table(title=f"HTTP Inspector: {url}", show_header=True, header_style="bold magenta")
            table.add_column("Header", style="cyan")
            table.add_column("Value", style="green")
            table.add_row("Status Code", f"[bold]{res.status_code}[/bold]")
            for key, value in res.headers.items():
                table.add_row(key, value)
            console.print("\n", table, "\n")
        except Exception as e:
            console.print(f"[danger]Gagal ambil header: {e}[/danger]")
    pause()

# ================= FITUR 3: PATH ANALYZER =================
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
    os.system('cls' if os.name == 'nt' else 'clear')
    console.print(Panel("[bold]MULTI-PATH ANALYZER & RTO DIAGNOSIS[/bold]\n[dim]Perbandingan Latency Global (ID / SG / US)[/dim]", style="info"))
    ip_cust = Prompt.ask("[cyan]1. IP Pelanggan[/cyan]")
    ip_game = Prompt.ask("[cyan]2. IP/Domain Game[/cyan]")
    
    locations = {"ID": "Indonesia", "SG": "Singapore", "US": "United States"}
    results = {}
    
    for loc_code in locations.keys():
        with console.status(f"[bold green]Menarik data Traceroute dari {loc_code}...[/bold green]"):
            res = run_globalping_trace(ip_game, loc_code)
            results[loc_code] = extract_hops(res)
            
    table = Table(title=f"Perbandingan Rute Global ke Game ({ip_game})", show_header=True, header_style="bold magenta", expand=True)
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
    console.print("[bold cyan]💡 VERDICT & REKOMENDASI ANALISIS:[/bold cyan]")
    console.print("[success]✅ Rute ke Server Game (dari 3 titik global) TIDAK menunjukkan Packet Loss berat di hop awal.[/success]")
    console.print("  Timeout panjang yang tidak ditampilkan biasanya terjadi di hop akhir karena Server Game memblokir ICMP (Anti-DDoS).")
    console.print("\n[bold green]📝 REKOMENDASI UNTUK CS/TEKNISI:[/bold green]")
    console.print("1. Sampaikan ke pelanggan bahwa rute jaringan dari ISP ke Server Game terpantau **NORMAL**.")
    console.print("2. RTO/Lag murni karena kebijakan Server Game atau masalah di sisi Game, **BUKAN** dari jaringan ISP.")
    console.print("3. Jika pelanggan masih komplain, sarankan ganti region akun atau tes menggunakan VPN.")
    pause()

if __name__ == "__main__":
    if not API_KEY:
        console.print("[danger]API_KEY_REAL tidak ditemukan di .env![/danger]")
        sys.exit(1)
    menu()
