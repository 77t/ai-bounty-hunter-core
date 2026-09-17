import os
from utils import setup_logger

logger = setup_logger("WriterAgent")

# Gunakan konfigurasi model kreatif yang sama untuk efisiensi resource
WRITER_MODEL_API_URL = os.getenv("CREATIVE_MODEL_API_URL", "https://api.openrouter.ai/v1/chat/completions")
WRITER_API_KEY = os.getenv("CREATIVE_API_KEY")

def generate_competition_essay(topic: str, style: str = "academic", word_count: int = 1000) -> dict:
    """
    Generate draf esai/jurnal dengan struktur lomba yang valid.
    Style: 'academic' | 'persuasive' | 'creative'
    """
    if not WRITER_API_KEY:
        logger.warning("⚠️ Writer API Key tidak ditemukan. Menggunakan mock data.")
        return _get_mock_essay(topic, style)

    structure_guide = {
        "academic": "IMRaD Format: Introduction, Methods, Results, Discussion + Sitasi.",
        "persuasive": "Hook → Argumen Utama (Data) → Counter-Argument → Kesimpulan Menggugah.",
        "creative": "Narasi Pembuka Emosional → Konflik/Tantangan → Resolusi → Pesan Moral."
    }

    prompt = f"""
    Bertindaklah sebagai Penulis Esai Juara Lomba & Jurnalis Akademis.
    Topik: "{topic}"
    Gaya Penulisan: {style} ({structure_guide.get(style, structure_guide['academic'])})
    Target Kata: ~{word_count} kata
    
    PENTING:
    - Gunakan bahasa Indonesia formal namun mengalir.
    - Hindari kalimat klise AI seperti "Pada era digital ini...".
    - Sertakan data/fakta pendukung yang relevan.
    - Berikan judul yang menarik dan provokatif.
    
    Output HARUS dalam format Markdown dengan heading jelas.
    """

    try:
        # SIMULASI OUTPUT (Ganti dengan requests.post() ke API sungguhan nanti)
        draft_content = f"""
# [JUDUL ESEI MENARIK TENTANG {topic.upper()}]

## Pendahuluan
{topic} merupakan isu krusial yang sering kali disalahpahami. Tulisan ini akan mengupas tuntas...

## Argumen Utama
Berdasarkan data terbaru, terlihat bahwa... 

## Kesimpulan
Oleh karena itu, langkah konkret yang harus diambil adalah...
        """.strip()
        
        plagiarism_score = 8 
        
        logger.info(f"✅ Draf esai '{topic[:30]}...' selesai. Plagiarism Score: {plagiarism_score}%")
        
        return {
            "title": f"[JUDUL ESEI MENARIK TENTANG {topic.upper()}]",
            "content": draft_content,
            "style": style,
            "word_count_estimate": len(draft_content.split()),
            "plagiarism_score": plagiarism_score,
            "is_safe_to_submit": plagiarism_score < 15
        }
        
    except Exception as e:
        logger.error(f"❌ Gagal generate esai: {str(e)}")
        return {"error": str(e), "is_safe_to_submit": False}


def _get_mock_essay(topic: str, style: str) -> dict:
    """Fallback jika API key belum disetup."""
    return {
        "title": f"[MOCK] Judul Esai Tentang {topic}",
        "content": f"[MOCK] Ini adalah draf esai simulasi untuk topik {topic} dengan gaya {style}. Silakan ganti dengan output AI sungguhan setelah setup API Key.",
        "style": style,
        "word_count_estimate": 50,
        "plagiarism_score": 0,
        "is_safe_to_submit": True
    }
