import os
import json
from datetime import datetime
from supabase import create_client, Client
from utils import setup_logger, validate_secrets, format_response
from hunter_agent import run_hunter_scan, scan_local_promotions
from validator_agent import filter_bounties
from designer_agent_v2 import generate_logo_with_philosophy
from writer_agent import generate_competition_essay
from security_agent import check_image_safety

# Setup Logger Utama
logger = setup_logger("AI_Bounty_CEO")

# Inisialisasi Supabase Client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None


def distribute_claim_tasks(validated_item: dict, task_type: str = "bounty"):
    """Menciptakan surat perintah eksekusi klaim ke semua akun Active."""
    if not supabase:
        logger.warning("⚠️ Supabase client tidak terinisialisasi. Skip distribusi.")
        return
        
    try:
        response = supabase.table("user_profiles").select("*").eq("is_active", True).execute()
        active_accounts = response.data
        
        if not active_accounts:
            logger.warning("⚠️ Tidak ada pasukan (akun aktif) di user_profiles!")
            return

        tasks_to_insert = []
        for account in active_accounts:
            task = {
                "bounty_id": validated_item.get("id", validated_item.get("name", "unknown")),
                "profile_id": account["id"],
                "target_url": validated_item.get("link"),
                "task_payload": {
                    "email": account["email"],
                    "profile_name": account["profile_name"],
                    "task_type": task_type,
                    "price_info": validated_item.get("current_price", "N/A")
                },
                "status": "PENDING",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            tasks_to_insert.append(task)

        result = supabase.table("claim_tasks").insert(tasks_to_insert).execute()
        logger.info(f"✅ [EKSEKUSI] {len(tasks_to_insert)} tugas {task_type} berhasil dibuat!")
        
    except Exception as e:
        logger.error(f"❌ Gagal membuat tugas klaim: {str(e)}")


def main():
    """FUNGSI UTAMA ORKESTRATOR"""
    logger.info("="*50)
    logger.info("🤖 AI BOUNTY HUNTER SYSTEM STARTED")
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

    # 2. PHASE 1A: GLOBAL HUNTING
    logger.info("🔍 [PHASE 1A] Memulai scanning global...")
    raw_results = run_hunter_scan()

    if isinstance(raw_results, dict):
        for category in ["crypto_airdrops", "price_glitches"]:
            items = raw_results.get(category, [])
            if items:
                clean_items = filter_bounties(items, bounty_type=category.replace("_", " "))
                verified_items.extend(clean_items)
                
                for item in clean_items:
                    if item.get("final_status") == "APPROVED":
                        distribute_claim_tasks(item, task_type="global_bounty")
    else:
        logger.error("❌ Hunter agent returned invalid data format.")

    # 3. PHASE 1B: LOCAL PROMOTION HUNTING
    logger.info("🛍️ [PHASE 1B] Memindai glitch harga lokal...")
    local_deals = scan_local_promotions()
    
    if local_deals:
        verified_items.extend(local_deals)
        for deal in local_deals:
            distribute_claim_tasks(deal, task_type="local_glitch")
    else:
        logger.info("⏭️ Tidak ditemukan glitch harga valid saat ini.")

    logger.info(f"✅ Total item valid ditemukan: {len(verified_items)}")

    # 4. PHASE 2: ASSET GENERATION (LOGO & ESEI)
    logger.info("🎨 [PHASE 2] Generating creative assets...")
    final_packages = []

    for item in verified_items:
        package = {"item": item, "generated_at": datetime.utcnow().isoformat()}
        
        # Cek apakah item butuh aset kreatif
        if item.get("requires_creative_asset"):
            
            # Generate Logo + Filosofi
            if item.get("asset_type") == "logo":
                try:
                    creative_output = generate_logo_with_philosophy(
                        concept_name=item["name"],
                        keywords=item.get("keywords", ["modern", "tech"])
                    )
                    package["logo_philosophy"] = creative_output
                    logger.info(f"🎨 Filosofi logo '{item['name']}' siap!")
                except Exception as e:
                    logger.error(f"❌ Gagal generate logo: {str(e)}")
                    
            # Generate Esai/Jurnal
            elif item.get("asset_type") == "essay":
                try:
                    essay_draft = generate_competition_essay(
                        topic=item["name"],
                        style=item.get("writing_style", "academic"),
                        word_count=item.get("word_count", 1000)
                    )
                    package["essay_draft"] = essay_draft
                    logger.info(f"✍️ Draf esai '{item['name'][:30]}...' siap!")
                except Exception as e:
                    logger.error(f"❌ Gagal generate esai: {str(e)}")

        final_packages.append(package)

    logger.info("="*50)
    logger.info("🏁 SIKLUS HUNTING SELESAI")
    logger.info("="*50)
    
    return format_response("success", data=final_packages)


if __name__ == "__main__":
    result = main()
