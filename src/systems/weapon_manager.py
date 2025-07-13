"""
Gestionnaire du système d'armes modulaire
Charge les configurations JSON et gère les armes
"""
import json
import os
import pygame
import math
from typing import Dict, List, Optional, Any
from ..entities.weapon_projectile import WeaponProjectile

class WeaponManager:
    """Gestionnaire principal du système d'armes"""
    
    def __init__(self):
        self.weapons = {}
        self.effects = {}
        
        # Chemin relatif depuis le dossier racine du projet
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        self.weapon_configs_path = os.path.join(project_root, "assets", "weapons")
        
        print(f"🔍 Recherche armes dans: {self.weapon_configs_path}")
        
        # Charger toutes les configurations
        self.load_all_configs()
    
    def load_all_configs(self):
        """Charge toutes les configurations d'armes et d'effets"""
        
        # Vérifier que le dossier existe
        if not os.path.exists(self.weapon_configs_path):
            print(f"❌ Dossier d'armes non trouvé: {self.weapon_configs_path}")
            self._load_fallback_config()
            return
        
        try:
            # Charger les effets d'abord
            effects_file = os.path.join(self.weapon_configs_path, "weapon_effects.json")
            if os.path.exists(effects_file):
                with open(effects_file, 'r', encoding='utf-8') as f:
                    self.effects = json.load(f)
                print(f"✅ Effets d'armes chargés: {len(self.effects)} catégories")
            else:
                print(f"⚠️  Fichier d'effets non trouvé: {effects_file}")
            
            # Charger tous les fichiers d'armes
            weapon_files = [
                "base_weapons.json",
                "special_weapons.json", 
                "holy_weapons.json",
                "chaos_weapons.json",
                "archetype_weapons.json"
            ]
            
            files_found = 0
            for weapon_file in weapon_files:
                file_path = os.path.join(self.weapon_configs_path, weapon_file)
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        weapons_data = json.load(f)
                        self.weapons.update(weapons_data)
                        print(f"✅ Armes chargées de {weapon_file}: {len(weapons_data)} armes")
                        files_found += 1
                else:
                    print(f"⚠️  Fichier d'armes non trouvé: {file_path}")
            
            if files_found == 0:
                print(f"❌ Aucun fichier d'armes trouvé dans {self.weapon_configs_path}")
                self._load_fallback_config()
            else:
                print(f"🔫 Total armes disponibles: {len(self.weapons)}")
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement des configurations: {e}")
            import traceback
            traceback.print_exc()
            self._load_fallback_config()
    
    def _load_fallback_config(self):
        """Charge une configuration de base en cas d'erreur"""
        print("🔧 Chargement de la configuration de fallback...")
        self.weapons = {
            "bolter_basic": {
                "name": "Bolter Standard",
                "description": "Arme de base",
                "type": "projectile", 
                "rarity": "common",
                "stats": {
                    "damage": 8,
                    "fire_rate": 10,
                    "projectile_speed": 8,
                    "accuracy": 0.95,
                    "reload_time": 0,
                    "ammo_capacity": -1,
                    "range": 800
                },
                "projectile": {
                    "size": 3,
                    "color": [255, 255, 0],
                    "sprite": None,
                    "trail": False,
                    "lifetime": 120
                },
                "effects": [],
                "sounds": {
                    "fire": "bolter_shot.wav",
                    "reload": None,
                    "empty": None
                },
                "upgrades": []
            }
        }
        self.effects = {}
        print(f"✅ Configuration de fallback chargée: {len(self.weapons)} arme(s)")
    
    def get_weapon(self, weapon_id: str) -> Optional[Dict]:
        """Récupère une configuration d'arme"""
        return self.weapons.get(weapon_id)
    
    def get_available_weapons(self, morality_system=None) -> List[str]:
        """Retourne la liste des armes disponibles selon la moralité"""
        available = []
        
        for weapon_id, weapon_data in self.weapons.items():
            if self.is_weapon_available(weapon_id, morality_system):
                available.append(weapon_id)
        
        return available
    
    def is_weapon_available(self, weapon_id: str, morality_system=None) -> bool:
        """Vérifie si une arme est disponible selon les prérequis de moralité"""
        weapon_data = self.weapons.get(weapon_id)
        if not weapon_data:
            return False
        
        # Si pas de système de moralité, toutes les armes sont disponibles
        if not morality_system:
            return True
        
        # Vérifier les prérequis de moralité
        requirements = weapon_data.get("morality_requirements", {})
        
        # Foi minimale requise
        if "min_faith" in requirements:
            if morality_system.faith < requirements["min_faith"]:
                return False
        
        # Foi maximale autorisée
        if "max_faith" in requirements:
            if morality_system.faith > requirements["max_faith"]:
                return False
        
        # Corruption minimale requise
        if "min_corruption" in requirements:
            if morality_system.corruption < requirements["min_corruption"]:
                return False
        
        # Corruption maximale autorisée
        if "max_corruption" in requirements:
            if morality_system.corruption > requirements["max_corruption"]:
                return False
        
        return True
    
    def create_projectiles(self, weapon_id: str, start_x: float, start_y: float, 
                          target_x: float, target_y: float, player=None) -> List[WeaponProjectile]:
        """Crée les projectiles pour une arme donnée"""
        weapon_data = self.get_weapon(weapon_id)
        if not weapon_data:
            print(f"❌ Arme inconnue: {weapon_id}")
            return []
        
        projectiles = []
        
        # Calculer la direction vers la cible
        dx = target_x - start_x
        dy = target_y - start_y
        length = math.sqrt(dx*dx + dy*dy)
        
        if length == 0:
            dx, dy = 1, 0  # Direction par défaut
        else:
            dx /= length
            dy /= length
        
        # Appliquer la précision de l'arme
        accuracy = weapon_data["stats"].get("accuracy", 1.0)
        if accuracy < 1.0:
            import random
            spread = (1.0 - accuracy) * 0.5  # Convertir en angle de dispersion
            angle_offset = random.uniform(-spread, spread)
            cos_offset = math.cos(angle_offset)
            sin_offset = math.sin(angle_offset)
            
            new_dx = dx * cos_offset - dy * sin_offset
            new_dy = dx * sin_offset + dy * cos_offset
            dx, dy = new_dx, new_dy
        
        # Déterminer le nombre de projectiles
        projectile_count = 1
        spread_angle = 0
        
        # Vérifier les effets de tir multiple de l'arme
        for effect_name in weapon_data.get("effects", []):
            if effect_name in ["multi_shot_2", "multi_shot_3"]:
                effect_data = self.get_effect_data("projectile_effects", effect_name)
                if effect_data:
                    projectile_count = effect_data["parameters"]["projectile_count"]
                    spread_angle = effect_data["parameters"]["spread_angle"]
        
        # Ajouter les projectiles bonus des améliorations globales
        if player and hasattr(player, 'global_upgrades'):
            bonus_projectiles = player.global_upgrades.get('multi_shot_bonus', 0)
            projectile_count += bonus_projectiles
            # Si on ajoute des projectiles bonus et qu'il n'y avait pas de spread, en ajouter un
            if bonus_projectiles > 0 and spread_angle == 0:
                spread_angle = 0.4  # Angle de dispersion par défaut pour les projectiles bonus
            if bonus_projectiles > 0:
                print(f"🚀 Projectiles bonus: {bonus_projectiles}, Total: {projectile_count}")
        
        # Créer les projectiles
        for i in range(projectile_count):
            # Calculer l'angle pour le spread
            if projectile_count > 1:
                # Répartir uniformément les projectiles autour de la direction centrale
                angle_offset = (i - (projectile_count - 1) / 2) * spread_angle
                cos_offset = math.cos(angle_offset)
                sin_offset = math.sin(angle_offset)
                
                proj_dx = dx * cos_offset - dy * sin_offset
                proj_dy = dx * sin_offset + dy * cos_offset
            else:
                proj_dx, proj_dy = dx, dy
            
            # Créer le projectile
            projectile = WeaponProjectile(
                x=start_x,
                y=start_y,
                dx=proj_dx,
                dy=proj_dy,
                weapon_data=weapon_data,
                effects_data=self.effects,
                owner=player
            )
            
            projectiles.append(projectile)
        
        return projectiles
    
    def get_effect_data(self, category: str, effect_name: str) -> Optional[Dict]:
        """Récupère les données d'un effet spécifique"""
        return self.effects.get(category, {}).get(effect_name)
    
    def get_weapon_upgrades(self, weapon_id: str) -> List[str]:
        """Retourne la liste des améliorations possibles pour une arme"""
        weapon_data = self.get_weapon(weapon_id)
        if weapon_data:
            return weapon_data.get("upgrades", [])
        return []
    
    def get_weapons_by_rarity(self, rarity: str) -> List[str]:
        """Retourne les armes d'une rareté donnée"""
        return [
            weapon_id for weapon_id, weapon_data in self.weapons.items()
            if weapon_data.get("rarity") == rarity
        ]
    
    def get_weapons_by_type(self, weapon_type: str) -> List[str]:
        """Retourne les armes d'un type donné"""
        return [
            weapon_id for weapon_id, weapon_data in self.weapons.items()
            if weapon_data.get("type") == weapon_type
        ]

class Weapon:
    """Classe représentant une arme équipée par le joueur"""
    
    def __init__(self, weapon_id: str, weapon_manager: WeaponManager):
        self.weapon_id = weapon_id
        self.weapon_manager = weapon_manager
        self.weapon_data = weapon_manager.get_weapon(weapon_id)
        
        if not self.weapon_data:
            raise ValueError(f"Arme inconnue: {weapon_id}")
        
        # État de l'arme
        self.current_ammo = self.weapon_data["stats"].get("ammo_capacity", -1)
        self.is_reloading = False
        self.reload_timer = 0
        self.fire_timer = 0
        self.overheat_timer = 0
        
        # Statistiques modifiées par les upgrades
        self.modified_stats = self.weapon_data["stats"].copy()
    
    def can_fire(self) -> bool:
        """Vérifie si l'arme peut tirer"""
        return (self.fire_timer <= 0 and 
                not self.is_reloading and 
                self.overheat_timer <= 0 and
                (self.current_ammo > 0 or self.current_ammo == -1))
    
    def fire(self, start_x: float, start_y: float, target_x: float, target_y: float, 
             player=None) -> List[WeaponProjectile]:
        """Tire avec l'arme"""
        if not self.can_fire():
            return []
        
        # Consommer les munitions
        if self.current_ammo > 0:
            self.current_ammo -= 1
            
            # Si munitions épuisées, déclencher rechargement automatique
            if self.current_ammo == 0 and self.weapon_data["stats"]["ammo_capacity"] > 0:
                print(f"🔄 Rechargement automatique de {self.weapon_data['name']}")
                self.start_reload()
        
        # Démarrer le timer de cadence
        self.fire_timer = self.modified_stats["fire_rate"]
        
        # Créer les projectiles
        projectiles = self.weapon_manager.create_projectiles(
            self.weapon_id, start_x, start_y, target_x, target_y, player
        )
        
        return projectiles
    
    def update(self):
        """Met à jour l'état de l'arme"""
        # Timer de cadence de tir
        if self.fire_timer > 0:
            self.fire_timer -= 1
        
        # Timer de rechargement
        if self.is_reloading:
            self.reload_timer -= 1
            if self.reload_timer <= 0:
                self.is_reloading = False
                self.current_ammo = self.weapon_data["stats"]["ammo_capacity"]
        
        # Timer de surchauffe
        if self.overheat_timer > 0:
            self.overheat_timer -= 1
    
    def start_reload(self):
        """Démarre le rechargement"""
        if (not self.is_reloading and 
            self.current_ammo != self.weapon_data["stats"]["ammo_capacity"] and
            self.weapon_data["stats"]["ammo_capacity"] > 0):
            self.is_reloading = True
            self.reload_timer = self.weapon_data["stats"]["reload_time"]
    
    def get_info(self) -> Dict[str, Any]:
        """Retourne les informations de l'arme"""
        return {
            "name": self.weapon_data["name"],
            "description": self.weapon_data["description"],
            "current_ammo": self.current_ammo,
            "max_ammo": self.weapon_data["stats"]["ammo_capacity"],
            "is_reloading": self.is_reloading,
            "reload_progress": 1.0 - (self.reload_timer / self.weapon_data["stats"]["reload_time"]) if self.is_reloading else 0,
            "can_fire": self.can_fire()
        }