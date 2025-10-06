# main.py - CORRIGÉ
import customtkinter as ctk
import sys
import os
import tkinter as tk
from tkinter import messagebox

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database.database_manager import DatabaseManager
from auth.login_window import LoginWindow
from auth.session_manager import SessionManager
from services.produit_service import ProduitService
from services.stock_service import StockService
from ui.formulaires_stock import FormulaireEntreeStock
from ui.formulaires_sortie_stock import FormulaireSortieStock

class ApplicationChambreFroide:
    def __init__(self):
        # Configuration de l'apparence
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialisation
        self.db = DatabaseManager()
        self.session = SessionManager()
        
        # Créer la fenêtre principale (cachée au début)
        self.root = ctk.CTk()
        self.root.title("Gestion Chambre Froide")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Cacher la fenêtre principale jusqu'à l'authentification
        self.root.withdraw()
        
        # Afficher la fenêtre de login
        self.afficher_login()
    
    def afficher_login(self):
        """Affiche la fenêtre de login"""
        LoginWindow(self.on_login_success)
    
    def on_login_success(self, utilisateur):
        """Callback appelé après une authentification réussie"""
        self.session.connecter(utilisateur)
        
        # Afficher la fenêtre principale
        self.root.deiconify()
        
        # Créer l'interface adaptée au rôle
        self.creer_interface()
        
        print(f"✓ Interface chargée pour {utilisateur['role']}")
    
    def creer_interface(self):
        """Crée l'interface adaptée au rôle de l'utilisateur"""
        # Configuration de la grille PRINCIPALE - CORRECTION ICI
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)  # ⬅️ Ligne 1 au lieu de 0
        
        # Header avec infos utilisateur
        self.creer_header()
        
        # Sidebar adaptée au rôle
        self.creer_sidebar()
        
        # Zone de contenu principal - CORRECTION ICI
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.main_frame.grid(row=1, column=1, sticky="nsew", padx=20, pady=20)  # ⬅️ Ligne 1
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Afficher l'accueil
        self.afficher_accueil()
    
    def creer_header(self):
        """Crée l'en-tête avec les infos utilisateur"""
        header = ctk.CTkFrame(self.root, height=60, corner_radius=0)
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        
        # Infos à gauche
        info_frame = ctk.CTkFrame(header, fg_color="transparent")
        info_frame.grid(row=0, column=0, sticky="w", padx=20)
        
        nom_utilisateur = self.session.get_utilisateur()['nom']
        role = self.session.get_utilisateur()['role']
        
        ctk.CTkLabel(
            info_frame, 
            text=f"👤 {nom_utilisateur} ({role})",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=(0, 10))
        
        # Bouton déconnexion à droite
        btn_deconnexion = ctk.CTkButton(
            header,
            text="🚪 Déconnexion",
            command=self.deconnecter,
            width=100,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90")
        )
        btn_deconnexion.grid(row=0, column=1, sticky="e", padx=20)
    
    def creer_sidebar(self):
        """Crée la sidebar adaptée au rôle"""
        sidebar = ctk.CTkFrame(self.root, width=250, corner_radius=0)
        sidebar.grid(row=1, column=0, sticky="nsew", rowspan=1)  # ⬅️ Ligne 1, rowspan=1
        sidebar.grid_rowconfigure(10, weight=1)
    
    # ... le reste du code reste inchangé
        
        # Titre sidebar
        titre = ctk.CTkLabel(sidebar, text="🧊 Menu Principal", 
                           font=ctk.CTkFont(size=18, weight="bold"))
        titre.grid(row=0, column=0, padx=20, pady=(30, 20))
        
        # Boutons communs à tous les rôles
        boutons_communs = [
            ("📊 Tableau de Bord", self.afficher_accueil),
            ("📦 Gestion Produits", self.afficher_produits),
            ("📈 Mouvements Stock", self.afficher_stock),
        ]
        
        # Boutons réservés aux admins
        boutons_admin = [
            ("👥 Gestion Utilisateurs", self.afficher_utilisateurs),
            ("⚙️ Paramètres Avancés", self.afficher_parametres),
        ]
        
        # Afficher les boutons communs
        row = 1
        for texte, commande in boutons_communs:
            btn = self.creer_bouton_menu(sidebar, texte, commande)
            btn.grid(row=row, column=0, padx=20, pady=5, sticky="ew")
            row += 1
        
        # Afficher les boutons admin si nécessaire
        if self.session.est_admin():
            # Séparateur
            separateur = ctk.CTkFrame(sidebar, height=2, fg_color="gray")
            separateur.grid(row=row, column=0, padx=20, pady=10, sticky="ew")
            row += 1
            
            ctk.CTkLabel(sidebar, text="Administration", 
                        font=ctk.CTkFont(size=12, weight="bold"),
                        text_color="gray").grid(row=row, column=0, padx=20, pady=(10, 5), sticky="w")
            row += 1
            
            for texte, commande in boutons_admin:
                btn = self.creer_bouton_menu(sidebar, texte, commande, couleur="red")
                btn.grid(row=row, column=0, padx=20, pady=5, sticky="ew")
                row += 1
    
    def creer_bouton_menu(self, parent, texte, commande, couleur="blue"):
        """Crée un bouton de menu standardisé"""
        return ctk.CTkButton(
            parent, 
            text=texte, 
            command=commande,
            font=ctk.CTkFont(size=14),
            height=40,
            corner_radius=8,
            fg_color="transparent" if couleur == "blue" else "#d13434",
            border_width=1,
            text_color=("gray10", "gray90")
        )
    
    def deconnecter(self):
        """Déconnecte l'utilisateur et retourne au login"""
        self.session.deconnecter()
        
        # Cacher la fenêtre principale
        self.root.withdraw()
        
        # Nettoyer l'interface
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Réafficher le login
        self.afficher_login()
    
    def afficher_accueil(self):
        """Affiche la page d'accueil"""
        self.nettoyer_main_frame()
        
        titre = ctk.CTkLabel(self.main_frame, text="Tableau de Bord",
                           font=ctk.CTkFont(size=28, weight="bold"))
        titre.grid(row=0, column=0, pady=(20, 10), sticky="w", padx=20)
        
        # Message de bienvenue adapté au rôle
        role = self.session.get_utilisateur()['role']
        message = f"Bienvenue {self.session.get_utilisateur()['nom']} !\n\n"
        message += f"Rôle: {role.upper()}\n"
        message += "✓ Système d'authentification opérationnel\n"
        message += "✓ Base de données connectée\n"
        message += "✓ Interface adaptée à votre profil"
        
        if self.session.est_admin():
            message += "\n\n🔧 Vous avez accès aux fonctions d'administration"
        
        label = ctk.CTkLabel(self.main_frame, text=message,
                           font=ctk.CTkFont(size=14), justify="left")
        label.grid(row=1, column=0, sticky="w", padx=20, pady=20)
    
    def afficher_produits(self):
        """Affiche l'interface de gestion des produits"""
        self.nettoyer_main_frame()
        
        # Import ici pour éviter les dépendances circulaires
        from services.produit_service import ProduitService
        self.produit_service = ProduitService(self.db.get_connection())
        
        # Titre
        titre = ctk.CTkLabel(self.main_frame, text="📦 Gestion des Produits",
                           font=ctk.CTkFont(size=28, weight="bold"))
        titre.grid(row=0, column=0, pady=(10, 20), sticky="w")
        
        # Barre d'outils
        toolbar_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        toolbar_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        toolbar_frame.grid_columnconfigure(1, weight=1)
        
        # Bouton Ajouter
        btn_ajouter = ctk.CTkButton(
            toolbar_frame,
            text="➕ Ajouter un produit",
            command=self.afficher_formulaire_ajout_produit,
            height=35
        )
        btn_ajouter.grid(row=0, column=0, padx=(0, 10))
        
        # Barre de recherche
        recherche_frame = ctk.CTkFrame(toolbar_frame, fg_color="transparent")
        recherche_frame.grid(row=0, column=1, sticky="ew")
        
        ctk.CTkLabel(recherche_frame, text="🔍").grid(row=0, column=0, padx=(0, 5))
        self.entry_recherche_produit = ctk.CTkEntry(
            recherche_frame, 
            placeholder_text="Rechercher un produit...",
            width=200
        )
        self.entry_recherche_produit.grid(row=0, column=1, padx=(0, 10))
        self.entry_recherche_produit.bind("<KeyRelease>", self.rechercher_produits)
        
        # Frame pour la liste des produits
        self.liste_produits_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.liste_produits_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 20))
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Charger les produits
        self.charger_liste_produits()

    def charger_liste_produits(self, produits=None):
        """Charge la liste des produits dans l'interface"""
        # Nettoyer la liste
        for widget in self.liste_produits_frame.winfo_children():
            widget.destroy()
        
        # Charger les produits si non fournis
        if produits is None:
            produits = self.produit_service.get_all_produits()
        
        if not produits:
            # Message si aucun produit
            label_vide = ctk.CTkLabel(
                self.liste_produits_frame, 
                text="Aucun produit trouvé. Cliquez sur 'Ajouter un produit' pour commencer.",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            label_vide.pack(pady=50)
            return
        
        # En-tête du tableau
        header_frame = ctk.CTkFrame(self.liste_produits_frame, height=40)
        header_frame.pack(fill="x", pady=(0, 10))
        
        headers = ["Nom", "Catégorie", "Stock", "Péremption", "Actions"]
        widths = [200, 150, 100, 120, 150]
        
        for i, (header, width) in enumerate(zip(headers, widths)):
            label = ctk.CTkLabel(
                header_frame, 
                text=header,
                font=ctk.CTkFont(weight="bold"),
                width=width
            )
            label.grid(row=0, column=i, padx=2)
        
        # Liste des produits
        for produit in produits:
            self.ajouter_ligne_produit(produit)

    def ajouter_ligne_produit(self, produit):
        """Ajoute une ligne produit dans la liste"""
        ligne_frame = ctk.CTkFrame(self.liste_produits_frame, height=50)
        ligne_frame.pack(fill="x", pady=2)
        
        # Couleur de fond et texte selon l'état du produit
        if produit.est_en_rupture():
            # Rouge pour rupture de stock - fond rouge clair, texte foncé
            ligne_frame.configure(fg_color="#ffebee")  # Rouge très clair
            text_color = "#c62828"  # Rouge foncé pour contraste
        elif produit.est_bientot_perime():
            # Orange pour péremption proche - fond orange clair, texte foncé
            ligne_frame.configure(fg_color="#fff3e0")  # Orange très clair  
            text_color = "#ef6c00"  # Orange foncé pour contraste
        else:
            # Normal - utiliser les couleurs par défaut de CustomTkinter
            text_color = None  # Laissera CustomTkinter gérer la couleur
        
        # Nom du produit
        nom_label = ctk.CTkLabel(ligne_frame, text=produit.nom, width=200,
                            text_color=text_color)  # ⬅️ Appliquer la couleur
        nom_label.grid(row=0, column=0, padx=2)
        
        # Catégorie
        categ_label = ctk.CTkLabel(ligne_frame, text=produit.categorie or "-", width=150,
                                text_color=text_color)  # ⬅️ Appliquer la couleur
        categ_label.grid(row=0, column=1, padx=2)
        
        # Stock avec indicateur
        stock_text = f"{produit.quantite}"
        if produit.est_en_rupture():
            stock_text += " ⚠️"
        stock_label = ctk.CTkLabel(ligne_frame, text=stock_text, width=100,
                                text_color=text_color)  # ⬅️ Appliquer la couleur
        stock_label.grid(row=0, column=2, padx=2)
        
        # Péremption
        jours_restants = produit.jours_avant_peremption()
        if jours_restants is not None:
            peremption_text = f"{jours_restants} jours"
            if produit.est_bientot_perime():
                peremption_text += " ⚠️"
        else:
            peremption_text = "-"
        
        peremption_label = ctk.CTkLabel(ligne_frame, text=peremption_text, width=120,
                                    text_color=text_color)  # ⬅️ Appliquer la couleur
        peremption_label.grid(row=0, column=3, padx=2)
        
        # Boutons d'action (toujours visibles)
        actions_frame = ctk.CTkFrame(ligne_frame, fg_color="transparent", width=150)
        actions_frame.grid(row=0, column=4, padx=2)
        
        btn_modifier = ctk.CTkButton(
            actions_frame, 
            text="✏️", 
            width=30,
            height=30,
            command=lambda p=produit: self.modifier_produit(p)
        )
        btn_modifier.pack(side="left", padx=2)
        
        btn_supprimer = ctk.CTkButton(
            actions_frame, 
            text="🗑️", 
            width=30,
            height=30,
            fg_color="#d32f2f",
            hover_color="#b71c1c",
            command=lambda p=produit: self.supprimer_produit(p)
        )
        btn_supprimer.pack(side="left", padx=2)

    def rechercher_produits(self, event):
        """Recherche en temps réel"""
        terme = self.entry_recherche_produit.get().strip()
        if terme:
            produits = self.produit_service.rechercher_produits(terme)
        else:
            produits = self.produit_service.get_all_produits()
        
        self.charger_liste_produits(produits)

    def afficher_formulaire_ajout_produit(self):
        """Affiche le formulaire d'ajout de produit"""
        from ui.formulaires import FormulaireProduit
        FormulaireProduit(
            parent=self.root,
            produit_service=self.produit_service,
            on_success=self.charger_liste_produits
        )

    def modifier_produit(self, produit):
        """Ouvre le formulaire de modification"""
        from ui.formulaires import FormulaireProduit
        FormulaireProduit(
            parent=self.root,
            produit_service=self.produit_service,
            on_success=self.charger_liste_produits,
            produit_existant=produit
        )

    def supprimer_produit(self, produit):  # ⬅️ INDENTATION CORRIGÉE
        """Demande confirmation avant suppression"""
        print(f"🔍 Tentative de suppression du produit: {produit.nom} (ID: {produit.id_produit})")
        
        root = tk.Tk()
        root.withdraw()
        
        reponse = messagebox.askyesno(
            "Confirmation de suppression",
            f"Êtes-vous sûr de vouloir supprimer le produit '{produit.nom}' ?\n\n"
            f"Cette action supprimera également son stock et son historique."
        )
        
        root.destroy()
        
        if reponse:
            print(f"🗑️ Suppression confirmée pour: {produit.nom}")
            success, message = self.produit_service.supprimer_produit(produit.id_produit)
            print(f"📝 Résultat suppression: {success} - {message}")
            
            if success:
                print("✅ Suppression réussie, rechargement de la liste...")
                self.afficher_message_succes(message)
                # Forcer le rechargement complet
                self.charger_liste_produits()
            else:
                print("❌ Erreur lors de la suppression")
                self.afficher_message_erreur(message)

    def afficher_message_succes(self, message):
        """Affiche un message de succès"""
        # Pour l'instant, simple print - on peut améliorer avec une notification UI plus tard
        print(f"✅ {message}")

    def afficher_message_erreur(self, message):
        """Affiche un message d'erreur"""
        print(f"❌ {message}")

    def afficher_stock(self): 
        self.afficher_module("Mouvements de Stock")
    
    def afficher_utilisateurs(self): 
        self.afficher_module("Gestion des Utilisateurs")
    
    def afficher_parametres(self): 
        self.afficher_module("Paramètres Avancés")
    
    def afficher_module(self, titre_module):
        """Affiche un module générique (à développer)"""
        self.nettoyer_main_frame()
        titre = ctk.CTkLabel(self.main_frame, text=titre_module,
                           font=ctk.CTkFont(size=28, weight="bold"))
        titre.pack(pady=20)
        
        label = ctk.CTkLabel(self.main_frame, text="Module en cours de développement...")
        label.pack(pady=10)
    
    def nettoyer_main_frame(self):
        """Nettoie le contenu principal"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def run(self):
        """Lance l'application"""
        self.root.mainloop()

    # INTERFACE MOUVEMENT DE STOCK

    def afficher_stock(self):
        """Affiche l'interface de gestion du stock"""
        self.nettoyer_main_frame()
        
        # Import des services
        from services.stock_service import StockService
        from services.produit_service import ProduitService
        from database.database_manager import DatabaseManager
        
        self.stock_service = StockService(self.db.get_connection())
        self.produit_service = ProduitService(self.db.get_connection())
        
        # Titre
        titre = ctk.CTkLabel(self.main_frame, text="📈 Gestion du Stock",
                        font=ctk.CTkFont(size=28, weight="bold"))
        titre.grid(row=0, column=0, pady=(10, 20), sticky="w")
        
        # Créer les onglets
        self.onglets_stock = ctk.CTkTabview(self.main_frame)
        self.onglets_stock.grid(row=1, column=0, sticky="nsew", pady=(0, 20))
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Ajouter les onglets
        self.onglets_stock.add("📊 Tableau de Bord")
        self.onglets_stock.add("📥 Entrées Stock")
        self.onglets_stock.add("📤 Sorties Stock")
        self.onglets_stock.add("📋 Historique")
        
        # Configurer chaque onglet
        self.creer_onglet_tableau_bord()
        self.creer_onglet_entrees()
        self.creer_onglet_sorties()
        self.creer_onglet_historique()

    def creer_onglet_tableau_bord(self):
        """Crée l'onglet tableau de bord"""
        onglet = self.onglets_stock.tab("📊 Tableau de Bord")
        
        # Statistiques rapides
        stats_frame = ctk.CTkFrame(onglet)
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        # Récupérer les données
        stocks = self.stock_service.get_stock_actuel()
        alertes = self.stock_service.get_alertes_stock()
        
        # Cartes statistiques
        stats_data = [
            ("📦 Produits en stock", len(stocks), "blue"),
            ("⚠️ Rupture imminente", len(alertes['rupture']), "red"),
            ("📅 Bientôt périmés", len(alertes['peremption']), "orange"),
            ("💰 Valeur totale", "Calcul...", "green")
        ]
        
        for i, (titre, valeur, couleur) in enumerate(stats_data):
            carte = ctk.CTkFrame(stats_frame, height=80)
            carte.grid(row=0, column=i, sticky="nsew", padx=5, pady=5)
            stats_frame.grid_columnconfigure(i, weight=1)
            
            ctk.CTkLabel(carte, text=titre, font=ctk.CTkFont(size=12)).pack(pady=(10, 5))
            ctk.CTkLabel(carte, text=str(valeur), font=ctk.CTkFont(size=24, weight="bold")).pack()
        
        # Alertes
        if alertes['rupture'] or alertes['peremption']:
            alertes_frame = ctk.CTkFrame(onglet)
            alertes_frame.pack(fill="x", padx=10, pady=10)
            
            ctk.CTkLabel(alertes_frame, text="🚨 Alertes Actives", 
                        font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(0, 10))
            
            # Alertes rupture
            if alertes['rupture']:
                for alerte in alertes['rupture']:
                    msg = f"🔴 {alerte[1]} - Stock: {alerte[2]} (seuil: {alerte[3]})"
                    ctk.CTkLabel(alertes_frame, text=msg, text_color="red").pack(anchor="w")
            
            # Alertes péremption
            if alertes['peremption']:
                for alerte in alertes['peremption']:
                    msg = f"🟠 {alerte[1]} - Périme dans {int(alerte[4])} jours"
                    ctk.CTkLabel(alertes_frame, text=msg, text_color="orange").pack(anchor="w")

    def creer_onglet_entrees(self):
        """Crée l'onglet entrées de stock"""
        onglet = self.onglets_stock.tab("📥 Entrées Stock")
        
        # Container principal avec scroll
        container = ctk.CTkScrollableFrame(onglet)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Section formulaire
        form_section = ctk.CTkFrame(container)
        form_section.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(form_section, text="Nouvelle Entrée de Stock", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(15, 10))
        
        # Bouton pour ouvrir le formulaire
        btn_nouvelle_entree = ctk.CTkButton(
            form_section,
            text="➕ Nouvelle entrée de stock",
            command=self.ouvrir_formulaire_entree,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        btn_nouvelle_entree.pack(pady=(0, 15))
        
        # Section historique récent
        historique_section = ctk.CTkFrame(container)
        historique_section.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(historique_section, text="Dernières entrées", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(15, 10))
        
        # Placeholder pour l'historique
        ctk.CTkLabel(historique_section, 
                    text="Les dernières entrées de stock apparaîtront ici...",
                    text_color="gray").pack(pady=20)

    def ouvrir_formulaire_entree(self):
        """Ouvre le formulaire d'entrée de stock"""
        from ui.formulaires_stock import FormulaireEntreeStock
        FormulaireEntreeStock(
            parent=self.root,
            stock_service=self.stock_service,
            produit_service=self.produit_service,
            on_success=self.actualiser_onglets_stock
        )

    def actualiser_onglets_stock(self):
        """Actualise les données des onglets stock après une action"""
        print("🔄 Actualisation des données stock...")
        
        # Vérifier que le module stock est chargé
        if hasattr(self, 'onglets_stock') and hasattr(self, 'stock_service'):
            
            # Actualiser les données en mémoire
            try:
                # Recharger les données de base
                self.stock_data = self.stock_service.get_stock_actuel()
                self.alertes_data = self.stock_service.get_alertes_stock()
                print("✅ Données stock rechargées")
                
                # Si on est sur l'onglet Tableau de Bord, actualiser l'affichage
                onglet_actuel = self.onglets_stock.get()
                if onglet_actuel == "📊 Tableau de Bord":
                    self.actualiser_tableau_bord()
                    
            except Exception as e:
                print(f"❌ Erreur lors de l'actualisation: {e}")

    def creer_onglet_sorties(self):
        """Crée l'onglet sorties de stock"""
        onglet = self.onglets_stock.tab("📤 Sorties Stock")
        
        # Container principal avec scroll
        container = ctk.CTkScrollableFrame(onglet)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Section formulaire
        form_section = ctk.CTkFrame(container)
        form_section.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(form_section, text="Nouvelle Sortie de Stock", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(15, 10))
        
        # Bouton pour ouvrir le formulaire
        btn_nouvelle_sortie = ctk.CTkButton(
            form_section,
            text="📤 Nouvelle sortie de stock",
            command=self.ouvrir_formulaire_sortie,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="#d32f2f"  # Rouge pour différencier des entrées
        )
        btn_nouvelle_sortie.pack(pady=(0, 15))
        
        # Information importante
        info_frame = ctk.CTkFrame(form_section, fg_color="#fff3e0")  # Fond orange clair
        info_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(info_frame, 
                    text="💡 Les sorties de stock génèrent automatiquement une facture",
                    text_color="#ef6c00",  # Orange foncé
                    font=ctk.CTkFont(size=12)).pack(padx=10, pady=8)
        
        # Section historique récent
        historique_section = ctk.CTkFrame(container)
        historique_section.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(historique_section, text="Dernières sorties", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(15, 10))
        
        # Placeholder pour l'historique
        ctk.CTkLabel(historique_section, 
                    text="Les dernières sorties de stock apparaîtront ici...",
                    text_color="gray").pack(pady=20)

    def ouvrir_formulaire_sortie(self):
        """Ouvre le formulaire de sortie de stock"""
        from ui.formulaires_sortie_stock import FormulaireSortieStock
        
        def actualiser_et_fermer():
            print("✅ Actualisation après sortie de stock")
            # Recharger tout l'onglet stock
            self.afficher_stock()
        
        FormulaireSortieStock(
            parent=self.root,
            stock_service=self.stock_service,
            produit_service=self.produit_service,
            on_success=actualiser_et_fermer
        )

    def creer_onglet_historique(self):
        """Crée l'onglet historique"""
        onglet = self.onglets_stock.tab("📋 Historique")
        
        # Barre d'outils
        toolbar_frame = ctk.CTkFrame(onglet, fg_color="transparent")
        toolbar_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(toolbar_frame, text="Historique des Mouvements").pack(side="left")
        
        # Ici on ajoutera la liste de l'historique
        historique_frame = ctk.CTkFrame(onglet)
        historique_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(historique_frame, text="Historique des mouvements à implémenter...").pack(pady=50)

if __name__ == "__main__":
    app = ApplicationChambreFroide()
    app.run()