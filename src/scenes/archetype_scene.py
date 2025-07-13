"""
Scène de sélection d'archétype intégrée au système de scènes
"""
import pygame
from .base_scene import BaseScene
from ..ui.scenes.archetype_selection import ArchetypeSelectionScene

class ArchetypeGameScene(BaseScene):
    """Scène de sélection d'archétype du jeu"""
    
    def __init__(self):
        super().__init__()
        self.archetype_selection = ArchetypeSelectionScene()
        self.next_scene = None
        self.selected_archetype = None
        
    def handle_event(self, event):
        """Gère les événements de la sélection d'archétype"""
        result = self.archetype_selection.handle_event(event)
        
        if result == "main_menu":
            self.next_scene = "main_menu"
        elif result == "start_game":
            self.selected_archetype = self.archetype_selection.get_selected_archetype()
            self.next_scene = "game"
    
    def update(self, dt):
        """Met à jour la sélection d'archétype"""
        self.archetype_selection.update(dt)
    
    def draw(self, screen):
        """Dessine la sélection d'archétype"""
        self.archetype_selection.draw(screen)
    
    def get_next_scene(self):
        """Retourne la prochaine scène à afficher"""
        scene = self.next_scene
        self.next_scene = None
        return scene
    
    def get_selected_archetype(self):
        """Retourne l'archétype sélectionné"""
        return self.selected_archetype