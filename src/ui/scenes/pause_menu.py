"""
Menu de pause avec affichage des améliorations acquises
"""
import pygame
from ..components.progress_bars import ButtonComponent

class PauseMenuScene:
    """Menu de pause avec historique des améliorations"""
    
    def __init__(self, screen_width=1200, screen_height=800):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Boutons
        button_width = 250
        button_height = 60
        button_spacing = 80
        
        center_x = screen_width // 2 - button_width // 2
        start_y = screen_height // 2 + 50
        
        self.resume_button = ButtonComponent("REPRENDRE", button_width, button_height)
        self.settings_button = ButtonComponent("PARAMÈTRES", button_width, button_height)
        self.menu_button = ButtonComponent("MENU PRINCIPAL", button_width, button_height)
        self.quit_button = ButtonComponent("QUITTER", button_width, button_height)
        
        # Positions
        self.resume_pos = (center_x, start_y)
        self.settings_pos = (center_x, start_y + button_spacing)
        self.menu_pos = (center_x, start_y + button_spacing * 2)
        self.quit_pos = (center_x, start_y + button_spacing * 3)
        
        # État
        self.selected_action = None
        
        # Améliorations acquises
        self.acquired_items = []
        
    def set_acquired_items(self, items):
        """Définit la liste des améliorations acquises"""
        self.acquired_items = items if items else []
    
    def handle_event(self, event):
        """Gère les événements du menu pause"""
        # Gérer les boutons
        if self.resume_button.handle_event(event):
            self.selected_action = "resume"
            return True
            
        if self.settings_button.handle_event(event):
            self.selected_action = "settings"
            return True
            
        if self.menu_button.handle_event(event):
            self.selected_action = "main_menu"
            return True
            
        if self.quit_button.handle_event(event):
            self.selected_action = "quit"
            return True
            
        # Échap pour reprendre
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.selected_action = "resume"
            return True
            
        return False
    
    def draw(self, surface):
        """Dessine le menu de pause"""
        # Fond semi-transparent
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # Titre
        self.draw_title(surface)
        
        # Section améliorations
        self.draw_upgrades_section(surface)
        
        # Boutons
        self.draw_buttons(surface)
        
        # Instructions
        self.draw_instructions(surface)
    
    def draw_title(self, surface):
        """Dessine le titre du menu pause"""
        title_font = pygame.font.Font(None, 72)
        title = title_font.render("PAUSE", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width // 2, 100))
        surface.blit(title, title_rect)
    
    def draw_upgrades_section(self, surface):
        """Dessine la section des améliorations acquises"""
        section_x = 50
        section_y = 150
        section_width = self.screen_width - 100
        section_height = 250
        
        # Fond de la section
        section_rect = pygame.Rect(section_x, section_y, section_width, section_height)
        pygame.draw.rect(surface, (40, 40, 40), section_rect)
        pygame.draw.rect(surface, (100, 100, 100), section_rect, 2)
        
        # Titre de la section
        section_font = pygame.font.Font(None, 36)
        section_title = section_font.render("AMÉLIORATIONS ACQUISES", True, (255, 215, 0))
        surface.blit(section_title, (section_x + 20, section_y + 10))
        
        # Liste des améliorations
        if not self.acquired_items:
            # Aucune amélioration
            no_items_font = pygame.font.Font(None, 24)
            no_items_text = no_items_font.render("Aucune amélioration acquise", True, (150, 150, 150))
            text_rect = no_items_text.get_rect(center=(section_rect.centerx, section_rect.centery))
            surface.blit(no_items_text, text_rect)
        else:
            # Afficher les améliorations
            self.draw_upgrade_list(surface, section_x + 20, section_y + 50, 
                                 section_width - 40, section_height - 70)
    
    def draw_upgrade_list(self, surface, x, y, width, height):
        """Dessine la liste des améliorations"""
        item_font = pygame.font.Font(None, 24)
        description_font = pygame.font.Font(None, 20)
        
        items_per_row = 2
        item_width = (width - 20) // items_per_row
        item_height = 80
        
        for i, item_type in enumerate(self.acquired_items[:8]):  # Max 8 items affichés
            row = i // items_per_row
            col = i % items_per_row
            
            item_x = x + col * (item_width + 10)
            item_y = y + row * (item_height + 10)
            
            # Simuler les données d'item (normalement viendraient d'ItemManager)
            item_data = self.get_item_display_data(item_type)
            
            # Fond de l'item
            item_rect = pygame.Rect(item_x, item_y, item_width, item_height)
            
            # Couleur selon la rareté
            rarity_colors = {
                "common": (70, 70, 120),
                "rare": (70, 120, 70),
                "epic": (120, 70, 120),
                "legendary": (120, 100, 50)
            }
            
            rarity = item_data.get("rarity", "common")
            bg_color = rarity_colors.get(rarity, (70, 70, 70))
            
            pygame.draw.rect(surface, bg_color, item_rect)
            pygame.draw.rect(surface, (150, 150, 150), item_rect, 1)
            
            # Nom de l'item
            name = item_data.get("name", item_type.replace("_", " ").title())
            name_surface = item_font.render(name, True, (255, 255, 255))
            name_rect = name_surface.get_rect(centerx=item_rect.centerx, top=item_y + 5)
            surface.blit(name_surface, name_rect)
            
            # Description courte
            desc = item_data.get("short_desc", "Amélioration")
            desc_surface = description_font.render(desc, True, (200, 200, 200))
            desc_rect = desc_surface.get_rect(centerx=item_rect.centerx, top=item_y + 30)
            surface.blit(desc_surface, desc_rect)
            
            # Effet (si disponible)
            if "effect" in item_data:
                effect_surface = description_font.render(item_data["effect"], True, (100, 255, 100))
                effect_rect = effect_surface.get_rect(centerx=item_rect.centerx, top=item_y + 50)
                surface.blit(effect_surface, effect_rect)
        
        # Indicateur s'il y a plus d'items
        if len(self.acquired_items) > 8:
            more_font = pygame.font.Font(None, 20)
            more_text = more_font.render(f"... et {len(self.acquired_items) - 8} autres", 
                                       True, (150, 150, 150))
            surface.blit(more_text, (x, y + 180))
    
    def get_item_display_data(self, item_type):
        """Retourne les données d'affichage pour un type d'item"""
        # Base de données simplifiée des items
        item_database = {
            "speed_boost": {
                "name": "Vitesse Améliorée",
                "short_desc": "Mouvement plus rapide",
                "effect": "+2 Vitesse",
                "rarity": "common"
            },
            "damage_up": {
                "name": "Puissance de Feu",
                "short_desc": "Dégâts augmentés",
                "effect": "+5 Dégâts",
                "rarity": "common"
            },
            "health_up": {
                "name": "Vitalité Renforcée",
                "short_desc": "Santé maximale",
                "effect": "+20 PV Max",
                "rarity": "common"
            },
            "fire_rate": {
                "name": "Cadence Rapide",
                "short_desc": "Tir plus fréquent",
                "effect": "+25% Cadence",
                "rarity": "rare"
            },
            "double_shot": {
                "name": "Tir Double",
                "short_desc": "Projectiles multiples",
                "effect": "2 Projectiles",
                "rarity": "rare"
            },
            "holy_weapon": {
                "name": "Arme Bénie",
                "short_desc": "Puissance sacrée",
                "effect": "Dégâts saints",
                "rarity": "epic"
            },
            "chaos_weapon": {
                "name": "Arme du Chaos",
                "short_desc": "Corruption destructrice",
                "effect": "Dégâts chaotiques",
                "rarity": "epic"
            }
        }
        
        return item_database.get(item_type, {
            "name": item_type.replace("_", " ").title(),
            "short_desc": "Amélioration mystérieuse",
            "effect": "Effet inconnu",
            "rarity": "common"
        })
    
    def draw_buttons(self, surface):
        """Dessine les boutons du menu"""
        button_font = pygame.font.Font(None, 36)
        
        self.resume_button.draw(surface, *self.resume_pos, button_font)
        self.settings_button.draw(surface, *self.settings_pos, button_font)
        self.menu_button.draw(surface, *self.menu_pos, button_font)
        self.quit_button.draw(surface, *self.quit_pos, button_font)
    
    def draw_instructions(self, surface):
        """Dessine les instructions"""
        instruction_font = pygame.font.Font(None, 24)
        instruction_text = instruction_font.render("ESC: Reprendre | Clic: Navigation", 
                                                 True, (150, 150, 150))
        instruction_rect = instruction_text.get_rect(center=(self.screen_width // 2, 
                                                           self.screen_height - 30))
        surface.blit(instruction_text, instruction_rect)
    
    def get_selected_action(self):
        """Retourne l'action sélectionnée"""
        action = self.selected_action
        self.selected_action = None
        return action