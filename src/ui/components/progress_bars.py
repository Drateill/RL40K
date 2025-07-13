"""
Barres de progression (XP, moralité, etc.)
"""
import pygame
import math

class ExperienceBar:
    """Barre d'expérience discrète"""
    
    def __init__(self, width=960):  # 80% de 1200px
        self.width = width
        self.height = 12
        self.bg_color = (30, 30, 30)
        self.exp_color = (100, 200, 255)
        self.border_color = (150, 150, 150)
        
        # Animation
        self.fill_animation = 0
        
    def draw_hud(self, surface, x, y, current_exp, exp_to_next, level):
        """Dessine la barre XP dans le HUD"""
        if exp_to_next <= 0:
            return
            
        # Ratio de progression
        exp_ratio = min(1, current_exp / exp_to_next)
        
        # Animation de remplissage avec reset au level up
        if exp_ratio < self.fill_animation * 0.5:  # Détection level up (XP revenue à 0)
            self.fill_animation = 0
        
        if self.fill_animation < exp_ratio:
            self.fill_animation = min(exp_ratio, self.fill_animation + 0.02)
        
        # Fond avec transparence
        bg_rect = pygame.Rect(x, y, self.width, self.height)
        bg_surface = pygame.Surface((self.width, self.height))
        bg_surface.set_alpha(180)
        bg_surface.fill(self.bg_color)
        surface.blit(bg_surface, (x, y))
        
        # Barre d'expérience
        if self.fill_animation > 0:
            exp_width = int(self.width * self.fill_animation)
            exp_rect = pygame.Rect(x, y, exp_width, self.height)
            
            # Gradient effet
            for i in range(exp_width):
                alpha = 100 + int(100 * (i / exp_width))
                color = (*self.exp_color, min(255, alpha))
                line_surface = pygame.Surface((1, self.height))
                line_surface.set_alpha(alpha)
                line_surface.fill(self.exp_color)
                surface.blit(line_surface, (x + i, y))
        
        # Bordure subtile
        pygame.draw.rect(surface, self.border_color, bg_rect, 1)
        
        # Texte du niveau dans la barre (à gauche)
        font = pygame.font.Font(None, 18)
        level_text = font.render(f"Niv. {level}", True, (255, 255, 255))
        level_rect = level_text.get_rect(left=x + 8, centery=y + self.height // 2)
        surface.blit(level_text, level_rect)
        
        # Texte XP au centre de la barre
        exp_font = pygame.font.Font(None, 16)
        exp_text = exp_font.render(f"{current_exp}/{exp_to_next}", True, (255, 255, 255))
        exp_rect = exp_text.get_rect(center=(x + self.width // 2, y + self.height // 2))
        surface.blit(exp_text, exp_rect)

class MoralityBar:
    """Barre de moralité Foi/Corruption"""
    
    def __init__(self, width=960):  # 80% de 1200px
        self.width = width
        self.height = 15
        self.bg_color = (50, 50, 50)
        self.faith_color = (255, 215, 0)      # Or pour la foi
        self.corruption_color = (138, 43, 226)  # Violet pour corruption
        self.neutral_color = (100, 100, 100)
        
    def draw_hud(self, surface, x, y, faith, corruption, max_morality=100):
        """Dessine la barre de moralité"""
        # Calculer les ratios
        total_morality = faith + corruption
        if total_morality <= 0:
            faith_ratio = corruption_ratio = 0
        else:
            faith_ratio = faith / total_morality
            corruption_ratio = corruption / total_morality
        
        # Fond
        bg_rect = pygame.Rect(x, y, self.width, self.height)
        pygame.draw.rect(surface, self.bg_color, bg_rect)
        
        # Zone neutre (centre)
        neutral_start = int(self.width * 0.4)
        neutral_end = int(self.width * 0.6)
        neutral_rect = pygame.Rect(x + neutral_start, y, neutral_end - neutral_start, self.height)
        pygame.draw.rect(surface, self.neutral_color, neutral_rect)
        
        # Barre de foi (côté gauche)
        if faith > 0:
            faith_width = int((self.width * 0.4) * min(1, faith / (max_morality * 0.5)))
            faith_rect = pygame.Rect(x + neutral_start - faith_width, y, faith_width, self.height)
            pygame.draw.rect(surface, self.faith_color, faith_rect)
        
        # Barre de corruption (côté droit)
        if corruption > 0:
            corruption_width = int((self.width * 0.4) * min(1, corruption / (max_morality * 0.5)))
            corruption_rect = pygame.Rect(x + neutral_end, y, corruption_width, self.height)
            pygame.draw.rect(surface, self.corruption_color, corruption_rect)
        
        # Bordure
        pygame.draw.rect(surface, (255, 255, 255), bg_rect, 1)
        
        # Marqueur central
        center_x = x + self.width // 2
        pygame.draw.line(surface, (255, 255, 255), 
                        (center_x, y), (center_x, y + self.height), 2)
        
        # Textes dans la barre
        font = pygame.font.Font(None, 16)
        
        # "Foi" à gauche dans la barre
        if faith > 0:
            faith_text = font.render("Foi", True, (255, 255, 255))
            faith_text_rect = faith_text.get_rect(center=(x + self.width * 0.2, y + self.height // 2))
            surface.blit(faith_text, faith_text_rect)
        
        # "Corruption" à droite dans la barre
        if corruption > 0:
            corruption_text = font.render("Corruption", True, (255, 255, 255))
            corruption_text_rect = corruption_text.get_rect(center=(x + self.width * 0.8, y + self.height // 2))
            surface.blit(corruption_text, corruption_text_rect)
        
        # Valeurs numériques discrètes en bas
        value_font = pygame.font.Font(None, 14)
        if faith > 0:
            faith_value = value_font.render(f"{int(faith)}", True, self.faith_color)
            surface.blit(faith_value, (x + 5, y + self.height + 2))
        
        if corruption > 0:
            corruption_value = value_font.render(f"{int(corruption)}", True, self.corruption_color)
            corruption_rect = corruption_value.get_rect(right=x + self.width - 5, top=y + self.height + 2)
            surface.blit(corruption_value, corruption_rect)

class ButtonComponent:
    """Composant bouton réutilisable"""
    
    def __init__(self, text, width=200, height=50):
        self.text = text
        self.width = width
        self.height = height
        
        # Rectangle par défaut (sera mis à jour lors du draw)
        self.rect = pygame.Rect(0, 0, width, height)
        
        # États
        self.is_hovered = False
        self.is_pressed = False
        
        # Couleurs
        self.normal_color = (70, 70, 70)
        self.hover_color = (100, 100, 100)
        self.pressed_color = (50, 50, 50)
        self.text_color = (255, 255, 255)
        self.border_color = (150, 150, 150)
        
    def update(self, mouse_pos, mouse_clicked):
        """Met à jour l'état du bouton"""
        # Vérifier si la souris est sur le bouton
        was_hovered = self.is_hovered
        # Note: needs rect to be set by draw method
        
        return self.is_pressed and mouse_clicked
        
    def draw(self, surface, x, y, font=None):
        """Dessine le bouton"""
        # Mettre à jour la position du rectangle
        self.rect.x = x
        self.rect.y = y
        print(f"🎨 ButtonComponent '{self.text}' dessiné à ({x}, {y}) - rect: {self.rect}")
        
        # Couleur selon l'état
        if self.is_pressed:
            color = self.pressed_color
        elif self.is_hovered:
            color = self.hover_color
        else:
            color = self.normal_color
        
        # Fond du bouton
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, 2)
        
        # Effet d'enfoncement
        if self.is_pressed:
            shadow_rect = pygame.Rect(x + 2, y + 2, self.width - 2, self.height - 2)
            pygame.draw.rect(surface, (30, 30, 30), shadow_rect)
        
        # Texte
        if not font:
            font = pygame.font.Font(None, 36)
        
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
        return self.rect
    
    def handle_event(self, event):
        """Gère les événements du bouton"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                print(f"🖱️ ButtonComponent '{self.text}' - MOUSEBUTTONDOWN détecté à {event.pos}")
                print(f"   Rect du bouton: {self.rect}")
                self.is_pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                was_pressed = self.is_pressed
                self.is_pressed = False
                if was_pressed and self.rect.collidepoint(event.pos):
                    print(f"✅ ButtonComponent '{self.text}' - CLIC CONFIRMÉ à {event.pos}")
                    return True  # Bouton cliqué
        
        return False