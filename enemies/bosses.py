"""
Boss épiques du jeu Warhammer 40K
ChaosSorcererBoss, InquisitorLordBoss, DaemonPrinceBoss - Ennemis de fin de niveau
"""

import pygame
import math
import random
from bullet import Bullet
from pathfinding import PathfindingHelper, FlockingBehavior
from .base_enemy import BaseBoss

# Couleurs pour les boss
CHAOS_RED = (139, 0, 0)
IMPERIAL_GOLD = (255, 215, 0)
DAEMON_PURPLE = (75, 0, 130)
SAINT_WHITE = (248, 248, 255)
MARINE_BLUE = (25, 25, 112)


class ChaosSorcererBoss(BaseBoss):
    """Boss Sorcier du Chaos - Téléportation, invocations, et sorts dévastateurs"""
    
    def __init__(self, x, y):
        super().__init__(x, y, 48, 48, 350, 1.5, CHAOS_RED, "SORCIER DU CHAOS")
        
        # Seuils de phases
        self.phase_thresholds = [250, 100]  # Phase 2 à 250 HP, Phase 3 à 100 HP
        
        # Capacités spéciales - Initialisation des timers
        self.ability_timers = {
            'teleport': 0,
            'summon': 0,
            'area_attack': 0,
            'barrage': 0
        }
        
        # Delays des capacités
        self.ability_delays = {
            'teleport': 180,  # 3 secondes
            'summon': 300,    # 5 secondes
            'area_attack': 240,  # 4 secondes
            'barrage': 150    # 2.5 secondes
        }
        
        # États des capacités
        self.is_teleporting = False
        self.teleport_animation = 0
        self.is_casting_area = False
        self.area_cast_timer = 0
        self.max_summons = 4
        self.current_summons = 0
        
        # Propriétés visuelles
        self.rage_mode = False
    
    def on_phase_change(self, new_phase):
        """Appelé lors d'un changement de phase"""
        super().on_phase_change(new_phase)
        
        if new_phase == 2:
            self.become_more_aggressive()
            self.rage_mode = True
            print("🔥 PHASE 2: Le Sorcier entre en rage !")
        elif new_phase == 3:
            self.become_berserk()
            print("💀 PHASE 3: BERSERK ! Le Sorcier est désespéré !")
    
    def become_more_aggressive(self):
        """Phase 2: Plus agressif"""
        self.ability_delays['teleport'] = 120  # Téléporte plus souvent
        self.ability_delays['summon'] = 200    # Invoque plus souvent
        self.ability_delays['area_attack'] = 180  # Attaque de zone plus fréquente
        self.speed = 2.0
    
    def become_berserk(self):
        """Phase 3: Berserk"""
        self.ability_delays['teleport'] = 80
        self.ability_delays['summon'] = 150
        self.ability_delays['area_attack'] = 120
        self.ability_delays['barrage'] = 100
        self.speed = 2.5
        self.damage_resistance = 0.4  # Plus résistant quand blessé
    
    def get_distance_to_player(self, player):
        """Calcule la distance au joueur"""
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        return distance, dx, dy
    
    def tactical_retreat(self, player, walls):
        """Recule intelligemment du joueur"""
        distance, dx, dy = self.get_distance_to_player(player)
        if distance > 0:
            dx /= distance
            dy /= distance
        
        # Direction opposée
        retreat_dx = -dx
        retreat_dy = -dy
        
        move_dx, move_dy = PathfindingHelper.get_movement_direction(
            self.x, self.y, self.x + retreat_dx * 100, self.y + retreat_dy * 100,
            self.width, self.height, walls, self.speed
        )
        self.update_position(self.x + move_dx, self.y + move_dy)
    
    def move_towards_player(self, player, walls):
        """Se rapproche du joueur"""
        move_dx, move_dy = PathfindingHelper.get_movement_direction(
            self.x, self.y, player.x, player.y,
            self.width, self.height, walls, self.speed * 0.7
        )
        self.update_position(self.x + move_dx, self.y + move_dy)
    
    def circle_player(self, player, walls):
        """Tourne autour du joueur"""
        distance, dx, dy = self.get_distance_to_player(player)
        if distance > 0:
            angle = math.atan2(dy, dx)
            angle += 1.2  # Mouvement circulaire
            
            target_distance = 120
            target_x = player.x + math.cos(angle) * target_distance
            target_y = player.y + math.sin(angle) * target_distance
            
            move_dx, move_dy = PathfindingHelper.get_movement_direction(
                self.x, self.y, target_x, target_y,
                self.width, self.height, walls, self.speed
            )
            self.update_position(self.x + move_dx, self.y + move_dy)
    
    def handle_teleportation(self, player):
        """Gère l'animation de téléportation"""
        self.teleport_animation += 1
        if self.teleport_animation > 60:
            self.perform_boss_teleport(player)
    
    def perform_boss_teleport(self, player):
        """Téléportation tactique du boss"""
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(100, 150)
        
        new_x = player.x + math.cos(angle) * distance
        new_y = player.y + math.sin(angle) * distance
        
        # S'assurer que c'est dans les limites du monde
        new_x = max(50, min(1998, new_x))
        new_y = max(50, min(1486, new_y))
        
        self.update_position(new_x, new_y)
        self.is_teleporting = False
        self.teleport_animation = 0
        self.invulnerable_timer = 30  # 0.5 seconde d'invulnérabilité
    
    def handle_area_cast(self):
        """Gère l'incantation de l'attaque de zone"""
        self.area_cast_timer += 1
        if self.area_cast_timer >= 120:  # 2 secondes de cast
            self.is_casting_area = False
            self.area_cast_timer = 0
            return True  # Signal pour déclencher l'attaque
        return False
    
    def try_teleport(self):
        """Tentative de téléportation"""
        if self.can_use_ability('teleport') and not self.is_teleporting:
            self.is_teleporting = True
            self.teleport_animation = 0
            self.use_ability('teleport', self.ability_delays['teleport'])
            return True
        return False
    
    def try_summon_daemon(self):
        """Tentative d'invocation de démon"""
        if (self.can_use_ability('summon') and 
            self.current_summons < self.max_summons):
            self.use_ability('summon', self.ability_delays['summon'])
            self.current_summons += 1
            return True
        return False
    
    def try_area_attack(self, player):
        """Tentative d'attaque de zone"""
        if self.can_use_ability('area_attack') and not self.is_casting_area:
            self.is_casting_area = True
            self.area_cast_timer = 0
            self.use_ability('area_attack', self.ability_delays['area_attack'])
            return True
        return False
    
    def try_projectile_barrage(self, player):
        """Tentative de barrage de projectiles"""
        if self.can_use_ability('barrage'):
            self.use_ability('barrage', self.ability_delays['barrage'])
            return True
        return False
    
    def on_summon_death(self):
        """Appelé quand un de ses démons meurt"""
        self.current_summons -= 1
    
    def update(self, player, walls, other_enemies=None):
        """Mise à jour du boss sorcier"""
        super().update(player, walls, other_enemies)
        
        # Distance au joueur
        distance, dx, dy = self.get_distance_to_player(player)
        
        # Comportement selon la phase et la distance
        if self.is_teleporting:
            self.handle_teleportation(player)
        elif self.is_casting_area:
            self.handle_area_cast()
        else:
            # Mouvement tactique
            if distance < 80:  # Trop proche, reculer
                self.tactical_retreat(player, walls)
            elif distance > 200:  # Trop loin, se rapprocher
                self.move_towards_player(player, walls)
            else:  # Distance idéale, tourner autour
                self.circle_player(player, walls)
    
    def draw(self, screen):
        # Corps du sorcier
        color = self.color
        if self.rage_mode:
            # Clignotement rouge en mode rage
            flash = (self.animation_timer // 10) % 2
            color = (255, 0, 0) if flash else self.color
        
        if self.is_teleporting:
            # Effet de téléportation
            alpha = int(255 * (1 - self.teleport_animation / 60))
            boss_surface = pygame.Surface((self.width * 2, self.height * 2))
            boss_surface.set_alpha(alpha)
            boss_surface.fill(color)
            screen.blit(boss_surface, (self.x - self.width//2, self.y - self.height//2))
            
            # Particules de téléportation
            for i in range(16):
                angle = (i / 16) * 2 * math.pi + self.teleport_animation * 0.2
                radius = 30 + self.teleport_animation
                particle_x = self.x + self.width//2 + math.cos(angle) * radius
                particle_y = self.y + self.height//2 + math.sin(angle) * radius
                pygame.draw.circle(screen, (255, 0, 255), (int(particle_x), int(particle_y)), 3)
        else:
            # Corps normal
            pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
            
            # Ornements du sorcier
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2
            
            # Robe + Staff
            pygame.draw.rect(screen, (100, 0, 100), 
                           (self.x + 8, self.y + 8, self.width - 16, self.height - 16))
            pygame.draw.circle(screen, (255, 215, 0), (center_x, center_y), 8)
            
            # Aura de puissance
            aura_radius = int(25 + math.sin(self.animation_timer * 0.1) * 5)
            aura_surface = pygame.Surface((aura_radius * 2, aura_radius * 2))
            aura_intensity = 30 if self.phase == 1 else 50 if self.phase == 2 else 80
            aura_surface.set_alpha(aura_intensity)
            aura_color = (150, 0, 150) if self.phase < 3 else (255, 0, 0)
            pygame.draw.circle(aura_surface, aura_color, 
                             (aura_radius, aura_radius), aura_radius)
            screen.blit(aura_surface, (center_x - aura_radius, center_y - aura_radius))
        
        # Indicateur d'incantation
        if self.is_casting_area:
            cast_progress = self.area_cast_timer / 120
            self.draw_casting_indicator(screen, "SORT PUISSANT !", cast_progress, 80, (255, 255, 0))
        
        # Barre de vie du boss
        self.draw_boss_health_bar(screen)


class InquisitorLordBoss(BaseBoss):
    """Boss Seigneur Inquisiteur - Purification, benedictions et justice impériale"""
    
    def __init__(self, x, y):
        super().__init__(x, y, 45, 45, 280, 2.0, IMPERIAL_GOLD, "SEIGNEUR INQUISITEUR")
        
        # Système de phases
        self.phase_thresholds = [140]  # Phase 2 à 50% de vie
        
        # Capacités impériales
        self.ability_timers = {
            'purification': 0,
            'blessed_shot': 0,
            'charge': 0,
            'shield': 0
        }
        
        self.ability_delays = {
            'purification': 360,  # 6 secondes - Très puissant
            'blessed_shot': 60,   # 1 seconde
            'charge': 240,        # 4 secondes
            'shield': 300         # 5 secondes
        }
        
        # États des capacités
        self.is_purifying = False
        self.purification_timer = 0
        self.is_charging = False
        self.charge_target_x = 0
        self.charge_target_y = 0
        self.charge_duration = 0
        self.shield_active = False
        self.shield_duration = 0
        
        # Animation
        self.righteous_fury = False  # S'active quand PV bas
        
        # Résistance morale
        self.damage_resistance = 0.15
    
    def on_phase_change(self, new_phase):
        """Appelé lors d'un changement de phase"""
        super().on_phase_change(new_phase)
        
        if new_phase == 2:
            self.become_righteous()
            print("⚡ COLÈRE SAINTE ! L'Inquisiteur devient redoutable !")
    
    def become_righteous(self):
        """Mode colère sainte"""
        self.righteous_fury = True
        self.speed = 3.0
        self.ability_delays['purification'] = 240  # Plus fréquent
        self.ability_delays['blessed_shot'] = 40   # Tir plus rapide
        self.ability_delays['charge'] = 180
        self.damage_resistance = 0.3   # Plus résistant
    
    def get_distance_to_player(self, player):
        """Calcule la distance au joueur"""
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        return distance, dx, dy
    
    def advance_on_heretic(self, player, walls):
        """Avance inexorablement vers l'hérétique"""
        move_dx, move_dy = PathfindingHelper.get_movement_direction(
            self.x, self.y, player.x, player.y,
            self.width, self.height, walls, self.speed
        )
        self.update_position(self.x + move_dx, self.y + move_dy)
    
    def maintain_firing_distance(self, player, walls):
        """Maintient une distance de tir optimale"""
        distance, dx, dy = self.get_distance_to_player(player)
        if distance > 0:
            # Mouvement en crabe pour rester à distance
            angle = math.atan2(dy, dx)
            angle += 1.0  # Mouvement latéral
            
            move_x = math.cos(angle) * self.speed * 0.8
            move_y = math.sin(angle) * self.speed * 0.8
            
            old_x, old_y = self.x, self.y
            self.update_position(self.x + move_x, self.y + move_y)
            
            # Vérifier collisions
            for wall in walls:
                if self.rect.colliderect(wall.rect):
                    self.update_position(old_x, old_y)
                    break
    
    def handle_purification(self):
        """Gère l'incantation de purification"""
        self.purification_timer += 1
        if self.purification_timer >= 150:  # 2.5 secondes de cast
            self.is_purifying = False
            self.purification_timer = 0
            return True  # Signal pour déclencher la purification
        return False
    
    def handle_charge(self):
        """Gère la charge sainte"""
        if self.charge_duration <= 0:
            self.is_charging = False
            return
        
        # Direction vers la cible
        dx = self.charge_target_x - self.x
        dy = self.charge_target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 5:
            dx /= distance
            dy /= distance
            charge_speed = 6
            self.update_position(
                self.x + dx * charge_speed,
                self.y + dy * charge_speed
            )
        
        self.charge_duration -= 1
    
    def try_charge(self, player):
        """Tentative de charge"""
        if self.can_use_ability('charge') and not self.is_charging:
            self.is_charging = True
            self.charge_target_x = player.x
            self.charge_target_y = player.y
            self.charge_duration = 30
            self.use_ability('charge', self.ability_delays['charge'])
            return True
        return False
    
    def try_purification(self):
        """Tentative de purification"""
        if self.can_use_ability('purification') and not self.is_purifying:
            self.is_purifying = True
            self.purification_timer = 0
            self.use_ability('purification', self.ability_delays['purification'])
            return True
        return False
    
    def try_blessed_shots(self, player):
        """Tentative de tirs bénis"""
        if self.can_use_ability('blessed_shot'):
            self.use_ability('blessed_shot', self.ability_delays['blessed_shot'])
            return True
        return False
    
    def try_activate_shield(self):
        """Tentative d'activation du bouclier de foi"""
        if self.can_use_ability('shield') and not self.shield_active:
            self.shield_active = True
            self.shield_duration = 180  # 3 secondes
            self.use_ability('shield', self.ability_delays['shield'])
            return True
        return False
    
    def update_shield(self):
        """Met à jour le bouclier de foi"""
        if self.shield_duration > 0:
            self.shield_duration -= 1
        else:
            self.shield_active = False
    
    def take_damage(self, damage):
        """Prend des dégâts avec résistance et bouclier"""
        if self.invulnerable_timer > 0:
            return False
        
        # Bouclier de foi
        if self.shield_active:
            damage *= 0.3  # Réduit 70% des dégâts
        
        # Résistance de base
        reduced_damage = damage * (1 - self.damage_resistance)
        self.health -= reduced_damage
        
        # Chance d'activer le bouclier quand blessé
        if self.health < self.max_health * 0.5 and random.random() < 0.4:
            self.try_activate_shield()
        
        self.check_phase_transition()
        return self.health <= 0
    
    def update(self, player, walls, other_enemies=None):
        """Mise à jour de l'Inquisiteur"""
        super().update(player, walls, other_enemies)
        
        # Distance au joueur
        distance, dx, dy = self.get_distance_to_player(player)
        
        # Comportement selon l'état
        if self.is_purifying:
            self.handle_purification()
        elif self.is_charging:
            self.handle_charge()
        else:
            # Mouvement tactique de l'Inquisiteur
            if distance < 60:  # Distance de mêlée
                self.try_charge(player)
            elif distance > 150:  # Trop loin
                self.advance_on_heretic(player, walls)
            else:  # Distance de tir
                self.maintain_firing_distance(player, walls)
        
        # Mise à jour du bouclier
        self.update_shield()
    
    def draw(self, screen):
        # Corps de l'Inquisiteur
        color = self.color
        if self.righteous_fury:
            # Aura dorée en mode colère
            flash = (self.animation_timer // 8) % 2
            color = (255, 255, 200) if flash else self.color
        
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        
        # Ornements impériaux
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        # Armure détaillée
        pygame.draw.rect(screen, (200, 200, 200), 
                        (self.x + 5, self.y + 5, self.width - 10, self.height - 10), 3)
        
        # Symbole de l'Inquisition (Crâne)
        pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), 8)
        pygame.draw.circle(screen, (0, 0, 0), (center_x - 3, center_y - 2), 2)
        pygame.draw.circle(screen, (0, 0, 0), (center_x + 3, center_y - 2), 2)
        
        # Bouclier de foi
        if self.shield_active:
            shield_radius = int(30 + math.sin(self.animation_timer * 0.2) * 3)
            shield_surface = pygame.Surface((shield_radius * 2, shield_radius * 2))
            shield_surface.set_alpha(80)
            pygame.draw.circle(shield_surface, (255, 255, 200), 
                             (shield_radius, shield_radius), shield_radius)
            screen.blit(shield_surface, (center_x - shield_radius, center_y - shield_radius))
            
            # Bordure du bouclier
            pygame.draw.circle(screen, (255, 215, 0), (center_x, center_y), shield_radius, 2)
        
        # Aura de purification
        if self.is_purifying:
            purif_progress = self.purification_timer / 150
            self.draw_casting_indicator(screen, "PURIFICATION !", purif_progress, 120, (255, 255, 0))
            
            # Rayons de purification
            warning_radius = int(120 + purif_progress * 80)
            for i in range(8):
                angle = (i / 8) * 2 * math.pi + self.purification_timer * 0.1
                end_x = center_x + math.cos(angle) * warning_radius
                end_y = center_y + math.sin(angle) * warning_radius
                pygame.draw.line(screen, (255, 255, 200), 
                               (center_x, center_y), (end_x, end_y), 3)
        
        # Effet de charge
        if self.is_charging:
            # Traînée de charge dorée
            for i in range(8):
                trail_alpha = int(255 * (1 - i / 8))
                trail_surface = pygame.Surface((self.width, self.height))
                trail_surface.set_alpha(trail_alpha)
                trail_surface.fill((255, 215, 0))
                trail_x = self.x - (i * 3)
                trail_y = self.y - (i * 3)
                screen.blit(trail_surface, (trail_x, trail_y))
        
        # Barre de vie du boss
        self.draw_boss_health_bar(screen)


class DaemonPrinceBoss(BaseBoss):
    """Boss Prince Daemon - Boss ultime de corruption avec pouvoirs chaotiques"""
    
    def __init__(self, x, y):
        super().__init__(x, y, 64, 64, 500, 1.8, DAEMON_PURPLE, "PRINCE DAEMON")
        
        # Système de phases
        self.phase_thresholds = [200]  # Transformation à 40% PV
        
        # Pouvoirs du chaos
        self.ability_timers = {
            'warp_storm': 0,
            'chaos_teleport': 0,
            'corruption_wave': 0,
            'mass_summon': 0
        }
        
        self.ability_delays = {
            'warp_storm': 480,    # 8 secondes - Attaque dévastatrice
            'chaos_teleport': 120,  # 2 secondes
            'corruption_wave': 200,  # 3.33 secondes
            'mass_summon': 600    # 10 secondes
        }
        
        # États des capacités
        self.is_summoning_storm = False
        self.storm_cast_timer = 0
        self.is_teleporting = False
        self.teleport_animation = 0
        self.total_summons = 0
        self.max_total_summons = 8
        
        # Régénération chaotique
        self.regeneration_timer = 0
        self.regen_rate = 0.1  # Régénère lentement
        
        # Transformation
        self.chaos_form = 1  # Forme 1: Normal, 2: Transformé
        self.transformation_threshold = 200  # Se transforme à 40% PV
        
        # Résistance massive
        self.damage_resistance = 0.3
    
    def on_phase_change(self, new_phase):
        """Appelé lors d'un changement de phase"""
        super().on_phase_change(new_phase)
        
        if new_phase == 2:
            self.transform_to_greater_daemon()
    
    def transform_to_greater_daemon(self):
        """Transformation en forme supérieure"""
        self.chaos_form = 2
        old_center_x = self.x + self.width // 2
        old_center_y = self.y + self.height // 2
        
        self.width = 80
        self.height = 80
        self.speed = 2.5
        self.damage_resistance = 0.5  # Encore plus résistant
        self.regen_rate = 0.2  # Régénère plus vite
        
        # Recentrer après transformation
        self.update_position(
            old_center_x - self.width // 2,
            old_center_y - self.height // 2
        )
        
        # Capacités améliorées
        self.ability_delays['warp_storm'] = 300  # Plus fréquent
        self.ability_delays['chaos_teleport'] = 80
        self.ability_delays['corruption_wave'] = 150
        
        print("💀🔥 LE PRINCE DAEMON SE TRANSFORME ! FORME ULTIME !")
    
    def handle_regeneration(self):
        """Régénération chaotique"""
        self.regeneration_timer += 1
        if self.regeneration_timer >= 60:  # Chaque seconde
            if self.health < self.max_health:
                self.health += self.regen_rate * self.max_health
                self.health = min(self.health, self.max_health)
            self.regeneration_timer = 0
    
    def get_distance_to_player(self, player):
        """Calcule la distance au joueur"""
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        return distance, dx, dy
    
    def chaotic_movement(self, player, walls, distance):
        """Mouvement chaotique et imprévisible"""
        if distance < 80:  # Combat rapproché - plus agressif
            self.aggressive_pursuit(player, walls)
        elif distance > 200:  # Trop loin - téléporter ou charger
            if random.random() < 0.3:
                self.try_chaos_teleport()
            else:
                self.charge_towards_player(player, walls)
        else:  # Distance moyenne - mouvement erratique
            self.erratic_movement(player, walls)
    
    def aggressive_pursuit(self, player, walls):
        """Poursuite agressive"""
        move_dx, move_dy = PathfindingHelper.get_movement_direction(
            self.x, self.y, player.x, player.y,
            self.width, self.height, walls, self.speed * 1.2
        )
        self.update_position(self.x + move_dx, self.y + move_dy)
    
    def charge_towards_player(self, player, walls):
        """Charge brutale vers le joueur"""
        move_dx, move_dy = PathfindingHelper.get_movement_direction(
            self.x, self.y, player.x, player.y,
            self.width, self.height, walls, self.speed * 1.5
        )
        self.update_position(self.x + move_dx, self.y + move_dy)
    
    def erratic_movement(self, player, walls):
        """Mouvement erratique et chaotique"""
        # Mélange de poursuite et de mouvement aléatoire
        random_offset_x = random.randint(-60, 60)
        random_offset_y = random.randint(-60, 60)
        
        target_x = player.x + random_offset_x
        target_y = player.y + random_offset_y
        
        move_dx, move_dy = PathfindingHelper.get_movement_direction(
            self.x, self.y, target_x, target_y,
            self.width, self.height, walls, self.speed
        )
        self.update_position(self.x + move_dx, self.y + move_dy)
    
    def handle_warp_storm(self):
        """Gère l'incantation de la tempête warp"""
        self.storm_cast_timer += 1
        if self.storm_cast_timer >= 180:  # 3 secondes de cast
            self.is_summoning_storm = False
            self.storm_cast_timer = 0
            return True  # Signal pour déclencher la tempête
        return False
    
    def handle_chaos_teleportation(self, player):
        """Téléportation chaotique"""
        self.teleport_animation += 1
        if self.teleport_animation > 40:
            self.perform_chaos_teleport(player)
    
    def perform_chaos_teleport(self, player):
        """Téléportation avec effet chaotique"""
        # Téléportation plus agressive que les démons normaux
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(40, 100)  # Plus proche que les autres
        
        new_x = player.x + math.cos(angle) * distance
        new_y = player.y + math.sin(angle) * distance
        
        # Assurer les limites
        new_x = max(80, min(1968, new_x))
        new_y = max(80, min(1456, new_y))
        
        self.update_position(new_x, new_y)
        self.is_teleporting = False
        self.teleport_animation = 0
    
    def try_chaos_teleport(self):
        """Tentative de téléportation chaotique"""
        if self.can_use_ability('chaos_teleport') and not self.is_teleporting:
            self.is_teleporting = True
            self.teleport_animation = 0
            self.use_ability('chaos_teleport', self.ability_delays['chaos_teleport'])
            return True
        return False
    
    def try_warp_storm(self):
        """Tentative de tempête warp"""
        if self.can_use_ability('warp_storm') and not self.is_summoning_storm:
            self.is_summoning_storm = True
            self.storm_cast_timer = 0
            self.use_ability('warp_storm', self.ability_delays['warp_storm'])
            return True
        return False
    
    def try_corruption_wave(self):
        """Tentative de vague de corruption"""
        if self.can_use_ability('corruption_wave'):
            self.use_ability('corruption_wave', self.ability_delays['corruption_wave'])
            return True
        return False
    
    def try_mass_summon(self):
        """Tentative d'invocation massive"""
        if (self.can_use_ability('mass_summon') and 
            self.total_summons < self.max_total_summons):
            self.use_ability('mass_summon', self.ability_delays['mass_summon'])
            return True
        return False
    
    def take_damage(self, damage):
        """Prend des dégâts avec résistance massive"""
        if self.invulnerable_timer > 0:
            return False
        
        reduced_damage = damage * (1 - self.damage_resistance)
        self.health -= reduced_damage
        
        # Réaction chaotique aux dégâts
        if random.random() < 0.4:
            if random.random() < 0.5:
                self.try_chaos_teleport()
            else:
                self.try_corruption_wave()
        
        self.check_phase_transition()
        return self.health <= 0
    
    def on_summon_death(self):
        """Appelé quand une invocation meurt"""
        self.total_summons -= 1
    
    def update(self, player, walls, other_enemies=None):
        """Mise à jour du Prince Daemon"""
        super().update(player, walls, other_enemies)
        
        # Régénération
        self.handle_regeneration()
        
        # Distance au joueur
        distance, dx, dy = self.get_distance_to_player(player)
        
        # Comportement selon l'état
        if self.is_summoning_storm:
            self.handle_warp_storm()
        elif self.is_teleporting:
            self.handle_chaos_teleportation(player)
        else:
            # Mouvement chaotique et imprévisible
            self.chaotic_movement(player, walls, distance)
    
    def draw(self, screen):
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        if self.is_teleporting:
            # Effet de téléportation chaotique
            alpha = int(255 * (1 - self.teleport_animation / 40))
            chaos_surface = pygame.Surface((self.width * 3, self.height * 3))
            chaos_surface.set_alpha(alpha)
            
            # Distorsion chaotique
            for i in range(20):
                color = (random.randint(100, 255), 0, random.randint(100, 255))
                size = random.randint(5, 15)
                offset_x = random.randint(-self.width, self.width)
                offset_y = random.randint(-self.height, self.height)
                pygame.draw.circle(chaos_surface, color, 
                                 (self.width + offset_x, self.height + offset_y), size)
            
            screen.blit(chaos_surface, (self.x - self.width, self.y - self.height))
        else:
            # Corps du Prince Daemon
            form_color = self.color if self.chaos_form == 1 else (100, 0, 100)
            
            # Effet de distorsion permanente
            distortion_offset = math.sin(self.animation_timer * 0.1) * 2
            daemon_rect = (self.x + distortion_offset, self.y, self.width, self.height)
            pygame.draw.rect(screen, form_color, daemon_rect)
            
            # Ornements daemoniques
            if self.chaos_form == 2:
                # Forme transformée - plus imposante
                pygame.draw.rect(screen, (150, 0, 150), 
                               (self.x + 10, self.y + 10, self.width - 20, self.height - 20))
                
                # Cornes
                horn_points = [
                    (center_x - 15, self.y + 10),
                    (center_x - 20, self.y - 10),
                    (center_x - 10, self.y)
                ]
                pygame.draw.polygon(screen, (200, 0, 0), horn_points)
                
                horn_points_2 = [
                    (center_x + 15, self.y + 10),
                    (center_x + 20, self.y - 10),
                    (center_x + 10, self.y)
                ]
                pygame.draw.polygon(screen, (200, 0, 0), horn_points_2)
            
            # Aura chaotique massive
            aura_radius = int(40 + math.sin(self.animation_timer * 0.08) * 8)
            if self.chaos_form == 2:
                aura_radius += 20
            
            # Multiples auras chaotiques
            for i in range(3):
                aura_surface = pygame.Surface(((aura_radius + i*10) * 2, (aura_radius + i*10) * 2))
                alpha = 40 - i*10
                aura_surface.set_alpha(alpha)
                
                colors = [(150, 0, 150), (200, 0, 200), (100, 0, 100)]
                pygame.draw.circle(aura_surface, colors[i], 
                                 (aura_radius + i*10, aura_radius + i*10), aura_radius + i*10)
                
                screen.blit(aura_surface, 
                           (center_x - aura_radius - i*10, center_y - aura_radius - i*10))
        
        # Tempête Warp
        if self.is_summoning_storm:
            storm_progress = self.storm_cast_timer / 180
            self.draw_casting_indicator(screen, "TEMPÊTE WARP !", storm_progress, 150, (255, 0, 255))
            
            # Éclairs chaotiques
            storm_radius = int(150 + storm_progress * 100)
            for i in range(12):
                angle = random.uniform(0, 2 * math.pi)
                length = random.uniform(storm_radius * 0.5, storm_radius)
                end_x = center_x + math.cos(angle) * length
                end_y = center_y + math.sin(angle) * length
                
                lightning_color = (random.randint(200, 255), 0, random.randint(200, 255))
                pygame.draw.line(screen, lightning_color, (center_x, center_y), (end_x, end_y), 4)
        
        # Barre de vie massive
        self.draw_boss_health_bar(screen)
        
        # Indicateur de régénération
        if self.regeneration_timer > 30:
            font = pygame.font.Font(None, 24)
            regen_text = font.render("RÉGÉNÉRATION", True, (150, 255, 150))
            regen_rect = regen_text.get_rect(center=(center_x, self.y + self.height + 20))
            screen.blit(regen_text, regen_rect)