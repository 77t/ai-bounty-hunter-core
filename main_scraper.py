import os
from supabase import create_client, Client
from datetime import datetime

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

def scrape_bounties():
    print(f"[{datetime.now()}] Starting AI Bounty Hunter + Giveaway Scanner...")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase credentials missing!")
    
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Connected to Supabase successfully")
    
    try:
        mock_results = [
            {
                "title": "XSS on Login Page",
                "category": "Web App",
                "program": "HackerOne Public",
                "severity": "High",
                "reward": "$500 Cash",
                "potential_value": 500.00,
                "status": "New",
                "target_url": "https://hackerone.com/reports/123",
                "ai_analysis": {"risk_level": "High", "type": "XSS"}
            },
            {
                "title": "Limited Edition Merch Giveaway",
                "category": "Community Event",
                "program": "TechCorp Community",
                "severity": "N/A",
                "reward": "Free T-Shirt + Sticker",
                "potential_value": 50.00,
                "status": "Open",
                "target_url": "https://techcorp.com/giveaway",
                "ai_analysis": {"risk_level": "Low", "type": "Giveaway"}
            }
        ]
        
        print(f" Inserting {len(mock_results)} items...")
        
        for item in mock_results:
            response = supabase.table("bounties").insert(item).execute()
            print(f" Saved: {item['title']} | Reward: {item['reward']}")
            
        print(f"✅ Scan completed! Data inserted successfully.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise

if __name__ == "__main__":
    scrape_bounties()
