import os
import json
from datetime import datetime
from supabase import create_client, Client
from utils import setup_logger, validate_secrets, format_response
from hunter_agent import run_hunter_scan
from validator_agent import filter_bounties
from designer_agent import generate_logo
from security_agent import check_image_safety
# >>> TAMBAHKAN IMPORT MODUL LOKAL INI <<<
from hunter_agent import scan_local_promotions 

# Setup Logger Utama
logger = setup_logger("AI_Bounty_CEO")

# Inisialisasi Supabase Client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None


def distribute_claim_tasks(validated_item: dict, task_type: str = "bounty"):
    """
    Menciptakan surat perintah eksekusi klaim ke semua akun Active.
    Mendukung bounty bug maupun glitch harga lokal.
    """
    if not supabase:
        logger.warning("️ Supabase client tidak terinisialisasi. Skip distribusi.")
        return
        
    try:
        # 1. Ambil akun fisik yang siap tempur
        response = supabase.table("user_profiles").select("*").eq("is_active", True).execute()
        active_accounts = response.data
        
        if not active_accounts:
            logger.warning(" Tidak ada pasukan (akun aktif) di user_profiles!")
            return

        # 2. Siapkan payload tugas untuk setiap akun
        tasks_to_insert = []
        for account in active_accounts:
            task = {
                "bounty_id": validated_item.get("id", validated_item.get("name", "unknown")),
                "profile_id": account["id"],
                "target_url": validated_item.get("link"),
                "task_payload": {
                    "email": account["email"],
                    "profile_name": account["profile_name"],
                    "task_type": task_type, # Bedakan antara 'bounty' dan 'glitch'
                    "price_info": validated_item.get("current_price", "N/A")
                },
                "status": "PENDING",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            tasks_to_insert.append(task)

        # 3. TEMBAKKAN KE DATABASE CLAIM_TASKS
        result = supabase.table("claim_tasks").insert(tasks_to_insert).execute()
        
        logger.info(f" [EKSEKUSI] {len(tasks_to_insert)} tugas {task_type} berhasil dibuat!")
        for acc in active_accounts:
            logger.info(f"   -> Target: {acc['email']} | Item: {validated_item.get('name')}")

    except Exception as e:
        logger.error(f"❌ Gagal membuat tugas klaim: {str(e)}")


def main():
    """
    FUNGSI UTAMA ORKESTRATOR
    """
    logger.info("="*50)
    logger.info(" AI BOUNTY HUNTER SYSTEM STARTED")
    logger.info(f"🕒 Timestamp: {datetime.utcnow().isoformat()}")
    logger.info("="*50)

    # 1. VALIDASI ENVIRONMENT
    try:
        validate_secrets()
        logger.info("✅ Secrets validated successfully.")
    except EnvironmentError as e:
        logger.error(f"❌ SYSTEM HALT: {str(e)}")
        return format_response("error", message=str(e))

    verified_items = []

    # 2. PHASE 1A: GLOBAL HUNTING (Crypto & Bug Bounty)
    logger.info("🔍 [PHASE 1A] Memulai scanning global...")
    raw_results = run_hunter_scan()

    if isinstance(raw_results, dict):
        for category in ["crypto_airdrops", "price_glitches"]:
            items = raw_results.get(category, [])
            if items:
                clean_items = filter_bounties(items, bounty_type=category.replace("_", " "))
                verified_items.extend(clean_items)
                
                # Distribusi otomatis untuk item APPROVED
                for item in clean_items:
                    if item.get("final_status") == "APPROVED":
                        distribute_claim_tasks(item, task_type="global_bounty")
    else:
        logger.error("❌ Hunter agent returned invalid data format.")

    # 3. PHASE 1B: LOCAL PROMOTION HUNTING (Anti-Fake Discount)
    logger.info("🛍️ [PHASE 1B] Memindai glitch harga lokal (TikTok/Lazada/Shopee)...")
    local_deals = scan_local_promotions()
    
    if local_deals:
        verified_items.extend(local_deals)
        # Untuk glitch lokal, langsung distribusikan karena sifatnya flash sale (cepat habis)
        for deal in local_deals:
            distribute_claim_tasks(deal, task_type="local_glitch")
    else:
        logger.info("⏭️ Tidak ditemukan glitch harga valid saat ini.")

    logger.info(f"✅ Total item valid ditemukan: {len(verified_items)}")

    # 4. PHASE 2: ASSET GENERATION (Hanya untuk Global Bounty)
    logger.info(" [PHASE 2] Generating promotional assets...")
    final_packages = []

    for item in verified_items:
        # Hanya generate logo untuk bounty global, glitch lokal tidak perlu
        if item.get("task_type", "global_bounty") == "global_bounty":
            try:
                logo_url = generate_logo(item.get('name', 'Bounty'))
                is_safe = check_image_safety(logo_url)
                
                package = {
                    "item": item,
                    "logo": logo_url,
                    "is_safe": is_safe,
                    "generated_at": datetime.utcnow().isoformat()
                }
                final_packages.append(package)
                logger.info(f"📦 Paket aset siap: {item.get('name')}")
                
            except Exception as e:
                logger.error(f"❌ Gagal generate aset: {str(e)}")
        else:
            # Masukkan glitch lokal tanpa logo
            final_packages.append({"item": item, "generated_at": datetime.utcnow().isoformat()})

    logger.info("="*50)
    logger.info(" SIKLUS HUNTING SELESAI")
    logger.info("="*50)
    
    return format_response("success", data=final_packages)


if __name__ == "__main__":
    result = main()
