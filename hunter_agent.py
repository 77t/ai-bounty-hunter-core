import requests
import json
from datetime import datetime
from utils import setup_logger

logger = setup_logger("LocalPromoHunter")

def scan_local_promotions():
    """
    Memantau sumber promo GRATIS & TERKURASI untuk hindari diskon palsu.
    Fokus: Glitch harga, Historical Low, dan Bug Price.
    """
    local_deals = []
    
    # SUMBER 1: RSS FEED PROMOGUY (Lazada/Shopee/Tokped Verified)
    # Ini sumber komunitas yang sudah filter harga naik-turun
    try:
        rss_url = "https://promoguy.com/feed/" 
        # Note: Ganti dengan endpoint JSON/RSS aktual jika ada
        # Untuk demo, kita simulasikan parsing logic
        logger.info(" Scanning Promoguy Feed untuk Historical Low...")
        
        # Simulasi data dari feed (nanti diganti real fetch)
        mock_feed_items = [
            {
                "title": "[GLITCH] Headset Bluetooth原本是Rp 500rb jadi Rp 15rb",
                "link": "https://shopee.co.id/glitch-item-123",
                "price_current": 15000,
                "price_original": 500000,
                "verified": True,  # Flag dari komunitas
                "platform": "Shopee"
            },
            {
                "title": "Flash Sale Baju Murah Rp 50rb",
                "link": "https://lazada.co.id/normal-sale-456",
                "price_current": 50000,
                "price_original": 100000,
                "verified": False,  # Tidak ada flag glitch
                "platform": "Lazada"
            }
        ]
        
        for item in mock_feed_items:
            # FILTER KRUSIAL: Hanya ambil yang VERIFIED GLITCH / HISTORICAL LOW
            if item.get("verified") and item["price_current"] < (item["price_original"] * 0.1):
                deal = {
                    "name": item["title"],
                    "link": item["link"],
                    "current_price": f"Rp {item['price_current']:,}",
                    "original_price": f"Rp {item['price_original']:,}",
                    "discount_pct": f"-{int((1 - item['price_current']/item['price_original']) * 100)}%",
                    "platform": item["platform"],
                    "status": "VERIFIED GLITCH",
                    "found_at": datetime.utcnow().isoformat()
                }
                local_deals.append(deal)
                logger.info(f"✅ Ditemukan glitch valid: {item['title']}")
            else:
                logger.debug(f"⏭️ Skip diskon biasa/palsu: {item['title']}")
                
    except Exception as e:
        logger.error(f"❌ Gagal scan Promoguy: {str(e)}")

    # SUMBER 2: TELEGRAM CHANNEL MONITOR (TikTok Shop Glitch)
    # NOTE: Perlu install 'telethon' dan setup API ID/Hash Telegram (GRATIS)
    # Untuk sekarang, kita siapkan struktur fungsinya saja
    try:
        logger.info(" Checking Telegram Glitch Channels...")
        # Nanti di sini pakai telethon.Client untuk baca channel
        # Filter pesan yang mengandung "GLITCH" + link tiktok
        pass 
    except Exception as e:
        logger.warning(f"⚠️ Telegram monitor belum aktif: {str(e)}")

    logger.info(f"🎯 Total local deals valid ditemukan: {len(local_deals)}")
    return local_deals
