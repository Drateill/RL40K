# Imports de tous les ennemis pour compatibilité
from .basic_enemies import BasicEnemy, ShooterEnemy, FastEnemy
from .special_enemies import CultistEnemy, RenegadeMarineEnemy, DaemonEnemy
from .bosses import ChaosSorcererBoss, InquisitorLordBoss, DaemonPrinceBoss

# Exports pour garder la compatibilité avec main.py
__all__ = [
    'BasicEnemy', 'ShooterEnemy', 'FastEnemy',
    'CultistEnemy', 'RenegadeMarineEnemy', 'DaemonEnemy', 
    'ChaosSorcererBoss', 'InquisitorLordBoss', 'DaemonPrinceBoss'
]
__version__ = "1.0.0"
__author__ = "WH40K Roguelike Team"