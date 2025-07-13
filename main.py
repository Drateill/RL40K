"""
Point d'entrée principal du jeu Roguelike Warhammer 40K
Nouveau main.py restructuré - Simple et clair
"""
import sys
import os

# Ajouter le dossier src au path Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Point d'entrée principal"""
    try:
        # Importer le moteur de jeu
        from src.core.game_engine import GameEngine
        
        # Créer et lancer le jeu
        print("🎮 Lancement de Roguelike Warhammer 40K...")
        print("=" * 50)
        
        game_engine = GameEngine()
        game_engine.run()
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("Vérifiez que tous les fichiers sont présents dans src/")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n🛑 Interruption clavier détectée")
        sys.exit(0)
    
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()