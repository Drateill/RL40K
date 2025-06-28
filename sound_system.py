import pygame
import math
import random
from enum import Enum
import os

class SoundEvent(Enum):
    """Énumération des événements sonores du jeu"""
    
    # === COMBAT ===
    PLAYER_SHOOT = "player_shoot"
    PLAYER_SHOOT_HOLY = "player_shoot_holy"
    PLAYER_SHOOT_CHAOS = "player_shoot_chaos"
    ENEMY_SHOOT = "enemy_shoot"
    BULLET_HIT = "bullet_hit"
    EXPLOSION = "explosion"
    
    # === ENNEMIS ===
    ENEMY_DEATH = "enemy_death"
    ENEMY_DEATH_DAEMON = "enemy_death_daemon"
    CULTIST_SUMMON = "cultist_summon"
    DAEMON_TELEPORT = "daemon_teleport"
    
    # === BOSS ===
    BOSS_SPAWN = "boss_spawn"
    BOSS_DEATH = "boss_death"
    BOSS_PHASE_CHANGE = "boss_phase_change"
    SORCERER_AREA_EXPLODE = "sorcerer_area_explode"
    INQUISITOR_PURIFICATION = "inquisitor_purification"
    DAEMON_PRINCE_WARP_STORM = "daemon_prince_warp_storm"
    
    # === JOUEUR ===
    PLAYER_DAMAGE = "player_damage"
    PLAYER_LEVEL_UP = "player_level_up"
    ITEM_PICKUP = "item_pickup"
    
    # === UI ===
    MENU_NAVIGATE = "menu_navigate"
    MENU_SELECT = "menu_select"
    WAVE_START = "wave_start"
    WAVE_COMPLETE = "wave_complete"
    
    # === MORALITÉ ===
    FAITH_GAIN = "faith_gain"
    CORRUPTION_GAIN = "corruption_gain"

class SoundPriority(Enum):
    """Priorités des sons pour la gestion des canaux"""
    LOW = 1        # Sons peu importants (impacts, tirs fréquents)
    MEDIUM = 2     # Sons moyens (morts d'ennemis)
    HIGH = 3       # Sons importants (boss, level-up)
    CRITICAL = 4   # Sons critiques (ne jamais interrompre)

class SimpleSoundGenerator:
    """Générateur de sons simple utilisant uniquement pygame de base"""
    
    def __init__(self, sample_rate=22050):
        self.sample_rate = sample_rate
        self.sounds_created = 0
    
    def create_beep(self, frequency=440, duration=100):
        """Crée un beep simple - retourne pygame.Sound ou None"""
        try:
            # Méthode 1: Essayer avec sndarray si disponible
            return self._create_with_sndarray(frequency, duration)
        except:
            try:
                # Méthode 2: Créer un son basique avec bytes
                return self._create_with_bytes(frequency, duration)
            except:
                try:
                    # Méthode 3: Utiliser un son minimal
                    return self._create_minimal_sound(duration)
                except:
                    # Fallback: retourner None
                    return None
    
    def _create_with_sndarray(self, frequency, duration):
        """Méthode avec sndarray (nécessite numpy)"""
        import pygame.sndarray
        import array
        
        frames = int(duration * self.sample_rate / 1000)
        arr = []
        
        for frame in range(frames):
            time = frame / self.sample_rate
            wave = int(4096 * math.sin(2 * math.pi * frequency * time))
            arr.append([wave, wave])
        
        sound = pygame.sndarray.make_sound(array.array('h', [item for sublist in arr for item in sublist]))
        self.sounds_created += 1
        return sound
    
    def _create_with_bytes(self, frequency, duration):
        """Méthode avec bytes bruts"""
        frames = int(duration * self.sample_rate / 1000)
        data = bytearray()
        
        for frame in range(frames):
            time = frame / self.sample_rate
            # Onde carrée simple (plus facile à générer)
            wave = 8192 if math.sin(2 * math.pi * frequency * time) > 0 else -8192
            
            # Ajouter sample stéréo (16-bit little endian)
            for channel in range(2):
                data.extend(wave.to_bytes(2, byteorder='little', signed=True))
        
        # Créer le son à partir des bytes
        sound = pygame.mixer.Sound(buffer=data)
        self.sounds_created += 1
        return sound
    
    def _create_minimal_sound(self, duration):
        """Créer un son minimal (click court)"""
        # Créer un click très court comme fallback
        frames = min(int(duration * self.sample_rate / 1000), 1000)  # Max 1000 frames
        data = bytearray()
        
        for frame in range(frames):
            # Son de click simple
            wave = 4096 if frame < frames // 4 else 0
            
            # Ajouter sample stéréo
            for channel in range(2):
                data.extend(wave.to_bytes(2, byteorder='little', signed=True))
        
        sound = pygame.mixer.Sound(buffer=data)
        self.sounds_created += 1
        return sound

class ChannelManager:
    """Gestionnaire intelligent des canaux audio"""
    
    def __init__(self, num_channels=16):
        # Augmenter le nombre de canaux disponibles
        pygame.mixer.set_num_channels(num_channels)
        self.num_channels = num_channels
        
        # Groupes de canaux par type
        self.channel_groups = {
            "shoot": list(range(0, 6)),      # 6 canaux pour les tirs
            "impact": list(range(6, 8)),     # 2 canaux pour les impacts
            "enemy": list(range(8, 12)),     # 4 canaux pour les ennemis
            "boss": list(range(12, 14)),     # 2 canaux pour les boss
            "ui": list(range(14, 16))        # 2 canaux pour l'UI
        }
        
        # Tracking des canaux occupés
        self.channel_usage = {}
        self.channel_priorities = {}
        
        # Pools de sons pour éviter les conflits
        self.sound_pools = {}
        
    def get_free_channel(self, group="general", priority=SoundPriority.MEDIUM):
        """Trouve un canal libre ou libère un canal de priorité inférieure"""
        
        # Essayer d'abord les canaux du groupe spécifique
        if group in self.channel_groups:
            channels_to_check = self.channel_groups[group]
        else:
            channels_to_check = range(self.num_channels)
        
        # Chercher un canal libre
        for ch_id in channels_to_check:
            channel = pygame.mixer.Channel(ch_id)
            if not channel.get_busy():
                self.channel_usage[ch_id] = True
                self.channel_priorities[ch_id] = priority
                return channel
        
        # Si pas de canal libre, essayer de libérer un canal de priorité inférieure
        for ch_id in channels_to_check:
            if ch_id in self.channel_priorities:
                if self.channel_priorities[ch_id].value < priority.value:
                    channel = pygame.mixer.Channel(ch_id)
                    channel.stop()
                    self.channel_usage[ch_id] = True
                    self.channel_priorities[ch_id] = priority
                    return channel
        
        # En dernier recours, prendre le premier canal du groupe
        if channels_to_check:
            ch_id = channels_to_check[0]
            channel = pygame.mixer.Channel(ch_id)
            channel.stop()
            self.channel_usage[ch_id] = True
            self.channel_priorities[ch_id] = priority
            return channel
        
        return None
    
    def stop_sounds_by_group(self, group):
        """Arrête tous les sons d'un groupe"""
        if group in self.channel_groups:
            for ch_id in self.channel_groups[group]:
                channel = pygame.mixer.Channel(ch_id)
                if channel.get_busy():
                    channel.stop()
                if ch_id in self.channel_usage:
                    del self.channel_usage[ch_id]
                if ch_id in self.channel_priorities:
                    del self.channel_priorities[ch_id]
    
    def cleanup_finished_channels(self):
        """Nettoie les canaux qui ont fini de jouer"""
        finished_channels = []
        for ch_id in list(self.channel_usage.keys()):
            channel = pygame.mixer.Channel(ch_id)
            if not channel.get_busy():
                finished_channels.append(ch_id)
        
        for ch_id in finished_channels:
            if ch_id in self.channel_usage:
                del self.channel_usage[ch_id]
            if ch_id in self.channel_priorities:
                del self.channel_priorities[ch_id]

class AudioEngine:
    """Moteur audio optimisé avec gestion intelligente des canaux"""
    
    def __init__(self):
        self.sounds = {}  # Dict[SoundEvent, pygame.Sound]
        self.volume_levels = {
            "master": 0.7,
            "sfx": 0.8,
            "music": 0.3
        }
        self.generator = SimpleSoundGenerator()
        self.channel_manager = ChannelManager()
        
        # Mapping priorités par type de son
        self.sound_priorities = {
            SoundEvent.PLAYER_SHOOT: SoundPriority.LOW,
            SoundEvent.PLAYER_SHOOT_HOLY: SoundPriority.MEDIUM,
            SoundEvent.PLAYER_SHOOT_CHAOS: SoundPriority.MEDIUM,
            SoundEvent.ENEMY_SHOOT: SoundPriority.LOW,
            SoundEvent.BULLET_HIT: SoundPriority.LOW,
            SoundEvent.EXPLOSION: SoundPriority.HIGH,
            SoundEvent.ENEMY_DEATH: SoundPriority.MEDIUM,
            SoundEvent.BOSS_SPAWN: SoundPriority.CRITICAL,
            SoundEvent.BOSS_DEATH: SoundPriority.CRITICAL,
            SoundEvent.PLAYER_LEVEL_UP: SoundPriority.HIGH,
            SoundEvent.PLAYER_DAMAGE: SoundPriority.HIGH,
        }
        
        # Mapping groupes par type de son
        self.sound_groups = {
            SoundEvent.PLAYER_SHOOT: "shoot",
            SoundEvent.PLAYER_SHOOT_HOLY: "shoot",
            SoundEvent.PLAYER_SHOOT_CHAOS: "shoot",
            SoundEvent.ENEMY_SHOOT: "shoot",
            SoundEvent.BULLET_HIT: "impact",
            SoundEvent.EXPLOSION: "impact",
            SoundEvent.ENEMY_DEATH: "enemy",
            SoundEvent.BOSS_SPAWN: "boss",
            SoundEvent.BOSS_DEATH: "boss",
            SoundEvent.PLAYER_LEVEL_UP: "ui",
            SoundEvent.MENU_SELECT: "ui",
        }
        
        # D'abord essayer de charger les sons réels
        self.load_real_sounds()
        
        # Puis générer les sons manquants
        self.preload_sounds()
    
    def load_real_sounds(self):
        """Charge des sons réalistes si disponibles"""
        sounds_folder = "sounds"
        if not os.path.exists(sounds_folder):
            print("📁 Dossier 'sounds' non trouvé, utilisation des sons générés")
            return
        
        print(f"📁 Dossier 'sounds' trouvé, recherche de fichiers audio...")
        
        # Mapping étendu avec de nombreuses variantes de noms
        file_mappings = {
            # Sons de base
            "bolter.wav": SoundEvent.PLAYER_SHOOT,
            # "player_shoot.wav": SoundEvent.PLAYER_SHOOT,
            # "gun_shot.wav": SoundEvent.PLAYER_SHOOT,
            # "laser.wav": SoundEvent.PLAYER_SHOOT,
            # "shoot.wav": SoundEvent.PLAYER_SHOOT,
            "shoot.wav": SoundEvent.BULLET_HIT,
            
            # Sons sacrés/chaos
            "holy_shot.wav": SoundEvent.PLAYER_SHOOT_HOLY,
            "blessed.wav": SoundEvent.PLAYER_SHOOT_HOLY,
            "chaos_shot.wav": SoundEvent.PLAYER_SHOOT_CHAOS,
            "dark_shot.wav": SoundEvent.PLAYER_SHOOT_CHAOS,
            
            # Ennemis
            "enemy_shoot.wav": SoundEvent.ENEMY_SHOOT,
            "enemy_gun.wav": SoundEvent.ENEMY_SHOOT,
            "enemy_death.wav": SoundEvent.ENEMY_DEATH,
            "death.wav": SoundEvent.ENEMY_DEATH,
            "kill.wav": SoundEvent.ENEMY_DEATH,
            
            # Démons
            "demon_death.wav": SoundEvent.ENEMY_DEATH_DAEMON,
            "demon_death.wav": SoundEvent.ENEMY_DEATH_DAEMON,
            "teleport.wav": SoundEvent.DAEMON_TELEPORT,
            
            # Explosions
            "explosion.wav": SoundEvent.EXPLOSION,
            "explode.wav": SoundEvent.EXPLOSION,
            "boom.wav": SoundEvent.EXPLOSION,
            
            # Impacts
            # "hit.wav": SoundEvent.BULLET_HIT,
            # "impact.wav": SoundEvent.BULLET_HIT,
            
            # Boss
            "boss_spawn.wav": SoundEvent.BOSS_SPAWN,
            "boss_death.wav": SoundEvent.BOSS_DEATH,
            "area_attack.wav": SoundEvent.SORCERER_AREA_EXPLODE,
            "purification.wav": SoundEvent.INQUISITOR_PURIFICATION,
            "warp_storm.wav": SoundEvent.DAEMON_PRINCE_WARP_STORM,
            
            # UI
            "level_up.wav": SoundEvent.PLAYER_LEVEL_UP,
            "pickup.wav": SoundEvent.ITEM_PICKUP,
            "item.wav": SoundEvent.ITEM_PICKUP,
            "damage.wav": SoundEvent.PLAYER_DAMAGE,
            "hurt.wav": SoundEvent.PLAYER_DAMAGE,
            
            # Navigation
            "menu_move.wav": SoundEvent.MENU_NAVIGATE,
            "menu_select.wav": SoundEvent.MENU_SELECT,
            "select.wav": SoundEvent.MENU_SELECT,
            "click.wav": SoundEvent.MENU_SELECT,
            
            # Vagues
            "wave_start.wav": SoundEvent.WAVE_START,
            "wave_start.wav": SoundEvent.WAVE_COMPLETE,
            
            # Moralité
            "faith.wav": SoundEvent.FAITH_GAIN,
            "corruption.wav": SoundEvent.CORRUPTION_GAIN,
            "holy.wav": SoundEvent.FAITH_GAIN,
            "chaos.wav": SoundEvent.CORRUPTION_GAIN,
        }
        print("File mappings définis:")
        for filename, event in file_mappings.items():
            print(f"  {filename} -> {event.value}")
            
        # Lister tous les fichiers du dossier
        try:
            files_in_folder = os.listdir(sounds_folder)
            print(f"📋 Fichiers trouvés: {', '.join(files_in_folder)}")
        except:
            print("❌ Impossible de lire le contenu du dossier sounds")
            return
        
        loaded = 0
        
        # Essayer de charger chaque mapping
        for filename, event in file_mappings.items():
            filepath = os.path.join(sounds_folder, filename)
            if os.path.exists(filepath):
                try:
                    print(f"🔄 Tentative de chargement: {filename}")
                    sound = pygame.mixer.Sound(filepath)
                    self.sounds[event] = sound
                    loaded += 1
                    print(f"✅ {filename} -> {event.value}")
                except Exception as e:
                    print(f"❌ Erreur chargement {filename}: {e}")
        
        # Essayer aussi avec les extensions mp3 et ogg
        if loaded == 0:
            print("🔄 Tentative avec d'autres extensions...")
            for base_name in ["bolter", "shoot", "gun", "laser", "explosion", "death", "level_up", "pickup"]:
                for ext in [".mp3", ".ogg", ".wav"]:
                    filename = base_name + ext
                    filepath = os.path.join(sounds_folder, filename)
                    if os.path.exists(filepath):
                        try:
                            sound = pygame.mixer.Sound(filepath)
                            # Assigner à un événement par défaut selon le nom
                            if "shoot" in base_name or "gun" in base_name or "bolter" in base_name:
                                event = SoundEvent.PLAYER_SHOOT
                            elif "explosion" in base_name:
                                event = SoundEvent.EXPLOSION
                            elif "death" in base_name:
                                event = SoundEvent.ENEMY_DEATH
                            elif "level" in base_name:
                                event = SoundEvent.PLAYER_LEVEL_UP
                            elif "pickup" in base_name:
                                event = SoundEvent.ITEM_PICKUP
                            else:
                                continue
                            
                            if event not in self.sounds:  # Ne pas écraser
                                self.sounds[event] = sound
                                loaded += 1
                                print(f"✅ {filename} -> {event.value}")
                        except Exception as e:
                            print(f"❌ Erreur {filename}: {e}")
        
        if loaded > 0:
            print(f"🎵 {loaded} sons réalistes chargés avec succès!")
        else:
            print("⚠️ Aucun son réaliste chargé, utilisation des sons générés")
    
    def preload_sounds(self):
        """Précharge tous les sons de base (seulement ceux qui ne sont pas déjà chargés)"""
        try:
            print("🔊 Génération des sons manquants...")
            created_count = 0
            skipped_count = 0
            total_sounds = 0
            
            # Liste des sons à créer
            sound_configs = [
                # Sons de combat - fréquences différentes pour variation
                (SoundEvent.PLAYER_SHOOT, 800, 150),
                (SoundEvent.PLAYER_SHOOT_HOLY, 1000, 200),
                (SoundEvent.PLAYER_SHOOT_CHAOS, 400, 250),
                (SoundEvent.ENEMY_SHOOT, 600, 120),
                
                # Explosions et impacts
                (SoundEvent.BULLET_HIT, 300, 80),
                (SoundEvent.EXPLOSION, 200, 300),
                
                # Ennemis
                (SoundEvent.ENEMY_DEATH, 250, 200),
                (SoundEvent.ENEMY_DEATH_DAEMON, 150, 400),
                (SoundEvent.DAEMON_TELEPORT, 1200, 300),
                
                # Boss
                (SoundEvent.BOSS_SPAWN, 100, 800),
                (SoundEvent.BOSS_DEATH, 80, 1000),
                (SoundEvent.SORCERER_AREA_EXPLODE, 150, 600),
                (SoundEvent.INQUISITOR_PURIFICATION, 880, 800),
                (SoundEvent.DAEMON_PRINCE_WARP_STORM, 60, 1200),
                
                # UI
                (SoundEvent.MENU_NAVIGATE, 600, 100),
                (SoundEvent.MENU_SELECT, 800, 150),
                (SoundEvent.PLAYER_LEVEL_UP, 660, 500),
                (SoundEvent.WAVE_START, 440, 300),
                (SoundEvent.WAVE_COMPLETE, 550, 400),
                
                # Moralité
                (SoundEvent.FAITH_GAIN, 880, 250),
                (SoundEvent.CORRUPTION_GAIN, 220, 350),
                
                # Autres
                (SoundEvent.PLAYER_DAMAGE, 200, 150),
                (SoundEvent.ITEM_PICKUP, 1320, 120),
            ]
            
            # Créer chaque son qui n'existe pas déjà
            for event, frequency, duration in sound_configs:
                total_sounds += 1
                
                if event in self.sounds:
                    # Son déjà chargé (depuis fichier)
                    skipped_count += 1
                    if skipped_count <= 3:
                        print(f"   ⏭️ {event.value}: Son réel déjà chargé")
                    continue
                
                # Générer le son
                sound = self.generator.create_beep(frequency, duration)
                if sound:
                    self.sounds[event] = sound
                    created_count += 1
                    if created_count <= 3:  # Afficher les premiers pour debug
                        print(f"   🔊 {event.value}: Généré {frequency}Hz, {duration}ms")
                else:
                    if total_sounds <= 3:  # Afficher les échecs pour debug
                        print(f"   ❌ {event.value}: Échec génération")
            
            print(f"✅ Sons: {skipped_count} réels + {created_count} générés = {skipped_count + created_count}/{total_sounds} total")
            
            # Si aucun son n'a été créé, essayer une méthode de fallback
            if created_count == 0 and skipped_count == 0:
                print("🔧 Tentative de création de sons de fallback...")
                self._create_fallback_sounds()
            
        except Exception as e:
            print(f"⚠️ Erreur lors de la génération des sons: {e}")
            print("🔧 Tentative de création de sons de fallback...")
            self._create_fallback_sounds()
    
    def _create_fallback_sounds(self):
        """Crée des sons de fallback très basiques"""
        try:
            # Essayer de créer au moins quelques sons de base
            basic_sounds = [
                (SoundEvent.PLAYER_SHOOT, 500),
                (SoundEvent.ENEMY_DEATH, 300),
                (SoundEvent.PLAYER_LEVEL_UP, 800),
                (SoundEvent.MENU_SELECT, 600),
            ]
            
            fallback_count = 0
            for event, freq in basic_sounds:
                if event not in self.sounds:  # Seulement si pas déjà présent
                    try:
                        # Son très court et simple
                        sound = self._create_click_sound(freq)
                        if sound:
                            self.sounds[event] = sound
                            fallback_count += 1
                    except:
                        continue
            
            print(f"🔧 {fallback_count} sons de fallback créés")
            
        except Exception as e:
            print(f"⚠️ Impossible de créer des sons de fallback: {e}")
            print("🔇 Le jeu fonctionnera en mode silencieux")
    
    def _create_click_sound(self, frequency):
        """Crée un click très simple"""
        try:
            # Créer un son très court (50ms) 
            duration_ms = 50
            sample_rate = 22050
            frames = int(duration_ms * sample_rate / 1000)
            
            # Créer les données audio brutes
            data = bytearray()
            
            for frame in range(frames):
                # Son de click simple - décroissance rapide
                amplitude = int(8192 * (1 - frame / frames))
                if frame < frames // 4:  # Premier quart = son
                    wave = amplitude if frame % 20 < 10 else -amplitude  # Onde carrée basique
                else:  # Reste = silence
                    wave = 0
                
                # Ajouter sample stéréo (16-bit little endian)
                for channel in range(2):
                    data.extend(wave.to_bytes(2, byteorder='little', signed=True))
            
            # Créer le son pygame
            return pygame.mixer.Sound(buffer=data)
            
        except Exception as e:
            print(f"⚠️ Erreur création click: {e}")
            return None
    
    def play_sound(self, event, volume=1.0, category="sfx"):
        """Joue un son avec gestion intelligente des canaux"""
        if event not in self.sounds or not self.sounds[event]:
            return False
        
        try:
            # Calculer le volume final
            final_volume = volume * self.volume_levels["master"] * self.volume_levels[category]
            
            # Obtenir priorité et groupe
            priority = self.sound_priorities.get(event, SoundPriority.MEDIUM)
            group = self.sound_groups.get(event, "general")
            
            # Obtenir un canal approprié
            channel = self.channel_manager.get_free_channel(group, priority)
            if not channel:
                return False
            
            # Jouer le son
            sound = self.sounds[event]
            sound.set_volume(final_volume)
            channel.play(sound)
            return True
            
        except Exception as e:
            print(f"⚠️ Erreur lecture son {event.value}: {e}")
            return False
    
    def update(self):
        """Met à jour le gestionnaire audio"""
        self.channel_manager.cleanup_finished_channels()
    
    def stop_sounds_of_type(self, sound_type):
        """Arrête tous les sons d'un type donné"""
        if sound_type in self.sound_groups:
            group = self.sound_groups[sound_type]
            self.channel_manager.stop_sounds_by_group(group)
    
    def set_volume(self, category, volume):
        """Règle le volume d'une catégorie"""
        if category in self.volume_levels:
            self.volume_levels[category] = max(0.0, min(1.0, volume))

class SoundManager:
    """Gestionnaire principal du son pour le jeu"""
    
    def __init__(self):
        # Initialiser pygame mixer avec plus de canaux et meilleur buffer
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=256)
                pygame.mixer.init()
                print("🔊 Audio initialisé avec optimisations")
            except Exception as e:
                print(f"⚠️ Impossible d'initialiser l'audio: {e}")
                self.audio_enabled = False
                return
        
        self.audio_enabled = True
        self.audio_engine = AudioEngine()
        
        # Configuration spatiale simplifiée
        self.max_audio_distance = 500
        
        # Délais pour éviter le spam de sons (réduits pour les tirs)
        self.sound_delays = {
            SoundEvent.PLAYER_SHOOT: 1,        # Très court pour les tirs
            SoundEvent.ENEMY_SHOOT: 2,
            SoundEvent.BULLET_HIT: 1,
            SoundEvent.ENEMY_DEATH: 10,
            SoundEvent.PLAYER_DAMAGE: 30,
            SoundEvent.PLAYER_LEVEL_UP: 120,
        }
        self.delay_timers = {}
    
    def update(self):
        """Mise à jour du système audio"""
        if not self.audio_enabled:
            return
        
        # Mettre à jour le moteur audio
        self.audio_engine.update()
        
        # Décrémenter les timers de délai
        for event in list(self.delay_timers.keys()):
            self.delay_timers[event] -= 1
            if self.delay_timers[event] <= 0:
                del self.delay_timers[event]
    
    def can_play_sound(self, event):
        """Vérifie si un son peut être joué (anti-spam)"""
        if not self.audio_enabled:
            return False
        return event not in self.delay_timers
    
    def play_sound_with_delay(self, event, delay_frames=None, volume=1.0, category="sfx"):
        """Joue un son avec délai anti-spam"""
        if not self.can_play_sound(event):
            return False
        
        success = self.audio_engine.play_sound(event, volume, category)
        if success:
            # Utiliser le délai par défaut ou celui spécifié
            if delay_frames is None:
                delay_frames = self.sound_delays.get(event, 10)
            self.delay_timers[event] = delay_frames
        
        return success
    
    def play_positional_sound(self, event, world_pos, player_pos, volume=1.0):
        """Joue un son avec positionnement spatial simple"""
        if not self.audio_enabled:
            return False
        
        # Calculer la distance
        dx = world_pos[0] - player_pos[0]
        dy = world_pos[1] - player_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Calculer le volume selon la distance
        if distance > self.max_audio_distance:
            return False  # Trop loin
        
        distance_volume = 1.0 - (distance / self.max_audio_distance)
        final_volume = volume * distance_volume
        
        return self.play_sound_with_delay(event, volume=final_volume)
    
    # === MÉTHODES POUR L'INTÉGRATION DANS LE JEU ===
    
    def on_player_shoot(self, player_pos, morality_system=None):
        """Son de tir du joueur (optimisé pour tir rapide)"""
        if not self.audio_enabled:
            return
        
        # Déterminer le type d'arme selon la moralité
        event = SoundEvent.PLAYER_SHOOT
        
        if morality_system:
            if morality_system.current_state == "pure":
                event = SoundEvent.PLAYER_SHOOT_HOLY
            elif morality_system.current_state in ["corrupted", "chaos_champion"]:
                event = SoundEvent.PLAYER_SHOOT_CHAOS
        
        # Délai très court pour permettre le tir rapide
        self.play_sound_with_delay(event, delay_frames=1, volume=0.4)
    
    def on_enemy_shoot(self, enemy_pos, player_pos):
        """Son de tir d'ennemi"""
        self.play_positional_sound(SoundEvent.ENEMY_SHOOT, enemy_pos, player_pos, volume=0.4)
    
    def on_enemy_death(self, enemy_pos, player_pos, enemy_type=""):
        """Son de mort d'ennemi"""
        event = SoundEvent.ENEMY_DEATH_DAEMON if "daemon" in enemy_type.lower() else SoundEvent.ENEMY_DEATH
        self.play_positional_sound(event, enemy_pos, player_pos, volume=0.7)
    
    def on_boss_spawn(self, boss_type=""):
        """Son de spawn de boss"""
        self.play_sound_with_delay(SoundEvent.BOSS_SPAWN, delay_frames=60, volume=0.9)
    
    def on_boss_death(self):
        """Son de mort de boss"""
        self.play_sound_with_delay(SoundEvent.BOSS_DEATH, delay_frames=60, volume=1.0)
    
    def on_boss_ability(self, ability_type, boss_pos, player_pos):
        """Sons d'abilities de boss"""
        event_map = {
            "sorcerer_area": SoundEvent.SORCERER_AREA_EXPLODE,
            "inquisitor_purification": SoundEvent.INQUISITOR_PURIFICATION,
            "daemon_warp_storm": SoundEvent.DAEMON_PRINCE_WARP_STORM,
            "daemon_teleport": SoundEvent.DAEMON_TELEPORT
        }
        
        event = event_map.get(ability_type)
        if event:
            self.play_positional_sound(event, boss_pos, player_pos, volume=0.8)
    
    def on_player_damage(self):
        """Son de dégâts au joueur"""
        self.play_sound_with_delay(SoundEvent.PLAYER_DAMAGE, delay_frames=30, volume=0.8)
    
    def on_level_up(self):
        """Son de level up"""
        self.play_sound_with_delay(SoundEvent.PLAYER_LEVEL_UP, delay_frames=120, volume=0.8)
    
    def on_item_pickup(self):
        """Son de ramassage d'objet"""
        self.play_sound_with_delay(SoundEvent.ITEM_PICKUP, delay_frames=15, volume=0.6)
    
    def on_wave_start(self, wave_number):
        """Son de début de vague"""
        self.play_sound_with_delay(SoundEvent.WAVE_START, delay_frames=60, volume=0.7)
    
    def on_wave_complete(self):
        """Son de fin de vague"""
        self.play_sound_with_delay(SoundEvent.WAVE_COMPLETE, delay_frames=60, volume=0.7)
    
    def on_morality_change(self, change_type, amount):
        """Sons de changement de moralité"""
        if amount < 1:  # Éviter les petits changements
            return
        
        volume = min(0.8, amount / 10.0)
        
        if change_type == "faith":
            self.play_sound_with_delay(SoundEvent.FAITH_GAIN, delay_frames=30, volume=volume)
        elif change_type == "corruption":
            self.play_sound_with_delay(SoundEvent.CORRUPTION_GAIN, delay_frames=30, volume=volume)
    
    def on_explosion(self, explosion_pos, player_pos):
        """Son d'explosion"""
        self.play_positional_sound(SoundEvent.EXPLOSION, explosion_pos, player_pos, volume=0.9)
    
    def on_bullet_hit(self, hit_pos, player_pos):
        """Son d'impact de projectile (réduit pour éviter le spam)"""
        self.play_positional_sound(SoundEvent.BULLET_HIT, hit_pos, player_pos, volume=0.2)
    
    # === MÉTHODES UI ===
    
    def on_menu_navigate(self):
        """Son de navigation menu"""
        self.play_sound_with_delay(SoundEvent.MENU_NAVIGATE, delay_frames=5, volume=0.5)
    
    def on_menu_select(self):
        """Son de sélection menu"""
        self.play_sound_with_delay(SoundEvent.MENU_SELECT, delay_frames=10, volume=0.6)
    
    # === CONTRÔLES VOLUME ===
    
    def set_master_volume(self, volume):
        """Règle le volume principal"""
        if self.audio_enabled:
            self.audio_engine.set_volume("master", volume)
    
    def set_sfx_volume(self, volume):
        """Règle le volume des effets"""
        if self.audio_enabled:
            self.audio_engine.set_volume("sfx", volume)
    
    def is_audio_enabled(self):
        """Retourne si l'audio est activé"""
        return self.audio_enabled
    
    # === MÉTHODES D'OPTIMISATION ===
    
    def clear_shoot_sounds(self):
        """Nettoie les sons de tir en cours"""
        if self.audio_enabled:
            self.audio_engine.stop_sounds_of_type(SoundEvent.PLAYER_SHOOT)

# === FONCTION D'AIDE POUR L'INTÉGRATION ===

def create_sound_manager():
    """Crée et retourne un gestionnaire audio optimisé"""
    try:
        return SoundManager()
    except Exception as e:
        print(f"⚠️ Impossible de créer le gestionnaire audio: {e}")
        # Retourner un gestionnaire "silencieux"
        manager = SoundManager()
        manager.audio_enabled = False
        return manager