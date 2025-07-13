"""
Menu des param\u00e8tres avec contr\u00f4les audio
"""
import pygame
from ..components.progress_bars import ButtonComponent

class SettingsMenuScene:
    """Menu des param\u00e8tres du jeu"""
    
    def __init__(self, screen_width=1200, screen_height=800):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Boutons
        button_width = 250
        button_height = 50
        button_spacing = 60
        
        center_x = screen_width // 2 - button_width // 2
        start_y = 200
        
        # Boutons de contr\u00f4le du volume
        self.volume_down_button = ButtonComponent("-", 50, button_height)
        self.volume_up_button = ButtonComponent("+", 50, button_height)
        self.mute_button = ButtonComponent("MUET", 120, button_height)
        
        # Bouton retour
        self.back_button = ButtonComponent("RETOUR", button_width, button_height)
        
        # Positions ajustées pour éviter chevauchement avec la barre de volume
        self.volume_down_pos = (center_x - 200, start_y + 200)  # Plus à gauche et plus bas
        self.volume_up_pos = (center_x + 150, start_y + 200)    # Plus à droite et plus bas
        self.mute_pos = (center_x - 60, start_y + 280)          # Plus bas
        self.back_pos = (center_x, start_y + 360)               # Plus bas
        
        # \u00c9tat
        self.selected_action = None
        self.current_volume = 0.7  # Volume par d\u00e9faut (70%)
        self.is_muted = False
        self.volume_before_mute = 0.7
        
    def set_sound_system(self, sound_system):
        """D\u00e9finit le syst\u00e8me audio \u00e0 contr\u00f4ler"""
        self.sound_system = sound_system
        if sound_system:
            self.current_volume = sound_system.master_volume
            self.is_muted = (sound_system.master_volume == 0)
    
    def handle_event(self, event):
        """Gère les événements du menu paramètres"""
        # Contr\u00f4le du volume
        if self.volume_down_button.handle_event(event):
            self.change_volume(-0.1)
            return True
            
        if self.volume_up_button.handle_event(event):
            self.change_volume(0.1)
            return True
            
        if self.mute_button.handle_event(event):
            self.toggle_mute()
            return True
            
        if self.back_button.handle_event(event):
            self.selected_action = "back"
            return True
            
        # \u00c9chap pour retour
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.selected_action = "back"
            return True
            
        return False
    
    def change_volume(self, delta):
        """Change le volume par incrément"""
        if self.is_muted:
            self.toggle_mute()  # D\u00e9sactiver le mute d'abord
        
        self.current_volume = max(0.0, min(1.0, self.current_volume + delta))
        
        # Appliquer au syst\u00e8me audio
        if hasattr(self, 'sound_system') and self.sound_system:
            self.sound_system.set_master_volume(self.current_volume)
            print(f"\ud83d\udd0a Volume: {int(self.current_volume * 100)}%")
    
    def toggle_mute(self):
        """Active/désactive le mode muet"""
        if hasattr(self, 'sound_system') and self.sound_system:
            if self.is_muted:
                # D\u00e9sactiver mute
                self.current_volume = self.volume_before_mute
                self.sound_system.set_master_volume(self.current_volume)
                self.is_muted = False
                print(f"Son reactive: {int(self.current_volume * 100)}%")
            else:
                # Activer mute
                self.volume_before_mute = self.current_volume
                self.current_volume = 0.0
                self.sound_system.set_master_volume(0.0)
                self.is_muted = True
                print("Son coupe")
    
    def draw(self, surface):
        """Dessine le menu des paramètres"""
        # Fond semi-transparent
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((20, 20, 20))
        surface.blit(overlay, (0, 0))
        
        # Titre
        self.draw_title(surface)
        
        # Section audio
        self.draw_audio_section(surface)
        
        # Boutons
        self.draw_buttons(surface)
    
    def draw_title(self, surface):
        """Dessine le titre du menu"""
        title_font = pygame.font.Font(None, 64)
        title = title_font.render("PARAM\u00c8TRES", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width // 2, 80))
        surface.blit(title, title_rect)
    
    def draw_audio_section(self, surface):
        """Dessine la section des contrôles audio"""
        section_font = pygame.font.Font(None, 36)
        
        # Titre section
        audio_title = section_font.render("AUDIO", True, (255, 215, 0))
        title_rect = audio_title.get_rect(center=(self.screen_width // 2, 160))
        surface.blit(audio_title, title_rect)
        
        # Affichage du volume actuel
        volume_font = pygame.font.Font(None, 32)
        if self.is_muted:
            volume_text = "MUET"
            volume_color = (255, 100, 100)
        else:
            volume_text = f"Volume: {int(self.current_volume * 100)}%"
            volume_color = (255, 255, 255)
        
        volume_surface = volume_font.render(volume_text, True, volume_color)
        volume_rect = volume_surface.get_rect(center=(self.screen_width // 2, 250))
        surface.blit(volume_surface, volume_rect)
        
        # Barre de volume visuelle
        self.draw_volume_bar(surface)
        
        # Labels pour les boutons
        label_font = pygame.font.Font(None, 24)
        
        # Label contrôles
        controls_label = label_font.render("Contrôles", True, (200, 200, 200))
        controls_rect = controls_label.get_rect(center=(self.screen_width // 2, 370))
        surface.blit(controls_label, controls_rect)
    
    def draw_volume_bar(self, surface):
        """Dessine une barre de volume visuelle"""
        bar_width = 300
        bar_height = 20
        bar_x = (self.screen_width - bar_width) // 2
        bar_y = 300  # Remonter un peu la barre
        
        # Fond de la barre
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(surface, (60, 60, 60), bg_rect)
        
        # Barre de volume
        if not self.is_muted:
            volume_width = int(bar_width * self.current_volume)
            volume_rect = pygame.Rect(bar_x, bar_y, volume_width, bar_height)
            
            # Couleur selon le niveau
            if self.current_volume > 0.7:
                color = (100, 255, 100)  # Vert
            elif self.current_volume > 0.3:
                color = (255, 255, 100)  # Jaune
            else:
                color = (255, 100, 100)  # Rouge
            
            pygame.draw.rect(surface, color, volume_rect)
        
        # Bordure
        pygame.draw.rect(surface, (255, 255, 255), bg_rect, 2)
    
    def draw_buttons(self, surface):
        """Dessine les boutons du menu"""
        button_font = pygame.font.Font(None, 32)
        
        # Boutons de volume
        self.volume_down_button.draw(surface, *self.volume_down_pos, button_font)
        self.volume_up_button.draw(surface, *self.volume_up_pos, button_font)
        
        # Bouton mute avec couleur sp\u00e9ciale
        mute_color = (255, 100, 100) if self.is_muted else (200, 200, 200)
        mute_surface = button_font.render("MUET", True, mute_color)
        mute_rect = self.mute_button.draw(surface, *self.mute_pos, button_font)
        # Redessiner le texte avec la bonne couleur
        mute_text_rect = mute_surface.get_rect(center=mute_rect.center)
        surface.blit(mute_surface, mute_text_rect)
        
        # Bouton retour
        self.back_button.draw(surface, *self.back_pos, button_font)
        
        # Instructions
        instruction_font = pygame.font.Font(None, 20)
        instructions = [
            "Utilisez + et - pour ajuster le volume",
            "MUET pour couper/réactiver le son",
            "ESC ou RETOUR pour revenir"
        ]
        
        start_y = self.screen_height - 80
        for i, instruction in enumerate(instructions):
            inst_surface = instruction_font.render(instruction, True, (150, 150, 150))
            inst_rect = inst_surface.get_rect(center=(self.screen_width // 2, start_y + i * 20))
            surface.blit(inst_surface, inst_rect)
    
    def update(self, dt):
        """Met à jour le menu"""
        pass
    
    def get_next_scene(self):
        """Retourne la transition de scène"""
        if self.selected_action == "back":
            self.selected_action = None
            return "back"
        return None
    
    def get_selected_action(self):
        """Retourne l'action sélectionnée"""
        action = self.selected_action
        self.selected_action = None
        return action