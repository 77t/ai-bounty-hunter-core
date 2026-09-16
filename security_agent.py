import os
from utils import setup_logger

# Setup Logger
logger = setup_logger("SecurityAgent")

def check_image_safety(image_uri: str) -> dict:
    """
    Memeriksa keamanan gambar berdasarkan URI/URL.
    
    Di versi production, fungsi ini akan:
    1. Download gambar dari URI
    2. Menggunakan Vision API (seperti Google Cloud Vision / AWS Rekognition) 
       untuk mendeteksi NSFW, kekerasan, atau teks sensitif.
    3. Mengembalikan status keamanan.
    
    Untuk saat ini, kita gunakan validasi dasar sebagai placeholder.
    """
    logger.info(f"️ Memulai pemeriksaan keamanan untuk: {image_uri}")
    
    # Validasi Dasar: Cek apakah URI valid dan bukan kosong
    if not image_uri or not isinstance(image_uri, str):
        logger.error("❌ Image URI tidak valid atau kosong.")
        return {"is_safe": False, "reason": "Invalid or empty image URI"}

    # Cek Ekstensi File (Hanya izinkan format gambar standar)
    allowed_extensions = ['.png', '.jpg', '.jpeg', '.webp']
    is_valid_ext = any(image_uri.lower().endswith(ext) for ext in allowed_extensions)
    
    if not is_valid_ext:
        logger.warning(f"⚠️ Format file tidak didukung: {image_uri}")
        return {"is_safe": False, "reason": f"Unsupported file format. Allowed: {allowed_extensions}"}

    # Placeholder untuk Deteksi Konten AI (NSFW/Violence)
    # TODO: Integrasikan dengan Google Cloud Vision API atau AWS Rekognition di sini
    # Contoh logika masa depan:
    # response = vision_client.safe_search_detection(image=image)
    # if response.safe_search_annotation.adult == Likelihood.LIKELY: return unsafe
    
    # Saat ini kita anggap AMAN jika URI valid dan ekstensi benar
    # Ini memungkinkan pipeline tetap berjalan saat testing
    logger.info("✅ Gambar lolos validasi dasar (Placeholder Safety Check).")
    
    return {
        "is_safe": True,
        "confidence": 0.95,
        "checks_passed": ["valid_uri", "safe_extension"],
        "note": "Production safety scan pending integration"
    }

# Helper function untuk dipanggil di main.py
def batch_check_safety(image_uris: list) -> list:
    """
    Memeriksa keamanan beberapa gambar sekaligus.
    Mengembalikan list hasil pemeriksaan.
    """
    results = []
    for uri in image_uris:
        result = check_image_safety(uri)
        results.append({"uri": uri, **result})
        
    safe_count = sum(1 for r in results if r["is_safe"])
    logger.info(f"🛡️ Batch check selesai: {safe_count}/{len(results)} gambar aman.")
    
    return results
    
