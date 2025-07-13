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
        """Initialise avec le menu principal"""
        from ..scenes.main_menu_scene import MainMenuGameScene
        from ..scenes.archetype_scene import ArchetypeGameScene
        
        # Ajouter les scènes
        main_menu = MainMenuGameScene()
        archetype_selection = ArchetypeGameScene()
        
        self.scene_manager.add_scene("main_menu", main_menu)
        self.scene_manager.add_scene("archetype_selection", archetype_selection)
        self.scene_manager.set_active_scene("main_menu")
    
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
        self.scene_manager.update(dt)
        
        # Gérer les transitions de scènes
        self._handle_scene_transitions()
    
    def draw(self):
        """Dessine tout à l'écran"""
        self.screen.fill((0, 0, 0))  # Fond noir
        
        self.scene_manager.render(self.screen)
        
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
    
    def _handle_scene_transitions(self):
        """Gère les transitions entre scènes"""
        if not self.scene_manager.active_scene:
            return
        
        # Vérifier si la scène active veut changer
        if hasattr(self.scene_manager.active_scene, 'get_next_scene'):
            next_scene = self.scene_manager.active_scene.get_next_scene()
            
            if next_scene:
                print(f"🎬 GameEngine: Transition détectée vers '{next_scene}'")
            
            if next_scene == "quit":
                print("🚪 Fermeture du jeu")
                self.quit_game()
            elif next_scene == "archetype_selection":
                print("🎭 Transition vers la sélection d'archétype")
                self.scene_manager.set_active_scene("archetype_selection")
            elif next_scene == "main_menu":
                print("🏠 Retour au menu principal")
                self.scene_manager.set_active_scene("main_menu")
            elif next_scene == "game":
                print("🎮 Démarrage du jeu")
                self._start_game_with_archetype()
    
    def _start_game_with_archetype(self):
        """Démarre le jeu avec l'archétype sélectionné"""
        # Récupérer l'archétype sélectionné
        archetype_scene = self.scene_manager.scenes.get("archetype_selection")
        selected_archetype = None
        
        if archetype_scene:
            selected_archetype = archetype_scene.get_selected_archetype()
        
        # Créer la scène de jeu avec l'archétype
        from ..scenes.game_scene import GameScene
        game_scene = GameScene(selected_archetype=selected_archetype)
        
        # Remplacer ou ajouter la scène de jeu
        self.scene_manager.add_scene("game", game_scene)
        self.scene_manager.set_active_scene("game")
        
        print(f"🎮 Jeu démarré avec l'archétype: {selected_archetype}")