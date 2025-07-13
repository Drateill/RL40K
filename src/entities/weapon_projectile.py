"""
Projectile d'arme modulaire basé sur les configurations JSON
Remplace l'ancienne classe Bullet
"""
import pygame
import math
import random
from typing import Dict, List, Optional, Any

class WeaponProjectile:
    """Projectile créé par le système d'armes modulaire"""
    
    def __init__(self, x: float, y: float, dx: float, dy: float, 
                 weapon_data: Dict, effects_data: Dict, owner=None):
        # Position et mouvement
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        
        # Direction et vitesse
        speed = weapon_data["stats"]["projectile_speed"]
        self.dx = dx * speed
        self.dy = dy * speed
        
        # Spécial pour les armes de corps à corps (speed = 0)
        self.is_melee = (speed == 0)
        if self.is_melee:
            # Sauvegarder la direction pour l'attaque en cône
            import math
            self.attack_direction = math.atan2(dy, dx) if dx != 0 or dy != 0 else 0
            self.dx = 0  # Pas de mouvement
            self.dy = 0
        
        # Données de l'arme et effets
        self.weapon_data = weapon_data
        self.effects_data = effects_data
        self.owner = owner
        
        # Propriétés du projectile
        self.damage = weapon_data["stats"]["damage"]
        self.radius = weapon_data["projectile"]["size"]
        self.color = tuple(weapon_data["projectile"]["color"])
        self.lifetime = weapon_data["projectile"]["lifetime"]
        self.age = 0
        
        # Appliquer les améliorations globales du joueur si disponibles
        if owner and hasattr(owner, 'global_upgrades'):
            # Bonus de dégâts global
            self.damage += owner.global_upgrades.get('damage_bonus', 0)
            
            # Bonus de taille global
            size_multiplier = owner.global_upgrades.get('bullet_size_multiplier', 1.0)
            self.radius = int(self.radius * size_multiplier)
        
        # État
        self.is_alive = True
        self.has_hit_targets = set()  # Pour le piercing
        self.pierce_count = 0
        
        # Rectangle de collision
        self.rect = pygame.Rect(x - self.radius, y - self.radius, 
                               self.radius * 2, self.radius * 2)
        
        # Effets actifs
        self.active_effects = self._parse_effects()
        
        # Propriétés spéciales selon les effets + améliorations globales
        self.piercing = self._has_effect("piercing") or (owner and hasattr(owner, 'global_upgrades') and owner.global_upgrades.get('piercing', False))
        self.explosive = self._has_effect("explosive") or (owner and hasattr(owner, 'global_upgrades') and owner.global_upgrades.get('explosive', False))
        self.homing = self._has_effect("homing") or (owner and hasattr(owner, 'global_upgrades') and owner.global_upgrades.get('homing', False))
        self.max_pierce_count = self._get_effect_param("piercing", "pierce_count", 3)  # Valeur par défaut augmentée
        
        # Variables pour le homing
        self.homing_target = None
        self.tracking_range = self._get_effect_param("homing", "tracking_range", 150)
        self.turn_rate = self._get_effect_param("homing", "turn_rate", 0.15)
        
        # Trail et effets visuels
        self.trail_points = []
        self.has_trail = weapon_data["projectile"].get("trail", False)
        self.max_trail_length = 8
        
        # Debug info seulement pour le premier projectile d'un groupe
        if not hasattr(WeaponProjectile, '_debug_printed'):
            WeaponProjectile._debug_printed = True
            print(f"🚀 Projectile créé: {weapon_data['name']}, dégâts: {self.damage}, perforant: {self.piercing}, explosif: {self.explosive}")
        else:
            # Reset après un délai pour permettre le debug du prochain tir
            import threading
            def reset_debug():
                WeaponProjectile._debug_printed = False
            threading.Timer(0.1, reset_debug).start()
    
    def _parse_effects(self) -> List[Dict]:
        """Parse les effets de l'arme"""
        effects = []
        for effect_name in self.weapon_data.get("effects", []):
            # Chercher l'effet dans toutes les catégories
            for category, category_effects in self.effects_data.items():
                if effect_name in category_effects:
                    effect_data = category_effects[effect_name].copy()
                    effect_data["name"] = effect_name
                    effect_data["category"] = category
                    effects.append(effect_data)
                    break
        return effects
    
    def _has_effect(self, effect_name: str) -> bool:
        """Vérifie si le projectile a un effet spécifique"""
        return any(effect["name"] == effect_name for effect in self.active_effects)
    
    def _get_effect_param(self, effect_name: str, param_name: str, default_value=None):
        """Récupère un paramètre d'effet"""
        for effect in self.active_effects:
            if effect["name"] == effect_name:
                return effect.get("parameters", {}).get(param_name, default_value)
        return default_value
    
    def update(self, walls: List, screen_width: int, screen_height: int, 
               enemies: List = None, game_scene=None) -> bool:
        """Met à jour le projectile"""
        self.age += 1
        
        # Vérifier la durée de vie
        if self.age >= self.lifetime:
            self.is_alive = False
            return False
        
        # Pour les attaques de corps à corps, gérer différemment
        if self.is_melee:
            return self._update_melee_attack(enemies, game_scene)
        
        # Homing vers les ennemis
        if self.homing and enemies and self.owner:
            self._update_homing(enemies)
        
        # Sauvegarder l'ancienne position pour le trail
        if self.has_trail:
            self.trail_points.append((self.x, self.y))
            if len(self.trail_points) > self.max_trail_length:
                self.trail_points.pop(0)
        
        # Déplacer le projectile
        self.x += self.dx
        self.y += self.dy
        self.rect.x = self.x - self.radius
        self.rect.y = self.y - self.radius
        
        # Vérifier collision avec les murs
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                self._handle_wall_collision(wall, game_scene)
                return False
        
        # Vérifier si hors écran
        margin = 100  # Marge pour permettre aux projectiles de sortir un peu
        if (self.x < -margin or self.x > screen_width + margin or 
            self.y < -margin or self.y > screen_height + margin):
            self.is_alive = False
            return False
        
        return self.is_alive
    
    def _update_homing(self, enemies: List):
        """Met à jour le homing du projectile"""
        # Trouver ou maintenir la cible
        if not self.homing_target or self.homing_target not in enemies:
            self.homing_target = self._find_closest_enemy(enemies)
        
        if self.homing_target:
            # Calculer la direction vers la cible
            target_dx = self.homing_target.x - self.x
            target_dy = self.homing_target.y - self.y
            target_distance = math.sqrt(target_dx**2 + target_dy**2)
            
            if target_distance > 0 and target_distance <= self.tracking_range:
                # Normaliser la direction cible
                target_dx /= target_distance
                target_dy /= target_distance
                
                # Direction actuelle normalisée
                current_speed = math.sqrt(self.dx**2 + self.dy**2)
                if current_speed > 0:
                    current_dx = self.dx / current_speed
                    current_dy = self.dy / current_speed
                    
                    # Interpoler vers la cible
                    new_dx = current_dx * (1 - self.turn_rate) + target_dx * self.turn_rate
                    new_dy = current_dy * (1 - self.turn_rate) + target_dy * self.turn_rate
                    
                    # Normaliser et maintenir la vitesse
                    new_length = math.sqrt(new_dx**2 + new_dy**2)
                    if new_length > 0:
                        self.dx = (new_dx / new_length) * current_speed
                        self.dy = (new_dy / new_length) * current_speed
            else:
                # Cible trop loin, la perdre
                self.homing_target = None
    
    def _find_closest_enemy(self, enemies: List):
        """Trouve l'ennemi le plus proche dans la portée"""
        closest_enemy = None
        closest_distance = self.tracking_range
        
        for enemy in enemies:
            distance = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
            if distance < closest_distance:
                closest_distance = distance
                closest_enemy = enemy
        
        return closest_enemy
    
    def _update_melee_attack(self, enemies, game_scene):
        """Met à jour une attaque de corps à corps"""
        if not enemies:
            return self.is_alive
        
        # Attaque en cône autour de la direction d'attaque
        import math
        
        # Paramètres de l'attaque de mêlée
        cone_angle = self._get_effect_param("melee_attack", "cone_angle", 60) * math.pi / 180  # Convertir en radians
        max_range = self.weapon_data["stats"].get("range", 60)
        max_targets = self._get_effect_param("cleave_attack", "max_targets", 3)
        
        targets_hit = 0
        
        for enemy in enemies[:]:  # Copie pour éviter la modification pendant l'itération
            if targets_hit >= max_targets:
                break
                
            if enemy in self.has_hit_targets:
                continue
                
            # Calculer la distance et l'angle vers l'ennemi
            dx = enemy.x - self.x
            dy = enemy.y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > max_range:
                continue
                
            # Calculer l'angle vers l'ennemi
            enemy_angle = math.atan2(dy, dx)
            
            # Calculer la différence d'angle avec la direction d'attaque
            angle_diff = abs(enemy_angle - self.attack_direction)
            
            # Normaliser l'angle (tenir compte du wrap-around)
            if angle_diff > math.pi:
                angle_diff = 2 * math.pi - angle_diff
                
            # Vérifier si l'ennemi est dans le cône d'attaque
            if angle_diff <= cone_angle / 2:
                # Ennemi dans le cône, l'attaquer
                self.hit_enemy(enemy, game_scene)
                targets_hit += 1
                print(f"⚔️  Attaque de mêlée ! Cible {targets_hit}/{max_targets}")
        
        # Les attaques de mêlée se terminent rapidement
        if self.age >= 5:  # Très courte durée de vie
            self.is_alive = False
            return False
            
        return self.is_alive
    
    def _handle_wall_collision(self, wall, game_scene):
        """Gère la collision avec un mur"""
        if self.explosive:
            self._create_explosion(game_scene)
        self.is_alive = False
    
    def hit_enemy(self, enemy, game_scene=None) -> bool:
        """Gère la collision avec un ennemi"""
        # Vérifier si déjà touché (pour le piercing)
        if enemy in self.has_hit_targets:
            return False
        
        # Marquer comme touché
        self.has_hit_targets.add(enemy)
        
        # Calculer les dégâts avec les effets
        final_damage = self._calculate_damage(enemy)
        
        # Appliquer les dégâts
        enemy.take_damage(final_damage)
        
        # Effets spéciaux au contact
        self._apply_hit_effects(enemy, game_scene)
        
        # Vérifier si le projectile doit être détruit
        if self.piercing and self.pierce_count < self.max_pierce_count:
            self.pierce_count += 1
            print(f"🏹 Projectile perforant traverse l'ennemi (hits: {self.pierce_count}/{self.max_pierce_count})")
            
            # Réduire les dégâts pour le prochain hit si configuré
            damage_reduction = self._get_effect_param("piercing", "damage_reduction_per_hit", 0)
            if damage_reduction > 0:
                old_damage = self.damage
                self.damage = max(1, int(self.damage * (1 - damage_reduction)))
                print(f"🏹 Dégâts réduits: {old_damage} → {self.damage}")
            return False  # Ne pas détruire le projectile
        else:
            print(f"💥 Projectile détruit (perforant: {self.piercing}, hits: {self.pierce_count}/{self.max_pierce_count})")
            
            # Explosion si nécessaire
            if self.explosive and game_scene:
                self._create_explosion(game_scene)
            
            self.is_alive = False
            return True  # Détruire le projectile
    
    def _calculate_damage(self, enemy) -> int:
        """Calcule les dégâts finaux avec les modificateurs"""
        damage = self.damage
        
        # Appliquer les modificateurs de dégâts selon les effets
        for effect in self.active_effects:
            if effect["category"] == "damage_effects":
                if effect["name"] == "holy_damage":
                    # Bonus contre les démons et chaos
                    if hasattr(enemy, 'enemy_type'):
                        if enemy.enemy_type in ['demon', 'daemon']:
                            damage *= effect["parameters"].get("damage_multiplier_vs_demon", 1.0)
                        elif enemy.enemy_type in ['chaos', 'heretic']:
                            damage *= effect["parameters"].get("damage_multiplier_vs_chaos", 1.0)
                
                elif effect["name"] == "energy_damage":
                    # Pénétration d'armure
                    armor_pen = effect["parameters"].get("armor_penetration", 0)
                    if hasattr(enemy, 'armor'):
                        effective_armor = enemy.armor * (1 - armor_pen)
                        damage = damage * (1 - effective_armor * 0.01)
        
        return max(1, int(damage))
    
    def _apply_hit_effects(self, enemy, game_scene):
        """Applique les effets spéciaux au contact"""
        for effect in self.active_effects:
            effect_name = effect["name"]
            
            if effect_name == "chaos_corruption":
                # Chance de corrompre
                corruption_chance = effect["parameters"].get("corruption_chance", 0)
                if random.random() < corruption_chance:
                    corruption_amount = effect["parameters"].get("corruption_amount", 5)
                    if hasattr(enemy, 'apply_corruption'):
                        enemy.apply_corruption(corruption_amount)
            
            elif effect_name == "suppression":
                # Ralentir l'ennemi
                speed_reduction = effect["parameters"].get("speed_reduction", 0.3)
                duration = effect["parameters"].get("duration", 90)
                if hasattr(enemy, 'apply_slow'):
                    enemy.apply_slow(speed_reduction, duration)
            
            elif effect_name == "thermal_damage":
                # Dégâts sur la durée
                dot_damage = effect["parameters"].get("damage_over_time", 3)
                duration = effect["parameters"].get("duration", 60)
                if hasattr(enemy, 'apply_burn'):
                    enemy.apply_burn(dot_damage, duration)
    
    def _create_explosion(self, game_scene):
        """Crée une explosion"""
        if not game_scene:
            return
        
        explosion_radius = self._get_effect_param("explosive", "explosion_radius", 50)
        explosion_damage = int(self.damage * self._get_effect_param("explosive", "explosion_damage", 0.5))
        
        # Trouver les ennemis dans le rayon d'explosion
        if hasattr(game_scene, 'entity_manager') and hasattr(game_scene.entity_manager, 'enemies'):
            for enemy in game_scene.entity_manager.enemies[:]:  # Copie pour éviter les modifications
                distance = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
                if distance <= explosion_radius:
                    # Dégâts réduits selon la distance
                    damage_multiplier = 1.0 - (distance / explosion_radius)
                    final_damage = int(explosion_damage * damage_multiplier)
                    if final_damage > 0:
                        enemy.take_damage(final_damage)
        
        # Effet visuel d'explosion (sera ajouté plus tard)
        print(f"💥 Explosion à ({self.x:.0f}, {self.y:.0f}) - Rayon: {explosion_radius}, Dégâts: {explosion_damage}")
    
    def draw(self, screen, camera_offset=(0, 0)):
        """Dessine le projectile"""
        if not self.is_alive:
            return
        
        screen_x = int(self.x - camera_offset[0])
        screen_y = int(self.y - camera_offset[1])
        
        # Pour les attaques de corps à corps, dessiner un arc
        if self.is_melee:
            self._draw_melee_attack(screen, screen_x, screen_y)
            return
        
        # Dessiner le trail si activé
        if self.has_trail and len(self.trail_points) > 1:
            trail_color = [max(0, c - 100) for c in self.color]  # Version plus sombre
            for i in range(len(self.trail_points) - 1):
                alpha = int(255 * (i + 1) / len(self.trail_points))
                start_x = int(self.trail_points[i][0] - camera_offset[0])
                start_y = int(self.trail_points[i][1] - camera_offset[1])
                end_x = int(self.trail_points[i + 1][0] - camera_offset[0])
                end_y = int(self.trail_points[i + 1][1] - camera_offset[1])
                
                if 0 <= alpha <= 255:
                    trail_surface = pygame.Surface((abs(end_x - start_x) + 2, abs(end_y - start_y) + 2))
                    trail_surface.set_alpha(alpha)
                    trail_surface.fill(trail_color)
                    pygame.draw.line(trail_surface, trail_color, (0, 0), 
                                   (end_x - start_x, end_y - start_y), 2)
                    screen.blit(trail_surface, (min(start_x, end_x), min(start_y, end_y)))
        
        # Dessiner le projectile principal
        pygame.draw.circle(screen, self.color, (screen_x, screen_y), self.radius)
        
        # Effets visuels selon les propriétés
        self._draw_visual_effects(screen, screen_x, screen_y)
    
    def _draw_melee_attack(self, screen, screen_x, screen_y):
        """Dessine une attaque de corps à corps sous forme d'arc"""
        import math
        
        # Paramètres de l'arc d'attaque
        cone_angle = self._get_effect_param("melee_attack", "cone_angle", 60) * math.pi / 180
        max_range = self.weapon_data["stats"].get("range", 60)
        
        # Calculer les points de l'arc
        start_angle = self.attack_direction - cone_angle / 2
        end_angle = self.attack_direction + cone_angle / 2
        
        # Dessiner l'arc d'attaque
        arc_color = self.color
        if self.age <= 2:  # Flash initial plus brillant
            arc_color = tuple(min(255, c + 100) for c in self.color)
        
        # Dessiner des lignes pour représenter l'arc
        num_lines = 8
        for i in range(num_lines):
            angle = start_angle + (end_angle - start_angle) * i / (num_lines - 1)
            end_x = screen_x + int(max_range * math.cos(angle))
            end_y = screen_y + int(max_range * math.sin(angle))
            
            # Ligne de l'arc
            pygame.draw.line(screen, arc_color, (screen_x, screen_y), (end_x, end_y), 3)
        
        # Dessiner l'arc extérieur
        if hasattr(pygame, 'gfxdraw'):
            import pygame.gfxdraw
            try:
                pygame.gfxdraw.arc(screen, screen_x, screen_y, int(max_range), 
                                 int(start_angle * 180 / math.pi), int(end_angle * 180 / math.pi), arc_color)
            except:
                pass  # Fallback si gfxdraw n'est pas disponible
    
    def _draw_visual_effects(self, screen, screen_x, screen_y):
        """Dessine les effets visuels du projectile"""
        for effect in self.active_effects:
            effect_name = effect["name"]
            
            if effect_name == "holy_damage":
                # Aura dorée
                pygame.draw.circle(screen, (255, 255, 150), (screen_x, screen_y), self.radius + 2, 1)
                if self.age % 10 < 5:  # Pulsation
                    pygame.draw.circle(screen, (255, 255, 200), (screen_x, screen_y), self.radius + 1, 1)
            
            elif effect_name == "chaos_corruption":
                # Aura chaotique
                chaos_colors = [(255, 100, 255), (200, 0, 200), (255, 0, 255)]
                color = chaos_colors[self.age % len(chaos_colors)]
                pygame.draw.circle(screen, color, (screen_x, screen_y), self.radius + 1, 1)
            
            elif effect_name == "energy_damage":
                # Éclairs d'énergie
                if self.age % 5 == 0:
                    for _ in range(3):
                        spark_x = screen_x + random.randint(-self.radius-2, self.radius+2)
                        spark_y = screen_y + random.randint(-self.radius-2, self.radius+2)
                        pygame.draw.circle(screen, (0, 255, 255), (spark_x, spark_y), 1)
            
            elif self.explosive:
                # Anneau d'explosion
                pygame.draw.circle(screen, (255, 200, 0), (screen_x, screen_y), self.radius + 2, 1)
    
    def get_rect(self) -> pygame.Rect:
        """Retourne le rectangle de collision"""
        return self.rect