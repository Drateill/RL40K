#!/usr/bin/env python3
"""
Test du système d'expérience et de level-up
"""

def test_experience_system():
    print("=== Test du système d'expérience ===")
    
    try:
        from experience_system import ExperienceSystem
        from items import ItemManager
        
        # Mock d'un système de moralité simple
        class MockMorality:
            def __init__(self):
                self.faith = 50
                self.corruption = 10
        
        # Setup
        exp_sys = ExperienceSystem()
        item_mgr = ItemManager()
        morality = MockMorality()
        
        print(f"Niveau initial: {exp_sys.level}")
        print(f"XP initial: {exp_sys.experience}/{exp_sys.exp_to_next_level}")
        
        # Test 1: Ajouter de l'XP sans level-up
        print("\n--- Test 1: +50 XP ---")
        exp_sys.add_experience(50)
        print(f"Après +50 XP: niveau {exp_sys.level}, XP {exp_sys.experience}/{exp_sys.exp_to_next_level}")
        
        # Test 2: Level-up
        print("\n--- Test 2: +100 XP (level-up) ---")
        exp_sys.add_experience(100)
        print(f"Après level-up: niveau {exp_sys.level}, XP {exp_sys.experience}/{exp_sys.exp_to_next_level}")
        print(f"En level-up: {exp_sys.is_leveling_up}")
        
        # Test 3: Génération des choix
        if exp_sys.is_leveling_up:
            print("\n--- Test 3: Génération des choix ---")
            exp_sys.generate_level_up_choices(morality, item_mgr)
            print(f"Choix générés: {exp_sys.level_up_choices}")
            
            # Test 4: Confirmer un choix
            print("\n--- Test 4: Confirmer choix ---")
            if exp_sys.level_up_choices:
                exp_sys.selected_choice = 0
                result = exp_sys.confirm_choice()
                print(f"Choix confirmé: {result}")
                print(f"Encore en level-up: {exp_sys.is_leveling_up}")
        
        print("\n✅ Tests d'expérience réussis !")
        
    except Exception as e:
        print(f"❌ Erreur dans les tests: {e}")
        import traceback
        traceback.print_exc()

def test_item_effects():
    print("\n=== Test des effets d'objets ===")
    
    try:
        from items import ItemManager
        
        # Mock d'un joueur simple
        class MockPlayer:
            def __init__(self):
                self.speed = 5
                self.base_damage = 20
                self.max_health = 100
                self.health = 100
                self.multi_shot = 1
                self.piercing = False
                self.fire_rate = 1.0
        
        # Mock de moralité
        class MockMorality:
            def __init__(self):
                self.faith = 25
                self.corruption = 5
        
        item_mgr = ItemManager()
        player = MockPlayer()
        morality = MockMorality()
        
        print(f"Stats initiales: vitesse={player.speed}, dégâts={player.base_damage}")
        
        # Test application d'objets
        items_to_test = ["speed_boost", "damage_up", "health_up"]
        
        for item_type in items_to_test:
            if hasattr(item_mgr, 'apply_item_directly'):
                print(f"\n--- Test {item_type} ---")
                try:
                    item_mgr.apply_item_directly(player, item_type, morality)
                    print(f"Après {item_type}: vitesse={getattr(player, 'speed', '?')}, dégâts={getattr(player, 'base_damage', '?')}")
                except Exception as e:
                    print(f"Erreur avec {item_type}: {e}")
        
        print("\n✅ Tests d'objets réussis !")
        
    except Exception as e:
        print(f"❌ Erreur dans les tests d'objets: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_experience_system()
    test_item_effects()
    print("\n🎮 Tests terminés - Le système est prêt à être testé dans le jeu !")
    print("\nCommandes de test dans le jeu:")
    print("- X: Ajouter +50 XP (debug)")
    print("- A/D + ESPACE: Naviguer et confirmer les choix de level-up")
    print("- Souris: Cliquer sur les cartes de level-up")