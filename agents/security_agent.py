from utils.ollama_client import ask_qwen

def execute_bug_bounty(item):
    system_prompt = "Kamu adalah Expert Bug Hunter & Penetration Tester. Output HARUS JSON."
    user_prompt = f"""BUATKAN TEMPLATE LAPORAN BUG BOUNTY PROFESIONAL:
Target: {item['title']} | Program: {item.get('program', 'Unknown')} | Severity: {item.get('severity', 'Medium')}

Buat struktur lengkap: Title, Summary, Steps to Reproduce (template), Impact Analysis, Remediation Suggestion. Gunakan bahasa teknis persuasif.
Output JSON dengan key: 'report_title', 'summary', 'steps_template', 'impact_analysis'."""
    
    return ask_qwen(system_prompt, user_prompt)
  
