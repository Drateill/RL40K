import pygame
import random
import math

class MoralitySystem:
    """Système de Foi/Corruption inspiré de Warhammer 40K"""
    
    def __init__(self):
        self.faith = 50      # 0-100, démarre neutre
        self.corruption = 0  # 0-100, démarre pur
        
        # Seuils importants
        self.PURE_THRESHOLD = 80      # Foi > 80 = Pur
        self.FAITHFUL_THRESHOLD = 60  # Foi > 60 = Fidèle
        self.NEUTRAL_LOW = 40         # Foi 40-60 = Neutre
        self.NEUTRAL_HIGH = 60
        self.HERETIC_THRESHOLD = 20   # Foi < 20 = Hérétique
        self.DAMNED_THRESHOLD = 10    # Foi < 10 = Damné
        
        self.CORRUPT_THRESHOLD = 30   # Corruption > 30 = Visible
        self.CHAOS_THRESHOLD = 70     # Corruption > 70 = Chaos
        
        # Événements de moralité
        self.morality_events = []
        self.event_timer = 0
        
        # Multiplicateurs selon l'état moral
        self.current_state = "neutral"
        self.update_state()
    
    def get_current_state(self):
        """Détermine l'état moral actuel du joueur"""
        if self.corruption >= self.CHAOS_THRESHOLD:
            return "chaos_champion"
        elif self.corruption >= self.CORRUPT_THRESHOLD:
            return "corrupted"
        elif self.faith >= self.PURE_THRESHOLD:
            return "pure"
        elif self.faith >= self.FAITHFUL_THRESHOLD:
            return "faithful"
        elif self.faith <= self.HERETIC_THRESHOLD:
            return "heretic"
        elif self.faith <= self.DAMNED_THRESHOLD:
            return "damned"
        else:
            return "neutral"
    
    def update_state(self):
        """Met à jour l'état et applique les effets"""
        old_state = self.current_state
        self.current_state = self.get_current_state()
        
        if old_state != self.current_state:
            self.trigger_state_change_event(old_state, self.current_state)
    
    def trigger_state_change_event(self, old_state, new_state):
        """Déclenche un événement de changement d'état"""
        events = {
            "pure": "L'Empereur vous bénit ! Vous rayonnez de pureté.",
            "faithful": "Votre foi en l'Empereur grandit.",
            "neutral": "Vous trouvez un équilibre... temporaire.",
            "heretic": "Des murmures hérétiques envahissent votre esprit...",
            "damned": "L'Empereur vous abandonne... Les ténèbres vous appellent.",
            "corrupted": "Le Chaos vous marque de ses stigmates.",
            "chaos_champion": "VOUS APPARTENEZ AU CHAOS ! Les Dieux Sombres vous récompensent !"
        }
        
        self.add_morality_event(events.get(new_state, "Votre âme change..."))
    
    def add_faith(self, amount, reason=""):
        """Ajoute de la foi et réduit la corruption"""
        old_faith = self.faith
        self.faith = min(100, self.faith + amount)
        
        # La foi combat la corruption
        corruption_reduction = amount * 0.3
        self.corruption = max(0, self.corruption - corruption_reduction)
        
        if amount > 0 and reason:
            self.add_morality_event(f"+{amount} Foi: {reason}")
        
        self.update_state()
        
        return self.faith - old_faith
    
    def add_corruption(self, amount, reason=""):
        """Ajoute de la corruption et réduit la foi"""
        old_corruption = self.corruption
        self.corruption = min(100, self.corruption + amount)
        
        # La corruption érode la foi
        faith_reduction = amount * 0.5
        self.faith = max(0, self.faith - faith_reduction)
        
        if amount > 0 and reason:
            self.add_morality_event(f"+{amount} Corruption: {reason}", is_corruption=True)
        
        self.update_state()
        
        return self.corruption - old_corruption
    
    def add_morality_event(self, text, is_corruption=False):
        """Ajoute un événement à afficher"""
        color = (255, 100, 100) if is_corruption else (255, 255, 150)
        self.morality_events.append({
            "text": text,
            "timer": 180,  # 3 secondes à 60 FPS
            "color": color
        })
    
    def update(self):
        """Met à jour le système (à appeler chaque frame)"""
        # Décompte des événements
        self.morality_events = [
            event for event in self.morality_events 
            if event["timer"] > 0
        ]
        
        for event in self.morality_events:
            event["timer"] -= 1
        
        # Dérive naturelle vers le neutre (très lente)
        self.event_timer += 1
        if self.event_timer > 3600:  # Chaque minute
            if self.faith > 50:
                self.faith -= 0.1
            elif self.faith < 50:
                self.faith += 0.1
            
            if self.corruption > 0:
                self.corruption -= 0.05  # La corruption s'efface plus lentement
            
            self.event_timer = 0
            self.update_state()
    
    def get_stat_modifiers(self):
        """Retourne les modificateurs de stats selon l'état moral"""
        modifiers = {
            "damage_multiplier": 1.0,
            "speed_multiplier": 1.0,
            "fire_rate_multiplier": 1.0,
            "health_regen": 0,
            "special_effects": []
        }
        
        state = self.current_state
        
        if state == "pure":
            modifiers["damage_multiplier"] = 1.3
            modifiers["health_regen"] = 0.1
            modifiers["special_effects"].append("holy_bullets")
        elif state == "faithful":
            modifiers["damage_multiplier"] = 1.15
            modifiers["health_regen"] = 0.05
        elif state == "heretic":
            modifiers["speed_multiplier"] = 1.2
            modifiers["fire_rate_multiplier"] = 1.1
        elif state == "damned":
            modifiers["speed_multiplier"] = 1.4
            modifiers["fire_rate_multiplier"] = 1.3
            modifiers["special_effects"].append("cursed_bullets")
        elif state == "corrupted":
            modifiers["damage_multiplier"] = 1.2
            modifiers["speed_multiplier"] = 1.1
            modifiers["special_effects"].append("chaos_aura")
        elif state == "chaos_champion":
            modifiers["damage_multiplier"] = 1.5
            modifiers["speed_multiplier"] = 1.3
            modifiers["fire_rate_multiplier"] = 1.2
            modifiers["special_effects"].append("chaos_powers")
        
        return modifiers
    
    def get_available_items(self):
        """Retourne les types d'objets disponibles selon l'état moral"""
        state = self.current_state
        
        base_items = ["speed_boost", "health_up", "damage_up", "fire_rate"]
        
        if state in ["pure", "faithful"]:
            return base_items + ["holy_bolter", "emperor_blessing", "purification_rites", "sacred_ammunition"]
        elif state in ["heretic", "damned"]:
            return base_items + ["dark_pact", "heretical_knowledge", "forbidden_weapons", "blood_sacrifice"]
        elif state in ["corrupted", "chaos_champion"]:
            return base_items + ["chaos_mutation", "warp_energy", "daemon_weapon", "chaos_blessing"]
        else:
            return base_items
    
    def process_kill(self, enemy_type):
        """Traite un kill d'ennemi pour la moralité"""
        if enemy_type == "BasicEnemy":
            # Ennemi standard - effet neutre ou léger selon contexte
            if self.current_state in ["pure", "faithful"]:
                self.add_faith(1, "Purge des hérétiques")
            elif random.random() < 0.1:  # 10% de chance
                self.add_corruption(0.5, "Violence excessive")
        
        elif enemy_type == "ShooterEnemy":
            # Ennemi dangereux - plus de récompense
            if self.current_state in ["pure", "faithful"]:
                self.add_faith(2, "Élimination d'un traître armé")
            else:
                if random.random() < 0.3:
                    self.add_corruption(1, "Goût du sang")
        
        elif enemy_type == "FastEnemy":
            # Ennemi agile - test de patience
            if random.random() < 0.2:
                if self.current_state in ["heretic", "damned"]:
                    self.add_corruption(1, "Frustration et colère")
                else:
                    self.add_faith(1, "Patience récompensée")
    
    def process_damage_taken(self, damage):
        """Traite les dégâts reçus"""
        # Dégâts peuvent tester la foi ou alimenter la corruption
        if damage >= 20:  # Gros dégâts
            if random.random() < 0.3:
                if self.current_state in ["faithful", "pure"]:
                    self.add_faith(1, "L'Empereur me protège")
                else:
                    self.add_corruption(1, "Douleur et désespoir")
    
    def draw_morality_bar(self, screen, x, y):
        """Dessine la barre de foi/corruption"""
        bar_width = 200
        bar_height = 12
        
        # Barre de foi
        faith_width = int((self.faith / 100) * bar_width)
        pygame.draw.rect(screen, (100, 100, 100), (x, y, bar_width, bar_height))
        pygame.draw.rect(screen, (255, 215, 0), (x, y, faith_width, bar_height))
        
        # Barre de corruption (en dessous)
        corruption_width = int((self.corruption / 100) * bar_width)
        pygame.draw.rect(screen, (100, 50, 50), (x, y + bar_height + 2, bar_width, bar_height))
        pygame.draw.rect(screen, (150, 0, 150), (x, y + bar_height + 2, corruption_width, bar_height))
        
        # Texte
        font = pygame.font.Font(None, 24)
        faith_text = font.render(f"Foi: {int(self.faith)}", True, (255, 255, 255))
        corruption_text = font.render(f"Corruption: {int(self.corruption)}", True, (255, 255, 255))
        state_text = font.render(f"État: {self.get_state_name()}", True, self.get_state_color())
        
        screen.blit(faith_text, (x + bar_width + 10, y - 2))
        screen.blit(corruption_text, (x + bar_width + 10, y + bar_height))
        screen.blit(state_text, (x, y + bar_height * 2 + 8))
    
    def get_state_name(self):
        """Retourne le nom affiché de l'état"""
        names = {
            "pure": "Pur",
            "faithful": "Fidèle", 
            "neutral": "Neutre",
            "heretic": "Hérétique",
            "damned": "Damné",
            "corrupted": "Corrompu",
            "chaos_champion": "Champion du Chaos"
        }
        return names.get(self.current_state, "Inconnu")
    
    def get_state_color(self):
        """Retourne la couleur de l'état"""
        colors = {
            "pure": (255, 255, 255),
            "faithful": (200, 200, 255),
            "neutral": (150, 150, 150),
            "heretic": (255, 200, 100),
            "damned": (255, 100, 100),
            "corrupted": (200, 100, 200),
            "chaos_champion": (255, 0, 255)
        }
        return colors.get(self.current_state, (255, 255, 255))
    
    def draw_events(self, screen, x, y):
        """Dessine les événements récents"""
        font = pygame.font.Font(None, 20)
        for i, event in enumerate(self.morality_events[-5:]):  # 5 derniers événements
            alpha = min(255, event["timer"] * 2)  # Fade out
            color = (*event["color"], alpha) if len(event["color"]) == 3 else event["color"]
            
            text = font.render(event["text"], True, event["color"])
            screen.blit(text, (x, y + i * 22))