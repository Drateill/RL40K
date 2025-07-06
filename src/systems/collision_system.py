"""
Système de collisions - Centralise toute la détection de collisions
Remplace la logique de collision dispersée dans main.py
"""
import pygame
import math

class CollisionSystem:
    """Gestionnaire centralisé des collisions"""
    
    def __init__(self):
        self.collision_stats = {
            "projectile_enemy": 0,
            "projectile_wall": 0,
            "player_enemy": 0,
            "player_item": 0,
            "total_checks": 0
        }
    
    
    def update(self, entity_manager):
        """Met à jour toutes les collisions"""
        self.collision_stats["total_checks"] += 1
        
        # Collisions projectiles vs ennemis
        self.check_projectile_enemy_collisions(entity_manager)
        
        # Collisions projectiles vs murs
        self.check_projectile_wall_collisions(entity_manager)
        
        # Collisions joueur vs ennemis
        self.check_player_enemy_collisions(entity_manager)
        
        # Collisions joueur vs objets
        self.check_player_item_collisions(entity_manager)
        
        # Nettoyage automatique des entités mortes
        entity_manager.cleanup_dead_entities()
    
    def check_projectile_enemy_collisions(self, entity_manager):
        """Vérifie les collisions entre projectiles et ennemis"""
        projectiles = entity_manager.get_projectiles()
        enemies = entity_manager.get_enemies()
        
        projectiles_to_remove = []
        enemies_to_remove = []
        
        for projectile in projectiles:
            # Ignorer les projectiles ennemis vs ennemis
            if hasattr(projectile, 'is_enemy_projectile') and projectile.is_enemy_projectile:
                continue
            
            for enemy in enemies:
                if self.circle_collision(
                    projectile.x, projectile.y, 3,  # Rayon projectile
                    enemy.x, enemy.y, 10  # Rayon ennemi
                ):
                    # Appliquer dégâts
                    if hasattr(enemy, 'take_damage'):
                        damage = getattr(projectile, 'damage', 20)
                        enemy.take_damage(damage)
                    elif hasattr(enemy, 'health'):
                        enemy.health -= getattr(projectile, 'damage', 20)
                    
                    # Marquer le projectile pour suppression
                    if projectile not in projectiles_to_remove:
                        projectiles_to_remove.append(projectile)
                    
                    # Si l'ennemi est mort, le marquer pour suppression
                    if hasattr(enemy, 'health') and enemy.health <= 0:
                        if enemy not in enemies_to_remove:
                            enemies_to_remove.append(enemy)
                    
                    self.collision_stats["projectile_enemy"] += 1
                    break  # Un projectile ne peut toucher qu'un ennemi
        
        # Supprimer les entités touchées
        for projectile in projectiles_to_remove:
            entity_manager.remove_projectile(projectile)
        
        for enemy in enemies_to_remove:
            entity_manager.remove_enemy(enemy)
    
    def check_projectile_wall_collisions(self, entity_manager):
        """Vérifie les collisions entre projectiles et murs"""
        projectiles = entity_manager.get_projectiles()
        walls = entity_manager.get_walls()
        
        projectiles_to_remove = []
        
        for projectile in projectiles:
            projectile_rect = pygame.Rect(
                projectile.x - 3, projectile.y - 3, 6, 6
            )
            
            for wall in walls:
                wall_rect = wall.rect if hasattr(wall, 'rect') else wall
                
                if projectile_rect.colliderect(wall_rect):
                    if projectile not in projectiles_to_remove:
                        projectiles_to_remove.append(projectile)
                        self.collision_stats["projectile_wall"] += 1
                    break
        
        # Supprimer les projectiles qui ont touché un mur
        for projectile in projectiles_to_remove:
            entity_manager.remove_projectile(projectile)
    
    def check_player_enemy_collisions(self, entity_manager):
        """Vérifie les collisions entre le joueur et les ennemis"""
        player = entity_manager.get_player()
        enemies = entity_manager.get_enemies()
        
        if not player:
            return
        
        for enemy in enemies:
            if self.circle_collision(
                player.x, player.y, 12,  # Rayon joueur
                enemy.x, enemy.y, 10   # Rayon ennemi
            ):
                # Appliquer dégâts au joueur
                if hasattr(player, 'take_damage'):
                    damage = getattr(enemy, 'damage', 10)
                    player.take_damage(damage)
                elif hasattr(player, 'health'):
                    player.health -= getattr(enemy, 'damage', 10)
                
                # Repousser le joueur (knockback)
                if hasattr(player, 'apply_knockback'):
                    dx = player.x - enemy.x
                    dy = player.y - enemy.y
                    distance = math.sqrt(dx*dx + dy*dy)
                    if distance > 0:
                        knockback_force = 30
                        player.apply_knockback(
                            (dx/distance) * knockback_force,
                            (dy/distance) * knockback_force
                        )
                
                self.collision_stats["player_enemy"] += 1
    
    def check_player_item_collisions(self, entity_manager):
        """Vérifie les collisions entre le joueur et les objets"""
        player = entity_manager.get_player()
        items = entity_manager.get_items()
        
        if not player:
            return
        
        items_to_remove = []
        
        for item in items:
            if self.circle_collision(
                player.x, player.y, 15,  # Rayon de ramassage
                item.x, item.y, 8      # Rayon objet
            ):
                # Appliquer l'effet de l'objet
                if hasattr(item, 'apply_effect'):
                    item.apply_effect(player)
                
                # Marquer pour suppression
                items_to_remove.append(item)
                self.collision_stats["player_item"] += 1
        
        # Supprimer les objets ramassés
        for item in items_to_remove:
            entity_manager.remove_item(item)
    
    def circle_collision(self, x1, y1, r1, x2, y2, r2):
        """Détection de collision entre deux cercles"""
        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx*dx + dy*dy)
        return distance < (r1 + r2)
    
    def rect_collision(self, rect1, rect2):
        """Détection de collision entre deux rectangles"""
        return rect1.colliderect(rect2)
    
    def point_in_rect(self, x, y, rect):
        """Vérifie si un point est dans un rectangle"""
        return rect.collidepoint(x, y)
    
    def circle_rect_collision(self, circle_x, circle_y, radius, rect):
        """Collision entre un cercle et un rectangle"""
        # Trouver le point le plus proche du centre du cercle sur le rectangle
        closest_x = max(rect.left, min(circle_x, rect.right))
        closest_y = max(rect.top, min(circle_y, rect.bottom))
        
        # Calculer la distance entre le centre du cercle et ce point
        dx = circle_x - closest_x
        dy = circle_y - closest_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        return distance < radius
    
    def line_circle_collision(self, x1, y1, x2, y2, circle_x, circle_y, radius):
        """Collision entre une ligne et un cercle"""
        # Distance du point au segment de ligne
        A = circle_x - x1
        B = circle_y - y1
        C = x2 - x1
        D = y2 - y1
        
        dot = A * C + B * D
        len_sq = C * C + D * D
        
        if len_sq == 0:
            # La ligne est un point
            distance = math.sqrt(A*A + B*B)
        else:
            param = dot / len_sq
            
            if param < 0:
                # Plus proche de (x1, y1)
                xx = x1
                yy = y1
            elif param > 1:
                # Plus proche de (x2, y2)
                xx = x2
                yy = y2
            else:
                # Sur le segment
                xx = x1 + param * C
                yy = y1 + param * D
            
            dx = circle_x - xx
            dy = circle_y - yy
            distance = math.sqrt(dx*dx + dy*dy)
        
        return distance < radius
    
    def get_collision_statistics(self):
        """Retourne les statistiques de collision"""
        return self.collision_stats.copy()
    
    def reset_statistics(self):
        """Remet à zéro les statistiques"""
        self.collision_stats = {
            "projectile_enemy": 0,
            "projectile_wall": 0,
            "player_enemy": 0,
            "player_item": 0,
            "total_checks": 0
        }
    
    def print_statistics(self):
        """Affiche les statistiques de collision"""
        stats = self.collision_stats
        print("📊 Statistiques de collision:")
        print(f"  💥 Projectile vs Ennemi: {stats['projectile_enemy']}")
        print(f"  🧱 Projectile vs Mur: {stats['projectile_wall']}")
        print(f"  👤 Joueur vs Ennemi: {stats['player_enemy']}")
        print(f"  📦 Joueur vs Objet: {stats['player_item']}")
        print(f"  🔄 Vérifications totales: {stats['total_checks']}")
    
    def optimize_collision_checks(self, entity_manager):
        """Optimise les vérifications de collision (spatial partitioning basique)"""
        # Cette méthode peut être implémentée plus tard pour optimiser
        # les performances avec un système de spatial partitioning
        pass

    