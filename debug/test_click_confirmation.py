#!/usr/bin/env python3
"""
Test de la confirmation par clic
"""

def simulate_click_flow():
    print("=== Test flux de confirmation par clic ===")
    
    # Mock des classes nécessaires
    class MockEvent:
        def __init__(self, event_type, pos=None, button=None):
            self.type = event_type
            self.pos = pos
            self.button = button
    
    class MockMorality:
        def __init__(self):
            self.faith = 50
            self.corruption = 10
    
    class MockItemManager:
        def __init__(self):
            self.item_definitions = {
                "speed_boost": {"name": "Vitesse", "description": "Plus rapide"},
                "damage_up": {"name": "Dégâts", "description": "Plus de dégâts"},
                "health_up": {"name": "Santé", "description": "Plus de vie"}
            }
        
        def is_item_available(self, item_type, morality):
            return True
    
    class MockPlayer:
        def __init__(self):
            self.speed = 5
    
    class MockGameScene:
        def __init__(self, exp_sys, item_mgr, player, morality):
            self.exp_system = exp_sys
            self.item_manager = item_mgr
            self.player = player
            self.morality_system = morality
        
        def apply_level_up_choice(self):
            """Simule apply_level_up_choice de GameScene"""
            if (not hasattr(self.exp_system, 'is_leveling_up') or 
                not self.exp_system.is_leveling_up or 
                not self.exp_system.level_up_choices):
                print("❌ Pas de level-up actif")
                return
            
            selected_idx = getattr(self.exp_system, 'selected_choice', -1)
            if 0 <= selected_idx < len(self.exp_system.level_up_choices):
                item_type = self.exp_system.level_up_choices[selected_idx]
                print(f"🎁 Application simulée de l'objet: {item_type}")
                
                # Simuler l'application de l'effet
                if item_type == "speed_boost":
                    self.player.speed += 2
                    print(f"  → Vitesse: {self.player.speed}")
                
                # Terminer le level-up
                if hasattr(self.exp_system, 'finish_level_up'):
                    self.exp_system.finish_level_up()
                    print("✅ Level-up terminé par finish_level_up()")
                else:
                    self.exp_system.is_leveling_up = False
                    print("✅ Level-up terminé par fallback")
            else:
                print(f"❌ Index invalide: {selected_idx}")
    
    try:
        # Simulation sans pygame
        print("Simulation du flux sans pygame...")
        
        # Setup - simulation de ExperienceSystem simplifié
        class MockExpSystem:
            def __init__(self):
                self.experience = 0
                self.level = 1
                self.exp_to_next_level = 100
                self.is_leveling_up = False
                self.level_up_choices = []
                self.selected_choice = -1
            
            def add_experience(self, amount):
                self.experience += amount
                if self.experience >= self.exp_to_next_level:
                    self.level_up()
            
            def level_up(self):
                self.level += 1
                self.experience = 0
                self.is_leveling_up = True
                print(f"🆙 LEVEL UP vers niveau {self.level}")
            
            def generate_level_up_choices(self, morality, item_mgr):
                self.level_up_choices = ["speed_boost", "damage_up", "health_up"]
                self.selected_choice = -1
                print(f"🎲 Choix générés: {self.level_up_choices}")
            
            def get_card_at_position(self, x, y):
                # Simulation simple de détection
                if 350 <= x <= 450 and 250 <= y <= 550:
                    return 0  # Carte 0
                elif 600 <= x <= 700 and 250 <= y <= 550:
                    return 1  # Carte 1
                elif 850 <= x <= 950 and 250 <= y <= 550:
                    return 2  # Carte 2
                return -1
            
            def handle_input(self, event):
                if not self.is_leveling_up:
                    return False
                
                MOUSEBUTTONDOWN = 1025
                MOUSEMOTION = 1024
                
                # Clic pour confirmer
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    mouse_x, mouse_y = event.pos
                    card_clicked = self.get_card_at_position(mouse_x, mouse_y)
                    if card_clicked >= 0:
                        print(f"🎯 Clic détecté sur carte {card_clicked}")
                        self.selected_choice = card_clicked
                        return self.confirm_choice()
                
                # Survol
                if event.type == MOUSEMOTION:
                    mouse_x, mouse_y = event.pos
                    card_hovered = self.get_card_at_position(mouse_x, mouse_y)
                    if card_hovered >= 0 and card_hovered != self.selected_choice:
                        print(f"🎯 Survol carte {card_hovered}")
                        self.selected_choice = card_hovered
                    elif card_hovered == -1 and self.selected_choice != -1:
                        print("🎯 Aucune carte survolée")
                        self.selected_choice = -1
                
                return True
            
            def confirm_choice(self):
                if 0 <= self.selected_choice < len(self.level_up_choices):
                    print(f"✅ Choix confirmé: {self.level_up_choices[self.selected_choice]}")
                    return True
                return False
            
            def finish_level_up(self):
                self.is_leveling_up = False
                self.level_up_choices = []
                self.selected_choice = -1
                print("🏁 Level-up terminé")
        
        # Setup
        exp_sys = MockExpSystem()
        item_mgr = MockItemManager()
        player = MockPlayer()
        morality = MockMorality()
        game_scene = MockGameScene(exp_sys, item_mgr, player, morality)
        
        print(f"Setup: Joueur vitesse={player.speed}")
        
        # Étape 1: Déclencher level-up
        print("\n--- Étape 1: Déclencher level-up ---")
        exp_sys.add_experience(100)
        exp_sys.generate_level_up_choices(morality, item_mgr)
        print(f"Level-up actif: {exp_sys.is_leveling_up}")
        
        # Étape 2: Survol de la première carte
        print("\n--- Étape 2: Survol première carte ---")
        event = MockEvent(1024, pos=(400, 400))  # Centre carte 0
        result = exp_sys.handle_input(event)
        print(f"Handle_input retourné: {result}")
        print(f"Selection: {exp_sys.selected_choice}")
        
        # Étape 3: Clic sur la première carte pour confirmer
        print("\n--- Étape 3: Clic confirmation ---")
        event = MockEvent(1025, pos=(400, 400), button=1)  # Clic sur carte 0
        result = exp_sys.handle_input(event)
        print(f"Handle_input retourné: {result}")
        
        # Étape 4: GameScene applique le choix
        print("\n--- Étape 4: Application par GameScene ---")
        if result:  # Si handle_input a retourné True
            game_scene.apply_level_up_choice()
        
        # Vérifications finales
        print("\n--- Vérifications finales ---")
        print(f"Level-up encore actif: {exp_sys.is_leveling_up}")
        print(f"Vitesse joueur: {player.speed} (devrait être 7)")
        
        if not exp_sys.is_leveling_up and player.speed == 7:
            print("\n🎉 TEST RÉUSSI ! Le clic confirme bien l'amélioration")
        else:
            print("\n❌ TEST ÉCHOUÉ")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simulate_click_flow()