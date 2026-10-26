# SEIN (Systematic Exploration - Internet Network)
> **"Support tools untuk analisa & evaluasi kualitas layanan pelanggan | By 96250009"**

SEIN adalah *Network Engineer Toolkit* berbasis CLI (Command Line Interface) yang dirancang khusus untuk mempercepat proses *troubleshooting*, analisa jaringan, dan pengambilan data pelanggan di lingkungan ISP. 

Aplikasi ini terintegrasi dengan sistem internal (Gladius) dan API publik, dibungkus dalam satu antarmuka terminal interaktif yang dapat diakses secara lokal maupun via Web Terminal.

---

## 🚀 Fitur Utama

### 1. IP Track & Locate (MaxMind)
Melacak lokasi IP Address (City-level) menggunakan database MaxMind GeoLite2 yang berjalan secara *offline* dan *private* di server.
- **Kegunaan:** Mengetahui lokasi perkiraan dari IP publik atau IP server game.

### 2. Network Tools (Pro Edition)
Kumpulan *tools* dasar Network Engineer:
- **WHOIS Lookup:** Melacak pemilik domain/IP.
- **DNS Record Checker:** Cek A, MX, TXT, CNAME record.
- **Port Scanner:** Scan 20 port umum untuk audit keamanan.
- **HTTP Header Inspector:** Melihat response header dari sebuah website.

### 3. Multi-Path Analyzer (Diagnosa Game RTO)
Mendiagnosa keluhan pelanggan terkait *ping* atau RTO (Request Time Out) pada game online menggunakan *Cloud Traceroute* (Globalping API) dari 3 titik global (ID, SG, US).
- **Kegunaan:** Membuktikan apakah masalah RTO berasal dari ISP atau dari Server Game (Region Lock / ICMP Block).

### 4. ISP Pro Toolkit
- **BGP / ASN Lookup:** Melacak ASN dan rute BGP dari suatu IP.
- **Subdomain Recon:** Mencari subdomain bocor (OSINT).
- **Advanced Ping Checker:** Mengukur Packet Loss, Jitter, dan RTT (beda dengan ping biasa).
- **Local Traceroute:** Traceroute dari sisi jaringan ISP.

### 5. Cek Embasy (Gladius Auto-Scraper)
Otomatisasi pengambilan data dari sistem Gladius Telkom.
- **Bypass Captcha (Manual Input):** Menampilkan gambar captcha langsung di CLI untuk diinput manual.
- **Auto OTP:** Generate TOTP secara otomatis menggunakan `PyOTP`.
- **Auto Screenshot & Summary:** Mengambil *screenshot* tabel (ter-crop presisi) dan menampilkan ringkasan data pelanggan (Paket, Rx Power, BRAS IP, dsb).

---

## 🛠️ Arsitektur & Teknologi

- **Python 3.12+**: Bahasa utama aplikasi.
- **FastAPI**: Backend API untuk endpoint IP Tracker.
- **Playwright & BeautifulSoup**: Engine otomatisasi browser (Gladius) dan HTML parsing.
- **Rich & Prompt Toolkit**: Antarmuka CLI interaktif & berwarna.
- **ttyd**: Web Terminal untuk mengakses CLI via browser.
- **Cloudflare Tunnel**: Mengamankan akses publik tanpa membuka port router.
- **Systemd**: Menjaga service tetap berjalan 24/7.

---

## 💻 Cara Akses

### Akses via Web Terminal (Mudah)
1. Buka browser (PC/HP).
2. Akses ke: `https://tools.sein.bid`
3. Masukkan kredensial login (Basic Auth).
4. Terminal siap digunakan.

### Akses via CLI (Lokal Server)
Buka terminal WSL/Ubuntu di server, lalu jalankan:
```bash
cd ~/sein
source venv/bin/activate
python sein.py

🔒 Keamanan & Privasi
Data Pelanggan: File gambar (.png) dan log tidak akan pernah di-commit ke repository publik (di-handle oleh .gitignore).
Akses API: Menggunakan Rate-Limiting, Honeypot, dan proteksi Cloudflare Access.
Kredensial Gladius: Disimpan dengan aman di file .env (tidak di-push ke Git).

📌 Catatan Penting (SOP)
Tool ini hanya untuk digunakan oleh personil internal berwenang.
Mohon gunakan akses ini secara bijak untuk mempercepat penyelesaian kendala pelanggan.
Jika menemukan bug atau ingin menambah fitur, silakan hubungi pengembang.

Made with ❤️ by 96250009 - 2026
