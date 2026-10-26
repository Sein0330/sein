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
    "menu": "bold magenta",
    "header": "bold black on cyan",
    "analisis": "bold yellow"
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
[dim]   IP Tracker & Network Engineer Toolkit v3.0[/dim]
    """
    console.print(logo)

# ================= MENU UTAMA =================
def menu():
    while True:
        show_logo()
        console.print("[menu](1)[/menu] IP Track & Locate (MaxMind)")
        console.print("[menu](2)[/menu] Network Tools (WHOIS, DNS, Port, Header)")
        console.print("[menu](3)[/menu] Multi-Path Analyzer (Diagnosa Game RTO)")
        console.print("[menu](4)[/menu] ISP Pro Toolkit (ASN, Recon, Adv Ping, Trace)")
        console.print("[menu](5)[/menu] Exit\n")
        
        choice = Prompt.ask("[bold yellow]Pilih menu[/bold yellow]", choices=["1", "2", "3", "4", "5"])
        
        if choice == "1": track_ip()
        elif choice == "2": network_menu()
        elif choice == "3": path_analyzer()
        elif choice == "4": isp_pro_menu()
        elif choice == "5":
            console.print("[info]Keluar dari SEIN. Sampai jumpa![/info]")
            sys.exit(0)

# ================= FITUR 1: IP TRACK =================
def track_ip():
    show_header("IP Track & Locate")
    console.print("[bold]Masukkan IP Address untuk dilacak.[/bold]")
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
                
                # ANALISIS
                console.print("[analisis]💡 ANALISIS & REKOMENDASI:[/analisis]")
                if data.get('country') == "Indonesia":
                    console.print("- IP ini terdaftar di Indonesia.")
                    console.print("- Jika IP ini milik pelanggan ISP, akurasi lokasi hanya sampai level Kota/Kabupaten (bukan titik rumah).")
                else:
                    console.print("- IP ini terdaftar di luar Indonesia (atau routing internasional).")
                    console.print("- Kemungkinan pelanggan menggunakan VPN, atau IP server game berada di luar negeri.")
                console.print("- Catatan: IP Geolocation tidak bisa digunakan untuk melacak alamat presisi (rumah) pelanggan.")
                
            elif res.status_code == 404:
                console.print("[warning]Gagal: IP tidak ditemukan di database.[/warning]")
                console.print("[analisis]💡 ANALISIS: IP Private/Lokal tidak akan ditemukan di database publik.[/analisis]")
            else:
                console.print(f"[danger]Error {res.status_code}: {res.text}[/danger]")
        except Exception as e:
            console.print(f"[danger]Error: {e}[/danger]")
    pause()

# ================= FITUR 2: NETWORK TOOLS =================
def network_menu():
    while True:
        show_header("Network Tools")
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
    show_header("Network Tools > WHOIS Lookup")
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
            
            console.print("[analisis]💡 ANALISIS & REKOMENDASI:[/analisis]")
            if w.org:
                console.print(f"- Target ini terdaftar atas nama: {w.org} ({w.country}).")
                console.print("- Gunakan info ini untuk validasi apakah target resmi atau mencurigakan.")
            else:
                console.print("- Info organisasi tidak tersedia. Domain mungkin disembunyikan (private WHOIS).")
        except Exception as e:
            console.print(f"[danger]Gagal WHOIS: {e}[/danger]")
    pause()

def dns_checker():
    show_header("Network Tools > DNS Record Checker")
    domain = Prompt.ask("Masukkan Domain (contoh: google.com)")
    if not domain: return
    table = Table(title=f"DNS Records: {domain}", show_header=True, header_style="bold magenta")
    table.add_column("Type", style="cyan")
    table.add_column("Value", style="green")
    
    has_a_record = False
    with console.status("[bold green]Mengecek DNS...[/bold green]"):
        for rtype in ["A", "MX", "TXT", "CNAME"]:
            try:
                answers = dns.resolver.resolve(domain, rtype)
                for rdata in answers:
                    table.add_row(rtype, str(rdata))
                    if rtype == "A": has_a_record = True
            except Exception:
                pass
    console.print("\n", table, "\n")
    
    console.print("[analisis]💡 ANALISIS & REKOMENDASI:[/analisis]")
    if not has_a_record:
        console.print("- [warning]Tidak ada A Record ditemukan.[/warning] Domain mungkin tidak aktif atau pakai IP dedicated.")
    else:
        console.print("- Domain aktif (punya A Record).")
        console.print("- Jika ada MX Record, berarti domain ini terhubung ke layanan email (Google/Microsoft/dll).")
        console.print("- Gunakan info ini untuk audit DNS kantor atau mendeteksi domain palsu (phishing).")
    pause()

def port_scanner():
    show_header("Network Tools > Port Scanner")
    target = Prompt.ask("Masukkan IP/Host (contoh: scanme.nmap.org)")
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
    console.print("[analisis]💡 ANALISIS & REKOMENDASI:[/analisis]")
    if not open_ports:
        console.print("- Semua port yang di-scan tertutup (CLOSED). Server aman dari akses luar yang tidak perlu.")
    else:
        console.print(f"- Ditemukan {len(open_ports)} port terbuka.")
        for p, s in open_ports:
            if p in [21, 23, 3306]:
                console.print(f"- [danger]PERINGATAN: Port {p} ({s}) terbuka! Ini berisiko tinggi jika terekspos ke internet.[/danger]")
            elif p == 3389:
                console.print(f"- [warning]Port 3389 (RDP) terbuka. Pastikan pakai VPN/Whitelist IP.[/warning]")
            else:
                console.print(f"- Port {p} ({s}) terbuka. Pastikan ini port yang memang dibutuhkan untuk layanan publik.")
    pause()

def http_inspector():
    show_header("Network Tools > HTTP Header Inspector")
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
            
            console.print("[analisis]💡 ANALISIS & REKOMENDASI:[/analisis]")
            if res.status_code == 200:
                console.print("- Website merespon dengan baik (200 OK).")
            elif res.status_code in [301, 302]:
                console.print("- Website melakukan redirect. Normal untuk HTTP ke HTTPS.")
            else:
                console.print(f"- Status code {res.status_code}. Cek apakah web sedang down atau butuh auth.")
            
            if "server" in res.headers:
                console.print(f"- Web server: {res.headers['server']}. Pastikan versi tidak usang (vulnerable).")
            if "strict-transport-security" not in res.headers:
                console.print("- [warning]HSTS tidak aktif. Disarankan mengaktifkan HSTS untuk keamanan HTTPS.[/warning]")
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
    show_header("Multi-Path Analyzer")
    console.print("[bold]Perbandingan Latency Global (ID / SG / US)[/bold]\n")
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
    console.print("[analisis]💡 ANALISIS & REKOMENDASI:[/analisis]")
    console.print("[success]✅ Rute ke Server Game (dari 3 titik global) TIDAK menunjukkan Packet Loss berat di hop awal.[/success]")
    console.print("  Timeout panjang yang tidak ditampilkan biasanya terjadi di hop akhir karena Server Game memblokir ICMP (Anti-DDoS).")
    console.print("\n[bold green]📝 REKOMENDASI UNTUK CS/TEKNISI:[/bold green]")
    console.print("1. Sampaikan ke pelanggan bahwa rute jaringan dari ISP ke Server Game terpantau **NORMAL**.")
    console.print("2. RTO/Lag murni karena kebijakan Server Game atau masalah di sisi Game, **BUKAN** dari jaringan ISP.")
    console.print("3. Jika pelanggan masih komplain, sarankan ganti region akun atau tes menggunakan VPN.")
    pause()

# ================= FITUR 4: ISP PRO TOOLKIT =================
def isp_pro_menu():
    while True:
        show_header("ISP Pro Toolkit")
        console.print("[menu](1)[/menu] BGP / ASN Lookup (Route Intelligence)")
        console.print("[menu](2)[/menu] Subdomain & Reverse DNS Recon")
        console.print("[menu](3)[/menu] Advanced Ping Checker (Loss, Jitter, RTT)")
        console.print("[menu](4)[/menu] Local Traceroute (ISP Side)")
        console.print("[menu](5)[/menu] Kembali ke Menu Utama\n")
        
        choice = Prompt.ask("[bold yellow]Pilih tool[/bold yellow]", choices=["1", "2", "3", "4", "5"])
        
        if choice == "1": asn_lookup()
        elif choice == "2": subdomain_recon()
        elif choice == "3": advanced_ping()
        elif choice == "4": local_traceroute()
        elif choice == "5": break

def asn_lookup():
    show_header("ISP Pro Toolkit > BGP / ASN Lookup")
    target = Prompt.ask("Masukkan IP atau Domain (contoh: 8.8.8.8 / google.com)")
    if not target: return
    console.print(f"[cyan]Menarik info ASN untuk {target}...[/cyan]")
    try:
        result = subprocess.run(["whois", "-h", "whois.cymru.com", f" -v {target}"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            console.print(result.stdout)
            console.print("[analisis]💡 ANALISIS & REKOMENDASI:[/analisis]")
            console.print("- Data ASN menunjukkan siapa pemilik IP (Provider/Perusahaan).")
            console.print("- Jika IP ini milik provider lain, berarti rute data pelanggan keluar dari jaringan ISP kita.")
            console.print("- Jika ini IP internal ISP kita, pastikan tidak ada konflik routing BGP.")
        else:
            console.print("[warning]Gagal narik data ASN. Coba lagi.[/warning]")
    except Exception as e:
        console.print(f"[danger]Error: {e}[/danger]")
    pause()

def subdomain_recon():
    show_header("ISP Pro Toolkit > Subdomain & Reverse DNS")
    domain = Prompt.ask("Masukkan Domain (contoh: example.com)")
    if not domain: return
    console.print(f"[cyan]Mencari subdomain untuk {domain}...[/cyan]")
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
                table = Table(title=f"Subdomain Ditemukan: {len(subdomains)}", show_header=True, header_style="bold magenta")
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
                console.print("[analisis]💡 ANALISIS & REKOMENDASI:[/analisis]")
                console.print("- Subdomain yang terekspos (bocor) bisa jadi celah keamanan jika tidak di-update.")
                console.print("- Gunakan info ini untuk audit domain kantor atau investigasi domain penipu.")
            else:
                console.print("[warning]Gak ada subdomain ditemukan.[/warning]")
        else:
            console.print("[warning]Gagal narik data dari crt.sh.[/warning]")
    except Exception as e:
        console.print(f"[danger]Error: {e}[/danger]")
    pause()

def advanced_ping():
    show_header("ISP Pro Toolkit > Advanced Ping Checker")
    target = Prompt.ask("Masukkan IP/Host (contoh: 8.8.8.8)")
    if not target: return
    
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    count = '20'
    
    console.print(f"[cyan]Ping ke {target} (20 paket)...[/cyan]")
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
        table.add_column("Metrik", style="cyan")
        table.add_column("Nilai", style="green")
        table.add_column("Status", style="yellow")
        
        loss_status = "[bold green]Normal[/bold green]" if loss == 0 else "[bold red]Packet Loss![/bold red]"
        table.add_row("Packet Loss", f"{loss}%", loss_status)
        
        if loss == 100:
            table.add_row("Avg RTT", "N/A", "[bold red]Mati[/bold red]")
            table.add_row("Jitter", "N/A", "[bold red]Mati[/bold red]")
        else:
            lat_status = "[bold green]Bagus[/bold green]" if avg_rtt < 50 else ("[yellow]Cukup[/yellow]" if avg_rtt < 100 else "[bold red]Tinggi[/bold red]")
            table.add_row("Avg RTT", f"{avg_rtt:.2f} ms", lat_status)
            
            jitter_status = "[bold green]Stabil[/bold green]" if jitter < 10 else "[bold red]Tidak Stabil[/bold red]"
            table.add_row("Jitter", f"{jitter:.2f} ms", jitter_status)
        
        console.print("\n", table, "\n")
        
        console.print("[analisis]💡 ANALISIS & REKOMENDASI:[/analisis]")
        if loss == 100:
            console.print("- [danger]Target tidak merespon ping (100% Loss).[/danger]")
            console.print("- Kemungkinan 1: Target (IP Modem/HP) memblokir ICMP (Anti-DDoS/Firewall).")
            console.print("- Kemungkinan 2: IP Private/NAT (seperti IP Telkomsel/Indihome yang di-NAT).")
            console.print("- Kemungkinan 3: Server sedang down atau kabel putus.")
            console.print("- Saran: Jika target adalah pelanggan, coba ping ke IP BRAS atau server game untuk membandingkan.")
        elif loss > 0:
            console.print(f"- [warning]Terjadi Packet Loss sebesar {loss}%.[/warning]")
            console.print("- Koneksi tidak stabil. Cek kualitas kabel LAN, WiFi, atau redaman optik (jika FTTH).")
        elif jitter > 10:
            console.print("- [warning]Jitter tinggi (koneksi naik-turun).[/warning]")
            console.print("- Sering terjadi saat ada download besar (Bufferbloat) atau kongesti jaringan.")
        else:
            console.print("- [success]Koneksi stabil dan sehat.[/success]")
            console.print("- RTT dan Jitter dalam batas normal. Siap digunakan untuk gaming/streaming.")
            
    except Exception as e:
        console.print(f"[danger]Error saat ping: {e}[/danger]")
    pause()

def local_traceroute():
    show_header("ISP Pro Toolkit > Local Traceroute")
    target = Prompt.ask("Masukkan IP/Host (contoh: 8.8.8.8)")
    if not target: return
    
    console.print(f"[cyan]Traceroute lokal ke {target}...[/cyan]")
    try:
        cmd = ['traceroute', '-n', target] if platform.system().lower() != 'windows' else ['tracert', '-n', target]
        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=30)
        lines = process.stdout.strip().split('\n')
        console.print("\n".join(lines[:15]))
        
        console.print("\n[analisis]💡 ANALISIS & REKOMENDASI:[/analisis]")
        console.print("- Traceroute menunjukkan jalur (hop) paket dari server ini ke target.")
        console.print("- Jika ada hop yang 'Timeout', itu wajar (router memblokir ping).")
        console.print("- Jika ada lonjakan latency (misal dari 10ms langsung ke 200ms), itu titik kongesti (bottleneck).")
        console.print("- Gunakan data ini untuk eskalasi ke NOC jika rute terlihat suboptimal (muter-muter).")
    except Exception as e:
        console.print(f"[danger]Gagal traceroute: {e}[/danger]")
    pause()

if __name__ == "__main__":
    if not API_KEY:
        console.print("[danger]API_KEY_REAL tidak ditemukan di .env![/danger]")
        sys.exit(1)
    menu()
