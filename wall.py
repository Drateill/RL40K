import pygame

# Couleurs
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