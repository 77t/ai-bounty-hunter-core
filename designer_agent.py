import os
import io
from huggingface_hub import InferenceClient
from supabase import create_client
from utils import setup_logger, validate_secrets

# Setup Logger
logger = setup_logger("DesignerAgent")

# Validasi Secrets di Awal (Fail Fast)
try:
    validate_secrets()
except EnvironmentError as e:
    logger.error(str(e))
    raise

# Konfigurasi dari Environment Variables
HF_TOKEN = os.environ.get("HF_TOKEN")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
BUCKET_NAME = "bounty-assets"

# Inisialisasi Client
hf_client = InferenceClient(token=HF_TOKEN)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def generate_logo(task: dict):
    """
    Spesialis Gambar: Generate logo via Hugging Face & Upload ke Supabase Storage
    Args:
        task: Dict berisi 'id' dan 'title'
    Returns:
        Dict dengan status dan image_uri
    """
    title = task.get('title', 'Logo Design')
    task_id = task.get('id', 'unknown')
    
    # Prompt engineering khusus untuk hasil profesional
    prompt = f"Professional vector logo design for '{title}'. Minimalist, modern, flat design, white background, high quality, 4k resolution, clean lines, no text."
    
    logger.info(f"Memulai generate logo untuk task #{task_id}: '{title}'")
    
    try:
        # 1. Generate Gambar menggunakan FLUX.1-dev (Kualitas terbaik saat ini)
        logger.info("Mengirim request ke Hugging Face FLUX model...")
        image = hf_client.text_to_image(
            prompt=prompt,
            model="black-forest-labs/FLUX.1-dev"
        )
        logger.info("Gambar berhasil digenerate!")
        
        # 2. Convert PIL Image ke Bytes untuk upload
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        # 3. Upload ke Supabase Storage
        # FIX: Parameter 'file' hanya ditulis SEKALI
        file_name = f"logo_task_{task_id}.png"
        logger.info(f"Mengupload gambar ke bucket '{BUCKET_NAME}' sebagai '{file_name}'...")
        
        supabase.storage.from_(BUCKET_NAME).upload(
            file=img_byte_arr,                # <--- PERBAIKAN DI SINI (Hanya 1x 'file')
            path=file_name,                   # Path di dalam bucket
            file_options={"content-type": "image/png"}
        )
        logger.info("Upload ke Supabase berhasil!")
        
        # 4. Dapatkan Public URL
        public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(file_name)
        logger.info(f"Logo siap! URL: {public_url}")
        
        return {"status": "success", "image_uri": public_url}

    except Exception as e:
        logger.error(f"Gagal generate/upload logo: {str(e)}")
        return {"status": "error", "message": str(e)}
        
