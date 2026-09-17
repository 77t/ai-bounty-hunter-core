import os
import json
from utils import setup_logger

logger = setup_logger("DesignerAgentV2")

# Konfigurasi Model AI Kreatif (Gunakan API Key gratis tier atau local model)
CREATIVE_MODEL_API_URL = os.getenv("CREATIVE_MODEL_API_URL", "https://api.openrouter.ai/v1/chat/completions")
CREATIVE_API_KEY = os.getenv("CREATIVE_API_KEY")

def generate_logo_with_philosophy(concept_name: str, keywords: list) -> dict:
    """
    Generate logo concept DAN filosofi lengkap dalam satu panggilan.
    Mengembalikan dictionary berisi URL gambar (simulasi) dan teks filosofi.
    """
    if not CREATIVE_API_KEY:
        logger.warning("️ Creative API Key tidak ditemukan. Menggunakan mock data.")
        return _get_mock_creative_output(concept_name)

    prompt = f"""
    Bertindaklah sebagai Desainer Grafis Senior & Filsuf Brand.
    Konsep Logo: "{concept_name}"
    Keywords: {', '.join(keywords)}
    
    Tugas:
    1. Deskripsikan visual logo secara detail (bentuk, warna, tipografi).
    2. Jelaskan FILOSOFI MENDALAM dari setiap elemen (makna warna, simbol, psikologi bentuk).
    3. Tentukan target audiens yang paling cocok.
    
    Format Output HARUS JSON valid:
    {{
      "visual_description": "...",
      "color_philosophy": "...",
      "symbol_meaning": "...",
      "target_audience": "...",
      "image_prompt_for_generation": "..." 
    }}
    """

    try:
        # Simulasi panggilan API ke model kreatif (Qwen/Llama/OpenRouter)
        # Nanti ganti dengan requests.post() ke endpoint AI Bos
        response_data = {
            "visual_description": f"Logo minimalis '{concept_name}' dengan garis geometris tegas.",
            "color_philosophy": "Emerald Green melambangkan pertumbuhan aset & stabilitas. Aksen Cyan merepresentasikan inovasi teknologi masa depan.",
            "symbol_meaning": "Bentuk perisai terfragmentasi menyiratkan proteksi multi-layer terhadap ancaman siber modern.",
            "target_audience": "Startup cybersecurity, platform DeFi, dan komunitas tech-savvy Gen-Z.",
            "image_prompt_for_generation": f"Minimalist vector logo for {concept_name}, emerald green and cyan neon accents, geometric shield shape, dark background, professional branding --v 6"
        }
        
        logger.info(f"✅ Filosofi logo '{concept_name}' berhasil digenerate!")
        return response_data
        
    except Exception as e:
        logger.error(f"❌ Gagal generate filosofi: {str(e)}")
        return _get_mock_creative_output(concept_name)


def _get_mock_creative_output(concept_name: str) -> dict:
    """Fallback jika API key belum disetup."""
    return {
        "visual_description": f"[MOCK] Desain logo {concept_name} dengan gaya modern flat design.",
        "color_philosophy": "[MOCK] Kombinasi warna dipilih berdasarkan psikologi brand trust & innovation.",
        "symbol_meaning": "[MOCK] Simbol utama merepresentasikan inti nilai dari konsep tersebut.",
        "target_audience": "[MOCK] Profesional muda & early adopters teknologi.",
        "image_prompt_for_generation": f"Mock logo prompt for {concept_name}"
  }
  
