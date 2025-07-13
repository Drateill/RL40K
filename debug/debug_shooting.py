#!/usr/bin/env python3
"""
Debug du système de tir - Simulation simple
"""

import math

class MockMoralitySystem:
    def get_stat_modifiers(self):
        return {
            "damage_multiplier": 1.0,
            "fire_rate_multiplier": 1.0,
            "special_effects": []
        }

class MockBullet:
    def __init__(self, x, y, dx, dy, damage=10):
        self.x = x
        self.y = y
        self.dx = dx * 8  # Vitesse
        self.dy = dy * 8
        self.damage = damage
        self.radius = 3
        print(f"Bullet créé: pos=({self.x:.1f}, {self.y:.1f}), vel=({self.dx:.1f}, {self.dy:.1f}), damage={self.damage}")

class MockPlayer:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.shoot_timer = 0
        self.shoot_delay = 10
        self.base_damage = 20
        self.multi_shot = 1
        self.piercing = False
        self.bullet_size = 1.0
        self.homing = False
        self.explosive = False
        self.holy_damage = False
    
    def try_shoot(self, mouse_pos, morality_system=None):
        """Version simplifiée de try_shoot"""
        print(f"try_shoot appelé: timer={self.shoot_timer}, mouse_pos={mouse_pos}")
        
        if self.shoot_timer <= 0:
            self.shoot_timer = self.shoot_delay
            return self.shoot(mouse_pos, morality_system)
        return []
    
    def shoot(self, mouse_pos, morality_system=None):
        """Version simplifiée de shoot"""
        print(f"shoot appelé vers {mouse_pos}")
        
        # Calculer direction
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        dx = mouse_pos[0] - center_x
        dy = mouse_pos[1] - center_y
        
        # Normaliser
        length = math.sqrt(dx*dx + dy*dy)
        if length != 0:
            dx /= length
            dy /= length
        
        print(f"Direction calculée: ({dx:.2f}, {dy:.2f})")
        
        # Créer bullet
        bullet = MockBullet(center_x, center_y, dx, dy, self.base_damage)
        return [bullet]
    
    def update_timer(self):
        if self.shoot_timer > 0:
            self.shoot_timer -= 1

def test_shooting_system():
    print("=== Test du système de tir ===")
    
    # Setup
    player = MockPlayer(100, 100)
    morality_system = MockMoralitySystem()
    
    # Test 1: Premier tir
    print("\n--- Test 1: Premier tir ---")
    mouse_pos = (200, 150)
    bullets = player.try_shoot(mouse_pos, morality_system)
    print(f"Bullets créés: {len(bullets)}")
    
    # Test 2: Tir immédiat (devrait échouer à cause du timer)
    print("\n--- Test 2: Tir immédiat (timer actif) ---")
    bullets2 = player.try_shoot(mouse_pos, morality_system)
    print(f"Bullets créés: {len(bullets2)} (devrait être 0)")
    
    # Test 3: Attendre et tirer à nouveau
    print("\n--- Test 3: Après délai ---")
    for i in range(15):  # Délai de 10 + marge
        player.update_timer()
    
    bullets3 = player.try_shoot((150, 200), morality_system)
    print(f"Bullets créés: {len(bullets3)} (devrait être 1)")

def test_collision_detection():
    print("\n=== Test de détection de collision ===")
    
    # Position du bullet et de l'ennemi
    bullet_x, bullet_y = 120, 115
    enemy_x, enemy_y = 125, 120
    
    # Calcul de distance
    dx = enemy_x - bullet_x
    dy = enemy_y - bullet_y
    distance = math.sqrt(dx*dx + dy*dy)
    
    bullet_radius = 3
    enemy_radius = 10
    collision_distance = bullet_radius + enemy_radius
    
    print(f"Bullet: ({bullet_x}, {bullet_y}), rayon={bullet_radius}")
    print(f"Ennemi: ({enemy_x}, {enemy_y}), rayon={enemy_radius}")
    print(f"Distance: {distance:.2f}")
    print(f"Distance collision: {collision_distance}")
    print(f"Collision: {'OUI' if distance < collision_distance else 'NON'}")

if __name__ == "__main__":
    test_shooting_system()
    test_collision_detection()
    print("\n🎯 Tests de logique terminés")