"""
Gestionnaire d'entités - Centralise la gestion de toutes les entités du jeu
Remplace la gestion dispersée des listes d'entités dans main.py
"""

class EntityManager:
    """Gestionnaire centralisé de toutes les entités du jeu"""
    
    def __init__(self):
        # Entités principales
        self.player = None
        self.enemies = []
        self.projectiles = []
        self.items = []
        self.walls = []
        
        # Statistiques
        self.stats = {
            "enemies_total": 0,
            "projectiles_total": 0,
            "items_total": 0
        }
    
    # === PLAYER ===
    
    def add_player(self, player):
        """Définit le joueur principal"""
        self.player = player
        print(f"👤 Joueur ajouté: {player}")
    
    def get_player(self):
        """Retourne le joueur"""
        return self.player
    
    # === ENEMIES ===
    
    def add_enemy(self, enemy):
        """Ajoute un ennemi"""
        self.enemies.append(enemy)
        self.stats["enemies_total"] += 1
    
    def remove_enemy(self, enemy):
        """Supprime un ennemi"""
        if enemy in self.enemies:
            self.enemies.remove(enemy)
            return True
        return False
    
    def get_enemies(self):
        """Retourne la liste des ennemis"""
        return self.enemies
    
    def get_enemies_count(self):
        """Retourne le nombre d'ennemis vivants"""
        return len(self.enemies)
    
    def clear_enemies(self):
        """Supprime tous les ennemis"""
        count = len(self.enemies)
        self.enemies.clear()
        print(f"🧹 {count} ennemis supprimés")
    
    # === PROJECTILES ===
    
    def add_projectile(self, projectile):
        """Ajoute un projectile"""
        self.projectiles.append(projectile)
        self.stats["projectiles_total"] += 1
    
    def remove_projectile(self, projectile):
        """Supprime un projectile"""
        if projectile in self.projectiles:
            self.projectiles.remove(projectile)
            return True
        return False
    
    def get_projectiles(self):
        """Retourne la liste des projectiles"""
        return self.projectiles
    
    def get_projectiles_count(self):
        """Retourne le nombre de projectiles actifs"""
        return len(self.projectiles)
    
    def clear_projectiles(self):
        """Supprime tous les projectiles"""
        count = len(self.projectiles)
        self.projectiles.clear()
        print(f"🧹 {count} projectiles supprimés")
    
    # === ITEMS ===
    
    def add_item(self, item):
        """Ajoute un objet ramassable"""
        self.items.append(item)
        self.stats["items_total"] += 1
    
    def remove_item(self, item):
        """Supprime un objet"""
        if item in self.items:
            self.items.remove(item)
            return True
        return False
    
    def get_items(self):
        """Retourne la liste des objets"""
        return self.items
    
    def get_items_count(self):
        """Retourne le nombre d'objets sur le terrain"""
        return len(self.items)
    
    def clear_items(self):
        """Supprime tous les objets"""
        count = len(self.items)
        self.items.clear()
        print(f"🧹 {count} objets supprimés")
    
    # === WALLS ===
    
    def set_walls(self, walls):
        """Définit la liste des murs"""
        self.walls = walls
        print(f"🧱 {len(walls)} murs définis")
    
    def add_wall(self, wall):
        """Ajoute un mur"""
        self.walls.append(wall)
    
    def get_walls(self):
        """Retourne la liste des murs"""
        return self.walls
    
    def clear_walls(self):
        """Supprime tous les murs"""
        count = len(self.walls)
        self.walls.clear()
        print(f"🧹 {count} murs supprimés")
    
    # === UTILITAIRES ===
    
    def clear_all(self):
        """Supprime toutes les entités sauf le joueur"""
        self.clear_enemies()
        self.clear_projectiles()
        self.clear_items()
        self.clear_walls()
        print("🧹 Toutes les entités supprimées")
    
    def reset(self):
        """Remet à zéro toutes les entités y compris le joueur"""
        self.player = None
        self.clear_all()
        
        # Réinitialiser les stats
        self.stats = {
            "enemies_total": 0,
            "projectiles_total": 0,
            "items_total": 0
        }
        print("🔄 EntityManager réinitialisé")
    
    def get_statistics(self):
        """Retourne les statistiques complètes"""
        current_stats = {
            "player": 1 if self.player else 0,
            "enemies_current": len(self.enemies),
            "projectiles_current": len(self.projectiles),
            "items_current": len(self.items),
            "walls_current": len(self.walls),
        }
        return {**self.stats, **current_stats}
    
    def print_status(self):
        """Affiche l'état actuel du gestionnaire"""
        stats = self.get_statistics()
        print("📊 État EntityManager:")
        print(f"  👤 Joueur: {'Oui' if self.player else 'Non'}")
        print(f"  👹 Ennemis: {stats['enemies_current']}")
        print(f"  💥 Projectiles: {stats['projectiles_current']}")
        print(f"  📦 Objets: {stats['items_current']}")
        print(f"  🧱 Murs: {stats['walls_current']}")
        print(f"  📈 Total spawné: {stats['enemies_total']} ennemis, {stats['projectiles_total']} projectiles")
    
    def find_closest_enemy_to_player(self):
        """Trouve l'ennemi le plus proche du joueur"""
        if not self.player or not self.enemies:
            return None
        
        import math
        closest_enemy = None
        min_distance = float('inf')
        
        for enemy in self.enemies:
            distance = math.sqrt(
                (enemy.x - self.player.x)**2 + (enemy.y - self.player.y)**2
            )
            if distance < min_distance:
                min_distance = distance
                closest_enemy = enemy
        
        return closest_enemy
    
    def find_enemies_in_radius(self, x, y, radius):
        """Trouve tous les ennemis dans un rayon donné"""
        import math
        enemies_in_radius = []
        
        for enemy in self.enemies:
            distance = math.sqrt((enemy.x - x)**2 + (enemy.y - y)**2)
            if distance <= radius:
                enemies_in_radius.append(enemy)
        
        return enemies_in_radius
    
    def cleanup_dead_entities(self):
        """Nettoie automatiquement les entités mortes/invalides"""
        # Nettoyer les ennemis morts
        initial_enemies = len(self.enemies)
        self.enemies = [e for e in self.enemies if hasattr(e, 'health') and e.health > 0]
        
        # Nettoyer les projectiles hors limites ou invalides
        initial_projectiles = len(self.projectiles)
        from ..core.constants import WORLD_WIDTH, WORLD_HEIGHT
        self.projectiles = [p for p in self.projectiles 
                          if 0 <= p.x <= WORLD_WIDTH and 0 <= p.y <= WORLD_HEIGHT]
        
        cleaned_enemies = initial_enemies - len(self.enemies)
        cleaned_projectiles = initial_projectiles - len(self.projectiles)
        
        if cleaned_enemies > 0 or cleaned_projectiles > 0:
            print(f"🧹 Nettoyage: {cleaned_enemies} ennemis, {cleaned_projectiles} projectiles")