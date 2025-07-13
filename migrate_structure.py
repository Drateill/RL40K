# migrate_structure.py
"""
Script d'aide pour la migration de la structure
À exécuter pour créer automatiquement la nouvelle structure
"""
import os
import shutil

def create_directory_structure():
    """Crée la nouvelle structure de dossiers"""
    
    directories = [
        "src",
        "src/core", 
        "src/scenes",
        "src/systems", 
        "src/world",
        "src/ui",
        "config",
        "tests",
        "assets",
        "assets/sounds",
        "assets/textures", 
        "assets/fonts"
    ]
    
    print("📁 Création de la structure de dossiers...")
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"   ✅ Créé: {directory}/")
        else:
            print(f"   ⏭️  Existe déjà: {directory}/")

def create_init_files():
    """Crée les fichiers __init__.py nécessaires"""
    
    init_files = [
        "src/__init__.py",
        "src/core/__init__.py",
        "src/scenes/__init__.py", 
        "src/systems/__init__.py",
        "src/world/__init__.py",
        "src/ui/__init__.py",
        "tests/__init__.py"
    ]
    
    print("\n📝 Création des fichiers __init__.py...")
    
    for init_file in init_files:
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('"""Module package"""')
            print(f"   ✅ Créé: {init_file}")
        else:
            print(f"   ⏭️  Existe déjà: {init_file}")

def backup_main():
    """Sauvegarde le main.py actuel"""
    
    if os.path.exists("main.py"):
        if not os.path.exists("main_backup.py"):
            shutil.copy2("main.py", "main_backup.py")
            print("\n💾 Sauvegarde: main.py -> main_backup.py")
        else:
            print("\n⏭️  Sauvegarde existe déjà: main_backup.py")
    else:
        print("\n⚠️  main.py non trouvé")

def create_requirements():
    """Crée le fichier requirements.txt s'il n'existe pas"""
    
    requirements_content = """pygame>=2.1.0
numpy>=1.21.0
"""
    
    if not os.path.exists("requirements.txt"):
        with open("requirements.txt", 'w') as f:
            f.write(requirements_content)
        print("\n📋 Créé: requirements.txt")
    else:
        print("\n⏭️  Existe déjà: requirements.txt")

def create_gitignore():
    """Crée/met à jour le .gitignore"""
    
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo

# Game specific
saves/
screenshots/
*.save
*.dat
main_backup.py

# OS
.DS_Store
Thumbs.db
"""
    
    if not os.path.exists(".gitignore"):
        with open(".gitignore", 'w') as f:
            f.write(gitignore_content)
        print("\n🚫 Créé: .gitignore")
    else:
        print("\n⏭️  Existe déjà: .gitignore")

def show_next_steps():
    """Affiche les prochaines étapes"""
    
    print("\n" + "="*60)
    print("🎯 MIGRATION SETUP TERMINÉ")
    print("="*60)
    print("\n📋 PROCHAINES ÉTAPES MANUELLES:")
    print("\n1. Copier les fichiers créés dans les phases 2-5:")
    print("   - src/core/constants.py")
    print("   - src/core/game_engine.py") 
    print("   - src/core/scene_manager.py")
    print("   - src/scenes/base_scene.py")
    print("   - src/scenes/game_scene.py")
    print("   - src/systems/entity_manager.py")
    print("   - src/systems/collision_system.py")
    print("   - src/systems/spawn_system.py")
    print("   - src/world/world_generator.py")
    print("   - src/world/level_manager.py")
    print("   - src/world/environment_effects.py")
    print("   - src/ui/game_hud.py")
    
    print("\n2. Créer le nouveau main.py")
    print("\n3. Adapter les imports dans tous les fichiers")
    print("\n4. Tester avec: python main.py")
    print("\n5. Corriger les erreurs d'import au fur et à mesure")
    
    print("\n💡 CONSEILS:")
    print("   - Migrer fichier par fichier")
    print("   - Tester après chaque étape")
    print("   - Consulter main_backup.py en cas de doute")
    print("   - Commiter régulièrement")
    
    print("\n🆘 EN CAS DE PROBLÈME:")
    print("   - Restaurer: cp main_backup.py main.py")
    print("   - Vérifier les imports relatifs")
    print("   - Consulter le plan détaillé dans les artifacts")

def main():
    """Fonction principale du script de migration"""
    
    print("🚀 SCRIPT DE MIGRATION - ROGUELIKE WH40K")
    print("=" * 50)
    
    # Vérifier qu'on est dans le bon dossier
    if not os.path.exists("player.py"):
        print("❌ Erreur: Ce script doit être exécuté dans le dossier du projet")
        print("   (le dossier qui contient player.py, main.py, etc.)")
        return
    
    try:
        backup_main()
        create_directory_structure()
        create_init_files()
        create_requirements()
        create_gitignore()
        show_next_steps()
        
        print("\n✅ SETUP DE MIGRATION RÉUSSI !")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la migration: {e}")
        print("Vérifiez les permissions et l'espace disque")

if __name__ == "__main__":
    main()

# =============================================================================
# AIDE-MÉMOIRE POUR LA MIGRATION
# =============================================================================

"""
ORDRE D'EXÉCUTION RECOMMANDÉ:

1. python migrate_structure.py
2. Copier manuellement les fichiers des phases 2-5
3. Créer le nouveau main.py  
4. Adapter les imports
5. Tester et corriger

IMPORTS À VÉRIFIER:

Dans game_scene.py:
- from player import Player
- from camera import Camera  
- from items import ItemManager
- etc.

Ajouter en haut si nécessaire:
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

TESTS DE VALIDATION:

□ Le jeu démarre sans erreur
□ Le joueur apparaît à l'écran
□ Les ennemis spawnt
□ Les projectiles fonctionnent
□ Le système de collision marche
□ L'audio fonctionne
□ Le level-up marche
□ Les boss apparaissent

ROLLBACK SI PROBLÈME:
cp main_backup.py main.py
"""