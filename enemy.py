import pygame
import math
import random
from bullet import Bullet
from pathfinding import PathfindingHelper, FlockingBehavior

# Couleurs
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)
DARK_RED = (100, 0, 0)

class BasicEnemy:
    """Ennemi basique qui suit le joueur"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 24
        self.height = 24
        self.speed = 2
        self.health = 30
        self.max_health = 30
        self.color = BLUE
        
        # Rectangle pour les collisions
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # Timer pour éviter de rester collé aux murs
        self.stuck_timer = 0
        self.last_pos = (x, y)
    
    def update(self, player, walls, other_enemies=None):
        # Sauvegarder position actuelle
        old_x, old_y = self.x, self.y
        
        # Pathfinding intelligent vers le joueur
        move_dx, move_dy = PathfindingHelper.get_movement_direction(
            self.x, self.y, player.x, player.y,
            self.width, self.height, walls, self.speed
        )
        
        # Force de séparation avec autres ennemis (éviter superposition)
        if other_enemies:
            sep_x, sep_y = FlockingBehavior.get_separation_force(self, other_enemies)
            move_dx += sep_x * 0.5  # Pondération de la force de séparation
            move_dy += sep_y * 0.5
        
        # Appliquer le mouvement
        self.x += move_dx
        self.y += move_dy
        
        # Mettre à jour le rectangle
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Vérification finale des collisions (sécurité)
        collision_detected = False
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                collision_detected = True
                break
        
        if collision_detected:
            # Utiliser wall sliding comme dernier recours
            self.x, self.y = old_x, old_y
            slide_dx, slide_dy = PathfindingHelper.wall_slide(
                old_x, old_y, move_dx, move_dy, 
                self.width, self.height, walls
            )
            self.x += slide_dx
            self.y += slide_dy
            self.rect.x = self.x
            self.rect.y = self.y
        
        # Réinitialiser le timer de blocage si on bouge
        if abs(self.x - self.last_pos[0]) > 1 or abs(self.y - self.last_pos[1]) > 1:
            self.stuck_timer = 0
        else:
            self.stuck_timer += 1
            
        # Si vraiment bloqué longtemps, téléportation d'urgence
        if self.stuck_timer > 120:  # 2 secondes
            new_x, new_y = PathfindingHelper.find_free_spawn_position(
                2048, 1536, self.width, self.height, walls, player, 50
            )
            self.x, self.y = new_x, new_y
            self.rect.x, self.rect.y = self.x, self.y
            self.stuck_timer = 0
        
        self.last_pos = (self.x, self.y)
    
    def take_damage(self, damage):
        """L'ennemi prend des dégâts"""
        self.health -= damage
        return self.health <= 0  # Retourne True si mort
    
    def draw(self, screen):
        # Dessiner l'ennemi
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
        # Barre de vie
        bar_width = self.width
        bar_height = 3
        health_ratio = self.health / self.max_health
        
        # Fond de la barre
        pygame.draw.rect(screen, DARK_RED, 
                        (self.x, self.y - 6, bar_width, bar_height))
        # Barre de vie
        pygame.draw.rect(screen, GREEN, 
                        (self.x, self.y - 6, bar_width * health_ratio, bar_height))

class ShooterEnemy:
    """Ennemi qui tire sur le joueur"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.speed = 1.5
        self.health = 20
        self.max_health = 20
        self.color = PURPLE
        
        # Rectangle pour les collisions
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # Système de tir
        self.shoot_timer = 0
        self.shoot_delay = 90  # Tire toutes les 1.5 secondes
        self.range = 200  # Portée de tir
    
    def update(self, player, walls, other_enemies=None):
        # Distance au joueur
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        old_x, old_y = self.x, self.y
        
        # Si trop proche, reculer intelligemment
        if distance < 100:
            # Utiliser pathfinding pour fuir
            flee_target_x = self.x - dx
            flee_target_y = self.y - dy
            
            move_dx, move_dy = PathfindingHelper.get_movement_direction(
                self.x, self.y, flee_target_x, flee_target_y,
                self.width, self.height, walls, self.speed
            )
            
            self.x += move_dx
            self.y += move_dy
        
        # Force de séparation
        if other_enemies:
            sep_x, sep_y = FlockingBehavior.get_separation_force(self, other_enemies)
            self.x += sep_x * 0.3
            self.y += sep_y * 0.3
        
        # Vérifier collisions
        self.rect.x = self.x
        self.rect.y = self.y
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                self.x, self.y = old_x, old_y
                self.rect.x = self.x
                self.rect.y = self.y
                break
        
        # Timer de tir
        if self.shoot_timer > 0:
            self.shoot_timer -= 1
    
    def try_shoot(self, player):
        """Tente de tirer sur le joueur"""
        if self.shoot_timer <= 0:
            dx = player.x - self.x
            dy = player.y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Tirer si dans la portée
            if distance <= self.range:
                self.shoot_timer = self.shoot_delay
                
                # Normaliser direction
                if distance > 0:
                    dx /= distance
                    dy /= distance
                
                # Créer projectile ennemi
                bullet_x = self.x + self.width // 2
                bullet_y = self.y + self.height // 2
                return Bullet(bullet_x, bullet_y, dx, dy, is_player_bullet=False)
        return None
    
    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0
    
    def draw(self, screen):
        # Dessiner l'ennemi
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
        # Indicateur de tir (cercle rouge quand prêt à tirer)
        if self.shoot_timer <= 10:
            pygame.draw.circle(screen, (255, 0, 0), 
                             (int(self.x + self.width//2), int(self.y + self.height//2)), 3)
        
        # Barre de vie
        bar_width = self.width
        bar_height = 3
        health_ratio = self.health / self.max_health
        
        pygame.draw.rect(screen, DARK_RED, 
                        (self.x, self.y - 6, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, 
                        (self.x, self.y - 6, bar_width * health_ratio, bar_height))

class FastEnemy:
    """Ennemi rapide mais fragile"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 16
        self.height = 16
        self.speed = 4
        self.health = 15
        self.max_health = 15
        self.color = ORANGE
        
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # Mouvement erratique
        self.direction_timer = 0
        self.target_offset_x = 0
        self.target_offset_y = 0
    
    def update(self, player, walls, other_enemies=None):
        old_x, old_y = self.x, self.y
        
        # Changer de direction périodiquement
        self.direction_timer += 1
        if self.direction_timer > 60:  # Chaque seconde
            self.target_offset_x = random.randint(-50, 50)
            self.target_offset_y = random.randint(-50, 50)
            self.direction_timer = 0
        
        # Se diriger vers le joueur avec un offset (mouvement erratique)
        target_x = player.x + self.target_offset_x
        target_y = player.y + self.target_offset_y
        
        # Utiliser le pathfinding intelligent
        move_dx, move_dy = PathfindingHelper.get_movement_direction(
            self.x, self.y, target_x, target_y,
            self.width, self.height, walls, self.speed
        )
        
        # Force de séparation
        if other_enemies:
            sep_x, sep_y = FlockingBehavior.get_separation_force(self, other_enemies, 30)
            move_dx += sep_x * 0.4
            move_dy += sep_y * 0.4
        
        self.x += move_dx
        self.y += move_dy
        
        # Gestion collisions
        self.rect.x = self.x
        self.rect.y = self.y
        collision = False
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                collision = True
                break
                
        if collision:
            self.x, self.y = old_x, old_y
            self.rect.x = self.x
            self.rect.y = self.y
            # Changer de direction si collision
            self.direction_timer = 60
    
    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
        # Barre de vie plus petite
        bar_width = self.width
        bar_height = 2
        health_ratio = self.health / self.max_health
        
        pygame.draw.rect(screen, DARK_RED, 
                        (self.x, self.y - 5, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, 
                        (self.x, self.y - 5, bar_width * health_ratio, bar_height))
        
DARK_PURPLE = (80, 0, 80)
BRONZE = (205, 127, 50)
CRIMSON = (220, 20, 60)
VOID_BLACK = (20, 20, 20)

class CultistEnemy:
    """Cultiste du Chaos - Invoque des démons mineurs et se sacrifie"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 22
        self.height = 22
        self.speed = 1.8
        self.health = 25
        self.max_health = 25
        self.color = DARK_PURPLE
        
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # Capacités spéciales
        self.summon_timer = 0
        self.summon_delay = 300  # 5 secondes entre invocations
        self.sacrifice_range = 80  # Distance pour se sacrifier
        self.is_summoning = False
        self.summon_animation = 0
        
        # Comportement en groupe
        self.group_bonus = 1.0
    
    def update(self, player, walls, other_enemies=None):
        old_x, old_y = self.x, self.y
        
        # Calculer bonus de groupe (plus de cultistes = plus fort)
        cultist_count = sum(1 for enemy in other_enemies if isinstance(enemy, CultistEnemy))
        self.group_bonus = 1.0 + (cultist_count * 0.2)  # +20% par cultiste
        
        # Distance au joueur
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Comportement selon la distance
        if distance <= self.sacrifice_range and self.health < self.max_health * 0.3:
            # Tentative de sacrifice si blessé et proche
            self.attempt_sacrifice(player)
        else:
            # Mouvement normal vers le joueur
            move_dx, move_dy = PathfindingHelper.get_movement_direction(
                self.x, self.y, player.x, player.y,
                self.width, self.height, walls, self.speed * self.group_bonus
            )
            
            # Séparation avec autres ennemis
            if other_enemies:
                sep_x, sep_y = FlockingBehavior.get_separation_force(self, other_enemies)
                move_dx += sep_x * 0.3
                move_dy += sep_y * 0.3
            
            self.x += move_dx
            self.y += move_dy
        
        # Gestion collisions
        self.rect.x = self.x
        self.rect.y = self.y
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                self.x, self.y = old_x, old_y
                self.rect.x = self.x
                self.rect.y = self.y
                break
        
        # Timer d'invocation
        if self.summon_timer > 0:
            self.summon_timer -= 1
        
        # Animation d'invocation
        if self.is_summoning:
            self.summon_animation += 1
            if self.summon_animation > 60:  # 1 seconde d'animation
                self.is_summoning = False
                self.summon_animation = 0
    
    def attempt_sacrifice(self, player):
        """Tentative de sacrifice - damage zone autour du cultiste"""
        # Le cultiste meurt mais inflige des dégâts dans une zone
        self.health = 0  # Se sacrifie
        # La logique de dégâts sera gérée dans le main.py
        return True
    
    def try_summon(self):
        """Tentative d'invocation d'un démon mineur"""
        if self.summon_timer <= 0:
            self.summon_timer = self.summon_delay
            self.is_summoning = True
            self.summon_animation = 0
            return True
        return False
    
    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0
    
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
        bar_width = self.width
        bar_height = 3
        health_ratio = self.health / self.max_health
        
        pygame.draw.rect(screen, (100, 0, 0), (self.x, self.y - 6, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 6, bar_width * health_ratio, bar_height))


class RenegadeMarineEnemy:
    """Space Marine Renégat - Ennemi lourd avec charge et résistance"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.speed = 0.8  # Plus lent mais dangereux
        self.health = 80
        self.max_health = 80
        self.color = BRONZE
        
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
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
        
        # Animation
        self.animation_timer = 0
    
    def update(self, player, walls, other_enemies=None):
        old_x, old_y = self.x, self.y
        
        # Distance au joueur
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Gestion de la charge
        if self.is_charging:
            # En cours de charge
            self.perform_charge()
        elif self.charge_cooldown <= 0 and distance <= self.charge_range and distance > 50:
            # Initier une charge
            self.start_charge(player)
        else:
            # Mouvement normal (lent mais inexorable)
            move_dx, move_dy = PathfindingHelper.get_movement_direction(
                self.x, self.y, player.x, player.y,
                self.width, self.height, walls, self.speed
            )
            
            self.x += move_dx
            self.y += move_dy
        
        # Séparation avec autres ennemis
        if other_enemies and not self.is_charging:
            sep_x, sep_y = FlockingBehavior.get_separation_force(self, other_enemies, 50)
            self.x += sep_x * 0.2
            self.y += sep_y * 0.2
        
        # Gestion collisions
        self.rect.x = self.x
        self.rect.y = self.y
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if self.is_charging:
                    # Arrêter la charge si on touche un mur
                    self.is_charging = False
                    self.charge_duration = 0
                self.x, self.y = old_x, old_y
                self.rect.x = self.x
                self.rect.y = self.y
                break
        
        # Timers
        if self.charge_cooldown > 0:
            self.charge_cooldown -= 1
        
        self.animation_timer += 1
    
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
            self.x += dx * self.charge_speed
            self.y += dy * self.charge_speed
        
        self.charge_duration -= 1
    
    def take_damage(self, damage):
        # Appliquer la résistance aux dégâts
        reduced_damage = damage * (1 - self.damage_resistance)
        self.health -= reduced_damage
        return self.health <= 0
    
    def draw(self, screen):
        # Corps du marine (plus gros)
        dx = self.charge_target_x - self.x
        dy = self.charge_target_y - self.y
        color = self.color
        if self.is_charging:
            # Rouge pendant la charge
            color = CRIMSON
        
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        
        # Armure détaillée
        pygame.draw.rect(screen, (150, 150, 150), (self.x + 5, self.y + 5, self.width - 10, self.height - 10), 2)
        
        # Indicateur de charge
        if self.charge_cooldown <= 60 and not self.is_charging:  # Prêt à charger
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2
            pygame.draw.circle(screen, (255, 0, 0), (center_x, center_y), 5)
        
        # Effet de charge
        if self.is_charging:
            # Traînée de la charge
            trail_length = 15
            for i in range(trail_length):
                alpha = int(255 * (1 - i / trail_length))
                trail_surface = pygame.Surface((self.width, self.height))
                trail_surface.set_alpha(alpha)
                trail_surface.fill(CRIMSON)
                trail_x = self.x - (dx * i * 2) if 'dx' in locals() else self.x
                trail_y = self.y - (dy * i * 2) if 'dy' in locals() else self.y
                screen.blit(trail_surface, (trail_x, trail_y))
        
        # Barre de vie (plus épaisse pour les marines)
        bar_width = self.width
        bar_height = 4
        health_ratio = self.health / self.max_health
        
        pygame.draw.rect(screen, (100, 0, 0), (self.x, self.y - 8, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 8, bar_width * health_ratio, bar_height))


class DaemonEnemy:
    """Démon mineur - Apparaît via invocation, téléportation et attaques psychiques"""
    def __init__(self, x, y, is_summoned=False):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.speed = 3
        self.health = 15 if is_summoned else 25
        self.max_health = self.health
        self.color = VOID_BLACK
        
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # Capacités démoniaques
        self.teleport_cooldown = 0
        self.teleport_delay = 180  # 3 secondes
        self.teleport_range = 150
        self.is_teleporting = False
        self.teleport_animation = 0
        
        # Attaque psychique
        self.psychic_cooldown = 0
        self.psychic_delay = 120  # 2 secondes
        self.psychic_range = 120
        
        # Propriétés démoniaques
        self.is_summoned = is_summoned
        self.lifespan = 600 if is_summoned else -1  # 10 secondes si invoqué
        self.phase_timer = 0  # Pour effet de phase
    
    def update(self, player, walls, other_enemies=None):
        # Décompte de la durée de vie si invoqué
        if self.is_summoned and self.lifespan > 0:
            self.lifespan -= 1
            if self.lifespan <= 0:
                self.health = 0  # Disparaît
                return
        
        old_x, old_y = self.x, self.y
        
        # Distance au joueur
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Gestion de la téléportation
        if self.is_teleporting:
            self.teleport_animation += 1
            if self.teleport_animation > 30:  # Fin de l'animation
                self.perform_teleport(player)
        elif self.teleport_cooldown <= 0 and distance > 100:
            # Téléportation si trop loin
            self.start_teleport()
        else:
            # Mouvement normal (rapide et erratique)
            target_x = player.x + random.randint(-30, 30)
            target_y = player.y + random.randint(-30, 30)
            
            move_dx, move_dy = PathfindingHelper.get_movement_direction(
                self.x, self.y, target_x, target_y,
                self.width, self.height, walls, self.speed
            )
            
            self.x += move_dx
            self.y += move_dy
        
        # Gestion collisions (les démons peuvent parfois les ignorer)
        self.rect.x = self.x
        self.rect.y = self.y
        if not self.is_teleporting:  # Pas de collision pendant téléportation
            for wall in walls:
                if self.rect.colliderect(wall.rect):
                    # 30% de chance d'ignorer les murs (phase)
                    if random.random() > 0.3:
                        self.x, self.y = old_x, old_y
                        self.rect.x = self.x
                        self.rect.y = self.y
                    break
        
        # Timers
        if self.teleport_cooldown > 0:
            self.teleport_cooldown -= 1
        if self.psychic_cooldown > 0:
            self.psychic_cooldown -= 1
        
        self.phase_timer += 1
    
    def start_teleport(self):
        """Démarre la téléportation"""
        self.is_teleporting = True
        self.teleport_animation = 0
        self.teleport_cooldown = self.teleport_delay
    
    def perform_teleport(self, player):
        """Exécute la téléportation près du joueur"""
        # Téléportation dans un rayon autour du joueur
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(50, 100)
        
        new_x = player.x + math.cos(angle) * distance
        new_y = player.y + math.sin(angle) * distance
        
        self.x = new_x
        self.y = new_y
        self.is_teleporting = False
        self.teleport_animation = 0
    
    def try_psychic_attack(self, player):
        """Tentative d'attaque psychique"""
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if self.psychic_cooldown <= 0 and distance <= self.psychic_range:
            self.psychic_cooldown = self.psychic_delay
            return True
        return False
    
    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0
    
    def draw(self, screen):
        if self.is_teleporting:
            # Effet de téléportation
            alpha = int(255 * (1 - self.teleport_animation / 30))
            demon_surface = pygame.Surface((self.width, self.height))
            demon_surface.set_alpha(alpha)
            demon_surface.fill(self.color)
            screen.blit(demon_surface, (self.x, self.y))
            
            # Particules de téléportation
            for i in range(8):
                angle = (i / 8) * 2 * math.pi + self.teleport_animation * 0.2
                particle_x = self.x + self.width//2 + math.cos(angle) * 20
                particle_y = self.y + self.height//2 + math.sin(angle) * 20
                pygame.draw.circle(screen, (150, 0, 150), (int(particle_x), int(particle_y)), 2)
        else:
            # Corps du démon avec effet de phase
            phase_offset = math.sin(self.phase_timer * 0.1) * 2
            demon_rect = (self.x + phase_offset, self.y, self.width, self.height)
            pygame.draw.rect(screen, self.color, demon_rect)
            
            # Aura démoniaque
            aura_radius = int(15 + math.sin(self.phase_timer * 0.05) * 3)
            center_x = int(self.x + self.width // 2)
            center_y = int(self.y + self.height // 2)
            
            aura_surface = pygame.Surface((aura_radius * 2, aura_radius * 2))
            aura_surface.set_alpha(50)
            pygame.draw.circle(aura_surface, (150, 0, 150), (aura_radius, aura_radius), aura_radius)
            screen.blit(aura_surface, (center_x - aura_radius, center_y - aura_radius))
            
            # Yeux brillants
            eye_y = self.y + 6
            pygame.draw.circle(screen, (255, 0, 0), (int(self.x + 6), int(eye_y)), 2)
            pygame.draw.circle(screen, (255, 0, 0), (int(self.x + 14), int(eye_y)), 2)
        
        # Barre de vie (si pas en téléportation)
        if not self.is_teleporting:
            bar_width = self.width
            bar_height = 2
            health_ratio = self.health / self.max_health
            
            pygame.draw.rect(screen, (50, 0, 50), (self.x, self.y - 5, bar_width, bar_height))
            pygame.draw.rect(screen, (150, 0, 150), (self.x, self.y - 5, bar_width * health_ratio, bar_height))
            
            # Indicateur de durée de vie si invoqué
            if self.is_summoned and self.lifespan > 0:
                life_ratio = self.lifespan / 600
                life_width = int(bar_width * life_ratio)
                pygame.draw.rect(screen, (255, 255, 0), (self.x, self.y - 8, life_width, 1))

CHAOS_RED = (139, 0, 0)
IMPERIAL_GOLD = (255, 215, 0)
DAEMON_PURPLE = (75, 0, 130)
SAINT_WHITE = (248, 248, 255)
MARINE_BLUE = (25, 25, 112)

class ChaosSorcererBoss:
    """Boss Sorcier du Chaos - Téléportation, invocations, et sorts dévastateurs"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 48
        self.height = 48
        self.speed = 1.5
        self.max_health = 35000
        self.health = self.max_health
        self.color = CHAOS_RED
        
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # === SYSTÈME DE PHASES ===
        self.phase = 1  # Phase 1: Normal, Phase 2: Aggressif, Phase 3: Berserk
        self.phase_transition_health = [25000, 10000]  # Seuils de changement de phase
        
        # === CAPACITÉS SPÉCIALES ===
        self.teleport_cooldown = 0
        self.teleport_delay = 180  # 3 secondes
        self.is_teleporting = False
        self.teleport_animation = 0
        
        # Invocation de démons
        self.summon_cooldown = 0
        self.summon_delay = 300  # 5 secondes
        self.max_summons = 4
        self.current_summons = 0
        
        # Attaque de zone
        self.area_attack_cooldown = 0
        self.area_attack_delay = 240  # 4 secondes
        self.is_casting_area = False
        self.area_cast_timer = 0
        
        # Barrage de projectiles
        self.barrage_cooldown = 0
        self.barrage_delay = 150  # 2.5 secondes
        
        # Animation et effets
        self.animation_timer = 0
        self.rage_mode = False
        self.invulnerable_timer = 0  # Invulnérabilité pendant téléportation
        
        # Résistance aux dégâts
        self.damage_resistance = 0.2  # Réduit 20% des dégâts
    
    def update(self, player, walls, other_enemies=None):
        old_x, old_y = self.x, self.y
        
        # Vérifier changement de phase
        self.check_phase_transition()
        
        # Distance au joueur
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
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
        
        # Mise à jour des timers
        self.update_timers()
        self.animation_timer += 1
        
        # Mise à jour du rectangle
        self.rect.x = self.x
        self.rect.y = self.y
    
    def check_phase_transition(self):
        """Gère les transitions de phase"""
        if self.phase == 1 and self.health <= self.phase_transition_health[0]:
            self.phase = 2
            self.rage_mode = True
            self.become_more_aggressive()
            print("🔥 PHASE 2: Le Sorcier entre en rage !")
        
        elif self.phase == 2 and self.health <= self.phase_transition_health[1]:
            self.phase = 3
            self.become_berserk()
            print("💀 PHASE 3: BERSERK ! Le Sorcier est désespéré !")
    
    def become_more_aggressive(self):
        """Phase 2: Plus agressif"""
        self.teleport_delay = 120  # Téléporte plus souvent
        self.summon_delay = 200    # Invoque plus souvent
        self.area_attack_delay = 180  # Attaque de zone plus fréquente
        self.speed = 2.0
    
    def become_berserk(self):
        """Phase 3: Berserk"""
        self.teleport_delay = 80
        self.summon_delay = 150
        self.area_attack_delay = 120
        self.barrage_delay = 100
        self.speed = 2.5
        self.damage_resistance = 0.4  # Plus résistant quand blessé
    
    def tactical_retreat(self, player, walls):
        """Recule intelligemment du joueur"""
        dx = self.x - player.x
        dy = self.y - player.y
        length = math.sqrt(dx*dx + dy*dy)
        if length > 0:
            dx /= length
            dy /= length
        
        move_dx, move_dy = PathfindingHelper.get_movement_direction(
            self.x, self.y, self.x + dx * 100, self.y + dy * 100,
            self.width, self.height, walls, self.speed
        )
        self.x += move_dx
        self.y += move_dy
    
    def move_towards_player(self, player, walls):
        """Se rapproche du joueur"""
        move_dx, move_dy = PathfindingHelper.get_movement_direction(
            self.x, self.y, player.x, player.y,
            self.width, self.height, walls, self.speed * 0.7
        )
        self.x += move_dx
        self.y += move_dy
    
    def circle_player(self, player, walls):
        """Tourne autour du joueur"""
        angle = math.atan2(player.y - self.y, player.x - self.x)
        angle += 1.2  # Mouvement circulaire
        
        target_distance = 120
        target_x = player.x + math.cos(angle) * target_distance
        target_y = player.y + math.sin(angle) * target_distance
        
        move_dx, move_dy = PathfindingHelper.get_movement_direction(
            self.x, self.y, target_x, target_y,
            self.width, self.height, walls, self.speed
        )
        self.x += move_dx
        self.y += move_dy
    
    def handle_teleportation(self, player):
        """Gère l'animation de téléportation"""
        self.teleport_animation += 1
        if self.teleport_animation > 60:
            self.perform_boss_teleport(player)
    
    def perform_boss_teleport(self, player):
        """Téléportation tactique du boss"""
        # Téléporter à une position tactique
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(100, 150)
        
        new_x = player.x + math.cos(angle) * distance
        new_y = player.y + math.sin(angle) * distance
        
        # S'assurer que c'est dans les limites du monde
        new_x = max(50, min(1998, new_x))
        new_y = max(50, min(1486, new_y))
        
        self.x = new_x
        self.y = new_y
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
    
    def update_timers(self):
        """Met à jour tous les cooldowns"""
        if self.teleport_cooldown > 0:
            self.teleport_cooldown -= 1
        if self.summon_cooldown > 0:
            self.summon_cooldown -= 1
        if self.area_attack_cooldown > 0:
            self.area_attack_cooldown -= 1
        if self.barrage_cooldown > 0:
            self.barrage_cooldown -= 1
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1
    
    def try_teleport(self):
        """Tentative de téléportation"""
        if self.teleport_cooldown <= 0 and not self.is_teleporting:
            self.is_teleporting = True
            self.teleport_animation = 0
            self.teleport_cooldown = self.teleport_delay
            return True
        return False
    
    def try_summon_daemon(self):
        """Tentative d'invocation de démon"""
        if (self.summon_cooldown <= 0 and 
            self.current_summons < self.max_summons):
            self.summon_cooldown = self.summon_delay
            self.current_summons += 1
            return True
        return False
    
    def try_area_attack(self, player):
        """Tentative d'attaque de zone"""
        if self.area_attack_cooldown <= 0 and not self.is_casting_area:
            self.is_casting_area = True
            self.area_cast_timer = 0
            self.area_attack_cooldown = self.area_attack_delay
            return True
        return False
    
    def try_projectile_barrage(self, player):
        """Tentative de barrage de projectiles"""
        if self.barrage_cooldown <= 0:
            self.barrage_cooldown = self.barrage_delay
            return True
        return False
    
    def take_damage(self, damage):
        """Prend des dégâts avec résistance"""
        if self.invulnerable_timer > 0:
            return False  # Invulnérable
        
        reduced_damage = damage * (1 - self.damage_resistance)
        self.health -= reduced_damage
        
        # Chance de téléporter quand blessé
        if random.random() < 0.3:
            self.try_teleport()
        
        return self.health <= 0
    
    def on_summon_death(self):
        """Appelé quand un de ses démons meurt"""
        self.current_summons -= 1
    
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
            pygame.draw.rect(screen, (100, 0, 100), (self.x + 8, self.y + 8, self.width - 16, self.height - 16))
            pygame.draw.circle(screen, (255, 215, 0), (center_x, center_y), 8)
            
            # Aura de puissance
            aura_radius = int(25 + math.sin(self.animation_timer * 0.1) * 5)
            aura_surface = pygame.Surface((aura_radius * 2, aura_radius * 2))
            aura_intensity = 30 if self.phase == 1 else 50 if self.phase == 2 else 80
            aura_surface.set_alpha(aura_intensity)
            aura_color = (150, 0, 150) if self.phase < 3 else (255, 0, 0)
            pygame.draw.circle(aura_surface, aura_color, (aura_radius, aura_radius), aura_radius)
            screen.blit(aura_surface, (center_x - aura_radius, center_y - aura_radius))
        
        # Indicateur d'incantation
        if self.is_casting_area:
            cast_progress = self.area_cast_timer / 120
            warning_radius = int(80 + cast_progress * 40)
            pygame.draw.circle(screen, (255, 255, 0), 
                             (int(self.x + self.width//2), int(self.y + self.height//2)), 
                             warning_radius, 3)
            
            # Texte d'avertissement
            font = pygame.font.Font(None, 32)
            warning_text = font.render("SORT PUISSANT !", True, (255, 0, 0))
            text_rect = warning_text.get_rect(center=(self.x + self.width//2, self.y - 30))
            screen.blit(warning_text, text_rect)
        
        # Barre de vie du boss (plus grosse et colorée)
        bar_width = self.width * 2
        bar_height = 8
        health_ratio = self.health / self.max_health
        
        # Fond de la barre
        pygame.draw.rect(screen, (50, 0, 0), (self.x - self.width//2, self.y - 20, bar_width, bar_height))
        
        # Couleur de la barre selon la phase
        if self.phase == 1:
            bar_color = (255, 100, 100)
        elif self.phase == 2:
            bar_color = (255, 50, 50)
        else:
            bar_color = (255, 0, 0)
        
        pygame.draw.rect(screen, bar_color, 
                        (self.x - self.width//2, self.y - 20, bar_width * health_ratio, bar_height))
        
        # Bordure dorée
        pygame.draw.rect(screen, (255, 215, 0), 
                        (self.x - self.width//2, self.y - 20, bar_width, bar_height), 2)
        
        # Nom du boss
        font = pygame.font.Font(None, 24)
        phase_text = ["", "ENRAGÉ", "BERSERK"][self.phase - 1]
        name_text = font.render(f"SORCIER DU CHAOS {phase_text}", True, (255, 215, 0))
        name_rect = name_text.get_rect(center=(self.x + self.width//2, self.y - 35))
        screen.blit(name_text, name_rect)


class InquisitorLordBoss:
    """Boss Seigneur Inquisiteur - Purification, benedictions et justice impériale"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 45
        self.height = 45
        self.speed = 2.0
        self.max_health = 28000
        self.health = self.max_health
        self.color = IMPERIAL_GOLD
        
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # === CAPACITÉS IMPÉRIALES ===
        self.purification_cooldown = 0
        self.purification_delay = 360  # 6 secondes - Très puissant
        self.is_purifying = False
        self.purification_timer = 0
        
        # Tir sanctifié en rafales
        self.blessed_shot_cooldown = 0
        self.blessed_shot_delay = 60  # 1 seconde
        
        # Charge sainte
        self.charge_cooldown = 0
        self.charge_delay = 240  # 4 secondes
        self.is_charging = False
        self.charge_target_x = 0
        self.charge_target_y = 0
        self.charge_duration = 0
        
        # Bouclier de foi (défense temporaire)
        self.shield_cooldown = 0
        self.shield_delay = 300  # 5 secondes
        self.shield_active = False
        self.shield_duration = 0
        
        # Animation
        self.animation_timer = 0
        self.righteous_fury = False  # S'active quand PV bas
        
        # Résistance morale
        self.damage_resistance = 0.15
    
    def update(self, player, walls, other_enemies=None):
        old_x, old_y = self.x, self.y
        
        # Vérifier si en colère sainte (< 30% PV)
        if self.health < self.max_health * 0.3 and not self.righteous_fury:
            self.righteous_fury = True
            self.become_righteous()
            print("⚡ COLÈRE SAINTE ! L'Inquisiteur devient redoutable !")
        
        # Distance au joueur
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
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
        
        # Mise à jour des timers
        self.update_timers()
        self.animation_timer += 1
        
        # Mise à jour du rectangle
        self.rect.x = self.x
        self.rect.y = self.y
    
    def become_righteous(self):
        """Mode colère sainte"""
        self.speed = 3.0
        self.purification_delay = 240  # Plus fréquent
        self.blessed_shot_delay = 40   # Tir plus rapide
        self.charge_delay = 180
        self.damage_resistance = 0.3   # Plus résistant
    
    def advance_on_heretic(self, player, walls):
        """Avance inexorablement vers l'hérétique"""
        move_dx, move_dy = PathfindingHelper.get_movement_direction(
            self.x, self.y, player.x, player.y,
            self.width, self.height, walls, self.speed
        )
        self.x += move_dx
        self.y += move_dy
    
    def maintain_firing_distance(self, player, walls):
        """Maintient une distance de tir optimale"""
        # Mouvement en crabe pour rester à distance
        angle = math.atan2(player.y - self.y, player.x - self.x)
        angle += 1.0  # Mouvement latéral
        
        move_x = math.cos(angle) * self.speed * 0.8
        move_y = math.sin(angle) * self.speed * 0.8
        
        self.x += move_x
        self.y += move_y
        
        # Vérifier collisions
        self.rect.x = self.x
        self.rect.y = self.y
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                self.x -= move_x
                self.y -= move_y
                self.rect.x = self.x
                self.rect.y = self.y
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
            self.x += dx * charge_speed
            self.y += dy * charge_speed
        
        self.charge_duration -= 1
    
    def try_charge(self, player):
        """Tentative de charge"""
        if self.charge_cooldown <= 0 and not self.is_charging:
            self.is_charging = True
            self.charge_target_x = player.x
            self.charge_target_y = player.y
            self.charge_duration = 30
            self.charge_cooldown = self.charge_delay
            return True
        return False
    
    def try_purification(self):
        """Tentative de purification"""
        if self.purification_cooldown <= 0 and not self.is_purifying:
            self.is_purifying = True
            self.purification_timer = 0
            self.purification_cooldown = self.purification_delay
            return True
        return False
    
    def try_blessed_shots(self, player):
        """Tentative de tirs bénis"""
        if self.blessed_shot_cooldown <= 0:
            self.blessed_shot_cooldown = self.blessed_shot_delay
            return True
        return False
    
    def try_activate_shield(self):
        """Tentative d'activation du bouclier de foi"""
        if self.shield_cooldown <= 0 and not self.shield_active:
            self.shield_active = True
            self.shield_duration = 180  # 3 secondes
            self.shield_cooldown = self.shield_delay
            return True
        return False
    
    def update_timers(self):
        """Met à jour tous les cooldowns"""
        if self.purification_cooldown > 0:
            self.purification_cooldown -= 1
        if self.blessed_shot_cooldown > 0:
            self.blessed_shot_cooldown -= 1
        if self.charge_cooldown > 0:
            self.charge_cooldown -= 1
        if self.shield_cooldown > 0:
            self.shield_cooldown -= 1
        if self.shield_duration > 0:
            self.shield_duration -= 1
        else:
            self.shield_active = False
    
    def take_damage(self, damage):
        """Prend des dégâts avec résistance et bouclier"""
        # Bouclier de foi
        if self.shield_active:
            damage *= 0.3  # Réduit 70% des dégâts
        
        # Résistance de base
        reduced_damage = damage * (1 - self.damage_resistance)
        self.health -= reduced_damage
        
        # Chance d'activer le bouclier quand blessé
        if self.health < self.max_health * 0.5 and random.random() < 0.4:
            self.try_activate_shield()
        
        return self.health <= 0
    
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
        pygame.draw.rect(screen, (200, 200, 200), (self.x + 5, self.y + 5, self.width - 10, self.height - 10), 3)
        
        # Symbole de l'Inquisition (Crâne)
        pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), 8)
        pygame.draw.circle(screen, (0, 0, 0), (center_x - 3, center_y - 2), 2)
        pygame.draw.circle(screen, (0, 0, 0), (center_x + 3, center_y - 2), 2)
        
        # Bouclier de foi
        if self.shield_active:
            shield_radius = int(30 + math.sin(self.animation_timer * 0.2) * 3)
            shield_surface = pygame.Surface((shield_radius * 2, shield_radius * 2))
            shield_surface.set_alpha(80)
            pygame.draw.circle(shield_surface, (255, 255, 200), (shield_radius, shield_radius), shield_radius)
            screen.blit(shield_surface, (center_x - shield_radius, center_y - shield_radius))
            
            # Bordure du bouclier
            pygame.draw.circle(screen, (255, 215, 0), (center_x, center_y), shield_radius, 2)
        
        # Aura de purification
        if self.is_purifying:
            purif_progress = self.purification_timer / 150
            warning_radius = int(120 + purif_progress * 80)
            
            # Zone de danger
            pygame.draw.circle(screen, (255, 255, 0), (center_x, center_y), warning_radius, 4)
            
            # Rayons de purification
            for i in range(8):
                angle = (i / 8) * 2 * math.pi + self.purification_timer * 0.1
                end_x = center_x + math.cos(angle) * warning_radius
                end_y = center_y + math.sin(angle) * warning_radius
                pygame.draw.line(screen, (255, 255, 200), (center_x, center_y), (end_x, end_y), 3)
            
            # Texte d'avertissement
            font = pygame.font.Font(None, 32)
            warning_text = font.render("PURIFICATION !", True, (255, 255, 0))
            text_rect = warning_text.get_rect(center=(center_x, self.y - 40))
            screen.blit(warning_text, text_rect)
        
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
        bar_width = self.width * 2
        bar_height = 6
        health_ratio = self.health / self.max_health
        
        # Fond
        pygame.draw.rect(screen, (100, 100, 0), (self.x - self.width//2, self.y - 18, bar_width, bar_height))
        
        # Couleur selon l'état
        bar_color = (255, 255, 100) if not self.righteous_fury else (255, 200, 0)
        pygame.draw.rect(screen, bar_color, 
                        (self.x - self.width//2, self.y - 18, bar_width * health_ratio, bar_height))
        
        # Bordure
        pygame.draw.rect(screen, (255, 215, 0), 
                        (self.x - self.width//2, self.y - 18, bar_width, bar_height), 2)
        
        # Nom
        font = pygame.font.Font(None, 24)
        fury_text = " - COLÈRE SAINTE" if self.righteous_fury else ""
        name_text = font.render(f"SEIGNEUR INQUISITEUR{fury_text}", True, (255, 215, 0))
        name_rect = name_text.get_rect(center=(center_x, self.y - 35))
        screen.blit(name_text, name_rect)


class DaemonPrinceBoss:
    """Boss Prince Daemon - Boss ultime de corruption avec pouvoirs chaotiques"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 64
        self.height = 64
        self.speed = 1.8
        self.max_health = 50000
        self.health = self.max_health
        self.color = DAEMON_PURPLE
        
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # === POUVOIRS DU CHAOS ===
        self.warp_storm_cooldown = 0
        self.warp_storm_delay = 480  # 8 secondes - Attaque dévastatrice
        self.is_summoning_storm = False
        self.storm_cast_timer = 0
        
        # Téléportation chaotique (plus agressive que les démons normaux)
        self.chaos_teleport_cooldown = 0
        self.chaos_teleport_delay = 120  # 2 secondes
        self.is_teleporting = False
        self.teleport_animation = 0
        
        # Vague de corruption
        self.corruption_wave_cooldown = 0
        self.corruption_wave_delay = 200  # 3.33 secondes
        
        # Invocation massive
        self.mass_summon_cooldown = 0
        self.mass_summon_delay = 600  # 10 secondes
        self.total_summons = 0
        self.max_total_summons = 8
        
        # Régénération chaotique
        self.regeneration_timer = 0
        self.regen_rate = 1  # Régénère lentement
        
        # Animation et transformation
        self.animation_timer = 0
        self.chaos_form = 1  # Forme 1: Normal, 2: Transformé
        self.transformation_threshold = 20000  # Se transforme à 40% PV
        
        # Résistance massive
        self.damage_resistance = 0.3
    
    def update(self, player, walls, other_enemies=None):
        old_x, old_y = self.x, self.y
        
        # Transformation du Prince Daemon
        if (self.health <= self.transformation_threshold and 
            self.chaos_form == 1):
            self.transform_to_greater_daemon()
        
        # Régénération
        self.handle_regeneration()
        
        # Distance au joueur
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Comportement selon l'état
        if self.is_summoning_storm:
            self.handle_warp_storm()
        elif self.is_teleporting:
            self.handle_chaos_teleportation(player)
        else:
            # Mouvement chaotique et imprévisible
            self.chaotic_movement(player, walls, distance)
        
        # Mise à jour des timers
        self.update_timers()
        self.animation_timer += 1
        
        # Mise à jour du rectangle
        self.rect.x = self.x
        self.rect.y = self.y
    
    def transform_to_greater_daemon(self):
        """Transformation en forme supérieure"""
        self.chaos_form = 2
        self.width = 80
        self.height = 80
        self.speed = 2.5
        self.damage_resistance = 0.5  # Encore plus résistant
        self.regen_rate = 0.2  # Régénère plus vite
        
        # Capacités améliorées
        self.warp_storm_delay = 300  # Plus fréquent
        self.chaos_teleport_delay = 80
        self.corruption_wave_delay = 150
        
        print("💀🔥 LE PRINCE DAEMON SE TRANSFORME ! FORME ULTIME !")
    
    def handle_regeneration(self):
        """Régénération chaotique"""
        self.regeneration_timer += 1
        if self.regeneration_timer >= 60:  # Chaque seconde
            if self.health < self.max_health:
                self.health += self.regen_rate * self.max_health
                self.health = min(self.health, self.max_health)
            self.regeneration_timer = 0
    
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
        self.x += move_dx
        self.y += move_dy
    
    def charge_towards_player(self, player, walls):
        """Charge brutale vers le joueur"""
        move_dx, move_dy = PathfindingHelper.get_movement_direction(
            self.x, self.y, player.x, player.y,
            self.width, self.height, walls, self.speed * 1.5
        )
        self.x += move_dx
        self.y += move_dy
    
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
        self.x += move_dx
        self.y += move_dy
    
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
        
        self.x = new_x
        self.y = new_y
        self.is_teleporting = False
        self.teleport_animation = 0
    
    def try_chaos_teleport(self):
        """Tentative de téléportation chaotique"""
        if self.chaos_teleport_cooldown <= 0 and not self.is_teleporting:
            self.is_teleporting = True
            self.teleport_animation = 0
            self.chaos_teleport_cooldown = self.chaos_teleport_delay
            return True
        return False
    
    def try_warp_storm(self):
        """Tentative de tempête warp"""
        if self.warp_storm_cooldown <= 0 and not self.is_summoning_storm:
            self.is_summoning_storm = True
            self.storm_cast_timer = 0
            self.warp_storm_cooldown = self.warp_storm_delay
            return True
        return False
    
    def try_corruption_wave(self):
        """Tentative de vague de corruption"""
        if self.corruption_wave_cooldown <= 0:
            self.corruption_wave_cooldown = self.corruption_wave_delay
            return True
        return False
    
    def try_mass_summon(self):
        """Tentative d'invocation massive"""
        if (self.mass_summon_cooldown <= 0 and 
            self.total_summons < self.max_total_summons):
            self.mass_summon_cooldown = self.mass_summon_delay
            return True
        return False
    
    def update_timers(self):
        """Met à jour tous les cooldowns"""
        if self.warp_storm_cooldown > 0:
            self.warp_storm_cooldown -= 1
        if self.chaos_teleport_cooldown > 0:
            self.chaos_teleport_cooldown -= 1
        if self.corruption_wave_cooldown > 0:
            self.corruption_wave_cooldown -= 1
        if self.mass_summon_cooldown > 0:
            self.mass_summon_cooldown -= 1
    
    def take_damage(self, damage):
        """Prend des dégâts avec résistance massive"""
        reduced_damage = damage * (1 - self.damage_resistance)
        self.health -= reduced_damage
        
        # Réaction chaotique aux dégâts
        if random.random() < 0.4:
            if random.random() < 0.5:
                self.try_chaos_teleport()
            else:
                self.try_corruption_wave()
        
        return self.health <= 0
    
    def on_summon_death(self):
        """Appelé quand une invocation meurt"""
        self.total_summons -= 1
    
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
            storm_radius = int(150 + storm_progress * 100)
            
            # Zone de danger massive
            pygame.draw.circle(screen, (255, 0, 255), (center_x, center_y), storm_radius, 6)
            
            # Éclairs chaotiques
            for i in range(12):
                angle = random.uniform(0, 2 * math.pi)
                length = random.uniform(storm_radius * 0.5, storm_radius)
                end_x = center_x + math.cos(angle) * length
                end_y = center_y + math.sin(angle) * length
                
                lightning_color = (random.randint(200, 255), 0, random.randint(200, 255))
                pygame.draw.line(screen, lightning_color, (center_x, center_y), (end_x, end_y), 4)
            
            # Texte d'avertissement
            font = pygame.font.Font(None, 36)
            warning_text = font.render("TEMPÊTE WARP !", True, (255, 0, 255))
            text_rect = warning_text.get_rect(center=(center_x, self.y - 50))
            screen.blit(warning_text, text_rect)
        
        # Barre de vie massive
        bar_width = self.width * 3
        bar_height = 10
        health_ratio = self.health / self.max_health
        
        # Fond
        pygame.draw.rect(screen, (50, 0, 50), 
                        (self.x - self.width, self.y - 25, bar_width, bar_height))
        
        # Couleur selon la forme
        bar_color = (150, 0, 150) if self.chaos_form == 1 else (200, 0, 200)
        pygame.draw.rect(screen, bar_color, 
                        (self.x - self.width, self.y - 25, bar_width * health_ratio, bar_height))
        
        # Bordure chaotique
        pygame.draw.rect(screen, (255, 0, 255), 
                        (self.x - self.width, self.y - 25, bar_width, bar_height), 3)
        
        # Nom terrifiant
        font = pygame.font.Font(None, 28)
        form_text = " - FORME ULTIME" if self.chaos_form == 2 else ""
        name_text = font.render(f"PRINCE DAEMON{form_text}", True, (255, 0, 255))
        name_rect = name_text.get_rect(center=(center_x, self.y - 45))
        screen.blit(name_text, name_rect)
        
        # Indicateur de régénération
        if self.regeneration_timer > 30:
            regen_text = font.render("RÉGÉNÉRATION", True, (150, 255, 150))
            regen_rect = regen_text.get_rect(center=(center_x, self.y + self.height + 20))
            screen.blit(regen_text, regen_rect)