import os
import json
import requests
from datetime import datetime, timedelta
from utils import setup_logger

logger = setup_logger("HunterAgent")

# --- KONFIGURASI SUMBER DATA ---
PROMOGUY_FEED_URL = "https://promoguy.com/feed/" 

def run_hunter_scan():
    """
    FUNGSI LAMA: Scanning Global (Crypto Airdrops & Price Glitches).
    Mengembalikan dictionary dengan key 'crypto_airdrops' dan 'price_glitches'.
    """
    logger.info("🌍 Memulai scanning global (Crypto & Glitches)...")
    
    # SIMULASI HASIL SCAN GLOBAL (Nanti ganti dengan logika scraping/API asli)
    mock_global_results = {
        "crypto_airdrops": [
            {
                "id": "airdrop_001",
                "name": "Nexus Protocol Airdrop",
                "link": "https://nexus-protocol.io/airdrop",
                "reward": "$50 - $500 USDT",
                "difficulty": "Easy",
                "final_status": "APPROVED"
            }
        ],
        "price_glitches": [
            {
                "id": "glitch_global_001",
                "name": "Amazon Kindle Paperwhite Price Error",
                "link": "https://amazon.com/dp/B08KTZ8249",
                "current_price": "$15.99",
                "original_price": "$139.99",
                "discount_pct": "-88%",
                "final_status": "APPROVED"
            }
        ]
    }
    
    logger.info(f"✅ Scanning global selesai. Ditemukan {len(mock_global_results['crypto_airdrops'])} airdrop & {len(mock_global_results['price_glitches'])} glitch.")
    return mock_global_results


def scan_local_promotions():
    """
    FUNGSI BARU: Memantau sumber promo GRATIS & TERKURASI untuk hindari diskon palsu.
    Fokus: Glitch harga, Historical Low, dan Bug Price di TikTok/Lazada/Shopee.
    """
    local_deals = []
    
    # SUMBER 1: RSS FEED PROMOGUY (Lazada/Shopee/Tokped Verified)
    try:
        logger.info("🛍️ Scanning Promoguy Feed untuk Historical Low...")
        
        # Simulasi data dari feed (nanti diganti real fetch via requests.get)
        mock_feed_items = [
            {
                "title": "[GLITCH] Headset Bluetooth原本是Rp 500rb jadi Rp 15rb",
                "link": "https://shopee.co.id/glitch-item-123",
                "price_current": 15000,
                "price_original": 500000,
                "verified": True, 
                "platform": "Shopee"
            },
            {
                "title": "Flash Sale Baju Murah Rp 50rb",
                "link": "https://lazada.co.id/normal-sale-456",
                "price_current": 50000,
                "price_original": 100000,
                "verified": False, 
                "platform": "Lazada"
            }
        ]
        
        for item in mock_feed_items:
            # FILTER KRUSIAL: Hanya ambil yang VERIFIED GLITCH / HISTORICAL LOW (>90% off)
            if item.get("verified") and item["price_current"] < (item["price_original"] * 0.1):
                deal = {
                    "name": item["title"],
                    "link": item["link"],
                    "current_price": f"Rp {item['price_current']:,}",
                    "original_price": f"Rp {item['price_original']:,}",
                    "discount_pct": f"-{int((1 - item['price_current']/item['price_original']) * 100)}%",
                    "platform": item["platform"],
                    "status": "VERIFIED GLITCH",
                    "found_at": datetime.utcnow().isoformat(),
                    "requires_creative_asset": False, 
                    "task_type": "local_glitch"
                }
                local_deals.append(deal)
                logger.info(f"✅ Ditemukan glitch valid: {item['title']}")
            else:
                logger.debug(f"️ Skip diskon biasa/palsu: {item['title']}")
                
    except Exception as e:
        logger.error(f"❌ Gagal scan Promoguy: {str(e)}")

    # SUMBER 2: TELEGRAM CHANNEL MONITOR (Placeholder)
    try:
        logger.info("📱 Checking Telegram Glitch Channels...")
        pass 
    except Exception as e:
        logger.warning(f"⚠️ Telegram monitor belum aktif: {str(e)}")

    logger.info(f" Total local deals valid ditemukan: {len(local_deals)}")
    return local_deals


def cleanup_expired_data(supabase_client):
    """
    AUTO-CLEANUP: Hapus data kadaluarsa dari Supabase agar tidak penuh sesak.
    Retensi: Claim tasks > 30 hari (kecuali status PENDING) akan dihapus.
    """
    if not supabase_client:
        logger.warning("⚠️ Supabase client tidak tersedia. Skip cleanup.")
        return
        
    try:
        # Hitung batas waktu 30 hari lalu
        cutoff_date = (datetime.utcnow() - timedelta(days=30)).isoformat()
        
        # 1. Backup data yang akan dihapus ke file JSON lokal (KEAMANAN FIRST!)
        backup_result = supabase_client.table("claim_tasks") \
            .select("*") \
            .lt("created_at", cutoff_date) \
            .neq("status", "PENDING") \
            .execute()
            
        if backup_result.data:
            backup_filename = f"backup_claim_tasks_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            with open(backup_filename, "w") as f:
                json.dump(backup_result.data, f, indent=2)
            logger.info(f"💾 Backup {len(backup_result.data)} data kadaluarsa ke {backup_filename}")
        
        # 2. Hapus data kadaluarsa dari database
        delete_result = supabase_client.table("claim_tasks") \
            .delete() \
            .lt("created_at", cutoff_date) \
            .neq("status", "PENDING") \
            .execute()
            
        deleted_count = len(delete_result.data) if hasattr(delete_result, 'data') and delete_result.data else 0
        logger.info(f"🧹 [CLEANUP] {deleted_count} tugas klaim kadaluarsa berhasil dihapus permanen!")
        
    except Exception as e:
        logger.error(f"❌ Gagal melakukan cleanup data: {str(e)}")
        
