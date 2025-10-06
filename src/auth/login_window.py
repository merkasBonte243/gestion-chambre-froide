# src/auth/login_window.py - VERSION CORRIGÉE
import customtkinter as ctk
from database.database_manager import DatabaseManager
import hashlib

class LoginWindow:
    """def __init__(self, on_login_success):
        self.on_login_success = on_login_success
        self.db = DatabaseManager()
        
        # Création de la fenêtre de login
        self.window = ctk.CTkToplevel()
        self.window.title("Connexion - Gestion Chambre Froide")
        self.window.geometry("400x300")
        self.window.resizable(False, False)
        
        # Centrer la fenêtre (méthode CustomTkinter)
        self.centrer_fenetre()
        
        self.window.grab_set()  # Rend la fenêtre modale
        self.window.transient(self.window)  # Reste au premier plan
        
        self.creer_interface()"""
    
    def __init__(self, on_login_success, parent=None):
        self.on_login_success = on_login_success
        self.db = DatabaseManager()
        
        # Création de la fenêtre de login
        self.window = ctk.CTkToplevel(parent)  # parent passé ici
        self.window.title("Connexion - Gestion Chambre Froide")
        self.window.geometry("400x300")
        self.window.resizable(False, False)
        
        # Centrer la fenêtre
        self.centrer_fenetre()
        
        self.window.grab_set()  # Rend la fenêtre modale
        if parent:
            self.window.transient(parent)  # ✅ parent passé ici
        
        self.creer_interface()
    
    def centrer_fenetre(self):
        """Centre la fenêtre sur l'écran"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def creer_interface(self):
        """Crée l'interface de login"""
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titre
        titre = ctk.CTkLabel(
            main_frame, 
            text="🔐 Connexion",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        titre.pack(pady=(20, 10))
        
        # Sous-titre
        sous_titre = ctk.CTkLabel(
            main_frame,
            text="Gestion Chambre Froide",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        sous_titre.pack(pady=(0, 30))
        
        # Formulaire de connexion
        form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        form_frame.pack(fill="x", padx=20)
        
        # Champ login
        ctk.CTkLabel(form_frame, text="Login:").pack(anchor="w", pady=(0, 5))
        self.entry_login = ctk.CTkEntry(form_frame, placeholder_text="Votre login")
        self.entry_login.pack(fill="x", pady=(0, 15))
        self.entry_login.bind("<Return>", lambda e: self.authentifier())
        
        # Champ mot de passe
        ctk.CTkLabel(form_frame, text="Mot de passe:").pack(anchor="w", pady=(0, 5))
        self.entry_mdp = ctk.CTkEntry(form_frame, placeholder_text="Votre mot de passe", show="•")
        self.entry_mdp.pack(fill="x", pady=(0, 20))
        self.entry_mdp.bind("<Return>", lambda e: self.authentifier())
        
        # Bouton de connexion
        btn_connexion = ctk.CTkButton(
            form_frame,
            text="Se connecter",
            command=self.authentifier,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        btn_connexion.pack(fill="x", pady=(0, 10))
        
        # Message d'erreur
        self.label_erreur = ctk.CTkLabel(
            form_frame,
            text="",
            text_color="red",
            font=ctk.CTkFont(size=12)
        )
        self.label_erreur.pack()
        
        # Informations de test
        info_test = ctk.CTkLabel(
            form_frame,
            text="Comptes test:\nAdmin: admin / admin123\nOpérateur: operateur / oper123",
            font=ctk.CTkFont(size=10),
            text_color="gray",
            justify="left"
        )
        info_test.pack(pady=(20, 0))
        
        # Focus sur le champ login
        self.entry_login.focus()
    
    def authentifier(self):
        """Authentifie l'utilisateur"""
        login = self.entry_login.get().strip()
        mdp = self.entry_mdp.get().strip()
        
        if not login or not mdp:
            self.afficher_erreur("Veuillez remplir tous les champs")
            return
        
        try:
            # Hasher le mot de passe
            mdp_hash = hashlib.sha256(mdp.encode()).hexdigest()
            
            # Rechercher l'utilisateur
            cursor = self.db.get_connection().cursor()
            cursor.execute(
                "SELECT * FROM Utilisateur WHERE login = ? AND motDePasse = ?",
                (login, mdp_hash)
            )
            utilisateur = cursor.fetchone()
            
            if utilisateur:
                # Authentification réussie
                user_data = {
                    'id': utilisateur[0],
                    'nom': utilisateur[1],
                    'role': utilisateur[2],
                    'login': utilisateur[3]
                }
                self.window.destroy()
                self.on_login_success(user_data)
            else:
                self.afficher_erreur("Login ou mot de passe incorrect")
                
        except Exception as e:
            self.afficher_erreur(f"Erreur de connexion: {str(e)}")
    
    def afficher_erreur(self, message):
        """Affiche un message d'erreur"""
        self.label_erreur.configure(text=message)
        self.entry_mdp.delete(0, 'end')
        self.entry_login.focus()