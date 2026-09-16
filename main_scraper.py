import os
import json
from supabase import create_client, Client
from datetime import datetime, timezone

# Konfigurasi Environment Variables (Pastikan sudah ada di GitHub Secrets)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

def scrape_all_opportunities():
    """
    Fungsi utama AI Super Hunter: 
    Menggabungkan Scout Agent (pencari info) dengan struktur data 
    yang siap untuk Worker & Submitter Agent.
    """
    print(f"[{datetime.now()}] 🚀 Starting AI SUPER Hunter System...")
    
    # Validasi Koneksi
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError(" Supabase credentials missing! Check GitHub Secrets.")
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected to Supabase successfully")
        
        # DATA LENGKAP: MOCK DATA UNTUK SEMUA KATEGORI
        mock_results = [
            # 1. FLASH SALE (Marketplace)
            {
                "title": "iPhone 15 Pro Max - Flash Sale Terbatas",
                "category": "Electronics",
                "platform": "Shopee",
                "deal_type": "flash_sale",
                "original_price": 18999000,
                "discount_pct": 35,
                "potential_value": 12349350,
                "reward": "Hemat Rp 6.649.650",
                "status": "Active",
                "target_url": "https://shopee.co.id/iphone15-flashsale",
                "agent_status": "scouted",
                "worker_output": None,
                "ai_analysis": {"urgency": "High", "stock_remaining": 12}
            },
            # 2. BARANG TESTER / SAMPLE GRATIS
            {
                "title": "Skincare Premium Sample Set - Free Tester",
                "category": "Beauty",
                "platform": "Tokopedia",
                "deal_type": "tester",
                "original_price": 150000,
                "discount_pct": 100,
                "potential_value": 0,
                "reward": "GRATIS (Sample Only)",
                "status": "Open",
                "target_url": "https://tokopedia.com/skincare-sample",
                "agent_status": "scouted",
                "worker_output": None,
                "ai_analysis": {"eligibility": "New User Only", "stock": 50}
            },
            # 3. PROMO E-WALLET
            {
                "title": "DANA Cashback 50% Max 25rb - Semua Merchant",
                "category": "Finance",
                "platform": "DANA",
                "deal_type": "ewallet",
                "discount_pct": 50,
                "potential_value": 25000,
                "reward": "Cashback Rp 25.000",
                "voucher_code": "DANACASHBACK50",
                "status": "Valid until 30 Sep",
                "target_url": "https://dana.id/promo/cashback",
                "agent_status": "scouted",
                "worker_output": None,
                "ai_analysis": {"min_transaction": 50000}
            },
            # 4. TIKTOK GIVEAWAY
            {
                "title": "Giveaway iPad Air M2 - Tech Creator",
                "category": "Tech",
                "platform": "TikTok",
                "deal_type": "giveaway",
                "potential_value": 9000000,
                "reward": "iPad Air M2 (Free)",
                "status": "Ends in 2 days",
                "target_url": "https://tiktok.com/@creator/giveaway",
                "agent_status": "scouted",
                "worker_output": None,
                "ai_analysis": {"requirement": "Follow + Comment + Share", "participants": 12500}
            },
            # 5. BUG BOUNTY THOUSANDS DOLLAR 💰💰
            {
                "title": "RCE on Payment Gateway API - Critical",
                "category": "Cybersecurity",
                "platform": "HackerOne",
                "program": "Stripe",
                "deal_type": "bug_bounty",
                "severity": "Critical",
                "cvss_score": 9.8,
                "potential_value": 150000,  # $150,000 USD!
                "reward": "$150,000 USD",
                "status": "Open",
                "target_url": "https://hackerone.com/stripe/reports/new",
                "agent_status": "scouted",
                "worker_output": None,
                "ai_analysis": {"impact": "Full Account Takeover", "reproducible": True}
            },
            # 6. SAYEMBARA DESAIN/NASKAH
            {
                "title": "Logo Design Contest - Fintech Startup",
                "category": "Design",
                "platform": "99designs",
                "program": "FintechCo Branding",
                "deal_type": "contest",
                "severity": "N/A",
                "potential_value": 1000,  # $1,000 USD Prize
                "reward": "$1,000 USD + Exposure",
                "status": "Active",
                "target_url": "https://99designs.com/logo-design/contests/fintech",
                "agent_status": "scouted",
                "worker_output": None,
                "ai_analysis": {"brief_complexity": "Medium", "entries_so_far": 45}
            }
        ]
        
        print(f" Inserting {len(mock_results)} opportunities into database...")
        
        for item in mock_results:
            # Insert data ke tabel 'bounties'
            response = supabase.table("bounties").insert(item).execute()
            
            # Log output yang rapi
            reward_display = item.get('reward', 'N/A')
            type_display = item.get('deal_type', 'unknown').upper()
            print(f"  ✅ Saved: [{type_display}] {item['title']} | Value: {reward_display}")
            
        print(f"\n🎉 AI SUPER Hunter Scan completed successfully!")
        print(f"   Total items processed: {len(mock_results)}")
        print(f"   Next scan scheduled in 15 minutes...")
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR during scraping: {str(e)}")
        raise

if __name__ == "__main__":
    scrape_all_opportunities()
    
