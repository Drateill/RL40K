"""
Gestionnaire des archétypes de personnages
Chaque archétype a une arme unique et des caractéristiques spécialisées
"""
from typing import Dict, Optional
from ..systems.weapon_manager import WeaponManager, Weapon

class ArchetypeManager:
    """Gestionnaire des archétypes de personnages"""
    
    def __init__(self):
        self.archetypes = {
            "pyromancer": {
                "name": "Pyromancien",
                "description": "Spécialiste des armes incendiaires",
                "weapon_id": "flamer_archetype",
                "stats_modifiers": {
                    "max_health": 90,  # Moins de vie
                    "speed": 4,        # Plus lent 
                    "damage_bonus": 5, # Plus de dégâts
                    "fire_resistance": 0.5  # Résistance au feu
                },
                "special_abilities": ["flame_immunity", "burn_spread"],
                "starting_upgrades": {
                    "damage_bonus": 3,
                    "bullet_size_multiplier": 1.2
                },
                "icon_color": (255, 100, 0),  # Orange
                "background_story": "Maître des flammes purificatrices, le Pyromancien incinère les hérétiques."
            },
            
            "marksman": {
                "name": "Tireur d'Élite", 
                "description": "Expert en armes de précision",
                "weapon_id": "laser_pistol_archetype",
                "stats_modifiers": {
                    "max_health": 70,  # Moins de vie
                    "speed": 6,        # Plus rapide
                    "accuracy_bonus": 0.1,  # Plus précis
                    "crit_chance": 0.15  # Chances de critique
                },
                "special_abilities": ["precision_shot", "weak_spot_targeting"],
                "starting_upgrades": {
                    "accuracy_bonus": 0.05,
                    "fire_rate_multiplier": 0.9
                },
                "icon_color": (255, 50, 50),  # Rouge laser
                "background_story": "Tireur d'élite de l'Astra Militarum, chaque tir compte."
            },
            
            "assault": {
                "name": "Assaut",
                "description": "Guerrier de corps à corps",
                "weapon_id": "chainsword_archetype", 
                "stats_modifiers": {
                    "max_health": 120,  # Plus de vie
                    "speed": 7,         # Très rapide
                    "melee_damage": 10, # Bonus mêlée
                    "armor": 2          # Armure naturelle
                },
                "special_abilities": ["charge_attack", "berserker_rage"],
                "starting_upgrades": {
                    "damage_bonus": 8,
                    "speed_bonus": 2
                },
                "icon_color": (200, 200, 200),  # Gris métal
                "background_story": "Guerrier proche combat, la chainsword rugit pour l'Empereur."
            }
        }
    
    def get_archetype(self, archetype_id: str) -> Optional[Dict]:
        """Récupère les données d'un archétype"""
        return self.archetypes.get(archetype_id)
    
    def get_all_archetypes(self) -> Dict:
        """Retourne tous les archétypes disponibles"""
        return self.archetypes
    
    def apply_archetype_to_player(self, player, archetype_id: str, weapon_manager: WeaponManager):
        """Applique un archétype à un joueur"""
        archetype = self.get_archetype(archetype_id)
        if not archetype:
            print(f"❌ Archétype {archetype_id} non trouvé")
            return False
        
        # Appliquer les modificateurs de stats
        stats_mods = archetype["stats_modifiers"]
        
        if "max_health" in stats_mods:
            player.max_health = stats_mods["max_health"]
            player.health = player.max_health  # Heal à max
            player.base_max_health = player.max_health
            
        if "speed" in stats_mods:
            player.speed = stats_mods["speed"]
            
        # Appliquer les améliorations de départ
        starting_upgrades = archetype.get("starting_upgrades", {})
        for upgrade_type, value in starting_upgrades.items():
            if hasattr(player, 'apply_global_upgrade'):
                player.apply_global_upgrade(upgrade_type, value)
        
        # Remplacer l'arme de base par l'arme d'archétype
        weapon_id = archetype["weapon_id"]
        try:
            # Supprimer l'arme de base
            player.weapons.clear()
            player.obtained_weapon_ids.clear()
            
            # Ajouter l'arme d'archétype
            archetype_weapon = Weapon(weapon_id, weapon_manager)
            player.weapons.append(archetype_weapon)
            player.obtained_weapon_ids.add(weapon_id)
            player.current_weapon_index = 0
            player.current_weapon = archetype_weapon
            
            # Appliquer les améliorations globales à la nouvelle arme
            if hasattr(player, '_apply_global_upgrades_to_weapon'):
                player._apply_global_upgrades_to_weapon(archetype_weapon)
            
            print(f"🎭 Archétype {archetype['name']} appliqué avec succès !")
            print(f"🔫 Arme : {archetype_weapon.weapon_data['name']}")
            print(f"❤️  Vie : {player.max_health}")
            print(f"🏃 Vitesse : {player.speed}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'application de l'archétype : {e}")
            return False
    
    def get_archetype_weapon_upgrades(self, archetype_id: str) -> list:
        """Retourne les améliorations d'armes disponibles pour un archétype"""
        archetype = self.get_archetype(archetype_id)
        if not archetype:
            return []
        
        # Retourner des améliorations spécialisées selon l'archétype
        if archetype_id == "pyromancer":
            return [
                "global_explosive", "global_damage_boost", "flame_damage_boost",
                "area_damage_boost", "burn_duration_boost"
            ]
        elif archetype_id == "marksman":
            return [
                "global_piercing", "global_damage_boost", "precision_boost", 
                "critical_chance_boost", "reload_speed_boost"
            ]
        elif archetype_id == "assault":
            return [
                "global_multi_shot", "global_damage_boost", "speed_boost",
                "armor_boost", "rage_boost"
            ]
        
        return []