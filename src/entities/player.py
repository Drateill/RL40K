import pygame
import math
from ..systems.weapon_manager import WeaponManager, Weapon

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
        self.health = 80  # Moins de PV pour plus de challenge
        self.max_health = 80
        
        # Rectangle pour les collisions
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # Nouveau système d'armes multi-armes
        self.weapon_manager = WeaponManager()
        self.weapons = [Weapon("bolter_basic", self.weapon_manager)]  # Liste des armes possédées
        self.current_weapon_index = 0  # Index de l'arme active
        self.current_weapon = self.weapons[0]  # Arme actuellement équipée
        self.obtained_weapon_ids = {"bolter_basic"}  # Set des IDs d'armes obtenues
        
        # Améliorations globales qui affectent toutes les armes
        self.global_upgrades = {
            "damage_bonus": 0,
            "fire_rate_multiplier": 1.0,
            "multi_shot_bonus": 0,
            "piercing": False,
            "explosive": False,
            "homing": False,
            "bullet_size_multiplier": 1.0,
            "speed_bonus": 0,
            "accuracy_bonus": 0.0
        }
        
        # Système d'invincibilité
        self.invincible_timer = 0
        self.invincible_duration = 60  # 1 seconde d'invincibilité à 60 FPS
        self.flash_timer = 0
        
        # Régénération de vie (conservée car non dupliquée)
        self.health_regen = 0
        # Note: Tous les autres attributs legacy (base_damage, multi_shot, piercing, etc.) 
        # ont été supprimés car ils sont maintenant gérés par global_upgrades
        
        # Statistiques de base pour les effets de moralité
        self.base_max_health = self.max_health
        self.morality_speed_modifier = 1.0
    
    def update(self, walls, morality_system=None):
        # Mettre à jour toutes les armes
        for weapon in self.weapons:
            weapon.update()
        
        # Gestion des inputs
        keys = pygame.key.get_pressed()
        
        # Changement d'arme avec touches numériques (1, 2, 3, etc.)
        if not hasattr(self, '_last_weapon_keys'):
            self._last_weapon_keys = [False] * 9
        
        for i in range(min(len(self.weapons), 9)):  # Max 9 armes (touches 1-9)
            key_pressed = keys[pygame.K_1 + i]
            if key_pressed and not self._last_weapon_keys[i]:  # Nouveau press
                if i != self.current_weapon_index:
                    self.switch_weapon(i)
            self._last_weapon_keys[i] = key_pressed
        
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
        
        # Rechargement manuel avec touche R
        if keys[pygame.K_r]:
            if not hasattr(self, '_reload_key_pressed'):
                self._reload_key_pressed = True
                if self.current_weapon:
                    self.current_weapon.start_reload()
                    weapon_info = self.current_weapon.get_info()
                    if weapon_info.get('max_ammo', -1) > 0:
                        print(f"🔄 Rechargement manuel: {weapon_info['name']}")
        else:
            self._reload_key_pressed = False
        
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
        
        # Timer de tir legacy supprimé - maintenant géré par chaque arme individuellement
            
        # Décrémenter le timer d'invincibilité
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
            self.flash_timer += 1
        
        # Régénération de vie
        if self.health_regen > 0 and self.health < self.max_health:
            self.health += self.health_regen
            self.health = min(self.health, self.max_health)
    
    def try_shoot(self, mouse_pos, morality_system=None):
        """Tente de tirer avec l'arme actuelle"""
        if not self.current_weapon or not self.current_weapon.can_fire():
            return []
        
        # Position de départ du tir
        start_x = self.x + self.width // 2
        start_y = self.y + self.height // 2
        
        # Tirer avec l'arme
        projectiles = self.current_weapon.fire(start_x, start_y, mouse_pos[0], mouse_pos[1], self)
        
        return projectiles
    
    # shoot_legacy supprimée - remplacée par try_shoot() avec le système d'armes modulaire
    
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
    
    # === NOUVELLES MÉTHODES POUR LE SYSTÈME MULTI-ARMES ===
    
    def add_weapon(self, weapon_id: str, morality_system=None) -> bool:
        """Ajoute une nouvelle arme à l'inventaire du joueur"""
        # Vérifier si déjà possédée
        if weapon_id in self.obtained_weapon_ids:
            print(f"❌ Arme {weapon_id} déjà possédée")
            return False
        
        # Vérifier disponibilité
        if not self.weapon_manager.is_weapon_available(weapon_id, morality_system):
            print(f"❌ Arme {weapon_id} non disponible avec moralité actuelle")
            return False
        
        try:
            new_weapon = Weapon(weapon_id, self.weapon_manager)
            self.weapons.append(new_weapon)
            self.obtained_weapon_ids.add(weapon_id)
            
            # Appliquer les améliorations globales à la nouvelle arme
            self._apply_global_upgrades_to_weapon(new_weapon)
            
            print(f"🔫 Nouvelle arme obtenue: {new_weapon.weapon_data['name']} (#{len(self.weapons)})")
            return True
        except ValueError as e:
            print(f"❌ Erreur ajout d'arme: {e}")
            return False
    
    def switch_weapon(self, weapon_index: int):
        """Change l'arme active"""
        if 0 <= weapon_index < len(self.weapons):
            old_weapon = self.current_weapon.weapon_data['name'] if self.current_weapon else "Aucune"
            self.current_weapon_index = weapon_index
            self.current_weapon = self.weapons[weapon_index]
            new_weapon = self.current_weapon.weapon_data['name']
            print(f"🔄 Changement d'arme: {old_weapon} → {new_weapon}")
    
    def change_weapon(self, weapon_id: str, morality_system=None) -> bool:
        """LEGACY: Change l'arme du joueur (remplacé par add_weapon)"""
        return self.add_weapon(weapon_id, morality_system)
    
    def get_current_weapon_info(self) -> dict:
        """Retourne les informations de l'arme actuelle"""
        if self.current_weapon:
            return self.current_weapon.get_info()
        return {"name": "Aucune arme", "can_fire": False}
    
    def reload_weapon(self):
        """Recharge l'arme actuelle"""
        if self.current_weapon:
            self.current_weapon.start_reload()
    
    def get_available_weapons(self, morality_system=None) -> list:
        """Retourne la liste des armes disponibles"""
        return self.weapon_manager.get_available_weapons(morality_system)
    
    def get_weapon_upgrades(self) -> list:
        """Retourne les améliorations possibles pour l'arme actuelle"""
        if self.current_weapon:
            return self.weapon_manager.get_weapon_upgrades(self.current_weapon.weapon_id)
        return []
    
    # === SYSTÈME D'AMÉLIORATIONS GLOBALES ===
    
    def apply_global_upgrade(self, upgrade_type: str, value):
        """Applique une amélioration globale à toutes les armes"""
        if upgrade_type == "damage":
            self.global_upgrades["damage_bonus"] += value
        elif upgrade_type == "fire_rate":
            self.global_upgrades["fire_rate_multiplier"] *= value
        elif upgrade_type == "multi_shot":
            self.global_upgrades["multi_shot_bonus"] += value
        elif upgrade_type == "piercing":
            self.global_upgrades["piercing"] = True
        elif upgrade_type == "explosive":
            self.global_upgrades["explosive"] = True
        elif upgrade_type == "homing":
            self.global_upgrades["homing"] = True
        elif upgrade_type == "bullet_size":
            self.global_upgrades["bullet_size_multiplier"] *= value
        elif upgrade_type == "speed":
            self.speed += value
            self.global_upgrades["speed_bonus"] += value
        elif upgrade_type == "accuracy":
            self.global_upgrades["accuracy_bonus"] += value
        
        # Appliquer aux armes existantes
        for weapon in self.weapons:
            self._apply_global_upgrades_to_weapon(weapon)
        
        print(f"🌟 Amélioration globale appliquée: {upgrade_type} (+{value})")
        print(f"   Affecte {len(self.weapons)} arme(s)")
    
    def _apply_global_upgrades_to_weapon(self, weapon):
        """Applique les améliorations globales à une arme spécifique"""
        # Réinitialiser les stats modifiées avec les stats de base
        weapon.modified_stats = weapon.weapon_data["stats"].copy()
        
        # Appliquer les bonus globaux
        weapon.modified_stats["damage"] += self.global_upgrades["damage_bonus"]
        weapon.modified_stats["fire_rate"] = int(weapon.modified_stats["fire_rate"] * self.global_upgrades["fire_rate_multiplier"])
        weapon.modified_stats["fire_rate"] = max(1, weapon.modified_stats["fire_rate"])
        
        # Accuracy bonus
        weapon.modified_stats["accuracy"] = min(1.0, weapon.modified_stats["accuracy"] + self.global_upgrades["accuracy_bonus"])
    
    def get_available_weapons_for_upgrade(self, morality_system=None) -> list:
        """Retourne les armes disponibles qui ne sont pas encore possédées"""
        all_available = self.weapon_manager.get_available_weapons(morality_system)
        return [weapon_id for weapon_id in all_available if weapon_id not in self.obtained_weapon_ids]
    
    def get_weapons_info(self) -> list:
        """Retourne les informations de toutes les armes possédées"""
        weapons_info = []
        for i, weapon in enumerate(self.weapons):
            info = weapon.get_info()
            info["index"] = i
            info["is_active"] = (i == self.current_weapon_index)
            weapons_info.append(info)
        return weapons_info