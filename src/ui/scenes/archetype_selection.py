"""
Menu de sélection d'archétype de personnage
"""
import pygame
from typing import Optional
from ...gameplay.archetype_manager import ArchetypeManager

class ArchetypeSelectionScene:
    """Scène de sélection d'archétype"""
    
    def __init__(self, screen_width=1200, screen_height=800):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.archetype_manager = ArchetypeManager()
        
        # État de la sélection
        self.selected_archetype = "pyromancer"  # Archétype sélectionné par défaut
        self.confirmed = False
        
        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.subtitle_font = pygame.font.Font(None, 32)
        self.description_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
        # Couleurs
        self.bg_color = (20, 20, 30)
        self.text_color = (255, 255, 255)
        self.selected_color = (255, 215, 0)  # Or
        self.card_bg_color = (40, 40, 50)
        self.card_selected_color = (60, 60, 80)
        
        # Positions des cartes d'archétype
        self.setup_archetype_cards()
        
        # Bouton de confirmation
        self.confirm_button_rect = pygame.Rect(
            screen_width // 2 - 100, screen_height - 100, 200, 50
        )
        
    def setup_archetype_cards(self):
        """Configure les positions des cartes d'archétype"""
        archetypes = self.archetype_manager.get_all_archetypes()
        archetype_ids = list(archetypes.keys())
        
        # Calculer les positions pour 3 cartes côte à côte
        card_width = 300
        card_height = 400
        spacing = 50
        total_width = len(archetype_ids) * card_width + (len(archetype_ids) - 1) * spacing
        start_x = (self.screen_width - total_width) // 2
        start_y = 150
        
        self.archetype_cards = {}
        for i, archetype_id in enumerate(archetype_ids):
            x = start_x + i * (card_width + spacing)
            self.archetype_cards[archetype_id] = {
                "rect": pygame.Rect(x, start_y, card_width, card_height),
                "data": archetypes[archetype_id]
            }
    
    def handle_event(self, event):
        """Gère les événements de la scène"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "main_menu"  # Retour au menu principal
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.confirmed = True
                return "start_game"
            elif event.key == pygame.K_LEFT:
                self._select_previous_archetype()
            elif event.key == pygame.K_RIGHT:
                self._select_next_archetype()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic gauche
                mouse_pos = pygame.mouse.get_pos()
                
                # Vérifier les clics sur les cartes d'archétype
                for archetype_id, card_data in self.archetype_cards.items():
                    if card_data["rect"].collidepoint(mouse_pos):
                        self.selected_archetype = archetype_id
                        break
                
                # Vérifier le clic sur le bouton de confirmation
                if self.confirm_button_rect.collidepoint(mouse_pos):
                    self.confirmed = True
                    return "start_game"
        
        return None
    
    def _select_previous_archetype(self):
        """Sélectionne l'archétype précédent"""
        archetype_ids = list(self.archetype_cards.keys())
        current_index = archetype_ids.index(self.selected_archetype)
        new_index = (current_index - 1) % len(archetype_ids)
        self.selected_archetype = archetype_ids[new_index]
    
    def _select_next_archetype(self):
        """Sélectionne l'archétype suivant"""
        archetype_ids = list(self.archetype_cards.keys())
        current_index = archetype_ids.index(self.selected_archetype)
        new_index = (current_index + 1) % len(archetype_ids)
        self.selected_archetype = archetype_ids[new_index]
    
    def update(self, dt):
        """Met à jour la scène"""
        pass
    
    def draw(self, screen):
        """Dessine la scène"""
        # Fond
        screen.fill(self.bg_color)
        
        # Titre
        title = self.title_font.render("Choisissez votre Archétype", True, self.text_color)
        title_rect = title.get_rect(center=(self.screen_width // 2, 50))
        screen.blit(title, title_rect)
        
        # Sous-titre
        subtitle = self.subtitle_font.render("Chaque archétype possède une arme unique et des capacités spécialisées", True, self.text_color)
        subtitle_rect = subtitle.get_rect(center=(self.screen_width // 2, 90))
        screen.blit(subtitle, subtitle_rect)
        
        # Dessiner les cartes d'archétype
        for archetype_id, card_data in self.archetype_cards.items():
            self._draw_archetype_card(screen, archetype_id, card_data)
        
        # Bouton de confirmation
        self._draw_confirm_button(screen)
        
        # Instructions
        instructions = self.small_font.render("Utilisez les flèches ou cliquez pour sélectionner. ENTRÉE ou clic pour confirmer.", True, self.text_color)
        instructions_rect = instructions.get_rect(center=(self.screen_width // 2, self.screen_height - 30))
        screen.blit(instructions, instructions_rect)
    
    def _draw_archetype_card(self, screen, archetype_id, card_data):
        """Dessine une carte d'archétype"""
        rect = card_data["rect"]
        archetype = card_data["data"]
        is_selected = (archetype_id == self.selected_archetype)
        
        # Couleur de fond de la carte
        bg_color = self.card_selected_color if is_selected else self.card_bg_color
        border_color = self.selected_color if is_selected else self.text_color
        border_width = 3 if is_selected else 1
        
        # Fond de la carte
        pygame.draw.rect(screen, bg_color, rect)
        pygame.draw.rect(screen, border_color, rect, border_width)
        
        # Icône colorée de l'archétype (simple cercle coloré)
        icon_radius = 40
        icon_center = (rect.centerx, rect.y + 60)
        pygame.draw.circle(screen, archetype["icon_color"], icon_center, icon_radius)
        pygame.draw.circle(screen, border_color, icon_center, icon_radius, 2)
        
        # Nom de l'archétype
        name_color = self.selected_color if is_selected else self.text_color
        name = self.subtitle_font.render(archetype["name"], True, name_color)
        name_rect = name.get_rect(center=(rect.centerx, rect.y + 120))
        screen.blit(name, name_rect)
        
        # Description courte
        description = self.description_font.render(archetype["description"], True, self.text_color)
        description_rect = description.get_rect(center=(rect.centerx, rect.y + 150))
        screen.blit(description, description_rect)
        
        # Statistiques
        y_offset = 180
        stats = archetype["stats_modifiers"]
        
        if "max_health" in stats:
            health_text = self.small_font.render(f"Vie: {stats['max_health']}", True, self.text_color)
            health_rect = health_text.get_rect(center=(rect.centerx, rect.y + y_offset))
            screen.blit(health_text, health_rect)
            y_offset += 25
        
        if "speed" in stats:
            speed_text = self.small_font.render(f"Vitesse: {stats['speed']}", True, self.text_color)
            speed_rect = speed_text.get_rect(center=(rect.centerx, rect.y + y_offset))
            screen.blit(speed_text, speed_rect)
            y_offset += 25
        
        # Arme spécialisée
        weapon_info = self._get_weapon_info(archetype["weapon_id"])
        if weapon_info:
            weapon_text = self.small_font.render(f"Arme: {weapon_info}", True, archetype["icon_color"])
            weapon_rect = weapon_text.get_rect(center=(rect.centerx, rect.y + y_offset))
            screen.blit(weapon_text, weapon_rect)
            y_offset += 25
        
        # Histoire de fond (texte wrap)
        story_lines = self._wrap_text(archetype["background_story"], self.small_font, rect.width - 20)
        for i, line in enumerate(story_lines):
            if y_offset + 20 < rect.bottom - 10:  # Vérifier qu'on ne dépasse pas
                story_text = self.small_font.render(line, True, (180, 180, 180))
                story_rect = story_text.get_rect(center=(rect.centerx, rect.y + y_offset + 20))
                screen.blit(story_text, story_rect)
                y_offset += 18
    
    def _get_weapon_info(self, weapon_id):
        """Récupère le nom de l'arme depuis l'ID"""
        weapon_names = {
            "flamer_archetype": "Lance-Flammes Militaire",
            "laser_pistol_archetype": "Pistolet Laser",
            "chainsword_archetype": "Épée Tronçonneuse"
        }
        return weapon_names.get(weapon_id, weapon_id)
    
    def _wrap_text(self, text, font, max_width):
        """Découpe le texte en lignes pour qu'il tienne dans la largeur"""
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines[:3]  # Limiter à 3 lignes maximum
    
    def _draw_confirm_button(self, screen):
        """Dessine le bouton de confirmation"""
        # Couleur selon si la souris survole
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.confirm_button_rect.collidepoint(mouse_pos)
        
        button_color = self.selected_color if is_hovered else self.card_bg_color
        text_color = (0, 0, 0) if is_hovered else self.text_color
        
        # Fond du bouton
        pygame.draw.rect(screen, button_color, self.confirm_button_rect)
        pygame.draw.rect(screen, self.text_color, self.confirm_button_rect, 2)
        
        # Texte du bouton
        button_text = self.description_font.render("COMMENCER", True, text_color)
        button_text_rect = button_text.get_rect(center=self.confirm_button_rect.center)
        screen.blit(button_text, button_text_rect)
    
    def get_selected_archetype(self):
        """Retourne l'archétype sélectionné"""
        return self.selected_archetype