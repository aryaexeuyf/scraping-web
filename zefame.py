from playwright.sync_api import sync_playwright
import time
import traceback

URL_ZEFAME = "https://zefame.com/id/free-tiktok-followers"
# GANTI DENGAN LINK TIKTOK KAMU (contoh: https://www.tiktok.com/@username)
LINK_TIKTOK = "https://www.tiktok.com/@rc_project_dj" 

def main():
    print(f"[*] Membuka: {URL_ZEFAME}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        # Pura-pura jadi Chrome asli
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            page.goto(URL_ZEFAME, timeout=60000, wait_until="domcontentloaded")
            print("[*] Halaman dibuka.")
            time.sleep(3) 

            # Cek error spesifik dari form
            if page.locator("text=Terjadi kesalahan. Coba lagi.").count() > 0:
                print("[!] Peringatan: Situs Zefame menampilkan pesan error di form.")
                raise Exception("Zefame Error Message Detected")

            # Cari kolom input
            input_selector = 'input[placeholder*="TikTok"]'
            if page.locator(input_selector).count() == 0:
                input_selector = 'input[type="text"]' 
            
            print(f"[*] Mengisi link: {LINK_TIKTOK}")
            page.fill(input_selector, LINK_TIKTOK)
            time.sleep(1)
            
            # Klik tombol
            button_selector = 'button:has-text("Dapatkan")'
            print("[*] Mengklik tombol 'Dapatkan'...")
            page.click(button_selector)
            
            # NUNGGU TIMER 60 DETIK
            print("[*] Menunggu proses (60 detik). Jangan tutup browser...")
            
            for i in range(12): 
                time.sleep(5)
                print(f"    -> Menunggu... ({(i+1)*5} detik)")
            
            print("[*] Waktu tunggu selesai. Mengambil screenshot hasil akhir...")
            
        except Exception as e:
            print(f"\n[!] ERROR TERJADI: {e}")
            traceback.print_exc()
        finally:
            # PASTIKAN SCREENSHOT DIAMBIL APAPUN YANG TERJADI
            try:
                print("[*] Mencoba mengambil screenshot...")
                page.screenshot(path="zefame_result.png", full_page=True)
                print("[*] Screenshot berhasil disimpan.")
            except Exception as ss_error:
                print(f"[!] Gagal mengambil screenshot: {ss_error}")
            
            browser.close()

if __name__ == "__main__":
    main()
