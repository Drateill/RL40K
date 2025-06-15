import pygame
import math

class MoralityEffects:
    """Gère les effets visuels et gameplay selon la moralité"""
    
    def __init__(self):
        self.particle_timer = 0
        self.aura_particles = []
        self.screen_effects = []
        
    def get_size_multiplier(self, morality_system):
        """Calcule le multiplicateur de taille selon la moralité"""
        faith = morality_system.faith
        corruption = morality_system.corruption
        
        # Système de taille basé sur la moralité
        if faith >= 80:  # Pur - Plus petit et agile
            return 0.8
        elif faith >= 60:  # Fidèle - Légèrement plus petit
            return 0.9
        elif corruption >= 90:  # Prince Daemon - Énorme
            return 2.0
        elif corruption >= 70:  # Chaos - Très gros
            return 1.6
        elif corruption >= 50:  # Corrompu - Plus gros
            return 1.3
        elif corruption >= 30:  # Début corruption - Légèrement plus gros
            return 1.1
        else:  # Neutre
            return 1.0
    
    def get_health_bonus(self, morality_system, base_max_health):
        """Calcule le bonus de vie selon la moralité"""
        faith = morality_system.faith
        corruption = morality_system.corruption
        
        bonus = 0
        
        # Bonus de Foi (résistance spirituelle)
        if faith >= 80:
            bonus += 50  # Pur : +50 HP
        elif faith >= 60:
            bonus += 25  # Fidèle : +25 HP
        
        # Bonus de Corruption (mutations physiques)
        if corruption >= 90:
            bonus += 200  # Prince Daemon : +200 HP
        elif corruption >= 70:
            bonus += 100  # Chaos : +100 HP
        elif corruption >= 50:
            bonus += 50   # Corrompu : +50 HP
        elif corruption >= 30:
            bonus += 20   # Début corruption : +20 HP
        
        return bonus
    
    def get_speed_modifier(self, morality_system):
        """Calcule le modificateur de vitesse selon la moralité"""
        faith = morality_system.faith
        corruption = morality_system.corruption
        
        modifier = 1.0
        
        # Effets de la Foi
        if faith >= 80:  # Pur - Rigidité doctrinale
            modifier *= 0.85  # -15% vitesse
        elif faith >= 60:  # Fidèle - Légère rigidité
            modifier *= 0.95  # -5% vitesse
        
        # Effets de la Corruption
        if corruption >= 90:  # Prince Daemon - Lourd mais puissant
            modifier *= 0.7   # -30% vitesse (compensé par résistance)
        elif corruption >= 70:  # Chaos - Boost chaotique
            modifier *= 1.2   # +20% vitesse
        elif corruption >= 50:  # Corrompu - Plus lourd
            modifier *= 0.9   # -10% vitesse
        
        return modifier
    
    def apply_morality_effects(self, player, morality_system):
        """Applique tous les effets de moralité au joueur"""
        
        # 1. Taille du joueur
        size_mult = self.get_size_multiplier(morality_system)
        new_width = int(32 * size_mult)  # Taille de base 32x32
        new_height = int(32 * size_mult)
        
        # Mettre à jour la taille si elle a changé
        if player.width != new_width or player.height != new_height:
            old_center_x = player.x + player.width // 2
            old_center_y = player.y + player.height // 2
            
            player.width = new_width
            player.height = new_height
            
            # Recentrer le joueur
            player.x = old_center_x - player.width // 2
            player.y = old_center_y - player.height // 2
            player.rect = pygame.Rect(player.x, player.y, player.width, player.height)
        
        # 2. Vie maximale
        base_max_health = getattr(player, 'base_max_health', 100)
        health_bonus = self.get_health_bonus(morality_system, base_max_health)
        new_max_health = base_max_health + health_bonus
        
        # Ajuster la vie si la vie max change
        if player.max_health != new_max_health:
            health_ratio = player.health / player.max_health if player.max_health > 0 else 1
            player.max_health = new_max_health
            player.health = min(player.health, player.max_health)  # Ne pas dépasser le nouveau max
        
        # 3. Modificateur de vitesse (appliqué dans player.update)
        player.morality_speed_modifier = self.get_speed_modifier(morality_system)
        
        # 4. Effets visuels
        self.update_visual_effects(player, morality_system)
    
    def update_visual_effects(self, player, morality_system):
        """Met à jour les effets visuels selon la moralité"""
        self.particle_timer += 1
        
        # Nettoyer les anciennes particules
        self.aura_particles = [p for p in self.aura_particles if p['life'] > 0]
        
        # Générer des particules selon l'état moral
        if self.particle_timer % 5 == 0:  # Toutes les 5 frames
            faith = morality_system.faith
            corruption = morality_system.corruption
            
            # Particules de Foi (dorées)
            if faith >= 60:
                for _ in range(2 if faith >= 80 else 1):
                    particle = {
                        'x': player.x + player.width // 2 + (random.randint(-20, 20)),
                        'y': player.y + player.height // 2 + (random.randint(-20, 20)),
                        'vx': random.uniform(-0.5, 0.5),
                        'vy': random.uniform(-1, -0.5),
                        'life': 30,
                        'max_life': 30,
                        'color': (255, 215, 0),  # Or
                        'type': 'faith'
                    }
                    self.aura_particles.append(particle)
            
            # Particules de Corruption (pourpres)
            if corruption >= 50:
                intensity = 3 if corruption >= 90 else 2 if corruption >= 70 else 1
                for _ in range(intensity):
                    particle = {
                        'x': player.x + player.width // 2 + (random.randint(-25, 25)),
                        'y': player.y + player.height // 2 + (random.randint(-25, 25)),
                        'vx': random.uniform(-1, 1),
                        'vy': random.uniform(-1, 1),
                        'life': 40,
                        'max_life': 40,
                        'color': (150, 0, 150),  # Pourpre
                        'type': 'corruption'
                    }
                    self.aura_particles.append(particle)
        
        # Mettre à jour les particules
        for particle in self.aura_particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
    
    def draw_morality_effects(self, screen, camera, player, morality_system):
        """Dessine les effets visuels de moralité"""
        
        # 1. Dessiner les particules d'aura
        for particle in self.aura_particles:
            if particle['life'] > 0:
                # Convertir en coordonnées écran
                screen_x, screen_y = camera.apply_pos(particle['x'], particle['y'])
                
                # Alpha basé sur la vie restante
                alpha_ratio = particle['life'] / particle['max_life']
                alpha = int(255 * alpha_ratio)
                
                # Créer une surface avec alpha
                particle_surface = pygame.Surface((4, 4))
                particle_surface.set_alpha(alpha)
                particle_surface.fill(particle['color'])
                screen.blit(particle_surface, (screen_x - 2, screen_y - 2))
        
        # 2. Aura autour du joueur
        player_screen_rect = camera.apply(player)
        player_center = (
            player_screen_rect.x + player_screen_rect.width // 2,
            player_screen_rect.y + player_screen_rect.height // 2
        )
        
        faith = morality_system.faith
        corruption = morality_system.corruption
        
        # Aura de Foi
        if faith >= 60:
            aura_radius = int(40 + (faith - 60) * 0.5)
            aura_intensity = int(30 + (faith - 60) * 0.3)
            
            aura_surface = pygame.Surface((aura_radius * 2, aura_radius * 2))
            aura_surface.set_alpha(aura_intensity)
            
            # Dessiner un cercle doré
            pygame.draw.circle(aura_surface, (255, 215, 0), 
                             (aura_radius, aura_radius), aura_radius)
            
            screen.blit(aura_surface, 
                       (player_center[0] - aura_radius, player_center[1] - aura_radius))
        
        # Aura de Corruption
        if corruption >= 50:
            aura_radius = int(35 + (corruption - 50) * 0.8)
            aura_intensity = int(40 + (corruption - 50) * 0.4)
            
            # Aura pulsante
            pulse = abs(math.sin(self.particle_timer * 0.1))
            current_radius = int(aura_radius * (0.8 + 0.2 * pulse))
            
            aura_surface = pygame.Surface((current_radius * 2, current_radius * 2))
            aura_surface.set_alpha(int(aura_intensity * pulse))
            
            # Dessiner un cercle pourpre
            pygame.draw.circle(aura_surface, (150, 0, 150), 
                             (current_radius, current_radius), current_radius)
            
            screen.blit(aura_surface, 
                       (player_center[0] - current_radius, player_center[1] - current_radius))
        
        # 3. Effets spéciaux selon l'état
        if corruption >= 90:  # Prince Daemon - Distorsion de l'écran
            self.draw_chaos_distortion(screen)
        elif faith >= 80:  # Pur - Lueur divine
            self.draw_divine_glow(screen)
    
    def draw_chaos_distortion(self, screen):
        """Effet de distorsion chaotique pour les Princes Daemon"""
        # Effet de tremblement subtil des bords
        distortion_intensity = 2
        
        for i in range(5):
            x = random.randint(0, 1024)
            y = random.randint(0, 768)
            
            distortion_surface = pygame.Surface((20, 20))
            distortion_surface.set_alpha(20)
            distortion_surface.fill((random.randint(100, 255), 0, random.randint(100, 255)))
            screen.blit(distortion_surface, (x, y))
    
    def draw_divine_glow(self, screen):
        """Effet de lueur divine pour les Purs"""
        # Légère lueur dorée sur les bords de l'écran
        glow_intensity = abs(math.sin(self.particle_timer * 0.05)) * 15
        
        glow_surface = pygame.Surface((1024, 768))
        glow_surface.set_alpha(int(glow_intensity))
        glow_surface.fill((255, 250, 200))
        screen.blit(glow_surface, (0, 0))

# Import nécessaire pour les particules
import random