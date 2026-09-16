import re
from utils import setup_logger

logger = setup_logger("ValidatorAgent")

class BountyValidator:
    def __init__(self):
        # Daftar kata kunci yang sering dipakai scammer
        self.scam_keywords = [
            "send eth first", "private key", "seed phrase", 
            "connect wallet to claim", "pay gas fee only",
            "limited time 5 min", "urgent verify"
        ]
        
        # Pola URL mencurigakan (bukan domain resmi)
        self.suspicious_domains = ["bit.ly", "tinyurl", "t.co", "short.link"]

    def check_scam_risk(self, item: dict) -> dict:
        """
        Menganalisis risiko scam berdasarkan deskripsi dan link.
        Score 0-100. >70 dianggap berbahaya.
        """
        risk_score = 0
        reasons = []
        
        text_to_check = f"{item.get('name', '')} {item.get('desc', '')}".lower()
        link = item.get('link', '').lower()

        # 1. Cek Keyword Berbahaya
        for keyword in self.scam_keywords:
            if keyword in text_to_check:
                risk_score += 30
                reasons.append(f"Terdeteksi frasa mencurigakan: '{keyword}'")

        # 2. Cek Domain Pendek/Anonymous
        for domain in self.suspicious_domains:
            if domain in link:
                risk_score += 40
                reasons.append(f"Menggunakan link pendek/anonim: {domain}")

        # 3. Cek Jika Tidak Ada Detail Jelas
        if len(text_to_check) < 20:
            risk_score += 20
            reasons.append("Deskripsi terlalu singkat/tidak jelas")

        status = "SAFE" if risk_score < 50 else ("WARNING" if risk_score < 80 else "SCAM_DETECTED")
        
        logger.info(f"Validasi Scam [{item.get('name')}]: {status} (Score: {risk_score})")
        
        return {
            "is_safe": risk_score < 50,
            "risk_score": risk_score,
            "status": status,
            "reasons": reasons
        }

    def check_stock_availability(self, item: dict) -> bool:
        """
        Simulasi cek stok. 
        Di production, ini harus hit API marketplace/scrape halaman produk real-time.
        """
        # Contoh logika sederhana: Jika harga glitch terlalu murah (<10% harga normal), 
        # kemungkinan besar stok sudah habis atau sistem error.
        normal_price = item.get('normal_price', 0)
        glitch_price = item.get('glitch_price', 0)
        
        if normal_price > 0 and glitch_price > 0:
            discount_pct = ((normal_price - glitch_price) / normal_price) * 100
            if discount_pct > 95:  # Diskon >95% biasanya stok habis dalam detik
                logger.warning(f"Stok kemungkinan habis: Diskon {discount_pct:.0f}% terlalu ekstrem")
                return False
                
        # Default anggap masih ada stok jika tidak ada data spesifik
        return True

    def validate_bounty(self, bounty_item: dict, bounty_type: str) -> dict:
        """
        Fungsi utama validasi. Menggabungkan cek scam + cek stok.
        """
        result = {"original_data": bounty_item, "type": bounty_type}
        
        # A. Validasi Scam (Untuk semua jenis bounty)
        scam_check = self.check_scam_risk(bounty_item)
        result["scam_analysis"] = scam_check
        
        if not scam_check["is_safe"]:
            result["final_status"] = "REJECTED_SCAM"
            logger.warning(f"Bounty DITOLAK karena risiko scam: {bounty_item.get('name')}")
            return result

        # B. Validasi Stok (Khusus untuk Price Glitch/Voucher Fisik)
        if bounty_type in ["price_glitch", "voucher_physical"]:
            stock_check = self.check_stock_availability(bounty_item)
            result["stock_available"] = stock_check
            
            if not stock_check:
                result["final_status"] = "REJECTED_OUT_OF_STOCK"
                logger.warning(f"Bounty DITOLAK karena stok habis: {bounty_item.get('name')}")
                return result

        # C. Lolos Semua Filter
        result["final_status"] = "APPROVED"
        logger.info(f"Bounty DISETUJUI: {bounty_item.get('name')}")
        return result

# Helper function untuk dipanggil di main.py
def filter_bounties(raw_bounties: list, bounty_type: str) -> list:
    validator = BountyValidator()
    approved_items = []
    
    for item in raw_bounties:
        validation = validator.validate_bounty(item, bounty_type)
        if validation["final_status"] == "APPROVED":
            approved_items.append(item)
            
    logger.info(f"Filter selesai: {len(approved_items)}/{len(raw_bounties)} item lolos validasi.")
    return approved_items
 
