from playwright.sync_api import sync_playwright
import time

URL_ZEFAME = "https://zefame.com/id/free-tiktok-followers"
LINK_TIKTOK = "https://www.tiktok.com/@rc_project_dj" # GANTI DENGAN LINK KAMU

def main():
    print(f"[*] Membuka: {URL_ZEFAME}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto(URL_ZEFAME, timeout=60000, wait_until="domcontentloaded")
            print("[*] Halaman dibuka.")
            time.sleep(3) 

            # 1. Cek error secara spesifik (abaikan teks di footer)
            # Kita cuma cek apakah ada teks error di area form utama
            if page.locator("text=Terjadi kesalahan. Coba lagi.").count() > 0:
                print("[!] Terjadi kesalahan pada form Zefame.")
                return

            # 2. Isi kolom
            input_selector = 'input[placeholder*="TikTok"]'
            if page.locator(input_selector).count() == 0:
                input_selector = 'input[type="text"]' 
            
            print(f"[*] Mengisi link: {LINK_TIKTOK}")
            page.fill(input_selector, LINK_TIKTOK)
            time.sleep(1)
            
            # 3. Klik tombol
            button_selector = 'button:has-text("Dapatkan")'
            print("[*] Mengklik tombol 'Dapatkan'...")
            page.click(button_selector)
            
            # 4. TUNGGU TIMER 60 DETIK
            print("[*] Menunggu proses (60 detik). Jangan tutup browser...")
            
            # Loop tiap 5 detik buat ngecek progress (opsional biar keliatan di log)
            for i in range(12): # 12 x 5 detik = 60 detik
                time.sleep(5)
                print(f"    -> Menunggu... ({(i+1)*5} detik)")
            
            print("[*] Waktu tunggu selesai. Mengambil screenshot hasil akhir...")
            
            # 5. Screenshot hasil akhir
            page.screenshot(path="zefame_result.png", full_page=True)
            print("[*] Selesai! Cek Artifact buat lihat hasil akhirnya.")

        except Exception as e:
            print(f"[!] ERROR: {e}")
            try:
                page.screenshot(path="zefame_error.png")
            except: pass
        finally:
            browser.close()

if __name__ == "__main__":
    main()
