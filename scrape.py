import requests
from bs4 import BeautifulSoup
from datetime import datetime

# --- 1. Ambil Halaman dari BMKG ---
url = "https://www.bmkg.go.id/cuaca/prakiraan-cuaca/35.16"
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
print(f"[*] Mengambil data dari: {url}")
response = requests.get(url, headers=headers, timeout=30)

if response.status_code != 200:
    print(f"[!] Gagal mengambil halaman. Status: {response.status_code}")
    exit()

# --- 2. Parse HTML ---
soup = BeautifulSoup(response.text, "html.parser")

judul = soup.select_one("h1")
if judul:
    print(f"[*] Judul halaman: {judul.get_text(strip=True)}")

print(f"[*] Waktu scraping: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

# --- 3. Scraping Data Cuaca (Cara Sederhana & Tahan Banting) ---
# Karena struktur BMKG kompleks, kita ambil semua teks yang relevan dulu.
# Ini adalah langkah "tester" untuk memastikan data bisa diambil.
semua_teks = soup.get_text(separator='\n', strip=True)

print("[*] Mencari baris teks yang mengandung info cuaca...")
print("-" * 60)

# Loop setiap baris teks, cari yang ada suhu/status cuacanya
for baris in semua_teks.split('\n'):
    baris = baris.strip()
    if not baris:
        continue
    # Filter: baris yang mengandung "°C", "Hujan", "Berawan", "Kabut", dll.
    if any(kata in baris for kata in ["°C", "Hujan", "Berawan", "Kabut", "Cerah", "Udara Kabur"]):
        print(baris)

print("-" * 60)
print("[*] Scraping selesai.")
