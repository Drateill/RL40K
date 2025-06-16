import pygame
import math

class UIManager:
    """Gestionnaire de l'interface utilisateur"""
    
    def __init__(self):
        self.is_paused = False
        self.pause_menu_selection = 0
        self.pause_menu_options = ["Reprendre", "Options", "Menu Principal", "Quitter"]
        
        # Animation du menu
        self.menu_alpha = 0
        self.menu_scale = 0.8
        self.button_hover_animations = [0, 0, 0, 0]
        
        # Polices
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Couleurs du thème WH40K
        self.colors = {
            "background": (10, 10, 15),
            "overlay": (0, 0, 0),
            "primary": (200, 180, 100),  # Or impérial
            "secondary": (150, 50, 50),  # Rouge sang
            "accent": (100, 150, 200),   # Bleu tech
            "text": (255, 255, 255),
            "text_dim": (180, 180, 180),
            "border": (100, 100, 120),
            "button_normal": (40, 40, 50),
            "button_hover": (60, 60, 80),
            "button_selected": (80, 60, 40)
        }
        
        # État de l'animation
        self.animation_time = 0
    
    def handle_input(self, event):
        """Gère les inputs de l'UI"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                print(f"ESC pressé ! Pause actuelle: {self.is_paused}")
                self.toggle_pause()
                print(f"Nouvelle pause: {self.is_paused}")
                return True
            
            if self.is_paused:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.pause_menu_selection = (self.pause_menu_selection - 1) % len(self.pause_menu_options)
                    return True
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.pause_menu_selection = (self.pause_menu_selection + 1) % len(self.pause_menu_options)
                    return True
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return self.handle_pause_menu_selection()
        
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_paused:
            mouse_x, mouse_y = event.pos
            button_clicked = self.get_pause_button_at_position(mouse_x, mouse_y)
            if button_clicked >= 0:
                self.pause_menu_selection = button_clicked
                return self.handle_pause_menu_selection()
        
        if event.type == pygame.MOUSEMOTION and self.is_paused:
            mouse_x, mouse_y = event.pos
            button_hovered = self.get_pause_button_at_position(mouse_x, mouse_y)
            if button_hovered >= 0:
                self.pause_menu_selection = button_hovered
        
        return False
    
    def toggle_pause(self):
        """Active/désactive la pause"""
        self.is_paused = not self.is_paused
        if self.is_paused:
            print("Jeu en pause")
        else:
            print("Jeu repris")
    
    def handle_pause_menu_selection(self):
        """Gère la sélection dans le menu pause"""
        selected = self.pause_menu_options[self.pause_menu_selection]
        
        if selected == "Reprendre":
            self.is_paused = False
            return False
        elif selected == "Options":
            # TODO: Implémenter menu options
            print("Menu options - À implémenter")
            return False
        elif selected == "Menu Principal":
            # TODO: Retour au menu principal
            print("Retour menu principal - À implémenter")
            return False
        elif selected == "Quitter":
            return "quit"
        
        return False
    
    def get_pause_button_at_position(self, x, y):
        """Retourne l'index du bouton du menu pause à la position donnée"""
        screen_width = 1024
        screen_height = 768
        
        button_width = 300
        button_height = 60
        button_spacing = 20
        
        start_x = (screen_width - button_width) // 2
        start_y = (screen_height - (len(self.pause_menu_options) * (button_height + button_spacing))) // 2 + 100
        
        for i in range(len(self.pause_menu_options)):
            button_y = start_y + i * (button_height + button_spacing)
            button_rect = pygame.Rect(start_x, button_y, button_width, button_height)
            
            if button_rect.collidepoint(x, y):
                return i
        
        return -1
    
    def update(self):
        """Met à jour les animations de l'UI"""
        self.animation_time += 1
        
        # Animation du menu pause
        if self.is_paused:
            self.menu_alpha = min(200, self.menu_alpha + 10)
            self.menu_scale = min(1.0, self.menu_scale + 0.05)
        else:
            self.menu_alpha = max(0, self.menu_alpha - 15)
            self.menu_scale = max(0.8, self.menu_scale - 0.03)
        
        # Animation des boutons
        for i in range(len(self.button_hover_animations)):
            if i == self.pause_menu_selection and self.is_paused:
                self.button_hover_animations[i] = min(10, self.button_hover_animations[i] + 1)
            else:
                self.button_hover_animations[i] = max(0, self.button_hover_animations[i] - 1)
    
    def draw_pause_menu(self, screen, player=None, morality_system=None, exp_system=None, wave_number=None, enemies_killed=None, enemies_count=None):
        """Dessine le menu pause"""
        print(f"draw_pause_menu appelé - is_paused: {self.is_paused}, menu_alpha: {self.menu_alpha}")
        
        if not self.is_paused and self.menu_alpha <= 0:
            return
        
        screen_width = 1024
        screen_height = 768
        
        # Fond semi-transparent
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(self.menu_alpha)
        overlay.fill(self.colors["overlay"])
        screen.blit(overlay, (0, 0))
        
        if self.menu_alpha < 50:  # Ne pas dessiner le contenu si trop transparent
            return
        
        # HUD détaillé à gauche
        if player and morality_system and exp_system:
            self.draw_detailed_hud(screen, player, morality_system, exp_system, wave_number, enemies_killed, enemies_count)
        
        # Menu à droite
        menu_x_offset = 200  # Décaler le menu vers la droite
        
        # Titre du menu avec effet de scale
        title_scale = self.menu_scale
        title_font = pygame.font.Font(None, int(72 * title_scale))
        title_text = title_font.render("PAUSE", True, self.colors["primary"])
        title_rect = title_text.get_rect(center=(screen_width // 2 + menu_x_offset, 200))
        screen.blit(title_text, title_rect)
        
        # Sous-titre atmosphérique
        subtitle_font = pygame.font.Font(None, int(28 * title_scale))
        subtitle_text = subtitle_font.render("« L'Empereur protège ceux qui attendent »", True, self.colors["text_dim"])
        subtitle_rect = subtitle_text.get_rect(center=(screen_width // 2 + menu_x_offset, 240))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Boutons du menu
        self.draw_pause_buttons(screen, menu_x_offset)
        
        # Instructions en bas
        instruction_text = self.font_small.render("ESC: Reprendre  |  ↑↓: Naviguer  |  ENTRÉE: Sélectionner", True, self.colors["text_dim"])
        instruction_rect = instruction_text.get_rect(center=(screen_width // 2 + menu_x_offset, screen_height - 50))
        screen.blit(instruction_text, instruction_rect)
    
    def draw_pause_buttons(self, screen, x_offset=0):
        """Dessine les boutons du menu pause"""
        screen_width = 1024
        screen_height = 768
        
        button_width = 300
        button_height = 60
        button_spacing = 20
        
        start_x = (screen_width - button_width) // 2 + x_offset
        start_y = (screen_height - (len(self.pause_menu_options) * (button_height + button_spacing))) // 2 + 100
        
        for i, option in enumerate(self.pause_menu_options):
            button_y = start_y + i * (button_height + button_spacing)
            
            # Animation du bouton
            hover_offset = self.button_hover_animations[i]
            is_selected = (i == self.pause_menu_selection)
            
            # Couleur du bouton
            if is_selected:
                button_color = self.colors["button_selected"]
                text_color = self.colors["primary"]
                border_color = self.colors["primary"]
            else:
                button_color = self.colors["button_normal"]
                text_color = self.colors["text"]
                border_color = self.colors["border"]
            
            # Rectangle du bouton avec animation
            button_rect = pygame.Rect(
                start_x - hover_offset,
                button_y - hover_offset // 2,
                button_width + hover_offset * 2,
                button_height + hover_offset
            )
            
            # Ombre du bouton
            shadow_rect = pygame.Rect(button_rect.x + 3, button_rect.y + 3, button_rect.width, button_rect.height)
            pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect)
            
            # Fond du bouton
            pygame.draw.rect(screen, button_color, button_rect)
            
            # Bordure du bouton
            border_width = 3 if is_selected else 2
            pygame.draw.rect(screen, border_color, button_rect, border_width)
            
            # Texte du bouton
            button_font = self.font_medium if is_selected else self.font_small
            button_text = button_font.render(option, True, text_color)
            text_rect = button_text.get_rect(center=button_rect.center)
            screen.blit(button_text, text_rect)
            
            # Effet de sélection
            if is_selected:
                # Petites décorations de chaque côté
                deco_size = 8
                left_deco = [
                    (button_rect.left - 20, button_rect.centery),
                    (button_rect.left - 10, button_rect.centery - deco_size),
                    (button_rect.left - 10, button_rect.centery + deco_size)
                ]
                right_deco = [
                    (button_rect.right + 20, button_rect.centery),
                    (button_rect.right + 10, button_rect.centery - deco_size),
                    (button_rect.right + 10, button_rect.centery + deco_size)
                ]
                
                pygame.draw.polygon(screen, self.colors["primary"], left_deco)
                pygame.draw.polygon(screen, self.colors["primary"], right_deco)
    
    def draw_minimal_hud(self, screen, player, morality_system, exp_system):
        """Dessine un HUD minimal pendant le jeu"""
        if self.is_paused:
            return  # Ne pas dessiner pendant la pause
        
        # 1. BARRE DE VIE - Haut gauche
        self.draw_health_bar(screen, player, 20, 20)
        
        # 2. MORALITÉ - Haut droite
        self.draw_morality_compact(screen, morality_system, 1024 - 250, 20)
        
        # 3. EXPÉRIENCE - Milieu bas
        self.draw_experience_bar(screen, exp_system, 1024 // 2 - 150, 768 - 60)
    
    def draw_health_bar(self, screen, player, x, y):
        """Dessine la barre de vie compacte"""
        bar_width = 200
        bar_height = 20
        
        # Fond de la barre
        pygame.draw.rect(screen, (50, 20, 20), (x, y, bar_width, bar_height))
        
        # Barre de vie
        health_ratio = player.health / player.max_health
        health_width = int(bar_width * health_ratio)
        
        # Couleur selon le niveau de vie
        if health_ratio > 0.6:
            health_color = (50, 200, 50)
        elif health_ratio > 0.3:
            health_color = (200, 200, 50)
        else:
            health_color = (200, 50, 50)
        
        pygame.draw.rect(screen, health_color, (x, y, health_width, bar_height))
        
        # Bordure
        pygame.draw.rect(screen, self.colors["border"], (x, y, bar_width, bar_height), 2)
        
        # Texte de vie
        health_text = self.font_small.render(f"{player.health:.0f} / {player.max_health}", True, self.colors["text"])
        screen.blit(health_text, (x + 5, y + 2))
    
    def draw_morality_compact(self, screen, morality_system, x, y):
        """Dessine la moralité compacte"""
        bar_width = 120
        bar_height = 12
        
        # Titre
        title_text = self.font_small.render("Moralité", True, self.colors["primary"])
        screen.blit(title_text, (x, y))
        
        # Barre de foi
        faith_ratio = morality_system.faith / 100
        faith_width = int(bar_width * faith_ratio)
        
        pygame.draw.rect(screen, (100, 80, 20), (x, y + 20, bar_width, bar_height))
        pygame.draw.rect(screen, (255, 215, 0), (x, y + 20, faith_width, bar_height))
        pygame.draw.rect(screen, self.colors["border"], (x, y + 20, bar_width, bar_height), 1)
        
        faith_text = self.font_small.render(f"Foi: {morality_system.faith:.0f}", True, (255, 215, 0))
        screen.blit(faith_text, (x + bar_width + 5, y + 18))
        
        # Barre de corruption
        corruption_ratio = morality_system.corruption / 100
        corruption_width = int(bar_width * corruption_ratio)
        
        pygame.draw.rect(screen, (80, 20, 80), (x, y + 35, bar_width, bar_height))
        pygame.draw.rect(screen, (200, 50, 200), (x, y + 35, corruption_width, bar_height))
        pygame.draw.rect(screen, self.colors["border"], (x, y + 35, bar_width, bar_height), 1)
        
        corruption_text = self.font_small.render(f"Corruption: {morality_system.corruption:.0f}", True, (200, 50, 200))
        screen.blit(corruption_text, (x + bar_width + 5, y + 33))
        
        # État moral centré
        state_text = self.font_small.render(morality_system.get_state_name(), True, morality_system.get_state_color())
        state_rect = state_text.get_rect(center=(x + bar_width // 2, y + 55))
        screen.blit(state_text, state_rect)
    
    def draw_experience_bar(self, screen, exp_system, x, y):
        """Dessine la barre d'expérience compacte"""
        bar_width = 300
        bar_height = 15
        
        # Fond de la barre
        pygame.draw.rect(screen, (20, 50, 20), (x, y, bar_width, bar_height))
        
        # Barre d'expérience
        exp_ratio = exp_system.experience / exp_system.exp_to_next_level
        exp_width = int(bar_width * exp_ratio)
        
        pygame.draw.rect(screen, (50, 200, 50), (x, y, exp_width, bar_height))
        pygame.draw.rect(screen, self.colors["border"], (x, y, bar_width, bar_height), 2)
        
        # Texte d'expérience centré
        exp_text = self.font_small.render(f"Niveau {exp_system.level} - {exp_system.experience}/{exp_system.exp_to_next_level} XP", True, self.colors["text"])
        text_rect = exp_text.get_rect(center=(x + bar_width // 2, y - 10))
        screen.blit(exp_text, text_rect)
    
    def draw_detailed_hud(self, screen, player, morality_system, exp_system, wave_number, enemies_killed, enemies_count):
        """Dessine le HUD détaillé (menu pause et level-up)"""
        # Panel HUD avec fond semi-transparent
        hud_panel = pygame.Surface((400, 500))
        hud_panel.set_alpha(200)
        hud_panel.fill((20, 20, 30))
        screen.blit(hud_panel, (50, 100))
        
        # Bordure du panel
        pygame.draw.rect(screen, self.colors["border"], (50, 100, 400, 500), 2)
        
        y_offset = 120
        
        # Titre du HUD détaillé
        title_text = self.font_medium.render("STATISTIQUES DÉTAILLÉES", True, self.colors["primary"])
        title_rect = title_text.get_rect(center=(250, y_offset))
        screen.blit(title_text, title_rect)
        y_offset += 50
        
        # Informations de combat
        combat_title = self.font_small.render("Combat:", True, self.colors["accent"])
        screen.blit(combat_title, (70, y_offset))
        y_offset += 25
        
        wave_text = self.font_small.render(f"Vague actuelle: {wave_number}", True, self.colors["text"])
        screen.blit(wave_text, (90, y_offset))
        y_offset += 20
        
        kills_text = self.font_small.render(f"Ennemis éliminés: {enemies_killed}", True, self.colors["text"])
        screen.blit(kills_text, (90, y_offset))
        y_offset += 20
        
        enemies_text = self.font_small.render(f"Ennemis restants: {enemies_count}", True, self.colors["secondary"] if enemies_count > 0 else self.colors["accent"])
        screen.blit(enemies_text, (90, y_offset))
        y_offset += 30
        
        # Informations du joueur
        player_title = self.font_small.render("Joueur:", True, self.colors["accent"])
        screen.blit(player_title, (70, y_offset))
        y_offset += 25
        
        # Statistiques physiques
        size_ratio = player.width / 32.0
        size_text = self.font_small.render(f"Taille: {size_ratio:.1f}x", True, self.colors["text"])
        screen.blit(size_text, (90, y_offset))
        y_offset += 20
        
        speed_text = self.font_small.render(f"Vitesse: {player.speed} (x{getattr(player, 'morality_speed_modifier', 1.0):.2f})", True, self.colors["text"])
        screen.blit(speed_text, (90, y_offset))
        y_offset += 20
        
        damage_text = self.font_small.render(f"Dégâts: {player.base_damage}", True, self.colors["text"])
        screen.blit(damage_text, (90, y_offset))
        y_offset += 20
        
        shots_text = self.font_small.render(f"Projectiles: {player.multi_shot}", True, self.colors["text"])
        screen.blit(shots_text, (90, y_offset))
        y_offset += 30
        
        # Informations système
        system_title = self.font_small.render("Système:", True, self.colors["accent"])
        screen.blit(system_title, (70, y_offset))
        y_offset += 25
        
        fps_text = self.font_small.render(f"FPS: {pygame.time.Clock().get_fps():.0f}", True, self.colors["text"])
        screen.blit(fps_text, (90, y_offset))
        y_offset += 20
    
    def draw_level_up_notification(self, screen):
        """Dessine une notification de level-up stylée"""
        # Animation de flash pour le level-up plus subtile
        flash_intensity = abs(math.sin(self.animation_time * 0.1)) * 15  # Réduit vitesse et intensité
        flash_surface = pygame.Surface((1024, 768))
        flash_surface.set_alpha(flash_intensity)
        flash_surface.fill((255, 215, 0))
        screen.blit(flash_surface, (0, 0))
    
    def should_pause_game(self, exp_system):
        """Détermine si le jeu doit être en pause"""
        return self.is_paused or exp_system.is_leveling_up