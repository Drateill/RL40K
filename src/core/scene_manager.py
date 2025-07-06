"""
Gestionnaire de scènes - Organise les différents écrans du jeu
Permet de basculer entre menu, jeu, pause, game over, etc.
"""

class SceneManager:
    """Gestionnaire des scènes du jeu"""
    
    def __init__(self):
        self.scenes = {}  # Dict des scènes disponibles
        self.active_scene = None  # Scène actuellement active
        self.previous_scene = None  # Scène précédente pour retour
        
        # Stack pour gestion des scènes empilées (pause par exemple)
        self.scene_stack = []
    
    def add_scene(self, name, scene):
        """Ajoute une nouvelle scène"""
        self.scenes[name] = scene
        scene.scene_manager = self  # Référence retour
        print(f"📝 Scène '{name}' ajoutée")
    
    def remove_scene(self, name):
        """Supprime une scène"""
        if name in self.scenes:
            del self.scenes[name]
            print(f"🗑️ Scène '{name}' supprimée")
    
    def set_active_scene(self, name):
        """Active une scène spécifique"""
        if name not in self.scenes:
            print(f"❌ Erreur: Scène '{name}' non trouvée")
            return False
        
        # Sauvegarder la scène précédente
        if self.active_scene:
            self.previous_scene = self.active_scene
            self.active_scene.on_exit()
        
        # Activer la nouvelle scène
        self.active_scene = self.scenes[name]
        self.active_scene.on_enter()
        
        print(f"🎬 Scène active: '{name}'")
        return True
    
    def push_scene(self, name):
        """Empile une scène (pour pause par exemple)"""
        if name not in self.scenes:
            print(f"❌ Erreur: Scène '{name}' non trouvée")
            return False
        
        # Mettre la scène actuelle en pause
        if self.active_scene:
            self.active_scene.on_pause()
            self.scene_stack.append(self.active_scene)
        
        # Activer la nouvelle scène
        self.active_scene = self.scenes[name]
        self.active_scene.on_enter()
        
        print(f"📚 Scène '{name}' empilée")
        return True
    
    def pop_scene(self):
        """Dépile la scène courante (retour de pause)"""
        if not self.scene_stack:
            print("❌ Aucune scène à dépiler")
            return False
        
        # Quitter la scène actuelle
        if self.active_scene:
            self.active_scene.on_exit()
        
        # Récupérer la scène précédente
        self.active_scene = self.scene_stack.pop()
        self.active_scene.on_resume()
        
        print("📚 Scène dépilée")
        return True
    
    def go_back(self):
        """Retourne à la scène précédente"""
        if self.previous_scene:
            current_name = self.get_active_scene_name()
            previous_scene = self.previous_scene
            
            # Chercher le nom de la scène précédente
            previous_name = None
            for name, scene in self.scenes.items():
                if scene == previous_scene:
                    previous_name = name
                    break
            
            if previous_name:
                self.set_active_scene(previous_name)
                print(f"⬅️ Retour à '{previous_name}' depuis '{current_name}'")
                return True
        
        print("❌ Aucune scène précédente")
        return False
    
    def get_active_scene_name(self):
        """Retourne le nom de la scène active"""
        if not self.active_scene:
            return None
        
        for name, scene in self.scenes.items():
            if scene == self.active_scene:
                return name
        return "unknown"
    
    def get_scene(self, name):
        """Retourne une scène par son nom"""
        return self.scenes.get(name)
    
    def list_scenes(self):
        """Liste toutes les scènes disponibles"""
        print("📋 Scènes disponibles:")
        for name in self.scenes.keys():
            status = "ACTIVE" if self.scenes[name] == self.active_scene else "inactive"
            print(f"  - {name} ({status})")
    
    def clear_stack(self):
        """Vide la pile des scènes"""
        self.scene_stack.clear()
        print("🗑️ Pile des scènes vidée")