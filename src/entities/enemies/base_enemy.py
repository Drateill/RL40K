"""
Classes de base pour tous les ennemis
Évite la duplication de code et centralise les mécaniques communes
"""

import pygame
import math
from pathfinding import PathfindingHelper, FlockingBehavior

class BaseEnemy:
    """Classe de base pour tous les ennemis - Évite la duplication de code"""
    
    def __init__(self, x, y, width, height, health, speed, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.health = health
        self.max_health = health
        self.color = color
        
        # Rectangle pour collisions
        self.rect = pygame.Rect(x, y, width, height)
        
        # Animation commune
        self.animation_timer = 0
        
        # Pathfinding commun
        self.stuck_timer = 0
        self.last_pos = (x, y)
    
    def update_position(self, new_x, new_y):
        """Met à jour la position et le rectangle"""
        self.x = new_x
        self.y = new_y
        self.rect.x = self.x
        self.rect.y = self.y
    
    def move_towards_player(self, player, walls):
        """Mouvement de base vers le joueur"""
        old_x, old_y = self.x, self.y
        
        move_dx, move_dy = PathfindingHelper.get_movement_direction(
            self.x, self.y, player.x, player.y,
            self.width, self.height, walls, self.speed
        )
        
        self.update_position(self.x + move_dx, self.y + move_dy)
        
        # Gestion collisions
        collision_detected = False
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                collision_detected = True
                break
        
        if collision_detected:
            self.update_position(old_x, old_y)
        
        # Gestion anti-blocage
        if abs(self.x - self.last_pos[0]) > 1 or abs(self.y - self.last_pos[1]) > 1:
            self.stuck_timer = 0
        else:
            self.stuck_timer += 1
        
        # Si vraiment bloqué longtemps, téléportation d'urgence
        if self.stuck_timer > 120:  # 2 secondes
            new_x, new_y = PathfindingHelper.find_free_spawn_position(
                2048, 1536, self.width, self.height, walls, player, 50
            )
            self.update_position(new_x, new_y)
            self.stuck_timer = 0
        
        self.last_pos = (self.x, self.y)
    
    def apply_separation(self, other_enemies, separation_distance=40):
        """Applique la force de séparation avec les autres ennemis"""
        if other_enemies:
            sep_x, sep_y = FlockingBehavior.get_separation_force(self, other_enemies, separation_distance)
            self.x += sep_x * 0.3
            self.y += sep_y * 0.3
            self.rect.x = self.x
            self.rect.y = self.y
    
    def take_damage(self, damage):
        """Applique des dégâts - À override si résistance spéciale"""
        self.health -= damage
        return self.health <= 0
    
    def draw_health_bar(self, screen, bar_height=3, y_offset=-6):
        """Dessine la barre de vie standard"""
        bar_width = self.width
        health_ratio = self.health / self.max_health
        
        # Fond rouge foncé
        pygame.draw.rect(screen, (100, 0, 0), 
                        (self.x, self.y + y_offset, bar_width, bar_height))
        # Barre verte
        pygame.draw.rect(screen, (0, 255, 0), 
                        (self.x, self.y + y_offset, bar_width * health_ratio, bar_height))
    
    def update(self, player, walls, other_enemies=None):
        """Méthode de base - À override dans les classes filles"""
        self.animation_timer += 1
        self.move_towards_player(player, walls)
        self.apply_separation(other_enemies)
    
    def draw(self, screen):
        """Dessin de base - À override dans les classes filles"""
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        self.draw_health_bar(screen)


class BaseBoss(BaseEnemy):
    """Classe de base pour tous les boss - Fonctionnalités communes"""
    
    def __init__(self, x, y, width, height, health, speed, color, name):
        super().__init__(x, y, width, height, health, speed, color)
        self.name = name
        self.damage_resistance = 0.2  # 20% de résistance par défaut
        self.is_boss = True
        
        # Système de phases commun
        self.phase = 1
        self.max_phases = 3
        self.phase_thresholds = []  # À définir dans les classes filles
        
        # Timers communs
        self.ability_timers = {}  # Dict des cooldowns
        
        # Animation boss
        self.boss_animation_effects = []
        
        # Invulnérabilité temporaire
        self.invulnerable_timer = 0
    
    def check_phase_transition(self):
        """Vérifie et gère les transitions de phase"""
        for i, threshold in enumerate(self.phase_thresholds):
            if self.health <= threshold and self.phase == i + 1:
                self.phase = i + 2
                self.on_phase_change(self.phase)
                break
    
    def on_phase_change(self, new_phase):
        """Appelé lors d'un changement de phase - À override"""
        print(f"{self.name} entre en phase {new_phase} !")
    
    def take_damage(self, damage):
        """Dégâts avec résistance pour les boss"""
        if self.invulnerable_timer > 0:
            return False  # Invulnérable
        
        reduced_damage = damage * (1 - self.damage_resistance)
        self.health -= reduced_damage
        self.check_phase_transition()
        return self.health <= 0
    
    def update_ability_timers(self):
        """Met à jour tous les cooldowns du boss"""
        for ability in self.ability_timers:
            if self.ability_timers[ability] > 0:
                self.ability_timers[ability] -= 1
        
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1
    
    def can_use_ability(self, ability_name):
        """Vérifie si une capacité peut être utilisée"""
        return self.ability_timers.get(ability_name, 0) <= 0
    
    def use_ability(self, ability_name, cooldown):
        """Déclenche une capacité et son cooldown"""
        self.ability_timers[ability_name] = cooldown
    
    def draw_boss_health_bar(self, screen):
        """Barre de vie spéciale pour boss"""
        bar_width = self.width * 2
        bar_height = 8
        health_ratio = self.health / self.max_health
        
        # Position centrée
        bar_x = self.x - self.width // 2
        bar_y = self.y - 25
        
        # Fond
        pygame.draw.rect(screen, (50, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        
        # Couleur selon la phase
        phase_colors = [(255, 100, 100), (255, 50, 50), (255, 0, 0)]
        bar_color = phase_colors[min(self.phase - 1, len(phase_colors) - 1)]
        
        # Barre de vie
        pygame.draw.rect(screen, bar_color, 
                        (bar_x, bar_y, bar_width * health_ratio, bar_height))
        
        # Bordure dorée
        pygame.draw.rect(screen, (255, 215, 0), 
                        (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Nom du boss
        font = pygame.font.Font(None, 24)
        phase_text = f" - PHASE {self.phase}" if self.phase > 1 else ""
        name_text = font.render(f"{self.name}{phase_text}", True, (255, 215, 0))
        name_rect = name_text.get_rect(center=(self.x + self.width//2, bar_y - 20))
        screen.blit(name_text, name_rect)
    
    def draw_casting_indicator(self, screen, ability_name, progress, radius=80, color=(255, 255, 0)):
        """Dessine un indicateur d'incantation générique"""
        if progress > 0:
            warning_radius = int(radius + progress * 40)
            center_x = int(self.x + self.width // 2)
            center_y = int(self.y + self.height // 2)
            
            pygame.draw.circle(screen, color, (center_x, center_y), warning_radius, 3)
            
            # Texte d'avertissement
            font = pygame.font.Font(None, 32)
            warning_text = font.render(ability_name, True, color)
            text_rect = warning_text.get_rect(center=(center_x, self.y - 30))
            screen.blit(warning_text, text_rect)
    
    def update(self, player, walls, other_enemies=None):
        """Update commun pour tous les boss"""
        super().update(player, walls, other_enemies)
        self.update_ability_timers()
    
    def draw(self, screen):
        """Dessin de base pour boss"""
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        self.draw_boss_health_bar(screen)


class BaseShooter(BaseEnemy):
    """Classe de base pour les ennemis qui tirent"""
    
    def __init__(self, x, y, width, height, health, speed, color, shoot_delay=90, range_distance=200):
        super().__init__(x, y, width, height, health, speed, color)
        self.shoot_timer = 0
        self.shoot_delay = shoot_delay
        self.range = range_distance
    
    def get_distance_to_player(self, player):
        """Calcule la distance au joueur"""
        dx = player.x - self.x
        dy = player.y - self.y
        return math.sqrt(dx*dx + dy*dy), dx, dy
    
    def should_retreat(self, player, min_distance=100):
        """Détermine si l'ennemi doit reculer"""
        distance, _, _ = self.get_distance_to_player(player)
        return distance < min_distance
    
    def retreat_from_player(self, player, walls):
        """Recule intelligemment du joueur"""
        distance, dx, dy = self.get_distance_to_player(player)
        if distance > 0:
            # Direction opposée au joueur
            flee_dx = -dx / distance
            flee_dy = -dy / distance
            
            flee_target_x = self.x + flee_dx * 100
            flee_target_y = self.y + flee_dy * 100
            
            old_x, old_y = self.x, self.y
            move_dx, move_dy = PathfindingHelper.get_movement_direction(
                self.x, self.y, flee_target_x, flee_target_y,
                self.width, self.height, walls, self.speed
            )
            
            self.update_position(self.x + move_dx, self.y + move_dy)
            
            # Vérifier collisions
            for wall in walls:
                if self.rect.colliderect(wall.rect):
                    self.update_position(old_x, old_y)
                    break
    
    def can_shoot(self):
        """Vérifie si peut tirer"""
        return self.shoot_timer <= 0
    
    def start_shooting(self):
        """Démarre le cooldown de tir"""
        self.shoot_timer = self.shoot_delay
    
    def update_shoot_timer(self):
        """Met à jour le timer de tir"""
        if self.shoot_timer > 0:
            self.shoot_timer -= 1
    
    def update(self, player, walls, other_enemies=None):
        """Update pour les tireurs"""
        # Logique de recul si trop proche
        if self.should_retreat(player):
            self.retreat_from_player(player, walls)
        else:
            # Mouvement normal
            super().update(player, walls, other_enemies)
        
        # Mise à jour du timer
        self.update_shoot_timer()