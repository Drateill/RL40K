"""
Ennemis spéciaux avancés
CultistEnemy, RenegadeMarineEnemy, DaemonEnemy - Ennemis avec capacités uniques
"""

import pygame
import math
import random
from bullet import Bullet
from pathfinding import PathfindingHelper, FlockingBehavior
from .base_enemy import BaseEnemy

# Couleurs pour les ennemis spéciaux
DARK_PURPLE = (80, 0, 80)
BRONZE = (205, 127, 50)
CRIMSON = (220, 20, 60)
VOID_BLACK = (20, 20, 20)
GREEN = (0, 255, 0)
DARK_RED = (100, 0, 0)


class CultistEnemy(BaseEnemy):
    """Cultiste du Chaos - Invoque des démons mineurs et se sacrifie"""
    
    def __init__(self, x, y):
        super().__init__(x, y, 22, 22, 25, 1.8, DARK_PURPLE)
        
        # Capacités spéciales
        self.summon_timer = 0
        self.summon_delay = 300  # 5 secondes entre invocations
        self.sacrifice_range = 80  # Distance pour se sacrifier
        self.is_summoning = False
        self.summon_animation = 0
        
        # Comportement en groupe
        self.group_bonus = 1.0
    
    def calculate_group_bonus(self, other_enemies):
        """Calcule le bonus de groupe (plus de cultistes = plus fort)"""
        cultist_count = sum(1 for enemy in other_enemies 
                           if isinstance(enemy, CultistEnemy))
        self.group_bonus = 1.0 + (cultist_count * 0.2)  # +20% par cultiste
    
    def should_sacrifice(self, player):
        """Détermine si le cultiste doit se sacrifier"""
        distance, _, _ = self.get_distance_to_player(player)
        return (distance <= self.sacrifice_range and 
                self.health < self.max_health * 0.3)
    
    def get_distance_to_player(self, player):
        """Calcule la distance au joueur"""
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        return distance, dx, dy
    
    def attempt_sacrifice(self, player):
        """Tentative de sacrifice - damage zone autour du cultiste"""
        self.health = 0  # Se sacrifie
        return True
    
    def try_summon(self):
        """Tentative d'invocation d'un démon mineur"""
        if self.summon_timer <= 0:
            self.summon_timer = self.summon_delay
            self.is_summoning = True
            self.summon_animation = 0
            return True
        return False
    
    def update(self, player, walls, other_enemies=None):
        old_x, old_y = self.x, self.y
        
        # Calculer bonus de groupe
        if other_enemies:
            self.calculate_group_bonus(other_enemies)
        
        # Distance au joueur
        distance, dx, dy = self.get_distance_to_player(player)
        
        # Comportement selon la distance
        if self.should_sacrifice(player):
            # Tentative de sacrifice si blessé et proche
            self.attempt_sacrifice(player)
        else:
            # Mouvement normal vers le joueur avec bonus de groupe
            move_dx, move_dy = PathfindingHelper.get_movement_direction(
                self.x, self.y, player.x, player.y,
                self.width, self.height, walls, self.speed * self.group_bonus
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
        
        # Séparation avec autres ennemis
        self.apply_separation(other_enemies)
        
        # Timer d'invocation
        if self.summon_timer > 0:
            self.summon_timer -= 1
        
        # Animation d'invocation
        if self.is_summoning:
            self.summon_animation += 1
            if self.summon_animation > 60:  # 1 seconde d'animation
                self.is_summoning = False
                self.summon_animation = 0
        
        self.animation_timer += 1
    
    def draw(self, screen):
        # Corps du cultiste
        color = self.color
        if self.is_summoning:
            # Clignotement pendant l'invocation
            flash = (self.summon_animation // 5) % 2
            color = (255, 0, 255) if flash else self.color
        
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        
        # Symbole du chaos au centre
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), 3)
        
        # Cercle d'invocation si en train d'invoquer
        if self.is_summoning:
            circle_radius = int(20 + self.summon_animation * 0.5)
            pygame.draw.circle(screen, (150, 0, 150), (center_x, center_y), circle_radius, 2)
        
        # Barre de vie
        self.draw_health_bar(screen)


class RenegadeMarineEnemy(BaseEnemy):
    """Space Marine Renégat - Ennemi lourd avec charge et résistance"""
    
    def __init__(self, x, y):
        super().__init__(x, y, 30, 30, 80, 0.8, BRONZE)
        
        # Capacités spéciales
        self.charge_cooldown = 0
        self.charge_delay = 240  # 4 secondes entre charges
        self.charge_range = 200
        self.is_charging = False
        self.charge_target_x = 0
        self.charge_target_y = 0
        self.charge_speed = 8
        self.charge_duration = 0
        
        # Résistance aux dégâts
        self.damage_resistance = 0.3  # Réduit 30% des dégâts
    
    def get_distance_to_player(self, player):
        """Calcule la distance au joueur"""
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        return distance, dx, dy
    
    def can_charge(self, player):
        """Détermine si peut charger"""
        distance, _, _ = self.get_distance_to_player(player)
        return (self.charge_cooldown <= 0 and 
                distance <= self.charge_range and 
                distance > 50)
    
    def start_charge(self, player):
        """Démarre une charge vers le joueur"""
        self.is_charging = True
        self.charge_target_x = player.x
        self.charge_target_y = player.y
        self.charge_duration = 40  # Durée de la charge
        self.charge_cooldown = self.charge_delay
    
    def perform_charge(self):
        """Exécute la charge"""
        if self.charge_duration <= 0:
            self.is_charging = False
            return
        
        # Direction vers la cible
        dx = self.charge_target_x - self.x
        dy = self.charge_target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 5:  # Si pas encore arrivé
            dx /= distance
            dy /= distance
            self.update_position(
                self.x + dx * self.charge_speed,
                self.y + dy * self.charge_speed
            )
        
        self.charge_duration -= 1
    
    def update(self, player, walls, other_enemies=None):
        old_x, old_y = self.x, self.y
        
        # Distance au joueur
        distance, dx, dy = self.get_distance_to_player(player)
        
        # Gestion de la charge
        if self.is_charging:
            self.perform_charge()
        elif self.can_charge(player):
            self.start_charge(player)
        else:
            # Mouvement normal (lent mais inexorable)
            move_dx, move_dy = PathfindingHelper.get_movement_direction(
                self.x, self.y, player.x, player.y,
                self.width, self.height, walls, self.speed
            )
            
            self.update_position(self.x + move_dx, self.y + move_dy)
        
        # Séparation avec autres ennemis (plus large pour les marines)
        if other_enemies and not self.is_charging:
            sep_x, sep_y = FlockingBehavior.get_separation_force(self, other_enemies, 50)
            self.x += sep_x * 0.2
            self.y += sep_y * 0.2
            self.rect.x = self.x
            self.rect.y = self.y
        
        # Gestion collisions
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if self.is_charging:
                    # Arrêter la charge si on touche un mur
                    self.is_charging = False
                    self.charge_duration = 0
                self.update_position(old_x, old_y)
                break
        
        # Timers
        if self.charge_cooldown > 0:
            self.charge_cooldown -= 1
        
        self.animation_timer += 1
    
    def take_damage(self, damage):
        """Prend des dégâts avec résistance"""
        reduced_damage = damage * (1 - self.damage_resistance)
        self.health -= reduced_damage
        return self.health <= 0
    
    def draw(self, screen):
        # Corps du marine (plus gros)
        color = self.color
        if self.is_charging:
            # Rouge pendant la charge
            color = CRIMSON
        
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        
        # Armure détaillée
        pygame.draw.rect(screen, (150, 150, 150), 
                        (self.x + 5, self.y + 5, self.width - 10, self.height - 10), 2)
        
        # Indicateur de charge
        if self.charge_cooldown <= 60 and not self.is_charging:  # Prêt à charger
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2
            pygame.draw.circle(screen, (255, 0, 0), (center_x, center_y), 5)
        
        # Effet de charge
        if self.is_charging:
            # Traînée de la charge
            for i in range(5):
                alpha = int(255 * (1 - i / 5))
                trail_surface = pygame.Surface((self.width, self.height))
                trail_surface.set_alpha(alpha)
                trail_surface.fill(CRIMSON)
                trail_x = self.x - (i * 3)
                trail_y = self.y - (i * 3)
                screen.blit(trail_surface, (trail_x, trail_y))
        
        # Barre de vie (plus épaisse pour les marines)
        self.draw_health_bar(screen, bar_height=4, y_offset=-8)


class DaemonEnemy(BaseEnemy):
    """Démon mineur - Téléportation intelligente et attaques psychiques"""
    
    def __init__(self, x, y, is_summoned=False):
        health = 15 if is_summoned else 25
        super().__init__(x, y, 20, 20, health, 2.5, VOID_BLACK)
        
        # Capacités démoniaques
        self.teleport_cooldown = 0
        self.teleport_delay = 240  # 4 secondes
        self.teleport_range = 200  # Distance minimale pour téléporter
        self.is_teleporting = False
        self.teleport_animation = 0
        
        # Attaque psychique
        self.psychic_cooldown = 0
        self.psychic_delay = 150
        self.psychic_range = 100
        
        # Propriétés démoniaques
        self.is_summoned = is_summoned
        self.lifespan = 600 if is_summoned else -1  # 10 secondes si invoqué
        self.phase_timer = 0
        
        # Téléportation intelligente
        self.preferred_distance = 80  # Distance préférée du joueur
        self.last_teleport_time = 0
        self.teleport_attempts = 0
        self.max_teleport_attempts = 3
    
    def get_distance_to_player(self, player):
        """Calcule la distance au joueur"""
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        return distance, dx, dy
    
    def should_teleport(self, distance_to_player):
        """Détermine si le démon devrait téléporter"""
        if self.teleport_cooldown > 0:
            return False
            
        if self.teleport_attempts >= self.max_teleport_attempts:
            return False
            
        if self.last_teleport_time < 180:  # Au moins 3 secondes entre téléportations
            return False
        
        # Téléporter si très loin OU si le joueur est trop proche
        should_teleport = (distance_to_player > self.teleport_range or 
                          distance_to_player < 40)
        
        return should_teleport
    
    def start_teleport(self):
        """Démarre la téléportation"""
        self.is_teleporting = True
        self.teleport_animation = 0
        self.teleport_cooldown = self.teleport_delay
        self.teleport_attempts += 1
        
        # Reset les tentatives après un certain temps
        if self.teleport_attempts >= self.max_teleport_attempts:
            self.teleport_attempts = 0
    
    def is_valid_teleport_position(self, x, y, walls):
        """Vérifie si une position de téléportation est valide"""
        test_rect = pygame.Rect(x, y, self.width, self.height)
        
        # Vérifier qu'on n'est pas dans un mur
        for wall in walls:
            if test_rect.colliderect(wall.rect):
                return False
        
        # Vérifier qu'on n'est pas hors du monde
        if x < 30 or y < 30 or x > 2018 or y > 1506:
            return False
        
        return True
    
    def perform_smart_teleport(self, player, walls):
        """Téléportation intelligente - évite d'être trop proche"""
        attempts = 0
        max_attempts = 10
        
        while attempts < max_attempts:
            # Choisir une position à une distance raisonnable
            angle = random.uniform(0, 2 * math.pi)
            # Distance entre 60 et 120 pixels (ni trop près ni trop loin)
            distance = random.uniform(60, 120)
            
            new_x = player.x + math.cos(angle) * distance
            new_y = player.y + math.sin(angle) * distance
            
            # Vérifier que la position est valide
            if self.is_valid_teleport_position(new_x, new_y, walls):
                self.update_position(new_x, new_y)
                break
            
            attempts += 1
        
        # Si aucune position valide trouvée, téléporter à une position safe
        if attempts >= max_attempts:
            # Téléportation de secours loin du joueur
            safe_angle = random.uniform(0, 2 * math.pi)
            safe_distance = 150
            safe_x = player.x + math.cos(safe_angle) * safe_distance
            safe_y = player.y + math.sin(safe_angle) * safe_distance
            self.update_position(safe_x, safe_y)
        
        self.is_teleporting = False
        self.teleport_animation = 0
        self.last_teleport_time = 0
    
    def try_psychic_attack(self, player):
        """Tentative d'attaque psychique"""
        distance, dx, dy = self.get_distance_to_player(player)
        
        if (self.psychic_cooldown <= 0 and 
            distance <= self.psychic_range and 
            distance >= 30):  # Pas trop proche pour l'attaque psychique
            self.psychic_cooldown = self.psychic_delay
            return True
        return False
    
    def update(self, player, walls, other_enemies=None):
        # Décompte de la durée de vie si invoqué
        if self.is_summoned and self.lifespan > 0:
            self.lifespan -= 1
            if self.lifespan <= 0:
                self.health = 0
                return
        
        old_x, old_y = self.x, self.y
        
        # Distance au joueur
        distance, dx, dy = self.get_distance_to_player(player)
        
        # Gestion de la téléportation
        if self.is_teleporting:
            self.teleport_animation += 1
            if self.teleport_animation > 45:  # Animation plus longue
                self.perform_smart_teleport(player, walls)
        elif self.should_teleport(distance):
            self.start_teleport()
        else:
            # Mouvement normal mais moins agressif
            if distance > self.preferred_distance:
                # S'approcher si trop loin
                move_dx, move_dy = PathfindingHelper.get_movement_direction(
                    self.x, self.y, player.x, player.y,
                    self.width, self.height, walls, self.speed
                )
            else:
                # Rester à distance et tourner autour
                angle = math.atan2(dy, dx) + 1.5  # Mouvement circulaire
                target_x = player.x + math.cos(angle) * self.preferred_distance
                target_y = player.y + math.sin(angle) * self.preferred_distance
                
                move_dx, move_dy = PathfindingHelper.get_movement_direction(
                    self.x, self.y, target_x, target_y,
                    self.width, self.height, walls, self.speed * 0.7
                )
            
            self.update_position(self.x + move_dx, self.y + move_dy)
        
        # Gestion collisions (phase réduite)
        if not self.is_teleporting:
            for wall in walls:
                if self.rect.colliderect(wall.rect):
                    # 20% de chance d'ignorer les murs (réduit de 30%)
                    if random.random() > 0.2:
                        self.update_position(old_x, old_y)
                    break
        
        # Timers
        if self.teleport_cooldown > 0:
            self.teleport_cooldown -= 1
        if self.psychic_cooldown > 0:
            self.psychic_cooldown -= 1
        
        self.phase_timer += 1
        self.last_teleport_time += 1
        self.animation_timer += 1
    
    def draw(self, screen):
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        if self.is_teleporting:
            # Effet de téléportation plus visible
            alpha = int(255 * (1 - self.teleport_animation / 45))
            demon_surface = pygame.Surface((self.width * 2, self.height * 2))
            demon_surface.set_alpha(alpha)
            demon_surface.fill(self.color)
            screen.blit(demon_surface, (self.x - self.width//2, self.y - self.height//2))
            
            # Particules de téléportation plus visibles
            for i in range(12):
                angle = (i / 12) * 2 * math.pi + self.teleport_animation * 0.3
                radius = 25 + self.teleport_animation
                particle_x = center_x + math.cos(angle) * radius
                particle_y = center_y + math.sin(angle) * radius
                particle_size = max(1, 4 - self.teleport_animation // 10)
                pygame.draw.circle(screen, (200, 0, 200), 
                                 (int(particle_x), int(particle_y)), particle_size)
            
            # Texte d'avertissement
            if self.teleport_animation < 30:
                font = pygame.font.Font(None, 24)
                warning_text = font.render("TÉLÉPORTATION", True, (255, 255, 0))
                text_rect = warning_text.get_rect(center=(center_x, self.y - 20))
                screen.blit(warning_text, text_rect)
        else:
            # Corps du démon avec effet de phase
            phase_offset = math.sin(self.phase_timer * 0.1) * 1
            demon_rect = (self.x + phase_offset, self.y, self.width, self.height)
            pygame.draw.rect(screen, self.color, demon_rect)
            
            # Aura démoniaque moins agressive
            aura_radius = int(12 + math.sin(self.phase_timer * 0.05) * 2)
            
            aura_surface = pygame.Surface((aura_radius * 2, aura_radius * 2))
            aura_surface.set_alpha(30)  # Moins opaque
            pygame.draw.circle(aura_surface, (150, 0, 150), 
                             (aura_radius, aura_radius), aura_radius)
            screen.blit(aura_surface, (center_x - aura_radius, center_y - aura_radius))
            
            # Yeux brillants
            eye_y = self.y + 6
            pygame.draw.circle(screen, (255, 0, 0), (int(self.x + 6), int(eye_y)), 2)
            pygame.draw.circle(screen, (255, 0, 0), (int(self.x + 14), int(eye_y)), 2)
            
            # Indicateur de téléportation imminente
            if self.teleport_cooldown <= 30 and not self.is_teleporting:
                warning_radius = int(10 + (30 - self.teleport_cooldown) * 0.5)
                pygame.draw.circle(screen, (255, 255, 0), (center_x, center_y), warning_radius, 2)
        
        # Barre de vie
        if not self.is_teleporting:
            self.draw_health_bar(screen, bar_height=2, y_offset=-5)
            
            # Indicateur de durée de vie si invoqué
            if self.is_summoned and self.lifespan > 0:
                life_ratio = self.lifespan / 600
                life_width = int(self.width * life_ratio)
                pygame.draw.rect(screen, (255, 255, 0), (self.x, self.y - 8, life_width, 1))