import os
import json
import time
import random
import requests
import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment variables dari file .env
load_dotenv()

# ==========================================
# KONFIGURASI SUPABASE (VIA REST API - ANDROID SAFE)
# ==========================================
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://xnpxiddpfqolfqchtadw.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_KEY:
    print("️ PERINGATAN: SUPABASE_SERVICE_ROLE_KEY tidak ditemukan di .env!")
    exit(1)

# Headers khusus untuk Supabase REST API
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates" 
}

# ==========================================
# HEADERS & ANTI-BOT CONFIGURATION
# ==========================================
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0'
]

SCAM_KEYWORDS = ["guaranteed profit", "send crypto first", "private key needed"]

def get_random_headers():
    return {'User-Agent': random.choice(USER_AGENTS)}

# ==========================================
# AI ANALYSIS ENGINE
# ==========================================
def analyze_real_data(title, desc, reward, category):
    text = f"{title} {desc}".lower()
    risk = "Low"
    if any(k in text for k in ["beta", "testnet", "new"]): risk = "Medium"
    if any(k in text for k in ["anonymous", "high yield"]): risk = "High"
    
    elig = "Open to All"
    if "whitelist" in text: elig = "Whitelist Only"
    if "kyc" in text: elig = "KYC Required"
    
    steps = ["1. Visit target URL.", "2. Read terms.", "3. Complete actions.", "4. Submit entry."]
    if category == "Bug Bounty": steps = ["1. Review scope.", "2. Perform recon.", "3. Find vuln.", "4. Write PoC.", "5. Submit report."]
    elif category == "Crypto Airdrop": steps = ["1. Connect wallet.", "2. Do on-chain tasks.", "3. Join Discord.", "4. Fill form."]
    
    return {
        "risk_level": risk, "eligibility": elig, "step_by_step_guide": steps,
        "is_scam": any(k in text for k in SCAM_KEYWORDS),
        "analyzed_at": datetime.now(timezone.utc).isoformat()
    }

# ==========================================
# FUNGSI INSERT KE SUPABASE (VIA HTTPX - TANPA LIBRARY SUPABASE)
# ==========================================
def save_to_supabase(item):
    """Insert data ke table 'bounties' via REST API langsung"""
    url = f"{SUPABASE_URL}/rest/v1/bounties"
    try:
        response = httpx.post(url, headers=HEADERS, json=item, timeout=10)
        if response.status_code in [200, 201, 204]:
            print(f"✅ Saved: {item['title']}")
            return True
        else:
            print(f" Error {response.status_code}: {response.text[:100]}")
            return False
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

# ==========================================
# SCRAPING MODULES
# ==========================================
def scrape_airdrop_alert():
    print("️ Scraping AirdropAlert...")
    try:
        resp = requests.get("https://airdropalert.com/latest", headers=get_random_headers(), timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        items = []
        # Selector mungkin perlu disesuaikan jika situs update struktur
        for card in soup.select('div.airdrop-card, article.post-item, .list-group-item')[:5]:
            title_el = card.select_one('h3, h4, .title')
            link_el = card.select_one('a[href*="airdrop"]')
            if title_el and link_el:
                title = title_el.get_text(strip=True)
                link = link_el['href']
                if not link.startswith('http'): link = f"https://airdropalert.com{link}"
                analysis = analyze_real_data(title, "", "TBA", "Crypto Airdrop")
                if not analysis["is_scam"]:
                    items.append({
                        "title": title, "program": "AirdropAlert", "reward": "TBA", 
                        "target_url": link, "category": "Crypto Airdrop", 
                        "description": "", "ai_analysis": analysis
                    })
        return items
    except Exception as e:
        print(f"❌ AirdropAlert Error: {e}")
        return []

def scrape_hackerone_fallback():
    """Fallback data Bug Bounty valid karena H1 sering block scraper"""
    return [{
        "title": "Stripe Security Bug Bounty", "program": "HackerOne", "reward": "$150,000 Max",
        "target_url": "https://hackerone.com/stripe", "category": "Bug Bounty",
        "description": "Official Stripe security program. Focus on payment gateway RCE.",
        "ai_analysis": analyze_real_data("Stripe RCE", "Payment gateway vuln", "$150k", "Bug Bounty")
    }]

# ==========================================
# MAIN EXECUTION
# ==========================================
def main():
    print("🚀 TEGUH HUNTER ANDROID SCANNER STARTED...")
    all_items = []
    
    # Jalankan scraping
    all_items.extend(scrape_airdrop_alert())
    all_items.extend(scrape_hackerone_fallback())
    
    print(f"📦 Total items collected: {len(all_items)}")
    
    # Simpan ke Supabase satu per satu
    success_count = 0
    for item in all_items:
        if save_to_supabase(item):
            success_count += 1
            
    print(f"✨ DONE. {success_count}/{len(all_items)} items saved to Supabase.")

if __name__ == "__main__":
    main()
