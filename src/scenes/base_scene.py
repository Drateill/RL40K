"""
Scène de base - Interface commune pour toutes les scènes
Définit les méthodes que chaque scène doit implémenter
"""
import pygame

class BaseScene:
    """Classe de base pour toutes les scènes du jeu"""
    
    def __init__(self):
        self.scene_manager = None  # Référence vers le gestionnaire
        self.is_active = False
        self.is_paused = False
    
    def on_enter(self):
        """Appelé quand la scène devient active"""
        self.is_active = True
        self.is_paused = False
        print(f"🎬 Entrée dans {self.__class__.__name__}")
    
    def on_exit(self):
        """Appelé quand la scène est quittée"""
        self.is_active = False
        print(f"🚪 Sortie de {self.__class__.__name__}")
    
    def on_pause(self):
        """Appelé quand la scène est mise en pause"""
        self.is_paused = True
        print(f"⏸️ Pause de {self.__class__.__name__}")
    
    def on_resume(self):
        """Appelé quand la scène reprend après une pause"""
        self.is_paused = False
        print(f"▶️ Reprise de {self.__class__.__name__}")
    
    def handle_event(self, event):
        """Gère les événements pygame"""
        # Les classes filles doivent surcharger cette méthode
        pass
    
    def update(self, dt):
        """Met à jour la logique de la scène"""
        # Les classes filles doivent surcharger cette méthode
        pass
    
    def draw(self, screen):
        """Dessine la scène à l'écran"""
        # Les classes filles doivent surcharger cette méthode
        pass
    
    def cleanup(self):
        """Nettoie les ressources de la scène"""
        # Méthode optionnelle pour libérer des ressources
        pass
    
    def switch_to_scene(self, scene_name):
        """Utilitaire pour changer de scène"""
        if self.scene_manager:
            self.scene_manager.set_active_scene(scene_name)
        else:
            print("❌ Aucun gestionnaire de scène disponible")
    
    def push_scene(self, scene_name):
        """Utilitaire pour empiler une scène"""
        if self.scene_manager:
            self.scene_manager.push_scene(scene_name)
        else:
            print("❌ Aucun gestionnaire de scène disponible")
    
    def pop_scene(self):
        """Utilitaire pour dépiler la scène courante"""
        if self.scene_manager:
            self.scene_manager.pop_scene()
        else:
            print("❌ Aucun gestionnaire de scène disponible")