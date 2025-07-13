"""
Menu principal du jeu
"""
import pygame
import math
from ..components.progress_bars import ButtonComponent

class MainMenuScene:
    """Scène du menu principal"""
    
    def __init__(self, screen_width=1200, screen_height=800):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Boutons
        button_width = 300
        button_height = 80
        button_spacing = 100
        
        start_y = screen_height // 2 - 100
        center_x = screen_width // 2 - button_width // 2
        
        self.play_button = ButtonComponent("JOUER", button_width, button_height)
        self.settings_button = ButtonComponent("PARAMÈTRES", button_width, button_height)
        self.quit_button = ButtonComponent("QUITTER", button_width, button_height)
        
        # Positions des boutons
        self.play_pos = (center_x, start_y)
        self.settings_pos = (center_x, start_y + button_spacing)
        self.quit_pos = (center_x, start_y + button_spacing * 2)
        
        # État
        self.selected_action = None
        
        # Effets visuels
        self.title_glow = 0
        self.particles = []
        
    def handle_event(self, event):
        """Gère les événements du menu"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            print(f"🖱️ MainMenuScene: MOUSEBUTTONDOWN reçu à {event.pos}")
        
        # Gérer les boutons
        if self.play_button.handle_event(event):
            self.selected_action = "play"
            print("🎮 Bouton JOUER cliqué ! Action définie sur 'play'")
            return True
            
        if self.settings_button.handle_event(event):
            self.selected_action = "settings"
            return True
            
        if self.quit_button.handle_event(event):
            self.selected_action = "quit"
            return True
            
        # Échap pour quitter
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.selected_action = "quit"
            return True
            
        return False
    
    def update(self, dt):
        """Met à jour le menu"""
        # Animation du titre
        self.title_glow = (self.title_glow + dt * 2) % (2 * 3.14159)
        
        # Mettre à jour les particules d'arrière-plan
        self.update_particles(dt)
    
    def update_particles(self, dt):
        """Met à jour les particules d'arrière-plan"""
        # Ajouter de nouvelles particules
        if len(self.particles) < 50:
            import random
            self.particles.append({
                'x': random.randint(0, self.screen_width),
                'y': self.screen_height + 10,
                'speed': random.uniform(20, 60),
                'size': random.randint(1, 3),
                'alpha': random.randint(50, 150)
            })
        
        # Mettre à jour les particules existantes
        for particle in self.particles[:]:
            particle['y'] -= particle['speed'] * dt
            particle['alpha'] -= dt * 30
            
            if particle['y'] < -10 or particle['alpha'] <= 0:
                self.particles.remove(particle)
    
    def draw(self, surface):
        """Dessine le menu principal"""
        # Fond dégradé
        self.draw_background(surface)
        
        # Particules
        self.draw_particles(surface)
        
        # Titre du jeu
        self.draw_title(surface)
        
        # Sous-titre
        self.draw_subtitle(surface)
        
        # Boutons
        self.draw_buttons(surface)
        
        # Version/crédits
        self.draw_footer(surface)
    
    def draw_background(self, surface):
        """Dessine le fond dégradé"""
        # Dégradé vertical sombre
        for y in range(self.screen_height):
            ratio = y / self.screen_height
            # Du bleu sombre au noir
            color = (
                int(20 * (1 - ratio)),
                int(30 * (1 - ratio)),
                int(60 * (1 - ratio))
            )
            pygame.draw.line(surface, color, (0, y), (self.screen_width, y))
    
    def draw_particles(self, surface):
        """Dessine les particules d'arrière-plan"""
        for particle in self.particles:
            if particle['alpha'] > 0:
                # Créer une surface avec alpha
                particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2))
                particle_surface.set_alpha(particle['alpha'])
                particle_surface.fill((100, 150, 255))
                
                surface.blit(particle_surface, 
                           (particle['x'] - particle['size'], 
                            particle['y'] - particle['size']))
    
    def draw_title(self, surface):
        """Dessine le titre principal"""
        # Police pour le titre
        title_font = pygame.font.Font(None, 120)
        
        # Effet de lueur
        glow_intensity = abs(math.cos(self.title_glow)) * 50 + 150
        
        # Titre principal
        title = "WARHAMMER 40K"
        title_surface = title_font.render(title, True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 150))
        
        # Effet glow
        for offset in range(5, 0, -1):
            glow_surface = title_font.render(title, True, 
                                           (int(glow_intensity), int(glow_intensity), 255))
            for dx in [-offset, 0, offset]:
                for dy in [-offset, 0, offset]:
                    if dx != 0 or dy != 0:
                        glow_rect = title_rect.copy()
                        glow_rect.center = (title_rect.centerx + dx, title_rect.centery + dy)
                        surface.blit(glow_surface, glow_rect)
        
        # Titre principal
        surface.blit(title_surface, title_rect)
    
    def draw_subtitle(self, surface):
        """Dessine le sous-titre"""
        subtitle_font = pygame.font.Font(None, 48)
        subtitle = "ROGUELIKE"
        subtitle_surface = subtitle_font.render(subtitle, True, (200, 200, 200))
        subtitle_rect = subtitle_surface.get_rect(center=(self.screen_width // 2, 220))
        surface.blit(subtitle_surface, subtitle_rect)
    
    def draw_buttons(self, surface):
        """Dessine les boutons du menu"""
        button_font = pygame.font.Font(None, 48)
        
        self.play_button.draw(surface, *self.play_pos, button_font)
        self.settings_button.draw(surface, *self.settings_pos, button_font)
        self.quit_button.draw(surface, *self.quit_pos, button_font)
    
    def draw_footer(self, surface):
        """Dessine les informations de bas de page"""
        footer_font = pygame.font.Font(None, 24)
        
        # Version
        version_text = footer_font.render("v1.0 - Alpha", True, (100, 100, 100))
        surface.blit(version_text, (20, self.screen_height - 30))
        
        # Contrôles
        controls_text = footer_font.render("ESC: Quitter | Souris: Navigation", True, (100, 100, 100))
        controls_rect = controls_text.get_rect(right=self.screen_width - 20, 
                                             bottom=self.screen_height - 10)
        surface.blit(controls_text, controls_rect)
    
    def get_selected_action(self):
        """Retourne l'action sélectionnée et la remet à None"""
        action = self.selected_action
        if action:
            print(f"🔄 get_selected_action() retourne: {action}")
        self.selected_action = None
        return action