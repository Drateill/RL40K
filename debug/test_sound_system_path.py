#!/usr/bin/env python3
"""
Test du chemin avec la vraie syntaxe du sound_system
"""
import os
import sys

def test_real_path():
    """Test avec la vraie logique du sound_system"""
    print("=== Test Vraie Logique Sound System ===")
    
    # Simuler __file__ depuis src/systems/sound_system.py
    fake_file = os.path.join(os.getcwd(), '..', 'src', 'systems', 'sound_system.py')
    
    # Logique exacte du sound_system
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(fake_file)))
    sounds_folder = os.path.join(project_root, "assets", "sounds")
    
    print(f"fake __file__: {fake_file}")
    print(f"project_root: {project_root}")
    print(f"sounds_folder: {sounds_folder}")
    print(f"Existe: {os.path.exists(sounds_folder)}")
    
    if os.path.exists(sounds_folder):
        print("✅ Chemin correct !")
        
        # Test quelques sons spécifiques
        test_sounds = ["bolter.wav", "level_up.wav", "enemy_death.wav"]
        for sound in test_sounds:
            sound_path = os.path.join(sounds_folder, sound)
            exists = os.path.exists(sound_path)
            print(f"  {sound}: {'✅' if exists else '❌'}")
    else:
        print("❌ Chemin incorrect")

if __name__ == "__main__":
    test_real_path()