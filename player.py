import pygame
import math
from bullet import Bullet

# Couleurs
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_RED = (100, 0, 0)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.speed = 5
        self.health = 100
        self.max_health = 100
        
        # Rectangle pour les collisions
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # Système de tir automatique
        self.shoot_timer = 0
        self.shoot_delay = 10  # Tir toutes les 10 frames (6 tirs/seconde à 60 FPS)
        
        # Système d'invincibilité
        self.invincible_timer = 0
        self.invincible_duration = 60  # 1 seconde d'invincibilité à 60 FPS
        self.flash_timer = 0
        
        # Statistiques modifiables par les objets
        self.base_damage = 10
        self.multi_shot = 1
        self.piercing = False
        self.bullet_size = 1.0
        self.homing = False
        self.explosive = False
        self.holy_damage = False
        self.health_regen = 0
        self.unstable = False
        self.chaos_power = False
        
        # Statistiques de base pour les effets de moralité
        self.base_max_health = self.max_health
        self.morality_speed_modifier = 1.0
    
    def update(self, walls, morality_system=None):
        # Gestion des inputs
        keys = pygame.key.get_pressed()
        
        # Sauvegarde de la position actuelle
        old_x, old_y = self.x, self.y
        
        # Appliquer les modificateurs de moralité
        speed_multiplier = 1.0
        if morality_system:
            modifiers = morality_system.get_stat_modifiers()
            speed_multiplier = modifiers["speed_multiplier"]
        
        # Appliquer aussi le modificateur de moralité direct
        total_speed_multiplier = speed_multiplier * getattr(self, 'morality_speed_modifier', 1.0)
        
        # Mouvement avec multiplicateur
        effective_speed = self.speed * total_speed_multiplier
        if keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_q]:
            self.x -= effective_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += effective_speed
        if keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_z]:
            self.y -= effective_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += effective_speed
        
        # Mettre à jour le rectangle de collision
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Vérifier les collisions avec les murs
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                # Collision détectée, revenir à l'ancienne position
                self.x, self.y = old_x, old_y
                self.rect.x = self.x
                self.rect.y = self.y
                break
        
        # Décrémenter le timer de tir
        if self.shoot_timer > 0:
            self.shoot_timer -= 1
            
        # Décrémenter le timer d'invincibilité
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
            self.flash_timer += 1
        
        # Régénération de vie
        if self.health_regen > 0 and self.health < self.max_health:
            self.health += self.health_regen
            self.health = min(self.health, self.max_health)
    
    def try_shoot(self, mouse_pos, morality_system=None):
        """Tente de tirer si le délai est écoulé"""
        if self.shoot_timer <= 0:
            # Modificateur de cadence selon la moralité
            fire_rate_multiplier = 1.0
            if morality_system:
                modifiers = morality_system.get_stat_modifiers()
                fire_rate_multiplier = modifiers["fire_rate_multiplier"]
            
            self.shoot_timer = int(self.shoot_delay * fire_rate_multiplier)
            return self.shoot(mouse_pos, morality_system)
        return []
    
    def shoot(self, mouse_pos, morality_system=None):
        # Calculer la direction vers la souris
        dx = mouse_pos[0] - (self.x + self.width // 2)
        dy = mouse_pos[1] - (self.y + self.height // 2)
        
        # Normaliser la direction
        length = math.sqrt(dx*dx + dy*dy)
        if length != 0:
            dx /= length
            dy /= length
        
        bullets = []
        bullet_x = self.x + self.width // 2
        bullet_y = self.y + self.height // 2
        
        # Modificateurs de moralité
        damage_multiplier = 1.0
        special_effects = []
        if morality_system:
            modifiers = morality_system.get_stat_modifiers()
            damage_multiplier = modifiers["damage_multiplier"]
            special_effects = modifiers["special_effects"]
        
        # Calcul des dégâts finaux
        final_damage = int(self.base_damage * damage_multiplier)
        
        # Effets spéciaux selon l'état moral
        bullet_effects = {
            "piercing": self.piercing,
            "size_multiplier": self.bullet_size,
            "homing": self.homing,
            "explosive": self.explosive,
            "holy_damage": self.holy_damage or "holy_bullets" in special_effects,
            "cursed": "cursed_bullets" in special_effects,
            "chaos_power": "chaos_powers" in special_effects
        }
        
        # Tir multiple
        for i in range(self.multi_shot):
            # Calculer angle pour spread
            if self.multi_shot > 1:
                angle_offset = (i - (self.multi_shot - 1) / 2) * 0.3
                final_dx = dx * math.cos(angle_offset) - dy * math.sin(angle_offset)
                final_dy = dx * math.sin(angle_offset) + dy * math.cos(angle_offset)
            else:
                final_dx, final_dy = dx, dy
            
            # Créer le projectile avec les propriétés du joueur
            bullet = Bullet(bullet_x, bullet_y, final_dx, final_dy, 
                           is_player_bullet=True, damage=final_damage,
                           piercing=bullet_effects["piercing"],
                           size_multiplier=bullet_effects["size_multiplier"],
                           homing=bullet_effects["homing"],
                           explosive=bullet_effects["explosive"],
                           holy_damage=bullet_effects["holy_damage"],
                           cursed=bullet_effects["cursed"],
                           chaos_power=bullet_effects["chaos_power"])
            bullets.append(bullet)
        
        return bullets
    
    def take_damage(self, damage):
        """Le joueur prend des dégâts (seulement si pas invincible)"""
        if self.invincible_timer <= 0:
            self.health -= damage
            self.invincible_timer = self.invincible_duration
            self.flash_timer = 0
            
            if self.health <= 0:
                self.health = 0
                return True  # Joueur mort
        return False
    
    def draw(self, screen):
        # Effet de clignotement si invincible
        should_draw = True
        if self.invincible_timer > 0:
            # Clignoter toutes les 5 frames
            should_draw = (self.flash_timer // 5) % 2 == 0
        
        if should_draw:
            # Dessiner le joueur en rouge
            pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
        
        # Barre de vie (toujours visible)
        bar_width = self.width
        bar_height = 4
        health_ratio = self.health / self.max_health
        
        # Fond de la barre (rouge foncé)
        pygame.draw.rect(screen, DARK_RED, 
                        (self.x, self.y - 8, bar_width, bar_height))
        # Barre de vie (vert)
        pygame.draw.rect(screen, GREEN, 
                        (self.x, self.y - 8, bar_width * health_ratio, bar_height))