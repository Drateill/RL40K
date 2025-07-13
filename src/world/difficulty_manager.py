"""
Gestionnaire de difficulté pour équilibrer le jeu selon la progression
"""
import math

class DifficultyManager:
    """Gère l'augmentation de difficulté selon les vagues"""
    
    def __init__(self):
        self.base_difficulty = 1.0
        
    def get_enemy_health_multiplier(self, wave_number):
        """Calcule le multiplicateur de PV des ennemis"""
        # +12% de PV par vague
        return 1.0 + (wave_number * 0.12)
    
    def get_enemy_damage_multiplier(self, wave_number):
        """Calcule le multiplicateur de dégâts des ennemis"""
        # +8% de dégâts par vague
        return 1.0 + (wave_number * 0.08)
    
    def get_enemy_speed_multiplier(self, wave_number):
        """Calcule le multiplicateur de vitesse des ennemis"""
        # +5% de vitesse par vague (plafonné à +50%)
        return min(1.5, 1.0 + (wave_number * 0.05))
    
    def get_spawn_count_multiplier(self, wave_number):
        """Calcule le multiplicateur du nombre d'ennemis"""
        # Progression exponentielle lissée
        if wave_number <= 5:
            return 1.0
        elif wave_number <= 10:
            return 1.0 + ((wave_number - 5) * 0.2)  # +20% par vague
        elif wave_number <= 15:
            return 2.0 + ((wave_number - 10) * 0.3)  # +30% par vague
        else:
            return 3.5 + ((wave_number - 15) * 0.4)  # +40% par vague
    
    def get_boss_health_multiplier(self, wave_number):
        """Calcule le multiplicateur de PV des boss"""
        # Les boss deviennent significativement plus forts
        return 1.0 + (wave_number * 0.2)  # +20% de PV par vague
    
    def get_experience_penalty(self, player_level):
        """Calcule une pénalité d'XP pour les joueurs de haut niveau"""
        # Les joueurs forts gagnent moins d'XP par kill
        if player_level <= 5:
            return 1.0
        elif player_level <= 10:
            return 0.9  # -10% XP
        elif player_level <= 15:
            return 0.8  # -20% XP
        else:
            return 0.7  # -30% XP
    
    def should_spawn_elite_enemy(self, wave_number):
        """Détermine si des ennemis élite doivent apparaître"""
        if wave_number < 3:
            return False
        
        # Probabilité croissante d'ennemis élite
        elite_chance = min(0.4, (wave_number - 2) * 0.05)  # Max 40% de chance
        import random
        return random.random() < elite_chance
    
    def get_difficulty_description(self, wave_number):
        """Retourne une description de la difficulté actuelle"""
        if wave_number <= 3:
            return "🟢 Facile"
        elif wave_number <= 7:
            return "🟡 Modéré"
        elif wave_number <= 12:
            return "🟠 Difficile"
        elif wave_number <= 18:
            return "🔴 Très Difficile"
        else:
            return "⚫ Extrême"
    
    def apply_enemy_scaling(self, enemy, wave_number):
        """Applique le scaling de difficulté à un ennemi"""
        if hasattr(enemy, 'max_health'):
            enemy.max_health = int(enemy.max_health * self.get_enemy_health_multiplier(wave_number))
            enemy.health = enemy.max_health
        
        if hasattr(enemy, 'damage'):
            enemy.damage = int(enemy.damage * self.get_enemy_damage_multiplier(wave_number))
        
        if hasattr(enemy, 'speed'):
            enemy.speed = enemy.speed * self.get_enemy_speed_multiplier(wave_number)
        
        return enemy