"""
Gestionnaire de l'interface utilisateur du jeu
"""
import pygame
from .components.health_bar import PlayerHealthBar, EnemyHealthBar
from .components.progress_bars import ExperienceBar, MoralityBar

class HUDManager:
    """Gestionnaire du HUD pendant le jeu"""
    
    def __init__(self, screen_width=1200, screen_height=800):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Composants UI
        self.player_health_bar = PlayerHealthBar()
        self.enemy_health_bar = EnemyHealthBar()
        self.experience_bar = ExperienceBar()
        self.morality_bar = MoralityBar()
        
        # Calcul des positions centrées (80% de largeur d'écran)
        bar_width = int(screen_width * 0.8)  # 80% de la largeur
        bar_start_x = (screen_width - bar_width) // 2  # Centré horizontalement
        
        # Positions dans le HUD avec espacement vertical adéquat
        self.health_pos = (bar_start_x, screen_height - 110)
        self.exp_pos = (bar_start_x, screen_height - 70) 
        self.morality_pos = (bar_start_x, screen_height - 160)
        
    def update(self, dt):
        """Met à jour l'UI"""
        # Mettre à jour les animations des barres
        pass
    
    def draw_hud(self, surface, player, exp_system, morality_system):
        """Dessine le HUD principal"""
        if not player:
            return
            
        # Barre de vie du joueur
        if hasattr(player, 'health') and hasattr(player, 'max_health'):
            self.player_health_bar.draw_hud(surface, *self.health_pos, 
                                          player.health, player.max_health)
        
        # Barre d'expérience
        if exp_system:
            level = getattr(exp_system, 'level', 1)
            current_exp = getattr(exp_system, 'experience', 0)
            exp_to_next = getattr(exp_system, 'exp_to_next_level', 100)
            
            self.experience_bar.draw_hud(surface, *self.exp_pos, 
                                       current_exp, exp_to_next, level)
        
        # Barre de moralité
        if morality_system:
            faith = getattr(morality_system, 'faith', 0)
            corruption = getattr(morality_system, 'corruption', 0)
            
            self.morality_bar.draw_hud(surface, *self.morality_pos, 
                                     faith, corruption)
        
        # Informations d'arme (munitions, rechargement, multi-armes)
        if hasattr(player, 'weapons') and player.weapons:
            self.draw_multi_weapon_info(surface, player)
        elif hasattr(player, 'current_weapon') and player.current_weapon:
            self.draw_weapon_info(surface, player.current_weapon)
    
    def draw_weapon_info(self, surface, weapon):
        """Dessine les informations de l'arme actuelle"""
        weapon_info = weapon.get_info()
        
        # Position en haut à droite
        font = pygame.font.Font(None, 28)
        small_font = pygame.font.Font(None, 22)
        
        x = self.screen_width - 250
        y = 20
        
        # Nom de l'arme
        weapon_name = weapon_info.get('name', 'Arme Inconnue')
        name_surface = font.render(weapon_name, True, (255, 255, 255))
        surface.blit(name_surface, (x, y))
        y += 30
        
        # Munitions (seulement si l'arme en a)
        max_ammo = weapon_info.get('max_ammo', -1)
        if max_ammo > 0:
            current_ammo = weapon_info.get('current_ammo', 0)
            
            # Couleur selon le niveau de munitions
            if current_ammo == 0:
                ammo_color = (255, 100, 100)  # Rouge si vide
            elif current_ammo <= max_ammo * 0.3:
                ammo_color = (255, 255, 100)  # Jaune si faible
            else:
                ammo_color = (255, 255, 255)  # Blanc si ok
            
            ammo_text = f"Munitions: {current_ammo}/{max_ammo}"
            ammo_surface = small_font.render(ammo_text, True, ammo_color)
            surface.blit(ammo_surface, (x, y))
            y += 25
            
            # Indicateur de rechargement
            if weapon_info.get('is_reloading', False):
                reload_progress = weapon_info.get('reload_progress', 0)
                reload_text = f"Rechargement... {int(reload_progress * 100)}%"
                reload_surface = small_font.render(reload_text, True, (100, 255, 100))
                surface.blit(reload_surface, (x, y))
                
                # Barre de rechargement
                bar_width = 150
                bar_height = 8
                bar_x = x
                bar_y = y + 20
                
                # Fond de la barre
                pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
                
                # Progression
                progress_width = int(bar_width * reload_progress)
                pygame.draw.rect(surface, (100, 255, 100), (bar_x, bar_y, progress_width, bar_height))
                
                # Bordure
                pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)
                y += 30
        
        # Aide pour rechargement manuel
        if max_ammo > 0 and not weapon_info.get('is_reloading', False):
            help_text = "Appuyez sur R pour recharger"
            help_surface = pygame.font.Font(None, 18).render(help_text, True, (180, 180, 180))
            surface.blit(help_surface, (x, y))
    
    def draw_multi_weapon_info(self, surface, player):
        """Dessine les informations pour le système multi-armes"""
        font = pygame.font.Font(None, 24)
        small_font = pygame.font.Font(None, 18)
        
        x = self.screen_width - 280
        y = 20
        
        # Titre
        title = font.render(f"Arsenal ({len(player.weapons)} armes)", True, (255, 255, 255))
        surface.blit(title, (x, y))
        y += 25
        
        # Liste des armes avec indicateur actuel
        for i, weapon in enumerate(player.weapons):
            weapon_info = weapon.get_info()
            is_active = (i == player.current_weapon_index)
            
            # Couleur selon l'état
            if is_active:
                name_color = (255, 255, 100)  # Jaune pour l'arme active
                prefix = "► "
            else:
                name_color = (180, 180, 180)  # Gris pour les autres
                prefix = f"{i+1}. "
            
            # Nom de l'arme
            weapon_name = f"{prefix}{weapon_info.get('name', 'Arme Inconnue')}"
            name_surface = small_font.render(weapon_name, True, name_color)
            surface.blit(name_surface, (x, y))
            y += 18
            
            # Munitions pour l'arme active
            if is_active:
                max_ammo = weapon_info.get('max_ammo', -1)
                if max_ammo > 0:
                    current_ammo = weapon_info.get('current_ammo', 0)
                    
                    # Couleur selon munitions
                    if current_ammo == 0:
                        ammo_color = (255, 100, 100)
                    elif current_ammo <= max_ammo * 0.3:
                        ammo_color = (255, 255, 100)
                    else:
                        ammo_color = (255, 255, 255)
                    
                    ammo_text = f"    Munitions: {current_ammo}/{max_ammo}"
                    ammo_surface = small_font.render(ammo_text, True, ammo_color)
                    surface.blit(ammo_surface, (x, y))
                    y += 16
                    
                    # Rechargement
                    if weapon_info.get('is_reloading', False):
                        reload_progress = weapon_info.get('reload_progress', 0)
                        reload_text = f"    Rechargement... {int(reload_progress * 100)}%"
                        reload_surface = small_font.render(reload_text, True, (100, 255, 100))
                        surface.blit(reload_surface, (x, y))
                        y += 16
        
        y += 10
        
        # Améliorations globales
        if hasattr(player, 'global_upgrades'):
            upgrades_text = small_font.render("Améliorations globales:", True, (200, 200, 255))
            surface.blit(upgrades_text, (x, y))
            y += 18
            
            upgrades = player.global_upgrades
            if upgrades['damage_bonus'] > 0:
                damage_text = small_font.render(f"  +{upgrades['damage_bonus']} Dégâts", True, (255, 200, 200))
                surface.blit(damage_text, (x, y))
                y += 16
            
            if upgrades['multi_shot_bonus'] > 0:
                multi_text = small_font.render(f"  +{upgrades['multi_shot_bonus']} Projectiles", True, (200, 255, 200))
                surface.blit(multi_text, (x, y))
                y += 16
            
            if upgrades['piercing']:
                piercing_text = small_font.render("  Perforant actif", True, (255, 255, 200))
                surface.blit(piercing_text, (x, y))
                y += 16
            
            if upgrades['explosive']:
                explosive_text = small_font.render("  Explosif actif", True, (255, 150, 100))
                surface.blit(explosive_text, (x, y))
                y += 16
        
        # Instructions
        y += 5
        if len(player.weapons) > 1:
            help_text = "Touches 1-9 pour changer d'arme"
            help_surface = pygame.font.Font(None, 16).render(help_text, True, (150, 150, 150))
            surface.blit(help_surface, (x, y))
            y += 14
        
        help_text2 = "R pour recharger"
        help_surface2 = pygame.font.Font(None, 16).render(help_text2, True, (150, 150, 150))
        surface.blit(help_surface2, (x, y))
    
    def draw_enemy_health_bars(self, surface, enemies, camera_x=0, camera_y=0):
        """Dessine les barres de vie des ennemis"""
        for enemy in enemies:
            if hasattr(enemy, 'health') and hasattr(enemy, 'max_health'):
                # Ne dessiner que si l'ennemi est blessé et visible
                if (enemy.health < enemy.max_health and 
                    -50 <= enemy.x - camera_x <= self.screen_width + 50 and
                    -50 <= enemy.y - camera_y <= self.screen_height + 50):
                    
                    self.enemy_health_bar.draw_above_enemy(surface, enemy, camera_x, camera_y)
    
    def draw_debug_info(self, surface, player, enemies, wave_info=None):
        """Dessine les informations de debug (optionnel)"""
        debug_font = pygame.font.Font(None, 24)
        y_offset = 20
        
        # Info joueur
        if player:
            player_info = f"Joueur: Pos({int(player.x)}, {int(player.y)})"
            if hasattr(player, 'health'):
                player_info += f" HP: {player.health}/{getattr(player, 'max_health', '?')}"
            
            debug_surface = debug_font.render(player_info, True, (255, 255, 255))
            surface.blit(debug_surface, (self.screen_width - 300, y_offset))
            y_offset += 25
        
        # Info ennemis
        enemy_count = len(enemies) if enemies else 0
        enemy_info = f"Ennemis: {enemy_count}"
        debug_surface = debug_font.render(enemy_info, True, (255, 255, 255))
        surface.blit(debug_surface, (self.screen_width - 300, y_offset))
        y_offset += 25
        
        # Info vague
        if wave_info:
            wave_text = f"Vague: {wave_info}"
            debug_surface = debug_font.render(wave_text, True, (255, 255, 255))
            surface.blit(debug_surface, (self.screen_width - 300, y_offset))