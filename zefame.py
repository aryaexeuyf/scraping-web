from playwright.sync_api import sync_playwright
import time
import traceback
import base64
import json
import os
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone

# --- INIT FIREBASE ---
firebase_key_json = os.environ.get("FIREBASE_KEY")
if not firebase_key_json:
    print("[!] FIREBASE_KEY tidak ada.")
    exit(1)

cred_dict = json.loads(firebase_key_json)
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)
db = firestore.client()

def proses_antrean():
    print("[*] Mengecek antrean request di Firebase...")
    # Cari 1 request yang statusnya 'pending'
    docs = db.collection("scrape_requests").where("status", "==", "pending").limit(1).stream()
    
    request_data = None
    doc_id = None
    for doc in docs:
        request_data = doc.to_dict()
        doc_id = doc.id
        break

    if not request_data:
        print("[*] Tidak ada antrean. Selesai.")
        return

    LINK_TIKTOK = request_data["tiktok_id"]
    print(f"[*] Memproses: {LINK_TIKTOK}")
    
    # Tandai sedang diproses
    db.collection("scrape_requests").document(doc_id).update({"status": "processing"})

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

            if page.locator("text=Harap tunggu").count() > 0:
                pesan_error = "IP Server kena limit (Harap tunggu)."
                raise Exception(pesan_error)
            if page.locator("text=Terjadi kesalahan").count() > 0:
                pesan_error = "Situs Zefame sedang error/maintenance."
                raise Exception(pesan_error)

            input_selector = 'input[placeholder*="TikTok"]'
            page.fill(input_selector, LINK_TIKTOK)
            time.sleep(1)
            
            page.click('button:has-text("Dapatkan")')
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
            print("[*] Mengambil screenshot...")
            try:
                ss_bytes = page.screenshot(full_page=True)
                ss_base64 = base64.b64encode(ss_bytes).decode('utf-8')
            except Exception as ss_error:
                print(f"[!] Gagal screenshot: {ss_error}")
            
            # Kirim hasil ke scrape_results
            db.collection("scrape_results").add({
                "tiktok_id": LINK_TIKTOK,
                "status": status_akhir,
                "pesan": pesan_error,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "image_base64": ss_base64
            })
            
            # Update status request jadi done
            db.collection("scrape_requests").document(doc_id).update({"status": "done"})
            browser.close()

if __name__ == "__main__":
    proses_antrean()
