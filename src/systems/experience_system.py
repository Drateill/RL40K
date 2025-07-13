import pygame
import random
import math

# Import du debug logger
try:
    from debug_logger import debug_log, debug_section
except ImportError:
    # Fallback si debug_logger n'est pas disponible
    def debug_log(msg): print(msg)
    def debug_section(title): print(f"=== {title} ===")

class ExperienceSystem:
    """Système d'expérience et de level-up avec choix de cartes"""
    
    def __init__(self):
        self.experience = 0
        self.level = 1
        self.exp_to_next_level = 100
        self.exp_curve_multiplier = 1.8  # Progression plus lente pour équilibrer
        
        # État du level-up
        self.is_leveling_up = False
        self.level_up_choices = []
        self.selected_choice = -1  # 🔧 AUCUNE SÉLECTION PAR DÉFAUT
        
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
    
    def generate_level_up_choices(self, morality_system, item_manager, player=None):
        """Génère 3 choix d'objets pour le level-up"""
        available_items = self.get_available_items_for_morality(morality_system, item_manager, player)
        
        print(f"Objets disponibles pour foi={morality_system.faith:.0f}, corruption={morality_system.corruption:.0f}: {available_items}")
        
        # Assurer qu'on a au moins 3 choix
        if len(available_items) < 3:
            # Ajouter des objets de base si pas assez
            base_items = ["speed_boost", "damage_up", "health_up", "fire_rate"]
            available_items.extend([item for item in base_items if item not in available_items])
        
        # Sélectionner 3 objets aléatoires
        self.level_up_choices = random.sample(available_items, min(3, len(available_items)))
        self.selected_choice = -1  # 🔧 AUCUNE SÉLECTION INITIALE
        
        print(f"Choix générés: {self.level_up_choices}")
        
        # Réinitialiser animations
        self.card_animations = [0, 0, 0]
        self.card_hover_time = [0, 0, 0]
    
    def get_available_items_for_morality(self, morality_system, item_manager, player=None):
        """Retourne les objets disponibles selon l'état de foi/corruption"""
        available_items = []
        
        print(f"Vérification des objets pour foi={morality_system.faith}, corruption={morality_system.corruption}")
        
        # Vérifier chaque objet avec ses prérequis
        for item_type in item_manager.item_definitions.keys():
            if item_manager.is_item_available(item_type, morality_system):
                # Filtrer les armes déjà possédées
                if self._is_weapon_upgrade(item_type) and player:
                    weapon_id = self._extract_weapon_id(item_type)
                    if hasattr(player, 'obtained_weapon_ids') and weapon_id in player.obtained_weapon_ids:
                        print(f"  - {item_type}: DÉJÀ POSSÉDÉE ({weapon_id})")
                        continue
                
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
    
    def _is_weapon_upgrade(self, item_type: str) -> bool:
        """Vérifie si un item est une amélioration d'arme"""
        return item_type.startswith("weapon_upgrade_")
    
    def _extract_weapon_id(self, item_type: str) -> str:
        """Extrait l'ID d'arme d'un item weapon_upgrade"""
        if item_type.startswith("weapon_upgrade_"):
            return item_type.replace("weapon_upgrade_", "")
        return item_type
    
    def handle_input(self, event):
        """Gère les inputs pendant le level-up - SOURIS UNIQUEMENT"""
        if not self.is_leveling_up:
            return False
        
        # 🔧 SOURIS UNIQUEMENT - pas de clavier
        
        # Clic pour confirmer le choix
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic gauche
                mouse_x, mouse_y = event.pos
                card_clicked = self.get_card_at_position(mouse_x, mouse_y)
                debug_section("EXPERIENCE SYSTEM - CLIC")
                debug_log(f"🎯 Position clic: ({mouse_x}, {mouse_y})")
                debug_log(f"🎯 Carte détectée: {card_clicked}")
                if card_clicked >= 0:
                    debug_log(f"🎯 CLIC DÉTECTÉ sur carte {card_clicked}")
                    self.selected_choice = card_clicked
                    debug_log(f"🎯 selected_choice mis à jour: {self.selected_choice}")
                    debug_log(f"🎯 level_up_choices: {self.level_up_choices}")
                    confirmed = self.confirm_choice()
                    debug_log(f"🎯 confirm_choice retourné: {confirmed}")
                    return confirmed
                else:
                    debug_log(f"❌ Aucune carte sous le clic")
        
        # Survol pour sélectionner (pas de log pour éviter le spam)
        if event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            card_hovered = self.get_card_at_position(mouse_x, mouse_y)
            
            if card_hovered >= 0:
                if card_hovered != self.selected_choice:
                    self.selected_choice = card_hovered
            else:
                # Si la souris n'est sur aucune carte, désélectionner
                if self.selected_choice != -1:
                    self.selected_choice = -1
        
        return True  # Consommer l'input pendant le level-up
    
    def get_card_at_position(self, x, y):
        """Retourne l'index de la carte à la position donnée"""
        # Utiliser les vraies dimensions d'écran du jeu
        screen_width = 1200  # SCREEN_WIDTH from constants
        screen_height = 800  # SCREEN_HEIGHT from constants
        
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
        """Confirme le choix - GameScene terminera le level-up"""
        debug_section("CONFIRM CHOICE")
        debug_log(f"🔧 selected_choice: {self.selected_choice}")
        debug_log(f"🔧 len(level_up_choices): {len(self.level_up_choices) if self.level_up_choices else 0}")
        if 0 <= self.selected_choice < len(self.level_up_choices):
            choice_name = self.level_up_choices[self.selected_choice]
            debug_log(f"✅ Choix confirmé: {choice_name}")
            return True  # Signal pour GameScene d'appliquer le choix
        else:
            debug_log(f"❌ Choix invalide")
            return False
    
    def finish_level_up(self):
        """Termine le level-up (appelé par GameScene après application)"""
        debug_section("FINISH LEVEL-UP")
        debug_log(f"🏁 finish_level_up appelé")
        debug_log(f"   Avant: is_leveling_up = {self.is_leveling_up}")
        self.is_leveling_up = False
        self.level_up_choices = []
        self.selected_choice = -1
        debug_log(f"   Après: is_leveling_up = {self.is_leveling_up}")
        debug_log(f"🎮 RETOUR AU JEU - level-up terminé")
    
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
        
        # Fond semi-transparent - utiliser vraies dimensions
        screen_width, screen_height = 1200, 800
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Titre - centré sur vrai écran
        font_title = pygame.font.Font(None, 48)
        title_text = font_title.render("LEVEL UP!", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(screen_width//2, 100))
        screen.blit(title_text, title_rect)
        
        level_text = font_title.render(f"Niveau {self.level}", True, (255, 215, 0))
        level_rect = level_text.get_rect(center=(screen_width//2, 150))
        screen.blit(level_text, level_rect)
        
        # Instructions améliorées
        font_small = pygame.font.Font(None, 24)
        font_tiny = pygame.font.Font(None, 20)
        
        # Instructions - NOUVEAU SYSTÈME
        # Instruction principale
        instruction_text = font_small.render("Survolez une amélioration avec la souris", True, (200, 200, 200))
        instruction_rect = instruction_text.get_rect(center=(screen_width//2, 660))
        screen.blit(instruction_text, instruction_rect)
        
        # Instruction confirmation
        confirm_text = font_small.render("Cliquez pour confirmer votre choix", True, (255, 255, 100))
        confirm_rect = confirm_text.get_rect(center=(screen_width//2, 685))
        screen.blit(confirm_text, confirm_rect)
        
        # Indication du statut
        if 0 <= self.selected_choice < len(self.level_up_choices):
            current_item = self.level_up_choices[self.selected_choice]
            item_data = item_manager.item_definitions.get(current_item, {})
            selected_text = font_tiny.render(f"Survolé: {item_data.get('name', current_item)}", True, (100, 255, 100))
            selected_rect = selected_text.get_rect(center=(screen_width//2, 710))
            screen.blit(selected_text, selected_rect)
        else:
            no_selection_text = font_tiny.render("Aucune amélioration survolée", True, (150, 150, 150))
            no_selection_rect = no_selection_text.get_rect(center=(screen_width//2, 710))
            screen.blit(no_selection_text, no_selection_rect)
        
        # Dessiner les 3 cartes
        self.draw_cards(screen, morality_system, item_manager)
    
    def draw_cards(self, screen, morality_system, item_manager):
        """Dessine les 3 cartes de choix"""
        card_width = 200
        card_height = 300
        card_spacing = 50
        
        # Utiliser vraies dimensions pour centrer les cartes
        screen_width, screen_height = 1200, 800
        start_x = (screen_width - (card_width * 3 + card_spacing * 2)) // 2
        start_y = (screen_height - card_height) // 2
        
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
            
            # 🔧 SYSTÈME DE SURBRILLANCE AU SURVOL
            is_hovered = (i == self.selected_choice and self.selected_choice >= 0)
            
            # Fond de la carte selon l'état
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            
            if is_hovered:
                # Carte survolée : SURBRILLANCE
                # Effet glow prononcé
                for glow_size in range(12, 0, -3):
                    glow_surface = pygame.Surface((card_width + glow_size * 2, card_height + glow_size * 2))
                    glow_surface.set_alpha(60 - glow_size * 4)
                    glow_surface.fill(card_color)
                    screen.blit(glow_surface, (card_x - glow_size, card_y - glow_size))
                
                # Fond lumineux
                pygame.draw.rect(screen, (80, 80, 80), card_rect)
                # Bordure épaisse et lumineuse
                pygame.draw.rect(screen, card_color, card_rect, 5)
                
                # Curseur pointeur visuel
                cursor_points = [
                    (card_x + card_width // 2, card_y - 20),
                    (card_x + card_width // 2 - 12, card_y - 8),
                    (card_x + card_width // 2 + 12, card_y - 8)
                ]
                pygame.draw.polygon(screen, card_color, cursor_points)
                
            else:
                # Cartes non survolées : SOMBRES
                # Fond très sombre
                pygame.draw.rect(screen, (25, 25, 25), card_rect)
                # Bordure fine et terne
                pygame.draw.rect(screen, (card_color[0]//3, card_color[1]//3, card_color[2]//3), card_rect, 2)
            
            # Couleurs de texte selon l'état de surbrillance
            if is_hovered:
                title_color = (255, 255, 255)  # Blanc pur pour carte survolée
                desc_color = (220, 220, 220)   # Gris clair
            else:
                title_color = (150, 150, 150)  # Gris pour cartes sombres
                desc_color = (100, 100, 100)   # Gris très sombre
            
            # Nom de l'objet
            font_name = pygame.font.Font(None, 28)
            name_lines = self.wrap_text(item_data["name"], font_name, card_width - 20)
            
            y_offset = card_y + 20
            for line in name_lines:
                name_surface = font_name.render(line, True, title_color)
                name_rect = name_surface.get_rect(centerx=card_x + card_width // 2)
                name_rect.y = y_offset
                screen.blit(name_surface, name_rect)
                y_offset += 30
            
            # Description
            font_desc = pygame.font.Font(None, 20)
            desc_lines = self.wrap_text(item_data["description"], font_desc, card_width - 20)
            
            y_offset += 10
            for line in desc_lines:
                desc_surface = font_desc.render(line, True, desc_color)
                desc_rect = desc_surface.get_rect(centerx=card_x + card_width // 2)
                desc_rect.y = y_offset
                screen.blit(desc_surface, desc_rect)
                y_offset += 22
            
            # Effets sur la moralité - ajustés selon surbrillance
            if "morality" in item_data:
                morality_effects = item_data["morality"]
                y_offset += 10
                
                for effect_type, value in morality_effects.items():
                    if effect_type == "faith" and value != 0:
                        if is_hovered:
                            color = (255, 215, 0) if value > 0 else (255, 100, 100)
                        else:
                            color = (180, 150, 0) if value > 0 else (180, 70, 70)
                        symbol = "+" if value > 0 else ""
                        faith_text = font_desc.render(f"{symbol}{value} Foi", True, color)
                        faith_rect = faith_text.get_rect(centerx=card_x + card_width // 2)
                        faith_rect.y = y_offset
                        screen.blit(faith_text, faith_rect)
                        y_offset += 20
                    
                    elif effect_type == "corruption" and value != 0:
                        if is_hovered:
                            color = (150, 0, 150) if value > 0 else (100, 255, 100)
                        else:
                            color = (100, 0, 100) if value > 0 else (70, 180, 70)
                        symbol = "+" if value > 0 else ""
                        corr_text = font_desc.render(f"{symbol}{value} Corruption", True, color)
                        corr_rect = corr_text.get_rect(centerx=card_x + card_width // 2)
                        corr_rect.y = y_offset
                        screen.blit(corr_text, corr_rect)
                        y_offset += 20
            
            # Rareté - ajustée selon surbrillance
            if is_hovered:
                rarity_color = card_color
            else:
                rarity_color = (card_color[0]//2, card_color[1]//2, card_color[2]//2)
            
            rarity_text = font_desc.render(item_data.get("rarity", "common").title(), True, rarity_color)
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