"""
Scène principale de jeu - Version corrigée
Contient toute la logique extraite de main()
Gère le gameplay principal du roguelike bullet hell Warhammer 40K

🔧 CORRECTIONS APPLIQUÉES :
- ✅ Caméra centrée sur le joueur
- ✅ Tir au clic de souris
- ✅ Ennemis avec IA active
"""
import pygame
import math
import random
import sys
import os

# Ajouter le chemin parent pour accéder aux modules racine
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import du debug logger
try:
    from ..utils.debug_logger import debug_log, debug_section
except ImportError:
    # Fallback si debug_logger n'est pas disponible
    def debug_log(msg): print(msg)
    def debug_section(title): print(f"=== {title} ===")

from .base_scene import BaseScene
from ..core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT, WHITE, BLACK
from ..systems.entity_manager import EntityManager
from ..systems.collision_system import CollisionSystem  
from ..world.level_manager import LevelManager

# Imports des modules restructurés
from ..entities.player import Player
from ..gameplay.camera import Camera
from ..systems.experience_system import ExperienceSystem
from ..ui.ui_manager import UIManager
from ..ui.hud_manager import HUDManager
from ..ui.scenes.pause_menu import PauseMenuScene
from ..gameplay.items import ItemManager
from ..systems.morality_system import MoralitySystem
from ..systems.sound_system import create_sound_manager
from ..world.background import GameBackground
from ..world.difficulty_manager import DifficultyManager

class GameScene(BaseScene):
    """Scène principale de jeu"""
    
    def __init__(self, selected_archetype=None):
        super().__init__()
        
        # Stocker l'archétype sélectionné
        self.selected_archetype = selected_archetype
        
        # === Managers principaux ===
        self.entity_manager = EntityManager()
        self.collision_system = CollisionSystem()
        self.level_manager = LevelManager()
        
        # Configurer le système de collision pour qu'il ait accès aux autres systèmes
        self.collision_system.game_scene = self
        
        # === Systèmes de jeu ===
        self.player = None
        self.camera = None
        self.exp_system = None
        self.ui_manager = None
        self.item_manager = None
        self.morality_system = None
        self.sound_system = None
        self.background = None
        
        # === État du jeu ===
        self.game_state = "playing"  # "playing", "game_over", "paused"
        self.wave_number = 1
        self.enemies_killed = 0
        self.wave_timer = 0
        self.enemies_remaining = 0
        
        # === Notifications visuelles ===
        self.floating_texts = []  # Pour afficher +XP, +Level, etc.
        
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
        
        # Appliquer l'archétype sélectionné
        if self.selected_archetype:
            self._apply_archetype_to_player(self.selected_archetype)
        
        # CORRECTION: Ajouter le joueur à l'EntityManager
        self.entity_manager.add_player(self.player)
        
        # Systèmes de jeu
        try:
            self.exp_system = ExperienceSystem()
        except:
            print("⚠️  ExperienceSystem non disponible")
            self.exp_system = None
        
        try:
            self.ui_manager = UIManager()
        except:
            print("⚠️  UIManager non disponible")
            self.ui_manager = None
        
        # 🎨 NOUVEAU: HUD Manager pour la nouvelle UI
        self.hud_manager = HUDManager(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # 🎨 NOUVEAU: Menu de pause
        self.pause_menu = PauseMenuScene(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Système de fond animé
        self.background = GameBackground(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Gestionnaire de difficulté
        self.difficulty_manager = DifficultyManager()
        
        try:
            self.item_manager = ItemManager()
        except:
            print("⚠️  ItemManager non disponible")
            self.item_manager = None
        
        try:
            self.morality_system = MoralitySystem()
        except:
            print("⚠️  MoralitySystem non disponible")
            self.morality_system = None
        
        try:
            self.sound_system = create_sound_manager()
        except:
            print("⚠️  SoundSystem non disponible")
            self.sound_system = None
        
        # Configurer les références dans le système de collision
        self.collision_system.exp_system = self.exp_system
        self.collision_system.sound_system = self.sound_system  
        self.collision_system.morality_system = self.morality_system
        
        # Générer le niveau
        self.generate_level()
        
        print("✅ Scène de jeu initialisée")
    
    def generate_level(self):
        """Génère un nouveau niveau"""
        print(f"🏗️  Génération du niveau {self.wave_number}...")
        
        # Nettoyer les entités existantes
        self.entity_manager.clear_all()
        
        # Générer le niveau avec le LevelManager
        try:
            level_data = self.level_manager.generate_level(
                self.wave_number, 
                WORLD_WIDTH, 
                WORLD_HEIGHT
            )
            
            # Ajouter les murs
            if "walls" in level_data:
                for wall_data in level_data["walls"]:
                    wall = self.create_wall_from_data(wall_data)
                    self.entity_manager.add_wall(wall)
            
            # Spawner les ennemis pour cette vague
            self.spawn_wave_enemies()
            
        except Exception as e:
            print(f"⚠️  Erreur génération niveau: {e}")
            # Fallback : niveau vide
            self.spawn_wave_enemies()
    
    def create_wall_from_data(self, wall_data):
        """Crée un mur à partir des données"""
        # Implémentation simple - à adapter selon vos classes
        class SimpleWall:
            def __init__(self, x, y, width, height):
                self.rect = pygame.Rect(x, y, width, height)
                self.x, self.y = x, y
                self.width, self.height = width, height
        
        return SimpleWall(
            wall_data.get("x", 0),
            wall_data.get("y", 0), 
            wall_data.get("width", 32),
            wall_data.get("height", 32)
        )
    
    def create_simple_enemy(self, x, y):
        """Crée un ennemi simple de fallback"""
        class SimpleEnemy:
            def __init__(self, x, y):
                self.x = x
                self.y = y
                self.width = 20
                self.height = 20
                self.health = 30
                self.max_health = 30
                self.speed = 2
                self.rect = pygame.Rect(x, y, 20, 20)
                self.color = (255, 0, 0)  # Rouge
            
            def update(self, player, walls, other_enemies=None):
                """Mouvement simple vers le joueur"""
                if player:
                    # Direction vers le joueur
                    dx = player.x - self.x
                    dy = player.y - self.y
                    
                    # Normaliser et appliquer vitesse
                    import math
                    distance = math.sqrt(dx*dx + dy*dy)
                    if distance > 0:
                        self.x += (dx/distance) * self.speed
                        self.y += (dy/distance) * self.speed
                        self.rect.x = self.x
                        self.rect.y = self.y
            
            def take_damage(self, damage):
                """Prendre des dégâts"""
                self.health -= damage
                return self.health <= 0
            
            def draw(self, screen, screen_x=None, screen_y=None):
                """Dessiner l'ennemi"""
                if screen_x is not None and screen_y is not None:
                    # Coordonnées d'écran fournies
                    pygame.draw.rect(screen, self.color, (screen_x, screen_y, self.width, self.height))
                else:
                    # Coordonnées monde
                    pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
        return SimpleEnemy(x, y)
    
    def add_floating_text(self, x, y, text, color, duration=60):
        """Ajoute un texte flottant à afficher"""
        self.floating_texts.append({
            'x': x,
            'y': y,
            'text': text,
            'color': color,
            'timer': duration,
            'start_y': y
        })
    
    def update_floating_texts(self):
        """Met à jour les textes flottants"""
        for text_data in self.floating_texts[:]:
            text_data['timer'] -= 1
            text_data['y'] = text_data['start_y'] - (60 - text_data['timer']) * 0.5  # Flotte vers le haut
            
            if text_data['timer'] <= 0:
                self.floating_texts.remove(text_data)
    
    def draw_floating_texts(self, screen):
        """Dessine les textes flottants"""
        font = pygame.font.Font(None, 24)
        for text_data in self.floating_texts:
            # Calculer l'alpha pour fade out
            alpha = min(255, text_data['timer'] * 4) if text_data['timer'] < 60 else 255
            
            # Coordonnées écran
            screen_x = text_data['x'] - self.camera.x
            screen_y = text_data['y'] - self.camera.y
            
            # Créer surface avec alpha
            text_surface = font.render(text_data['text'], True, text_data['color'])
            if alpha < 255:
                text_surface.set_alpha(alpha)
            
            # Centrer le texte
            text_rect = text_surface.get_rect(center=(screen_x, screen_y))
            screen.blit(text_surface, text_rect)
    
    def apply_level_up_choice(self):
        """Applique le choix de level-up sélectionné"""
        debug_section("APPLY LEVEL-UP CHOICE")
        debug_log(f"🔧 apply_level_up_choice appelé")
        debug_log(f"   is_leveling_up: {getattr(self.exp_system, 'is_leveling_up', 'N/A')}")
        debug_log(f"   level_up_choices: {getattr(self.exp_system, 'level_up_choices', 'N/A')}")
        debug_log(f"   selected_choice: {getattr(self.exp_system, 'selected_choice', 'N/A')}")
        
        if (not hasattr(self.exp_system, 'is_leveling_up') or 
            not self.exp_system.is_leveling_up or 
            not self.exp_system.level_up_choices):
            debug_log("❌ Conditions not met pour apply_level_up_choice")
            return
        
        selected_idx = getattr(self.exp_system, 'selected_choice', 0)
        if 0 <= selected_idx < len(self.exp_system.level_up_choices):
            item_type = self.exp_system.level_up_choices[selected_idx]
            
            debug_log(f"🎁 Application de l'objet: {item_type}")
            
            # Appliquer l'effet de l'objet au joueur
            debug_log(f"🔧 Application de l'effet...")
            if hasattr(self.item_manager, 'apply_item_directly'):
                debug_log(f"   Utilisation apply_item_directly")
                self.item_manager.apply_item_directly(self.player, item_type, self.morality_system)
            elif hasattr(self.item_manager, 'apply_item_to_player'):
                debug_log(f"   Utilisation apply_item_to_player")
                self.item_manager.apply_item_to_player(item_type, self.player, self.morality_system)
            else:
                debug_log(f"   ❌ Aucune méthode d'application trouvée")
            
            # Marquer le level-up comme terminé
            debug_log(f"🔧 Fin du level-up...")
            if hasattr(self.exp_system, 'finish_level_up'):
                debug_log(f"   Utilisation finish_level_up")
                self.exp_system.finish_level_up()
            else:
                debug_log(f"   Utilisation fallback")
                self.exp_system.is_leveling_up = False
                self.exp_system.level_up_choices = []
            
            # Effet sonore d'acquisition d'objet
            if self.sound_system and hasattr(self.sound_system, 'on_item_pickup'):
                try:
                    self.sound_system.on_item_pickup((self.player.x, self.player.y))
                except:
                    pass
            
            debug_log(f"✅ Level-up terminé, retour au jeu")
    
    def spawn_wave_enemies(self):
        """Génère les ennemis pour la vague actuelle"""
        print(f"🌊 Spawn vague {self.wave_number}...")
        
        # Calculer le nombre d'ennemis selon la vague (progression exponentielle)
        base_enemies = min(5 + int(self.wave_number * 1.4), 25)  # Plus d'ennemis, croissance exponentielle
        
        # Appliquer le multiplicateur de difficulté
        spawn_multiplier = self.difficulty_manager.get_spawn_count_multiplier(self.wave_number)
        actual_enemy_count = int(base_enemies * spawn_multiplier)
        
        print(f"🎯 Difficulté: {self.difficulty_manager.get_difficulty_description(self.wave_number)}")
        print(f"📊 Ennemis prévus: {actual_enemy_count} (base: {base_enemies}, mult: {spawn_multiplier:.1f}x)")
        enemy_types = []
        
        # Tenter d'importer les types d'ennemis un par un
        try:
            from enemies.basic_enemies import BasicEnemy
            enemy_types.append(BasicEnemy)
            print("✅ BasicEnemy importé")
        except Exception as e:
            print(f"⚠️  BasicEnemy échoué: {e}")
        
        try:
            from enemies.basic_enemies import ShooterEnemy
            enemy_types.append(ShooterEnemy)
            print("✅ ShooterEnemy importé")
        except Exception as e:
            print(f"⚠️  ShooterEnemy échoué: {e}")
        
        try:
            from enemies.basic_enemies import FastEnemy
            enemy_types.append(FastEnemy)
            print("✅ FastEnemy importé")
        except Exception as e:
            print(f"⚠️  FastEnemy échoué: {e}")
        
        # Si aucun ennemi n'a pu être importé, créer des ennemis de base simples
        if not enemy_types:
            print("❌ Aucun ennemi importé, création d'ennemis simples...")
            enemy_types = [self.create_simple_enemy]
        
        self.enemies_remaining = base_enemies
        enemies_created = 0
        
        for i in range(actual_enemy_count):
            try:
                # Position aléatoire aux bords de la map
                edge = random.choice(['top', 'bottom', 'left', 'right'])
                if edge == 'top':
                    x, y = random.randint(50, WORLD_WIDTH - 50), 50
                elif edge == 'bottom':
                    x, y = random.randint(50, WORLD_WIDTH - 50), WORLD_HEIGHT - 50
                elif edge == 'left':
                    x, y = 50, random.randint(50, WORLD_HEIGHT - 50)
                else:  # right
                    x, y = WORLD_WIDTH - 50, random.randint(50, WORLD_HEIGHT - 50)
                
                # Choisir un type d'ennemi
                enemy_class = random.choice(enemy_types)
                enemy = enemy_class(x, y)
                
                # Appliquer le scaling de difficulté
                enemy = self.difficulty_manager.apply_enemy_scaling(enemy, self.wave_number)
                
                self.entity_manager.add_enemy(enemy)
                enemies_created += 1
                
            except Exception as e:
                print(f"⚠️  Erreur création ennemi {i}: {e}")
                continue
        
        print(f"✅ {enemies_created}/{actual_enemy_count} ennemis créés avec scaling vague {self.wave_number}")
        # Ajuster le count si certains ennemis n'ont pas pu être créés
        self.enemies_remaining = enemies_created
    
    def handle_event(self, event):
        """Gère les événements de jeu"""
        # 🎨 NOUVEAU: Gérer le menu de pause en priorité
        if self.game_state == "paused":
            if self.pause_menu.handle_event(event):
                action = self.pause_menu.get_selected_action()
                if action == "resume":
                    self.game_state = "playing"
                elif action == "main_menu":
                    # TODO: Retourner au menu principal
                    print("🔧 TODO: Retour au menu principal")
                elif action == "settings":
                    # TODO: Ouvrir les paramètres
                    print("🔧 TODO: Ouvrir paramètres")
                elif action == "quit":
                    pygame.quit()
                    exit()
            return  # Ne pas traiter les autres événements en pause
        
        if event.type == pygame.KEYDOWN:
            self.keys_pressed[event.key] = True
            
            # Pause
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                if self.game_state == "playing":
                    self.game_state = "paused"
                    # 🎨 NOUVEAU: Passer les améliorations au menu de pause
                    acquired_items = getattr(self.item_manager, 'acquired_items', []) if self.item_manager else []
                    self.pause_menu.set_acquired_items(acquired_items)
                elif self.game_state == "paused":
                    self.game_state = "playing"
            
            # Debug: Forcer la vague suivante (N key)
            if event.key == pygame.K_n and self.game_state == "playing":
                print("🔧 Debug: Forcer vague suivante")
                self.next_wave()
            
            # Debug: Afficher état des ennemis (M key)
            if event.key == pygame.K_m and self.game_state == "playing":
                actual_count = len(self.entity_manager.get_enemies())
                print(f"📊 Debug état: enemies_remaining={self.enemies_remaining}, actual_count={actual_count}")
                self.entity_manager.print_status()
            
            # Debug: Ajouter de l'expérience (X key)
            if event.key == pygame.K_x and self.game_state == "playing":
                if hasattr(self.exp_system, 'add_experience'):
                    old_level = getattr(self.exp_system, 'level', 0)
                    old_exp = getattr(self.exp_system, 'experience', 0)
                    print(f"🎯 Debug: +50 XP (avant: {old_exp} XP, niveau {old_level})")
                    
                    self.exp_system.add_experience(50)
                    
                    new_level = getattr(self.exp_system, 'level', 0)
                    new_exp = getattr(self.exp_system, 'experience', 0)
                    print(f"🎯 Debug: après: {new_exp} XP, niveau {new_level}")
                    
                    # Notification
                    self.add_floating_text(self.player.x, self.player.y, "+50 XP", (0, 255, 0))
                    
                    if new_level > old_level:
                        self.add_floating_text(self.player.x, self.player.y - 30, "LEVEL UP!", (255, 215, 0))
                else:
                    print("❌ exp_system non disponible ou pas de add_experience")
            
            # 🔧 PLUS DE GESTION CLAVIER POUR LEVEL-UP
            # Tous les contrôles level-up sont maintenant à la souris uniquement
        
        elif event.type == pygame.KEYUP:
            if event.key in self.keys_pressed:
                del self.keys_pressed[event.key]
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic gauche
                debug_section("MOUSEBUTTONDOWN REÇU")
                debug_log(f"🖱️ Clic détecté - Position: {event.pos}")
                debug_log(f"🖱️ game_state: {self.game_state}")
                debug_log(f"🖱️ hasattr exp_system: {hasattr(self, 'exp_system')}")
                debug_log(f"🖱️ exp_system: {self.exp_system}")
                
                if hasattr(self.exp_system, 'is_leveling_up'):
                    debug_log(f"🖱️ is_leveling_up: {self.exp_system.is_leveling_up}")
                else:
                    debug_log(f"🖱️ exp_system n'a pas is_leveling_up")
                
                # 🔧 PRIORITÉ LEVEL-UP : vérifier en premier
                if (hasattr(self.exp_system, 'is_leveling_up') and 
                    self.exp_system.is_leveling_up):
                    # Gestion level-up avec la souris
                    debug_section("CLIC LEVEL-UP DÉTECTÉ")
                    debug_log(f"🖱️ Event clic pendant level-up détecté")
                    debug_log(f"   Position clic: {event.pos}")
                    debug_log(f"   hasattr handle_input: {hasattr(self.exp_system, 'handle_input')}")
                    
                    if hasattr(self.exp_system, 'handle_input'):
                        debug_log(f"🔧 Appel de handle_input...")
                        result = self.exp_system.handle_input(event)
                        debug_log(f"🔧 handle_input a retourné: {result}")
                        
                        if result:
                            debug_log(f"🎯 handle_input a retourné True, application du choix...")
                            self.apply_level_up_choice()
                            debug_log(f"🎯 apply_level_up_choice terminé, is_leveling_up = {self.exp_system.is_leveling_up}")
                            return
                        else:
                            debug_log(f"❌ handle_input a retourné False - pas de confirmation")
                    else:
                        debug_log(f"❌ handle_input n'existe pas sur exp_system")
                
                elif self.game_state == "playing":
                    debug_log(f"🖱️ game_state = playing - traitement tir normal")
                    # 🔧 CORRECTION: Tir au clic de souris
                    mouse_x, mouse_y = event.pos
                    world_x = mouse_x + self.camera.x
                    world_y = mouse_y + self.camera.y
                    
                    # Tirer vers la position de la souris
                    if hasattr(self.player, 'try_shoot'):
                        projectiles = self.player.try_shoot((world_x, world_y), self.morality_system)
                        if projectiles:
                            for projectile in projectiles:
                                self.entity_manager.add_projectile(projectile)
                            
                            # Son de tir
                            if self.sound_system:
                                self.sound_system.on_player_shoot((self.player.x, self.player.y), self.morality_system)
        
        elif event.type == pygame.MOUSEMOTION:
            # Priorité au level-up si en cours
            if (hasattr(self.exp_system, 'is_leveling_up') and 
                self.exp_system.is_leveling_up):
                if hasattr(self.exp_system, 'handle_input'):
                    self.exp_system.handle_input(event)
                return
            
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
        
        # 🔧 PAUSE pendant le level-up
        if (hasattr(self.exp_system, 'is_leveling_up') and 
            self.exp_system.is_leveling_up):
            # Ne mettre à jour que les animations d'interface pendant le level-up
            if hasattr(self.exp_system, 'update'):
                self.exp_system.update()
            self.update_floating_texts()
            return  # Arrêter ici - pas de mise à jour du gameplay
        
        # DEBUG - vérifier l'état des systèmes
        if not self.player:
            print("⚠️  Pas de joueur !")
            return
        
        # Mettre à jour le timer de vague
        self.wave_timer += dt
        
        # === UPDATE INPUT ===
        self.update_player_input()
        
        # === UPDATE ENTITIES ===
        # Player - 🔧 CORRECTION: Passer morality_system
        walls = self.entity_manager.get_walls()
        if self.player:
            try:
                self.player.update(walls, self.morality_system)
            except TypeError:
                try:
                    self.player.update(walls)
                except TypeError:
                    try:
                        self.player.update()
                    except:
                        pass  # Ignorer si incompatible
        
        # Ennemis - 🔧 CORRECTION: Passer tous les paramètres pour l'IA
        enemies = self.entity_manager.get_enemies()
        walls = self.entity_manager.get_walls()
        for enemy in enemies[:]:  # Copie pour éviter les modifications concurrentes
            if hasattr(enemy, 'update'):
                try:
                    # Passer tous les paramètres nécessaires pour l'IA
                    enemy.update(self.player, walls, enemies)
                except TypeError:
                    try:
                        # Fallback pour compatibilité
                        enemy.update(self.player, walls)
                    except TypeError:
                        try:
                            enemy.update()
                        except:
                            pass  # Ignorer si vraiment incompatible
            
            # Vérifier si l'ennemi est mort (il sera supprimé par le système de collision)
            # Cette vérification n'est plus nécessaire car le système de collision gère tout
            pass
        
        # Projectiles - CORRECTION: Passer les bons paramètres à update()
        projectiles = self.entity_manager.get_projectiles()
        for projectile in projectiles[:]:
            # Vérifier si la méthode update existe et ses paramètres
            if hasattr(projectile, 'update'):
                try:
                    # La méthode Bullet.update() attend: walls, screen_width, screen_height, enemies
                    enemies = self.entity_manager.get_enemies()
                    result = projectile.update(walls, WORLD_WIDTH, WORLD_HEIGHT, enemies)
                    
                    # Si update() retourne False, supprimer le projectile
                    if result is False:
                        self.entity_manager.remove_projectile(projectile)
                        continue
                        
                except TypeError:
                    # Fallback pour compatibilité avec d'anciens projectiles
                    try:
                        projectile.update(walls)
                    except:
                        # Si ça échoue encore, on retire le projectile
                        self.entity_manager.remove_projectile(projectile)
                        continue
            
            # Supprimer les projectiles hors limites (sécurité supplémentaire)
            if (projectile.x < 0 or projectile.x > WORLD_WIDTH or 
                projectile.y < 0 or projectile.y > WORLD_HEIGHT):
                self.entity_manager.remove_projectile(projectile)
        
        # === COLLISIONS ===
        self.collision_system.update(self.entity_manager)
        
        # === CAMERA === - 🔧 CORRECTION: Passer l'objet player directement
        if self.camera and self.player:
            self.camera.update(self.player)
        
        # === SYSTÈMES ===
        # === SYSTÈMES DE JEU ===
        # Morality system
        if hasattr(self.morality_system, 'update'):
            try:
                self.morality_system.update(dt)
            except TypeError:
                try:
                    self.morality_system.update()
                except:
                    pass
        
        # Experience system - ACTIVÉ
        if hasattr(self.exp_system, 'update'):
            try:
                self.exp_system.update()
            except:
                pass
        
        # Générer les choix de level-up si nécessaire
        if (hasattr(self.exp_system, 'is_leveling_up') and 
            self.exp_system.is_leveling_up and 
            not self.exp_system.level_up_choices):
            print("🎲 Génération des choix de level-up...")
            if hasattr(self.exp_system, 'generate_level_up_choices'):
                self.exp_system.generate_level_up_choices(self.morality_system, self.item_manager, self.player)
        
        # Mettre à jour le système audio
        if self.sound_system:
            try:
                self.sound_system.update()
            except:
                pass  # Ignorer si ça échoue
        
        # Mettre à jour les textes flottants
        self.update_floating_texts()
        
        # Mettre à jour le fond animé
        if self.background:
            self.background.update(dt, self.camera.x, self.camera.y)
        
        # === VÉRIFIER FIN DE VAGUE ===
        # Compter les ennemis réellement présents
        actual_enemies_count = len(self.entity_manager.get_enemies())
        
        # Si pas d'ennemis ET que enemies_remaining est <= 0, passer à la vague suivante
        if (actual_enemies_count <= 0 and self.enemies_remaining <= 0 and 
            not (hasattr(self.exp_system, 'is_leveling_up') and self.exp_system.is_leveling_up)):
            print(f"🏁 Vague {self.wave_number} terminée (ennemis restants: {actual_enemies_count})")
            self.next_wave()
        
        # Correction si enemies_remaining est décalé par rapport à la réalité
        elif actual_enemies_count == 0 and self.enemies_remaining > 0:
            print(f"🔧 Correction: enemies_remaining={self.enemies_remaining} mais 0 ennemis présents")
            self.enemies_remaining = 0
        
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
        
        # Tir automatique si le joueur a une cible - 🔧 CORRECTION: try_shoot au lieu de shoot
        enemies = self.entity_manager.get_enemies()
        if enemies:
            # Vérifier si le joueur peut tirer (en vérifiant le timer)
            can_shoot = getattr(self.player, 'shoot_timer', 0) <= 0
            
            if can_shoot:
                # Tirer vers l'ennemi le plus proche
                closest_enemy = min(enemies, key=lambda e: 
                    math.sqrt((e.x - self.player.x)**2 + (e.y - self.player.y)**2))
                
                if hasattr(self.player, 'try_shoot'):
                    # Utiliser try_shoot avec position de l'ennemi
                    projectiles = self.player.try_shoot((closest_enemy.x, closest_enemy.y), self.morality_system)
                    if projectiles:
                        for projectile in projectiles:
                            self.entity_manager.add_projectile(projectile)
                        
                        # Son de tir
                        if self.sound_system:
                            self.sound_system.on_player_shoot((self.player.x, self.player.y), self.morality_system)
    
    def next_wave(self):
        """Passe à la vague suivante"""
        print(f"✅ Vague {self.wave_number} terminée !")
        self.wave_number += 1
        self.wave_timer = 0
        
        # Générer la nouvelle vague
        self.generate_level()
        
        print(f"🌊 Début de la vague {self.wave_number}")
    
    def draw(self, screen):
        """Dessine la scène de jeu"""
        # Dessiner le fond animé au lieu du noir uniforme
        if self.background:
            self.background.draw(screen, self.camera.x, self.camera.y)
        else:
            screen.fill(BLACK)
        
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
        
        # Textes flottants (+XP, etc.)
        self.draw_floating_texts(screen)
        
        # === UI (coordonnées écran) ===
        
        # Informations de jeu
        if self.game_state == "playing":
            self.draw_hud(screen)
        elif self.game_state == "paused":
            self.draw_pause_screen(screen)
        elif self.game_state == "game_over":
            self.draw_game_over_screen(screen)
        
        # Level-up screen
        if (hasattr(self.exp_system, 'is_leveling_up') and 
            self.exp_system.is_leveling_up):
            if hasattr(self.exp_system, 'draw_level_up_screen'):
                try:
                    self.exp_system.draw_level_up_screen(screen, self.morality_system, self.item_manager)
                except TypeError:
                    # Fallback si la signature est différente
                    try:
                        self.exp_system.draw_level_up_screen(screen)
                    except:
                        # Affichage simple de fallback
                        self.draw_simple_level_up_screen(screen)
        
        # 🎨 NOUVEAU: HUD moderne
        if self.game_state == "playing":
            # HUD principal (barres de vie, XP, moralité)
            self.hud_manager.draw_hud(screen, self.player, self.exp_system, self.morality_system)
            
            # Barres de vie des ennemis
            enemies = self.entity_manager.get_enemies()
            self.hud_manager.draw_enemy_health_bars(screen, enemies, self.camera.x, self.camera.y)
        
        # 🎨 NOUVEAU: Menu de pause moderne
        elif self.game_state == "paused":
            self.pause_menu.draw(screen)
    
    def draw_hud(self, screen):
        """Dessine l'interface utilisateur"""
        # Santé
        if hasattr(self.player, 'health'):
            health_text = f"Vie: {self.player.health}/{getattr(self.player, 'max_health', 100)}"
            text_surface = self.font.render(health_text, True, WHITE)
            screen.blit(text_surface, (10, 10))
        
        # Vague
        wave_text = f"Vague: {self.wave_number}"
        wave_surface = self.font.render(wave_text, True, WHITE)
        screen.blit(wave_surface, (10, 50))
        
        # Ennemis restants
        enemies_text = f"Ennemis: {self.enemies_remaining}"
        enemies_surface = self.font.render(enemies_text, True, WHITE)
        screen.blit(enemies_surface, (10, 90))
        
        # Expérience
        if hasattr(self.exp_system, 'level'):
            exp_text = f"Niveau: {self.exp_system.level}"
            exp_surface = self.font.render(exp_text, True, WHITE)
            screen.blit(exp_surface, (10, 130))
            
            # Barre d'expérience
            if hasattr(self.exp_system, 'draw_exp_bar'):
                self.exp_system.draw_exp_bar(screen, 10, 160)
    
    def draw_pause_screen(self, screen):
        """Dessine l'écran de pause"""
        # Overlay semi-transparent
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Texte PAUSE
        pause_text = "JEU EN PAUSE"
        pause_surface = self.font.render(pause_text, True, WHITE)
        text_rect = pause_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(pause_surface, text_rect)
        
        # Instructions
        instr_text = "Appuyez sur ÉCHAP pour reprendre"
        instr_surface = self.font.render(instr_text, True, WHITE)
        instr_rect = instr_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        screen.blit(instr_surface, instr_rect)
    
    def draw_game_over_screen(self, screen):
        """Dessine l'écran de game over"""
        # Fond rouge semi-transparent
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((100, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Texte GAME OVER
        game_over_text = "GAME OVER"
        game_over_surface = self.font.render(game_over_text, True, WHITE)
        text_rect = game_over_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(game_over_surface, text_rect)
        
        # Statistiques
        stats_text = f"Vague atteinte: {self.wave_number}"
        stats_surface = self.font.render(stats_text, True, WHITE)
        stats_rect = stats_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        screen.blit(stats_surface, stats_rect)
        
        kills_text = f"Ennemis tués: {self.enemies_killed}"
        kills_surface = self.font.render(kills_text, True, WHITE)
        kills_rect = kills_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 90))
        screen.blit(kills_surface, kills_rect)
    
    def draw_simple_level_up_screen(self, screen):
        """Écran de level-up simple de fallback"""
        # Overlay semi-transparent
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Titre
        level_text = "LEVEL UP!"
        level_surface = self.font.render(level_text, True, WHITE)
        level_rect = level_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        screen.blit(level_surface, level_rect)
        
        # Instructions
        instr_text = "Appuyez sur ESPACE pour continuer"
        instr_surface = self.font.render(instr_text, True, WHITE)
        instr_rect = instr_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        screen.blit(instr_surface, instr_rect)
    
    def _apply_archetype_to_player(self, archetype_id):
        """Applique l'archétype sélectionné au joueur"""
        from ..gameplay.archetype_manager import ArchetypeManager
        
        archetype_manager = ArchetypeManager()
        success = archetype_manager.apply_archetype_to_player(
            self.player, archetype_id, self.player.weapon_manager
        )
        
        if success:
            print(f"✅ Archétype {archetype_id} appliqué avec succès au joueur")
        else:
            print(f"❌ Échec de l'application de l'archétype {archetype_id}")
            # Fallback sur l'arme de base si l'archétype échoue
            print("🔧 Utilisation de l'arme de base en fallback")