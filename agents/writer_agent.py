from utils.ollama_client import ask_qwen

def execute_contest(item):
    system_prompt = "Kamu adalah Penulis Profesional & Desainer Kreatif. Output HARUS JSON."
    user_prompt = f"""BUATKAN DRAF KARYA UNTUK LOMBA INI:
Judul: {item['title']} | Platform: {item['platform']} | Kategori: {item['category']}

Buat draf awal yang kreatif & profesional. Jika lomba desain, beri deskripsi konsep visual detail. Jika menulis, buat outline + paragraf pembuka kuat.
Output JSON dengan key: 'concept', 'draft_content', 'suggestions'."""
    
    return ask_qwen(system_prompt, user_prompt)
  
