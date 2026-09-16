import os
import json
from datetime import datetime
from supabase import create_client, Client
from utils import setup_logger, validate_secrets, format_response, get_timestamp
from hunter_agent import run_hunter_scan
from validator_agent import filter_bounties
from designer_agent import generate_logo
from security_agent import check_image_safety

# Setup Logger Utama
logger = setup_logger("AI_Bounty_CEO")

# Inisialisasi Supabase Client untuk Multi-Akun Farming
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None


def distribute_claim_tasks(validated_bounty: dict):
    """
    Memetakan tugas klaim massal ke semua akun Active di user_profiles.
    Dijalankan SETELAH bounty divalidasi APPROVED oleh ValidatorAgent.
    """
    if not supabase:
        logger.warning("️ Supabase client tidak terinisialisasi. Skip distribusi klaim.")
        return
        
    try:
        # 1. Ambil semua akun fisik yang statusnya Active
        response = supabase.table("user_profiles").select("*").eq("is_active", True).execute()
        active_accounts = response.data
        
        if not active_accounts:
            logger.warning("⚠️ Tidak ada akun Active di user_profiles untuk farming!")
            return

        logger.info(f"🛡️ Mendistribusikan {len(active_accounts)} tugas klaim ke akun fisik...")
        
        # 2. Loop dan log pengiriman tugas (Nanti di sini kita insert ke tabel claim_tasks)
        for account in active_accounts:
            logger.info(f"   -> Tugas dikirim ke: {account['email']} ({account['profile_name']})")
            
            # TODO: Uncomment baris di bawah jika tabel 'claim_tasks' sudah siap di Supabase
            # task_data = {
            #     "bounty_id": validated_bounty.get("id"),
            #     "profile_id": account["id"],
            #     "target_url": validated_bounty.get("link"),
            #     "status": "PENDING_AUTOCLAIM",
            #     "created_at": datetime.utcnow().isoformat()
            # }
            # supabase.table("claim_tasks").insert(task_data).execute()

    except Exception as e:
        logger.error(f"❌ Gagal distribusi tugas klaim: {str(e)}")


def main():
    """
    FUNGSI UTAMA ORKESTRATOR
    Mengatur alur kerja dari pencarian hingga packaging aset.
    """
    logger.info("="*50)
    logger.info("🚀 AI BOUNTY HUNTER SYSTEM STARTED")
    logger.info(f"🕒 Timestamp: {datetime.utcnow().isoformat()}")
    logger.info("="*50)

    # 1. VALIDASI ENVIRONMENT
    try:
        validate_secrets()
        logger.info("✅ Secrets validated successfully.")
    except EnvironmentError as e:
        logger.error(f"❌ SYSTEM HALT: {str(e)}")
        return format_response("error", message=str(e))

    # 2. PHASE 1: HUNTING (Pencarian Data Mentah)
    logger.info("🔍 [PHASE 1] Memulai scanning bounty...")
    raw_results = run_hunter_scan()

    if not isinstance(raw_results, dict):
        logger.error("❌ Hunter agent returned invalid data format.")
        return format_response("error", message="Hunter agent failure")

    # 3. PHASE 2: VALIDATION (Filter Scam & Stok)
    logger.info("🛡️ [PHASE 2] Memvalidasi hasil hunting...")
    verified_bounties = []

    # Proses setiap kategori bounty
    for category in ["crypto_airdrops", "price_glitches", "vouchers"]:
        items = raw_results.get(category, [])
        if items:
            clean_items = filter_bounties(items, bounty_type=category.replace("_", " "))
            verified_bounties.extend(clean_items)
            
            # >>> FITUR BARU: Distribusi Klaim Massal <<<
            for item in clean_items:
                if item.get("final_status") == "APPROVED":
                    distribute_claim_tasks(item)

    logger.info(f"✅ Validasi selesai. {len(verified_bounties)} bounty lolos filter.")

    # 4. PHASE 3: ASSET GENERATION (Logo & Safety Check)
    logger.info(" [PHASE 3] Generating promotional assets...")
    final_packages = []

    for bounty in verified_bounties:
        try:
            logo_url = generate_logo(bounty.get('name', 'Bounty'))
            is_safe = check_image_safety(logo_url)
            
            package = {
                "bounty": bounty,
                "logo": logo_url,
                "is_safe": is_safe,
                "generated_at": get_timestamp()
            }
            final_packages.append(package)
            logger.info(f"📦 Paket siap: {bounty.get('name')}")
            
        except Exception as e:
            logger.error(f"❌ Gagal generate aset untuk {bounty.get('name')}: {str(e)}")

    logger.info("="*50)
    logger.info("🏁 SIKLUS HUNTING SELESAI")
    logger.info("="*50)
    
    return format_response("success", data=final_packages)


if __name__ == "__main__":
    result = main()
