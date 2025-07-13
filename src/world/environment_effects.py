"""
Effets d'environnement - Extrait de main.py
Contient EnvironmentEffects avec toute la logique de particules et effets visuels
"""
import pygame
import random
from ..core.constants import WORLD_WIDTH, WORLD_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT

class EnvironmentEffects:
    """Effets visuels d'environnement"""
    
    def __init__(self):
        self.particle_timer = 0
        self.particles = []
    
    def update(self, environment):
        """Met à jour les effets"""
        self.particle_timer += 1
        
        # Nettoyer les anciennes particules
        self.particles = [p for p in self.particles if p['life'] > 0]
        
        # Limiter le nombre de particules
        if len(self.particles) > 50:
            self.particles = self.particles[-50:]
        
        # Générer nouvelles particules
        if self.particle_timer % 15 == 0:
            if environment == "imperial_shrine":
                self.add_holy_particle()
            elif environment == "chaos_temple":
                self.add_chaos_particle()
            elif environment == "daemon_realm":
                self.add_warp_particle()
        
        # Mettre à jour les particules
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
    
    def add_holy_particle(self):
        """Ajoute une particule sacrée"""
        particle = {
            'x': random.randint(0, WORLD_WIDTH),
            'y': random.randint(0, WORLD_HEIGHT),
            'vx': random.uniform(-0.5, 0.5),
            'vy': random.uniform(-1, -0.3),
            'life': 120,
            'color': (255, 255, 200),
            'size': random.randint(2, 4)
        }
        self.particles.append(particle)
    
    def add_chaos_particle(self):
        """Ajoute une particule chaotique"""
        particle = {
            'x': random.randint(0, WORLD_WIDTH),
            'y': random.randint(0, WORLD_HEIGHT),
            'vx': random.uniform(-2, 2),
            'vy': random.uniform(-2, 2),
            'life': 80,
            'color': (random.randint(150, 255), 0, random.randint(150, 255)),
            'size': random.randint(3, 6)
        }
        self.particles.append(particle)
    
    def add_warp_particle(self):
        """Ajoute une particule warp"""
        particle = {
            'x': random.randint(0, WORLD_WIDTH),
            'y': random.randint(0, WORLD_HEIGHT),
            'vx': random.uniform(-3, 3),
            'vy': random.uniform(-3, 3),
            'life': 60,
            'color': (random.randint(100, 200), random.randint(0, 100), random.randint(100, 255)),
            'size': random.randint(4, 8)
        }
        self.particles.append(particle)
    
    def draw(self, screen, camera):
        """Dessine les effets"""
        for particle in self.particles:
            screen_x, screen_y = camera.apply_pos(particle['x'], particle['y'])
            
            # Vérifier si visible
            if -50 <= screen_x <= SCREEN_WIDTH + 50 and -50 <= screen_y <= SCREEN_HEIGHT + 50:
                alpha = int(255 * (particle['life'] / 120))
                alpha = max(0, min(255, alpha))
                
                size = particle['size']
                particle_surface = pygame.Surface((size * 2, size * 2))
                particle_surface.set_alpha(alpha)
                particle_surface.fill(particle['color'])
                screen.blit(particle_surface, (screen_x - size, screen_y - size))