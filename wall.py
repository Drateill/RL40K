import pygame
from typing import List, Optional

# Couleurs par défaut
GRAY = (128, 128, 128)

class Wall:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
    
    def draw(self, screen):
        pygame.draw.rect(screen, GRAY, (self.x, self.y, self.width, self.height))

def create_border_walls(world_width, world_height):
    """Créer les murs de bordure pour un monde plus grand"""
    wall_thickness = 30
    walls = []
    
    # Mur du haut
    walls.append(Wall(0, 0, world_width, wall_thickness))
    # Mur du bas
    walls.append(Wall(0, world_height - wall_thickness, world_width, wall_thickness))
    # Mur de gauche
    walls.append(Wall(0, 0, wall_thickness, world_height))
    # Mur de droite
    walls.append(Wall(world_width - wall_thickness, 0, wall_thickness, world_height))
    
    return walls

def create_interior_walls(world_width, world_height):
    """Créer quelques murs intérieurs pour rendre le niveau plus intéressant"""
    walls = []
    
    # Quelques piliers/obstacles dans le monde (ÉVITER LE CENTRE)
    pillar_size = 60
    
    # Piliers aux quarts (pas au centre pour éviter le spawn du joueur)
    quarter_x = world_width // 4
    quarter_y = world_height // 4
    three_quarter_x = 3 * world_width // 4
    three_quarter_y = 3 * world_height // 4
    
    # 4 piliers aux coins des quarts
    walls.append(Wall(quarter_x - pillar_size//2, quarter_y - pillar_size//2, pillar_size, pillar_size))
    walls.append(Wall(three_quarter_x - pillar_size//2, quarter_y - pillar_size//2, pillar_size, pillar_size))
    walls.append(Wall(quarter_x - pillar_size//2, three_quarter_y - pillar_size//2, pillar_size, pillar_size))
    walls.append(Wall(three_quarter_x - pillar_size//2, three_quarter_y - pillar_size//2, pillar_size, pillar_size))
    
    # Quelques murs longs pour créer des couloirs (éviter le centre)
    wall_length = 200
    wall_width = 20
    
    # Murs horizontaux (décalés du centre)
    walls.append(Wall(world_width // 6, world_height // 3, wall_length, wall_width))
    walls.append(Wall(2 * world_width // 3, 2 * world_height // 3, wall_length, wall_width))
    
    # Murs verticaux (décalés du centre)
    walls.append(Wall(2 * world_width // 3, world_height // 6, wall_width, wall_length))
    walls.append(Wall(world_width // 3, 2 * world_height // 3, wall_width, wall_length))
    
    return walls

# ===== NOUVELLE INTÉGRATION AVEC LE SYSTÈME D'ENVIRONNEMENTS =====

def create_environment_walls(world_width: int, world_height: int, wave_number: int = 1, 
                           morality_system=None, environment_system=None) -> List[Wall]:
    """
    Créer les murs selon le système d'environnements
    Fonction principale qui remplace les anciennes fonctions pour les nouveaux niveaux
    """
    
    # Si pas de système d'environnement, utiliser l'ancien système
    if environment_system is None:
        print("⚠️ Pas de système d'environnement - Utilisation du layout par défaut")
        walls = create_border_walls(world_width, world_height)
        walls.extend(create_interior_walls(world_width, world_height))
        return walls
    
    # Sélectionner l'environnement pour cette vague
    env_type = environment_system.select_environment_for_wave(wave_number, morality_system)
    
    # Générer l'environnement complet
    walls = environment_system.generate_environment(world_width, world_height, env_type)
    
    print(f"🎮 Génération de niveau terminée")
    print(f"   Environnement: {environment_system.get_environment_info()['name']}")
    print(f"   Nombre de murs: {len(walls)}")
    print(f"   Modificateur de mouvement: {environment_system.get_movement_modifier():.1f}x")
    
    return walls

def get_environment_spawn_position(world_width: int, world_height: int, 
                                 entity_width: int, entity_height: int,
                                 walls: List[Wall], avoid_center: bool = True) -> tuple:
    """
    ✅ VERSION CORRIGÉE : Trouve une position de spawn GARANTIE
    """
    from pathfinding import PathfindingHelper
    
    if avoid_center:
        # Pour les ennemis - spawn sur les bords
        return PathfindingHelper.find_free_spawn_position(
            world_width, world_height, entity_width, entity_height, walls, 
            # Créer un objet player factice au centre
            type('Player', (), {'x': world_width//2, 'y': world_height//2})(),
            min_distance_from_player=200
        )
    else:
        # ✅ POUR LE JOUEUR - Logique améliorée avec fallbacks multiples
        
        # 1. Essayer le centre d'abord
        center_x = world_width // 2 - entity_width // 2
        center_y = world_height // 2 - entity_height // 2
        
        if PathfindingHelper.is_position_free(center_x, center_y, entity_width, entity_height, walls):
            print(f"✅ Spawn joueur au centre : ({center_x}, {center_y})")
            return center_x, center_y
        
        # 2. Essayer autour du centre en spirale
        print("⚠️ Centre occupé, recherche en spirale...")
        for radius in range(50, 400, 25):  # Rayons croissants
            for angle_step in range(0, 360, 30):  # Tous les 30 degrés
                angle = math.radians(angle_step)
                test_x = center_x + radius * math.cos(angle)
                test_y = center_y + radius * math.sin(angle)
                
                # Vérifier les limites du monde
                if (entity_width <= test_x <= world_width - entity_width and
                    entity_height <= test_y <= world_height - entity_height):
                    
                    if PathfindingHelper.is_position_free(test_x, test_y, entity_width, entity_height, walls):
                        print(f"✅ Spawn joueur trouvé en spirale : ({test_x:.0f}, {test_y:.0f})")
                        return test_x, test_y
        
        # 3. Fallback : Chercher dans les couloirs principaux (zones généralement libres)
        print("⚠️ Spirale échouée, recherche dans les couloirs...")
        corridor_positions = [
            # Centre horizontal
            (world_width // 2, world_height // 2 - 100),
            (world_width // 2, world_height // 2 + 100),
            # Centre vertical
            (world_width // 2 - 100, world_height // 2),
            (world_width // 2 + 100, world_height // 2),
            # Coins sûrs
            (150, 150),
            (world_width - 150, 150),
            (150, world_height - 150),
            (world_width - 150, world_height - 150),
        ]
        
        for test_x, test_y in corridor_positions:
            if PathfindingHelper.is_position_free(test_x, test_y, entity_width, entity_height, walls):
                print(f"✅ Spawn joueur dans couloir : ({test_x}, {test_y})")
                return test_x, test_y
        
        # 4. Fallback extrême : Forcer une position libre en supprimant des murs
        print("🚨 FALLBACK EXTRÊME : Création d'un espace pour le joueur...")
        emergency_x = world_width // 2 - entity_width // 2
        emergency_y = world_height // 2 - entity_height // 2
        
        # Supprimer les murs qui bloquent la zone de spawn d'urgence
        emergency_rect = pygame.Rect(emergency_x - 50, emergency_y - 50, 
                                   entity_width + 100, entity_height + 100)
        
        walls_to_remove = []
        for i, wall in enumerate(walls):
            if wall.rect.colliderect(emergency_rect):
                # Ne supprimer que les murs intérieurs (pas les bordures)
                if (wall.x > 50 and wall.y > 50 and 
                    wall.x < world_width - 50 and wall.y < world_height - 50):
                    walls_to_remove.append(i)
        
        # Supprimer les murs bloquants (en ordre inverse pour les indices)
        for i in reversed(walls_to_remove):
            removed_wall = walls.pop(i)
            print(f"   🗑️ Mur supprimé : ({removed_wall.x}, {removed_wall.y})")
        
        print(f"✅ Spawn joueur d'urgence : ({emergency_x}, {emergency_y})")
        return emergency_x, emergency_y

# ===== FONCTIONS DE COMPATIBILITÉ =====

def create_walls_for_wave(world_width: int, world_height: int, wave_number: int,
                         morality_system=None) -> List[Wall]:
    """Fonction de compatibilité pour intégration progressive"""
    try:
        from environment_system import EnvironmentSystem
        
        # Créer le système d'environnement
        env_system = EnvironmentSystem()
        
        # Générer avec le nouveau système
        return create_environment_walls(world_width, world_height, wave_number, 
                                      morality_system, env_system)
    
    except (ImportError, AttributeError) as e:
        # Fallback vers l'ancien système si erreur
        print(f"⚠️ Erreur système d'environnements: {e}")
        print("   Mode compatibilité activé")
        walls = create_border_walls(world_width, world_height)
        walls.extend(create_interior_walls(world_width, world_height))
        return walls
    

# ===== UTILITAIRES POUR LES ENVIRONNEMENTS =====

class EnvironmentWall(Wall):
    """
    Extension de Wall avec propriétés spécifiques aux environnements
    """
    
    def __init__(self, x, y, width, height, wall_type="normal", environment_type=None):
        super().__init__(x, y, width, height)
        self.wall_type = wall_type  # "normal", "door", "window", "machine", etc.
        self.environment_type = environment_type
        self.interactive = False
        self.breakable = False
        self.special_properties = {}
    
    def set_interactive(self, callback_function=None):
        """Rend le mur interactif"""
        self.interactive = True
        self.interaction_callback = callback_function
    
    def set_breakable(self, health: int = 100):
        """Rend le mur destructible"""
        self.breakable = True
        self.health = health
        self.max_health = health
    
    def interact(self, player=None):
        """Exécute l'interaction avec le mur"""
        if self.interactive and hasattr(self, 'interaction_callback'):
            if self.interaction_callback:
                self.interaction_callback(self, player)
    
    def take_damage(self, damage: int) -> bool:
        """
        Le mur prend des dégâts
        Returns: True si le mur est détruit
        """
        if not self.breakable:
            return False
        
        self.health -= damage
        return self.health <= 0

def create_door(x: int, y: int, width: int, height: int, is_open: bool = False):
    """Crée une porte interactive"""
    door = EnvironmentWall(x, y, width, height, "door")
    door.is_open = is_open
    door.set_interactive(lambda wall, player: wall.toggle_door())
    
    def toggle_door(self):
        self.is_open = not self.is_open
        print(f"Porte {'ouverte' if self.is_open else 'fermée'}")
    
    door.toggle_door = toggle_door.__get__(door, EnvironmentWall)
    return door

def create_breakable_wall(x: int, y: int, width: int, height: int, health: int = 50):
    """Crée un mur destructible"""
    wall = EnvironmentWall(x, y, width, height, "breakable")
    wall.set_breakable(health)
    return wall

# Import math pour les calculs de spawn
import math