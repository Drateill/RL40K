#!/usr/bin/env python3
"""
Test final du chemin sons avec la logique exacte
"""
import os

def test_path_from_sound_system():
    """Test avec __file__ depuis src/systems/sound_system.py"""
    
    # Simuler être dans src/systems/sound_system.py
    sound_system_path = os.path.join(os.getcwd(), "src", "systems", "sound_system.py")
    
    print(f"Simulation __file__: {sound_system_path}")
    
    # Appliquer la logique du sound_system  
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(sound_system_path)))
    sounds_folder = os.path.join(project_root, "assets", "sounds")
    
    print(f"project_root: {project_root}")
    print(f"sounds_folder: {sounds_folder}")
    print(f"Existe: {os.path.exists(sounds_folder)}")
    
    if os.path.exists(sounds_folder):
        # Test fichiers spécifiques
        test_files = ["bolter.wav", "level_up.wav", "enemy_death.wav"]
        for file in test_files:
            file_path = os.path.join(sounds_folder, file)
            exists = os.path.exists(file_path)
            print(f"  {file}: {'✅' if exists else '❌'}")
    
    return os.path.exists(sounds_folder)

if __name__ == "__main__":
    test_path_from_sound_system()