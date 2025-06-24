# Nouveau fichier: warning_system.py
import pygame
import math

class WarningZone:
    def __init__(self, x, y, radius, duration, warning_time):
        self.x = x
        self.y = y
        self.radius = radius
        self.duration = duration
        self.warning_time = warning_time
        self.timer = 0
        self.active = False
    
    def update(self):
        self.timer += 1
        if self.timer >= self.warning_time and not self.active:
            self.active = True
            return True  # Signal pour déclencher l'attaque
        elif self.timer >= self.warning_time + self.duration:
            return "remove"  # Signal pour supprimer la zone
        return False
    
    def draw(self, screen, camera):
        screen_x, screen_y = camera.apply_pos(self.x, self.y)
        
        if not self.active:
            # Phase d'avertissement
            alpha = int(100 + 50 * math.sin(self.timer * 0.3))
            warning_surface = pygame.Surface((self.radius * 2, self.radius * 2))
            warning_surface.set_alpha(alpha)
            warning_surface.fill((255, 255, 0))
            
            pygame.draw.circle(warning_surface, (255, 255, 0), 
                             (self.radius, self.radius), self.radius)
            screen.blit(warning_surface, (screen_x - self.radius, screen_y - self.radius))
        else:
            # Phase active
            pygame.draw.circle(screen, (255, 0, 0), (int(screen_x), int(screen_y)), 
                             self.radius, 5)