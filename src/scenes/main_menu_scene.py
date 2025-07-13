"""
Scène du menu principal intégrée au système de scènes
"""
import pygame
from .base_scene import BaseScene
from ..ui.scenes.main_menu import MainMenuScene

class MainMenuGameScene(BaseScene):
    """Scène de menu principal du jeu"""
    
    def __init__(self):
        super().__init__()
        self.menu = MainMenuScene()
        self.next_scene = None
        # Initialiser le système audio pour les paramètres
        try:
            from ..systems.sound_system import create_sound_manager
            self.sound_system = create_sound_manager()
        except Exception as e:
            print(f"Erreur initialisation audio: {e}")
            self.sound_system = None
        
    def handle_event(self, event):
        """Gère les événements du menu"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            print(f"🖱️ MainMenuGameScene: MOUSEBUTTONDOWN reçu à {event.pos}")
        self.menu.handle_event(event)
        
        # Vérifier l'action sélectionnée
        action = self.menu.get_selected_action()
        if action:
            print(f"🎬 MainMenuGameScene a reçu l'action: {action}")
        
        if action == "play":
            print("🚀 Transition vers la sélection d'archétype")
            self.next_scene = "archetype_selection"  # Aller vers la sélection d'archétype
        elif action == "settings":
            self.next_scene = "settings"
        elif action == "quit":
            self.next_scene = "quit"
    
    def update(self, dt):
        """Met à jour le menu"""
        self.menu.update(dt)
    
    def draw(self, screen):
        """Dessine le menu"""
        self.menu.draw(screen)
    
    def get_next_scene(self):
        """Retourne la prochaine scène à afficher"""
        scene = self.next_scene
        self.next_scene = None
        return scene