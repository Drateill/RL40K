import random
import math
import pygame
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional

class EnvironmentType(Enum):
    """Types d'environnements selon la thématique WH40K"""
    IMPERIAL_SHRINE = "imperial_shrine"        # Sanctuaire impérial (Foi élevée)
    CHAOS_TEMPLE = "chaos_temple"              # Temple du Chaos (Corruption élevée)
    NEUTRAL_RUINS = "neutral_ruins"            # Ruines neutres
    HIVE_CITY = "hive_city"                    # Cité-ruche (urbain dense)
    SPACE_HULK = "space_hulk"                  # Épave spatiale (corridors étroits)
    BATTLEFIELD = "battlefield"                # Champ de bataille (espaces ouverts)
    DAEMON_REALM = "daemon_realm"              # Royaume démoniaque (chaos pur)

class RoomType(Enum):
    """Types de salles pour la génération"""
    ARENA = "arena"                # Grande salle ouverte (boss fights)
    CORRIDOR = "corridor"          # Couloir de connexion
    CHAMBER = "chamber"            # Salle moyenne avec obstacles
    CHOKEPOINT = "chokepoint"      # Point d'étranglement tactique
    SANCTUARY = "sanctuary"        # Zone de repos/items
    MAZE = "maze"                  # Labyrinthe dense

@dataclass
class Room:
    """Représente une salle du niveau"""
    x: int
    y: int
    width: int
    height: int
    room_type: RoomType
    environment: EnvironmentType
    connections: List[Tuple[int, int]] = None
    obstacles: List[pygame.Rect] = None
    spawn_points: List[Tuple[int, int]] = None
    special_features: List[str] = None

    def __post_init__(self):
        if self.connections is None:
            self.connections = []
        if self.obstacles is None:
            self.obstacles = []
        if self.spawn_points is None:
            self.spawn_points = []
        if self.special_features is None:
            self.special_features = []

class WorldGenerator:
    """Générateur de monde procédural pour RL40K"""
    
    def __init__(self, world_width: int = 3072, world_height: int = 2304):
        # Monde plus grand pour plus d'espace bullet hell
        self.world_width = world_width
        self.world_height = world_height
        self.grid_size = 64  # Taille de la grille pour le placement
        self.rooms: List[Room] = []
        self.walls: List[pygame.Rect] = []
        self.environment_type = EnvironmentType.NEUTRAL_RUINS
        
        # Paramètres de génération
        self.min_room_size = 200
        self.max_room_size = 600
        self.corridor_width = 80
        self.obstacle_density = 0.3  # Densité d'obstacles (30%)
        
    def generate_world(self, wave_number: int, morality_system=None) -> Tuple[List[pygame.Rect], List[Room]]:
        """Génère un niveau complet selon la vague et la moralité"""
        
        # 1. Déterminer l'environnement selon la moralité
        self.determine_environment(morality_system)
        
        # 2. Générer le layout selon la vague
        self.generate_layout(wave_number)
        
        # 3. Créer les salles principales
        self.create_rooms(wave_number)
        
        # 4. Connecter les salles
        self.connect_rooms()
        
        # 5. Placer les obstacles
        self.place_obstacles()
        
        # 6. Ajouter des éléments spéciaux
        self.add_special_features(wave_number, morality_system)
        
        # 7. Optimiser pour le bullet hell
        self.optimize_for_bullet_hell()
        
        # 8. Créer les murs finaux
        self.create_walls()
        
        return self.walls, self.rooms
    
    def determine_environment(self, morality_system):
        """Détermine l'environnement selon l'état moral du joueur"""
        if not morality_system:
            self.environment_type = EnvironmentType.NEUTRAL_RUINS
            return
            
        faith = morality_system.faith
        corruption = morality_system.corruption
        
        if faith >= 80:
            self.environment_type = EnvironmentType.IMPERIAL_SHRINE
        elif faith >= 60:
            self.environment_type = EnvironmentType.NEUTRAL_RUINS
        elif corruption >= 90:
            self.environment_type = EnvironmentType.DAEMON_REALM
        elif corruption >= 70:
            self.environment_type = EnvironmentType.CHAOS_TEMPLE
        elif corruption >= 40:
            self.environment_type = EnvironmentType.HIVE_CITY
        else:
            self.environment_type = EnvironmentType.BATTLEFIELD
    
    def generate_layout(self, wave_number: int):
        """Génère le layout général selon la vague"""
        
        # Layout différent selon la vague
        if wave_number % 5 == 0:  # Boss waves
            self.create_boss_layout(wave_number)
        elif wave_number < 5:
            self.create_intro_layout()
        elif wave_number < 10:
            self.create_standard_layout()
        elif wave_number < 15:
            self.create_complex_layout()
        else:
            self.create_endgame_layout()
    
    def create_boss_layout(self, wave_number: int):
        """Crée un layout optimisé pour les combats de boss"""
        
        # Grande arène centrale pour le boss
        arena_size = min(800, 400 + wave_number * 20)
        arena_x = (self.world_width - arena_size) // 2
        arena_y = (self.world_height - arena_size) // 2
        
        boss_arena = Room(
            arena_x, arena_y, arena_size, arena_size,
            RoomType.ARENA, self.environment_type
        )
        boss_arena.special_features.append("boss_arena")
        self.rooms.append(boss_arena)
        
        # Chambres d'approche aux 4 coins
        approach_size = 150
        margin = 100
        
        approaches = [
            (margin, margin),  # Top-left
            (self.world_width - margin - approach_size, margin),  # Top-right
            (margin, self.world_height - margin - approach_size),  # Bottom-left
            (self.world_width - margin - approach_size, self.world_height - margin - approach_size)  # Bottom-right
        ]
        
        for i, (x, y) in enumerate(approaches):
            approach_room = Room(
                x, y, approach_size, approach_size,
                RoomType.CHAMBER, self.environment_type
            )
            approach_room.special_features.append(f"approach_{i}")
            self.rooms.append(approach_room)
    
    def create_standard_layout(self):
        """Layout standard avec salles connectées"""
        
        # Grille 3x3 de salles
        grid_width = 3
        grid_height = 3
        
        room_width = (self.world_width - 200) // grid_width
        room_height = (self.world_height - 200) // grid_height
        
        for grid_x in range(grid_width):
            for grid_y in range(grid_height):
                x = 100 + grid_x * room_width
                y = 100 + grid_y * room_height
                
                # Variation de taille pour plus de diversité
                w = room_width + random.randint(-50, 50)
                h = room_height + random.randint(-50, 50)
                
                # Type de salle selon la position
                if grid_x == 1 and grid_y == 1:  # Centre
                    room_type = RoomType.ARENA
                elif grid_x == 0 or grid_x == 2 or grid_y == 0 or grid_y == 2:  # Bords
                    room_type = random.choice([RoomType.CHAMBER, RoomType.CHOKEPOINT])
                else:
                    room_type = RoomType.CORRIDOR
                
                room = Room(x, y, w, h, room_type, self.environment_type)
                self.rooms.append(room)
    
    def create_complex_layout(self):
        """Layout complexe avec plus de variations"""
        
        # Hub central avec rayons
        hub_size = 300
        hub_x = (self.world_width - hub_size) // 2
        hub_y = (self.world_height - hub_size) // 2
        
        hub = Room(hub_x, hub_y, hub_size, hub_size, RoomType.ARENA, self.environment_type)
        hub.special_features.append("central_hub")
        self.rooms.append(hub)
        
        # Salles satellites autour du hub
        satellite_count = 6
        satellite_distance = 400
        
        for i in range(satellite_count):
            angle = (i / satellite_count) * 2 * math.pi
            sat_x = hub_x + hub_size//2 + math.cos(angle) * satellite_distance - 100
            sat_y = hub_y + hub_size//2 + math.sin(angle) * satellite_distance - 100
            
            # Garder dans les limites
            sat_x = max(50, min(self.world_width - 250, sat_x))
            sat_y = max(50, min(self.world_height - 250, sat_y))
            
            satellite = Room(
                int(sat_x), int(sat_y), 200, 200,
                random.choice([RoomType.CHAMBER, RoomType.MAZE, RoomType.SANCTUARY]),
                self.environment_type
            )
            satellite.special_features.append(f"satellite_{i}")
            self.rooms.append(satellite)
    
    def connect_rooms(self):
        """Crée des connexions entre les salles"""
        
        if len(self.rooms) < 2:
            return
        
        # Connecter chaque salle à sa plus proche voisine
        for i, room in enumerate(self.rooms):
            if not room.connections:  # Si pas encore connectée
                closest_room = self.find_closest_room(room, exclude_index=i)
                if closest_room:
                    self.create_corridor_between_rooms(room, closest_room)
        
        # Ajouter quelques connexions supplémentaires pour éviter les dead ends
        for _ in range(min(3, len(self.rooms) // 2)):
            room1 = random.choice(self.rooms)
            room2 = random.choice([r for r in self.rooms if r != room1])
            
            if not self.rooms_connected(room1, room2):
                self.create_corridor_between_rooms(room1, room2, width=60)
    
    def find_closest_room(self, target_room: Room, exclude_index: int) -> Optional[Room]:
        """Trouve la salle la plus proche"""
        min_distance = float('inf')
        closest = None
        
        target_center = (target_room.x + target_room.width//2, target_room.y + target_room.height//2)
        
        for i, room in enumerate(self.rooms):
            if i == exclude_index:
                continue
                
            room_center = (room.x + room.width//2, room.y + room.height//2)
            distance = math.sqrt((target_center[0] - room_center[0])**2 + 
                               (target_center[1] - room_center[1])**2)
            
            if distance < min_distance:
                min_distance = distance
                closest = room
        
        return closest
    
    def create_corridor_between_rooms(self, room1: Room, room2: Room, width: int = None):
        """Crée un couloir entre deux salles"""
        if width is None:
            width = self.corridor_width
        
        # Points de connexion
        center1 = (room1.x + room1.width//2, room1.y + room1.height//2)
        center2 = (room2.x + room2.width//2, room2.y + room2.height//2)
        
        # Enregistrer la connexion
        room1.connections.append(center2)
        room2.connections.append(center1)
        
        # Créer le couloir en L
        if random.choice([True, False]):
            # Horizontal puis vertical
            corridor1 = Room(
                min(center1[0], center2[0]) - width//2,
                center1[1] - width//2,
                abs(center2[0] - center1[0]) + width,
                width,
                RoomType.CORRIDOR,
                self.environment_type
            )
            corridor2 = Room(
                center2[0] - width//2,
                min(center1[1], center2[1]) - width//2,
                width,
                abs(center2[1] - center1[1]) + width,
                RoomType.CORRIDOR,
                self.environment_type
            )
        else:
            # Vertical puis horizontal
            corridor1 = Room(
                center1[0] - width//2,
                min(center1[1], center2[1]) - width//2,
                width,
                abs(center2[1] - center1[1]) + width,
                RoomType.CORRIDOR,
                self.environment_type
            )
            corridor2 = Room(
                min(center1[0], center2[0]) - width//2,
                center2[1] - width//2,
                abs(center2[0] - center1[0]) + width,
                width,
                RoomType.CORRIDOR,
                self.environment_type
            )
        
        self.rooms.extend([corridor1, corridor2])
    
    def place_obstacles(self):
        """Place des obstacles dans les salles selon leur type"""
        
        for room in self.rooms:
            if room.room_type == RoomType.CORRIDOR:
                continue  # Pas d'obstacles dans les couloirs
            
            obstacle_count = self.calculate_obstacle_count(room)
            
            for _ in range(obstacle_count):
                obstacle = self.create_obstacle_for_room(room)
                if obstacle and self.is_obstacle_valid(obstacle, room):
                    room.obstacles.append(obstacle)
    
    def calculate_obstacle_count(self, room: Room) -> int:
        """Calcule le nombre d'obstacles selon le type de salle"""
        area = room.width * room.height
        base_count = int(area * self.obstacle_density / 10000)  # Normalisation
        
        type_multipliers = {
            RoomType.ARENA: 0.3,      # Peu d'obstacles pour le mouvement
            RoomType.CHAMBER: 1.0,    # Nombre normal
            RoomType.MAZE: 2.0,       # Beaucoup d'obstacles
            RoomType.CHOKEPOINT: 1.5, # Obstacles tactiques
            RoomType.SANCTUARY: 0.5,  # Minimal pour le repos
            RoomType.CORRIDOR: 0.0    # Pas d'obstacles
        }
        
        multiplier = type_multipliers.get(room.room_type, 1.0)
        return max(0, int(base_count * multiplier))
    
    def create_obstacle_for_room(self, room: Room) -> Optional[pygame.Rect]:
        """Crée un obstacle adapté à l'environnement"""
        
        # Taille d'obstacle selon l'environnement
        size_ranges = {
            EnvironmentType.IMPERIAL_SHRINE: (40, 120),    # Piliers gothiques
            EnvironmentType.CHAOS_TEMPLE: (30, 100),       # Autels chaotiques
            EnvironmentType.NEUTRAL_RUINS: (20, 80),       # Débris variés
            EnvironmentType.HIVE_CITY: (25, 90),           # Structures urbaines
            EnvironmentType.SPACE_HULK: (35, 70),          # Épaves métalliques
            EnvironmentType.BATTLEFIELD: (15, 60),         # Cratères, barricades
            EnvironmentType.DAEMON_REALM: (50, 150),       # Formations chaotiques
        }
        
        min_size, max_size = size_ranges.get(self.environment_type, (20, 80))
        
        width = random.randint(min_size, max_size)
        height = random.randint(min_size, max_size)
        
        # Position aléatoire dans la salle (avec marges)
        margin = 30
        max_x = room.x + room.width - width - margin
        max_y = room.y + room.height - height - margin
        
        if max_x <= room.x + margin or max_y <= room.y + margin:
            return None  # Salle trop petite
        
        x = random.randint(room.x + margin, max_x)
        y = random.randint(room.y + margin, max_y)
        
        return pygame.Rect(x, y, width, height)
    
    def optimize_for_bullet_hell(self):
        """Optimise le niveau pour le gameplay bullet hell"""
        
        for room in self.rooms:
            if room.room_type == RoomType.ARENA:
                self.ensure_movement_space(room)
                self.create_cover_patterns(room)
            elif room.room_type == RoomType.CHAMBER:
                self.create_tactical_positions(room)
        
        # S'assurer qu'il y a des chemins libres pour l'esquive
        self.create_escape_routes()
    
    def ensure_movement_space(self, room: Room):
        """S'assure qu'il y a assez d'espace libre pour le mouvement"""
        
        # Zone centrale libre pour le combat
        center_x = room.x + room.width // 4
        center_y = room.y + room.height // 4
        center_width = room.width // 2
        center_height = room.height // 2
        
        center_zone = pygame.Rect(center_x, center_y, center_width, center_height)
        
        # Supprimer les obstacles qui intersectent la zone centrale
        room.obstacles = [obs for obs in room.obstacles if not obs.colliderect(center_zone)]
        
        # Ajouter des spawn points sur le périmètre
        perimeter_points = [
            (room.x + 50, room.y + room.height // 2),  # Gauche
            (room.x + room.width - 50, room.y + room.height // 2),  # Droite
            (room.x + room.width // 2, room.y + 50),  # Haut
            (room.x + room.width // 2, room.y + room.height - 50),  # Bas
        ]
        
        room.spawn_points.extend(perimeter_points)
    
    def create_cover_patterns(self, room: Room):
        """Crée des patterns de couverture pour le gameplay tactique"""
        
        if self.environment_type == EnvironmentType.IMPERIAL_SHRINE:
            # Piliers en croix gothique
            self.create_gothic_pillars(room)
        elif self.environment_type == EnvironmentType.CHAOS_TEMPLE:
            # Formation chaotique
            self.create_chaos_formation(room)
        elif self.environment_type == EnvironmentType.BATTLEFIELD:
            # Tranchées et barricades
            self.create_battlefield_cover(room)
    
    def create_gothic_pillars(self, room: Room):
        """Crée des piliers gothiques symétriques"""
        pillar_width = 40
        pillar_height = 120
        
        # 4 piliers aux positions stratégiques
        positions = [
            (room.x + room.width * 0.3 - pillar_width//2, room.y + room.height * 0.3 - pillar_height//2),
            (room.x + room.width * 0.7 - pillar_width//2, room.y + room.height * 0.3 - pillar_height//2),
            (room.x + room.width * 0.3 - pillar_width//2, room.y + room.height * 0.7 - pillar_height//2),
            (room.x + room.width * 0.7 - pillar_width//2, room.y + room.height * 0.7 - pillar_height//2),
        ]
        
        for x, y in positions:
            pillar = pygame.Rect(int(x), int(y), pillar_width, pillar_height)
            room.obstacles.append(pillar)
    
    def create_chaos_formation(self, room: Room):
        """Crée une formation chaotique d'obstacles"""
        center_x = room.x + room.width // 2
        center_y = room.y + room.height // 2
        
        # Formation en étoile chaotique
        for i in range(8):
            angle = (i / 8) * 2 * math.pi + random.uniform(-0.3, 0.3)
            distance = random.uniform(80, 150)
            
            x = center_x + math.cos(angle) * distance - 25
            y = center_y + math.sin(angle) * distance - 25
            
            size = random.randint(30, 70)
            chaos_obstacle = pygame.Rect(int(x), int(y), size, size)
            room.obstacles.append(chaos_obstacle)
    
    def create_battlefield_cover(self, room: Room):
        """Crée des couvertures de champ de bataille"""
        
        # Barricades horizontales et verticales
        barricade_length = 100
        barricade_width = 20
        
        # Barricades horizontales
        for i in range(2):
            x = room.x + room.width * (0.25 + i * 0.5) - barricade_length // 2
            y = room.y + room.height * 0.4 - barricade_width // 2
            
            barricade = pygame.Rect(int(x), int(y), barricade_length, barricade_width)
            room.obstacles.append(barricade)
        
        # Barricades verticales
        for i in range(2):
            x = room.x + room.width * 0.5 - barricade_width // 2
            y = room.y + room.height * (0.25 + i * 0.5) - barricade_length // 2
            
            barricade = pygame.Rect(int(x), int(y), barricade_width, barricade_length)
            room.obstacles.append(barricade)
    
    def create_walls(self):
        """Crée les murs finaux à partir des salles"""
        
        # Murs de bordure du monde
        wall_thickness = 30
        self.walls.extend([
            pygame.Rect(0, 0, self.world_width, wall_thickness),  # Haut
            pygame.Rect(0, self.world_height - wall_thickness, self.world_width, wall_thickness),  # Bas
            pygame.Rect(0, 0, wall_thickness, self.world_height),  # Gauche
            pygame.Rect(self.world_width - wall_thickness, 0, wall_thickness, self.world_height)  # Droite
        ])
        
        # Murs des obstacles dans chaque salle
        for room in self.rooms:
            self.walls.extend(room.obstacles)
        
        # Murs de séparation entre salles (zones non-room)
        self.fill_empty_spaces()
    
    def fill_empty_spaces(self):
        """Remplit les espaces vides entre les salles avec des murs"""
        
        # Créer une grille pour marquer les zones occupées
        grid_resolution = 32
        grid_width = self.world_width // grid_resolution
        grid_height = self.world_height // grid_resolution
        
        occupied = [[False for _ in range(grid_height)] for _ in range(grid_width)]
        
        # Marquer les zones occupées par les salles
        for room in self.rooms:
            start_x = max(0, room.x // grid_resolution)
            end_x = min(grid_width, (room.x + room.width) // grid_resolution + 1)
            start_y = max(0, room.y // grid_resolution)
            end_y = min(grid_height, (room.y + room.height) // grid_resolution + 1)
            
            for x in range(start_x, end_x):
                for y in range(start_y, end_y):
                    occupied[x][y] = True
        
        # Créer des murs dans les zones non-occupées
        for x in range(grid_width):
            for y in range(grid_height):
                if not occupied[x][y]:
                    wall_x = x * grid_resolution
                    wall_y = y * grid_resolution
                    wall = pygame.Rect(wall_x, wall_y, grid_resolution, grid_resolution)
                    self.walls.append(wall)
    
    def get_spawn_positions(self, room_type: RoomType = None) -> List[Tuple[int, int]]:
        """Retourne les positions de spawn appropriées"""
        spawn_positions = []
        
        for room in self.rooms:
            if room_type and room.room_type != room_type:
                continue
                
            if room.spawn_points:
                spawn_positions.extend(room.spawn_points)
            else:
                # Position par défaut au centre de la salle
                center_x = room.x + room.width // 2
                center_y = room.y + room.height // 2
                spawn_positions.append((center_x, center_y))
        
        return spawn_positions
    
    def get_boss_arena(self) -> Optional[Room]:
        """Retourne l'arène de boss si elle existe"""
        for room in self.rooms:
            if "boss_arena" in room.special_features:
                return room
        
        # Si pas d'arène spécifique, retourner la plus grande salle
        if self.rooms:
            return max(self.rooms, key=lambda r: r.width * r.height)
        
        return None
    
    def rooms_connected(self, room1: Room, room2: Room) -> bool:
        """Vérifie si deux salles sont déjà connectées"""
        room1_center = (room1.x + room1.width//2, room1.y + room1.height//2)
        room2_center = (room2.x + room2.width//2, room2.y + room2.height//2)
        
        return room2_center in room1.connections or room1_center in room2.connections
    
    def is_obstacle_valid(self, obstacle: pygame.Rect, room: Room) -> bool:
        """Vérifie si un obstacle est valide (pas de collision avec existants)"""
        
        # Vérifier collision avec autres obstacles
        for existing in room.obstacles:
            if obstacle.colliderect(existing):
                return False
        
        # Vérifier que l'obstacle n'est pas trop près des bords
        margin = 20
        if (obstacle.x < room.x + margin or 
            obstacle.y < room.y + margin or
            obstacle.x + obstacle.width > room.x + room.width - margin or
            obstacle.y + obstacle.height > room.y + room.height - margin):
            return False
        
        return True
    
    def create_escape_routes(self):
        """Crée des routes d'évasion pour le gameplay bullet hell"""
        
        # S'assurer qu'il y a toujours un chemin libre vers les bords des salles
        for room in self.rooms:
            if room.room_type in [RoomType.ARENA, RoomType.CHAMBER]:
                self.ensure_edge_access(room)
    
    def ensure_edge_access(self, room: Room):
        """S'assure qu'il y a un accès libre vers les bords de la salle"""
        
        edge_width = 60  # Largeur de la zone de bord libre
        
        # Zones de bord à garder libres
        edge_zones = [
            pygame.Rect(room.x, room.y, room.width, edge_width),  # Haut
            pygame.Rect(room.x, room.y + room.height - edge_width, room.width, edge_width),  # Bas
            pygame.Rect(room.x, room.y, edge_width, room.height),  # Gauche
            pygame.Rect(room.x + room.width - edge_width, room.y, edge_width, room.height)  # Droite
        ]
        
        # Supprimer les obstacles qui bloquent les bords
        room.obstacles = [
            obs for obs in room.obstacles 
            if not any(obs.colliderect(zone) for zone in edge_zones)
        ]
    
    # Méthodes pour la génération de layouts spéciaux
    def create_intro_layout(self):
        """Layout simple pour les premières vagues"""
        # Une grande salle centrale simple
        margin = 200
        room = Room(
            margin, margin,
            self.world_width - 2 * margin,
            self.world_height - 2 * margin,
            RoomType.ARENA,
            self.environment_type
        )
        room.special_features.append("intro_arena")
        self.rooms.append(room)
    
    def create_endgame_layout(self):
        """Layout complexe pour les vagues finales"""
        
        # Complexe de salles interconnectées
        # Centre avec plusieurs arènes connectées
        
        # Arène principale
        main_size = 400
        main_x = (self.world_width - main_size) // 2
        main_y = (self.world_height - main_size) // 2
        
        main_arena = Room(
            main_x, main_y, main_size, main_size,
            RoomType.ARENA, self.environment_type
        )
        main_arena.special_features.append("main_arena")
        self.rooms.append(main_arena)
        
        # Arènes satellites
        satellite_positions = [
            (main_x - 300, main_y, 250, 400),      # Gauche
            (main_x + main_size + 50, main_y, 250, 400),  # Droite
            (main_x, main_y - 300, 400, 250),      # Haut
            (main_x, main_y + main_size + 50, 400, 250),  # Bas
        ]
        
        for i, (x, y, w, h) in enumerate(satellite_positions):
            # S'assurer que c'est dans les limites
            x = max(50, min(self.world_width - w - 50, x))
            y = max(50, min(self.world_height - h - 50, y))
            
            satellite = Room(
                x, y, w, h,
                RoomType.CHAMBER, self.environment_type
            )
            satellite.special_features.append(f"endgame_satellite_{i}")
            self.rooms.append(satellite)

# Classe d'intégration avec le jeu principal
class WorldGeneratorIntegrator:
    """Intègre le générateur de monde avec le système existant"""
    
    @staticmethod
    def create_walls_for_wave(wave_number: int, morality_system=None) -> List[pygame.Rect]:
        """Crée les murs pour une vague donnée (compatible avec main.py)"""
        
        generator = WorldGenerator()
        walls, rooms = generator.generate_world(wave_number, morality_system)
        
        return walls
    
    @staticmethod
    def get_enemy_spawn_positions(wave_number: int, morality_system=None) -> List[Tuple[int, int]]:
        """Retourne les positions de spawn pour les ennemis"""
        
        generator = WorldGenerator()
        walls, rooms = generator.generate_world(wave_number, morality_system)
        
        spawn_positions = generator.get_spawn_positions()
        
        # Si pas de positions spécifiques, utiliser des positions par défaut
        if not spawn_positions:
            world_width = generator.world_width
            world_height = generator.world_height
            
            spawn_positions = [
                (100, 100),
                (world_width - 100, 100),
                (100, world_height - 100),
                (world_width - 100, world_height - 100),
                (world_width // 2, 100),
                (world_width // 2, world_height - 100),
                (100, world_height // 2),
                (world_width - 100, world_height // 2),
            ]
        
        return spawn_positions