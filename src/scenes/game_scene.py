"""
Scène principale de jeu - Contient toute la logique extraite de main()
Gère le gameplay principal du roguelike bullet hell Warhammer 40K
"""
import pygame
import math
import random
import sys
import os

# Ajouter le chemin parent pour accéder aux modules racine
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from .base_scene import BaseScene
from ..core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT, WHITE, BLACK
from ..systems.entity_manager import EntityManager
from ..systems.collision_system import CollisionSystem  
from ..world.level_manager import LevelManager

# Imports des modules racine existants
from player import Player
from camera import Camera
from experience_system import ExperienceSystem
from ui_manager import UIManager
from items import ItemManager
from morality_system import MoralitySystem
from sound_system import create_sound_manager

class GameScene(BaseScene):
    """Scène principale de jeu"""
    
    def __init__(self):
        super().__init__()
        
        # === Managers principaux ===
        self.entity_manager = EntityManager()
        self.collision_system = CollisionSystem()
        self.level_manager = LevelManager()
        
        # === Systèmes de jeu ===
        self.player = None
        self.camera = None
        self.exp_system = None
        self.ui_manager = None
        self.item_manager = None
        self.morality_system = None
        self.sound_system = None
        
        # === État du jeu ===
        self.game_state = "playing"  # "playing", "game_over", "paused"
        self.wave_number = 1
        self.enemies_killed = 0
        self.wave_timer = 0
        self.enemies_remaining = 0
        
        # === Contrôles ===
        self.keys_pressed = {}
        
        # === Fontes ===
        self.font = pygame.font.Font(None, 36)
        
        # Initialiser le jeu
        self.initialize_game()
    
    def initialize_game(self):
        """Initialise tous les systèmes de jeu"""
        print("🎮 Initialisation de la scène de jeu...")
        
        # Player et caméra
        self.player = Player(WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT)
        
        # Systèmes
        self.exp_system = ExperienceSystem()
        self.ui_manager = UIManager()
        self.item_manager = ItemManager()
        self.morality_system = MoralitySystem()
        self.sound_system = create_sound_manager()
        
        # Enregistrer le joueur dans l'entity manager
        self.entity_manager.add_player(self.player)
        
        # Générer le premier niveau
        self.generate_wave()
        
        print("✅ Scène de jeu initialisée")
    
    def generate_wave(self):
        """Génère une nouvelle vague d'ennemis"""
        print(f"🌊 Génération de la vague {self.wave_number}")
        
        # Générer le niveau
        walls = self.level_manager.generate_level(self.wave_number, self.morality_system)
        self.entity_manager.set_walls(walls)
        
        # Spawner les ennemis - génération directe
        enemies = self.spawn_enemies_for_wave_direct(self.wave_number)
        
        # Ajouter les ennemis à l'entity manager
        for enemy in enemies:
            self.entity_manager.add_enemy(enemy)
        
        self.enemies_remaining = len(enemies)
        self.wave_timer = 0
        
        # Jouer le son de début de vague
        if self.sound_system:
            self.sound_system.on_wave_start(self.wave_number)
    
    def handle_event(self, event):
        """Gère les événements de jeu"""
        if event.type == pygame.KEYDOWN:
            self.keys_pressed[event.key] = True
            
            # Restart sur R en game over
            if event.key == pygame.K_r and self.game_state == "game_over":
                self.restart_game()
            
            # Pause sur ESC
            elif event.key == pygame.K_ESCAPE and self.game_state == "playing":
                self.game_state = "paused"
        
        elif event.type == pygame.KEYUP:
            if event.key in self.keys_pressed:
                del self.keys_pressed[event.key]
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic gauche
                # Gérer la sélection de level-up
                if (hasattr(self.exp_system, 'is_leveling_up') and 
                    self.exp_system.is_leveling_up):
                    self.handle_level_up_selection(event.pos)
        
        elif event.type == pygame.MOUSEMOTION:
            if hasattr(self.player, 'set_target_direction'):
                # Diriger le joueur vers la souris
                mouse_x, mouse_y = event.pos
                # Convertir en coordonnées monde (conversion manuelle)
                world_x = mouse_x + self.camera.x
                world_y = mouse_y + self.camera.y
                self.player.set_target_direction(world_x, world_y)
    
    def handle_level_up_selection(self, mouse_pos):
        """Gère la sélection lors du level-up"""
        if hasattr(self.exp_system, 'handle_level_up_choice'):
            try:
                choice_index = self.exp_system.get_choice_at_position(mouse_pos)
                if choice_index is not None:
                    self.exp_system.handle_level_up_choice(
                        choice_index, self.morality_system, self.item_manager
                    )
            except:
                # Si la gestion échoue, continuer
                pass
    
    def update(self, dt):
        """Met à jour la logique de jeu"""
        if self.game_state != "playing":
            return
        
        # Mettre à jour le timer de vague
        self.wave_timer += dt
        
        # === UPDATE INPUT ===
        self.update_player_input()
        
        # === UPDATE ENTITIES ===
        # Player
        walls = self.entity_manager.get_walls()
        try:
            self.player.update(walls)
        except TypeError:
            # Si update ne prend pas de paramètres, essayer sans
            try:
                self.player.update()
            except:
                pass  # Si ça échoue, ignorer pour cette frame
        
        # Ennemis
        enemies = self.entity_manager.get_enemies()
        walls = self.entity_manager.get_walls()
        for enemy in enemies[:]:  # Copie pour éviter les modifications concurrentes
            # Mettre à jour l'ennemi - gérer les différentes signatures
            if hasattr(enemy, 'update'):
                try:
                    enemy.update()
                except TypeError:
                    # Certains ennemis pourraient nécessiter des paramètres
                    try:
                        enemy.update(walls)
                    except:
                        pass  # Ignorer si ça ne marche pas
            
            # Passer le joueur et les murs pour l'IA
            if hasattr(enemy, 'update_ai'):
                try:
                    enemy.update_ai(self.player, walls)
                except:
                    # Si l'IA échoue, continuer quand même
                    pass
            
            # Vérifier si l'ennemi est mort
            if hasattr(enemy, 'health') and enemy.health <= 0:
                self.entity_manager.remove_enemy(enemy)
                self.enemies_killed += 1
                self.enemies_remaining -= 1
                
                # Son de mort d'ennemi
                if self.sound_system:
                    self.sound_system.on_enemy_death((enemy.x, enemy.y), (self.player.x, self.player.y), enemy.__class__.__name__)
                
                # Donner de l'expérience
                if hasattr(self.exp_system, 'add_exp'):
                    old_level = getattr(self.exp_system, 'level', 0)
                    self.exp_system.add_exp(10)
                    new_level = getattr(self.exp_system, 'level', 0)
                    
                    # Son de level up si le niveau a augmenté
                    if new_level > old_level and self.sound_system:
                        self.sound_system.on_level_up()
                
                # Moralité selon le type d'ennemi
                if hasattr(self.morality_system, 'process_kill'):
                    self.morality_system.process_kill(enemy.__class__.__name__)
        
        # Projectiles
        projectiles = self.entity_manager.get_projectiles()
        for projectile in projectiles[:]:
            # Vérifier si la méthode update existe et ses paramètres
            if hasattr(projectile, 'update'):
                try:
                    projectile.update()
                except TypeError:
                    # Certains projectiles pourraient nécessiter des paramètres
                    try:
                        projectile.update(walls)
                    except:
                        # Si ça échoue encore, on retire le projectile
                        self.entity_manager.remove_projectile(projectile)
                        continue
            
            # Supprimer les projectiles hors limites
            if (projectile.x < 0 or projectile.x > WORLD_WIDTH or 
                projectile.y < 0 or projectile.y > WORLD_HEIGHT):
                self.entity_manager.remove_projectile(projectile)
        
        # === COLLISIONS ===
        self.collision_system.update(self.entity_manager)
        
        # === CAMERA ===
        try:
            self.camera.update(self.player.x, self.player.y)
        except TypeError:
            # Si la caméra n'accepte pas de paramètres, essayer sans
            try:
                # Peut-être que la caméra a une méthode follow ou set_target
                if hasattr(self.camera, 'follow'):
                    self.camera.follow(self.player)
                elif hasattr(self.camera, 'set_target'):
                    self.camera.set_target(self.player.x, self.player.y)
                elif hasattr(self.camera, 'update'):
                    self.camera.update()
                else:
                    # Fallback : mettre à jour manuellement
                    self.camera.x = self.player.x - SCREEN_WIDTH // 2
                    self.camera.y = self.player.y - SCREEN_HEIGHT // 2
            except:
                # Si tout échoue, continuer sans caméra
                pass
        
        # === SYSTÈMES ===
        # Temporairement désactivé pour éviter les erreurs de compatibilité
        # Morality system
        # if hasattr(self.morality_system, 'update'):
        #     try:
        #         self.morality_system.update(dt)
        #     except TypeError:
        #         self.morality_system.update()
        #     except:
        #         pass
        
        # Experience system
        # if hasattr(self.exp_system, 'update'):
        #     try:
        #         self.exp_system.update(dt)
        #     except TypeError:
        #         self.exp_system.update()
        #     except:
        #         pass
        
        # Mettre à jour le système audio
        if self.sound_system:
            try:
                self.sound_system.update()
            except:
                pass  # Ignorer si ça échoue
        
        # === VÉRIFIER FIN DE VAGUE ===
        if (self.enemies_remaining <= 0 and 
            not (hasattr(self.exp_system, 'is_leveling_up') and self.exp_system.is_leveling_up)):
            self.next_wave()
        
        # === VÉRIFIER GAME OVER ===
        if hasattr(self.player, 'health') and self.player.health <= 0:
            self.game_state = "game_over"
    
    def update_player_input(self):
        """Met à jour les contrôles du joueur"""
        dx, dy = 0, 0
        
        # Mouvement WASD
        if pygame.K_w in self.keys_pressed or pygame.K_z in self.keys_pressed:
            dy -= 1
        if pygame.K_s in self.keys_pressed:
            dy += 1
        if pygame.K_a in self.keys_pressed or pygame.K_q in self.keys_pressed:
            dx -= 1
        if pygame.K_d in self.keys_pressed:
            dx += 1
        
        # Normaliser le mouvement diagonal
        if dx != 0 and dy != 0:
            length = math.sqrt(dx*dx + dy*dy)
            dx /= length
            dy /= length
        
        # Appliquer le mouvement
        walls = self.entity_manager.get_walls()
        if hasattr(self.player, 'move'):
            self.player.move(dx, dy, walls)
        
        # Tir automatique si le joueur a une cible
        enemies = self.entity_manager.get_enemies()
        if enemies and hasattr(self.player, 'can_shoot'):
            try:
                can_shoot = self.player.can_shoot()
            except TypeError:
                # can_shoot pourrait nécessiter des paramètres
                can_shoot = True  # Fallback
            
            if can_shoot:
                # Tirer vers le proche ennemi
                closest_enemy = min(enemies, key=lambda e: 
                    math.sqrt((e.x - self.player.x)**2 + (e.y - self.player.y)**2))
                
                if hasattr(self.player, 'shoot'):
                    projectile = self.player.shoot(closest_enemy.x, closest_enemy.y)
                    if projectile:
                        self.entity_manager.add_projectile(projectile)
                        
                        # Son de tir
                        if self.sound_system:
                            self.sound_system.on_player_shoot((self.player.x, self.player.y), self.morality_system)
    
    def next_wave(self):
        """Passe à la vague suivante"""
        print(f"✅ Vague {self.wave_number} terminée !")
        
        self.wave_number += 1
        
        # Son de fin de vague
        if self.sound_system:
            self.sound_system.on_wave_complete()
        
        # Générer la nouvelle vague
        self.generate_wave()
    
    def spawn_enemies_for_wave_direct(self, wave_number):
        """Génère directement les ennemis pour éviter les problèmes d'imports relatifs"""
        import random  # Import local pour éviter les conflits
        enemies = []
        
        # Import des classes d'ennemis
        from enemies import (
            BasicEnemy, ShooterEnemy, FastEnemy, 
            CultistEnemy, RenegadeMarineEnemy, DaemonEnemy,
            ChaosSorcererBoss, InquisitorLordBoss, DaemonPrinceBoss
        )
        
        # === BOSS WAVES ===
        if wave_number == 5:
            print("🔥 BOSS WAVE ! Un Sorcier du Chaos apparaît !")
            boss_x, boss_y = WORLD_WIDTH // 2, WORLD_HEIGHT // 2
            enemies.append(ChaosSorcererBoss(boss_x, boss_y))
            return enemies
        
        elif wave_number == 15:
            print("⚡ BOSS WAVE ! Un Seigneur Inquisiteur vous défie !")
            boss_x, boss_y = WORLD_WIDTH // 2, WORLD_HEIGHT // 2
            enemies.append(InquisitorLordBoss(boss_x, boss_y))
            return enemies
        
        elif wave_number == 20:
            print("💀 BOSS FINAL ! Un Prince Daemon émerge du Warp !")
            boss_x, boss_y = WORLD_WIDTH // 2, WORLD_HEIGHT // 2
            enemies.append(DaemonPrinceBoss(boss_x, boss_y))
            return enemies
        
        # === VAGUES NORMALES ===
        # Calcul du nombre d'ennemis selon la vague
        base_enemies = min(3 + wave_number, 15)
        total_enemies = base_enemies
        
        # Types d'ennemis selon la vague
        enemy_types = []
        if wave_number >= 1:
            enemy_types.extend([BasicEnemy] * 3)
        if wave_number >= 3:
            enemy_types.extend([ShooterEnemy] * 2)
        if wave_number >= 5:
            enemy_types.extend([FastEnemy] * 2)
        if wave_number >= 7:
            enemy_types.extend([CultistEnemy] * 1)
        if wave_number >= 10:
            enemy_types.extend([RenegadeMarineEnemy] * 1)
        if wave_number >= 12:
            enemy_types.extend([DaemonEnemy] * 1)
        
        # Positions de spawn
        spawn_positions = self.level_manager.current_spawn_positions.copy()
        
        # Générer les ennemis
        for i in range(total_enemies):
            # Choisir un type d'ennemi
            enemy_class = random.choice(enemy_types) if enemy_types else BasicEnemy
            
            # Choisir une position
            if spawn_positions:
                x, y = spawn_positions.pop(0)
            else:
                # Position aléatoire si plus de positions prédéfinies
                x = random.randint(50, WORLD_WIDTH - 50)
                y = random.randint(50, WORLD_HEIGHT - 50)
                
                # Éviter de spawn trop près du joueur
                while abs(x - self.player.x) < 100 and abs(y - self.player.y) < 100:
                    x = random.randint(50, WORLD_WIDTH - 50)
                    y = random.randint(50, WORLD_HEIGHT - 50)
            
            enemies.append(enemy_class(x, y))
        
        print(f"📊 Spawn Wave {wave_number}: {len(enemies)} ennemis créés")
        return enemies
    
    def restart_game(self):
        """Redémarre le jeu"""
        print("🔄 Redémarrage du jeu...")
        
        # Réinitialiser les variables
        self.game_state = "playing"
        self.wave_number = 1
        self.enemies_killed = 0
        self.enemies_remaining = 0
        
        # Réinitialiser le joueur
        if hasattr(self.player, 'reset'):
            self.player.reset(WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
        else:
            # Fallback si pas de méthode reset
            self.player.x = WORLD_WIDTH // 2
            self.player.y = WORLD_HEIGHT // 2
            if hasattr(self.player, 'health'):
                self.player.health = getattr(self.player, 'max_health', 100)
        
        # Nettoyer l'entity manager
        self.entity_manager.clear_all()
        self.entity_manager.add_player(self.player)
        
        # Réinitialiser les systèmes
        if hasattr(self.exp_system, 'reset'):
            self.exp_system.reset()
        if hasattr(self.morality_system, 'reset'):
            self.morality_system.reset()
        else:
            # Fallback pour morality_system
            if hasattr(self.morality_system, '__init__'):
                self.morality_system.__init__()
        
        # Générer la première vague
        self.generate_wave()
    
    def draw(self, screen):
        """Dessine la scène de jeu"""
        # Fond noir
        screen.fill(BLACK)
        
        if self.game_state == "playing":
            self.draw_game(screen)
        elif self.game_state == "game_over":
            self.draw_game_over(screen)
        elif self.game_state == "paused":
            self.draw_paused(screen)
    
    def draw_game(self, screen):
        """Dessine le jeu en cours"""
        # === MONDE (avec caméra) ===
        
        # Murs
        wall_color = self.level_manager.get_wall_color()
        for wall in self.entity_manager.get_walls():
            wall_rect = wall.rect
            # Conversion manuelle des coordonnées monde vers écran
            screen_x = wall_rect.x - self.camera.x
            screen_y = wall_rect.y - self.camera.y
            
            # Ne dessiner que si visible à l'écran
            if (screen_x + wall_rect.width > 0 and screen_x < SCREEN_WIDTH and
                screen_y + wall_rect.height > 0 and screen_y < SCREEN_HEIGHT):
                screen_rect = pygame.Rect(screen_x, screen_y, wall_rect.width, wall_rect.height)
                pygame.draw.rect(screen, wall_color, screen_rect)
        
        # Joueur
        if self.player:
            screen_x = self.player.x - self.camera.x
            screen_y = self.player.y - self.camera.y
            if hasattr(self.player, 'draw'):
                try:
                    # Essayer avec les coordonnées d'écran
                    self.player.draw(screen, screen_x, screen_y)
                except TypeError:
                    # Si ça échoue, sauvegarder la position originale et dessiner
                    original_x, original_y = self.player.x, self.player.y
                    self.player.x, self.player.y = screen_x, screen_y
                    try:
                        self.player.draw(screen)
                    except:
                        # Fallback : cercle blanc
                        pygame.draw.circle(screen, WHITE, (int(screen_x), int(screen_y)), 10)
                    finally:
                        # Restaurer la position originale
                        self.player.x, self.player.y = original_x, original_y
            else:
                pygame.draw.circle(screen, WHITE, (int(screen_x), int(screen_y)), 10)
        
        # Ennemis
        for enemy in self.entity_manager.get_enemies():
            screen_x = enemy.x - self.camera.x
            screen_y = enemy.y - self.camera.y
            if hasattr(enemy, 'draw'):
                try:
                    # Essayer avec les coordonnées d'écran
                    enemy.draw(screen, screen_x, screen_y)
                except TypeError:
                    # Si ça échoue, sauvegarder la position originale et dessiner
                    original_x, original_y = enemy.x, enemy.y
                    enemy.x, enemy.y = screen_x, screen_y
                    try:
                        enemy.draw(screen)
                    except:
                        # Fallback : cercle rouge
                        pygame.draw.circle(screen, (255, 0, 0), (int(screen_x), int(screen_y)), 8)
                    finally:
                        # Restaurer la position originale
                        enemy.x, enemy.y = original_x, original_y
            else:
                pygame.draw.circle(screen, (255, 0, 0), (int(screen_x), int(screen_y)), 8)
        
        # Projectiles
        for projectile in self.entity_manager.get_projectiles():
            screen_x = projectile.x - self.camera.x
            screen_y = projectile.y - self.camera.y
            if hasattr(projectile, 'draw'):
                try:
                    # Essayer avec les coordonnées d'écran
                    projectile.draw(screen, screen_x, screen_y)
                except TypeError:
                    # Si ça échoue, sauvegarder la position originale et dessiner
                    original_x, original_y = projectile.x, projectile.y
                    projectile.x, projectile.y = screen_x, screen_y
                    try:
                        projectile.draw(screen)
                    except:
                        # Fallback : cercle jaune
                        pygame.draw.circle(screen, (255, 255, 0), (int(screen_x), int(screen_y)), 3)
                    finally:
                        # Restaurer la position originale
                        projectile.x, projectile.y = original_x, original_y
            else:
                pygame.draw.circle(screen, (255, 255, 0), (int(screen_x), int(screen_y)), 3)
        
        # === UI ===
        self.draw_hud(screen)
        
        # === LEVEL UP ===
        if hasattr(self.exp_system, 'is_leveling_up') and self.exp_system.is_leveling_up:
            self.draw_level_up(screen)
    
    def draw_hud(self, screen):
        """Dessine le HUD"""
        if self.ui_manager and hasattr(self.ui_manager, 'draw_minimal_hud'):
            self.ui_manager.draw_minimal_hud(
                screen, self.player, self.morality_system, self.exp_system
            )
        
        # Informations de vague
        wave_text = self.font.render(f"Vague {self.wave_number}", True, WHITE)
        screen.blit(wave_text, (10, 10))
        
        enemies_text = self.font.render(f"Ennemis: {self.enemies_remaining}", True, WHITE)
        screen.blit(enemies_text, (10, 50))
        
        # Environnement
        env_text = self.font.render(self.level_manager.get_environment_info(), True, WHITE)
        screen.blit(env_text, (10, 90))
    
    def draw_level_up(self, screen):
        """Dessine l'écran de level-up"""
        if hasattr(self.exp_system, 'draw_level_up_screen'):
            try:
                self.exp_system.draw_level_up_screen(
                    screen, self.morality_system, self.item_manager
                )
            except:
                # Si le rendu échoue, dessiner un message simple
                font = pygame.font.Font(None, 48)
                text = font.render("Level Up!", True, WHITE)
                screen.blit(text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2))
    
    def draw_game_over(self, screen):
        """Dessine l'écran de game over"""
        # Dessiner le jeu en arrière-plan assombri
        self.draw_game(screen)
        
        # Overlay sombre
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((50, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Textes
        game_over_text = self.font.render("GAME OVER", True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 50))
        
        restart_text = self.font.render("Appuie sur R pour recommencer", True, WHITE)
        screen.blit(restart_text, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2))
        
        stats_text = self.font.render(f"Vague: {self.wave_number} - Tués: {self.enemies_killed}", True, WHITE)
        screen.blit(stats_text, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 + 50))
    
    def draw_paused(self, screen):
        """Dessine l'écran de pause"""
        # Dessiner le jeu en arrière-plan
        self.draw_game(screen)
        
        # Overlay de pause
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(100)
        overlay.fill((0, 0, 50))
        screen.blit(overlay, (0, 0))
        
        pause_text = self.font.render("PAUSE", True, WHITE)
        screen.blit(pause_text, (SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT//2))