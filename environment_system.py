"""
Système d'environnements procéduraux pour le roguelike WH40K
Génère différents types de niveaux avec leurs thèmes et mécaniques uniques
"""

import pygame
import random
import math
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional

class EnvironmentType(Enum):
    """Types d'environnements disponibles"""
    SHIP = "ship"              # Vaisseau spatial - Couloirs, portes
    TEMPLE = "temple"          # Temple impérial - Grandes salles, colonnes  
    FORGE = "forge"            # Forge World - Machines, convoyeurs, dangers
    CHAOS = "chaos"            # Monde corrompu - Géométrie impossible
    DEATH_WORLD = "death"      # Monde de la mort - Pièges naturels

@dataclass
class EnvironmentConfig:
    """Configuration d'un type d'environnement"""
    name: str
    description: str
    wall_color: Tuple[int, int, int]
    floor_color: Tuple[int, int, int]
    accent_color: Tuple[int, int, int]
    
    # Probabilités de génération
    corridor_chance: float = 0.3
    room_chance: float = 0.4
    obstacle_chance: float = 0.2
    special_chance: float = 0.1
    
    # Dimensions préférées
    min_room_size: int = 80
    max_room_size: int = 200
    corridor_width: int = 40
    
    # Effets spéciaux
    has_ambient_effects: bool = False
    has_interactive_elements: bool = False
    movement_modifier: float = 1.0

class EnvironmentSystem:
    """Gestionnaire principal des environnements"""
    
    def __init__(self):
        self.current_environment = EnvironmentType.SHIP
        self.current_config = None
        self.generated_layout = None
        
        # Définir les configurations pour chaque environnement
        self.environment_configs = {
            EnvironmentType.SHIP: EnvironmentConfig(
                name="Vaisseau Spatial",
                description="Couloirs métalliques et salles techniques",
                wall_color=(80, 80, 100),      # Gris métallique
                floor_color=(40, 40, 50),      # Sol sombre
                accent_color=(0, 150, 200),    # Bleu tech
                corridor_chance=0.5,           # Beaucoup de couloirs
                room_chance=0.3,
                corridor_width=50,
                movement_modifier=1.0
            ),
            
            EnvironmentType.TEMPLE: EnvironmentConfig(
                name="Temple Impérial", 
                description="Architecture sacrée et voûtes gothiques",
                wall_color=(120, 100, 80),     # Pierre dorée
                floor_color=(60, 50, 40),      # Marbre sombre
                accent_color=(255, 215, 0),    # Or impérial
                corridor_chance=0.2,           # Moins de couloirs
                room_chance=0.6,               # Grandes salles
                min_room_size=120,
                max_room_size=300,
                movement_modifier=1.1          # Terrain sanctifié
            ),
            
            EnvironmentType.FORGE: EnvironmentConfig(
                name="Forge World",
                description="Complexe industriel et machineries", 
                wall_color=(100, 60, 40),      # Métal rouillé
                floor_color=(80, 40, 20),      # Sol industriel
                accent_color=(255, 100, 0),    # Orange forge
                corridor_chance=0.4,
                obstacle_chance=0.4,           # Beaucoup d'obstacles
                special_chance=0.2,            # Machines spéciales
                has_interactive_elements=True,
                movement_modifier=0.9          # Terrain difficile
            ),
            
            EnvironmentType.CHAOS: EnvironmentConfig(
                name="Monde Corrompu",
                description="Réalité distordue par le Chaos",
                wall_color=(100, 20, 100),     # Pourpre chaotique
                floor_color=(50, 10, 50),      # Sol corrompu
                accent_color=(255, 0, 255),    # Magenta chaos
                corridor_chance=0.3,
                room_chance=0.3,
                special_chance=0.4,            # Beaucoup d'éléments étranges
                has_ambient_effects=True,
                movement_modifier=0.8          # Corruption ralentit
            ),
            
            EnvironmentType.DEATH_WORLD: EnvironmentConfig(
                name="Monde de la Mort", 
                description="Environnement hostile et dangereux",
                wall_color=(60, 80, 40),       # Vert naturel
                floor_color=(40, 60, 20),      # Sol organique
                accent_color=(200, 0, 0),      # Rouge danger
                corridor_chance=0.1,           # Peu de couloirs
                room_chance=0.3,
                obstacle_chance=0.5,           # Très dangereux
                special_chance=0.3,
                has_ambient_effects=True,
                movement_modifier=0.7          # Terrain très difficile
            )
        }
    
    def select_environment_for_wave(self, wave_number: int, morality_system=None) -> EnvironmentType:
        """Sélectionne l'environnement selon la vague et la moralité"""
        
        # Progression basée sur les vagues
        if wave_number <= 3:
            # Début : Vaisseau spatial (tutoriel)
            return EnvironmentType.SHIP
        
        elif wave_number <= 8:
            # Milieu début : Temple ou Vaisseau
            return random.choice([EnvironmentType.SHIP, EnvironmentType.TEMPLE])
        
        elif wave_number <= 15:
            # Milieu : Tous sauf les plus dangereux
            base_envs = [EnvironmentType.SHIP, EnvironmentType.TEMPLE, EnvironmentType.FORGE]
            
            # Influence de la moralité
            if morality_system:
                if morality_system.corruption >= 50:
                    base_envs.append(EnvironmentType.CHAOS)
                if morality_system.faith >= 60:
                    # Les purs préfèrent les temples
                    base_envs.extend([EnvironmentType.TEMPLE] * 2)
            
            return random.choice(base_envs)
        
        else:
            # Fin de jeu : Tous les environnements possibles
            all_envs = list(EnvironmentType)
            
            # Influence forte de la moralité
            if morality_system:
                if morality_system.corruption >= 70:
                    # Les corrompus vont plus souvent en terrain chaos
                    return random.choice([EnvironmentType.CHAOS, EnvironmentType.DEATH_WORLD, EnvironmentType.FORGE])
                elif morality_system.faith >= 80:
                    # Les purs évitent les lieux corrompus
                    return random.choice([EnvironmentType.TEMPLE, EnvironmentType.SHIP])
            
            return random.choice(all_envs)
    
    def generate_environment(self, world_width: int, world_height: int, 
                           env_type: EnvironmentType = None) -> List:
        """Génère un nouvel environnement complet"""
        
        if env_type is None:
            env_type = self.current_environment
        else:
            self.current_environment = env_type
        
        self.current_config = self.environment_configs[env_type]
        
        print(f"🌍 Génération de l'environnement : {self.current_config.name}")
        print(f"   Description : {self.current_config.description}")
        
        # Générer le layout selon le type
        if env_type == EnvironmentType.SHIP:
            return self._generate_ship_layout(world_width, world_height)
        elif env_type == EnvironmentType.TEMPLE:
            return self._generate_temple_layout(world_width, world_height)
        elif env_type == EnvironmentType.FORGE:
            return self._generate_forge_layout(world_width, world_height)
        elif env_type == EnvironmentType.CHAOS:
            return self._generate_chaos_layout(world_width, world_height)
        elif env_type == EnvironmentType.DEATH_WORLD:
            return self._generate_death_world_layout(world_width, world_height)
        else:
            # Fallback vers un layout basique
            return self._generate_basic_layout(world_width, world_height)
    
    def _generate_ship_layout(self, width: int, height: int) -> List:
        """Génère un layout de vaisseau spatial avec couloirs et salles"""
        from wall import Wall
        walls = []
        
        # Bordures métalliques
        border_thickness = 40
        walls.extend(self._create_borders(width, height, border_thickness))
        
        # Réseau de couloirs principaux
        corridor_width = self.current_config.corridor_width
        
        # Couloir central horizontal
        center_y = height // 2
        walls.append(Wall(border_thickness, center_y - corridor_width//2, 
                         width - 2*border_thickness, 20))
        walls.append(Wall(border_thickness, center_y + corridor_width//2, 
                         width - 2*border_thickness, 20))
        
        # Couloir central vertical  
        center_x = width // 2
        walls.append(Wall(center_x - corridor_width//2, border_thickness,
                         20, height - 2*border_thickness))
        walls.append(Wall(center_x + corridor_width//2, border_thickness,
                         20, height - 2*border_thickness))
        
        # Salles techniques dans les coins
        room_size = 150
        margin = border_thickness + 60
        
        # Salle coin haut-gauche
        walls.extend(self._create_room_walls(margin, margin, room_size, room_size, 20))
        
        # Salle coin haut-droite
        walls.extend(self._create_room_walls(width - margin - room_size, margin, 
                                           room_size, room_size, 20))
        
        # Salle coin bas-gauche
        walls.extend(self._create_room_walls(margin, height - margin - room_size,
                                           room_size, room_size, 20))
        
        # Salle coin bas-droite
        walls.extend(self._create_room_walls(width - margin - room_size, 
                                           height - margin - room_size,
                                           room_size, room_size, 20))
        
        # Obstacles techniques aléatoires
        for _ in range(8):
            if random.random() < 0.7:
                obs_x = random.randint(border_thickness + 100, width - border_thickness - 100)
                obs_y = random.randint(border_thickness + 100, height - border_thickness - 100)
                obs_size = random.randint(30, 60)
                walls.append(Wall(obs_x, obs_y, obs_size, obs_size))
        
        return walls
    
    def _generate_temple_layout(self, width: int, height: int) -> List:
        """Génère un layout de temple avec grandes salles et colonnes"""
        from wall import Wall
        walls = []
        
        # Bordures en pierre
        border_thickness = 50
        walls.extend(self._create_borders(width, height, border_thickness))
        
        # Grande salle centrale
        center_room_width = 400
        center_room_height = 300
        center_x = (width - center_room_width) // 2
        center_y = (height - center_room_height) // 2
        
        # Murs de la salle centrale (avec ouvertures)
        wall_thickness = 30
        opening_size = 80
        
        # Mur du haut avec ouverture
        walls.append(Wall(center_x, center_y, 
                         (center_room_width - opening_size) // 2, wall_thickness))
        walls.append(Wall(center_x + (center_room_width + opening_size) // 2, center_y,
                         (center_room_width - opening_size) // 2, wall_thickness))
        
        # Mur du bas avec ouverture
        walls.append(Wall(center_x, center_y + center_room_height - wall_thickness,
                         (center_room_width - opening_size) // 2, wall_thickness))
        walls.append(Wall(center_x + (center_room_width + opening_size) // 2, 
                         center_y + center_room_height - wall_thickness,
                         (center_room_width - opening_size) // 2, wall_thickness))
        
        # Murs latéraux avec ouvertures
        walls.append(Wall(center_x, center_y,
                         wall_thickness, (center_room_height - opening_size) // 2))
        walls.append(Wall(center_x, center_y + (center_room_height + opening_size) // 2,
                         wall_thickness, (center_room_height - opening_size) // 2))
        
        walls.append(Wall(center_x + center_room_width - wall_thickness, center_y,
                         wall_thickness, (center_room_height - opening_size) // 2))
        walls.append(Wall(center_x + center_room_width - wall_thickness, 
                         center_y + (center_room_height + opening_size) // 2,
                         wall_thickness, (center_room_height - opening_size) // 2))
        
        # Colonnes dans la salle centrale
        column_size = 25
        col_spacing_x = center_room_width // 4
        col_spacing_y = center_room_height // 3
        
        for i in range(1, 4):  # 3 colonnes horizontalement
            for j in range(1, 3):  # 2 colonnes verticalement
                col_x = center_x + i * col_spacing_x - column_size // 2
                col_y = center_y + j * col_spacing_y - column_size // 2
                walls.append(Wall(col_x, col_y, column_size, column_size))
        
        # Chapelles latérales
        chapel_width = 120
        chapel_height = 100
        
        # Chapelle gauche
        chapel_x = border_thickness + 80
        chapel_y = center_y + (center_room_height - chapel_height) // 2
        walls.extend(self._create_room_walls(chapel_x, chapel_y, 
                                           chapel_width, chapel_height, 25))
        
        # Chapelle droite
        chapel_x = width - border_thickness - 80 - chapel_width
        walls.extend(self._create_room_walls(chapel_x, chapel_y,
                                           chapel_width, chapel_height, 25))
        
        return walls
    
    def _generate_forge_layout(self, width: int, height: int) -> List:
        """Génère un layout industriel avec machines et convoyeurs"""
        from wall import Wall
        walls = []
        
        # Bordures industrielles
        border_thickness = 45
        walls.extend(self._create_borders(width, height, border_thickness))
        
        # Zones de production (rectangles irréguliers)
        production_zones = [
            (border_thickness + 100, border_thickness + 80, 200, 150),
            (width - border_thickness - 300, border_thickness + 80, 200, 150),
            (border_thickness + 80, height - border_thickness - 200, 250, 120),
            (width - border_thickness - 330, height - border_thickness - 200, 250, 120)
        ]
        
        for zone_x, zone_y, zone_w, zone_h in production_zones:
            # Contour de la zone
            walls.extend(self._create_room_walls(zone_x, zone_y, zone_w, zone_h, 15))
            
            # Machines à l'intérieur
            machine_count = random.randint(2, 4)
            for _ in range(machine_count):
                machine_x = zone_x + random.randint(30, zone_w - 60)
                machine_y = zone_y + random.randint(30, zone_h - 60)
                machine_size = random.randint(20, 40)
                walls.append(Wall(machine_x, machine_y, machine_size, machine_size))
        
        # Convoyeurs (lignes de obstacles)
        conveyor_width = 40
        
        # Convoyeur horizontal central
        conv_y = height // 2 - conveyor_width // 2
        for i in range(5, 15):
            obstacle_x = border_thickness + i * 80
            if obstacle_x < width - border_thickness - 50:
                walls.append(Wall(obstacle_x, conv_y, 30, 15))
                walls.append(Wall(obstacle_x, conv_y + conveyor_width - 15, 30, 15))
        
        # Convoyeur vertical
        conv_x = width // 2 - conveyor_width // 2
        for i in range(3, 12):
            obstacle_y = border_thickness + i * 60
            if obstacle_y < height - border_thickness - 50:
                walls.append(Wall(conv_x, obstacle_y, 15, 25))
                walls.append(Wall(conv_x + conveyor_width - 15, obstacle_y, 15, 25))
        
        # Obstacles industriels aléatoires
        for _ in range(12):
            if random.random() < 0.8:
                obs_x = random.randint(border_thickness + 50, width - border_thickness - 100)
                obs_y = random.randint(border_thickness + 50, height - border_thickness - 100)
                
                # Formes variées d'obstacles
                if random.random() < 0.5:
                    # Obstacle carré
                    size = random.randint(25, 50)
                    walls.append(Wall(obs_x, obs_y, size, size))
                else:
                    # Obstacle rectangulaire
                    w = random.randint(30, 80)
                    h = random.randint(20, 40)
                    walls.append(Wall(obs_x, obs_y, w, h))
        
        return walls
    
    def _generate_chaos_layout(self, width: int, height: int) -> List:
        """Génère un layout chaotique avec géométrie impossible"""
        from wall import Wall
        walls = []
        
        # Bordures corrompues (irrégulières)
        border_thickness = random.randint(35, 55)
        walls.extend(self._create_borders(width, height, border_thickness))
        
        # Centre : zone de corruption majeure
        center_x, center_y = width // 2, height // 2
        corruption_radius = 100
        
        # Cercle corrompu central (approximé par des rectangles)
        circle_segments = 16
        for i in range(circle_segments):
            angle = (i / circle_segments) * 2 * math.pi
            segment_x = center_x + math.cos(angle) * corruption_radius - 15
            segment_y = center_y + math.sin(angle) * corruption_radius - 15
            walls.append(Wall(int(segment_x), int(segment_y), 30, 30))
        
        # Formes géométriques impossibles
        # Spirale chaotique
        spiral_segments = 20
        for i in range(spiral_segments):
            t = i / spiral_segments
            spiral_radius = 50 + t * 100
            angle = t * 6 * math.pi  # 3 tours complets
            
            spiral_x = center_x + math.cos(angle) * spiral_radius
            spiral_y = center_y + math.sin(angle) * spiral_radius
            
            # Vérifier les limites
            if (border_thickness + 40 < spiral_x < width - border_thickness - 40 and
                border_thickness + 40 < spiral_y < height - border_thickness - 40):
                walls.append(Wall(int(spiral_x - 20), int(spiral_y - 20), 40, 40))
        
        # Portails chaotiques (zones vides entourées de murs)
        portal_count = random.randint(3, 6)
        for _ in range(portal_count):
            portal_x = random.randint(border_thickness + 100, width - border_thickness - 200)
            portal_y = random.randint(border_thickness + 100, height - border_thickness - 200)
            portal_size = random.randint(60, 100)
            
            # Contour du portail
            walls.extend(self._create_room_walls(portal_x, portal_y, 
                                               portal_size, portal_size, 20))
        
        # Fragments chaotiques aléatoires
        for _ in range(25):
            if random.random() < 0.7:
                frag_x = random.randint(border_thickness + 30, width - border_thickness - 80)
                frag_y = random.randint(border_thickness + 30, height - border_thickness - 80)
                
                # Formes chaotiques variées
                chaos_type = random.randint(1, 4)
                if chaos_type == 1:
                    # Triangle approximé
                    walls.append(Wall(frag_x, frag_y, 30, 15))
                    walls.append(Wall(frag_x + 10, frag_y + 15, 10, 20))
                elif chaos_type == 2:
                    # Croix chaotique
                    walls.append(Wall(frag_x, frag_y + 10, 40, 15))
                    walls.append(Wall(frag_x + 12, frag_y, 15, 40))
                elif chaos_type == 3:
                    # Forme en L
                    walls.append(Wall(frag_x, frag_y, 50, 20))
                    walls.append(Wall(frag_x, frag_y, 20, 50))
                else:
                    # Rectangle déformé
                    w = random.randint(25, 60)
                    h = random.randint(15, 45)
                    walls.append(Wall(frag_x, frag_y, w, h))
        
        return walls
    
    def _generate_death_world_layout(self, width: int, height: int) -> List:
        """Génère un layout de monde de la mort avec pièges naturels"""
        from wall import Wall
        walls = []
        
        # Bordures naturelles irrégulières
        border_thickness = random.randint(40, 60)
        walls.extend(self._create_borders(width, height, border_thickness))
        
        # Crevasses et ravins (lignes d'obstacles)
        ravine_count = random.randint(2, 4)
        for _ in range(ravine_count):
            if random.random() < 0.5:
                # Ravin horizontal
                ravine_y = random.randint(border_thickness + 100, height - border_thickness - 200)
                ravine_length = random.randint(300, 600)
                ravine_x = random.randint(border_thickness + 50, width - ravine_length - 50)
                
                # Bords du ravin
                for i in range(0, ravine_length, 40):
                    walls.append(Wall(ravine_x + i, ravine_y, 35, 15))
                    walls.append(Wall(ravine_x + i, ravine_y + 60, 35, 15))
            else:
                # Ravin vertical
                ravine_x = random.randint(border_thickness + 100, width - border_thickness - 200)
                ravine_length = random.randint(250, 500)
                ravine_y = random.randint(border_thickness + 50, height - ravine_length - 50)
                
                for i in range(0, ravine_length, 35):
                    walls.append(Wall(ravine_x, ravine_y + i, 15, 30))
                    walls.append(Wall(ravine_x + 60, ravine_y + i, 15, 30))
        
        # Formations rocheuses naturelles
        rock_formation_count = random.randint(4, 8)
        for _ in range(rock_formation_count):
            form_center_x = random.randint(border_thickness + 80, width - border_thickness - 160)
            form_center_y = random.randint(border_thickness + 80, height - border_thickness - 160)
            formation_size = random.randint(60, 120)
            
            # Création d'une formation organique
            rock_count = random.randint(5, 12)
            for i in range(rock_count):
                angle = (i / rock_count) * 2 * math.pi
                distance = random.randint(20, formation_size // 2)
                
                rock_x = form_center_x + math.cos(angle) * distance
                rock_y = form_center_y + math.sin(angle) * distance
                rock_size = random.randint(25, 50)
                
                walls.append(Wall(int(rock_x), int(rock_y), rock_size, rock_size))
        
        # Végétation dense (obstacles organiques)
        vegetation_zones = random.randint(2, 5)
        for _ in range(vegetation_zones):
            zone_x = random.randint(border_thickness + 50, width - border_thickness - 200)
            zone_y = random.randint(border_thickness + 50, height - border_thickness - 200)
            zone_size = random.randint(80, 150)
            
            # Plantes dans la zone
            plant_count = random.randint(8, 15)
            for _ in range(plant_count):
                plant_x = zone_x + random.randint(0, zone_size)
                plant_y = zone_y + random.randint(0, zone_size)
                plant_size = random.randint(15, 35)
                
                # Vérifier qu'on ne sort pas du monde
                if (plant_x + plant_size < width - border_thickness and
                    plant_y + plant_size < height - border_thickness):
                    walls.append(Wall(plant_x, plant_y, plant_size, plant_size))
        
        # Pièges dispersés (petits obstacles)
        trap_count = random.randint(15, 25)
        for _ in range(trap_count):
            trap_x = random.randint(border_thickness + 30, width - border_thickness - 50)
            trap_y = random.randint(border_thickness + 30, height - border_thickness - 50)
            trap_size = random.randint(10, 25)
            walls.append(Wall(trap_x, trap_y, trap_size, trap_size))
        
        return walls
    
    def _generate_basic_layout(self, width: int, height: int) -> List:
        """Layout de base en cas de fallback"""
        from wall import Wall
        walls = []
        walls.extend(self._create_borders(width, height, 30))
        
        # Quelques obstacles simples
        for _ in range(8):
            x = random.randint(100, width - 200)
            y = random.randint(100, height - 200)
            size = random.randint(40, 80)
            walls.append(Wall(x, y, size, size))
        
        return walls
    
    def _create_borders(self, width: int, height: int, thickness: int) -> List:
        """Crée les murs de bordure"""
        from wall import Wall
        return [
            Wall(0, 0, width, thickness),                    # Haut
            Wall(0, height - thickness, width, thickness),   # Bas
            Wall(0, 0, thickness, height),                   # Gauche
            Wall(width - thickness, 0, thickness, height)    # Droite
        ]
    
    def _create_room_walls(self, x: int, y: int, width: int, height: int, 
                          wall_thickness: int, opening_size: int = 60) -> List:
        """Crée les murs d'une salle avec une ouverture"""
        from wall import Wall
        walls = []
        
        # Mur du haut avec ouverture
        left_width = (width - opening_size) // 2
        right_width = width - opening_size - left_width
        
        if left_width > 0:
            walls.append(Wall(x, y, left_width, wall_thickness))
        if right_width > 0:
            walls.append(Wall(x + left_width + opening_size, y, right_width, wall_thickness))
        
        # Murs latéraux complets
        walls.append(Wall(x, y, wall_thickness, height))
        walls.append(Wall(x + width - wall_thickness, y, wall_thickness, height))
        
        # Mur du bas complet
        walls.append(Wall(x, y + height - wall_thickness, width, wall_thickness))
        
        return walls
    
    def get_environment_info(self) -> dict:
        """Retourne les informations sur l'environnement actuel"""
        if self.current_config is None:
            return {"name": "Aucun", "description": "Pas d'environnement chargé"}
        
        return {
            "name": self.current_config.name,
            "description": self.current_config.description,
            "type": self.current_environment.value,
            "movement_modifier": self.current_config.movement_modifier,
            "has_ambient_effects": self.current_config.has_ambient_effects,
            "has_interactive_elements": self.current_config.has_interactive_elements
        }
    
    def get_wall_color(self) -> Tuple[int, int, int]:
        """Retourne la couleur des murs pour l'environnement actuel"""
        if self.current_config:
            return self.current_config.wall_color
        return (128, 128, 128)  # Gris par défaut
    
    def get_floor_color(self) -> Tuple[int, int, int]:
        """Retourne la couleur du sol pour l'environnement actuel"""
        if self.current_config:
            return self.current_config.floor_color
        return (64, 64, 64)  # Gris foncé par défaut
    
    def get_movement_modifier(self) -> float:
        """Retourne le modificateur de mouvement pour l'environnement"""
        if self.current_config:
            return self.current_config.movement_modifier
        return 1.0
    
    def should_spawn_special_effects(self) -> bool:
        """Détermine si des effets spéciaux ambiants doivent apparaître"""
        if self.current_config:
            return (self.current_config.has_ambient_effects and 
                    random.random() < 0.1)  # 10% de chance par frame
        return False