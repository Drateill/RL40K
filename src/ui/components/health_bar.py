"""
Composant barre de vie réutilisable
"""
import pygame
import math

class HealthBar:
    """Barre de vie générique pour joueur et ennemis"""
    
    def __init__(self, width=100, height=8, show_text=True):
        self.width = width
        self.height = height
        self.show_text = show_text
        
        # Couleurs
        self.bg_color = (60, 60, 60)
        self.border_color = (255, 255, 255)
        self.health_color = (0, 255, 0)
        self.damage_color = (255, 255, 0)
        self.critical_color = (255, 0, 0)
        
        # Animation
        self.last_health = 100
        self.damage_flash = 0
        
    def draw(self, surface, x, y, current_health, max_health, font=None):
        """Dessine la barre de vie"""
        if max_health <= 0:
            return
            
        # Calculer le ratio de vie
        health_ratio = max(0, min(1, current_health / max_health))
        
        # Animation de dégâts (flash rouge)
        if current_health < self.last_health:
            self.damage_flash = 10
        self.last_health = current_health
        
        if self.damage_flash > 0:
            self.damage_flash -= 1
        
        # Fond de la barre
        bg_rect = pygame.Rect(x, y, self.width, self.height)
        pygame.draw.rect(surface, self.bg_color, bg_rect)
        
        # Barre de vie
        if health_ratio > 0:
            health_width = int(self.width * health_ratio)
            health_rect = pygame.Rect(x, y, health_width, self.height)
            
            # Couleur selon le niveau de vie
            if health_ratio > 0.6:
                color = self.health_color
            elif health_ratio > 0.3:
                color = self.damage_color
            else:
                color = self.critical_color
            
            # Flash rouge si dégâts récents
            if self.damage_flash > 0:
                flash_intensity = self.damage_flash / 10
                color = (
                    min(255, color[0] + int(255 * flash_intensity)),
                    max(0, color[1] - int(255 * flash_intensity)),
                    max(0, color[2] - int(255 * flash_intensity))
                )
            
            pygame.draw.rect(surface, color, health_rect)
        
        # Bordure
        pygame.draw.rect(surface, self.border_color, bg_rect, 1)
        
        # Texte (optionnel)
        if self.show_text and font:
            text = f"{int(current_health)}/{int(max_health)}"
            text_surface = font.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(x + self.width // 2, y + self.height // 2))
            surface.blit(text_surface, text_rect)

class EnemyHealthBar(HealthBar):
    """Barre de vie spécialisée pour les ennemis"""
    
    def __init__(self):
        super().__init__(width=40, height=4, show_text=False)
        self.border_color = (200, 200, 200)
        
    def draw_above_enemy(self, surface, enemy, camera_x=0, camera_y=0):
        """Dessine la barre au-dessus d'un ennemi"""
        if not hasattr(enemy, 'health') or not hasattr(enemy, 'max_health'):
            return
            
        # Ne pas afficher si pleine vie
        if enemy.health >= enemy.max_health:
            return
            
        # Position au-dessus de l'ennemi
        enemy_center_x = enemy.x + (getattr(enemy, 'width', 20) // 2)
        bar_x = enemy_center_x - (self.width // 2) - camera_x
        bar_y = enemy.y - 8 - camera_y
        
        self.draw(surface, bar_x, bar_y, enemy.health, enemy.max_health)

class PlayerHealthBar(HealthBar):
    """Barre de vie du joueur avec style amélioré"""
    
    def __init__(self, width=960):  # 80% de 1200px
        super().__init__(width=width, height=30, show_text=True)
        self.bg_color = (40, 40, 40)
        self.border_color = (255, 255, 255)
        
    def draw_hud(self, surface, x, y, current_health, max_health):
        """Dessine la barre de vie du joueur dans le HUD"""
        font = pygame.font.Font(None, 18)
        
        # Fond avec ombre
        shadow_rect = pygame.Rect(x + 2, y + 2, self.width, self.height)
        pygame.draw.rect(surface, (0, 0, 0), shadow_rect)
        
        self.draw(surface, x, y, current_health, max_health, font)
        
        # Plus de label VIE - supprimé