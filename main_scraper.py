import os
import time
from supabase import create_client, Client

# Ambil secrets dari environment variable (sudah disetting di YAML)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

def main():
    print("=== AI Bounty Hunter Script Started ===")
    
    # Cek apakah secrets tersedia
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("ERROR: Supabase credentials not found in environment variables!")
        return

    try:
        # Inisialisasi Supabase Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Successfully connected to Supabase!")

        # CONTOH LOGIKA SCRAPING SEDERHANA
        # (Ganti bagian ini dengan logika scraping asli kamu jika ada)
        print("Starting bounty hunting process...")
        
        # Simulasi data hasil scrape
        sample_data = {
            "title": "Test Bounty Found",
            "url": "https://example.com/bounty/123",
            "reward": "$500",
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        # Insert ke tabel 'bounties' (sesuaikan nama tabel dengan database kamu)
        # Jika tabel belum ada, script ini akan error. Pastikan tabel sudah dibuat di Supabase.
        response = supabase.table("bounties").insert(sample_data).execute()
        
        print(f"Data inserted successfully: {response.data}")
        print("=== Script Finished Successfully ===")

    except Exception as e:
        print(f"FATAL ERROR during execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()

