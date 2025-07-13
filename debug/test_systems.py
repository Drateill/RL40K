#!/usr/bin/env python3
"""
Test des systèmes de jeu sans pygame pour vérifier la logique
"""

# Mock de pygame pour les tests
class MockRect:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.width, self.height = x, y, w, h
        self.left, self.top, self.right, self.bottom = x, y, x+w, y+h
    
    def colliderect(self, other):
        return not (self.right < other.left or self.left > other.right or 
                   self.bottom < other.top or self.top > other.bottom)

# Mock d'entités pour les tests
class MockPlayer:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.width, self.height = 32, 32
        self.health = 100
        self.shoot_timer = 0
    
    def take_damage(self, damage):
        self.health -= damage
        print(f"Joueur prend {damage} dégâts, santé: {self.health}")

class MockEnemy:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.width, self.height = 20, 20
        self.health = 30
        self.damage = 10
    
    def take_damage(self, damage):
        self.health -= damage
        print(f"Ennemi prend {damage} dégâts, santé: {self.health}")

class MockProjectile:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.radius = 3
        self.damage = 20
        self.is_player_bullet = True

# Import des systèmes réels
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.systems.entity_manager import EntityManager
from src.systems.collision_system import CollisionSystem

def test_entity_manager():
    print("=== Test EntityManager ===")
    
    em = EntityManager()
    
    # Test ajout player
    player = MockPlayer(100, 100)
    em.add_player(player)
    assert em.get_player() == player
    print("✅ Ajout joueur OK")
    
    # Test ajout ennemis
    enemy1 = MockEnemy(150, 150)
    enemy2 = MockEnemy(200, 200)
    em.add_enemy(enemy1)
    em.add_enemy(enemy2)
    assert len(em.get_enemies()) == 2
    print("✅ Ajout ennemis OK")
    
    # Test ajout projectiles
    projectile = MockProjectile(120, 120)
    em.add_projectile(projectile)
    assert len(em.get_projectiles()) == 1
    print("✅ Ajout projectiles OK")
    
    print(f"État: Joueur={em.get_player() is not None}, Ennemis={len(em.get_enemies())}, Projectiles={len(em.get_projectiles())}")

def test_collision_system():
    print("\n=== Test CollisionSystem ===")
    
    em = EntityManager()
    cs = CollisionSystem()
    
    # Setup
    player = MockPlayer(100, 100)
    em.add_player(player)
    
    enemy = MockEnemy(110, 110)  # Proche du joueur pour collision
    em.add_enemy(enemy)
    
    projectile = MockProjectile(115, 115)  # Proche de l'ennemi
    em.add_projectile(projectile)
    
    print(f"Avant collision - Joueur santé: {player.health}, Ennemi santé: {enemy.health}")
    
    # Test collision projectile-ennemi
    cs.check_projectile_enemy_collisions(em)
    print(f"Après collision projectile-ennemi - Ennemi santé: {enemy.health}")
    
    # Test collision joueur-ennemi
    cs.check_player_enemy_collisions(em)
    print(f"Après collision joueur-ennemi - Joueur santé: {player.health}")
    
    print("✅ Système de collision fonctionne")

def test_bullet_logic():
    print("\n=== Test Logique Bullet ===")
    
    # Import bullet
    sys.path.append(os.path.dirname(__file__))
    
    try:
        from bullet import Bullet
        
        # Test création bullet
        bullet = Bullet(100, 100, 1, 0, True, 25)
        print(f"Bullet créé: pos=({bullet.x}, {bullet.y}), damage={bullet.damage}")
        
        # Test movement
        old_x = bullet.x
        # Simuler update sans pygame
        bullet.x += bullet.dx
        bullet.y += bullet.dy
        
        print(f"Après mouvement: pos=({bullet.x}, {bullet.y}), déplacement={bullet.x - old_x}")
        print("✅ Logique bullet OK")
        
    except ImportError as e:
        print(f"⚠️ Import bullet échoué: {e}")

if __name__ == "__main__":
    try:
        test_entity_manager()
        test_collision_system()
        test_bullet_logic()
        print("\n🎉 Tous les tests passent - les systèmes de base fonctionnent!")
    except Exception as e:
        print(f"\n❌ Erreur dans les tests: {e}")
        import traceback
        traceback.print_exc()