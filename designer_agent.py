import os
import io
from huggingface_hub import InferenceClient
from supabase import create_client

# Konfigurasi dari Environment Variables (GitHub Secrets)
HF_TOKEN = os.environ.get("HF_TOKEN")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") # Pakai Service Role Key!
BUCKET_NAME = "bounty-assets"

# Inisialisasi Client
hf_client = InferenceClient(token=HF_TOKEN)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def generate_logo(task):
    """
    Spesialis Gambar: Generate logo via Hugging Face & Upload ke Supabase Storage
    """
    title = task.get('title', 'Logo Design')
    # Prompt engineering khusus untuk hasil profesional
    prompt = f"Professional vector logo design for '{title}'. Minimalist, modern, flat design, white background, high quality, 4k resolution."
    
    try:
        # 1. Generate Gambar menggunakan FLUX.1-dev (Kualitas terbaik saat ini)
        image = hf_client.text_to_image(
            prompt, 
            model="black-forest-labs/FLUX.1-dev"
        )
        
        # 2. Convert PIL Image ke Bytes untuk upload
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        # 3. Upload ke Supabase Storage
        file_name = f"logo_task_{task['id']}.png"
        supabase.storage.from_(BUCKET_NAME).upload(
            file=file_name, 
            file=img_byte_arr, 
            file_options={"content-type": "image/png"}
        )
        
        # 4. Dapatkan Public URL
        public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(file_name)
        
        return {"status": "success", "image_url": public_url}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
  
