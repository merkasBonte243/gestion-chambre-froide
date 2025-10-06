# src/auth/session_manager.py
class SessionManager:
    def __init__(self):
        self.utilisateur_connecte = None
        self.est_connecte = False
    
    def connecter(self, utilisateur):
        """Connecte un utilisateur"""
        self.utilisateur_connecte = utilisateur
        self.est_connecte = True
        print(f"✓ Utilisateur connecté: {utilisateur['nom']} ({utilisateur['role']})")
    
    def deconnecter(self):
        """Déconnecte l'utilisateur"""
        if self.utilisateur_connecte:
            print(f"✓ Utilisateur déconnecté: {self.utilisateur_connecte['nom']}")
        self.utilisateur_connecte = None
        self.est_connecte = False
    
    def est_admin(self):
        """Vérifie si l'utilisateur est admin"""
        return self.est_connecte and self.utilisateur_connecte['role'] == 'admin'
    
    def est_operateur(self):
        """Vérifie si l'utilisateur est opérateur"""
        return self.est_connecte and self.utilisateur_connecte['role'] == 'operateur'
    
    def get_utilisateur(self):
        """Retourne les données de l'utilisateur connecté"""
        return self.utilisateur_connecte