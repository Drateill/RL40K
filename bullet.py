import pygame

# Couleurs
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

class Bullet:
    def __init__(self, x, y, dx, dy, is_player_bullet=True, damage=10, 
                 piercing=False, size_multiplier=1.0, homing=False, explosive=False,
                 holy_damage=False, cursed=False, chaos_power=False):
        self.x = x
        self.y = y
        self.dx = dx * 8  # Vitesse du projectile
        self.dy = dy * 8
        self.radius = int(3 * size_multiplier)
        self.is_player_bullet = is_player_bullet
        self.damage = damage
        self.piercing = piercing
        self.homing = homing
        self.explosive = explosive
        self.has_hit = False  # Pour le piercing
        
        # Nouveaux effets moraux
        self.holy_damage = holy_damage
        self.cursed = cursed
        self.chaos_power = chaos_power
        
        # Couleur selon qui tire et propriétés
        if is_player_bullet:
            if holy_damage:
                self.color = (255, 255, 200)  # Jaune doré pour sacré
            elif cursed:
                self.color = (200, 50, 50)    # Rouge sombre pour maudit
            elif chaos_power:
                self.color = (255, 100, 255)  # Magenta pour chaos
            elif explosive:
                self.color = (255, 100, 0)    # Orange pour explosif
            elif homing:
                self.color = (0, 255, 255)    # Cyan pour homing
            elif piercing:
                self.color = (255, 255, 0)    # Jaune pour piercing
            else:
                self.color = YELLOW
        else:
            self.color = RED
        
        # Rectangle pour les collisions
        self.rect = pygame.Rect(x - self.radius, y - self.radius, 
                               self.radius * 2, self.radius * 2)
    
    def update(self, walls, screen_width, screen_height, enemies=None):
        # Homing: chercher l'ennemi le plus proche
        if self.homing and self.is_player_bullet and enemies:
            closest_enemy = None
            closest_dist = float('inf')
            
            for enemy in enemies:
                dist = ((enemy.x - self.x) ** 2 + (enemy.y - self.y) ** 2) ** 0.5
                if dist < closest_dist and dist < 150:  # Portée de homing
                    closest_dist = dist
                    closest_enemy = enemy
            
            if closest_enemy:
                # Ajuster direction vers l'ennemi
                target_dx = closest_enemy.x - self.x
                target_dy = closest_enemy.y - self.y
                target_length = (target_dx**2 + target_dy**2) ** 0.5
                
                if target_length > 0:
                    target_dx /= target_length
                    target_dy /= target_length
                    
                    # Mélanger direction actuelle et cible (homing progressif)
                    mix_factor = 0.15
                    current_length = (self.dx**2 + self.dy**2) ** 0.5
                    if current_length > 0:
                        current_dx = self.dx / current_length
                        current_dy = self.dy / current_length
                        
                        new_dx = current_dx * (1 - mix_factor) + target_dx * mix_factor
                        new_dy = current_dy * (1 - mix_factor) + target_dy * mix_factor
                        
                        # Normaliser et garder la vitesse
                        new_length = (new_dx**2 + new_dy**2) ** 0.5
                        if new_length > 0:
                            self.dx = (new_dx / new_length) * current_length
                            self.dy = (new_dy / new_length) * current_length
        
        # Déplacer le projectile
        self.x += self.dx
        self.y += self.dy
        self.rect.x = self.x - self.radius
        self.rect.y = self.y - self.radius
        
        # Vérifier collision avec les murs
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                return False  # Le projectile doit être détruit
        
        # Vérifier si hors écran
        if (self.x < 0 or self.x > screen_width or 
            self.y < 0 or self.y > screen_height):
            return False
        
        return True  # Le projectile continue
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Effets visuels selon le type
        if self.explosive and self.is_player_bullet:
            pygame.draw.circle(screen, (255, 200, 0), (int(self.x), int(self.y)), self.radius + 2, 1)
        
        if self.holy_damage and self.is_player_bullet:
            # Aura dorée pour les projectiles sacrés
            pygame.draw.circle(screen, (255, 255, 150), (int(self.x), int(self.y)), self.radius + 1, 1)
        
        if self.cursed and self.is_player_bullet:
            # Aura rouge sombre pour les projectiles maudits
            pygame.draw.circle(screen, (150, 0, 0), (int(self.x), int(self.y)), self.radius + 1, 1)
        
        if self.chaos_power and self.is_player_bullet:
            # Aura chaotique qui change
            import random
            chaos_color = (random.randint(200, 255), random.randint(0, 100), random.randint(200, 255))
            pygame.draw.circle(screen, chaos_color, (int(self.x), int(self.y)), self.radius + 1, 1)