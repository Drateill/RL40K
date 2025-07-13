#!/usr/bin/env python3
"""
Test simple des configurations JSON sans dépendances
"""
import json
import os

def test_weapon_configs():
    """Test de chargement des configurations JSON"""
    print("🔧 Test des configurations d'armes...")
    
    configs_path = "/workspaces/avec_claude/assets/weapons/"
    
    weapon_files = [
        "base_weapons.json",
        "special_weapons.json", 
        "holy_weapons.json",
        "chaos_weapons.json",
        "weapon_effects.json"
    ]
    
    total_weapons = 0
    
    for weapon_file in weapon_files:
        file_path = os.path.join(configs_path, weapon_file)
        
        if not os.path.exists(file_path):
            print(f"❌ Fichier manquant: {weapon_file}")
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if weapon_file == "weapon_effects.json":
                effect_count = sum(len(category) for category in data.values())
                print(f"✅ {weapon_file}: {effect_count} effets chargés")
            else:
                weapon_count = len(data)
                total_weapons += weapon_count
                print(f"✅ {weapon_file}: {weapon_count} armes chargées")
                
                # Vérifier quelques armes
                for weapon_id, weapon_data in list(data.items())[:2]:
                    print(f"   - {weapon_id}: {weapon_data.get('name', 'Sans nom')}")
        
        except json.JSONDecodeError as e:
            print(f"❌ Erreur JSON dans {weapon_file}: {e}")
        except Exception as e:
            print(f"❌ Erreur lors du chargement de {weapon_file}: {e}")
    
    print(f"\n📊 Total: {total_weapons} armes configurées")
    
    # Test de structure d'une arme
    try:
        with open(os.path.join(configs_path, "base_weapons.json"), 'r') as f:
            base_weapons = json.load(f)
        
        bolter = base_weapons.get("bolter_basic", {})
        print(f"\n🔍 Structure bolter_basic:")
        print(f"  Nom: {bolter.get('name')}")
        print(f"  Type: {bolter.get('type')}")
        print(f"  Dégâts: {bolter.get('stats', {}).get('damage')}")
        print(f"  Cadence: {bolter.get('stats', {}).get('fire_rate')}")
        print(f"  Effets: {bolter.get('effects', [])}")
        
    except Exception as e:
        print(f"❌ Erreur test structure: {e}")
    
    print("\n✅ Test des configurations terminé!")

if __name__ == "__main__":
    test_weapon_configs()