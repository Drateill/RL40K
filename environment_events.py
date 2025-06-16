"""
Système d'événements spéciaux et d'effets environnementaux
Crée des événements dynamiques qui transforment l'expérience de jeu
"""

import pygame
import random
import math
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from environment_system import EnvironmentType

class EventType(Enum):
    """Types d'événements environnementaux"""
    # Événements du vaisseau
    SHIP_ALARM = "ship_alarm"
    POWER_OUTAGE = "power_outage"
    HULL_BREACH = "hull_breach"
    REACTOR_OVERLOAD = "reactor_overload"
    
    # Événements du temple
    DIVINE_BLESSING = "divine_blessing"
    HOLY_CHOIR = "holy_choir"
    HERETIC_INTRUSION = "heretic_intrusion"
    RELIC_ACTIVATION = "relic_activation"
    
    # Événements de la forge
    MACHINE_MALFUNCTION = "machine_malfunction"
    TOXIC_LEAK = "toxic_leak"
    PRODUCTION_BOOST = "production_boost"
    SERVITOR_REBELLION = "servitor_rebellion"
    
    # Événements du chaos
    WARP_STORM = "warp_storm"
    REALITY_DISTORTION = "reality_distortion"
    DAEMON_MANIFESTATION = "daemon_manifestation"
    CHAOS_SURGE = "chaos_surge"
    
    # Événements du monde de la mort
    TOXIC_RAIN = "toxic_rain"
    PREDATOR_HUNT = "predator_hunt"
    SEISMIC_ACTIVITY = "seismic_activity"
    DEADLY_SPORES = "deadly_spores"

@dataclass
class EnvironmentEvent:
    """Définition d'un événement environnemental"""
    event_type: EventType
    name: str
    description: str
    duration: int  # En frames (60 = 1 seconde)
    trigger_chance: float  # Probabilité par frame
    effects: Dict[str, Any]
    visual_effects: List[str]
    sound_effects: List[str]
    
    # Conditions
    min_wave: int = 1
    max_wave: int = 999
    morality_condition: Optional[Tuple[str, int]] = None  # ("faith", 50) ou ("corruption", 30)

class EnvironmentEffectManager:
    """Gestionnaire des effets environnementaux actifs"""
    
    def __init__(self):
        self.active_effects: List[Dict[str, Any]] = []
        self.event_timer = 0
        self.last_event_time = 0
        self.min_event_interval = 600  # 10 secondes minimum entre événements
        
        # Particules d'effets
        self.effect_particles: List[Dict[str, Any]] = []
        
        # Configuration des événements par environnement
        self.environment_events = {
            EnvironmentType.SHIP: self._create_ship_events(),
            EnvironmentType.TEMPLE: self._create_temple_events(),
            EnvironmentType.FORGE: self._create_forge_events(),
            EnvironmentType.CHAOS: self._create_chaos_events(),
            EnvironmentType.DEATH_WORLD: self._create_death_world_events()
        }
    
    def _create_ship_events(self) -> List[EnvironmentEvent]:
        """Événements pour le vaisseau spatial"""
        return [
            EnvironmentEvent(
                EventType.SHIP_ALARM,
                "Alerte Rouge",
                "Alerte générale ! Tous aux postes de combat !",
                duration=300,  # 5 secondes
                trigger_chance=0.0008,
                effects={
                    "speed_boost": 1.3,
                    "damage_boost": 1.2,
                    "stress": 5
                },
                visual_effects=["red_flash", "alarm_lights"],
                sound_effects=["alarm_klaxon", "ship_alert"]
            ),
            
            EnvironmentEvent(
                EventType.POWER_OUTAGE,
                "Panne de Courant",
                "Les lumières s'éteignent... Visibilité réduite.",
                duration=480,  # 8 secondes
                trigger_chance=0.0005,
                effects={
                    "visibility_range": 0.6,
                    "enemy_spawn_rate": 0.8
                },
                visual_effects=["darkness_overlay", "emergency_lighting"],
                sound_effects=["power_down", "electrical_buzz"]
            ),
            
            EnvironmentEvent(
                EventType.HULL_BREACH,
                "Brèche dans la Coque",
                "Dépressurisation ! L'air s'échappe !",
                duration=360,  # 6 secondes
                trigger_chance=0.0003,
                effects={
                    "wind_force": {"x": 2, "y": 0},
                    "health_drain": 1  # 1 PV par seconde
                },
                visual_effects=["wind_particles", "debris_flying"],
                sound_effects=["wind_rush", "hull_stress"],
                min_wave=3
            ),
            
            EnvironmentEvent(
                EventType.REACTOR_OVERLOAD,
                "Surcharge du Réacteur",
                "Le réacteur surchauffe ! Danger d'explosion !",
                duration=600,  # 10 secondes
                trigger_chance=0.0002,
                effects={
                    "random_explosions": True,
                    "fire_rate_boost": 1.5,
                    "screen_shake": 3
                },
                visual_effects=["reactor_glow", "heat_distortion", "sparks"],
                sound_effects=["reactor_alarm", "energy_buildup"],
                min_wave=5
            )
        ]
    
    def _create_temple_events(self) -> List[EnvironmentEvent]:
        """Événements pour le temple impérial"""
        return [
            EnvironmentEvent(
                EventType.DIVINE_BLESSING,
                "Bénédiction Divine",
                "L'Empereur guide vos pas ! Ses fidèles sont bénis.",
                duration=450,  # 7.5 secondes
                trigger_chance=0.0006,
                effects={
                    "damage_boost": 1.4,
                    "health_regen": 2,
                    "holy_bullets": True
                },
                visual_effects=["golden_light", "holy_aura"],
                sound_effects=["choir_chanting", "divine_blessing"],
                morality_condition=("faith", 40)
            ),
            
            EnvironmentEvent(
                EventType.HOLY_CHOIR,
                "Chœur Sacré",
                "Les voix des saints résonnent dans le temple.",
                duration=720,  # 12 secondes
                trigger_chance=0.0004,
                effects={
                    "morale_boost": 10,
                    "corruption_resist": 0.5,
                    "speed_boost": 1.2
                },
                visual_effects=["light_rays", "floating_notes"],
                sound_effects=["holy_choir", "sacred_hymn"],
                morality_condition=("faith", 20)
            ),
            
            EnvironmentEvent(
                EventType.HERETIC_INTRUSION,
                "Intrusion Hérétique",
                "Des hérétiques profanent le lieu saint !",
                duration=540,  # 9 secondes
                trigger_chance=0.0005,
                effects={
                    "enemy_spawn_boost": 1.5,
                    "corruption_aura": 2,
                    "desecration": True
                },
                visual_effects=["dark_smoke", "corruption_tendrils"],
                sound_effects=["heretic_chants", "corruption_whispers"],
                min_wave=4
            ),
            
            EnvironmentEvent(
                EventType.RELIC_ACTIVATION,
                "Activation de Relique",
                "Une relique sacrée s'active ! Puissance divine !",
                duration=600,  # 10 secondes
                trigger_chance=0.0003,
                effects={
                    "mass_heal": 30,
                    "faith_boost": 15,
                    "enemy_fear": True,
                    "invulnerability": 60  # 1 seconde d'invulnérabilité
                },
                visual_effects=["relic_glow", "divine_explosion"],
                sound_effects=["relic_activation", "divine_power"],
                morality_condition=("faith", 60),
                min_wave=6
            )
        ]
    
    def _create_forge_events(self) -> List[EnvironmentEvent]:
        """Événements pour la forge world"""
        return [
            EnvironmentEvent(
                EventType.MACHINE_MALFUNCTION,
                "Dysfonctionnement Machine",
                "Les machines deviennent imprévisibles !",
                duration=420,  # 7 secondes
                trigger_chance=0.0007,
                effects={
                    "random_obstacles": True,
                    "movement_hazards": True,
                    "electric_damage": 5
                },
                visual_effects=["sparks_shower", "smoke_clouds"],
                sound_effects=["machine_error", "electrical_discharge"]
            ),
            
            EnvironmentEvent(
                EventType.TOXIC_LEAK,
                "Fuite Toxique",
                "Produits chimiques toxiques se répandent !",
                duration=600,  # 10 secondes
                trigger_chance=0.0004,
                effects={
                    "poison_zones": True,
                    "health_drain": 2,
                    "vision_impair": 0.8
                },
                visual_effects=["toxic_clouds", "green_mist"],
                sound_effects=["gas_leak", "chemical_hiss"]
            ),
            
            EnvironmentEvent(
                EventType.PRODUCTION_BOOST,
                "Boost de Production",
                "Les machines fonctionnent à plein régime !",
                duration=480,  # 8 secondes
                trigger_chance=0.0005,
                effects={
                    "item_spawn_rate": 2.0,
                    "machine_efficiency": 1.5,
                    "exp_boost": 1.3
                },
                visual_effects=["efficiency_glow", "production_sparks"],
                sound_effects=["machines_accelerate", "production_hum"]
            ),
            
            EnvironmentEvent(
                EventType.SERVITOR_REBELLION,
                "Rébellion de Serviteurs",
                "Les serviteurs se retournent contre leurs maîtres !",
                duration=720,  # 12 secondes
                trigger_chance=0.0002,
                effects={
                    "friendly_fire": True,
                    "servitor_enemies": 3,
                    "chaos_factor": 1.2
                },
                visual_effects=["red_eyes", "servitor_sparks"],
                sound_effects=["servitor_malfunction", "rebellion_sounds"],
                min_wave=8
            )
        ]
    
    def _create_chaos_events(self) -> List[EnvironmentEvent]:
        """Événements pour le monde corrompu"""
        return [
            EnvironmentEvent(
                EventType.WARP_STORM,
                "Tempête Warp",
                "Le Warp se déchaîne ! La réalité se distord !",
                duration=540,  # 9 secondes
                trigger_chance=0.0004,
                effects={
                    "reality_distortion": True,
                    "random_teleports": True,
                    "warp_damage": 8,
                    "corruption_boost": 5
                },
                visual_effects=["warp_lightning", "reality_tears", "chaos_swirls"],
                sound_effects=["warp_storm", "reality_rip"]
            ),
            
            EnvironmentEvent(
                EventType.REALITY_DISTORTION,
                "Distorsion de Réalité",
                "L'espace et le temps se mélangent...",
                duration=360,  # 6 secondes
                trigger_chance=0.0006,
                effects={
                    "gravity_change": {"strength": 0.5, "direction": "random"},
                    "time_dilation": 1.3,
                    "space_warp": True
                },
                visual_effects=["space_distortion", "time_ripples"],
                sound_effects=["reality_distort", "time_echo"]
            ),
            
            EnvironmentEvent(
                EventType.DAEMON_MANIFESTATION,
                "Manifestation Démoniaque",
                "Des démons émergent du Warp !",
                duration=600,  # 10 secondes
                trigger_chance=0.0003,
                effects={
                    "daemon_spawn": 2,
                    "corruption_aura": 3,
                    "fear_effect": True
                },
                visual_effects=["daemon_portals", "warp_energy"],
                sound_effects=["daemon_roar", "warp_tear"],
                min_wave=5
            ),
            
            EnvironmentEvent(
                EventType.CHAOS_SURGE,
                "Déferlante Chaotique",
                "Le Chaos vous emporte dans sa folie !",
                duration=480,  # 8 secondes
                trigger_chance=0.0005,
                effects={
                    "chaos_power": True,
                    "random_effects": True,
                    "corruption_boost": 8,
                    "damage_boost": 1.6
                },
                visual_effects=["chaos_explosion", "color_shift"],
                sound_effects=["chaos_surge", "madness_whispers"],
                morality_condition=("corruption", 30)
            )
        ]
    
    def _create_death_world_events(self) -> List[EnvironmentEvent]:
        """Événements pour le monde de la mort"""
        return [
            EnvironmentEvent(
                EventType.TOXIC_RAIN,
                "Pluie Toxique",
                "Une pluie acide tombe du ciel !",
                duration=720,  # 12 secondes
                trigger_chance=0.0005,
                effects={
                    "acid_damage": 3,
                    "equipment_damage": True,
                    "visibility_reduce": 0.7
                },
                visual_effects=["acid_drops", "corrosion_effects"],
                sound_effects=["acid_rain", "corrosion_sizzle"]
            ),
            
            EnvironmentEvent(
                EventType.PREDATOR_HUNT,
                "Chasse de Prédateurs",
                "Des prédateurs vous traquent !",
                duration=600,  # 10 secondes
                trigger_chance=0.0004,
                effects={
                    "predator_spawn": 1,
                    "stealth_enemies": True,
                    "hunt_pressure": 1.3
                },
                visual_effects=["predator_eyes", "stalking_shadows"],
                sound_effects=["predator_growl", "hunt_music"],
                min_wave=3
            ),
            
            EnvironmentEvent(
                EventType.SEISMIC_ACTIVITY,
                "Activité Sismique",
                "Le sol tremble ! Attention aux chutes !",
                duration=480,  # 8 seconds
                trigger_chance=0.0006,
                effects={
                    "screen_shake": 5,
                    "falling_rocks": True,
                    "terrain_change": True
                },
                visual_effects=["ground_cracks", "falling_debris"],
                sound_effects=["earthquake", "rocks_falling"]
            ),
            
            EnvironmentEvent(
                EventType.DEADLY_SPORES,
                "Spores Mortelles",
                "Des spores toxiques envahissent l'air !",
                duration=540,  # 9 secondes
                trigger_chance=0.0007,
                effects={
                    "poison_air": True,
                    "health_drain": 4,
                    "hallucinations": True
                },
                visual_effects=["spore_clouds", "toxic_fog"],
                sound_effects=["spore_release", "toxic_wind"]
            )
        ]
    
    def update(self, environment_type: EnvironmentType, wave_number: int, 
              morality_system=None):
        """Met à jour les événements environnementaux"""
        self.event_timer += 1
        
        # Mise à jour des effets actifs
        self._update_active_effects()
        
        # Mise à jour des particules
        self._update_effect_particles()
        
        # Vérifier si on peut déclencher un nouvel événement
        if (self.event_timer - self.last_event_time > self.min_event_interval and
            environment_type in self.environment_events):
            
            self._check_event_triggers(environment_type, wave_number, morality_system)
    
    def _update_active_effects(self):
        """Met à jour les effets actifs"""
        active_effects = []
        
        for effect in self.active_effects:
            effect['remaining_duration'] -= 1
            
            if effect['remaining_duration'] > 0:
                active_effects.append(effect)
            else:
                # Effet terminé
                print(f"Événement '{effect['event'].name}' terminé")
        
        self.active_effects = active_effects
    
    def _update_effect_particles(self):
        """Met à jour les particules d'effets"""
        active_particles = []
        
        for particle in self.effect_particles:
            particle['life'] -= 1
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            
            # Appliquer la gravité si nécessaire
            if particle.get('gravity', False):
                particle['vy'] += 0.1
            
            if particle['life'] > 0:
                active_particles.append(particle)
        
        self.effect_particles = active_particles
    
    def _check_event_triggers(self, environment_type: EnvironmentType, 
                            wave_number: int, morality_system=None):
        """Vérifie et déclenche les événements"""
        if environment_type not in self.environment_events:
            return
        
        events = self.environment_events[environment_type]
        
        for event in events:
            # Vérifier les conditions
            if not self._check_event_conditions(event, wave_number, morality_system):
                continue
            
            # Vérifier la probabilité
            if random.random() < event.trigger_chance:
                self.trigger_event(event)
                break  # Un seul événement à la fois
    
    def _check_event_conditions(self, event: EnvironmentEvent, 
                               wave_number: int, morality_system=None) -> bool:
        """Vérifie si les conditions d'un événement sont remplies"""
        # Vérifier la vague
        if wave_number < event.min_wave or wave_number > event.max_wave:
            return False
        
        # Vérifier la condition de moralité
        if event.morality_condition and morality_system:
            moral_type, min_value = event.morality_condition
            current_value = getattr(morality_system, moral_type, 0)
            if current_value < min_value:
                return False
        
        # Vérifier qu'il n'y a pas déjà un événement de ce type actif
        for active_effect in self.active_effects:
            if active_effect['event'].event_type == event.event_type:
                return False
        
        return True
    
    def trigger_event(self, event: EnvironmentEvent):
        """Déclenche un événement"""
        print(f"🌍 ÉVÉNEMENT: {event.name}")
        print(f"   {event.description}")
        
        # Ajouter l'effet actif
        self.active_effects.append({
            'event': event,
            'remaining_duration': event.duration,
            'effects': event.effects.copy()
        })
        
        # Générer les particules visuelles
        self._spawn_event_particles(event)
        
        # Marquer le temps du dernier événement
        self.last_event_time = self.event_timer
    
    def _spawn_event_particles(self, event: EnvironmentEvent):
        """Génère les particules visuelles pour un événement"""
        particle_count = 20
        
        for visual_effect in event.visual_effects:
            if visual_effect == "red_flash":
                # Flash rouge d'alarme
                for _ in range(5):
                    self.effect_particles.append({
                        'type': 'flash',
                        'x': random.randint(0, 1024),
                        'y': random.randint(0, 768),
                        'vx': 0,
                        'vy': 0,
                        'life': 30,
                        'color': (255, 0, 0),
                        'size': random.randint(20, 40),
                        'alpha': 200
                    })
            
            elif visual_effect == "sparks_shower":
                # Pluie d'étincelles
                for _ in range(particle_count):
                    self.effect_particles.append({
                        'type': 'spark',
                        'x': random.randint(0, 1024),
                        'y': random.randint(0, 200),
                        'vx': random.uniform(-2, 2),
                        'vy': random.uniform(1, 4),
                        'life': random.randint(60, 120),
                        'color': (255, 200, 50),
                        'size': random.randint(2, 5),
                        'gravity': True
                    })
            
            elif visual_effect == "golden_light":
                # Lumière dorée divine
                for _ in range(15):
                    self.effect_particles.append({
                        'type': 'divine',
                        'x': random.randint(0, 1024),
                        'y': random.randint(0, 768),
                        'vx': random.uniform(-1, 1),
                        'vy': random.uniform(-2, -0.5),
                        'life': random.randint(120, 180),
                        'color': (255, 215, 0),
                        'size': random.randint(8, 15),
                        'alpha': 150
                    })
            
            elif visual_effect == "toxic_clouds":
                # Nuages toxiques
                for _ in range(12):
                    self.effect_particles.append({
                        'type': 'toxic',
                        'x': random.randint(0, 1024),
                        'y': random.randint(400, 768),
                        'vx': random.uniform(-0.5, 0.5),
                        'vy': random.uniform(-1, 0),
                        'life': random.randint(180, 300),
                        'color': (100, 200, 100),
                        'size': random.randint(25, 50),
                        'alpha': 100
                    })
            
            elif visual_effect == "warp_lightning":
                # Éclairs du Warp
                for _ in range(8):
                    self.effect_particles.append({
                        'type': 'lightning',
                        'x': random.randint(0, 1024),
                        'y': random.randint(0, 768),
                        'vx': random.uniform(-3, 3),
                        'vy': random.uniform(-3, 3),
                        'life': random.randint(30, 60),
                        'color': (200, 0, 200),
                        'size': random.randint(3, 8),
                        'alpha': 255
                    })
    
    def get_active_effects(self) -> Dict[str, Any]:
        """Retourne les effets actifs compilés"""
        compiled_effects = {}
        
        for active_effect in self.active_effects:
            for effect_name, effect_value in active_effect['effects'].items():
                if effect_name in compiled_effects:
                    # Combiner les effets (multiplication pour les boosts, addition pour les autres)
                    if isinstance(effect_value, (int, float)) and effect_name.endswith('_boost'):
                        compiled_effects[effect_name] *= effect_value
                    else:
                        compiled_effects[effect_name] = effect_value
                else:
                    compiled_effects[effect_name] = effect_value
        
        return compiled_effects
    
    def apply_effects_to_player(self, player, morality_system=None):
        """Applique les effets actifs au joueur"""
        effects = self.get_active_effects()
        
        # Boosts de vitesse
        if 'speed_boost' in effects:
            player.morality_speed_modifier *= effects['speed_boost']
        
        # Boosts de dégâts
        if 'damage_boost' in effects:
            # Appliquer temporairement (sera réinitialisé à chaque frame)
            player.base_damage = int(player.base_damage * effects['damage_boost'])
        
        # Régénération de santé
        if 'health_regen' in effects:
            if player.health < player.max_health:
                player.health += effects['health_regen'] / 60  # Par seconde
                player.health = min(player.health, player.max_health)
        
        # Drain de santé
        if 'health_drain' in effects:
            player.health -= effects['health_drain'] / 60
            player.health = max(1, player.health)  # Ne peut pas mourir des effets d'environnement
        
        # Guérison massive
        if 'mass_heal' in effects:
            heal_amount = min(effects['mass_heal'], player.max_health - player.health)
            player.health += heal_amount
            print(f"Guérison divine ! +{heal_amount} PV")
        
        # Boosts de moralité
        if morality_system:
            if 'faith_boost' in effects:
                morality_system.add_faith(effects['faith_boost'], "Événement environnemental")
            if 'corruption_boost' in effects:
                morality_system.add_corruption(effects['corruption_boost'], "Événement environnemental")
    
    def draw_effect_particles(self, screen: pygame.Surface):
        """Dessine les particules d'effets"""
        for particle in self.effect_particles:
            # Calculer l'alpha selon la vie restante
            alpha_ratio = particle['life'] / 120  # Assuming max life of 120
            alpha = int(particle.get('alpha', 255) * min(1.0, alpha_ratio))
            
            # Créer une surface avec alpha
            particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2))
            particle_surface.set_alpha(alpha)
            
            if particle['type'] == 'flash':
                # Flash rectangulaire
                pygame.draw.rect(particle_surface, particle['color'],
                               (0, 0, particle['size'] * 2, particle['size'] * 2))
            else:
                # Particule circulaire
                pygame.draw.circle(particle_surface, particle['color'],
                                 (particle['size'], particle['size']), particle['size'])
            
            screen.blit(particle_surface,
                       (particle['x'] - particle['size'], particle['y'] - particle['size']))
    
    def draw_active_effects_ui(self, screen: pygame.Surface):
        """Dessine l'interface des effets actifs"""
        if not self.active_effects:
            return
        
        font = pygame.font.Font(None, 24)
        y_offset = 10
        
        for i, active_effect in enumerate(self.active_effects):
            event = active_effect['event']
            remaining = active_effect['remaining_duration']
            
            # Couleur selon le type d'événement
            color = (255, 255, 255)
            if event.event_type.value.startswith('ship'):
                color = (0, 150, 255)
            elif event.event_type.value.startswith('divine') or 'blessing' in event.event_type.value:
                color = (255, 215, 0)
            elif 'chaos' in event.event_type.value or 'warp' in event.event_type.value:
                color = (255, 0, 255)
            elif 'toxic' in event.event_type.value or 'death' in event.event_type.value:
                color = (100, 255, 100)
            
            # Texte de l'événement
            time_left = remaining // 60 + 1  # Convertir en secondes
            event_text = font.render(f"{event.name} ({time_left}s)", True, color)
            
            # Fond semi-transparent
            text_rect = event_text.get_rect()
            bg_rect = text_rect.inflate(10, 4)
            bg_rect.topleft = (10, y_offset)
            
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
            bg_surface.set_alpha(150)
            bg_surface.fill((0, 0, 0))
            screen.blit(bg_surface, bg_rect)
            
            # Texte
            screen.blit(event_text, (15, y_offset + 2))
            
            y_offset += 30
    
    def force_event(self, event_type: EventType, environment_type: EnvironmentType):
        """Force un événement spécifique (pour testing)"""
        if environment_type not in self.environment_events:
            return False
        
        for event in self.environment_events[environment_type]:
            if event.event_type == event_type:
                self.trigger_event(event)
                return True
        
        return False
    
    def clear_all_effects(self):
        """Supprime tous les effets actifs"""
        self.active_effects.clear()
        self.effect_particles.clear()
        print("Tous les effets environnementaux ont été supprimés")
    
    def get_environment_status(self) -> str:
        """Retourne le statut actuel de l'environnement"""
        if not self.active_effects:
            return "Stable"
        
        # Déterminer le niveau de danger
        danger_level = 0
        active_names = []
        
        for active_effect in self.active_effects:
            active_names.append(active_effect['event'].name)
            
            # Calculer le niveau de danger
            effects = active_effect['effects']
            if any(key in effects for key in ['health_drain', 'warp_damage', 'acid_damage']):
                danger_level += 2
            if any(key in effects for key in ['damage_boost', 'speed_boost']):
                danger_level -= 1  # Les boosts réduisent le danger perçu
        
        # Retourner le statut
        if danger_level >= 4:
            return f"CRITIQUE - {', '.join(active_names[:2])}"
        elif danger_level >= 2:
            return f"Dangereux - {', '.join(active_names[:2])}"
        elif danger_level <= -2:
            return f"Béni - {', '.join(active_names[:2])}"
        else:
            return f"Actif - {', '.join(active_names[:2])}"