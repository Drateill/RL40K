"""
Générateur de monde - Extrait de main.py
Contient SimpleWorldGenerator et WallWrapper
"""
import pygame
import random
import math

# Import des constantes (sera adapté)
from ..core.constants import WORLD_WIDTH, WORLD_HEIGHT

class WallWrapper:
    """Wrapper pour les murs pour compatibilité avec PathfindingHelper"""
    def __init__(self, rect):
        self.rect = rect

class SimpleWorldGenerator:
    """Générateur de monde simplifié intégré directement dans main.py"""
    
    def __init__(self):
        self.current_environment = "neutral"
        self.current_layout = "standard"
        
    def determine_environment(self, morality_system):
        """Détermine l'environnement selon la moralité"""
        if not morality_system:
            return "neutral"
            
        faith = morality_system.faith
        corruption = morality_system.corruption
        
        if faith >= 80:
            return "imperial_shrine"
        elif faith >= 60:
            return "neutral_ruins"
        elif corruption >= 90:
            return "daemon_realm"
        elif corruption >= 70:
            return "chaos_temple"
        elif corruption >= 40:
            return "hive_city"
        else:
            return "battlefield"
    
    def create_boss_arena(self, world_width, world_height):
        """Crée une arène optimisée pour les boss"""
        walls = []
        
        # Murs de bordure
        wall_thickness = 30
        walls.extend([
            pygame.Rect(0, 0, world_width, wall_thickness),  # Haut
            pygame.Rect(0, world_height - wall_thickness, world_width, wall_thickness),  # Bas
            pygame.Rect(0, 0, wall_thickness, world_height),  # Gauche
            pygame.Rect(world_width - wall_thickness, 0, wall_thickness, world_height)  # Droite
        ])
        
        # Piliers stratégiques pour la couverture (optimisés bullet hell)
        arena_center_x = world_width // 2
        arena_center_y = world_height // 2
        
        # 4 piliers aux coins de l'arène centrale
        pillar_size = 60
        pillar_distance = 200
        
        pillar_positions = [
            (arena_center_x - pillar_distance, arena_center_y - pillar_distance),  # Top-left
            (arena_center_x + pillar_distance, arena_center_y - pillar_distance),  # Top-right
            (arena_center_x - pillar_distance, arena_center_y + pillar_distance),  # Bottom-left
            (arena_center_x + pillar_distance, arena_center_y + pillar_distance),  # Bottom-right
        ]
        
        for x, y in pillar_positions:
            walls.append(pygame.Rect(x - pillar_size//2, y - pillar_size//2, pillar_size, pillar_size))
        
        return walls
    
    def create_standard_layout(self, world_width, world_height, environment):
        """Crée un layout standard adapté à l'environnement"""
        walls = []
        
        # Murs de bordure
        wall_thickness = 30
        walls.extend([
            pygame.Rect(0, 0, world_width, wall_thickness),
            pygame.Rect(0, world_height - wall_thickness, world_width, wall_thickness),
            pygame.Rect(0, 0, wall_thickness, world_height),
            pygame.Rect(world_width - wall_thickness, 0, wall_thickness, world_height)
        ])
        
        # Obstacles selon l'environnement
        if environment == "imperial_shrine":
            walls.extend(self.create_gothic_pillars(world_width, world_height))
        elif environment == "chaos_temple":
            walls.extend(self.create_chaos_formation(world_width, world_height))
        elif environment == "battlefield":
            walls.extend(self.create_battlefield_cover(world_width, world_height))
        elif environment == "daemon_realm":
            walls.extend(self.create_warp_distortions(world_width, world_height))
        else:
            walls.extend(self.create_neutral_obstacles(world_width, world_height))
        
        return walls
    
    def create_gothic_pillars(self, world_width, world_height):
        """Crée des piliers gothiques symétriques"""
        pillars = []
        pillar_width = 40
        pillar_height = 120
        
        # Formation en croix gothique
        positions = [
            (world_width * 0.3, world_height * 0.3),
            (world_width * 0.7, world_height * 0.3),
            (world_width * 0.3, world_height * 0.7),
            (world_width * 0.7, world_height * 0.7),
            (world_width * 0.5, world_height * 0.2),
            (world_width * 0.5, world_height * 0.8),
            (world_width * 0.2, world_height * 0.5),
            (world_width * 0.8, world_height * 0.5),
        ]
        
        for x, y in positions:
            pillars.append(pygame.Rect(int(x - pillar_width//2), int(y - pillar_height//2), 
                                     pillar_width, pillar_height))
        
        return pillars
    
    def create_chaos_formation(self, world_width, world_height):
        """Crée une formation chaotique"""
        obstacles = []
        center_x = world_width // 2
        center_y = world_height // 2
        
        # Formation en étoile chaotique
        for i in range(8):
            angle = (i / 8) * 2 * math.pi + random.uniform(-0.3, 0.3)
            distance = random.uniform(150, 250)
            
            x = center_x + math.cos(angle) * distance
            y = center_y + math.sin(angle) * distance
            
            size = random.randint(40, 80)
            obstacles.append(pygame.Rect(int(x - size//2), int(y - size//2), size, size))
        
        return obstacles
    
    def create_battlefield_cover(self, world_width, world_height):
        """Crée des couvertures de champ de bataille"""
        covers = []
        
        # Barricades horizontales et verticales
        barricade_length = 120
        barricade_width = 25
        
        # Pattern de tranchées
        for i in range(3):
            # Barricades horizontales
            x = world_width * (0.2 + i * 0.3) - barricade_length // 2
            y = world_height * 0.4 - barricade_width // 2
            covers.append(pygame.Rect(int(x), int(y), barricade_length, barricade_width))
            
            y = world_height * 0.6 - barricade_width // 2
            covers.append(pygame.Rect(int(x), int(y), barricade_length, barricade_width))
        
        # Barricades verticales
        for i in range(2):
            x = world_width * 0.5 - barricade_width // 2
            y = world_height * (0.3 + i * 0.4) - barricade_length // 2
            covers.append(pygame.Rect(int(x), int(y), barricade_width, barricade_length))
        
        return covers
    
    def create_warp_distortions(self, world_width, world_height):
        """Crée des distorsions warp chaotiques"""
        distortions = []
        
        # Formations imprévisibles
        for _ in range(12):
            x = random.randint(100, world_width - 100)
            y = random.randint(100, world_height - 100)
            width = random.randint(30, 100)
            height = random.randint(30, 100)
            
            # Éviter le centre pour le mouvement
            center_x = world_width // 2
            center_y = world_height // 2
            if abs(x - center_x) < 200 and abs(y - center_y) < 200:
                continue
                
            distortions.append(pygame.Rect(x, y, width, height))
        
        return distortions
    
    def create_neutral_obstacles(self, world_width, world_height):
        """Crée des obstacles neutres standard"""
        obstacles = []
        
        # Pattern standard avec quelques piliers
        pillar_size = 60
        
        # 4 piliers aux quarts
        quarter_x = world_width // 4
        quarter_y = world_height // 4
        three_quarter_x = 3 * world_width // 4
        three_quarter_y = 3 * world_height // 4
        
        positions = [
            (quarter_x, quarter_y),
            (three_quarter_x, quarter_y),
            (quarter_x, three_quarter_y),
            (three_quarter_x, three_quarter_y),
        ]
        
        for x, y in positions:
            obstacles.append(pygame.Rect(x - pillar_size//2, y - pillar_size//2, 
                                       pillar_size, pillar_size))
        
        # Quelques murs longs
        wall_length = 200
        wall_width = 20
        
        obstacles.extend([
            pygame.Rect(world_width // 6, world_height // 3, wall_length, wall_width),
            pygame.Rect(2 * world_width // 3, 2 * world_height // 3, wall_length, wall_width),
            pygame.Rect(2 * world_width // 3, world_height // 6, wall_width, wall_length),
            pygame.Rect(world_width // 3, 2 * world_height // 3, wall_width, wall_length),
        ])
        
        return obstacles
    
    def get_spawn_positions(self, environment, world_width, world_height):
        """Retourne les positions de spawn selon l'environnement"""
        if environment == "imperial_shrine":
            # Spawn aux portes d'entrée
            return [
                (world_width // 2, 100),  # Entrée principale
                (100, world_height // 2),  # Entrée latérale gauche
                (world_width - 100, world_height // 2),  # Entrée latérale droite
                (world_width // 4, world_height - 100),  # Sortie gauche
                (3 * world_width // 4, world_height - 100),  # Sortie droite
            ]
        elif environment == "chaos_temple":
            # Spawn chaotique autour du centre
            center_x = world_width // 2
            center_y = world_height // 2
            spawn_positions = []
            
            for i in range(8):
                angle = (i / 8) * 2 * math.pi
                distance = 300
                x = center_x + math.cos(angle) * distance
                y = center_y + math.sin(angle) * distance
                spawn_positions.append((int(x), int(y)))
            
            return spawn_positions
        else:
            # Spawn standard optimisé
            return [
                (world_width // 6, world_height // 6),
                (5 * world_width // 6, world_height // 6),
                (world_width // 6, 5 * world_height // 6),
                (5 * world_width // 6, 5 * world_height // 6),
                (world_width // 2, 80),
                (world_width // 2, world_height - 80),
                (80, world_height // 2),
                (world_width - 80, world_height // 2),
            ]