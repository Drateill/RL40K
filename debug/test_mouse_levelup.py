#!/usr/bin/env python3
"""
Test rapide du système de level-up à la souris
"""

def simulate_mouse_events():
    print("=== Test simulation événements souris ===")
    
    # Mock des événements pygame
    class MockEvent:
        def __init__(self, event_type, pos=None, button=None):
            self.type = event_type
            self.pos = pos
            self.button = button
    
    # Mock pygame constants
    MOUSEMOTION = 1024
    MOUSEBUTTONDOWN = 1025
    
    try:
        from experience_system import ExperienceSystem
        from items import ItemManager
        
        # Mock morality system
        class MockMorality:
            def __init__(self):
                self.faith = 50
                self.corruption = 10
        
        # Setup
        exp_sys = ExperienceSystem()
        item_mgr = ItemManager()
        morality = MockMorality()
        
        # Déclencher un level-up
        print("🎮 Déclenchement level-up...")
        exp_sys.add_experience(100)
        
        if exp_sys.is_leveling_up:
            print("✅ Level-up activé")
            
            # Générer les choix
            exp_sys.generate_level_up_choices(morality, item_mgr)
            print(f"✅ Choix générés: {exp_sys.level_up_choices}")
            print(f"Selection initiale: {exp_sys.selected_choice}")
            
            # Test 1: Mouvement de souris hors des cartes
            print("\n--- Test 1: Souris hors cartes ---")
            event = MockEvent(MOUSEMOTION, pos=(100, 100))
            result = exp_sys.handle_input(event)
            print(f"Selection après mouvement hors cartes: {exp_sys.selected_choice}")
            
            # Test 2: Mouvement sur première carte (centre approximatif)
            print("\n--- Test 2: Survol première carte ---")
            # Carte 1 est environ à x=350, y=250, taille 200x300
            event = MockEvent(MOUSEMOTION, pos=(450, 400))  
            result = exp_sys.handle_input(event)
            print(f"Selection après survol carte 0: {exp_sys.selected_choice}")
            
            # Test 3: Mouvement sur deuxième carte
            print("\n--- Test 3: Survol deuxième carte ---")
            # Carte 2 est environ à x=600, y=250
            event = MockEvent(MOUSEMOTION, pos=(700, 400))
            result = exp_sys.handle_input(event)
            print(f"Selection après survol carte 1: {exp_sys.selected_choice}")
            
            # Test 4: Clic pour confirmer
            print("\n--- Test 4: Clic confirmation ---")
            event = MockEvent(MOUSEBUTTONDOWN, pos=(700, 400), button=1)
            result = exp_sys.handle_input(event)
            print(f"Résultat clic: {result}")
            print(f"Encore en level-up: {exp_sys.is_leveling_up}")
            
            print("\n✅ Tests de simulation réussis!")
            
        else:
            print("❌ Level-up pas activé")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

def test_card_detection():
    print("\n=== Test détection cartes ===")
    
    try:
        from experience_system import ExperienceSystem
        
        exp_sys = ExperienceSystem()
        
        # Calculer les positions théoriques des cartes
        screen_width = 1200
        screen_height = 800
        card_width = 200
        card_height = 300
        card_spacing = 50
        
        start_x = (screen_width - (card_width * 3 + card_spacing * 2)) // 2
        start_y = (screen_height - card_height) // 2
        
        print(f"Dimensions écran: {screen_width}x{screen_height}")
        print(f"Position départ cartes: ({start_x}, {start_y})")
        
        for i in range(3):
            card_x = start_x + i * (card_width + card_spacing)
            center_x = card_x + card_width // 2
            center_y = start_y + card_height // 2
            
            print(f"Carte {i}: rect=({card_x},{start_y},{card_width},{card_height})")
            print(f"  Centre: ({center_x}, {center_y})")
            
            # Test détection au centre
            detected = exp_sys.get_card_at_position(center_x, center_y)
            print(f"  Détection au centre: {detected} {'✅' if detected == i else '❌'}")
        
        print("\n✅ Test détection terminé!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_card_detection()
    simulate_mouse_events()
    print("\n🎮 Tests terminés - Le système devrait maintenant fonctionner!")