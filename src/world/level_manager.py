"""
Gestionnaire de niveau - Extrait de main.py
Contient LevelManager avec toute la logique de génération de niveaux
"""
import pygame
from .world_generator import SimpleWorldGenerator, WallWrapper
from ..core.constants import WORLD_WIDTH, WORLD_HEIGHT

class LevelManager:
    """Gestionnaire de niveau intégré"""
    
    def __init__(self):
        self.world_generator = SimpleWorldGenerator()
        self.current_walls = []
        self.current_spawn_positions = []
        self.current_environment = "neutral"
        
    def generate_level(self, wave_number, morality_system):
        """Génère un niveau pour la vague donnée"""
        
        # Déterminer l'environnement
        self.current_environment = self.world_generator.determine_environment(morality_system)
        
        # Créer le layout approprié
        if wave_number in [5, 15, 20]:  # Boss waves
            raw_walls = self.world_generator.create_boss_arena(WORLD_WIDTH, WORLD_HEIGHT)
            # Boss spawn au centre
            self.current_spawn_positions = [(WORLD_WIDTH // 2, WORLD_HEIGHT // 2)]
        else:
            raw_walls = self.world_generator.create_standard_layout(
                WORLD_WIDTH, WORLD_HEIGHT, self.current_environment
            )
            self.current_spawn_positions = self.world_generator.get_spawn_positions(
                self.current_environment, WORLD_WIDTH, WORLD_HEIGHT
            )
        
        # Convertir les pygame.Rect en objets avec attribut .rect pour compatibilité
        self.current_walls = []
        for wall_rect in raw_walls:
            wall_obj = WallWrapper(wall_rect)
            self.current_walls.append(wall_obj)
        
        return self.current_walls
    
    def get_environment_info(self):
        """Retourne les informations sur l'environnement actuel"""
        env_descriptions = {
            "imperial_shrine": "⛪ Sanctuaire Impérial - La foi vous guide",
            "chaos_temple": "🔥 Temple du Chaos - La corruption règne",
            "neutral_ruins": "🏚️ Ruines neutres - Terrain d'épreuve",
            "hive_city": "🏙️ Cité-ruche - Dédale urbain",
            "battlefield": "⚔️ Champ de bataille - Combat ouvert",
            "daemon_realm": "👹 Royaume démoniaque - Réalité distordue"
        }
        return env_descriptions.get(self.current_environment, "Environnement inconnu")
    
    def get_wall_color(self):
        """Retourne la couleur des murs selon l'environnement"""
        colors = {
            "imperial_shrine": (150, 140, 120),  # Doré
            "chaos_temple": (120, 80, 80),      # Rouge sombre
            "daemon_realm": (100, 60, 120),     # Pourpre
            "hive_city": (100, 100, 120),       # Bleu-gris
            "battlefield": (120, 100, 80),      # Terre
            "neutral_ruins": (128, 128, 128)    # Gris standard
        }
        return colors.get(self.current_environment, (128, 128, 128))