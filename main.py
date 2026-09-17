# Tambahkan di bagian import atas main.py
from designer_agent_v2 import generate_logo_with_philosophy
from writer_agent import generate_competition_essay

# ... di dalam loop final_packages di main.py ...

for item in verified_items:
    # Cek apakah item ini butuh aset kreatif (misal dari sayembara)
    if item.get("requires_creative_asset"):
        
        # 1. Generate Logo + Filosofi
        if item.get("asset_type") == "logo":
            creative_output = generate_logo_with_philosophy(
                concept_name=item["name"],
                keywords=item.get("keywords", ["modern", "tech"])
            )
            package["logo_philosophy"] = creative_output
            
        # 2. Generate Esai/Jurnal
        elif item.get("asset_type") == "essay":
            essay_draft = generate_competition_essay(
                topic=item["name"],
                style=item.get("writing_style", "academic"),
                word_count=item.get("word_count", 1000)
            )
            package["essay_draft"] = essay_draft
            
    final_packages.append(package)
    
