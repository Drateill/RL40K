import pygame
import random
import math

class ExperienceSystem:
    """Système d'expérience et de level-up avec choix de cartes"""
    
    def __init__(self):
        self.experience = 0
        self.level = 1
        self.exp_to_next_level = 100
        self.exp_curve_multiplier = 1.5
        
        # État du level-up
        self.is_leveling_up = False
        self.level_up_choices = []
        self.selected_choice = 0
        
        # Animation des cartes
        self.card_animations = [0, 0, 0]  # Pour chaque carte
        self.card_hover_time = [0, 0, 0]
        
    def add_experience(self, amount):
        """Ajoute de l'expérience et gère le level-up"""
        self.experience += amount
        
        if self.experience >= self.exp_to_next_level:
            self.level_up()
    
    def level_up(self):
        """Déclenche un level-up"""
        self.level += 1
        self.experience = 0
        self.exp_to_next_level = int(100 * (self.exp_curve_multiplier ** (self.level - 1)))
        self.is_leveling_up = True
        # Réinitialiser les choix pour forcer une nouvelle génération
        self.level_up_choices = []
        print(f"LEVEL UP ! Niveau {self.level}")
        print("Level-up activé, choix réinitialisés")
    
    def generate_level_up_choices(self, morality_system, item_manager):
        """Génère 3 choix d'objets pour le level-up"""
        available_items = self.get_available_items_for_morality(morality_system, item_manager)
        
        print(f"Objets disponibles pour foi={morality_system.faith:.0f}, corruption={morality_system.corruption:.0f}: {available_items}")
        
        # Assurer qu'on a au moins 3 choix
        if len(available_items) < 3:
            # Ajouter des objets de base si pas assez
            base_items = ["speed_boost", "damage_up", "health_up", "fire_rate"]
            available_items.extend([item for item in base_items if item not in available_items])
        
        # Sélectionner 3 objets aléatoires
        self.level_up_choices = random.sample(available_items, min(3, len(available_items)))
        self.selected_choice = 0
        
        print(f"Choix générés: {self.level_up_choices}")
        
        # Réinitialiser animations
        self.card_animations = [0, 0, 0]
        self.card_hover_time = [0, 0, 0]
    
    def get_available_items_for_morality(self, morality_system, item_manager):
        """Retourne les objets disponibles selon l'état de foi/corruption"""
        available_items = []
        
        print(f"Vérification des objets pour foi={morality_system.faith}, corruption={morality_system.corruption}")
        
        # Vérifier chaque objet avec ses prérequis
        for item_type in item_manager.item_definitions.keys():
            if item_manager.is_item_available(item_type, morality_system):
                available_items.append(item_type)
                print(f"  - {item_type}: DISPONIBLE")
            else:
                print(f"  - {item_type}: NON DISPONIBLE")
        
        print(f"Total objets disponibles: {len(available_items)}")
        
        # S'assurer qu'on a au moins quelques objets
        if len(available_items) < 5:
            print("Pas assez d'objets, ajout des objets de base...")
            # Ajouter des objets de base qui n'ont pas de prérequis
            base_items = ["speed_boost", "damage_up", "health_up", "fire_rate", "double_shot"]
            for item in base_items:
                if item not in available_items:
                    available_items.append(item)
                    print(f"  + Ajouté: {item}")
        
        print(f"Liste finale: {available_items}")
        return available_items
    
    def handle_input(self, event):
        """Gère les inputs pendant le level-up"""
        if not self.is_leveling_up:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.selected_choice = (self.selected_choice - 1) % 3
                return True
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.selected_choice = (self.selected_choice + 1) % 3
                return True
            elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                return self.confirm_choice()
        
        # Support souris
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic gauche
                mouse_x, mouse_y = event.pos
                card_clicked = self.get_card_at_position(mouse_x, mouse_y)
                if card_clicked >= 0:
                    self.selected_choice = card_clicked
                    return self.confirm_choice()
        
        if event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            card_hovered = self.get_card_at_position(mouse_x, mouse_y)
            if card_hovered >= 0:
                self.selected_choice = card_hovered
        
        return True  # Consommer l'input pendant le level-up
    
    def get_card_at_position(self, x, y):
        """Retourne l'index de la carte à la position donnée"""
        screen_width = 1024
        screen_height = 768
        
        card_width = 200
        card_height = 300
        card_spacing = 50
        
        start_x = (screen_width - (card_width * 3 + card_spacing * 2)) // 2
        start_y = (screen_height - card_height) // 2
        
        for i in range(3):
            card_x = start_x + i * (card_width + card_spacing)
            card_rect = pygame.Rect(card_x, start_y, card_width, card_height)
            
            if card_rect.collidepoint(x, y):
                return i
        
        return -1
    
    def confirm_choice(self):
        """Confirme le choix et termine le level-up"""
        if 0 <= self.selected_choice < len(self.level_up_choices):
            self.is_leveling_up = False
            return True  # Choix confirmé
        return False
    
    def update(self):
        """Met à jour les animations des cartes"""
        if self.is_leveling_up:
            for i in range(3):
                if i == self.selected_choice:
                    self.card_hover_time[i] += 1
                    self.card_animations[i] = min(10, self.card_animations[i] + 1)
                else:
                    self.card_hover_time[i] = max(0, self.card_hover_time[i] - 1)
                    self.card_animations[i] = max(0, self.card_animations[i] - 1)
    
    def draw_level_up_screen(self, screen, morality_system, item_manager):
        """Dessine l'écran de level-up avec les 3 cartes"""
        if not self.is_leveling_up or not self.level_up_choices:
            print("Pas de level-up ou pas de choix à afficher")
            return
        
        print(f"Affichage écran level-up avec choix: {self.level_up_choices}")
        
        # Fond semi-transparent
        overlay = pygame.Surface((1024, 768))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Titre
        font_title = pygame.font.Font(None, 48)
        title_text = font_title.render("LEVEL UP!", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(512, 100))
        screen.blit(title_text, title_rect)
        
        level_text = font_title.render(f"Niveau {self.level}", True, (255, 215, 0))
        level_rect = level_text.get_rect(center=(512, 150))
        screen.blit(level_text, level_rect)
        
        # Instructions
        font_small = pygame.font.Font(None, 24)
        instruction_text = font_small.render("Utilisez A/D ou la souris pour choisir, ESPACE pour confirmer", True, (200, 200, 200))
        instruction_rect = instruction_text.get_rect(center=(512, 680))
        screen.blit(instruction_text, instruction_rect)
        
        # Dessiner les 3 cartes
        self.draw_cards(screen, morality_system, item_manager)
    
    def draw_cards(self, screen, morality_system, item_manager):
        """Dessine les 3 cartes de choix"""
        card_width = 200
        card_height = 300
        card_spacing = 50
        
        start_x = (1024 - (card_width * 3 + card_spacing * 2)) // 2
        start_y = (768 - card_height) // 2
        
        for i, item_type in enumerate(self.level_up_choices):
            # Position de la carte
            card_x = start_x + i * (card_width + card_spacing)
            card_y = start_y
            
            # Animation de hover
            hover_offset = self.card_animations[i]
            card_y -= hover_offset
            
            # Données de l'objet
            item_data = item_manager.item_definitions.get(item_type, {
                "name": "Objet Inconnu",
                "description": "???",
                "rarity": "common"
            })
            
            # Couleur de la carte selon rareté
            rarity_colors = {
                "common": (100, 100, 255),
                "rare": (0, 255, 0),
                "epic": (128, 0, 128),
                "legendary": (255, 165, 0)
            }
            
            card_color = rarity_colors.get(item_data.get("rarity", "common"), (100, 100, 255))
            
            # Bordure plus épaisse si sélectionné
            border_width = 4 if i == self.selected_choice else 2
            
            # Fond de la carte
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            pygame.draw.rect(screen, (40, 40, 40), card_rect)
            pygame.draw.rect(screen, card_color, card_rect, border_width)
            
            # Nom de l'objet
            font_name = pygame.font.Font(None, 28)
            name_lines = self.wrap_text(item_data["name"], font_name, card_width - 20)
            
            y_offset = card_y + 20
            for line in name_lines:
                name_surface = font_name.render(line, True, (255, 255, 255))
                name_rect = name_surface.get_rect(centerx=card_x + card_width // 2)
                name_rect.y = y_offset
                screen.blit(name_surface, name_rect)
                y_offset += 30
            
            # Description
            font_desc = pygame.font.Font(None, 20)
            desc_lines = self.wrap_text(item_data["description"], font_desc, card_width - 20)
            
            y_offset += 10
            for line in desc_lines:
                desc_surface = font_desc.render(line, True, (200, 200, 200))
                desc_rect = desc_surface.get_rect(centerx=card_x + card_width // 2)
                desc_rect.y = y_offset
                screen.blit(desc_surface, desc_rect)
                y_offset += 22
            
            # Effets sur la moralité
            if "morality" in item_data:
                morality_effects = item_data["morality"]
                y_offset += 10
                
                for effect_type, value in morality_effects.items():
                    if effect_type == "faith" and value != 0:
                        color = (255, 215, 0) if value > 0 else (255, 100, 100)
                        symbol = "+" if value > 0 else ""
                        faith_text = font_desc.render(f"{symbol}{value} Foi", True, color)
                        faith_rect = faith_text.get_rect(centerx=card_x + card_width // 2)
                        faith_rect.y = y_offset
                        screen.blit(faith_text, faith_rect)
                        y_offset += 20
                    
                    elif effect_type == "corruption" and value != 0:
                        color = (150, 0, 150) if value > 0 else (100, 255, 100)
                        symbol = "+" if value > 0 else ""
                        corr_text = font_desc.render(f"{symbol}{value} Corruption", True, color)
                        corr_rect = corr_text.get_rect(centerx=card_x + card_width // 2)
                        corr_rect.y = y_offset
                        screen.blit(corr_text, corr_rect)
                        y_offset += 20
            
            # Rareté
            rarity_text = font_desc.render(item_data.get("rarity", "common").title(), True, card_color)
            rarity_rect = rarity_text.get_rect(centerx=card_x + card_width // 2)
            rarity_rect.y = card_y + card_height - 30
            screen.blit(rarity_text, rarity_rect)
    
    def wrap_text(self, text, font, max_width):
        """Découpe le texte en lignes pour qu'il tienne dans la largeur"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def draw_exp_bar(self, screen, x, y):
        """Dessine la barre d'expérience"""
        bar_width = 200
        bar_height = 20
        
        # Barre de fond
        pygame.draw.rect(screen, (50, 50, 50), (x, y, bar_width, bar_height))
        
        # Barre d'expérience
        exp_ratio = self.experience / self.exp_to_next_level
        exp_width = int(bar_width * exp_ratio)
        pygame.draw.rect(screen, (0, 255, 0), (x, y, exp_width, bar_height))
        
        # Bordure
        pygame.draw.rect(screen, (255, 255, 255), (x, y, bar_width, bar_height), 2)
        
        # Texte
        font = pygame.font.Font(None, 24)
        exp_text = font.render(f"Niveau {self.level} - {self.experience}/{self.exp_to_next_level} XP", True, (255, 255, 255))
        screen.blit(exp_text, (x + bar_width + 10, y - 2))