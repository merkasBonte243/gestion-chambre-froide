# src/ui/formulaires_sortie_stock.py
import customtkinter as ctk
from datetime import datetime

class FormulaireSortieStock:
    def __init__(self, parent, stock_service, produit_service, on_success=None):
        self.parent = parent
        self.stock_service = stock_service
        self.produit_service = produit_service
        self.on_success = on_success
        
        # Créer la fenêtre
        self.fenetre = ctk.CTkToplevel(parent)
        self.fenetre.title("📤 Nouvelle Sortie de Stock")
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
            text="📤 Nouvelle Sortie de Stock",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        titre.pack(pady=(0, 20))
        
        # Formulaire
        form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        form_frame.pack(fill="x", padx=10)
        
        # Sélection du produit
        ctk.CTkLabel(form_frame, text="Produit *", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        
        # Récupérer la liste des produits avec stock
        produits = self.produit_service.get_all_produits()
        produits_avec_stock = [p for p in produits if p.quantite > 0]
        noms_produits = [f"{p.nom} (Stock: {p.quantite})" for p in produits_avec_stock]
        self.produits_dict = {f"{p.nom} (Stock: {p.quantite})": p for p in produits_avec_stock}
        
        if not produits_avec_stock:
            ctk.CTkLabel(form_frame, text="❌ Aucun produit en stock disponible", 
                        text_color="red").pack(pady=10)
            return
        
        self.combo_produit = ctk.CTkComboBox(form_frame, values=noms_produits)
        self.combo_produit.pack(fill="x", pady=(0, 15))
        self.combo_produit.bind("<<ComboboxSelected>>", self.on_produit_selectionne)
        
        # Information stock actuel
        self.label_stock = ctk.CTkLabel(form_frame, text="Stock actuel: --", 
                                      font=ctk.CTkFont(size=12))
        self.label_stock.pack(anchor="w", pady=(0, 10))
        
        # Quantité
        ctk.CTkLabel(form_frame, text="Quantité à sortir *").pack(anchor="w", pady=(10, 5))
        self.entry_quantite = ctk.CTkEntry(form_frame, placeholder_text="Ex: 10")
        self.entry_quantite.pack(fill="x", pady=(0, 15))
        
        # Prix unitaire
        ctk.CTkLabel(form_frame, text="Prix unitaire (€)").pack(anchor="w", pady=(10, 5))
        self.entry_prix = ctk.CTkEntry(form_frame, placeholder_text="Ex: 15.50")
        self.entry_prix.pack(fill="x", pady=(0, 15))
        
        # Client (simplifié pour l'instant)
        ctk.CTkLabel(form_frame, text="Client").pack(anchor="w", pady=(10, 5))
        self.entry_client = ctk.CTkEntry(form_frame, placeholder_text="Client principal")
        self.entry_client.insert(0, "Client principal")
        self.entry_client.pack(fill="x", pady=(0, 15))
        
        # Description
        ctk.CTkLabel(form_frame, text="Description (motif de la sortie)").pack(anchor="w", pady=(10, 5))
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
            height=40,
            width=120,
            font=ctk.CTkFont(size=14, weight="bold") 
        )
        btn_annuler.pack(side="left", padx=(0, 10))
        
        btn_valider = ctk.CTkButton(
            boutons_frame,
            text="✅ Enregistrer la sortie",
            command=self.valider_formulaire,
            height=40,
            fg_color="#d32f2f",  # Rouge pour sortie
            font=ctk.CTkFont(size=14, weight="bold"),
            hover_color="#b71c1c"
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
    
    def on_produit_selectionne(self, event):
        """Quand un produit est sélectionné, affiche le stock actuel"""
        nom_complet = self.combo_produit.get()
        if nom_complet in self.produits_dict:
            produit = self.produits_dict[nom_complet]
            self.label_stock.configure(text=f"Stock actuel: {produit.quantite} unités")
    
    def valider_formulaire(self):
        """Valide et enregistre la sortie de stock"""
        try:
            print("🔍 Début validation formulaire sortie stock")
            
            # Récupérer les valeurs
            nom_complet = self.combo_produit.get().strip()
            quantite_str = self.entry_quantite.get().strip()
            prix_str = self.entry_prix.get().strip()
            client = self.entry_client.get().strip()
            description = self.text_description.get("1.0", "end-1c").strip()
            
            print(f"📋 Données: produit={nom_complet}, quantite={quantite_str}")
            
            # Validation
            if not nom_complet:
                raise ValueError("Veuillez sélectionner un produit")
            
            if not quantite_str:
                raise ValueError("La quantité est obligatoire")
            
            quantite = int(quantite_str)
            if quantite <= 0:
                raise ValueError("La quantité doit être positive")
            
            prix = float(prix_str) if prix_str else 0.0
            
            # Récupérer le produit
            if nom_complet not in self.produits_dict:
                raise ValueError("Produit non trouvé")
            
            produit = self.produits_dict[nom_complet]
            
            # Vérifier le stock
            if quantite > produit.quantite:
                raise ValueError(f"Stock insuffisant! Stock actuel: {produit.quantite}")
            
            print(f"📦 Produit trouvé: ID={produit.id_produit}, Stock={produit.quantite}")
            
            # Pour l'instant, client par défaut (ID 1)
            id_client = 1
            
            # Enregistrer la sortie
            print("💾 Enregistrement sortie en cours...")
            success, message = self.stock_service.enregistrer_sortie_stock(
                id_produit=produit.id_produit,
                id_client=id_client,
                quantite=quantite,
                prix_unitaire=prix,
                description=description
            )
            
            print(f"📝 Résultat: {success} - {message}")
            
            if success:
                self.label_message.configure(text=message, text_color="green")
                # Fermer après 2 secondes
                self.fenetre.after(2000, self.fermer_apres_succes)
            else:
                self.label_message.configure(text=message, text_color="red")
                
        except ValueError as e:
            error_msg = f"Erreur: {str(e)}"
            print(f"❌ {error_msg}")
            self.label_message.configure(text=error_msg, text_color="red")
        except Exception as e:
            error_msg = f"Erreur inattendue: {str(e)}"
            print(f"❌ {error_msg}")
            self.label_message.configure(text=error_msg, text_color="red")
    
    def fermer_apres_succes(self):
        """Ferme la fenêtre après un succès"""
        print("🔄 Fermeture fenêtre sortie stock...")
        if self.on_success:
            self.on_success()
        self.fenetre.destroy()