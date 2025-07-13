import pygame
import math
import random

class PathfindingHelper:
    """Aide au pathfinding pour les ennemis"""
    
    @staticmethod
    def is_position_free(x, y, width, height, walls):
        """Vérifie si une position est libre (pas dans un mur)"""
        test_rect = pygame.Rect(x, y, width, height)
        for wall in walls:
            if test_rect.colliderect(wall.rect):
                return False
        return True
    
    @staticmethod
    def find_free_spawn_position(world_width, world_height, entity_width, entity_height, walls, player, min_distance_from_player=100):
        """Trouve une position de spawn libre pour un ennemi"""
        max_attempts = 50
        
        for _ in range(max_attempts):
            # Position aléatoire sur les bords
            side = random.randint(1, 4)
            margin = 60  # Plus de marge pour éviter les murs de bordure
            
            if side == 1:  # Haut
                x = random.randint(margin, world_width - margin - entity_width)
                y = margin
            elif side == 2:  # Bas
                x = random.randint(margin, world_width - margin - entity_width)
                y = world_height - margin - entity_height
            elif side == 3:  # Gauche
                x = margin
                y = random.randint(margin, world_height - margin - entity_height)
            else:  # Droite
                x = world_width - margin - entity_width
                y = random.randint(margin, world_height - margin - entity_height)
            
            # Vérifier que la position est libre
            if PathfindingHelper.is_position_free(x, y, entity_width, entity_height, walls):
                # Vérifier la distance au joueur
                distance_to_player = math.sqrt((x - player.x)**2 + (y - player.y)**2)
                if distance_to_player >= min_distance_from_player:
                    return x, y
        
        # Si on ne trouve pas, spawn au centre d'un bord (position safe)
        return world_width // 2, 50  # Haut centre par défaut
    
    @staticmethod
    def get_movement_direction(start_x, start_y, target_x, target_y, entity_width, entity_height, walls, speed):
        """Calcule la direction de mouvement avec évitement d'obstacles"""
        
        # Direction directe vers la cible
        dx = target_x - start_x
        dy = target_y - start_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance == 0:
            return 0, 0
        
        # Normaliser
        direct_dx = (dx / distance) * speed
        direct_dy = (dy / distance) * speed
        
        # Tester si on peut aller directement vers la cible
        test_x = start_x + direct_dx
        test_y = start_y + direct_dy
        
        if PathfindingHelper.is_position_free(test_x, test_y, entity_width, entity_height, walls):
            return direct_dx, direct_dy
        
        # Si bloqué, essayer des directions alternatives
        alternatives = [
            # Essayer de contourner par les côtés
            (direct_dx * 0.7 + direct_dy * 0.7, direct_dy * 0.7 - direct_dx * 0.7),  # Rotation +45°
            (direct_dx * 0.7 - direct_dy * 0.7, direct_dy * 0.7 + direct_dx * 0.7),  # Rotation -45°
            # Mouvement perpendiculaire pour sortir du mur
            (-direct_dy, direct_dx),   # Perpendiculaire droite
            (direct_dy, -direct_dx),   # Perpendiculaire gauche
            # Mouvement de recul
            (-direct_dx * 0.5, -direct_dy * 0.5),
        ]
        
        # Tester chaque alternative
        for alt_dx, alt_dy in alternatives:
            test_x = start_x + alt_dx
            test_y = start_y + alt_dy
            
            if PathfindingHelper.is_position_free(test_x, test_y, entity_width, entity_height, walls):
                return alt_dx, alt_dy
        
        # Si rien ne marche, rester sur place
        return 0, 0
    
    @staticmethod
    def wall_slide(entity_x, entity_y, desired_dx, desired_dy, entity_width, entity_height, walls):
        """Permet de glisser le long des murs au lieu de se bloquer"""
        
        # Tester le mouvement horizontal uniquement
        test_x = entity_x + desired_dx
        if PathfindingHelper.is_position_free(test_x, entity_y, entity_width, entity_height, walls):
            return desired_dx, 0
        
        # Tester le mouvement vertical uniquement  
        test_y = entity_y + desired_dy
        if PathfindingHelper.is_position_free(entity_x, test_y, entity_width, entity_height, walls):
            return 0, desired_dy
        
        # Aucun mouvement possible
        return 0, 0

class FlockingBehavior:
    """Comportement de groupe pour éviter que les ennemis se superposent"""
    
    @staticmethod
    def get_separation_force(entity, other_entities, separation_distance=40):
        """Force de séparation pour éviter les collisions entre ennemis"""
        force_x, force_y = 0, 0
        count = 0
        
        for other in other_entities:
            if other == entity:
                continue
                
            distance = math.sqrt((entity.x - other.x)**2 + (entity.y - other.y)**2)
            
            if 0 < distance < separation_distance:
                # Force proportionnelle inverse à la distance
                force_strength = (separation_distance - distance) / separation_distance
                
                diff_x = entity.x - other.x
                diff_y = entity.y - other.y
                
                if distance > 0:
                    diff_x /= distance
                    diff_y /= distance
                
                force_x += diff_x * force_strength
                force_y += diff_y * force_strength
                count += 1
        
        if count > 0:
            force_x /= count
            force_y /= count
            
            # Normaliser et limiter la force
            force_magnitude = math.sqrt(force_x**2 + force_y**2)
            if force_magnitude > 0:
                max_force = 2.0
                if force_magnitude > max_force:
                    force_x = (force_x / force_magnitude) * max_force
                    force_y = (force_y / force_magnitude) * max_force
        
        return force_x, force_y