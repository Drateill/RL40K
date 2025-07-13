import pygame
import random
import math
from player import Player
from enemies import BasicEnemy, ShooterEnemy, FastEnemy, CultistEnemy, RenegadeMarineEnemy, DaemonEnemy
from enemies import ChaosSorcererBoss, InquisitorLordBoss, DaemonPrinceBoss
from wall import create_border_walls, create_interior_walls
from items import ItemManager
from camera import Camera
from pathfinding import PathfindingHelper
from morality_system import MoralitySystem
from experience_system import ExperienceSystem
from ui_manager import UIManager
from morality_effects import MoralityEffects
from bullet import Bullet
from sound_system import create_sound_manager

# Initialisation
pygame.init()

# Constantes
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
WORLD_WIDTH = 3072   # Monde plus grand pour bullet hell
WORLD_HEIGHT = 2304  # Monde plus grand pour bullet hell
FPS = 60

# Couleurs
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Classe utilitaire pour la compatibilité avec le pathfinding
class WallWrapper:
    """Wrapper pour les murs pour compatibilité avec PathfindingHelper"""
    def __init__(self, rect):
        self.rect = rect

# Nouvelle classe pour la génération de monde intégrée
class SimpleWorldGenerator:
    """Générateur de monde simplifié intégré directement dans main.py"""
    
    def __init__(self):
        self.current_environment = "neutral"
        self.current_layout = "standard"
        
    def determine_environment(self, morality_system):
        """Détermine l'environnement selon la moralité"""
        if not morality_system:
            return "neutral"
            
        faith = morality_system.faith
        corruption = morality_system.corruption
        
        if faith >= 80:
            return "imperial_shrine"
        elif faith >= 60:
            return "neutral_ruins"
        elif corruption >= 90:
            return "daemon_realm"
        elif corruption >= 70:
            return "chaos_temple"
        elif corruption >= 40:
            return "hive_city"
        else:
            return "battlefield"
    
    def create_boss_arena(self, world_width, world_height):
        """Crée une arène optimisée pour les boss"""
        walls = []
        
        # Murs de bordure
        wall_thickness = 30
        walls.extend([
            pygame.Rect(0, 0, world_width, wall_thickness),  # Haut
            pygame.Rect(0, world_height - wall_thickness, world_width, wall_thickness),  # Bas
            pygame.Rect(0, 0, wall_thickness, world_height),  # Gauche
            pygame.Rect(world_width - wall_thickness, 0, wall_thickness, world_height)  # Droite
        ])
        
        # Piliers stratégiques pour la couverture (optimisés bullet hell)
        arena_center_x = world_width // 2
        arena_center_y = world_height // 2
        
        # 4 piliers aux coins de l'arène centrale
        pillar_size = 60
        pillar_distance = 200
        
        pillar_positions = [
            (arena_center_x - pillar_distance, arena_center_y - pillar_distance),  # Top-left
            (arena_center_x + pillar_distance, arena_center_y - pillar_distance),  # Top-right
            (arena_center_x - pillar_distance, arena_center_y + pillar_distance),  # Bottom-left
            (arena_center_x + pillar_distance, arena_center_y + pillar_distance),  # Bottom-right
        ]
        
        for x, y in pillar_positions:
            walls.append(pygame.Rect(x - pillar_size//2, y - pillar_size//2, pillar_size, pillar_size))
        
        return walls
    
    def create_standard_layout(self, world_width, world_height, environment):
        """Crée un layout standard adapté à l'environnement"""
        walls = []
        
        # Murs de bordure
        wall_thickness = 30
        walls.extend([
            pygame.Rect(0, 0, world_width, wall_thickness),
            pygame.Rect(0, world_height - wall_thickness, world_width, wall_thickness),
            pygame.Rect(0, 0, wall_thickness, world_height),
            pygame.Rect(world_width - wall_thickness, 0, wall_thickness, world_height)
        ])
        
        # Obstacles selon l'environnement
        if environment == "imperial_shrine":
            walls.extend(self.create_gothic_pillars(world_width, world_height))
        elif environment == "chaos_temple":
            walls.extend(self.create_chaos_formation(world_width, world_height))
        elif environment == "battlefield":
            walls.extend(self.create_battlefield_cover(world_width, world_height))
        elif environment == "daemon_realm":
            walls.extend(self.create_warp_distortions(world_width, world_height))
        else:
            walls.extend(self.create_neutral_obstacles(world_width, world_height))
        
        return walls
    
    def create_gothic_pillars(self, world_width, world_height):
        """Crée des piliers gothiques symétriques"""
        pillars = []
        pillar_width = 40
        pillar_height = 120
        
        # Formation en croix gothique
        positions = [
            (world_width * 0.3, world_height * 0.3),
            (world_width * 0.7, world_height * 0.3),
            (world_width * 0.3, world_height * 0.7),
            (world_width * 0.7, world_height * 0.7),
            (world_width * 0.5, world_height * 0.2),
            (world_width * 0.5, world_height * 0.8),
            (world_width * 0.2, world_height * 0.5),
            (world_width * 0.8, world_height * 0.5),
        ]
        
        for x, y in positions:
            pillars.append(pygame.Rect(int(x - pillar_width//2), int(y - pillar_height//2), 
                                     pillar_width, pillar_height))
        
        return pillars
    
    def create_chaos_formation(self, world_width, world_height):
        """Crée une formation chaotique"""
        obstacles = []
        center_x = world_width // 2
        center_y = world_height // 2
        
        # Formation en étoile chaotique
        for i in range(8):
            angle = (i / 8) * 2 * math.pi + random.uniform(-0.3, 0.3)
            distance = random.uniform(150, 250)
            
            x = center_x + math.cos(angle) * distance
            y = center_y + math.sin(angle) * distance
            
            size = random.randint(40, 80)
            obstacles.append(pygame.Rect(int(x - size//2), int(y - size//2), size, size))
        
        return obstacles
    
    def create_battlefield_cover(self, world_width, world_height):
        """Crée des couvertures de champ de bataille"""
        covers = []
        
        # Barricades horizontales et verticales
        barricade_length = 120
        barricade_width = 25
        
        # Pattern de tranchées
        for i in range(3):
            # Barricades horizontales
            x = world_width * (0.2 + i * 0.3) - barricade_length // 2
            y = world_height * 0.4 - barricade_width // 2
            covers.append(pygame.Rect(int(x), int(y), barricade_length, barricade_width))
            
            y = world_height * 0.6 - barricade_width // 2
            covers.append(pygame.Rect(int(x), int(y), barricade_length, barricade_width))
        
        # Barricades verticales
        for i in range(2):
            x = world_width * 0.5 - barricade_width // 2
            y = world_height * (0.3 + i * 0.4) - barricade_length // 2
            covers.append(pygame.Rect(int(x), int(y), barricade_width, barricade_length))
        
        return covers
    
    def create_warp_distortions(self, world_width, world_height):
        """Crée des distorsions warp chaotiques"""
        distortions = []
        
        # Formations imprévisibles
        for _ in range(12):
            x = random.randint(100, world_width - 100)
            y = random.randint(100, world_height - 100)
            width = random.randint(30, 100)
            height = random.randint(30, 100)
            
            # Éviter le centre pour le mouvement
            center_x = world_width // 2
            center_y = world_height // 2
            if abs(x - center_x) < 200 and abs(y - center_y) < 200:
                continue
                
            distortions.append(pygame.Rect(x, y, width, height))
        
        return distortions
    
    def create_neutral_obstacles(self, world_width, world_height):
        """Crée des obstacles neutres standard"""
        obstacles = []
        
        # Pattern standard avec quelques piliers
        pillar_size = 60
        
        # 4 piliers aux quarts
        quarter_x = world_width // 4
        quarter_y = world_height // 4
        three_quarter_x = 3 * world_width // 4
        three_quarter_y = 3 * world_height // 4
        
        positions = [
            (quarter_x, quarter_y),
            (three_quarter_x, quarter_y),
            (quarter_x, three_quarter_y),
            (three_quarter_x, three_quarter_y),
        ]
        
        for x, y in positions:
            obstacles.append(pygame.Rect(x - pillar_size//2, y - pillar_size//2, 
                                       pillar_size, pillar_size))
        
        # Quelques murs longs
        wall_length = 200
        wall_width = 20
        
        obstacles.extend([
            pygame.Rect(world_width // 6, world_height // 3, wall_length, wall_width),
            pygame.Rect(2 * world_width // 3, 2 * world_height // 3, wall_length, wall_width),
            pygame.Rect(2 * world_width // 3, world_height // 6, wall_width, wall_length),
            pygame.Rect(world_width // 3, 2 * world_height // 3, wall_width, wall_length),
        ])
        
        return obstacles
    
    def get_spawn_positions(self, environment, world_width, world_height):
        """Retourne les positions de spawn selon l'environnement"""
        if environment == "imperial_shrine":
            # Spawn aux portes d'entrée
            return [
                (world_width // 2, 100),  # Entrée principale
                (100, world_height // 2),  # Entrée latérale gauche
                (world_width - 100, world_height // 2),  # Entrée latérale droite
                (world_width // 4, world_height - 100),  # Sortie gauche
                (3 * world_width // 4, world_height - 100),  # Sortie droite
            ]
        elif environment == "chaos_temple":
            # Spawn chaotique autour du centre
            center_x = world_width // 2
            center_y = world_height // 2
            spawn_positions = []
            
            for i in range(8):
                angle = (i / 8) * 2 * math.pi
                distance = 300
                x = center_x + math.cos(angle) * distance
                y = center_y + math.sin(angle) * distance
                spawn_positions.append((int(x), int(y)))
            
            return spawn_positions
        else:
            # Spawn standard optimisé
            return [
                (world_width // 6, world_height // 6),
                (5 * world_width // 6, world_height // 6),
                (world_width // 6, 5 * world_height // 6),
                (5 * world_width // 6, 5 * world_height // 6),
                (world_width // 2, 80),
                (world_width // 2, world_height - 80),
                (80, world_height // 2),
                (world_width - 80, world_height // 2),
            ]

class LevelManager:
    """Gestionnaire de niveau intégré"""
    
    def __init__(self):
        self.world_generator = SimpleWorldGenerator()
        self.current_walls = []
        self.current_spawn_positions = []
        self.current_environment = "neutral"
        
    def generate_level(self, wave_number, morality_system):
        """Génère un niveau pour la vague donnée"""
        
        # Déterminer l'environnement
        self.current_environment = self.world_generator.determine_environment(morality_system)
        
        # Créer le layout approprié
        if wave_number in [5, 15, 20]:  # Boss waves
            raw_walls = self.world_generator.create_boss_arena(WORLD_WIDTH, WORLD_HEIGHT)
            # Boss spawn au centre
            self.current_spawn_positions = [(WORLD_WIDTH // 2, WORLD_HEIGHT // 2)]
        else:
            raw_walls = self.world_generator.create_standard_layout(
                WORLD_WIDTH, WORLD_HEIGHT, self.current_environment
            )
            self.current_spawn_positions = self.world_generator.get_spawn_positions(
                self.current_environment, WORLD_WIDTH, WORLD_HEIGHT
            )
        
        # Convertir les pygame.Rect en objets avec attribut .rect pour compatibilité
        self.current_walls = []
        for wall_rect in raw_walls:
            wall_obj = WallWrapper(wall_rect)
            self.current_walls.append(wall_obj)
        
        return self.current_walls
    
    def get_environment_info(self):
        """Retourne les informations sur l'environnement actuel"""
        env_descriptions = {
            "imperial_shrine": "⛪ Sanctuaire Impérial - La foi vous guide",
            "chaos_temple": "🔥 Temple du Chaos - La corruption règne",
            "neutral_ruins": "🏚️ Ruines neutres - Terrain d'épreuve",
            "hive_city": "🏙️ Cité-ruche - Dédale urbain",
            "battlefield": "⚔️ Champ de bataille - Combat ouvert",
            "daemon_realm": "👹 Royaume démoniaque - Réalité distordue"
        }
        return env_descriptions.get(self.current_environment, "Environnement inconnu")
    
    def get_wall_color(self):
        """Retourne la couleur des murs selon l'environnement"""
        colors = {
            "imperial_shrine": (150, 140, 120),  # Doré
            "chaos_temple": (120, 80, 80),      # Rouge sombre
            "daemon_realm": (100, 60, 120),     # Pourpre
            "hive_city": (100, 100, 120),       # Bleu-gris
            "battlefield": (120, 100, 80),      # Terre
            "neutral_ruins": (128, 128, 128)    # Gris standard
        }
        return colors.get(self.current_environment, (128, 128, 128))

class EnvironmentEffects:
    """Effets visuels d'environnement"""
    
    def __init__(self):
        self.particle_timer = 0
        self.particles = []
    
    def update(self, environment):
        """Met à jour les effets"""
        self.particle_timer += 1
        
        # Nettoyer les anciennes particules
        self.particles = [p for p in self.particles if p['life'] > 0]
        
        # Limiter le nombre de particules
        if len(self.particles) > 50:
            self.particles = self.particles[-50:]
        
        # Générer nouvelles particules
        if self.particle_timer % 15 == 0:
            if environment == "imperial_shrine":
                self.add_holy_particle()
            elif environment == "chaos_temple":
                self.add_chaos_particle()
            elif environment == "daemon_realm":
                self.add_warp_particle()
        
        # Mettre à jour les particules
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
    
    def add_holy_particle(self):
        """Ajoute une particule sacrée"""
        particle = {
            'x': random.randint(0, WORLD_WIDTH),
            'y': random.randint(0, WORLD_HEIGHT),
            'vx': random.uniform(-0.5, 0.5),
            'vy': random.uniform(-1, -0.3),
            'life': 120,
            'color': (255, 255, 200),
            'size': random.randint(2, 4)
        }
        self.particles.append(particle)
    
    def add_chaos_particle(self):
        """Ajoute une particule chaotique"""
        particle = {
            'x': random.randint(0, WORLD_WIDTH),
            'y': random.randint(0, WORLD_HEIGHT),
            'vx': random.uniform(-2, 2),
            'vy': random.uniform(-2, 2),
            'life': 80,
            'color': (random.randint(150, 255), 0, random.randint(150, 255)),
            'size': random.randint(3, 6)
        }
        self.particles.append(particle)
    
    def add_warp_particle(self):
        """Ajoute une particule warp"""
        particle = {
            'x': random.randint(0, WORLD_WIDTH),
            'y': random.randint(0, WORLD_HEIGHT),
            'vx': random.uniform(-3, 3),
            'vy': random.uniform(-3, 3),
            'life': 60,
            'color': (random.randint(100, 200), random.randint(0, 100), random.randint(100, 255)),
            'size': random.randint(4, 8)
        }
        self.particles.append(particle)
    
    def draw(self, screen, camera):
        """Dessine les effets"""
        for particle in self.particles:
            screen_x, screen_y = camera.apply_pos(particle['x'], particle['y'])
            
            # Vérifier si visible
            if -50 <= screen_x <= SCREEN_WIDTH + 50 and -50 <= screen_y <= SCREEN_HEIGHT + 50:
                alpha = int(255 * (particle['life'] / 120))
                alpha = max(0, min(255, alpha))
                
                size = particle['size']
                particle_surface = pygame.Surface((size * 2, size * 2))
                particle_surface.set_alpha(alpha)
                particle_surface.fill(particle['color'])
                screen.blit(particle_surface, (screen_x - size, screen_y - size))

def spawn_enemies_optimized(wave_number, level_manager, player):
    """Génère des ennemis avec positions optimisées"""
    enemies = []
    
    # Récupérer les positions de spawn
    spawn_positions = level_manager.current_spawn_positions.copy()
    
    # Les murs sont déjà wrappés par le LevelManager
    walls = level_manager.current_walls
    
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
    
    elif wave_number > 20:
        boss_chance = min(0.3, (wave_number - 20) * 0.1)
        if random.random() < boss_chance:
            boss_type = random.choice([ChaosSorcererBoss, InquisitorLordBoss])
            print(f"🎯 BOSS SURPRISE ! {boss_type.__name__} apparaît !")
            boss_x, boss_y = WORLD_WIDTH // 2, WORLD_HEIGHT // 2
            enemies.append(boss_type(boss_x, boss_y))
    
    # === ENNEMIS NORMAUX ===
    basic_count = min(3 + wave_number, 8)
    shooter_count = min(wave_number // 2, 4)
    fast_count = min(wave_number // 3, 3)
    cultist_count = min(max(0, wave_number - 2), 4)
    marine_count = min(max(0, wave_number - 4), 3)
    daemon_count = min(max(0, wave_number - 6), 3)
    
    if wave_number > 10:
        cultist_count += 1
        marine_count += 1
        daemon_count += 1
    
    # Spawn avec répartition optimisée
    enemy_types = [
        (BasicEnemy, basic_count, 24, 24, 150),
        (ShooterEnemy, shooter_count, 20, 20, 200),
        (FastEnemy, fast_count, 16, 16, 180),
        (CultistEnemy, cultist_count, 22, 22, 200),
        (RenegadeMarineEnemy, marine_count, 30, 30, 250),
        (DaemonEnemy, daemon_count, 20, 20, 300)
    ]
    
    spawn_index = 0
    for enemy_class, count, width, height, min_distance in enemy_types:
        for _ in range(count):
            if spawn_index < len(spawn_positions):
                # Utiliser position prédéfinie
                x, y = spawn_positions[spawn_index]
                
                # Vérifier que la position est valide
                if PathfindingHelper.is_position_free(x, y, width, height, walls):
                    enemies.append(enemy_class(x, y))
                    spawn_index += 1
                else:
                    # Position bloquée, utiliser le pathfinding
                    x, y = PathfindingHelper.find_free_spawn_position(
                        WORLD_WIDTH, WORLD_HEIGHT, width, height, 
                        walls, player, min_distance
                    )
                    enemies.append(enemy_class(x, y))
            else:
                # Plus de positions prédéfinies, utiliser le pathfinding
                x, y = PathfindingHelper.find_free_spawn_position(
                    WORLD_WIDTH, WORLD_HEIGHT, width, height, 
                    walls, player, min_distance
                )
                enemies.append(enemy_class(x, y))
    
    return enemies

def main():
    # Initialiser Pygame
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Roguelike WH40K - Avec Audio")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    
    # === INITIALISER LE SYSTÈME AUDIO ===
    sound_manager = create_sound_manager()
    print(f"🔊 Audio {'activé' if sound_manager.is_audio_enabled() else 'désactivé'}")
    
    # Créer le joueur au centre du monde
    player = Player(WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
    
    # Créer la caméra et la centrer immédiatement sur le joueur
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT)
    camera.x = player.x + player.width // 2 - SCREEN_WIDTH // 2
    camera.y = player.y + player.height // 2 - SCREEN_HEIGHT // 2
    camera.target_x = camera.x
    camera.target_y = camera.y
    
    # Gestionnaires
    level_manager = LevelManager()
    environment_effects = EnvironmentEffects()
    item_manager = ItemManager()
    morality_system = MoralitySystem()
    exp_system = ExperienceSystem()
    ui_manager = UIManager()
    morality_effects = MoralityEffects()
    
    # Listes de jeu
    player_bullets = []
    enemy_bullets = []
    enemies = []
    
    # Système de vagues
    wave_number = 1
    enemies_killed = 0
    wave_clear = False
    
    # Générer le niveau initial
    walls = level_manager.generate_level(wave_number, morality_system)
    
    # Spawn première vague
    enemies = spawn_enemies_optimized(wave_number, level_manager, player)
    sound_manager.on_wave_start(wave_number)
    
    # Game Over
    game_over = False
    
    # Variables pour le système audio
    last_morality_faith = morality_system.faith
    last_morality_corruption = morality_system.corruption
    
    # Boucle principale
    running = True
    while running:
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Gérer les inputs du système d'expérience en priorité
            if exp_system.handle_input(event):
                if not exp_system.is_leveling_up and exp_system.level_up_choices:
                    chosen_item = exp_system.level_up_choices[exp_system.selected_choice]
                    item_manager.apply_item_directly(player, chosen_item, morality_system)
                    exp_system.level_up_choices = []
                    sound_manager.on_item_pickup()  # Son de ramassage d'objet
                continue
            
            # UI audio
            if ui_manager.handle_input(event):
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Son de pause
                        sound_manager.on_menu_select()
                    elif event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_w, pygame.K_s]:
                        # Son de navigation
                        sound_manager.on_menu_navigate()
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        # Son de sélection
                        sound_manager.on_menu_select()
                continue
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_over:
                    # Restart du jeu
                    player = Player(WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
                    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT)
                    camera.x = player.x + player.width // 2 - SCREEN_WIDTH // 2
                    camera.y = player.y + player.height // 2 - SCREEN_HEIGHT // 2
                    camera.target_x = camera.x
                    camera.target_y = camera.y
                    player_bullets = []
                    enemy_bullets = []
                    wave_number = 1
                    enemies_killed = 0
                    game_over = False
                    item_manager = ItemManager()
                    morality_system = MoralitySystem()
                    exp_system = ExperienceSystem()
                    level_manager = LevelManager()
                    walls = level_manager.generate_level(wave_number, morality_system)
                    enemies = spawn_enemies_optimized(wave_number, level_manager, player)
                    sound_manager.on_wave_start(wave_number)
                    # Reset morality tracking
                    last_morality_faith = morality_system.faith
                    last_morality_corruption = morality_system.corruption
        
        # Vérifier si le jeu doit être en pause
        game_paused = ui_manager.should_pause_game(exp_system)
        
        if not game_over and not game_paused:
            # Mise à jour du joueur
            player.update(walls, morality_system)
            
            # Mise à jour de la caméra
            camera.update(player)
            
            # Mise à jour des effets environnementaux
            environment_effects.update(level_manager.current_environment)
            
            # Mise à jour du système de moralité et détection des changements pour l'audio
            old_faith = morality_system.faith
            old_corruption = morality_system.corruption
            morality_system.update()
            
            # Sons de changement de moralité
            faith_change = morality_system.faith - old_faith
            corruption_change = morality_system.corruption - old_corruption
            
            if abs(faith_change) > 0.5:
                sound_manager.on_morality_change("faith", abs(faith_change))
            if abs(corruption_change) > 0.5:
                sound_manager.on_morality_change("corruption", abs(corruption_change))
            
            # Appliquer les effets de moralité au joueur
            morality_effects.apply_morality_effects(player, morality_system)
            
            # Mise à jour du système d'expérience
            exp_system.update()
            
            # Générer choix de level-up si nécessaire
            if exp_system.is_leveling_up and not exp_system.level_up_choices:
                exp_system.generate_level_up_choices(morality_system, item_manager)
                sound_manager.on_level_up()  # Son de level up
            
            # Tir automatique du joueur
            keys = pygame.key.get_pressed()
            mouse_buttons = pygame.mouse.get_pressed()
            
            if keys[pygame.K_SPACE] or mouse_buttons[0]:
                mouse_pos = pygame.mouse.get_pos()
                world_mouse_pos = camera.screen_to_world(mouse_pos[0], mouse_pos[1])
                bullets = player.try_shoot(world_mouse_pos, morality_system)
                if bullets:
                    player_bullets.extend(bullets)
                    # Son de tir du joueur
                    sound_manager.on_player_shoot((player.x, player.y), morality_system)
            
            # Mise à jour des ennemis et gestion des boss
            for enemy in enemies:
                enemy.update(player, walls, enemies)
                
                # Gestion spécifique selon le type d'ennemi
                if isinstance(enemy, ShooterEnemy):
                    bullet = enemy.try_shoot(player)
                    if bullet:
                        enemy_bullets.append(bullet)
                        # Son de tir d'ennemi
                        sound_manager.on_enemy_shoot((enemy.x, enemy.y), (player.x, player.y))
                
                elif isinstance(enemy, CultistEnemy):
                    if enemy.try_summon():
                        daemon_x = enemy.x + random.randint(-50, 50)
                        daemon_y = enemy.y + random.randint(-50, 50)
                        summoned_daemon = DaemonEnemy(daemon_x, daemon_y, is_summoned=True)
                        enemies.append(summoned_daemon)
                        print("Un démon a été invoqué !")
                
                elif isinstance(enemy, DaemonEnemy):
                    if enemy.try_psychic_attack(player):
                        dx = player.x - enemy.x
                        dy = player.y - enemy.y
                        length = math.sqrt(dx*dx + dy*dy)
                        if length > 0:
                            dx /= length
                            dy /= length
                        
                        psychic_bullet = Bullet(
                            enemy.x + enemy.width // 2, 
                            enemy.y + enemy.height // 2,
                            dx, dy, 
                            is_player_bullet=False, 
                            damage=8
                        )
                        psychic_bullet.color = (150, 0, 150)
                        enemy_bullets.append(psychic_bullet)
                        sound_manager.on_enemy_shoot((enemy.x, enemy.y), (player.x, player.y))
                
                # === GESTION DES BOSS ===
                elif isinstance(enemy, ChaosSorcererBoss):
                    if random.random() < 0.02:
                        if enemy.try_teleport():
                            sound_manager.on_boss_ability("daemon_teleport", (enemy.x, enemy.y), (player.x, player.y))
                    
                    if enemy.try_summon_daemon():
                        for _ in range(2):
                            daemon_x = enemy.x + random.randint(-80, 80)
                            daemon_y = enemy.y + random.randint(-80, 80)
                            summoned_daemon = DaemonEnemy(daemon_x, daemon_y, is_summoned=True)
                            enemies.append(summoned_daemon)
                        print("🔥 Le Sorcier invoque des démons !")
                    
                    if enemy.try_area_attack(player):
                        print("⚠️ ATTAQUE DE ZONE IMMINENTE !")
                    
                    if enemy.handle_area_cast():
                        area_radius = 120
                        sorcerer_center_x = enemy.x + enemy.width // 2
                        sorcerer_center_y = enemy.y + enemy.height // 2
                        player_center_x = player.x + player.width // 2
                        player_center_y = player.y + player.height // 2
                        
                        distance_to_player = math.sqrt(
                            (player_center_x - sorcerer_center_x)**2 + 
                            (player_center_y - sorcerer_center_y)**2
                        )
                        
                        if distance_to_player <= area_radius:
                            area_damage = 25
                            if player.take_damage(area_damage):
                                game_over = True
                            else:
                                morality_system.process_damage_taken(area_damage)
                                sound_manager.on_player_damage()
                            print("💥 DÉFLAGRATION CHAOTIQUE !")
                        
                        # Son d'explosion de zone
                        sound_manager.on_boss_ability("sorcerer_area", (sorcerer_center_x, sorcerer_center_y), (player.x, player.y))
                    
                    if enemy.try_projectile_barrage(player):
                        for i in range(8):
                            angle = (i / 8) * 2 * math.pi
                            dx = math.cos(angle)
                            dy = math.sin(angle)
                            
                            chaos_bullet = Bullet(
                                enemy.x + enemy.width // 2,
                                enemy.y + enemy.height // 2,
                                dx, dy,
                                is_player_bullet=False,
                                damage=12
                            )
                            chaos_bullet.color = (255, 0, 255)
                            enemy_bullets.append(chaos_bullet)
                        print("🌀 BARRAGE CHAOTIQUE !")
                
                elif isinstance(enemy, InquisitorLordBoss):
                    if random.random() < 0.015:
                        if enemy.try_purification():
                            sound_manager.on_boss_ability("inquisitor_purification", (enemy.x, enemy.y), (player.x, player.y))
                    
                    if enemy.handle_purification():
                        purif_radius = 150
                        inquisitor_center_x = enemy.x + enemy.width // 2
                        inquisitor_center_y = enemy.y + enemy.height // 2
                        player_center_x = player.x + player.width // 2
                        player_center_y = player.y + player.height // 2
                        
                        distance_to_player = math.sqrt(
                            (player_center_x - inquisitor_center_x)**2 + 
                            (player_center_y - inquisitor_center_y)**2
                        )
                        
                        if distance_to_player <= purif_radius:
                            purif_damage = 30
                            if player.take_damage(purif_damage):
                                game_over = True
                            else:
                                morality_system.process_damage_taken(purif_damage)
                                sound_manager.on_player_damage()
                            print("⚡ PURIFICATION IMPÉRIALE !")
                    
                    if enemy.try_blessed_shots(player):
                        for i in range(3):
                            angle_offset = (i - 1) * 0.3
                            dx = player.x - enemy.x
                            dy = player.y - enemy.y
                            length = math.sqrt(dx*dx + dy*dy)
                            if length > 0:
                                dx /= length
                                dy /= length
                            
                            final_dx = dx * math.cos(angle_offset) - dy * math.sin(angle_offset)
                            final_dy = dx * math.sin(angle_offset) + dy * math.cos(angle_offset)
                            
                            blessed_bullet = Bullet(
                                enemy.x + enemy.width // 2,
                                enemy.y + enemy.height // 2,
                                final_dx, final_dy,
                                is_player_bullet=False,
                                damage=15
                            )
                            blessed_bullet.color = (255, 255, 150)
                            enemy_bullets.append(blessed_bullet)
                        sound_manager.on_enemy_shoot((enemy.x, enemy.y), (player.x, player.y))
                    
                    if enemy.health < enemy.max_health * 0.4 and random.random() < 0.01:
                        enemy.try_activate_shield()
                
                elif isinstance(enemy, DaemonPrinceBoss):
                    if random.random() < 0.025:
                        if enemy.try_chaos_teleport():
                            sound_manager.on_boss_ability("daemon_teleport", (enemy.x, enemy.y), (player.x, player.y))
                    
                    if random.random() < 0.008:
                        if enemy.try_warp_storm():
                            sound_manager.on_boss_ability("daemon_warp_storm", (enemy.x, enemy.y), (player.x, player.y))
                    
                    if enemy.handle_warp_storm():
                        storm_radius = 200
                        prince_center_x = enemy.x + enemy.width // 2
                        prince_center_y = enemy.y + enemy.height // 2
                        player_center_x = player.x + player.width // 2
                        player_center_y = player.y + player.height // 2
                        
                        distance_to_player = math.sqrt(
                            (player_center_x - prince_center_x)**2 + 
                            (player_center_y - prince_center_y)**2
                        )
                        
                        if distance_to_player <= storm_radius:
                            storm_damage = 40
                            if player.take_damage(storm_damage):
                                game_over = True
                            else:
                                morality_system.process_damage_taken(storm_damage)
                                sound_manager.on_player_damage()
                            print("🌩️ TEMPÊTE WARP DÉVASTATRICE !")
                    
                    if enemy.try_corruption_wave():
                        for i in range(12):
                            angle = (i / 12) * 2 * math.pi + enemy.animation_timer * 0.1
                            dx = math.cos(angle)
                            dy = math.sin(angle)
                            
                            corruption_bullet = Bullet(
                                enemy.x + enemy.width // 2,
                                enemy.y + enemy.height // 2,
                                dx, dy,
                                is_player_bullet=False,
                                damage=18
                            )
                            corruption_bullet.color = (150, 0, 150)
                            enemy_bullets.append(corruption_bullet)
                        print("🌀 VAGUE DE CORRUPTION !")
                        sound_manager.on_enemy_shoot((enemy.x, enemy.y), (player.x, player.y))
                    
                    if enemy.try_mass_summon():
                        summon_count = 3 if enemy.chaos_form == 1 else 5
                        for _ in range(summon_count):
                            daemon_x = enemy.x + random.randint(-100, 100)
                            daemon_y = enemy.y + random.randint(-100, 100)
                            summoned_daemon = DaemonEnemy(daemon_x, daemon_y, is_summoned=True)
                            enemies.append(summoned_daemon)
                            enemy.total_summons += 1
                        print(f"💀 INVOCATION MASSIVE ! {summon_count} démons apparaissent !")
            
            # Mise à jour des projectiles du joueur
            clean_bullets = []
            for bullet in player_bullets:
                if hasattr(bullet, 'update'):
                    if bullet.update(walls, WORLD_WIDTH, WORLD_HEIGHT, enemies):
                        clean_bullets.append(bullet)
            player_bullets = clean_bullets
            
            # Mise à jour des projectiles ennemis
            enemy_bullets = [bullet for bullet in enemy_bullets 
                           if bullet.update(walls, WORLD_WIDTH, WORLD_HEIGHT)]
            
            # Mise à jour des objets
            item_manager.update()
            item_manager.check_pickup(player, morality_system)
            
            # Mise à jour du système audio
            sound_manager.update()

            # ===== GESTION DES COLLISIONS =====
            enemies_to_remove = []
            bullets_to_remove = []
            
            # Collisions projectiles joueur vs ennemis
            for bullet in player_bullets:
                if bullet in bullets_to_remove:
                    continue
                
                # Initialiser la liste des ennemis touchés si elle n'existe pas
                if not hasattr(bullet, 'hit_enemies'):
                    bullet.hit_enemies = set()
                    
                for enemy in enemies:
                    if enemy in enemies_to_remove:
                        continue
                    
                    # Vérifier si ce projectile a déjà touché cet ennemi
                    if id(enemy) in bullet.hit_enemies:
                        continue
                        
                    if bullet.rect.colliderect(enemy.rect):
                        # Marquer cet ennemi comme touché par ce projectile
                        bullet.hit_enemies.add(id(enemy))
                        
                        # Son d'impact
                        sound_manager.on_bullet_hit((enemy.x, enemy.y), (player.x, player.y))
                        
                        if enemy.take_damage(bullet.damage):
                            # Gestion des événements spéciaux à la mort des boss
                            if isinstance(enemy, ChaosSorcererBoss):
                                print("🔥 Le Sorcier du Chaos est vaincu ! +100 XP")
                                exp_system.add_experience(100)
                                morality_system.add_faith(15, "Destruction d'un Sorcier du Chaos")
                                sound_manager.on_boss_death()
                            
                            elif isinstance(enemy, InquisitorLordBoss):
                                print("⚡ Le Seigneur Inquisiteur est vaincu ! +120 XP") 
                                exp_system.add_experience(120)
                                morality_system.add_corruption(10, "Meurtre d'un Inquisiteur")
                                sound_manager.on_boss_death()
                            
                            elif isinstance(enemy, DaemonPrinceBoss):
                                print("💀 LE PRINCE DAEMON EST VAINCU ! VICTOIRE ÉPIQUE ! +200 XP")
                                exp_system.add_experience(200)
                                morality_system.add_faith(25, "Bannissement d'un Prince Daemon")
                                sound_manager.on_boss_death()
                            
                            else:
                                morality_system.process_kill(type(enemy).__name__)
                                exp_rewards = {
                                    "BasicEnemy": 10,
                                    "ShooterEnemy": 15,
                                    "FastEnemy": 12,
                                    "CultistEnemy": 20,
                                    "RenegadeMarineEnemy": 35,
                                    "DaemonEnemy": 25
                                }
                                exp_reward = exp_rewards.get(type(enemy).__name__, 10)
                                exp_system.add_experience(exp_reward)
                                
                                # Son de mort d'ennemi
                                sound_manager.on_enemy_death((enemy.x, enemy.y), (player.x, player.y), type(enemy).__name__)
                            
                            # Pour tous les boss - nettoyer leurs invocations
                            if isinstance(enemy, (ChaosSorcererBoss, InquisitorLordBoss, DaemonPrinceBoss)):
                                demons_to_remove = []
                                for other_enemy in enemies:
                                    if (isinstance(other_enemy, DaemonEnemy) and 
                                        hasattr(other_enemy, 'is_summoned') and 
                                        other_enemy.is_summoned):
                                        demons_to_remove.append(other_enemy)
                                
                                for demon in demons_to_remove:
                                    if demon in enemies and demon not in enemies_to_remove:
                                        enemies_to_remove.append(demon)
                                
                                print("Les invocations du boss disparaissent...")
                            
                            if exp_system.is_leveling_up and not exp_system.level_up_choices:
                                exp_system.generate_level_up_choices(morality_system, item_manager)
                            
                            enemies_to_remove.append(enemy)
                            enemies_killed += 1
                        
                        # Si ce n'est pas un projectile perforant, le détruire après le premier impact
                        if not bullet.piercing:
                            bullets_to_remove.append(bullet)
                            break
            
            # Supprimer les ennemis et projectiles marqués
            for enemy in enemies_to_remove:
                if enemy in enemies:
                    enemies.remove(enemy)

            for bullet in bullets_to_remove:
                if bullet in player_bullets:
                    player_bullets.remove(bullet)
            
            # Collisions projectiles ennemis vs joueur
            for bullet in enemy_bullets[:]:
                if bullet.rect.colliderect(player.rect):
                    damage_taken = bullet.damage
                    if player.take_damage(damage_taken):
                        game_over = True
                    else:
                        morality_system.process_damage_taken(damage_taken)
                        sound_manager.on_player_damage()
                    enemy_bullets.remove(bullet)
            
            # Collisions ennemis vs joueur (contact direct)
            for enemy in enemies:
                if enemy.rect.colliderect(player.rect):
                    contact_damage = 5
                    
                    if isinstance(enemy, RenegadeMarineEnemy) and enemy.is_charging:
                        contact_damage = 20
                        enemy.is_charging = False
                        print("Charge du Marine Renégat !")
                    
                    elif isinstance(enemy, ChaosSorcererBoss):
                        contact_damage = 15
                        print("💥 Contact avec le Sorcier du Chaos !")
                    
                    elif isinstance(enemy, InquisitorLordBoss):
                        contact_damage = 18
                        if enemy.is_charging:
                            contact_damage = 25
                            enemy.is_charging = False
                            print("⚡ CHARGE SAINTE !")
                        else:
                            print("⚡ Contact avec l'Inquisiteur !")
                    
                    elif isinstance(enemy, DaemonPrinceBoss):
                        contact_damage = 25
                        print("💀 CONTACT AVEC LE PRINCE DAEMON !")
                        if random.random() < 0.3:
                            morality_system.add_corruption(3, "Contact avec un Prince Daemon")
                    
                    if player.take_damage(contact_damage):
                        game_over = True
                    else:
                        morality_system.process_damage_taken(contact_damage)
                        sound_manager.on_player_damage()
            
            # Vérifier si vague terminée
            if len(enemies) == 0:
                if wave_number == 10:
                    print("✅ Sorcier du Chaos vaincu ! La vague 11 vous attend...")
                elif wave_number == 15:
                    print("✅ Seigneur Inquisiteur vaincu ! Préparez-vous pour le boss final...")
                elif wave_number == 20:
                    print("🎉 PRINCE DAEMON VAINCU ! VOUS AVEZ GAGNÉ ! Mais les vagues continuent...")
                
                sound_manager.on_wave_complete()
                wave_number += 1
                
                # Régénérer le niveau pour certaines vagues importantes
                regenerate_level = (
                    wave_number in [5, 15, 20] or  # Boss waves
                    wave_number % 10 == 1  # Après boss
                )
                
                if regenerate_level:
                    print(f"🔄 Régénération du niveau pour la vague {wave_number}")
                    walls = level_manager.generate_level(wave_number, morality_system)
                
                enemies = spawn_enemies_optimized(wave_number, level_manager, player)
                
                # Sons de boss spawn
                if wave_number == 5:
                    sound_manager.on_boss_spawn("chaos")
                elif wave_number == 15:
                    sound_manager.on_boss_spawn("imperial")
                elif wave_number == 20:
                    sound_manager.on_boss_spawn("daemon")
                else:
                    sound_manager.on_wave_start(wave_number)
                
                wave_clear = True
        
        # Mise à jour de l'UI
        ui_manager.update()
        
        # Rendu
        screen.fill(BLACK)
        
        if not game_over:
            # Dessiner les effets d'arrière-plan
            environment_effects.draw(screen, camera)
            
            # Dessiner les murs (optimisé pour la visibilité)
            wall_color = level_manager.get_wall_color()
            visible_walls = 0
            for wall in walls:
                # Récupérer le rectangle du mur
                wall_rect = wall.rect
                wall_screen_rect = pygame.Rect(
                    wall_rect.x - camera.x, wall_rect.y - camera.y,
                    wall_rect.width, wall_rect.height
                )
                
                # Culling basique - ne dessiner que si visible
                if (wall_screen_rect.right >= 0 and wall_screen_rect.x <= SCREEN_WIDTH and
                    wall_screen_rect.bottom >= 0 and wall_screen_rect.y <= SCREEN_HEIGHT):
                    pygame.draw.rect(screen, wall_color, wall_screen_rect)
                    visible_walls += 1
            
            # Dessiner le joueur
            player_screen_rect = camera.apply(player)
            old_x, old_y = player.x, player.y
            player.x, player.y = player_screen_rect.x, player_screen_rect.y
            player.draw(screen)
            player.x, player.y = old_x, old_y
            
            # Dessiner les ennemis (seulement ceux visibles)
            visible_enemies = 0
            for enemy in enemies:
                if camera.is_visible(enemy):
                    enemy_screen_rect = camera.apply(enemy)
                    old_x, old_y = enemy.x, enemy.y
                    enemy.x, enemy.y = enemy_screen_rect.x, enemy_screen_rect.y
                    enemy.draw(screen)
                    enemy.x, enemy.y = old_x, old_y
                    visible_enemies += 1
            
            # Dessiner les objets au sol (seulement ceux visibles)
            for item in item_manager.items_on_ground:
                if camera.is_visible(item):
                    item_screen_pos = camera.apply_pos(item.x, item.y)
                    old_x, old_y = item.x, item.y
                    item.x, item.y = item_screen_pos[0], item_screen_pos[1]
                    item.draw(screen)
                    item.x, item.y = old_x, old_y
            
            # Dessiner les projectiles (seulement ceux visibles)
            for bullet in player_bullets:
                bullet_screen_pos = camera.apply_pos(bullet.x, bullet.y)
                if (0 <= bullet_screen_pos[0] <= SCREEN_WIDTH and 
                    0 <= bullet_screen_pos[1] <= SCREEN_HEIGHT):
                    old_x, old_y = bullet.x, bullet.y
                    bullet.x, bullet.y = bullet_screen_pos[0], bullet_screen_pos[1]
                    bullet.draw(screen)
                    bullet.x, bullet.y = old_x, old_y
            
            for bullet in enemy_bullets:
                bullet_screen_pos = camera.apply_pos(bullet.x, bullet.y)
                if (0 <= bullet_screen_pos[0] <= SCREEN_WIDTH and 
                    0 <= bullet_screen_pos[1] <= SCREEN_HEIGHT):
                    old_x, old_y = bullet.x, bullet.y
                    bullet.x, bullet.y = bullet_screen_pos[0], bullet_screen_pos[1]
                    bullet.draw(screen)
                    bullet.x, bullet.y = old_x, old_y
            
            # Effets visuels de moralité
            morality_effects.draw_morality_effects(screen, camera, player, morality_system)
            
            # HUD minimal pendant le jeu
            ui_manager.draw_minimal_hud(screen, player, morality_system, exp_system)
            
            # Informations sur l'environnement
            env_info = level_manager.get_environment_info()
            env_font = pygame.font.Font(None, 24)
            env_text = env_font.render(env_info, True, WHITE)
            screen.blit(env_text, (10, SCREEN_HEIGHT - 140))
            
            # Instructions et informations (avec statut audio)
            audio_status = "🔊 Audio" if sound_manager.is_audio_enabled() else "🔇 Silent"
            instructions = [
                "WASD/Flèches: Déplacement | Espace/Clic: Tir automatique",
                "🌍 Environnement adaptatif selon votre moralité",
                "🔥 BOSS: Vague 5, 15, 20 | Arènes dédiées !",
                f"Vague {wave_number} - {len(enemies)} ennemis - {audio_status}"
            ]
            for i, instruction in enumerate(instructions):
                text = pygame.font.Font(None, 18).render(instruction, True, WHITE)
                screen.blit(text, (10, SCREEN_HEIGHT - 120 + i * 18))
        
        else:
            # Écran Game Over
            ui_manager.draw_minimal_hud(screen, player, morality_system, exp_system)
            
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(150)
            overlay.fill((50, 0, 0))
            screen.blit(overlay, (0, 0))
            
            game_over_text = font.render("GAME OVER", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 50))
            
            restart_text = font.render("Appuie sur R pour recommencer", True, WHITE)
            screen.blit(restart_text, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2))
            
            final_stats = font.render(f"Vague atteinte: {wave_number} - Ennemis tués: {enemies_killed}", True, WHITE)
            screen.blit(final_stats, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 + 50))
            
            env_final = font.render(f"Environnement final: {level_manager.get_environment_info()}", True, WHITE)
            screen.blit(env_final, (SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 + 80))
        
        # Écran de level-up par-dessus tout
        if exp_system.is_leveling_up:
            if exp_system.level_up_choices:
                ui_manager.draw_level_up_notification(screen)
                exp_system.draw_level_up_screen(screen, morality_system, item_manager)
            else:
                font = pygame.font.Font(None, 48)
                loading_text = font.render("Génération des choix...", True, (255, 255, 255))
                loading_rect = loading_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                screen.blit(loading_text, loading_rect)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":
    main()