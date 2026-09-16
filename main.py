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
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Missing Supabase credentials!")
        return
        
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Ambil semua tugas yang belum dikerjakan
    response = supabase.table("bounties").select("*").eq("agent_status", "scouted").execute()
    tasks = response.data
    
    if not tasks:
        print("✅ No pending tasks.")
        return
        
    print(f" Found {len(tasks)} tasks to process...")
    
    for task in tasks:
        # SAFEGUARD: Cek apakah deal_type ada dan valid
        deal_type = task.get('deal_type')
        title = task.get('title', 'Unknown Task')
        
        if not deal_type:
            print(f"⚠️ Skipping task '{title}': Missing deal_type")
            continue
            
        print(f"\n🤖 Processing [{deal_type.upper()}]: {title}")
        result = None
        
        # ROUTING OTOMATIS
        if deal_type == 'contest':
            result = execute_contest(task)
        elif deal_type == 'bug_bounty':
            result = execute_bug_bounty(task)
        else:
            print(f"️ Unknown deal_type: {deal_type}. Skipping.")
            continue
        
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
