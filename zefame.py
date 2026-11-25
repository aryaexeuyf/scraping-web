from playwright.sync_api import sync_playwright
import time

URL_ZEFAME = "https://zefame.com/id/free-tiktok-followers"
# GANTI dengan link TikTok kamu, atau biarin dummy dulu buat tes
LINK_TIKTOK = "https://www.tiktok.com/@username_kamu" 

def main():
    print(f"[*] Membuka: {URL_ZEFAME}")
    
    with sync_playwright() as p:
        # Wajib headless=True di GitHub Actions
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # 1. Buka halaman
            page.goto(URL_ZEFAME, timeout=60000, wait_until="domcontentloaded")
            print("[*] Halaman dibuka.")
            time.sleep(3) # Kasih waktu JS jalan

            # 2. Cek Cloudflare (indikasi awal)
            content = page.content()
            if "Verifying" in content or "Checking your browser" in content:
                print("[!] TERDETEKSI CLOUDFLARE CHALLENGE. Script kemungkinan gagal.")
                # Kita tetap lanjut coba, siapa tahu bisa lewat
            elif "Pemeliharaan" in content or "Terjadi kesalahan" in content:
                print("[!] Situs mungkin sedang error/pemeliharaan.")

            # 3. Cari kolom input (pakai placeholder yang kamu kasih)
            print("[*] Mencari kolom input...")
            input_selector = 'input[placeholder*="TikTok"]'
            # Fallback kalau placeholder beda
            if page.locator(input_selector).count() == 0:
                input_selector = 'input[type="text"]' 
            
            if page.locator(input_selector).count() > 0:
                print(f"[*] Ketemu kolom input: {input_selector}")
                page.fill(input_selector, LINK_TIKTOK)
                time.sleep(1)
            else:
                print("[!] Kolom input tidak ketemu. Mungkin di dalam iframe atau selector beda.")
                # Coba cari di dalam iframe
                for frame in page.frames:
                    if frame.locator('input[type="text"]').count() > 0:
                        print(f"[*] Ketemu input di iframe: {frame.url}")
                        frame.fill('input[type="text"]', LINK_TIKTOK)
                        input_selector = 'iframe' # penanda
                        break
            
            # 4. Cari dan klik tombol "Dapatkan"
            print("[*] Mencari tombol 'Dapatkan'...")
            button_selector = 'button:has-text("Dapatkan")'
            if page.locator(button_selector).count() == 0:
                button_selector = 'button[type="submit"]'
            
            if page.locator(button_selector).count() > 0:
                print(f"[*] Klik tombol: {button_selector}")
                page.click(button_selector)
                time.sleep(5) # Tunggu reaksi
                print("[*] Selesai klik. Cek screenshot.")
            else:
                print("[!] Tombol 'Dapatkan' tidak ketemu.")
            
            # 5. Screenshot buat bukti
            page.screenshot(path="zefame_result.png", full_page=True)
            print("[*] Screenshot disimpan: zefame_result.png")

        except Exception as e:
            print(f"[!] ERROR: {e}")
            # Coba screenshot kalau error
            try:
                page.screenshot(path="zefame_error.png")
            except: pass
        finally:
            browser.close()

if __name__ == "__main__":
    main()
