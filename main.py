import os
import json
from designer_agent import generate_logo
from security_agent import check_logo_safety

def run_bounty_task(task_id: str, title: str):
    """
    CEO Dashboard: Orkestrasi penuh pembuatan & validasi logo
    """
    print(f"[CEO] Memulai tugas bounty #{task_id}: '{title}'")
    
    # Tahap 1: Generate Logo
    print("[CEO] >> Mengirim perintah ke Designer Agent...")
    design_result = generate_logo({"id": task_id, "title": title})
    
    if design_result["status"] != "success":
        print(f"[CEO] Gagal generate logo: {design_result['message']}")
        return {"task_id": task_id, "final_status": "failed_design", "detail": design_result}
    
    image_url = design_result["image_uri"]
    print(f"[CEO] >> Logo berhasil dibuat! URL: {image_url}")
    
    # Tahap 2: Security Check
    print("[CEO] >> Mengirim perintah ke Security Agent...")
    safety_result = check_logo_safety(image_url)
    
    if safety_result["status"] != "approved":
        print(f"[CEO] Logo DITOLAK oleh Security Agent: {safety_result['message']}")
        # Opsional: Hapus file dari storage jika ditolak
        return {
            "task_id": task_id, 
            "final_status": "rejected_security", 
            "image_url": image_url,
            "detail": safety_result
        }
    
    # Tahap 3: Final Approval
    print("[CEO] >> Logo DISETUJUI! Siap dikirim ke klien.")
    return {
        "task_id": task_id,
        "final_status": "completed",
        "image_url": image_url,
        "audit_log": safety_result
    }

# Entry point untuk testing lokal atau trigger workflow
if __name__ == "__main__":
    # Contoh trigger manual
    result = run_bounty_task("test-001", "Minimalist Coffee Shop Logo")
    print("\n=== HASIL FINAL ===")
    print(json.dumps(result, indent=2))
        
