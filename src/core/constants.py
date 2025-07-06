"""
Constantes globales du jeu - Extrait de main.py
Centralise toutes les constantes utilisées dans le projet
"""

# === DIMENSIONS D'ÉCRAN ===
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# === DIMENSIONS DU MONDE ===
WORLD_WIDTH = 2400  # Double de l'écran pour effet de caméra
WORLD_HEIGHT = 1600

# === COULEURS ===
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# Couleurs thématiques Warhammer 40K
IMPERIAL_GOLD = (255, 215, 0)
CHAOS_RED = (139, 0, 0)
BLOOD_RED = (120, 0, 0)
METAL_GRAY = (169, 169, 169)
WARP_PURPLE = (128, 0, 128)

# === GAMEPLAY ===
PLAYER_SPEED = 5
BULLET_SPEED = 10
ENEMY_SPEED = 2

# === TAILLES DES ENTITÉS ===
PLAYER_SIZE = 20
BULLET_SIZE = 5
ENEMY_SIZE = 15
BOSS_SIZE = 40

# === SYSTÈME DE COMBAT ===
PLAYER_MAX_HEALTH = 100
PLAYER_DAMAGE = 20
ENEMY_DAMAGE = 10
BOSS_DAMAGE = 25

# === SYSTÈME D'EXPÉRIENCE ===
BASE_EXP_FOR_LEVEL = 100
EXP_MULTIPLIER = 1.5

# === VAGUES D'ENNEMIS ===
BOSS_WAVES = [5, 15, 20]
MAX_ENEMIES_PER_WAVE = 50

# === SYSTÈME AUDIO ===
MASTER_VOLUME = 0.7
SFX_VOLUME = 0.8
MUSIC_VOLUME = 0.6

# === CHEMINS DES ASSETS ===
ASSETS_PATH = "assets"
SOUNDS_PATH = "assets/sounds"
TEXTURES_PATH = "assets/textures"
FONTS_PATH = "assets/fonts"

# === CONFIGURATION DU JEU ===
DEBUG_MODE = False
SHOW_FPS = True
SHOW_DEBUG_INFO = True

# === SYSTÈME DE MORALITÉ ===
FAITH_DECAY_RATE = 0.1  # Perte de foi par seconde
CORRUPTION_GROWTH_RATE = 0.05  # Croissance de corruption passive

# === PHYSICS ===
COLLISION_MARGIN = 2  # Marge pour les collisions
MIN_SPAWN_DISTANCE = 100  # Distance minimum du joueur pour spawn
WALL_THICKNESS = 10