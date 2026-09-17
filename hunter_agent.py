def main():
    # ... kode existing ...
    
    # 1. VALIDASI ENVIRONMENT
    try:
        validate_secrets()
        logger.info("✅ Secrets validated successfully.")
    except EnvironmentError as e:
        logger.error(f" SYSTEM HALT: {str(e)}")
        return format_response("error", message=str(e))

    # >>> TAMBAHKAN 3 BARIS INI DI SINI <<<
    from hunter_agent import cleanup_expired_data
    logger.info("🧹 [PRE-CHECK] Membersihkan data kadaluarsa di Supabase...")
    cleanup_expired_data(supabase)
    # >>> SELESAI <<<

    verified_items = []
    # ... sisa kode hunting ...
    
