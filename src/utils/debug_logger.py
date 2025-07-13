#!/usr/bin/env python3
"""
Logger de debug pour tracer le système de level-up
"""
import datetime

class DebugLogger:
    def __init__(self, filename="levelup_debug.log"):
        self.filename = filename
        self.clear_log()
    
    def clear_log(self):
        """Efface le fichier de log"""
        with open(self.filename, 'w', encoding='utf-8') as f:
            f.write(f"=== DEBUG LEVEL-UP SESSION ===\n")
            f.write(f"Démarré: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    def log(self, message):
        """Ajoute un message au log ET l'affiche en console"""
        timestamp = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
        log_line = f"[{timestamp}] {message}"
        
        # Écrire dans le fichier avec encodage UTF-8
        try:
            with open(self.filename, 'a', encoding='utf-8') as f:
                f.write(log_line + "\n")
        except UnicodeEncodeError:
            # Fallback sans emojis si problème d'encodage
            clean_message = message.encode('ascii', 'ignore').decode('ascii')
            clean_log_line = f"[{timestamp}] {clean_message}"
            with open(self.filename, 'a', encoding='utf-8') as f:
                f.write(clean_log_line + "\n")
        
        # Afficher en console aussi
        print(log_line)
    
    def section(self, title):
        """Crée une section dans le log"""
        separator = "=" * 50
        self.log(separator)
        self.log(f"  {title}")
        self.log(separator)

# Instance globale
debug_logger = DebugLogger()

def debug_log(message):
    """Fonction raccourci pour logger"""
    debug_logger.log(message)

def debug_section(title):
    """Fonction raccourci pour créer une section"""
    debug_logger.section(title)