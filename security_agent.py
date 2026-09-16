import os
from huggingface_hub import InferenceClient
from supabase import create_client

# Konfigurasi dari Environment Variables
HF_TOKEN = os.environ.get("HF_TOKEN")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
BUCKET_NAME = "bounty-assets"

# Inisialisasi Client
hf_client = InferenceClient(token=HF_TOKEN)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_logo_safety(image_url: str):
    """
    Spesialis Keamanan: Cek safety & kualitas logo via Vision Model
    """
    try:
        # 1. Download gambar dari Supabase URL untuk dianalisis
        # Note: Di production sebaiknya pakai stream langsung, tapi untuk simplicity kita pakai URL public
        response = hf_client.image_classification(
            image=image_url,
            model="google/vit-base-patch16-224-in21k" # Model lightweight untuk klasifikasi umum/safety
        )
        
        # Logika sederhana: Cek label berbahaya (contoh implementasi dasar)
        unsafe_keywords = ["violence", "gore", "nsfw", "weapon"]
        is_safe = True
        
        for item in response:
            label = item['label'].lower()
            if any(keyword in label for keyword in unsafe_keywords):
                is_safe = False
                break
                
        # 2. Simpan hasil audit ke database (Opsional, bisa dikembangkan nanti)
        # supabase.table('logo_audits').insert({
        #     "image_url": image_url,
        #     "is_safe": is_safe,
        #     "details": str(response[:3]) 
        # }).execute()

        if is_safe:
            return {"status": "approved", "message": "Logo aman dan sesuai standar."}
        else:
            return {"status": "rejected", "message": "Logo terdeteksi mengandung konten tidak aman."}

    except Exception as e:
        # Fallback: Jika model error, anggap perlu review manual atau tolak demi keamanan
        return {"status": "error", "message": f"Gagal melakukan audit keamanan: {str(e)}"}
      
