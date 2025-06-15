"""
Ennemis de base du jeu
BasicEnemy, ShooterEnemy, FastEnemy - Les 3 premiers types d'ennemis
"""

import pygame
import math
import random
from bullet import Bullet
from .base_enemy import BaseEnemy, BaseShooter
from pathfinding import PathfindingHelper, FlockingBehavior

# Couleurs
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)
DARK_RED = (100, 0, 0)


class BasicEnemy(BaseEnemy):
    """Ennemi basique qui suit le joueur"""
    
    def __init__(self, x, y):
        super().__init__(x, y, 24, 24, 30, 2, BLUE)
    
    def draw(self, screen):
        # Dessiner l'ennemi
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        self.draw_health_bar(screen)


class ShooterEnemy(BaseShooter):
    """Ennemi qui tire sur le joueur"""
    
    def __init__(self, x, y):
        super().__init__(x, y, 20, 20, 20, 1.5, PURPLE, shoot_delay=90, range_distance=200)
    
    def try_shoot(self, player):
        """Tente de tirer sur le joueur"""
        if not self.can_shoot():
            return None
        
        distance, dx, dy = self.get_distance_to_player(player)
        
        # Tirer si dans la portée
        if distance <= self.range:
            self.start_shooting()
            
            # Normaliser direction
            if distance > 0:
                dx /= distance
                dy /= distance
            
            # Créer projectile ennemi
            bullet_x = self.x + self.width // 2
            bullet_y = self.y + self.height // 2
            return Bullet(bullet_x, bullet_y, dx, dy, is_player_bullet=False)
        
        return None
    
    def update(self, player, walls, other_enemies=None):
        """Mise à jour avec logique de tir"""
        super().update(player, walls, other_enemies)
        
        # Force de séparation spécifique
        self.apply_separation(other_enemies)
    
    def draw(self, screen):
        # Dessiner l'ennemi
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
        # Indicateur de tir (cercle rouge quand prêt à tirer)
        if self.shoot_timer <= 10:
            pygame.draw.circle(screen, (255, 0, 0), 
                             (int(self.x + self.width//2), int(self.y + self.height//2)), 3)
        
        # Barre de vie
        self.draw_health_bar(screen)


class FastEnemy(BaseEnemy):
    """Ennemi rapide mais fragile"""
    
    def __init__(self, x, y):
        super().__init__(x, y, 16, 16, 15, 4, ORANGE)
        
        # Mouvement erratique
        self.direction_timer = 0
        self.target_offset_x = 0
        self.target_offset_y = 0
    
    def update_erratic_movement(self):
        """Met à jour le mouvement erratique"""
        self.direction_timer += 1
        if self.direction_timer > 60:  # Chaque seconde
            self.target_offset_x = random.randint(-50, 50)
            self.target_offset_y = random.randint(-50, 50)
            self.direction_timer = 0
    
    def move_towards_player(self, player, walls):
        """Mouvement erratique vers le joueur"""
        old_x, old_y = self.x, self.y
        
        # Se diriger vers le joueur avec un offset (mouvement erratique)
        target_x = player.x + self.target_offset_x
        target_y = player.y + self.target_offset_y
        
        # Utiliser le pathfinding intelligent
        move_dx, move_dy = PathfindingHelper.get_movement_direction(
            self.x, self.y, target_x, target_y,
            self.width, self.height, walls, self.speed
        )
        
        self.update_position(self.x + move_dx, self.y + move_dy)
        
        # Gestion collisions
        collision = False
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                collision = True
                break
                
        if collision:
            self.update_position(old_x, old_y)
            # Changer de direction si collision
            self.direction_timer = 60
    
    def update(self, player, walls, other_enemies=None):
        """Mise à jour avec mouvement erratique"""
        self.animation_timer += 1
        self.update_erratic_movement()
        self.move_towards_player(player, walls)
        
        # Force de séparation avec distance plus petite pour les ennemis rapides
        if other_enemies:
            sep_x, sep_y = FlockingBehavior.get_separation_force(self, other_enemies, 30)
            self.x += sep_x * 0.4
            self.y += sep_y * 0.4
            self.rect.x = self.x
            self.rect.y = self.y
    
    def draw(self, screen):
        # Corps de l'ennemi
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
        # Barre de vie plus petite
        self.draw_health_bar(screen, bar_height=2, y_offset=-5)