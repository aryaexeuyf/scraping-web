from playwright.sync_api import sync_playwright
import time
import traceback
import base64
import json
import os
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone

# --- AMBIL URL DARI GITHUB ACTIONS (Dikirim via Cloudflare Worker) ---
LINK_TIKTOK = os.environ.get("TIKTOK_LINK", "https://www.tiktok.com/@username_kamu")

# --- INIT FIREBASE ---
firebase_key_json = os.environ.get("FIREBASE_KEY")
if firebase_key_json:
    cred_dict = json.loads(firebase_key_json)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
else:
    print("[!] FIREBASE_KEY tidak ditemukan.")
    db = None

def main():
    print(f"[*] Membuka Zefame untuk: {LINK_TIKTOK}")
    status_akhir = "Gagal"
    pesan_error = ""
    ss_base64 = ""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            page.goto("https://zefame.com/id/free-tiktok-followers", timeout=60000, wait_until="domcontentloaded")
            time.sleep(3)

            # Cek Limit IP / Error
            if page.locator("text=Harap tunggu").count() > 0:
                pesan_error = "IP Server kena limit (Harap tunggu)."
                raise Exception(pesan_error)
            if page.locator("text=Terjadi kesalahan").count() > 0:
                pesan_error = "Situs Zefame sedang error/maintenance."
                raise Exception(pesan_error)

            # Isi Form
            input_selector = 'input[placeholder*="TikTok"]'
            print("[*] Mengisi link TikTok...")
            page.fill(input_selector, LINK_TIKTOK)
            time.sleep(1)
            
            # Klik Tombol
            print("[*] Mengklik tombol 'Dapatkan'...")
            page.click('button:has-text("Dapatkan")')
            
            # Tunggu Timer 60 Detik
            print("[*] Menunggu proses (60 detik)...")
            for i in range(12): 
                time.sleep(5)
                print(f"    -> Detik ke-{(i+1)*5}")
            
            status_akhir = "Berhasil"
            pesan_error = "Proses pengiriman followers sukses!"

        except Exception as e:
            print(f"[!] ERROR: {e}")
            if not pesan_error: pesan_error = str(e)
        finally:
            print("[*] Mengambil screenshot (termasuk jika gagal)...")
            try:
                ss_bytes = page.screenshot(full_page=True)
                ss_base64 = base64.b64encode(ss_bytes).decode('utf-8')
            except Exception as ss_error:
                print(f"[!] Gagal screenshot: {ss_error}")
            
            # Kirim ke Firebase
            if db:
                print("[*] Mengirim hasil & screenshot ke Firebase...")
                db.collection("scrape_results").add({
                    "tiktok_id": LINK_TIKTOK,
                    "status": status_akhir,
                    "pesan": pesan_error,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "image_base64": ss_base64
                })
            
            browser.close()

if __name__ == "__main__":
    main()
