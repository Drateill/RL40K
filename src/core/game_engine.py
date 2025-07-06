"""
Moteur principal du jeu - Remplace la boucle principale de main.py
Gère l'initialisation, la boucle de jeu et les scènes
"""
import pygame
import sys
from .constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from .scene_manager import SceneManager
from ..scenes.game_scene import GameScene

class GameEngine:
    """Moteur principal du jeu"""
    
    def __init__(self):
        # Initialisation de Pygame
        pygame.init()
        
        # Écran et horloge
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Roguelike Warhammer 40K")
        self.clock = pygame.time.Clock()
        
        # Gestionnaire de scènes
        self.scene_manager = SceneManager()
        
        # Variables de contrôle
        self.running = True
        
        # Initialiser la scène de jeu
        self.initialize_game_scene()
    
    def initialize_game_scene(self):
        """Initialise la scène principale de jeu"""
        game_scene = GameScene()
        self.scene_manager.add_scene("game", game_scene)
        self.scene_manager.set_active_scene("game")
    
    def handle_events(self):
        """Gère les événements globaux"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Passer l'événement à la scène active
            if self.scene_manager.active_scene:
                self.scene_manager.active_scene.handle_event(event)
    
    def update(self, dt):
        """Met à jour la logique du jeu"""
        if self.scene_manager.active_scene:
            self.scene_manager.active_scene.update(dt)
    
    def draw(self):
        """Dessine tout à l'écran"""
        self.screen.fill((0, 0, 0))  # Fond noir
        
        if self.scene_manager.active_scene:
            self.scene_manager.active_scene.draw(self.screen)
        
        pygame.display.flip()
    
    def run(self):
        """Boucle principale du jeu"""
        print("🚀 Démarrage du moteur de jeu Warhammer 40K...")
        
        while self.running:
            # Calculer le delta time
            dt = self.clock.tick(FPS) / 1000.0  # en secondes
            
            # Cycle principal
            self.handle_events()
            self.update(dt)
            self.draw()
        
        # Nettoyage
        self.cleanup()
    
    def cleanup(self):
        """Nettoie les ressources avant fermeture"""
        print("🔧 Nettoyage des ressources...")
        
        # Arrêter la musique
        pygame.mixer.stop()
        
        # Fermer pygame
        pygame.quit()
        
        print("✅ Jeu fermé proprement")
    
    def get_screen(self):
        """Retourne la surface d'écran"""
        return self.screen
    
    def get_clock(self):
        """Retourne l'horloge du jeu"""
        return self.clock
    
    def quit_game(self):
        """Méthode pour quitter le jeu proprement"""
        self.running = False