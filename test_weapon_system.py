#!/usr/bin/env python3
"""
Test du système d'armes sans dépendances lourdes
"""
import sys
import os

# Ajouter le chemin src pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_weapon_manager():
    """Test du WeaponManager"""
    print("🔧 Test du WeaponManager...")
    
    try:
        from systems.weapon_manager import WeaponManager
        
        # Initialiser le gestionnaire
        weapon_manager = WeaponManager()
        
        # Vérifier le chargement des armes
        print(f"Armes chargées: {len(weapon_manager.weapons)}")
        print(f"Effets chargés: {len(weapon_manager.effects)}")
        
        # Lister quelques armes
        print("\n📋 Armes disponibles:")
        for weapon_id in list(weapon_manager.weapons.keys())[:5]:
            weapon_data = weapon_manager.get_weapon(weapon_id)
            print(f"  - {weapon_id}: {weapon_data['name']} ({weapon_data['rarity']})")
        
        # Tester la disponibilité d'armes
        available = weapon_manager.get_available_weapons()
        print(f"\n✅ Armes disponibles sans moralité: {len(available)}")
        
        print("✅ WeaponManager fonctionne correctement!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur WeaponManager: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_weapon_class():
    """Test de la classe Weapon"""
    print("\n🔫 Test de la classe Weapon...")
    
    try:
        from systems.weapon_manager import WeaponManager, Weapon
        
        # Initialiser le gestionnaire
        weapon_manager = WeaponManager()
        
        # Créer une arme
        weapon = Weapon("bolter_basic", weapon_manager)
        print(f"Arme créée: {weapon.weapon_data['name']}")
        
        # Tester l'état de l'arme
        info = weapon.get_info()
        print(f"Info arme: {info}")
        
        # Tester si on peut tirer
        can_fire = weapon.can_fire()
        print(f"Peut tirer: {can_fire}")
        
        print("✅ Classe Weapon fonctionne correctement!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur Weapon: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_weapon_projectile():
    """Test de WeaponProjectile (sans pygame)"""
    print("\n🚀 Test de WeaponProjectile...")
    
    try:
        # Mock pygame pour le test
        class MockPygame:
            class Rect:
                def __init__(self, x, y, w, h):
                    self.x, self.y, self.width, self.height = x, y, w, h
                def colliderect(self, other):
                    return False
        
        # Remplacer pygame temporairement
        import sys
        sys.modules['pygame'] = MockPygame()
        
        from entities.weapon_projectile import WeaponProjectile
        from systems.weapon_manager import WeaponManager
        
        # Créer les données d'arme
        weapon_manager = WeaponManager()
        weapon_data = weapon_manager.get_weapon("bolter_basic")
        
        # Créer un projectile
        projectile = WeaponProjectile(
            x=100, y=100, dx=1, dy=0,
            weapon_data=weapon_data,
            effects_data=weapon_manager.effects
        )
        
        print(f"Projectile créé: dégâts={projectile.damage}, rayon={projectile.radius}")
        print(f"Effets actifs: {len(projectile.active_effects)}")
        print(f"Position: ({projectile.x}, {projectile.y})")
        
        print("✅ WeaponProjectile fonctionne correctement!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur WeaponProjectile: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Exécuter tous les tests"""
    print("🧪 === TEST DU SYSTÈME D'ARMES ===\n")
    
    tests = [
        test_weapon_manager,
        test_weapon_class,
        test_weapon_projectile
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test échoué avec exception: {e}")
            results.append(False)
    
    # Résumé
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 === RÉSULTATS ===")
    print(f"Tests réussis: {passed}/{total}")
    
    if passed == total:
        print("🎉 Tous les tests sont passés! Le système d'armes est fonctionnel.")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)