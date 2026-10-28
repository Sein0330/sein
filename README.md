# SEIN (Systematic Exploration - Internet Network)
> **"Support tools untuk analisa & evaluasi kualitas layanan pelanggan | By 96250009"**

SEIN adalah *Network Engineer & Cyber Security Toolkit* berbasis CLI (Command Line Interface) yang dirancang untuk mempercepat proses *troubleshooting*, analisa jaringan, otomatisasi web, dan pengambilan data pelanggan. 

Aplikasi ini terintegrasi dengan sistem internal (Gladius) dan API publik, dibungkus dalam satu antarmuka terminal interaktif yang dapat diakses secara lokal maupun via Web Terminal.

---

## 🚀 Fitur Utama (v6.0)

### 1. IP Track & Locate (MaxMind)
Melacak lokasi IP Address (City-level) menggunakan database MaxMind GeoLite2 yang berjalan secara *offline* dan *private* di server.

### 2. Network Tools (Pro Edition)
Kumpulan *tools* dasar Network Engineer:
- **WHOIS Lookup:** Melacak pemilik domain/IP.
- **DNS Record Checker:** Cek A, MX, TXT, CNAME record.
- **Port Scanner:** Scan 20 port umum untuk audit keamanan.
- **HTTP Header Inspector:** Melihat response header dari sebuah website.

### 3. Multi-Path Analyzer (Diagnosa Game RTO)
Mendiagnosa keluhan pelanggan terkait *ping* atau RTO (Request Time Out) pada game online menggunakan *Cloud Traceroute* (Globalping API) dari 3 titik global (ID, SG, US).

### 4. ISP Pro Toolkit
- **BGP / ASN Lookup:** Melacak ASN dan rute BGP dari suatu IP.
- **Subdomain Recon:** Mencari subdomain bocor (OSINT).
- **Advanced Ping Checker:** Mengukur Packet Loss, Jitter, dan RTT.
- **Traceroute (NOC Escalation):** Dual-Trace (Cloud & Pelanggan) untuk bahan eskalasi ke DSO/NOC.

### 5. Cek Embasy (Gladius Auto-Scraper)
Otomatisasi pengambilan data dari sistem Gladius Telkom.
- **Bypass Captcha (Manual Input):** Menampilkan gambar captcha langsung di CLI.
- **Auto OTP:** Generate TOTP secara otomatis menggunakan `PyOTP`.
- **Auto Screenshot & Summary:** Mengambil *screenshot* tabel (ter-crop presisi) dan menampilkan ringkasan data pelanggan.

### 6. Upwork Project Hunter (Secret Menu)
Otomatisasi pencarian *project* di Upwork.
- **Bypass Cloudflare:** Menggunakan *Cookies* dan Mode Stealth.
- **AI Cost Calculator:** Menghitung estimasi modal AI (GPT-4o/Vision) dan profit dari setiap proyek.
- *(Akses: Ketik kode `HOOK` di menu utama).*

### 7. Universal Reverse Engine Web
Membedah API di balik layar website.
- **Universal Form Handler:** Mampu mendeteksi form login, dropdown SSO, OTP, dan Captcha secara dinamis.
- **AI Vision Integration:** Menggunakan AI (OpenRouter) untuk menganalisa screenshot halaman.
- **Auto-Explore:** Otomatis mengklik menu untuk menangkap API (JSON).
- **Screenshot Download:** Link download untuk melihat *capture* layar dengan resolusi penuh.

---

## 🛠️ Arsitektur & Teknologi

- **Python 3.12+**: Bahasa utama aplikasi.
- **FastAPI**: Backend API untuk endpoint IP Tracker & Download File.
- **Playwright & BeautifulSoup**: Engine otomatisasi browser (Gladius/Upwork/RE Web) dan HTML parsing.
- **Rich & Prompt Toolkit**: Antarmuka CLI interaktif & berwarna.
- **ttyd**: Web Terminal untuk mengakses CLI via browser (dilindungi Basic Auth).
- **Cloudflare Tunnel**: Mengamankan akses publik tanpa membuka port router.
- **Systemd**: Menjaga service API & Web Terminal tetap berjalan 24/7.
- **Xvfb (Virtual Display)**: Menjalankan browser *headless* untuk otomatisasi.

---

## 💻 Cara Akses

### Akses via Web Terminal (Mudah)
1. Buka browser (PC/HP).
2. Akses ke: `https://tools.sein.bid`
3. Masukkan kredensial login (Basic Auth: admin / sein2026).
4. Terminal siap digunakan.

### Akses via CLI (Lokal Server)
Buka terminal WSL/Ubuntu di server, lalu jalankan:
```bash
cd ~/sein
source venv/bin/activate
python sein.py

🔒 Keamanan & Privasi
-Data Pelanggan: File gambar (.png) dan log tidak akan pernah di-commit ke repository publik (di-handle oleh .gitignore).
-Akses API: Menggunakan Rate-Limiting, Honeypot, dan proteksi Cloudflare Access.
-Kredensial: Disimpan dengan aman di file .env (tidak di-push ke Git).
-Secret Menu: Menu Upwork Hunter disembunyikan untuk mencegah penyalahgunaan.

📌 Catatan Penting (SOP)
-Tool ini hanya untuk digunakan oleh personil internal berwenang.
-Mohon gunakan akses ini secara bijak untuk mempercepat penyelesaian kendala pelanggan.
-Jika menemukan bug atau ingin menambah fitur, silakan hubungi pengembang.

Made with ❤️ by 96250009 - 2026
