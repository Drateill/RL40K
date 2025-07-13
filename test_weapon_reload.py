#!/usr/bin/env python3
"""
Test du système de rechargement d'armes
"""
import sys
import os

# Ajouter le chemin src pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_weapon_reload():
    """Test du rechargement d'armes"""
    print("🔄 Test du système de rechargement...")
    
    try:
        # Mock pygame pour le test
        class MockPygame:
            class Rect:
                def __init__(self, x, y, w, h):
                    self.x, self.y, self.width, self.height = x, y, w, h
        
        import sys
        sys.modules['pygame'] = MockPygame()
        
        from systems.weapon_manager import WeaponManager, Weapon
        
        # Créer le gestionnaire d'armes
        weapon_manager = WeaponManager()
        
        # Vérifier qu'on a au moins le bolter de fallback
        print(f"Armes disponibles: {list(weapon_manager.weapons.keys())}")
        
        # Créer une arme (on utilise le fallback)
        weapon = Weapon("bolter_basic", weapon_manager)
        print(f"✅ Arme créée: {weapon.weapon_data['name']}")
        
        # Vérifier l'état initial
        initial_info = weapon.get_info()
        print(f"État initial: {initial_info}")
        
        # Simuler plusieurs tirs
        print("\n🔫 Simulation de tirs...")
        for i in range(5):
            can_fire = weapon.can_fire()
            print(f"Tir {i+1}: Peut tirer = {can_fire}")
            
            if can_fire:
                # Simuler un tir (sans créer de vraies projectiles)
                if weapon.current_ammo > 0:
                    weapon.current_ammo -= 1
                    if weapon.current_ammo == 0 and weapon.weapon_data["stats"]["ammo_capacity"] > 0:
                        print(f"🔄 Rechargement automatique déclenché")
                        weapon.start_reload()
                
                weapon.fire_timer = weapon.modified_stats["fire_rate"]
            
            # Mettre à jour l'arme
            weapon.update()
            
            info = weapon.get_info()
            print(f"  État: {info}")
        
        print("✅ Test de rechargement terminé!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_weapon_reload()