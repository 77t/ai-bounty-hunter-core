import os
import json
from datetime import datetime
from utils import setup_logger, validate_secrets, format_response, get_timestamp_id
from hunter_agent import run_hunter_scan
from validator_agent import filter_bounties
from designer_agent import generate_logo
from security_agent import check_image_safety

# Setup Logger Utama
logger = setup_logger("AI_Bounty_CEO")

def main():
    """
    FUNGSI UTAMA ORKESTRATOR
    Mengatur alur kerja dari pencarian hingga packaging aset.
    """
    logger.info("="*50)
    logger.info("🚀 AI BOUNTY HUNTER SYSTEM STARTED")
    logger.info(f"⏰ Timestamp: {datetime.utcnow().isoformat()}")
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
            
    logger.info(f"✅ Validasi selesai. {len(verified_bounties)} bounty lolos filter.")

    # 4. PHASE 3: ASSET GENERATION (Logo & Safety Check)
    logger.info("🎨 [PHASE 3] Generating promotional assets...")
    final_packages = []
    
    for bounty in verified_bounties:
        task_id = get_timestamp_id()
        bounty_name = bounty.get('name', 'Unknown Bounty')
        
        # A. Generate Logo Promosi
        logo_task = {"id": task_id, "title": f"Promo: {bounty_name}"}
        logo_result = generate_logo(logo_task)
        
        if logo_result.get("status") != "success":
            logger.warning(f"⚠️ Gagal generate logo untuk {bounty_name}, skip asset generation.")
            continue
            
        # B. Security Check pada Logo
        safety_check = check_image_safety(logo_result["image_uri"])
        
        package = {
            "bounty_data": bounty,
            "promotional_logo": logo_result["image_uri"],
            "safety_status": safety_check.get("is_safe", False),
            "generated_at": datetime.utcnow().isoformat()
        }
        
        if safety_check.get("is_safe"):
            final_packages.append(package)
            logger.info(f"✅ Package siap untuk: {bounty_name}")
        else:
            logger.warning(f"🚫 Logo ditolak security check untuk: {bounty_name}")

    # 5. FINAL REPORT
    logger.info("="*50)
    logger.info(f"🏁 MISSION COMPLETE. {len(final_packages)} packages ready for dashboard.")
    logger.info("="*50)
    
    return format_response(
        status="success", 
        data={"total_verified": len(verified_bounties), "packages_ready": len(final_packages), "items": final_packages},
        message="Sistem berhasil memproses semua bounty."
    )

# Entry Point untuk GitHub Actions / Local Run
if __name__ == "__main__":
    result = main()
    print(result)
    
