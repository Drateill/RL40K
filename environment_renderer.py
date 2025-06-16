"""
Système de rendu pour les environnements
Gère l'affichage visuel des différents biomes avec leurs effets spéciaux
"""

import pygame
import random
import math
from typing import List, Tuple
from environment_system import EnvironmentSystem, EnvironmentType

class EnvironmentRenderer:
    """Gestionnaire du rendu visuel des environnements"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Timer pour les effets animés
        self.animation_timer = 0
        
        # Particules d'ambiance
        self.ambient_particles = []
        
        # Cache des surfaces pour les effets de sol
        self.floor_pattern_cache = {}
        self.wall_pattern_cache = {}
        
        # Effets spéciaux par environnement
        self.environment_effects = {
            EnvironmentType.SHIP: self._create_ship_effects,
            EnvironmentType.TEMPLE: self._create_temple_effects,
            EnvironmentType.FORGE: self._create_forge_effects,
            EnvironmentType.CHAOS: self._create_chaos_effects,
            EnvironmentType.DEATH_WORLD: self._create_death_world_effects
        }
    
    def update(self, environment_system: EnvironmentSystem):
        """Met à jour les effets visuels"""
        self.animation_timer += 1
        
        # Mettre à jour les particules ambiantes
        self._update_ambient_particles()
        
        # Générer de nouvelles particules selon l'environnement
        if environment_system.should_spawn_special_effects():
            self._spawn_ambient_effects(environment_system.current_environment)
    
    def draw_background(self, screen: pygame.Surface, camera, 
                       environment_system: EnvironmentSystem):
        """Dessine le fond de l'environnement"""
        if not environment_system.current_config:
            return
        
        # Couleur de base du sol
        floor_color = environment_system.get_floor_color()
        screen.fill(floor_color)
        
        # Motifs spécifiques selon l'environnement
        self._draw_floor_pattern(screen, camera, environment_system)
        
        # Effets d'ambiance
        self._draw_ambient_effects(screen, camera, environment_system)
    
    def draw_walls(self, screen: pygame.Surface, walls: List, camera,
                   environment_system: EnvironmentSystem):
        """Dessine les murs avec le style de l'environnement"""
        if not environment_system.current_config:
            # Rendu par défaut
            for wall in walls:
                if camera.is_visible(wall):
                    wall_screen_rect = camera.apply(wall)
                    pygame.draw.rect(screen, (128, 128, 128), wall_screen_rect)
            return
        
        wall_color = environment_system.get_wall_color()
        accent_color = environment_system.current_config.accent_color
        env_type = environment_system.current_environment
        
        for wall in walls:
            if camera.is_visible(wall):
                wall_screen_rect = camera.apply(wall)
                
                # Dessiner le mur de base
                pygame.draw.rect(screen, wall_color, wall_screen_rect)
                
                # Ajouter des détails selon l'environnement
                self._add_wall_details(screen, wall_screen_rect, env_type, 
                                     wall_color, accent_color)
    
    def _draw_floor_pattern(self, screen: pygame.Surface, camera,
                           environment_system: EnvironmentSystem):
        """Dessine les motifs du sol selon l'environnement"""
        env_type = environment_system.current_environment
        
        if env_type == EnvironmentType.SHIP:
            self._draw_ship_floor(screen, camera, environment_system)
        elif env_type == EnvironmentType.TEMPLE:
            self._draw_temple_floor(screen, camera, environment_system)
        elif env_type == EnvironmentType.FORGE:
            self._draw_forge_floor(screen, camera, environment_system)
        elif env_type == EnvironmentType.CHAOS:
            self._draw_chaos_floor(screen, camera, environment_system)
        elif env_type == EnvironmentType.DEATH_WORLD:
            self._draw_death_world_floor(screen, camera, environment_system)
    
    def _draw_ship_floor(self, screen: pygame.Surface, camera,
                        environment_system: EnvironmentSystem):
        """Motifs métalliques pour le vaisseau"""
        # Grille métallique subtile
        grid_size = 64
        line_color = (60, 60, 80)  # Lignes métalliques sombres
        
        # Calculer les lignes visibles
        start_x = int(camera.x // grid_size) * grid_size
        start_y = int(camera.y // grid_size) * grid_size
        
        # Lignes verticales
        for x in range(start_x, start_x + self.screen_width + grid_size, grid_size):
            screen_x = x - camera.x
            if 0 <= screen_x <= self.screen_width:
                pygame.draw.line(screen, line_color, 
                               (screen_x, 0), (screen_x, self.screen_height), 1)
        
        # Lignes horizontales
        for y in range(start_y, start_y + self.screen_height + grid_size, grid_size):
            screen_y = y - camera.y
            if 0 <= screen_y <= self.screen_height:
                pygame.draw.line(screen, line_color,
                               (0, screen_y), (self.screen_width, screen_y), 1)
        
        # Plaques métalliques occasionnelles
        if self.animation_timer % 30 == 0:  # Toutes les 0.5 secondes
            for _ in range(2):
                plate_world_x = random.randint(int(camera.x), int(camera.x + self.screen_width))
                plate_world_y = random.randint(int(camera.y), int(camera.y + self.screen_height))
                plate_screen_x, plate_screen_y = camera.apply_pos(plate_world_x, plate_world_y)
                
                plate_size = random.randint(20, 40)
                plate_color = (80, 80, 100)
                pygame.draw.rect(screen, plate_color,
                               (plate_screen_x, plate_screen_y, plate_size, plate_size))
    
    def _draw_temple_floor(self, screen: pygame.Surface, camera,
                          environment_system: EnvironmentSystem):
        """Motifs de marbre pour le temple"""
        # Dalles de marbre
        tile_size = 80
        mortar_color = (50, 40, 30)  # Joints sombres
        
        start_x = int(camera.x // tile_size) * tile_size
        start_y = int(camera.y // tile_size) * tile_size
        
        # Dessiner les joints
        for x in range(start_x, start_x + self.screen_width + tile_size, tile_size):
            screen_x = x - camera.x
            if 0 <= screen_x <= self.screen_width:
                pygame.draw.line(screen, mortar_color,
                               (screen_x, 0), (screen_x, self.screen_height), 2)
        
        for y in range(start_y, start_y + self.screen_height + tile_size, tile_size):
            screen_y = y - camera.y
            if 0 <= screen_y <= self.screen_height:
                pygame.draw.line(screen, mortar_color,
                               (0, screen_y), (self.screen_width, screen_y), 2)
        
        # Motifs dorés occasionnels
        if random.random() < 0.02:  # 2% de chance par frame
            pattern_world_x = random.randint(int(camera.x), int(camera.x + self.screen_width))
            pattern_world_y = random.randint(int(camera.y), int(camera.y + self.screen_height))
            pattern_screen_x, pattern_screen_y = camera.apply_pos(pattern_world_x, pattern_world_y)
            
            # Petit motif en croix dorée
            gold_color = (200, 180, 100)
            cross_size = 8
            pygame.draw.line(screen, gold_color,
                           (pattern_screen_x - cross_size, pattern_screen_y),
                           (pattern_screen_x + cross_size, pattern_screen_y), 2)
            pygame.draw.line(screen, gold_color,
                           (pattern_screen_x, pattern_screen_y - cross_size),
                           (pattern_screen_x, pattern_screen_y + cross_size), 2)
    
    def _draw_forge_floor(self, screen: pygame.Surface, camera,
                         environment_system: EnvironmentSystem):
        """Sol industriel avec taches et grilles"""
        # Grilles d'aération
        grate_spacing = 120
        grate_color = (60, 40, 20)
        
        start_x = int(camera.x // grate_spacing) * grate_spacing
        start_y = int(camera.y // grate_spacing) * grate_spacing
        
        for x in range(start_x, start_x + self.screen_width + grate_spacing, grate_spacing):
            for y in range(start_y, start_y + self.screen_height + grate_spacing, grate_spacing):
                screen_x, screen_y = camera.apply_pos(x, y)
                
                if (-50 <= screen_x <= self.screen_width + 50 and 
                    -50 <= screen_y <= self.screen_height + 50):
                    # Grille carrée
                    grate_size = 30
                    for i in range(0, grate_size, 6):
                        pygame.draw.line(screen, grate_color,
                                       (screen_x + i, screen_y),
                                       (screen_x + i, screen_y + grate_size), 1)
                        pygame.draw.line(screen, grate_color,
                                       (screen_x, screen_y + i),
                                       (screen_x + grate_size, screen_y + i), 1)
        
        # Taches d'huile et de rouille
        if random.random() < 0.05:  # 5% de chance
            stain_world_x = random.randint(int(camera.x), int(camera.x + self.screen_width))
            stain_world_y = random.randint(int(camera.y), int(camera.y + self.screen_height))
            stain_screen_x, stain_screen_y = camera.apply_pos(stain_world_x, stain_world_y)
            
            stain_color = random.choice([(100, 50, 20), (60, 30, 10), (40, 40, 20)])
            stain_size = random.randint(15, 35)
            
            # Tache irrégulière (approximée par un cercle)
            pygame.draw.circle(screen, stain_color,
                             (stain_screen_x, stain_screen_y), stain_size)
    
    def _draw_chaos_floor(self, screen: pygame.Surface, camera,
                         environment_system: EnvironmentSystem):
        """Sol corrompu avec distorsions"""
        # Motifs chaotiques changeants
        chaos_intensity = (math.sin(self.animation_timer * 0.05) + 1) / 2
        
        # Cercles de corruption
        if random.random() < 0.08:  # 8% de chance
            corruption_world_x = random.randint(int(camera.x), int(camera.x + self.screen_width))
            corruption_world_y = random.randint(int(camera.y), int(camera.y + self.screen_height))
            corruption_screen_x, corruption_screen_y = camera.apply_pos(corruption_world_x, corruption_world_y)
            
            corruption_radius = int(20 + chaos_intensity * 15)
            corruption_alpha = int(30 + chaos_intensity * 20)
            
            # Surface avec transparence pour l'effet de corruption
            corruption_surface = pygame.Surface((corruption_radius * 2, corruption_radius * 2))
            corruption_surface.set_alpha(corruption_alpha)
            
            corruption_color = (150 + int(chaos_intensity * 50), 0, 150 + int(chaos_intensity * 50))
            pygame.draw.circle(corruption_surface, corruption_color,
                             (corruption_radius, corruption_radius), corruption_radius)
            
            screen.blit(corruption_surface,
                       (corruption_screen_x - corruption_radius,
                        corruption_screen_y - corruption_radius))
        
        # Lignes de fracture chaotiques
        if random.random() < 0.03:  # 3% de chance
            fracture_start_x = random.randint(0, self.screen_width)
            fracture_start_y = random.randint(0, self.screen_height)
            fracture_end_x = fracture_start_x + random.randint(-100, 100)
            fracture_end_y = fracture_start_y + random.randint(-100, 100)
            
            fracture_color = (200, 0, 200)
            pygame.draw.line(screen, fracture_color,
                           (fracture_start_x, fracture_start_y),
                           (fracture_end_x, fracture_end_y), 2)
    
    def _draw_death_world_floor(self, screen: pygame.Surface, camera,
                               environment_system: EnvironmentSystem):
        """Sol organique et dangereux"""
        # Texture organique avec des "veines"
        vein_color = (60, 80, 40)
        
        if random.random() < 0.04:  # 4% de chance
            vein_world_x = random.randint(int(camera.x), int(camera.x + self.screen_width))
            vein_world_y = random.randint(int(camera.y), int(camera.y + self.screen_height))
            vein_screen_x, vein_screen_y = camera.apply_pos(vein_world_x, vein_world_y)
            
            # Veine organique courbe
            vein_length = random.randint(40, 80)
            vein_angle = random.uniform(0, 2 * math.pi)
            
            vein_end_x = vein_screen_x + math.cos(vein_angle) * vein_length
            vein_end_y = vein_screen_y + math.sin(vein_angle) * vein_length
            
            pygame.draw.line(screen, vein_color,
                           (vein_screen_x, vein_screen_y),
                           (vein_end_x, vein_end_y), 3)
        
        # Spores flottantes
        if random.random() < 0.06:  # 6% de chance
            spore_world_x = random.randint(int(camera.x), int(camera.x + self.screen_width))
            spore_world_y = random.randint(int(camera.y), int(camera.y + self.screen_height))
            spore_screen_x, spore_screen_y = camera.apply_pos(spore_world_x, spore_world_y)
            
            spore_color = (80, 120, 60)
            spore_size = random.randint(3, 8)
            
            # Spore avec léger halo
            pygame.draw.circle(screen, spore_color,
                             (spore_screen_x, spore_screen_y), spore_size)
            pygame.draw.circle(screen, (40, 60, 30),
                             (spore_screen_x, spore_screen_y), spore_size + 2, 1)
    
    def _add_wall_details(self, screen: pygame.Surface, wall_rect: pygame.Rect,
                         env_type: EnvironmentType, wall_color: Tuple[int, int, int],
                         accent_color: Tuple[int, int, int]):
        """Ajoute des détails aux murs selon l'environnement"""
        
        if env_type == EnvironmentType.SHIP:
            # Bordures métalliques
            border_color = tuple(min(255, c + 30) for c in wall_color)
            pygame.draw.rect(screen, border_color, wall_rect, 2)
            
            # Rivets occasionnels
            if wall_rect.width > 40 and wall_rect.height > 40:
                rivet_color = accent_color
                rivet_spacing = 25
                
                for x in range(wall_rect.left + rivet_spacing, 
                             wall_rect.right - 5, rivet_spacing):
                    for y in range(wall_rect.top + rivet_spacing,
                                 wall_rect.bottom - 5, rivet_spacing):
                        pygame.draw.circle(screen, rivet_color, (x, y), 2)
        
        elif env_type == EnvironmentType.TEMPLE:
            # Bordures dorées pour les gros murs
            if wall_rect.width > 60 or wall_rect.height > 60:
                pygame.draw.rect(screen, accent_color, wall_rect, 3)
            
            # Motifs en croix
            if wall_rect.width > 50 and wall_rect.height > 50:
                center_x = wall_rect.centerx
                center_y = wall_rect.centery
                cross_size = 8
                
                pygame.draw.line(screen, accent_color,
                               (center_x - cross_size, center_y),
                               (center_x + cross_size, center_y), 2)
                pygame.draw.line(screen, accent_color,
                               (center_x, center_y - cross_size),
                               (center_x, center_y + cross_size), 2)
        
        elif env_type == EnvironmentType.FORGE:
            # Tuyaux et conduits
            pipe_color = tuple(max(0, c - 20) for c in wall_color)
            
            if wall_rect.width > 80:
                # Tuyau horizontal
                pipe_y = wall_rect.centery
                pygame.draw.line(screen, pipe_color,
                               (wall_rect.left, pipe_y),
                               (wall_rect.right, pipe_y), 4)
            
            if wall_rect.height > 80:
                # Tuyau vertical
                pipe_x = wall_rect.centerx
                pygame.draw.line(screen, pipe_color,
                               (pipe_x, wall_rect.top),
                               (pipe_x, wall_rect.bottom), 4)
        
        elif env_type == EnvironmentType.CHAOS:
            # Bordures pulsantes
            pulse_intensity = abs(math.sin(self.animation_timer * 0.1))
            pulse_color = tuple(int(c + pulse_intensity * 50) for c in accent_color)
            border_width = int(2 + pulse_intensity * 3)
            
            pygame.draw.rect(screen, pulse_color, wall_rect, border_width)
            
            # Symboles chaotiques occasionnels
            if wall_rect.width > 60 and wall_rect.height > 60 and random.random() < 0.3:
                symbol_color = accent_color
                center_x, center_y = wall_rect.center
                
                # Étoile du chaos simplifiée
                star_size = 12
                for i in range(8):
                    angle = (i / 8) * 2 * math.pi
                    end_x = center_x + math.cos(angle) * star_size
                    end_y = center_y + math.sin(angle) * star_size
                    pygame.draw.line(screen, symbol_color,
                                   (center_x, center_y), (end_x, end_y), 2)
        
        elif env_type == EnvironmentType.DEATH_WORLD:
            # Texture organique rugueuse
            rough_color = tuple(min(255, c + random.randint(-10, 20)) for c in wall_color)
            pygame.draw.rect(screen, rough_color, wall_rect)
            
            # Mousses et lichens
            if random.random() < 0.4:
                moss_color = (60, 100, 40)
                moss_spots = random.randint(2, 5)
                
                for _ in range(moss_spots):
                    moss_x = random.randint(wall_rect.left + 5, wall_rect.right - 5)
                    moss_y = random.randint(wall_rect.top + 5, wall_rect.bottom - 5)
                    moss_size = random.randint(3, 8)
                    
                    pygame.draw.circle(screen, moss_color, (moss_x, moss_y), moss_size)
    
    def _update_ambient_particles(self):
        """Met à jour les particules d'ambiance"""
        # Supprimer les particules expirées et mettre à jour les autres
        active_particles = []
        
        for particle in self.ambient_particles:
            particle['life'] -= 1
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            
            # Appliquer la gravité ou d'autres forces selon le type
            if particle['type'] == 'spore':
                particle['vy'] += 0.02  # Légère gravité
            elif particle['type'] == 'spark':
                particle['vy'] += 0.05  # Gravité plus forte
            elif particle['type'] == 'chaos':
                # Mouvement chaotique
                particle['vx'] += random.uniform(-0.1, 0.1)
                particle['vy'] += random.uniform(-0.1, 0.1)
            
            if particle['life'] > 0:
                active_particles.append(particle)
        
        self.ambient_particles = active_particles
    
    def _spawn_ambient_effects(self, env_type: EnvironmentType):
        """Génère des particules d'ambiance selon l'environnement"""
        if env_type == EnvironmentType.SHIP:
            # Étincelles électriques occasionnelles
            if random.random() < 0.3:
                self.ambient_particles.append({
                    'type': 'spark',
                    'x': random.randint(0, self.screen_width),
                    'y': random.randint(0, self.screen_height),
                    'vx': random.uniform(-1, 1),
                    'vy': random.uniform(-0.5, 0.5),
                    'life': random.randint(30, 60),
                    'color': (150, 200, 255),
                    'size': random.randint(2, 4)
                })
        
        elif env_type == EnvironmentType.FORGE:
            # Étincelles de forge
            for _ in range(random.randint(1, 3)):
                self.ambient_particles.append({
                    'type': 'spark',
                    'x': random.randint(0, self.screen_width),
                    'y': random.randint(0, self.screen_height // 2),
                    'vx': random.uniform(-0.5, 0.5),
                    'vy': random.uniform(0.5, 2),
                    'life': random.randint(20, 40),
                    'color': (255, 150, 50),
                    'size': random.randint(2, 5)
                })
        
        elif env_type == EnvironmentType.CHAOS:
            # Particules chaotiques
            for _ in range(random.randint(2, 5)):
                self.ambient_particles.append({
                    'type': 'chaos',
                    'x': random.randint(0, self.screen_width),
                    'y': random.randint(0, self.screen_height),
                    'vx': random.uniform(-2, 2),
                    'vy': random.uniform(-2, 2),
                    'life': random.randint(60, 120),
                    'color': (random.randint(150, 255), 0, random.randint(150, 255)),
                    'size': random.randint(3, 7)
                })
        
        elif env_type == EnvironmentType.DEATH_WORLD:
            # Spores flottantes
            if random.random() < 0.7:
                self.ambient_particles.append({
                    'type': 'spore',
                    'x': random.randint(0, self.screen_width),
                    'y': -10,  # Apparaît en haut
                    'vx': random.uniform(-0.2, 0.2),
                    'vy': random.uniform(0.1, 0.5),
                    'life': random.randint(120, 200),
                    'color': (80, 120, 60),
                    'size': random.randint(3, 6)
                })
    
    def _draw_ambient_effects(self, screen: pygame.Surface, camera,
                             environment_system: EnvironmentSystem):
        """Dessine les effets d'ambiance et particules"""
        
        # Dessiner les particules
        for particle in self.ambient_particles:
            # Convertir en coordonnées écran (les particules sont déjà en coordonnées écran)
            alpha_ratio = particle['life'] / 120  # Assuming max life of 120
            alpha = int(255 * min(1.0, alpha_ratio))
            
            # Créer une surface avec alpha pour la particule
            particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2))
            particle_surface.set_alpha(alpha)
            particle_surface.fill(particle['color'])
            
            # Dessiner la particule
            pygame.draw.circle(particle_surface, particle['color'],
                             (particle['size'], particle['size']), particle['size'])
            
            screen.blit(particle_surface,
                       (particle['x'] - particle['size'], particle['y'] - particle['size']))
        
        # Effets d'éclairage selon l'environnement
        env_type = environment_system.current_environment
        
        if env_type == EnvironmentType.CHAOS:
            # Pulsation chaotique de l'écran
            pulse_intensity = abs(math.sin(self.animation_timer * 0.03)) * 0.1
            pulse_surface = pygame.Surface((self.screen_width, self.screen_height))
            pulse_surface.set_alpha(int(pulse_intensity * 255))
            pulse_surface.fill((150, 0, 150))
            screen.blit(pulse_surface, (0, 0))
        
        elif env_type == EnvironmentType.FORGE:
            # Lueur rouge occasionnelle (simulation de la forge)
            if random.random() < 0.05:
                glow_surface = pygame.Surface((self.screen_width, self.screen_height))
                glow_surface.set_alpha(30)
                glow_surface.fill((255, 100, 0))
                screen.blit(glow_surface, (0, 0))
    
    def _create_ship_effects(self):
        """Crée des effets spéciaux pour le vaisseau"""
        # Clignotement des lumières, alarmes, etc.
        pass
    
    def _create_temple_effects(self):
        """Crée des effets spéciaux pour le temple"""
        # Rayons de lumière divine, échos, etc.
        pass
    
    def _create_forge_effects(self):
        """Crée des effets spéciaux pour la forge"""
        # Vapeur, étincelles, bruits de machines, etc.
        pass
    
    def _create_chaos_effects(self):
        """Crée des effets spéciaux pour le chaos"""
        # Distorsions, apparitions, mutations visuelles, etc.
        pass
    
    def _create_death_world_effects(self):
        """Crée des effets spéciaux pour le monde de la mort"""
        # Brouillard toxique, cris d'animaux, végétation qui bouge, etc.
        pass