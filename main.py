import os
import json
from datetime import datetime
from supabase import create_client, Client
from utils import setup_logger, validate_secrets, format_response
from hunter_agent import run_hunter_scan
from validator_agent import filter_bounties
from designer_agent import generate_logo
from security_agent import check_image_safety

# Setup Logger Utama
logger = setup_logger("AI_Bounty_CEO")

# Inisialisasi Supabase Client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None


def distribute_claim_tasks(validated_bounty: dict):
    """
    Menciptakan surat perintah eksekusi klaim ke semua akun Active.
    Data masuk ke tabel claim_tasks sebagai antrian resmi.
    """
    if not supabase:
        logger.warning("⚠️ Supabase client tidak terinisialisasi. Skip distribusi.")
        return
        
    try:
        # 1. Ambil akun fisik yang siap tempur
        response = supabase.table("user_profiles").select("*").eq("is_active", True).execute()
        active_accounts = response.data
        
        if not active_accounts:
            logger.warning("️ Tidak ada pasukan (akun aktif) di user_profiles!")
            return

        # 2. Siapkan payload tugas untuk setiap akun
        tasks_to_insert = []
        for account in active_accounts:
            task = {
                "bounty_id": validated_bounty.get("id", "unknown"),
                "profile_id": account["id"],
                "target_url": validated_bounty.get("link"),
                "task_payload": {
                    "email": account["email"],
                    "profile_name": account["profile_name"]
                    # Cookie & Password tidak disimpan di task demi keamanan
                    # Dashboard akan mengambil cookie langsung dari user_profiles saat eksekusi
                },
                "status": "PENDING",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            tasks_to_insert.append(task)

        # 3. TEMBAKKAN KE DATABASE CLAIM_TASKS
        result = supabase.table("claim_tasks").insert(tasks_to_insert).execute()
        
        logger.info(f"🛡️ [EKSEKUSI] {len(tasks_to_insert)} surat perintah klaim berhasil dibuat!")
        for acc in active_accounts:
            logger.info(f"   -> Target: {acc['email']} | Bounty: {validated_bounty.get('name')}")

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

    # 2. PHASE 1: HUNTING
    logger.info("🔍 [PHASE 1] Memulai scanning bounty...")
    raw_results = run_hunter_scan()

    if not isinstance(raw_results, dict):
        logger.error("❌ Hunter agent returned invalid data format.")
        return format_response("error", message="Hunter agent failure")

    # 3. PHASE 2: VALIDATION & DISTRIBUTION
    logger.info("🛡️ [PHASE 2] Memvalidasi & Mendistribusikan Tugas...")
    verified_bounties = []

    for category in ["crypto_airdrops", "price_glitches", "vouchers"]:
        items = raw_results.get(category, [])
        if items:
            clean_items = filter_bounties(items, bounty_type=category.replace("_", " "))
            verified_bounties.extend(clean_items)
            
            # >>> EKSEKUSI LANGSUNG SAAT APPROVED <<<
            for item in clean_items:
                if item.get("final_status") == "APPROVED":
                    distribute_claim_tasks(item)

    logger.info(f"✅ Validasi selesai. {len(verified_bounties)} bounty lolos filter.")

    # 4. PHASE 3: ASSET GENERATION
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
                "generated_at": datetime.utcnow().isoformat()
            }
            final_packages.append(package)
            logger.info(f"📦 Paket siap: {bounty.get('name')}")
            
        except Exception as e:
            logger.error(f"❌ Gagal generate aset: {str(e)}")

    logger.info("="*50)
    logger.info("🏁 SIKLUS HUNTING SELESAI")
    logger.info("="*50)
    
    return format_response("success", data=final_packages)


if __name__ == "__main__":
    result = main()
