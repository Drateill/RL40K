import pygame
import random
from player import Player
from enemies import BasicEnemy, ShooterEnemy, FastEnemy, CultistEnemy, RenegadeMarineEnemy, DaemonEnemy, ChaosSorcererBoss, InquisitorLordBoss, DaemonPrinceBoss
from wall import create_border_walls, create_interior_walls
from items import ItemManager
from camera import Camera
from pathfinding import PathfindingHelper
from morality_system import MoralitySystem
from experience_system import ExperienceSystem
from ui_manager import UIManager
from morality_effects import MoralityEffects
from bullet import Bullet
from environment_system import EnvironmentSystem, EnvironmentType
from environment_renderer import EnvironmentRenderer
from wall import create_environment_walls, get_environment_spawn_position
import math

# Initialisation
pygame.init()

# Constantes
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
WORLD_WIDTH = 2048   # Monde 2x plus grand
WORLD_HEIGHT = 1536  # Monde 2x plus grand
FPS = 60


# Couleurs
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

def spawn_enemies(wave_number, world_width, world_height, walls, player, environment_system):
    """Génère des ennemis selon le numéro de vague avec boss et adaptation environnement"""
    enemies = []
    
    # Récupérer les infos de l'environnement actuel
    env_info = environment_system.get_environment_info()
    movement_modifier = environment_system.get_movement_modifier()
    
    print(f"🌍 Spawn vague {wave_number} dans {env_info['name']}")
    
    # === BOSS WAVES ===
    if wave_number == 5:
        print("🔥 BOSS WAVE ! Un Sorcier du Chaos apparaît !")
        x, y = get_environment_spawn_position(world_width, world_height, 48, 48, walls, avoid_center=True)
        enemies.append(ChaosSorcererBoss(x, y))
        return enemies
    
    elif wave_number == 15:
        print("⚡ BOSS WAVE ! Un Seigneur Inquisiteur vous défie !")
        x, y = get_environment_spawn_position(world_width, world_height, 45, 45, walls, avoid_center=True)
        enemies.append(InquisitorLordBoss(x, y))
        return enemies
    
    elif wave_number == 20:
        print("💀 BOSS FINAL ! Un Prince Daemon émerge du Warp !")
        x, y = get_environment_spawn_position(world_width, world_height, 64, 64, walls, avoid_center=True)
        enemies.append(DaemonPrinceBoss(x, y))
        return enemies
    
    elif wave_number > 20:
        boss_chance = min(0.3, (wave_number - 20) * 0.1)
        if random.random() < boss_chance:
            boss_type = random.choice([ChaosSorcererBoss, InquisitorLordBoss])
            print(f"🎯 BOSS SURPRISE ! {boss_type.__name__} apparaît !")
            x, y = get_environment_spawn_position(world_width, world_height, 48, 48, walls, avoid_center=True)
            enemies.append(boss_type(x, y))
    
    # === ADAPTATION SELON L'ENVIRONNEMENT ===
    env_type = environment_system.current_environment
    
    # Nombre de base d'ennemis
    basic_count = min(3 + wave_number, 8)
    shooter_count = min(wave_number // 2, 4)
    fast_count = min(wave_number // 3, 3)
    cultist_count = min(max(0, wave_number - 2), 4)
    marine_count = min(max(0, wave_number - 4), 3)
    daemon_count = min(max(0, wave_number - 6), 3)
    
    # Modifications selon l'environnement
    if env_type == EnvironmentType.SHIP:
        # Vaisseau : Plus de Marines Renégats, moins de Démons
        marine_count += 2
        daemon_count = max(0, daemon_count - 1)
        
    elif env_type == EnvironmentType.TEMPLE:
        # Temple : Plus de Cultistes, équilibre foi/corruption
        cultist_count += 2
        
    elif env_type == EnvironmentType.FORGE:
        # Forge : Ennemis plus résistants mais moins nombreux
        basic_count = int(basic_count * 0.8)
        marine_count += 1
        
    elif env_type == EnvironmentType.CHAOS:
        # Chaos : Plus de Démons et Cultistes
        daemon_count += 2
        cultist_count += 2
        basic_count = int(basic_count * 0.7)  # Moins d'ennemis normaux
        
    elif env_type == EnvironmentType.DEATH_WORLD:
        # Monde Mort : Plus d'ennemis rapides et dangereux
        fast_count += 2
        basic_count += 1
    
    # Après vague 10, plus d'ennemis difficiles
    if wave_number > 10:
        cultist_count += 1
        marine_count += 1
        daemon_count += 1
    
    # Spawn des ennemis avec adaptation environnementale
    enemy_types = [
        (BasicEnemy, basic_count, 24, 24),
        (ShooterEnemy, shooter_count, 20, 20),
        (FastEnemy, fast_count, 16, 16),
        (CultistEnemy, cultist_count, 22, 22),
        (RenegadeMarineEnemy, marine_count, 30, 30),
        (DaemonEnemy, daemon_count, 20, 20)
    ]
    
    for enemy_class, count, width, height in enemy_types:
        for _ in range(count):
            x, y = get_environment_spawn_position(world_width, world_height, width, height, walls, avoid_center=True)
            enemy = enemy_class(x, y)
            
            # Appliquer les modificateurs d'environnement
            if hasattr(enemy, 'speed'):
                enemy.speed *= movement_modifier
            
            enemies.append(enemy)
    
    print(f"   {len(enemies)} ennemis générés (Modificateur vitesse: {movement_modifier:.1f}x)")
    return enemies

def main():
    # Initialiser Pygame
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Roguelike WH40K - Prototype avec Boss")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
 
    # Listes de jeu
    player_bullets = []
    enemy_bullets = []
    enemies = []
    
    # Gestionnaire d'objets
    item_manager = ItemManager()
    
    # Système de moralité
    morality_system = MoralitySystem()
    
    # Système d'expérience
    exp_system = ExperienceSystem()
    
    # Gestionnaire d'UI
    ui_manager = UIManager()
    
    # Effets de moralité
    morality_effects = MoralityEffects()
    
    # Système de vagues
    wave_number = 1
    enemies_killed = 0
    wave_clear = False
    

        # Système d'environnements
    environment_system = EnvironmentSystem()
    environment_renderer = EnvironmentRenderer(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # Générer l'environnement initial
    walls = create_environment_walls(WORLD_WIDTH, WORLD_HEIGHT, 1, morality_system, environment_system)


    # Position de spawn du joueur selon l'environnement
    player_spawn_x, player_spawn_y = get_environment_spawn_position(
        WORLD_WIDTH, WORLD_HEIGHT, 32, 32, walls, avoid_center=False
    )
    player = Player(player_spawn_x, player_spawn_y)
    
    # Créer la caméra et la centrer immédiatement sur le joueur
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT)
    camera.x = player.x + player.width // 2 - SCREEN_WIDTH // 2
    camera.y = player.y + player.height // 2 - SCREEN_HEIGHT // 2
    camera.target_x = camera.x
    camera.target_y = camera.y
    
    # Spawn première vague
    enemies = spawn_enemies(wave_number, WORLD_WIDTH, WORLD_HEIGHT, walls, player, environment_system)

    # Game Over
    game_over = False
    
    # Boucle principale
    running = True
    while running:
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Gérer les inputs du système d'expérience en priorité
            if exp_system.handle_input(event):
                # Si on confirme un choix, récupérer l'objet choisi
                if not exp_system.is_leveling_up and exp_system.level_up_choices:
                    # Le joueur vient de choisir, récupérer le choix
                    chosen_item = exp_system.level_up_choices[exp_system.selected_choice]
                    item_manager.apply_item_directly(player, chosen_item, morality_system)
                    exp_system.level_up_choices = []
                continue
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_over:
                    # Restart du jeu
                    walls = create_environment_walls(WORLD_WIDTH, WORLD_HEIGHT, 1, morality_system, environment_system)
                    player_spawn_x, player_spawn_y = get_environment_spawn_position(
                        WORLD_WIDTH, WORLD_HEIGHT, 32, 32, walls, avoid_center=False
                    )
                    player = Player(player_spawn_x, player_spawn_y)

                    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT)
                    camera.x = player.x + player.width // 2 - SCREEN_WIDTH // 2
                    camera.y = player.y + player.height // 2 - SCREEN_HEIGHT // 2
                    camera.target_x = camera.x
                    camera.target_y = camera.y

                    player_bullets = []
                    enemy_bullets = []
                    enemies = spawn_enemies(1, WORLD_WIDTH, WORLD_HEIGHT, walls, player, environment_system)
                    wave_number = 1
                    enemies_killed = 0
                    game_over = False
                    item_manager = ItemManager()
                    morality_system = MoralitySystem()
                    exp_system = ExperienceSystem()

                    # Réinitialiser le système d'environnement
                    environment_system = EnvironmentSystem()
                    environment_renderer = EnvironmentRenderer(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Vérifier si le jeu doit être en pause
        game_paused = ui_manager.should_pause_game(exp_system)
        
        if not game_over and not game_paused:
            # Mise à jour du joueur
            player.update(walls, morality_system)
            
            # Mise à jour de la caméra
            camera.update(player)
            
            # Mise à jour du système de moralité
            morality_system.update()
            
            # Appliquer les effets de moralité au joueur
            morality_effects.apply_morality_effects(player, morality_system)
            
            # Mise à jour du système d'expérience
            exp_system.update()

            # Mise à jour du renderer d'environnement
            environment_renderer.update(environment_system)
            
            # Générer choix de level-up si nécessaire
            if exp_system.is_leveling_up and not exp_system.level_up_choices:
                print("Génération des choix de level-up...")
                exp_system.generate_level_up_choices(morality_system, item_manager)
                print(f"Choix générés: {exp_system.level_up_choices}")
            
            # Tir automatique du joueur
            keys = pygame.key.get_pressed()
            mouse_buttons = pygame.mouse.get_pressed()
            
            if keys[pygame.K_SPACE] or mouse_buttons[0]:
                mouse_pos = pygame.mouse.get_pos()
                world_mouse_pos = camera.screen_to_world(mouse_pos[0], mouse_pos[1])
                bullets = player.try_shoot(world_mouse_pos)
                player_bullets.extend(bullets)
            
            # Mise à jour des ennemis et gestion des boss
            for enemy in enemies:
                enemy.update(player, walls, enemies)
                
                # Gestion spécifique selon le type d'ennemi
                if isinstance(enemy, ShooterEnemy):
                    bullet = enemy.try_shoot(player)
                    if bullet:
                        enemy_bullets.append(bullet)
                
                elif isinstance(enemy, CultistEnemy):
                    # Tentative d'invocation de démon
                    if enemy.try_summon():
                        daemon_x = enemy.x + random.randint(-50, 50)
                        daemon_y = enemy.y + random.randint(-50, 50)
                        summoned_daemon = DaemonEnemy(daemon_x, daemon_y, is_summoned=True)
                        enemies.append(summoned_daemon)
                        print("Un démon a été invoqué !")
                
                elif isinstance(enemy, DaemonEnemy):
                    # Attaque psychique
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
                
                # === GESTION DES BOSS ===
                elif isinstance(enemy, ChaosSorcererBoss):
                    # Téléportation
                    if random.random() < 0.02:  # 2% de chance par frame
                        enemy.try_teleport()
                    
                    # Invocation de démons
                    if enemy.try_summon_daemon():
                        for _ in range(2):  # Invoque 2 démons à la fois
                            daemon_x = enemy.x + random.randint(-80, 80)
                            daemon_y = enemy.y + random.randint(-80, 80)
                            summoned_daemon = DaemonEnemy(daemon_x, daemon_y, is_summoned=True)
                            enemies.append(summoned_daemon)
                        print("🔥 Le Sorcier invoque des démons !")
                    
                    # Attaque de zone
                    if enemy.try_area_attack(player):
                        print("⚠️ ATTAQUE DE ZONE IMMINENTE !")
                    
                    if enemy.handle_area_cast():  # Si l'incantation est terminée
                        # Dégâts de zone autour du sorcier
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
                            print("💥 DÉFLAGRATION CHAOTIQUE !")
                    
                    # Barrage de projectiles
                    if enemy.try_projectile_barrage(player):
                        for i in range(8):  # 8 projectiles en cercle
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
                    # Purification
                    if random.random() < 0.015:  # 1.5% de chance par frame
                        enemy.try_purification()
                    
                    if enemy.handle_purification():  # Si l'incantation est terminée
                        # Dégâts de purification (très larges)
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
                            print("⚡ PURIFICATION IMPÉRIALE !")
                    
                    # Tirs bénis
                    if enemy.try_blessed_shots(player):
                        for i in range(3):  # Triple tir
                            angle_offset = (i - 1) * 0.3
                            dx = player.x - enemy.x
                            dy = player.y - enemy.y
                            length = math.sqrt(dx*dx + dy*dy)
                            if length > 0:
                                dx /= length
                                dy /= length
                            
                            # Rotation pour le spread
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
                    
                    # Activation automatique du bouclier
                    if enemy.health < enemy.max_health * 0.4 and random.random() < 0.01:
                        enemy.try_activate_shield()
                
                elif isinstance(enemy, DaemonPrinceBoss):
                    # Téléportation chaotique
                    if random.random() < 0.025:  # 2.5% de chance
                        enemy.try_chaos_teleport()
                    
                    # Tempête Warp
                    if random.random() < 0.008:  # 0.8% de chance
                        enemy.try_warp_storm()
                    
                    if enemy.handle_warp_storm():  # Si l'incantation est terminée
                        # Tempête massive - dégâts énormes
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
                            print("🌩️ TEMPÊTE WARP DÉVASTATRICE !")
                    
                    # Vague de corruption
                    if enemy.try_corruption_wave():
                        # Projectiles en spirale
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
                    
                    # Invocation massive
                    if enemy.try_mass_summon():
                        summon_count = 3 if enemy.chaos_form == 1 else 5
                        for _ in range(summon_count):
                            daemon_x = enemy.x + random.randint(-100, 100)
                            daemon_y = enemy.y + random.randint(-100, 100)
                            summoned_daemon = DaemonEnemy(daemon_x, daemon_y, is_summoned=True)
                            enemies.append(summoned_daemon)
                            enemy.total_summons += 1
                        print(f"💀 INVOCATION MASSIVE ! {summon_count} démons apparaissent !")
            
            # Mise à jour des projectiles du joueur (avec nettoyage)
            clean_bullets = []
            for bullet in player_bullets:
                if hasattr(bullet, 'update'):  # Vérifier que c'est un vrai bullet
                    if bullet.update(walls, WORLD_WIDTH, WORLD_HEIGHT, enemies):
                        clean_bullets.append(bullet)
                # Ignorer silencieusement les objets qui ne sont pas des bullets
            player_bullets = clean_bullets
            
            # Mise à jour des projectiles ennemis
            enemy_bullets = [bullet for bullet in enemy_bullets 
                           if bullet.update(walls, WORLD_WIDTH, WORLD_HEIGHT)]
            
            # Mise à jour des objets
            item_manager.update()
            item_manager.check_pickup(player, morality_system)

            # ===== GESTION DES COLLISIONS (VERSION CORRIGÉE) =====
            enemies_to_remove = []  # Liste des ennemis à supprimer
            bullets_to_remove = []  # Liste des projectiles à supprimer
            
            # Collisions projectiles joueur vs ennemis
            for bullet in player_bullets:
                if bullet in bullets_to_remove:  # Skip si déjà marqué pour suppression
                    continue
                    
                for enemy in enemies:
                    if enemy in enemies_to_remove:  # Skip si ennemi déjà marqué pour suppression
                        continue
                        
                    if bullet.rect.colliderect(enemy.rect):
                        # Appliquer dégâts
                        if enemy.take_damage(bullet.damage):
                            # Gestion des événements spéciaux à la mort des boss
                            if isinstance(enemy, ChaosSorcererBoss):
                                print("🔥 Le Sorcier du Chaos est vaincu ! +100 XP")
                                exp_system.add_experience(100)
                                morality_system.add_faith(15, "Destruction d'un Sorcier du Chaos")
                            
                            elif isinstance(enemy, InquisitorLordBoss):
                                print("⚡ Le Seigneur Inquisiteur est vaincu ! +120 XP") 
                                exp_system.add_experience(120)
                                morality_system.add_corruption(10, "Meurtre d'un Inquisiteur")
                            
                            elif isinstance(enemy, DaemonPrinceBoss):
                                print("💀 LE PRINCE DAEMON EST VAINCU ! VICTOIRE ÉPIQUE ! +200 XP")
                                exp_system.add_experience(200)
                                morality_system.add_faith(25, "Bannissement d'un Prince Daemon")
                            
                            # Traitement normal pour les autres ennemis
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
                            
                            # Pour tous les boss - nettoyer leurs invocations
                            if isinstance(enemy, (ChaosSorcererBoss, InquisitorLordBoss, DaemonPrinceBoss)):
                                # Supprimer les démons invoqués par ce boss
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
                            
                            # Si level-up, générer immédiatement les choix
                            if exp_system.is_leveling_up and not exp_system.level_up_choices:
                                exp_system.generate_level_up_choices(morality_system, item_manager)
                            
                            # Marquer l'ennemi pour suppression
                            enemies_to_remove.append(enemy)
                            enemies_killed += 1
                        
                        # Détruire le projectile (sauf si piercing)
                        if not bullet.piercing:
                            bullets_to_remove.append(bullet)
                            break
                        else:
                            bullet.has_hit = True
            
            # Supprimer les ennemis et projectiles marqués APRÈS l'itération
            for enemy in enemies_to_remove:
                if enemy in enemies:  # Vérification de sécurité
                    enemies.remove(enemy)

            for bullet in bullets_to_remove:
                if bullet in player_bullets:  # Vérification de sécurité
                    player_bullets.remove(bullet)
            
            # Collisions projectiles ennemis vs joueur
            for bullet in enemy_bullets[:]:
                if bullet.rect.colliderect(player.rect):
                    damage_taken = bullet.damage
                    if player.take_damage(damage_taken):
                        game_over = True
                    else:
                        # Traiter les dégâts pour la moralité
                        morality_system.process_damage_taken(damage_taken)
                    enemy_bullets.remove(bullet)
            
            # Collisions ennemis vs joueur (contact direct)
            for enemy in enemies:
                if enemy.rect.colliderect(player.rect):
                    contact_damage = 5
                    
                    # Dégâts spéciaux selon le type
                    if isinstance(enemy, RenegadeMarineEnemy) and enemy.is_charging:
                        contact_damage = 20
                        enemy.is_charging = False
                        print("Charge du Marine Renégat !")
                    
                    # BOSS - Dégâts de contact massifs
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
                        # Chance de corruption au contact
                        if random.random() < 0.3:
                            morality_system.add_corruption(3, "Contact avec un Prince Daemon")
                    
                    if player.take_damage(contact_damage):
                        game_over = True
                    else:
                        morality_system.process_damage_taken(contact_damage)
            
            # Vérifier si vague terminée
            if len(enemies) == 0:
                # Messages spéciaux après boss
                if wave_number == 5:
                    print("✅ Sorcier du Chaos vaincu ! La vague 6 vous attend...")
                elif wave_number == 15:
                    print("✅ Seigneur Inquisiteur vaincu ! Préparez-vous pour le boss final...")
                elif wave_number == 20:
                    print("🎉 PRINCE DAEMON VAINCU ! VOUS AVEZ GAGNÉ ! Mais les vagues continuent...")
                
                wave_number += 1
                
                # Générer un nouvel environnement pour la nouvelle vague
                walls = create_environment_walls(WORLD_WIDTH, WORLD_HEIGHT, wave_number, morality_system, environment_system)
                
                # Repositionner le joueur si nécessaire (éviter qu'il soit dans un mur)
                if not get_environment_spawn_position:  # Vérification de sécurité
                    from pathfinding import PathfindingHelper
                    if not PathfindingHelper.is_position_free(player.x, player.y, player.width, player.height, walls):
                        # Repositionner le joueur
                        new_x, new_y = get_environment_spawn_position(WORLD_WIDTH, WORLD_HEIGHT, 
                                                                    player.width, player.height, walls, avoid_center=False)
                        player.x, player.y = new_x, new_y
                        player.rect.x, player.rect.y = player.x, player.y
                
                enemies = spawn_enemies(wave_number, WORLD_WIDTH, WORLD_HEIGHT, walls, player, environment_system)
                wave_clear = True
        
        # Mise à jour de l'UI (toujours, même en pause)
        ui_manager.update()
        
        # Rendu
        screen.fill(BLACK)

        if not game_over:
            # Dessiner le fond d'environnement
            environment_renderer.draw_background(screen, camera, environment_system)
            
            # Dessiner les murs avec le style d'environnement
            environment_renderer.draw_walls(screen, walls, camera, environment_system)
            
            # Dessiner le joueur
            player_screen_rect = camera.apply(player)
            old_x, old_y = player.x, player.y
            player.x, player.y = player_screen_rect.x, player_screen_rect.y
            player.draw(screen)
            player.x, player.y = old_x, old_y
            
            # Dessiner les ennemis (seulement ceux visibles)
            for enemy in enemies:
                if camera.is_visible(enemy):
                    enemy_screen_rect = camera.apply(enemy)
                    old_x, old_y = enemy.x, enemy.y
                    enemy.x, enemy.y = enemy_screen_rect.x, enemy_screen_rect.y
                    enemy.draw(screen)
                    enemy.x, enemy.y = old_x, old_y
            
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
            
            # Instructions mises à jour avec info environnement
            env_info = environment_system.get_environment_info()
            instructions = [
                "WASD/Flèches: Déplacement | Espace/Clic: Tir automatique",
                f"🌍 Environnement: {env_info['name']} | Vague {wave_number}",
                "🔥 BOSS: Vague 5, 15, 20 | Esquivez les attaques de zone !",
                "Violet: Cultiste  Bronze: Marine  Noir: Démon"
            ]
            for i, instruction in enumerate(instructions):
                text = pygame.font.Font(None, 20).render(instruction, True, WHITE)
                screen.blit(text, (10, SCREEN_HEIGHT - 80 + i * 20))
        else:
            # Écran Game Over
            ui_manager.draw_minimal_hud(screen, player, morality_system, exp_system)
            
            # Overlay Game Over
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
        
        # Écran de level-up par-dessus tout
        if exp_system.is_leveling_up:
            if exp_system.level_up_choices:  # S'assurer qu'il y a des choix
                ui_manager.draw_level_up_notification(screen)
                exp_system.draw_level_up_screen(screen, morality_system, item_manager)
            else:
                # Afficher un message temporaire si pas de choix
                font = pygame.font.Font(None, 48)
                loading_text = font.render("Génération des choix...", True, (255, 255, 255))
                loading_rect = loading_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                screen.blit(loading_text, loading_rect)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":
    main()