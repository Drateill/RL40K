#!/usr/bin/env python3
"""
Script pour ajouter la propriété range à toutes les armes
"""
import json
import os

def add_range_to_weapons():
    """Ajoute la propriété range à toutes les armes"""
    weapons_dir = "/workspaces/avec_claude/assets/weapons/"
    
    # Mapping des types d'armes vers leur portée
    range_by_type = {
        "projectile": 800,
        "energy": 700,
        "thermal": 200,  # Courte portée pour melta
        "flame": 150,    # Très courte portée
        "chaos": 750,
        "dark_energy": 600,
        "bio_weapon": 400,
        "melee": 50      # Pour futures armes de corps à corps
    }
    
    weapon_files = [
        "base_weapons.json",
        "special_weapons.json", 
        "holy_weapons.json",
        "chaos_weapons.json"
    ]
    
    for weapon_file in weapon_files:
        file_path = os.path.join(weapons_dir, weapon_file)
        
        if not os.path.exists(file_path):
            print(f"⚠️  Fichier non trouvé: {weapon_file}")
            continue
        
        try:
            # Charger le fichier
            with open(file_path, 'r', encoding='utf-8') as f:
                weapons_data = json.load(f)
            
            # Modifier chaque arme
            modified_count = 0
            for weapon_id, weapon_data in weapons_data.items():
                if "stats" in weapon_data:
                    if "range" not in weapon_data["stats"]:
                        weapon_type = weapon_data.get("type", "projectile")
                        default_range = range_by_type.get(weapon_type, 800)
                        weapon_data["stats"]["range"] = default_range
                        modified_count += 1
                        print(f"  + {weapon_id}: range {default_range} ({weapon_type})")
            
            # Sauvegarder le fichier
            if modified_count > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(weapons_data, f, indent=2, ensure_ascii=False)
                print(f"✅ {weapon_file}: {modified_count} armes modifiées")
            else:
                print(f"✅ {weapon_file}: aucune modification nécessaire")
                
        except Exception as e:
            print(f"❌ Erreur avec {weapon_file}: {e}")
    
    print("🎯 Mise à jour des portées terminée !")

if __name__ == "__main__":
    add_range_to_weapons()