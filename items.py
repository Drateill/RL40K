import pygame
import random
import math

# Couleurs pour les objets
LIGHT_BLUE = (173, 216, 230)
LIGHT_GREEN = (144, 238, 144)
LIGHT_RED = (255, 182, 193)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
PURPLE = (221, 160, 221)

class Item:
    """Classe de base pour tous les objets"""
    def __init__(self, x, y, item_type, name, description, rarity="common"):
        self.x = x
        self.y = y
        self.width = 16
        self.height = 16
        self.item_type = item_type
        self.name = name
        self.description = description
        self.rarity = rarity
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # Couleur selon la rareté
        self.color = {
            "common": LIGHT_BLUE,
            "rare": LIGHT_GREEN, 
            "epic": PURPLE,
            "legendary": GOLD
        }.get(rarity, LIGHT_BLUE)
        
        # Animation de flottement
        self.float_timer = 0
        self.base_y = y
    
    def update(self):
        """Animation de flottement"""
        self.float_timer += 0.1
        self.y = self.base_y + (math.sin(self.float_timer) * 3)
        self.rect.y = self.y
    
    def draw(self, screen):
        # Dessiner l'objet
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
        # Bordure selon rareté
        border_color = {
            "common": (100, 100, 255),
            "rare": (0, 255, 0),
            "epic": (128, 0, 128),
            "legendary": (255, 165, 0)
        }.get(self.rarity, (100, 100, 255))
        
        pygame.draw.rect(screen, border_color, (self.x, self.y, self.width, self.height), 2)

class ItemManager:
    """Gestionnaire des objets et de leurs effets"""
    def __init__(self):
        self.items_on_ground = []
        self.player_items = []
        
        # Définition des objets disponibles
        self.item_definitions = {
            # Objets communs neutres (50% de chance)
            "speed_boost": {
                "name": "Bottes de Vitesse",
                "description": "+1 Vitesse",
                "rarity": "common",
                "effect": {"speed": 1}
            },
            "damage_up": {
                "name": "Bolter Amélioré", 
                "description": "+5 Dégâts",
                "rarity": "common",
                "effect": {"damage": 5}
            },
            "health_up": {
                "name": "Stimulant Médical",
                "description": "+20 Vie Max",
                "rarity": "common", 
                "effect": {"max_health": 20}
            },
            "fire_rate": {
                "name": "Servo-Crâne",
                "description": "Cadence +25%",
                "rarity": "common",
                "effect": {"fire_rate": 0.75}
            },
            
            # Objets de FOI - Palier 20+ Foi
            "sacred_ammunition": {
                "name": "Munitions Bénites",
                "description": "Projectiles perforants sacrés",
                "rarity": "rare",
                "effect": {"piercing": True, "damage": 4, "holy_damage": True},
                "morality": {"faith": 3},
                "required_faith": 20
            },
            "purification_rites": {
                "name": "Rites de Purification",
                "description": "Purifie la corruption",
                "rarity": "rare",
                "effect": {"purify": True},
                "morality": {"faith": 8, "corruption": -15},
                "required_faith": 20
            },
            
            # Objets de FOI - Palier 40+ Foi
            "holy_bolter": {
                "name": "Bolter Consacré",
                "description": "Dégâts sacrés, +Foi",
                "rarity": "rare",
                "effect": {"damage": 8, "holy_damage": True},
                "morality": {"faith": 5},
                "required_faith": 40
            },
            "blessed_armor": {
                "name": "Armure Bénie",
                "description": "Protection divine",
                "rarity": "rare",
                "effect": {"max_health": 30, "health_regen": 0.05},
                "morality": {"faith": 4},
                "required_faith": 40
            },
            
            # Objets de FOI - Palier 60+ Foi
            "emperor_blessing": {
                "name": "Bénédiction Impériale",
                "description": "Régénération + Foi",
                "rarity": "epic",
                "effect": {"health_regen": 0.1, "damage": 5, "speed": 1},
                "morality": {"faith": 10},
                "required_faith": 60
            },
            "divine_protection": {
                "name": "Protection Divine",
                "description": "L'Empereur veille",
                "rarity": "epic",
                "effect": {"max_health": 50, "invincibility_time": 0.8},
                "morality": {"faith": 8},
                "required_faith": 60
            },
            
            # Objets de FOI - Palier 80+ Foi (Pur)
            "emperor_champion": {
                "name": "Champion de l'Empereur",
                "description": "Puissance divine ultime",
                "rarity": "legendary",
                "effect": {"damage": 15, "multi_shot": 2, "holy_damage": True, "health_regen": 0.2},
                "morality": {"faith": 15},
                "required_faith": 80
            },
            "holy_wrath": {
                "name": "Courroux Sacré",
                "description": "Colère divine",
                "rarity": "legendary",
                "effect": {"damage": 20, "fire_rate": 0.4, "explosive": True, "holy_damage": True},
                "morality": {"faith": 12},
                "required_faith": 80
            },
            "divine_intervention": {
                "name": "Intervention Divine",
                "description": "Miracle permanent",
                "rarity": "legendary",
                "effect": {"max_health": 100, "health_regen": 0.3, "speed": 2},
                "morality": {"faith": 20},
                "required_faith": 80
            },
            
            # Objets de CORRUPTION - Palier 10+ Corruption
            "dark_whispers": {
                "name": "Murmures Sombres",
                "description": "Secrets interdits",
                "rarity": "common",
                "effect": {"damage": 3, "fire_rate": 0.9},
                "morality": {"corruption": 3},
                "required_corruption": 10
            },
            "minor_mutation": {
                "name": "Mutation Mineure",
                "description": "Changement subtil",
                "rarity": "common",
                "effect": {"speed": 1, "max_health": 10},
                "morality": {"corruption": 5},
                "required_corruption": 10
            },
            
            # Objets de CORRUPTION - Palier 30+ Corruption
            "heretical_knowledge": {
                "name": "Savoir Hérétique",
                "description": "Visions interdites",
                "rarity": "rare",
                "effect": {"fire_rate": 0.6, "damage": 6, "homing": True},
                "morality": {"corruption": 8},
                "required_corruption": 30
            },
            "forbidden_weapons": {
                "name": "Arme Interdite",
                "description": "Puissance corrompue",
                "rarity": "rare",
                "effect": {"damage": 10, "explosive": True},
                "morality": {"corruption": 10},
                "required_corruption": 30
            },
            
            # Objets de CORRUPTION - Palier 50+ Corruption
            "dark_pact": {
                "name": "Pacte Sombre",
                "description": "Puissance vs âme",
                "rarity": "epic",
                "effect": {"damage": 15, "speed": 2, "max_health": -15},
                "morality": {"corruption": 15, "faith": -8},
                "required_corruption": 50
            },
            "blood_sacrifice": {
                "name": "Sacrifice Sanglant",
                "description": "Vie contre puissance",
                "rarity": "epic",
                "effect": {"damage": 18, "multi_shot": 2, "max_health": -25},
                "morality": {"corruption": 20},
                "required_corruption": 50
            },
            
            # Objets de CORRUPTION - Palier 70+ Corruption (Chaos)
            "chaos_mutation": {
                "name": "Mutation du Chaos",
                "description": "Transformation chaotique",
                "rarity": "legendary",
                "effect": {"speed": 3, "damage": 12, "bullet_size": 1.8, "max_health": 40},
                "morality": {"corruption": 25},
                "required_corruption": 70
            },
            "warp_energy": {
                "name": "Énergie Warp",
                "description": "Projectiles du Warp",
                "rarity": "legendary",
                "effect": {"homing": True, "damage": 15, "multi_shot": 2, "chaos_power": True},
                "morality": {"corruption": 20},
                "required_corruption": 70
            },
            "daemon_weapon": {
                "name": "Arme Démoniaque",
                "description": "Lame de daemon",
                "rarity": "legendary",
                "effect": {"damage": 25, "fire_rate": 0.3, "explosive": True, "piercing": True},
                "morality": {"corruption": 30},
                "required_corruption": 70
            },
            
            # Objets de CORRUPTION - Palier 90+ Corruption (Champion du Chaos)
            "chaos_ascension": {
                "name": "Ascension Chaotique",
                "description": "Devenir daemonic",
                "rarity": "legendary",
                "effect": {"damage": 30, "speed": 4, "multi_shot": 3, "chaos_power": True, "max_health": 50},
                "morality": {"corruption": 35},
                "required_corruption": 90
            },
            "warp_mastery": {
                "name": "Maîtrise du Warp",
                "description": "Contrôle total",
                "rarity": "legendary",
                "effect": {"homing": True, "explosive": True, "damage": 20, "fire_rate": 0.2},
                "morality": {"corruption": 30},
                "required_corruption": 90
            },
            "daemon_prince": {
                "name": "Prince Daemon",
                "description": "Apothéose du Chaos",
                "rarity": "legendary",
                "effect": {"damage": 35, "speed": 3, "max_health": 100, "health_regen": -0.1, "chaos_power": True},
                "morality": {"corruption": 40},
                "required_corruption": 90
            },
            
            # Objets spéciaux
            "balanced_training": {
                "name": "Entraînement Équilibré",
                "description": "Discipline martiale",
                "rarity": "rare",
                "effect": {"damage": 5, "speed": 1, "fire_rate": 0.8},
                "morality": {"faith": 2},
                "required_faith_range": [40, 60],
                "required_corruption_max": 20
            },
            "tactical_knowledge": {
                "name": "Savoir Tactique",
                "description": "Art de la guerre",
                "rarity": "rare",
                "effect": {"multi_shot": 1, "piercing": True, "damage": 3},
                "morality": {"faith": 3},
                "required_faith_range": [40, 60],
                "required_corruption_max": 20
            },
            "inner_conflict": {
                "name": "Conflit Intérieur",
                "description": "Lutte foi vs corruption",
                "rarity": "epic",
                "effect": {"damage": 10, "speed": 2, "max_health": 20, "unstable": True},
                "morality": {"faith": 5, "corruption": 5},
                "required_faith_min": 30,
                "required_corruption_min": 30
            },
            "dual_nature": {
                "name": "Double Nature",
                "description": "Équilibre précaire",
                "rarity": "epic",
                "effect": {"multi_shot": 2, "homing": True, "explosive": True, "max_health": -10},
                "morality": {"faith": -2, "corruption": -2},
                "required_faith_min": 30,
                "required_corruption_min": 30
            },
            "daemon_weapon": {
                "name": "Arme Démoniaque",
                "description": "Lame de daemon, puissance ultime",
                "rarity": "legendary",
                "effect": {"damage": 20, "fire_rate": 0.3, "explosive": True, "piercing": True},
                "morality": {"corruption": 30}
            },
            
            # Objets rares neutres (5% de chance)
            "double_shot": {
                "name": "Bolter Jumelé",
                "description": "Tire 2 projectiles",
                "rarity": "rare",
                "effect": {"multi_shot": 2}
            },
            "piercing": {
                "name": "Munitions Perforantes",
                "description": "Projectiles traversent ennemis",
                "rarity": "rare",
                "effect": {"piercing": True}
            },
            "big_bullets": {
                "name": "Bolter Lourd",
                "description": "Projectiles +50% plus gros",
                "rarity": "rare",
                "effect": {"bullet_size": 1.5, "damage": 3}
            }
        }
    

    def spawn_item(self, x, y, morality_system=None):
        """Fait apparaître un objet aléatoire selon l'état moral"""
        available_items = list(self.item_definitions.keys())
        
        # Filtrer selon l'état moral si fourni
        if morality_system:
            state = morality_system.current_state
            
            # Objets de foi plus probables si fidèle/pur
            if state in ["faithful", "pure"]:
                faith_items = ["holy_bolter", "emperor_blessing", "purification_rites", "sacred_ammunition"]
                available_items = ["speed_boost", "damage_up", "health_up", "fire_rate"] + faith_items * 3
                
            # Objets de corruption plus probables si hérétique/damné
            elif state in ["heretic", "damned"]:
                corrupt_items = ["dark_pact", "heretical_knowledge", "forbidden_weapons", "blood_sacrifice"]
                available_items = ["speed_boost", "damage_up", "health_up", "fire_rate"] + corrupt_items * 3
                
            # Objets chaos si très corrompu
            elif state in ["corrupted", "chaos_champion"]:
                chaos_items = ["chaos_mutation", "warp_energy", "daemon_weapon"]
                corrupt_items = ["dark_pact", "heretical_knowledge", "forbidden_weapons"]
                available_items = chaos_items * 2 + corrupt_items + ["speed_boost", "damage_up"]
        
        # Sélection aléatoire
        if available_items:
            item_type = random.choice(available_items)
            item_data = self.item_definitions[item_type]
            
            item = Item(x, y, item_type, item_data["name"], 
                       item_data["description"], item_data.get("rarity", "common"))
            self.items_on_ground.append(item)
    
    def update(self):
        """Met à jour tous les objets au sol"""
        for item in self.items_on_ground:
            item.update()
    
    def check_pickup(self, player, morality_system=None):
        """Vérifie si le joueur ramasse un objet"""
        for item in self.items_on_ground[:]:
            if item.rect.colliderect(player.rect):
                self.pickup_item(player, item, morality_system)
                self.items_on_ground.remove(item)
    
    def pickup_item(self, player, item, morality_system=None):
        """Applique les effets d'un objet au joueur"""
        self.player_items.append(item)
        item_data = self.item_definitions[item.item_type]
        effects = item_data["effect"]
        
        # Appliquer les effets sur le joueur
        for effect_type, value in effects.items():
            if effect_type == "speed":
                player.speed += value
            elif effect_type == "damage":
                player.base_damage = getattr(player, 'base_damage', 10) + value
            elif effect_type == "max_health":
                old_max = player.max_health
                player.max_health += value
                if value > 0:  # Si augmentation de vie max, heal aussi
                    player.health += value
                elif value < 0:  # Si réduction, ajuster la vie actuelle si nécessaire
                    player.health = min(player.health, player.max_health)
            elif effect_type == "fire_rate":
                player.shoot_delay = int(player.shoot_delay * value)
                player.shoot_delay = max(1, player.shoot_delay)
            elif effect_type == "multi_shot":
                player.multi_shot = getattr(player, 'multi_shot', 1) + value
            elif effect_type == "piercing":
                player.piercing = True
            elif effect_type == "bullet_size":
                player.bullet_size = getattr(player, 'bullet_size', 1.0) * value
            elif effect_type == "homing":
                player.homing = True
            elif effect_type == "explosive":
                player.explosive = True
            elif effect_type == "holy_damage":
                player.holy_damage = True
            elif effect_type == "health_regen":
                player.health_regen = getattr(player, 'health_regen', 0) + value
            elif effect_type == "purify":
                if morality_system:
                    morality_system.corruption = max(0, morality_system.corruption - 20)
            elif effect_type == "invincibility_time":
                player.invincible_duration = int(60 * value)  # Conversion secondes -> frames
            elif effect_type == "unstable":
                player.unstable = True  # Effet spécial pour objets instables
            elif effect_type == "chaos_power":
                player.chaos_power = True
        
        # Appliquer les effets de moralité
        if morality_system and "morality" in item_data:
            morality_effects = item_data["morality"]
            for effect_type, value in morality_effects.items():
                if effect_type == "faith":
                    morality_system.add_faith(value, f"Objet: {item.name}")
                elif effect_type == "corruption":
                    if value > 0:
                        morality_system.add_corruption(value, f"Objet: {item.name}")
                    else:  # Réduction de corruption
                        morality_system.corruption = max(0, morality_system.corruption + value)
        
        print(f"Ramassé: {item.name} - {item.description}")
    
    def apply_item_directly(self, player, item_type, morality_system=None):
        """Applique directement un objet par son type (pour le level-up)"""
        if item_type not in self.item_definitions:
            print(f"Erreur: objet {item_type} non trouvé")
            return
        
        item_data = self.item_definitions[item_type]
        
        # Créer un objet temporaire pour l'ajouter à l'inventaire
        temp_item = Item(0, 0, item_type, item_data["name"], 
                        item_data["description"], item_data.get("rarity", "common"))
        
        # Appliquer l'objet
        self.pickup_item(player, temp_item, morality_system)
    
    def is_item_available(self, item_type, morality_system):
        """Vérifie si un objet est disponible selon les prérequis moraux"""
        if item_type not in self.item_definitions:
            return False
        
        item_data = self.item_definitions[item_type]
        faith = morality_system.faith
        corruption = morality_system.corruption
        
        # Vérifier foi minimale requise
        if "required_faith" in item_data:
            if faith < item_data["required_faith"]:
                return False
        
        # Vérifier corruption minimale requise
        if "required_corruption" in item_data:
            if corruption < item_data["required_corruption"]:
                return False
        
        # Vérifier plage de foi requise
        if "required_faith_range" in item_data:
            faith_min, faith_max = item_data["required_faith_range"]
            if not (faith_min <= faith <= faith_max):
                return False
        
        # Vérifier corruption maximale autorisée
        if "required_corruption_max" in item_data:
            if corruption > item_data["required_corruption_max"]:
                return False
        
        # Vérifier foi minimale ET corruption minimale
        if "required_faith_min" in item_data and "required_corruption_min" in item_data:
            if faith < item_data["required_faith_min"] or corruption < item_data["required_corruption_min"]:
                return False
            
        # Si toutes les conditions sont remplies, l'objet est disponible       
        return True
    
    def get_synergy_effects(self):
        """Calcule les effets de synergie entre objets"""
        synergies = []
        
        # Synergie: Bolter Jumelé + Munitions Perforantes = "Tempête de Balles"
        has_double = any(item.item_type == "double_shot" for item in self.player_items)
        has_piercing = any(item.item_type == "piercing" for item in self.player_items)
        
        if has_double and has_piercing:
            synergies.append("Tempête de Balles: +1 projectile supplémentaire")
        
        # Synergie: Vitesse + Cadence = "Zèle Fanatique"
        speed_items = sum(1 for item in self.player_items if item.item_type == "speed_boost")
        firerate_items = sum(1 for item in self.player_items if item.item_type == "fire_rate")
        
        if speed_items >= 2 and firerate_items >= 1:
            synergies.append("Zèle Fanatique: Invincibilité réduite à 0.5s")
        
        return synergies
    
    def draw_items(self, screen):
        """Dessine tous les objets au sol"""
        for item in self.items_on_ground:
            item.draw(screen)
    
    def draw_inventory(self, screen):
        """Affiche l'inventaire du joueur"""
        if not self.player_items:
            return
            
        font = pygame.font.Font(None, 24)
        y_offset = 200
        
        # Titre
        title = font.render("Objets:", True, (255, 255, 255))
        screen.blit(title, (10, y_offset))
        y_offset += 25
        
        # Liste des objets
        for i, item in enumerate(self.player_items[-5:]):  # Afficher les 5 derniers
            color = {
                "common": (173, 216, 230),
                "rare": (144, 238, 144),
                "epic": (221, 160, 221), 
                "legendary": (255, 215, 0)
            }.get(item.rarity, (255, 255, 255))
            
            text = font.render(f"• {item.name}", True, color)
            screen.blit(text, (10, y_offset + i * 20))
        
        # Synergies
        synergies = self.get_synergy_effects()
        if synergies:
            y_offset += len(self.player_items[-5:]) * 20 + 10
            synergy_title = font.render("Synergies:", True, (255, 255, 0))
            screen.blit(synergy_title, (10, y_offset))
            
            for i, synergy in enumerate(synergies):
                synergy_text = font.render(f"★ {synergy}", True, (255, 255, 0))
                screen.blit(synergy_text, (10, y_offset + 20 + i * 20))