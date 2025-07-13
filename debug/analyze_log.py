#!/usr/bin/env python3
"""
Analyseur de logs pour diagnostiquer le problème de level-up
"""

def analyze_levelup_log(filename="levelup_debug.log"):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("=" * 60)
        print("    ANALYSE DU LOG DE LEVEL-UP")
        print("=" * 60)
        
        # Vérifications par étapes
        checks = [
            ("🖱️ CLIC DÉTECTÉ", "Event clic pendant level-up détecté"),
            ("🎯 HANDLE INPUT", "handle_input a retourné True"),
            ("🔧 APPLY CALLED", "apply_level_up_choice appelé"),
            ("🎁 ITEM SELECTED", "Application de l'objet"),
            ("🔧 EFFECT APPLIED", "Application de l'effet"),
            ("🏁 FINISH CALLED", "finish_level_up appelé"),
            ("🎮 RETOUR JEU", "RETOUR AU JEU - level-up terminé")
        ]
        
        results = []
        for emoji, search_text in checks:
            found = search_text in content
            status = "✅ OUI" if found else "❌ NON"
            results.append((emoji, search_text, found))
            print(f"{emoji} {search_text}: {status}")
        
        print("\n" + "=" * 60)
        print("    DIAGNOSTIC")
        print("=" * 60)
        
        # Analyse des résultats
        failed_at = None
        for i, (emoji, text, found) in enumerate(results):
            if not found:
                failed_at = i
                break
        
        if failed_at is None:
            print("🎉 TOUS LES STEPS DÉTECTÉS !")
            print("Le problème n'est PAS dans la séquence de level-up.")
            print("Possible causes:")
            print("- Problème dans la logique de pause du jeu")
            print("- Problème d'affichage/rendu")
            print("- State du jeu non mis à jour correctement")
        
        elif failed_at == 0:
            print("❌ PROBLÈME: Le clic n'est même pas détecté")
            print("Causes possibles:")
            print("- Position du clic hors des zones de cartes")
            print("- Event MOUSEBUTTONDOWN pas transmis à GameScene")
            print("- is_leveling_up = False quand on clique")
        
        elif failed_at == 1:
            print("❌ PROBLÈME: Clic détecté mais handle_input retourne False")
            print("Causes possibles:")
            print("- get_card_at_position retourne -1")
            print("- confirm_choice retourne False")
            print("- Problème dans ExperienceSystem.handle_input")
        
        elif failed_at <= 3:
            print("❌ PROBLÈME: Application du choix échoue")
            print("Causes possibles:")
            print("- Conditions de apply_level_up_choice pas remplies")
            print("- is_leveling_up devient False trop tôt")
            print("- level_up_choices vide ou selected_choice invalide")
        
        elif failed_at <= 5:
            print("❌ PROBLÈME: Application réussie mais pas de fin")
            print("Causes possibles:")
            print("- finish_level_up pas appelée")
            print("- Exception dans apply_level_up_choice")
        
        else:
            print("❌ PROBLÈME: Tout semble fonctionner mais jeu reste en pause")
            print("Causes possibles:")
            print("- is_leveling_up pas vraiment mis à False")
            print("- Cache/delay dans la mise à jour du state")
        
        print("\n" + "=" * 60)
        print("    EXTRAIT DU LOG")
        print("=" * 60)
        
        # Afficher les sections importantes
        lines = content.split('\n')
        for line in lines:
            if any(keyword in line for keyword in ["CLIC", "APPLY", "FINISH", "ERROR", "❌"]):
                print(line)
        
        return content
        
    except FileNotFoundError:
        print("❌ Fichier levelup_debug.log non trouvé")
        print("Le logger n'a pas créé de fichier ou le jeu n'a pas été lancé")
        return None

if __name__ == "__main__":
    analyze_levelup_log()