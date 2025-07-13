#!/usr/bin/env python3
"""
Test pour vérifier que le chemin des sons fonctionne correctement
"""
import os
import sys

# Ajouter src au path
sys.path.insert(0, '../src')

def test_sound_path():
    """Test le nouveau chemin des sons"""
    print("=== Test Chemin Sons ===")
    
    # Simuler le chemin depuis sound_system.py
    current_file = os.path.join(os.getcwd(), '..', 'src', 'systems', 'sound_system.py')
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
    sounds_folder = os.path.join(project_root, "assets", "sounds")
    
    print(f"Chemin calculé: {sounds_folder}")
    print(f"Chemin existe: {os.path.exists(sounds_folder)}")
    
    if os.path.exists(sounds_folder):
        print("✅ Dossier sons trouvé !")
        
        # Lister quelques sons
        files = os.listdir(sounds_folder)
        wav_files = [f for f in files if f.endswith('.wav')]
        print(f"Fichiers .wav trouvés: {len(wav_files)}")
        
        # Montrer quelques exemples
        for wav_file in wav_files[:5]:
            print(f"  - {wav_file}")
            
        if len(wav_files) > 5:
            print(f"  ... et {len(wav_files) - 5} autres")
            
    else:
        print("❌ Dossier sons non trouvé")
        
        # Debug du chemin
        print(f"current_file simulé: {current_file}")
        print(f"project_root calculé: {project_root}")
        
        # Vérifier alternatives
        alternatives = [
            "assets/sounds",
            "../assets/sounds", 
            "../../assets/sounds"
        ]
        
        for alt in alternatives:
            if os.path.exists(alt):
                print(f"✅ Alternative trouvée: {alt}")
                break
        else:
            print("❌ Aucune alternative trouvée")

if __name__ == "__main__":
    test_sound_path()