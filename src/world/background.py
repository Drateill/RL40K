"""
Système de fond animé pour donner l'impression de mouvement
"""
import pygame
import random
import math

class StarField:
    """Champ d'étoiles animé avec parallaxe"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Créer plusieurs couches d'étoiles pour l'effet de parallaxe
        self.star_layers = [
            {"stars": [], "speed": 0.1, "color": (100, 100, 100), "size": 1},  # Étoiles lointaines
            {"stars": [], "speed": 0.3, "color": (150, 150, 150), "size": 1},  # Étoiles moyennes
            {"stars": [], "speed": 0.6, "color": (200, 200, 200), "size": 2},  # Étoiles proches
        ]
        
        # Générer les étoiles
        self.generate_stars()
    
    def generate_stars(self):
        """Génère les étoiles pour chaque couche"""
        star_counts = [200, 100, 50]  # Nombre d'étoiles par couche
        
        for layer_idx, layer in enumerate(self.star_layers):
            for _ in range(star_counts[layer_idx]):
                star = {
                    "x": random.randint(0, self.screen_width * 2),  # Zone plus large pour le défilement
                    "y": random.randint(0, self.screen_height * 2),
                    "brightness": random.uniform(0.3, 1.0)  # Variation de luminosité
                }
                layer["stars"].append(star)
    
    def update(self, camera_x, camera_y):
        """Met à jour la position des étoiles selon la caméra"""
        for layer in self.star_layers:
            for star in layer["stars"]:
                # Déplacement parallaxe basé sur la vitesse de la couche
                star["x"] -= camera_x * layer["speed"] * 0.01
                star["y"] -= camera_y * layer["speed"] * 0.01
                
                # Réapparition des étoiles qui sortent de l'écran
                if star["x"] < -50:
                    star["x"] = self.screen_width + 50
                    star["y"] = random.randint(0, self.screen_height)
                elif star["x"] > self.screen_width + 50:
                    star["x"] = -50
                    star["y"] = random.randint(0, self.screen_height)
                
                if star["y"] < -50:
                    star["y"] = self.screen_height + 50
                    star["x"] = random.randint(0, self.screen_width)
                elif star["y"] > self.screen_height + 50:
                    star["y"] = -50
                    star["x"] = random.randint(0, self.screen_width)
    
    def draw(self, surface):
        """Dessine le champ d'étoiles"""
        for layer in self.star_layers:
            for star in layer["stars"]:
                # Calculer la couleur avec la luminosité
                color = tuple(int(c * star["brightness"]) for c in layer["color"])
                
                # Dessiner l'étoile
                if layer["size"] == 1:
                    surface.set_at((int(star["x"]), int(star["y"])), color)
                else:
                    pygame.draw.circle(surface, color, 
                                     (int(star["x"]), int(star["y"])), layer["size"])

class GridBackground:
    """Grille de fond pour accentuer le mouvement"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.grid_size = 100  # Taille des cellules de la grille
        self.color = (30, 30, 40)  # Couleur subtile
        self.alpha = 80  # Transparence
    
    def draw(self, surface, camera_x, camera_y):
        """Dessine la grille avec défilement"""
        # Créer une surface transparente pour la grille
        grid_surface = pygame.Surface((self.screen_width, self.screen_height))
        grid_surface.set_alpha(self.alpha)
        grid_surface.fill((0, 0, 0))  # Fond transparent
        
        # Calculer l'offset de la grille basé sur la caméra
        offset_x = int(camera_x) % self.grid_size
        offset_y = int(camera_y) % self.grid_size
        
        # Dessiner les lignes verticales
        for x in range(-offset_x, self.screen_width + self.grid_size, self.grid_size):
            pygame.draw.line(grid_surface, self.color, 
                           (x, 0), (x, self.screen_height), 1)
        
        # Dessiner les lignes horizontales
        for y in range(-offset_y, self.screen_height + self.grid_size, self.grid_size):
            pygame.draw.line(grid_surface, self.color, 
                           (0, y), (self.screen_width, y), 1)
        
        surface.blit(grid_surface, (0, 0))

class FloatingParticles:
    """Particules flottantes pour plus d'ambiance"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.particles = []
        
        # Générer des particules initiales
        for _ in range(30):
            self.create_particle()
    
    def create_particle(self):
        """Crée une nouvelle particule"""
        particle = {
            "x": random.randint(0, self.screen_width),
            "y": random.randint(0, self.screen_height),
            "size": random.randint(1, 3),
            "speed_x": random.uniform(-0.5, 0.5),
            "speed_y": random.uniform(-0.5, 0.5),
            "alpha": random.randint(50, 150),
            "color": random.choice([(100, 100, 150), (80, 120, 100), (120, 100, 100)])
        }
        return particle
    
    def update(self, dt):
        """Met à jour les particules"""
        for particle in self.particles:
            particle["x"] += particle["speed_x"] * dt * 60
            particle["y"] += particle["speed_y"] * dt * 60
            
            # Réapparition des particules qui sortent
            if particle["x"] < -10:
                particle["x"] = self.screen_width + 10
            elif particle["x"] > self.screen_width + 10:
                particle["x"] = -10
            
            if particle["y"] < -10:
                particle["y"] = self.screen_height + 10
            elif particle["y"] > self.screen_height + 10:
                particle["y"] = -10
    
    def draw(self, surface):
        """Dessine les particules"""
        for particle in self.particles:
            # Créer une surface transparente pour la particule
            particle_surface = pygame.Surface((particle["size"] * 2, particle["size"] * 2))
            particle_surface.set_alpha(particle["alpha"])
            particle_surface.fill(particle["color"])
            
            surface.blit(particle_surface, 
                        (int(particle["x"]), int(particle["y"])))

class GameBackground:
    """Gestionnaire principal du fond de jeu"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Créer les différents éléments de fond
        self.star_field = StarField(screen_width, screen_height)
        self.grid = GridBackground(screen_width, screen_height)
        self.particles = FloatingParticles(screen_width, screen_height)
        
        # Couleur de fond de base
        self.base_color = (10, 10, 15)  # Bleu très sombre
    
    def update(self, dt, camera_x, camera_y):
        """Met à jour tous les éléments de fond"""
        self.star_field.update(camera_x, camera_y)
        self.particles.update(dt)
    
    def draw(self, surface, camera_x, camera_y):
        """Dessine le fond complet"""
        # Fond de base
        surface.fill(self.base_color)
        
        # Champ d'étoiles (arrière-plan)
        self.star_field.draw(surface)
        
        # Grille (pour accentuer le mouvement)
        self.grid.draw(surface, camera_x, camera_y)
        
        # Particules flottantes (avant-plan)
        self.particles.draw(surface)