"""
Système de spawn d'ennemis - Extrait de main.py
Contient SpawnSystem avec toute la logique de spawn d'ennemis et de boss
"""
import random
import sys
import os

# Ajouter le chemin parent pour accéder aux modules racine
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from pathfinding import PathfindingHelper
from enemies import (
    BasicEnemy, ShooterEnemy, FastEnemy, 
    CultistEnemy, RenegadeMarineEnemy, DaemonEnemy,
    ChaosSorcererBoss, InquisitorLordBoss, DaemonPrinceBoss
)
from ..core.constants import WORLD_WIDTH, WORLD_HEIGHT

class SpawnSystem:
    """Gestionnaire de spawn d'ennemis"""
    
    def __init__(self):
        self.spawn_stats = {
            "total_spawned": 0,
            "bosses_spawned": 0,
            "last_wave": 0
        }
    
    def spawn_enemies_for_wave(self, wave_number, level_manager, player):
        """Génère des ennemis avec positions optimisées (fonction extraite de main.py)"""
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
            self.spawn_stats["bosses_spawned"] += 1
            return enemies
        
        elif wave_number == 15:
            print("⚡ BOSS WAVE ! Un Seigneur Inquisiteur vous défie !")
            boss_x, boss_y = WORLD_WIDTH // 2, WORLD_HEIGHT // 2
            enemies.append(InquisitorLordBoss(boss_x, boss_y))
            self.spawn_stats["bosses_spawned"] += 1
            return enemies
        
        elif wave_number == 20:
            print("💀 BOSS FINAL ! Un Prince Daemon émerge du Warp !")
            boss_x, boss_y = WORLD_WIDTH // 2, WORLD_HEIGHT // 2
            enemies.append(DaemonPrinceBoss(boss_x, boss_y))
            self.spawn_stats["bosses_spawned"] += 1
            return enemies
        
        elif wave_number > 20:
            boss_chance = min(0.3, (wave_number - 20) * 0.1)
            if random.random() < boss_chance:
                boss_type = random.choice([ChaosSorcererBoss, InquisitorLordBoss])
                print(f"🎯 BOSS SURPRISE ! {boss_type.__name__} apparaît !")
                boss_x, boss_y = WORLD_WIDTH // 2, WORLD_HEIGHT // 2
                enemies.append(boss_type(boss_x, boss_y))
                self.spawn_stats["bosses_spawned"] += 1
        
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
        total_spawned_this_wave = 0
        
        for enemy_class, count, width, height, min_distance in enemy_types:
            for _ in range(count):
                if spawn_index < len(spawn_positions):
                    # Utiliser position prédéfinie
                    x, y = spawn_positions[spawn_index]
                    
                    # Vérifier que la position est valide
                    if PathfindingHelper.is_position_free(x, y, width, height, walls):
                        enemies.append(enemy_class(x, y))
                        spawn_index += 1
                        total_spawned_this_wave += 1
                    else:
                        # Position bloquée, utiliser le pathfinding
                        x, y = PathfindingHelper.find_free_spawn_position(
                            WORLD_WIDTH, WORLD_HEIGHT, width, height, 
                            walls, player, min_distance
                        )
                        enemies.append(enemy_class(x, y))
                        total_spawned_this_wave += 1
                else:
                    # Plus de positions prédéfinies, utiliser le pathfinding
                    x, y = PathfindingHelper.find_free_spawn_position(
                        WORLD_WIDTH, WORLD_HEIGHT, width, height, 
                        walls, player, min_distance
                    )
                    enemies.append(enemy_class(x, y))
                    total_spawned_this_wave += 1
        
        # Mettre à jour les statistiques
        self.spawn_stats["total_spawned"] += total_spawned_this_wave
        self.spawn_stats["last_wave"] = wave_number
        
        print(f"📊 Spawn Wave {wave_number}: {total_spawned_this_wave} ennemis créés")
        
        return enemies
    
    def get_spawn_statistics(self):
        """Retourne les statistiques de spawn"""
        return self.spawn_stats.copy()
    
    def reset_statistics(self):
        """Remet à zéro les statistiques"""
        self.spawn_stats = {
            "total_spawned": 0,
            "bosses_spawned": 0,
            "last_wave": 0
        }