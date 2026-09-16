import os
from supabase import create_client, Client
from datetime import datetime
from agents.writer_agent import execute_contest
from agents.security_agent import execute_bug_bounty

# Konfigurasi
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

def process_tasks():
    print(f"[{datetime.now()}] 🚀 Unified Agent System Started...")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Ambil semua tugas yang belum dikerjakan
    response = supabase.table("bounties").select("*").eq("agent_status", "scouted").execute()
    tasks = response.data
    
    if not tasks:
        print("✅ No pending tasks.")
        return
        
    print(f"🔨 Found {len(tasks)} tasks to process...")
    
    for task in tasks:
        print(f"\n🤖 Processing [{task['deal_type'].upper()}]: {task['title']}")
        result = None
        
        # ROUTING OTOMATIS BERDASARKAN TIPE TUGAS
        if task['deal_type'] == 'contest':
            result = execute_contest(task)
        elif task['deal_type'] == 'bug_bounty':
            result = execute_bug_bounty(task)
        # Nanti tinggal tambah elif untuk kategori lain!
        # elif task['deal_type'] == 'flash_sale': ...
        
        if result and "error" not in result:
            supabase.table("bounties").update({
                "agent_status": "completed",
                "worker_output": result,
                "submitted_at": datetime.now().isoformat()
            }).eq("id", task["id"]).execute()
            print(f"✅ Completed & Saved!")
        else:
            print(f"❌ Failed: {result}")

if __name__ == "__main__":
    process_tasks()
  
