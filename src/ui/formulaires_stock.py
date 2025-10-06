# src/ui/formulaires_stock.py
import customtkinter as ctk
from datetime import datetime, timedelta

class FormulaireEntreeStock:
    def __init__(self, parent, stock_service, produit_service, on_success=None):
        self.parent = parent
        self.stock_service = stock_service
        self.produit_service = produit_service
        self.on_success = on_success
        
        # Créer la fenêtre
        self.fenetre = ctk.CTkToplevel(parent)
        self.fenetre.title("📥 Nouvelle Entrée de Stock")
        self.fenetre.geometry("600x500")
        self.fenetre.resizable(False, False)
        self.fenetre.grab_set()
        
        self.creer_interface()
        self.centrer_fenetre()
    
    def centrer_fenetre(self):
        """Centre la fenêtre sur l'écran"""
        self.fenetre.update_idletasks()
        width = self.fenetre.winfo_width()
        height = self.fenetre.winfo_height()
        x = (self.fenetre.winfo_screenwidth() // 2) - (width // 2)
        y = (self.fenetre.winfo_screenheight() // 2) - (height // 2)
        self.fenetre.geometry(f'{width}x{height}+{x}+{y}')
    
    def creer_interface(self):
        """Crée l'interface du formulaire"""
        main_frame = ctk.CTkFrame(self.fenetre)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titre
        titre = ctk.CTkLabel(
            main_frame,
            text="📥 Nouvelle Entrée de Stock",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        titre.pack(pady=(0, 20))
        
        # Formulaire
        form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        form_frame.pack(fill="x", padx=10)
        
        # Sélection du produit
        ctk.CTkLabel(form_frame, text="Produit *", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        
        # Récupérer la liste des produits
        produits = self.produit_service.get_all_produits()
        noms_produits = [p.nom for p in produits]
        self.produits_dict = {p.nom: p.id_produit for p in produits}
        
        self.combo_produit = ctk.CTkComboBox(form_frame, values=noms_produits)
        self.combo_produit.pack(fill="x", pady=(0, 15))
        
        # Quantité
        ctk.CTkLabel(form_frame, text="Quantité *").pack(anchor="w", pady=(10, 5))
        self.entry_quantite = ctk.CTkEntry(form_frame, placeholder_text="Ex: 50")
        self.entry_quantite.pack(fill="x", pady=(0, 15))
        
        # Date de péremption
        ctk.CTkLabel(form_frame, text="Date de péremption").pack(anchor="w", pady=(10, 5))
        date_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        date_frame.pack(fill="x", pady=(0, 15))
        
        date_defaut = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        self.entry_date_peremption = ctk.CTkEntry(date_frame, placeholder_text="YYYY-MM-DD")
        self.entry_date_peremption.insert(0, date_defaut)
        self.entry_date_peremption.pack(side="left", fill="x", expand=True)
        
        # Boutons de date rapide
        btn_frame = ctk.CTkFrame(date_frame, fg_color="transparent")
        btn_frame.pack(side="right", padx=(5, 0))
        
        ctk.CTkButton(btn_frame, text="+7j", width=40,
                     command=lambda: self.set_date(7)).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="+30j", width=40,
                     command=lambda: self.set_date(30)).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="+90j", width=40,
                     command=lambda: self.set_date(90)).pack(side="left", padx=2)
        
        # Fournisseur (simplifié pour l'instant)
        ctk.CTkLabel(form_frame, text="Fournisseur").pack(anchor="w", pady=(10, 5))
        self.entry_fournisseur = ctk.CTkEntry(form_frame, placeholder_text="Fournisseur principal")
        self.entry_fournisseur.insert(0, "Fournisseur principal")
        self.entry_fournisseur.pack(fill="x", pady=(0, 15))
        
        # Description
        ctk.CTkLabel(form_frame, text="Description").pack(anchor="w", pady=(10, 5))
        self.text_description = ctk.CTkTextbox(form_frame, height=60)
        self.text_description.pack(fill="x", pady=(0, 20))
        
        # Boutons
        boutons_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        boutons_frame.pack(fill="x", pady=(20, 0))
        
        btn_annuler = ctk.CTkButton(
            boutons_frame,
            text="❌ Annuler",
            command=self.fenetre.destroy,
            fg_color="transparent",
            border_width=1,
            height=40
        )
        btn_annuler.pack(side="left", padx=(0, 10))
        
        btn_valider = ctk.CTkButton(
            boutons_frame,
            text="✅ Enregistrer l'entrée",
            command=self.valider_formulaire,
            height=40,
            fg_color="#2E7D32"
        )
        btn_valider.pack(side="right")
        
        # Message d'erreur/succès
        self.label_message = ctk.CTkLabel(
            form_frame,
            text="",
            text_color="red",
            font=ctk.CTkFont(size=12)
        )
        self.label_message.pack(pady=(10, 0))
        
        # Focus sur le premier champ
        self.combo_produit.focus()
    
    def set_date(self, jours):
        """Définit une date rapidement"""
        nouvelle_date = (datetime.now() + timedelta(days=jours)).strftime('%Y-%m-%d')
        self.entry_date_peremption.delete(0, 'end')
        self.entry_date_peremption.insert(0, nouvelle_date)
    
    def valider_formulaire(self):
        """Valide et enregistre l'entrée de stock - VERSION SIMPLIFIÉE"""
        try:
            print("🔍 Début validation formulaire entrée stock")
            
            # Récupérer les valeurs
            nom_produit = self.combo_produit.get().strip()
            quantite_str = self.entry_quantite.get().strip()
            date_peremption = self.entry_date_peremption.get().strip()
            
            print(f"📋 Données: produit={nom_produit}, quantite={quantite_str}")
            
            # Validation basique
            if not nom_produit:
                self.label_message.configure(text="Veuillez sélectionner un produit", text_color="red")
                return
                
            if not quantite_str or not quantite_str.isdigit():
                self.label_message.configure(text="Quantité invalide", text_color="red")
                return
            
            quantite = int(quantite_str)
            if quantite <= 0:
                self.label_message.configure(text="La quantité doit être positive", text_color="red")
                return
            
            # Récupérer l'ID du produit
            id_produit = self.produits_dict.get(nom_produit)
            if not id_produit:
                self.label_message.configure(text="Produit non trouvé", text_color="red")
                return
            
            print(f"📦 Produit trouvé: ID={id_produit}")
            
            # Utiliser le fournisseur par défaut (ID 1) pour l'instant
            id_fournisseur = 1
            
            # Enregistrer l'entrée
            print("💾 Enregistrement en cours...")
            success, message = self.stock_service.enregistrer_entree_stock(
                id_produit=id_produit,
                id_fournisseur=id_fournisseur,
                quantite=quantite,
                date_peremption=date_peremption if date_peremption else None
            )
            
            print(f"📝 Résultat: {success} - {message}")
            
            if success:
                self.label_message.configure(text="✅ Entrée de stock enregistrée avec succès!", text_color="green")
                # Fermer après 2 secondes
                self.fenetre.after(2000, self.fermer_apres_succes)
            else:
                self.label_message.configure(text=f"❌ {message}", text_color="red")
                
        except Exception as e:
            error_msg = f"Erreur: {str(e)}"
            print(f"❌ {error_msg}")
            self.label_message.configure(text=error_msg, text_color="red")
    
    def fermer_apres_succes(self):
        """Ferme la fenêtre après un succès"""
        print("🔄 Fermeture de la fenêtre après succès...")
        if self.on_success:
            self.on_success()
        # AJOUTER CETTE LIGNE pour fermer la fenêtre
        self.fenetre.destroy()
        print("✅ Fenêtre fermée")