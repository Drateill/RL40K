import pygame

class Camera:
    def __init__(self, screen_width, screen_height, world_width, world_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.world_width = world_width
        self.world_height = world_height
        
        # Position de la caméra dans le monde
        self.x = 0
        self.y = 0
        
        # Smoothing de la caméra
        self.smoothing = 0.1  # Plus doux pour un effet cinématique
        self.target_x = 0
        self.target_y = 0
        
        # Deadzone réduite pour un meilleur suivi
        self.deadzone_width = 50
        self.deadzone_height = 40
        
    def update(self, target):
        """Met à jour la position de la caméra pour suivre la cible (joueur)"""
        # Position idéale : centrer le joueur sur l'écran
        ideal_x = target.x + target.width // 2 - self.screen_width // 2
        ideal_y = target.y + target.height // 2 - self.screen_height // 2
        
        # Smoothing pour un suivi fluide
        self.x += (ideal_x - self.x) * self.smoothing
        self.y += (ideal_y - self.y) * self.smoothing
        
        # Limiter aux bords du monde
        self.x = max(0, min(self.x, self.world_width - self.screen_width))
        self.y = max(0, min(self.y, self.world_height - self.screen_height))
    
    def apply(self, entity):
        """Applique l'offset de la caméra à une entité pour l'affichage"""
        return pygame.Rect(
            entity.rect.x - self.x,
            entity.rect.y - self.y, 
            entity.rect.width,
            entity.rect.height
        )
    
    def apply_pos(self, x, y):
        """Applique l'offset de la caméra à une position"""
        return (x - self.x, y - self.y)
    
    def world_to_screen(self, world_x, world_y):
        """Convertit des coordonnées monde en coordonnées écran"""
        return (world_x - self.x, world_y - self.y)
    
    def screen_to_world(self, screen_x, screen_y):
        """Convertit des coordonnées écran en coordonnées monde"""
        world_x = screen_x + self.x
        world_y = screen_y + self.y
        return (world_x, world_y)
    
    def is_visible(self, entity, margin=50):
        """Vérifie si une entité est visible à l'écran (avec marge)"""
        screen_rect = pygame.Rect(-margin, -margin, 
                                 self.screen_width + margin * 2, 
                                 self.screen_height + margin * 2)
        entity_screen_pos = self.apply(entity)
        return screen_rect.colliderect(entity_screen_pos)
    
    def get_visible_area(self):
        """Retourne le rectangle de la zone visible dans le monde"""
        return pygame.Rect(self.x, self.y, self.screen_width, self.screen_height)