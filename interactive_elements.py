"""
Système d'éléments interactifs pour les environnements
Portes, machines, consoles, pièges et objets spéciaux
"""

import pygame
import random
import math
from typing import List, Callable, Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass

class InteractionType(Enum):
    """Types d'interactions possibles"""
    DOOR = "door"
    CONSOLE = "console"
    MACHINE = "machine"
    TRAP = "trap"
    HEALING_SHRINE = "shrine"
    CORRUPTION_ALTAR = "altar"
    TELEPORTER = "teleporter"
    LOOT_CONTAINER = "loot"
    ENVIRONMENTAL_HAZARD = "hazard"

@dataclass
class InteractionResult:
    """Résultat d'une interaction"""
    success: bool
    message: str
    effects: Dict[str, Any] = None
    sound_effect: str = None
    visual_effect: str = None

class InteractiveElement:
    """Classe de base pour tous les éléments interactifs"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 interaction_type: InteractionType, name: str):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        
        self.interaction_type = interaction_type
        self.name = name
        self.description = ""
        
        # État de l'élément
        self.active = True
        self.used = False
        self.uses_remaining = -1  # -1 = illimité
        
        # Visuels
        self.color = (100, 100, 100)
        self.highlight_color = (150, 150, 150)
        self.is_highlighted = False
        
        # Animation
        self.animation_timer = 0
        self.pulse_speed = 0.05
        
        # Conditions d'utilisation
        self.morality_requirement = None  # (type, min_value) ex: ("faith", 30)
        self.level_requirement = None
        self.item_requirement = None
        
        # Cooldown
        self.cooldown = 0
        self.max_cooldown = 0
    
    def can_interact(self, player, morality_system=None, exp_system=None) -> tuple:
        """
        Vérifie si le joueur peut interagir avec cet élément
        Returns: (can_interact: bool, reason: str)
        """
        if not self.active:
            return False, "Élément inactif"
        
        if self.cooldown > 0:
            return False, f"Rechargement... ({self.cooldown}s)"
        
        if self.uses_remaining == 0:
            return False, "Plus d'utilisations disponibles"
        
        # Vérifier les prérequis de moralité
        if self.morality_requirement and morality_system:
            req_type, min_value = self.morality_requirement
            current_value = getattr(morality_system, req_type, 0)
            if current_value < min_value:
                return False, f"Nécessite {min_value} {req_type}"
        
        # Vérifier le niveau
        if self.level_requirement and exp_system:
            if exp_system.level < self.level_requirement:
                return False, f"Nécessite niveau {self.level_requirement}"
        
        return True, "Peut interagir"
    
    def interact(self, player, morality_system=None, exp_system=None, 
                item_manager=None) -> InteractionResult:
        """Exécute l'interaction - À override dans les classes filles"""
        return InteractionResult(False, "Interaction non implémentée")
    
    def update(self):
        """Met à jour l'élément"""
        self.animation_timer += 1
        
        if self.cooldown > 0:
            self.cooldown -= 1/60  # Assuming 60 FPS
    
    def draw(self, screen: pygame.Surface):
        """Dessine l'élément de base"""
        color = self.highlight_color if self.is_highlighted else self.color
        
        # Pulsation si actif
        if self.active and self.uses_remaining != 0:
            # Réduire la vitesse et l'intensité du pulse
            pulse = abs(math.sin(self.animation_timer * 0.02)) * 0.3  # Beaucoup plus lent
            color = tuple(min(255, int(c + pulse * 20)) for c in color)
        
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2)
    
    def draw_interaction_hint(self, screen: pygame.Surface, font):
        """Dessine l'indication d'interaction"""
        if self.is_highlighted:
            hint_text = font.render(f"[E] {self.name}", True, (255, 255, 255))
            hint_rect = hint_text.get_rect(centerx=self.rect.centerx, 
                                         bottom=self.rect.top - 5)
            
            # Fond semi-transparent
            bg_rect = hint_rect.inflate(10, 4)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
            bg_surface.set_alpha(180)
            bg_surface.fill((0, 0, 0))
            screen.blit(bg_surface, bg_rect)
            
            screen.blit(hint_text, hint_rect)

class Door(InteractiveElement):
    """Porte interactive qui peut s'ouvrir/fermer"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 is_locked: bool = False, requires_key: bool = False):
        super().__init__(x, y, width, height, InteractionType.DOOR, "Porte")
        
        self.is_open = False
        self.is_locked = is_locked
        self.requires_key = requires_key
        self.door_type = "normal"  # "normal", "blast", "security"
        
        self.color = (120, 80, 40) if not is_locked else (80, 80, 120)
        self.highlight_color = (150, 100, 50) if not is_locked else (100, 100, 150)
        
        # Animation d'ouverture
        self.opening_animation = 0
        self.is_animating = False
    
    def interact(self, player, morality_system=None, exp_system=None, 
                item_manager=None) -> InteractionResult:
        
        if self.is_locked:
            if self.requires_key:
                # Vérifier si le joueur a une clé
                # TODO: Système d'inventaire pour les clés
                return InteractionResult(False, "Porte verrouillée - Clé requise")
            else:
                # Tentative de piratage/forçage
                hack_chance = 0.3  # 30% de base
                if morality_system and morality_system.corruption >= 30:
                    hack_chance += 0.2  # Bonus corruption
                
                if random.random() < hack_chance:
                    self.is_locked = False
                    return InteractionResult(True, "Porte piratée avec succès !",
                                           sound_effect="hack_success")
                else:
                    return InteractionResult(False, "Échec du piratage",
                                           sound_effect="hack_fail")
        
        # Ouvrir/fermer la porte
        self.is_open = not self.is_open
        self.is_animating = True
        self.opening_animation = 0
        
        action = "ouverte" if self.is_open else "fermée"
        return InteractionResult(True, f"Porte {action}",
                               sound_effect="door_open" if self.is_open else "door_close")
    
    def update(self):
        super().update()
        
        if self.is_animating:
            self.opening_animation += 2
            if self.opening_animation >= 20:
                self.is_animating = False
    
    def draw(self, screen: pygame.Surface):
        if not self.is_open:
            super().draw(screen)
            
            # Indicateur de verrouillage
            if self.is_locked:
                lock_color = (255, 255, 0)
                lock_pos = (self.rect.centerx, self.rect.centery)
                pygame.draw.circle(screen, lock_color, lock_pos, 5)
        else:
            # Porte ouverte - juste les contours
            pygame.draw.rect(screen, (100, 100, 100), self.rect, 2)

class TechConsole(InteractiveElement):
    """Console technologique avec différentes fonctions"""
    
    def __init__(self, x: int, y: int, console_function: str = "info"):
        super().__init__(x, y, 40, 30, InteractionType.CONSOLE, "Console")
        
        self.console_function = console_function  # "info", "hack", "upgrade", "map"
        self.uses_remaining = 3 if console_function == "upgrade" else -1
        
        self.color = (0, 100, 150)
        self.highlight_color = (0, 150, 200)
        self.pulse_speed = 0.08
        
        # Fonctions spécifiques
        self.info_data = self._generate_info_data()
    
    def _generate_info_data(self) -> List[str]:
        """Génère des données d'information aléatoires"""
        ship_logs = [
            "Log: Système de navigation opérationnel",
            "Alerte: Présence xenos détectée secteur 7",
            "Rapport: Moral des troupes en baisse",
            "Status: Réacteur à 87% de capacité",
            "Warning: Corruption du Warp détectée"
        ]
        
        temple_data = [
            "Prière: L'Empereur protège les fidèles",
            "Relique: Manuscrit de Saint Celestine",
            "Rite: Purification en cours...",
            "Oracle: Les ténèbres approchent",
            "Hymne: Ave Imperator Gloria"
        ]
        
        forge_specs = [
            "Spec: Plasma coil à 94% d'efficacité",
            "Production: 1,247 bolters/jour",
            "Maintenance: Serviteur #4471 en panne",
            "Qualité: Tolérance ±0.001mm",
            "Bénédiction: Machine-Esprit apaisé"
        ]
        
        return random.choice([ship_logs, temple_data, forge_specs])
    
    def interact(self, player, morality_system=None, exp_system=None, 
                item_manager=None) -> InteractionResult:
        
        if self.console_function == "info":
            info = random.choice(self.info_data)
            return InteractionResult(True, f"Console: {info}")
        
        elif self.console_function == "hack":
            if morality_system and morality_system.corruption >= 20:
                # Bonus d'expérience pour les corrompus
                if exp_system:
                    exp_system.add_experience(15)
                morality_system.add_corruption(2, "Piratage de console")
                return InteractionResult(True, "Données piratées ! +15 XP",
                                       effects={"exp": 15, "corruption": 2})
            else:
                return InteractionResult(False, "Accès refusé - Autorisation insuffisante")
        
        elif self.console_function == "upgrade" and self.uses_remaining > 0:
            # Amélioration d'arme temporaire
            self.uses_remaining -= 1
            return InteractionResult(True, f"Arme améliorée ! ({self.uses_remaining} utilisations restantes)",
                                   effects={"weapon_upgrade": True})
        
        elif self.console_function == "map":
            return InteractionResult(True, "Carte téléchargée - Ennemis révélés !",
                                   effects={"reveal_enemies": 300})  # 5 secondes
        
        return InteractionResult(False, "Console non fonctionnelle")
    
    def draw(self, screen: pygame.Surface):
        super().draw(screen)
        
        # Écran de la console
        screen_rect = pygame.Rect(self.rect.x + 5, self.rect.y + 5, 
                                self.rect.width - 10, self.rect.height - 15)
        screen_color = (0, 200, 100) if self.active else (100, 100, 100)
        pygame.draw.rect(screen, screen_color, screen_rect)
        
        # Indicateur de fonction
        if self.console_function == "upgrade" and self.uses_remaining >= 0:
            font = pygame.font.Font(None, 16)
            uses_text = font.render(str(self.uses_remaining), True, (255, 255, 255))
            screen.blit(uses_text, (self.rect.right - 12, self.rect.bottom - 15))

class IndustrialMachine(InteractiveElement):
    """Machine industrielle avec différents effets"""
    
    def __init__(self, x: int, y: int, machine_type: str = "fabricator"):
        super().__init__(x, y, 60, 50, InteractionType.MACHINE, "Machine")
        
        self.machine_type = machine_type  # "fabricator", "recycler", "purifier", "corrupted"
        self.fuel = 100
        self.max_fuel = 100
        self.consumption_rate = 10
        
        if machine_type == "corrupted":
            self.color = (120, 0, 120)
            self.highlight_color = (150, 0, 150)
        else:
            self.color = (150, 100, 50)
            self.highlight_color = (180, 120, 60)
        
        self.max_cooldown = 300  # 5 secondes
    
    def interact(self, player, morality_system=None, exp_system=None, 
                item_manager=None) -> InteractionResult:
        
        if self.fuel < self.consumption_rate:
            return InteractionResult(False, "Machine à court de carburant")
        
        self.fuel -= self.consumption_rate
        self.cooldown = self.max_cooldown
        
        if self.machine_type == "fabricator":
            # Crée un objet aléatoire
            if item_manager:
                item_manager.spawn_item(self.x, self.y - 40, morality_system)
            return InteractionResult(True, "Objet fabriqué !",
                                   sound_effect="machine_work",
                                   visual_effect="sparks")
        
        elif self.machine_type == "recycler":
            # Convertit la santé en expérience
            if player.health < player.max_health:
                heal_amount = min(20, player.max_health - player.health)
                player.health += heal_amount
                if exp_system:
                    exp_system.add_experience(5)
                return InteractionResult(True, f"Réparations effectuées ! +{heal_amount} PV, +5 XP")
            else:
                return InteractionResult(False, "Réparations non nécessaires")
        
        elif self.machine_type == "purifier":
            # Réduit la corruption
            if morality_system and morality_system.corruption > 0:
                purify_amount = min(15, morality_system.corruption)
                morality_system.corruption -= purify_amount
                morality_system.add_faith(5, "Purification par machine")
                return InteractionResult(True, f"Purification effectuée ! -{purify_amount} Corruption, +5 Foi")
            else:
                return InteractionResult(False, "Purification non nécessaire")
        
        elif self.machine_type == "corrupted":
            # Machine corrompue - effets aléatoires
            roll = random.random()
            if roll < 0.3:
                # Bonus de corruption
                if morality_system:
                    morality_system.add_corruption(10, "Machine corrompue")
                player.base_damage += 5
                return InteractionResult(True, "Puissance chaotique ! +5 Dégâts, +10 Corruption",
                                       visual_effect="chaos_energy")
            elif roll < 0.6:
                # Dégâts
                damage = 15
                player.take_damage(damage)
                return InteractionResult(True, f"La machine vous blesse ! -{damage} PV",
                                       visual_effect="electric_shock")
            else:
                # Téléportation aléatoire
                return InteractionResult(True, "Téléportation chaotique !",
                                       effects={"random_teleport": True},
                                       visual_effect="warp_energy")
        
        return InteractionResult(False, "Machine défaillante")
    
    def draw(self, screen: pygame.Surface):
        super().draw(screen)
        
        # Tuyaux et détails
        pipe_color = (80, 80, 80)
        pygame.draw.line(screen, pipe_color, 
                        (self.rect.left, self.rect.centery),
                        (self.rect.right, self.rect.centery), 3)
        
        # Barre de carburant
        fuel_ratio = self.fuel / self.max_fuel
        fuel_width = int(self.rect.width * fuel_ratio)
        fuel_color = (0, 255, 0) if fuel_ratio > 0.5 else (255, 255, 0) if fuel_ratio > 0.2 else (255, 0, 0)
        
        pygame.draw.rect(screen, (50, 50, 50), 
                        (self.rect.x, self.rect.bottom + 2, self.rect.width, 4))
        pygame.draw.rect(screen, fuel_color,
                        (self.rect.x, self.rect.bottom + 2, fuel_width, 4))

class Trap(InteractiveElement):
    """Piège caché qui se déclenche au passage"""
    
    def __init__(self, x: int, y: int, trap_type: str = "spikes"):
        super().__init__(x, y, 40, 40, InteractionType.TRAP, "Piège")
        
        self.trap_type = trap_type  # "spikes", "gas", "electric", "warp"
        self.is_hidden = True
        self.is_triggered = False
        self.detection_range = 30
        
        # Les pièges ne sont pas visibles tant qu'ils ne sont pas découverts
        self.color = (100, 50, 50)
        self.highlight_color = (150, 75, 75)
        
        # Dégâts et effets
        self.damage = {"spikes": 20, "gas": 10, "electric": 15, "warp": 25}[trap_type]
        self.special_effect = {"spikes": None, "gas": "poison", "electric": "stun", "warp": "teleport"}[trap_type]
    
    def check_trigger(self, player) -> bool:
        """Vérifie si le piège doit se déclencher"""
        if self.is_triggered or not self.active:
            return False
        
        distance = math.sqrt((player.x - self.x)**2 + (player.y - self.y)**2)
        return distance <= self.detection_range
    
    def trigger(self, player, morality_system=None) -> InteractionResult:
        """Déclenche le piège"""
        if self.is_triggered:
            return InteractionResult(False, "Piège déjà déclenché")
        
        self.is_triggered = True
        self.is_hidden = False
        
        # Appliquer les dégâts
        actual_damage = self.damage
        
        # Réduction selon la moralité (les purs résistent mieux)
        if morality_system and morality_system.faith >= 60:
            actual_damage = int(actual_damage * 0.7)
        
        player.take_damage(actual_damage)
        
        message = f"Piège {self.trap_type} ! -{actual_damage} PV"
        effects = {}
        
        # Effets spéciaux
        if self.special_effect == "poison":
            effects["poison"] = 180  # 3 secondes d'empoisonnement
            message += " (Empoisonné !)"
        elif self.special_effect == "stun":
            effects["stun"] = 120  # 2 secondes de ralentissement
            message += " (Étourdi !)"
        elif self.special_effect == "teleport":
            effects["random_teleport"] = True
            message += " (Téléportation !)"
        
        return InteractionResult(True, message, effects=effects,
                               sound_effect=f"trap_{self.trap_type}",
                               visual_effect=f"trap_{self.trap_type}_effect")
    
    def interact(self, player, morality_system=None, exp_system=None, 
                item_manager=None) -> InteractionResult:
        """Interaction directe (désarmement)"""
        if self.is_triggered:
            return InteractionResult(False, "Piège déjà déclenché")
        
        disarm_chance = 0.5  # 50% de base
        
        # Bonus selon l'expérience et la moralité
        if exp_system and exp_system.level >= 5:
            disarm_chance += 0.2
        if morality_system and morality_system.corruption >= 40:
            disarm_chance += 0.15  # Les corrompus sont plus habiles avec les pièges
        
        if random.random() < disarm_chance:
            self.active = False
            self.is_hidden = False
            if exp_system:
                exp_system.add_experience(10)
            return InteractionResult(True, "Piège désarmé ! +10 XP",
                                   effects={"exp": 10})
        else:
            # Échec = déclenchement
            return self.trigger(player, morality_system)
    
    def draw(self, screen: pygame.Surface):
        if self.is_hidden and not self.is_triggered:
            # Piège caché - à peine visible
            hidden_color = tuple(max(0, c - 50) for c in self.color)
            pygame.draw.rect(screen, hidden_color, self.rect)
        elif self.is_triggered:
            # Piège déclenché - très visible
            danger_color = (200, 50, 50)
            pygame.draw.rect(screen, danger_color, self.rect)
            
            # Effet visuel selon le type
            if self.trap_type == "spikes":
                # Dessiner des pointes
                for i in range(3):
                    spike_x = self.rect.x + 10 + i * 10
                    spike_points = [
                        (spike_x, self.rect.bottom),
                        (spike_x + 5, self.rect.y + 10),
                        (spike_x + 10, self.rect.bottom)
                    ]
                    pygame.draw.polygon(screen, (150, 150, 150), spike_points)
            
            elif self.trap_type == "gas":
                # Nuage de gaz
                gas_color = (100, 200, 100, 100)
                gas_surface = pygame.Surface((self.rect.width + 20, self.rect.height + 20))
                gas_surface.set_alpha(100)
                gas_surface.fill((100, 200, 100))
                screen.blit(gas_surface, (self.rect.x - 10, self.rect.y - 10))
        else:
            # Piège découvert mais pas déclenché
            super().draw(screen)

class HealingShrine(InteractiveElement):
    """Sanctuaire de guérison pour les fidèles"""
    
    def __init__(self, x: int, y: int):
        super().__init__(x, y, 50, 60, InteractionType.HEALING_SHRINE, "Sanctuaire")
        
        self.morality_requirement = ("faith", 30)
        self.uses_remaining = 3
        self.healing_power = 40
        
        self.color = (200, 200, 100)
        self.highlight_color = (255, 255, 150)
        self.pulse_speed = 0.03  # Pulsation lente et apaisante
    
    def interact(self, player, morality_system=None, exp_system=None, 
                item_manager=None) -> InteractionResult:
        
        if player.health >= player.max_health:
            return InteractionResult(False, "Vous êtes déjà en pleine santé")
        
        # Calcul de la guérison selon la foi
        heal_amount = self.healing_power
        if morality_system:
            faith_bonus = min(20, morality_system.faith // 5)
            heal_amount += faith_bonus
        
        # Appliquer la guérison
        actual_heal = min(heal_amount, player.max_health - player.health)
        player.health += actual_heal
        
        # Bonus de foi
        if morality_system:
            morality_system.add_faith(3, "Prière au sanctuaire")
        
        self.uses_remaining -= 1
        if self.uses_remaining <= 0:
            self.active = False
        
        return InteractionResult(True, f"L'Empereur vous bénit ! +{actual_heal} PV, +3 Foi",
                               sound_effect="holy_healing",
                               visual_effect="divine_light")
    
    def draw(self, screen: pygame.Surface):
        # Base du sanctuaire
        super().draw(screen)
        
        # Symbole impérial
        center_x = self.rect.centerx
        center_y = self.rect.centery
        
        # Aigle impérial simplifié (croix)
        cross_size = 15
        cross_color = (255, 215, 0)
        
        # Croix verticale
        pygame.draw.line(screen, cross_color,
                        (center_x, center_y - cross_size),
                        (center_x, center_y + cross_size), 3)
        # Croix horizontale
        pygame.draw.line(screen, cross_color,
                        (center_x - cross_size, center_y),
                        (center_x + cross_size, center_y), 3)
        
        # Aura sainte
        if self.active:
            aura_radius = int(25 + math.sin(self.animation_timer * self.pulse_speed) * 5)
            aura_surface = pygame.Surface((aura_radius * 2, aura_radius * 2))
            aura_surface.set_alpha(30)
            aura_surface.fill((255, 255, 200))
            screen.blit(aura_surface, (center_x - aura_radius, center_y - aura_radius))

class CorruptionAltar(InteractiveElement):
    """Autel de corruption pour gagner en puissance chaotique"""
    
    def __init__(self, x: int, y: int):
        super().__init__(x, y, 55, 45, InteractionType.CORRUPTION_ALTAR, "Autel du Chaos")
        
        self.morality_requirement = ("corruption", 20)
        self.uses_remaining = 5
        
        self.color = (120, 0, 120)
        self.highlight_color = (150, 0, 150)
        self.pulse_speed = 0.07  # Pulsation inquiétante
    
    def interact(self, player, morality_system=None, exp_system=None, 
                item_manager=None) -> InteractionResult:
        
        # Sacrifice de santé pour pouvoir
        sacrifice_health = min(15, player.health - 1)  # Ne peut pas tuer
        player.health -= sacrifice_health
        
        # Gains chaotiques
        damage_bonus = sacrifice_health // 3
        player.base_damage += damage_bonus
        
        if morality_system:
            corruption_gain = sacrifice_health // 2
            morality_system.add_corruption(corruption_gain, "Sacrifice à l'autel du Chaos")
        
        self.uses_remaining -= 1
        if self.uses_remaining <= 0:
            self.active = False
        
        return InteractionResult(True, f"Puissance chaotique ! +{damage_bonus} Dégâts, -{sacrifice_health} PV",
                               sound_effect="chaos_whisper",
                               visual_effect="corruption_energy")
    
    def draw(self, screen: pygame.Surface):
        super().draw(screen)
        
        # Symboles chaotiques
        center_x = self.rect.centerx
        center_y = self.rect.centery
        
        # Étoile du chaos
        star_size = 12
        chaos_color = (200, 0, 200)
        
        for i in range(8):
            angle = (i / 8) * 2 * math.pi
            end_x = center_x + math.cos(angle) * star_size
            end_y = center_y + math.sin(angle) * star_size
            pygame.draw.line(screen, chaos_color,
                           (center_x, center_y), (end_x, end_y), 2)
        
        # Aura chaotique
        if self.active:
            pulse = abs(math.sin(self.animation_timer * self.pulse_speed))
            aura_radius = int(20 + pulse * 10)
            aura_surface = pygame.Surface((aura_radius * 2, aura_radius * 2))
            aura_surface.set_alpha(int(40 + pulse * 20))
            aura_surface.fill((150, 0, 150))
            screen.blit(aura_surface, (center_x - aura_radius, center_y - aura_radius))

class InteractiveElementManager:
    """Gestionnaire des éléments interactifs"""
    
    def __init__(self):
        self.elements: List[InteractiveElement] = []
        self.interaction_range = 50
        self.last_interaction_time = 0
        self.interaction_cooldown = 30  # 0.5 seconde
    
    def add_element(self, element: InteractiveElement):
        """Ajoute un élément interactif"""
        self.elements.append(element)
    
    def spawn_elements_for_environment(self, walls: List, environment_type, 
                                     world_width: int, world_height: int):
        """Génère des éléments selon l'environnement"""
        self.elements.clear()
        
        if environment_type.value == "ship":
            self._spawn_ship_elements(walls, world_width, world_height)
        elif environment_type.value == "temple":
            self._spawn_temple_elements(walls, world_width, world_height)
        elif environment_type.value == "forge":
            self._spawn_forge_elements(walls, world_width, world_height)
        elif environment_type.value == "chaos":
            self._spawn_chaos_elements(walls, world_width, world_height)
        elif environment_type.value == "death":
            self._spawn_death_world_elements(walls, world_width, world_height)
    
    def _find_safe_position(self, walls: List, width: int, height: int, 
                           world_width: int, world_height: int) -> tuple:
        """Trouve une position sûre pour placer un élément"""
        for _ in range(50):  # 50 tentatives max
            x = random.randint(100, world_width - width - 100)
            y = random.randint(100, world_height - height - 100)
            
            # Vérifier collision avec murs
            test_rect = pygame.Rect(x, y, width, height)
            collision = False
            
            for wall in walls:
                if test_rect.colliderect(wall.rect):
                    collision = True
                    break
            
            if not collision:
                return x, y
        
        # Position par défaut si rien trouvé
        return world_width // 2, world_height // 2
    
    def _spawn_ship_elements(self, walls: List, world_width: int, world_height: int):
        """Éléments pour vaisseau spatial"""
        # Consoles technologiques
        for _ in range(random.randint(3, 5)):
            x, y = self._find_safe_position(walls, 40, 30, world_width, world_height)
            console_type = random.choice(["info", "hack", "upgrade", "map"])
            self.add_element(TechConsole(x, y, console_type))
        
        # Portes
        for _ in range(random.randint(2, 4)):
            x, y = self._find_safe_position(walls, 30, 80, world_width, world_height)
            is_locked = random.random() < 0.3
            self.add_element(Door(x, y, 30, 80, is_locked))
    
    def _spawn_temple_elements(self, walls: List, world_width: int, world_height: int):
        """Éléments pour temple impérial"""
        # Sanctuaires de guérison
        for _ in range(random.randint(1, 3)):
            x, y = self._find_safe_position(walls, 50, 60, world_width, world_height)
            self.add_element(HealingShrine(x, y))
        
        # Portes sacrées
        for _ in range(random.randint(1, 2)):
            x, y = self._find_safe_position(walls, 40, 90, world_width, world_height)
            self.add_element(Door(x, y, 40, 90))
    
    def _spawn_forge_elements(self, walls: List, world_width: int, world_height: int):
        """Éléments pour forge world"""
        # Machines industrielles
        for _ in range(random.randint(4, 7)):
            x, y = self._find_safe_position(walls, 60, 50, world_width, world_height)
            machine_type = random.choice(["fabricator", "recycler", "purifier"])
            self.add_element(IndustrialMachine(x, y, machine_type))
        
        # Pièges industriels
        for _ in range(random.randint(2, 4)):
            x, y = self._find_safe_position(walls, 40, 40, world_width, world_height)
            trap_type = random.choice(["electric", "gas"])
            self.add_element(Trap(x, y, trap_type))
    
    def _spawn_chaos_elements(self, walls: List, world_width: int, world_height: int):
        """Éléments pour monde corrompu"""
        # Autels de corruption
        for _ in range(random.randint(2, 4)):
            x, y = self._find_safe_position(walls, 55, 45, world_width, world_height)
            self.add_element(CorruptionAltar(x, y))
        
        # Machines corrompues
        for _ in range(random.randint(2, 3)):
            x, y = self._find_safe_position(walls, 60, 50, world_width, world_height)
            self.add_element(IndustrialMachine(x, y, "corrupted"))
        
        # Pièges du Warp
        for _ in range(random.randint(3, 6)):
            x, y = self._find_safe_position(walls, 40, 40, world_width, world_height)
            self.add_element(Trap(x, y, "warp"))
    
    def _spawn_death_world_elements(self, walls: List, world_width: int, world_height: int):
        """Éléments pour monde de la mort"""
        # Beaucoup de pièges
        for _ in range(random.randint(6, 10)):
            x, y = self._find_safe_position(walls, 40, 40, world_width, world_height)
            trap_type = random.choice(["spikes", "gas", "spikes"])  # Plus de spikes
            self.add_element(Trap(x, y, trap_type))
    
    def update(self):
        """Met à jour tous les éléments"""
        for element in self.elements:
            element.update()
        
        if self.last_interaction_time > 0:
            self.last_interaction_time -= 1
    
    def check_interactions(self, player) -> Optional[InteractiveElement]:
        """Vérifie les interactions possibles avec le joueur"""
        closest_element = None
        closest_distance = float('inf')
        
        for element in self.elements:
            if not element.active:
                continue
            
            # Distance au joueur
            distance = math.sqrt((player.x - element.x)**2 + (player.y - element.y)**2)
            
            if distance <= self.interaction_range:
                element.is_highlighted = True
                if distance < closest_distance:
                    closest_distance = distance
                    closest_element = element
            else:
                element.is_highlighted = False
        
        return closest_element
    
    def interact_with_element(self, element: InteractiveElement, player, 
                            morality_system=None, exp_system=None, 
                            item_manager=None) -> Optional[InteractionResult]:
        """Exécute l'interaction avec un élément"""
        if self.last_interaction_time > 0:
            return None
        
        can_interact, reason = element.can_interact(player, morality_system, exp_system)
        if not can_interact:
            return InteractionResult(False, reason)
        
        self.last_interaction_time = self.interaction_cooldown
        return element.interact(player, morality_system, exp_system, item_manager)
    
    def handle_trap_triggers(self, player, morality_system=None) -> List[InteractionResult]:
        """Vérifie et déclenche les pièges"""
        results = []
        
        for element in self.elements:
            if (isinstance(element, Trap) and 
                element.check_trigger(player)):
                result = element.trigger(player, morality_system)
                results.append(result)
        
        return results
    
    def draw(self, screen: pygame.Surface, camera):
        """Dessine tous les éléments visibles"""
        font = pygame.font.Font(None, 20)
        
        for element in self.elements:
            # Convertir en coordonnées écran
            element_screen_x = element.x - camera.x
            element_screen_y = element.y - camera.y
            
            # Vérifier si visible
            if (-100 <= element_screen_x <= camera.screen_width + 100 and
                -100 <= element_screen_y <= camera.screen_height + 100):
                
                # Temporairement déplacer l'élément pour le dessin
                old_x, old_y = element.x, element.y
                element.x, element.y = element_screen_x, element_screen_y
                element.rect.x, element.rect.y = element.x, element.y
                
                # Dessiner l'élément
                element.draw(screen)
                element.draw_interaction_hint(screen, font)
                
                # Restaurer la position
                element.x, element.y = old_x, old_y
                element.rect.x, element.rect.y = element.x, element.y