# src/ui/formulaires.py - VERSION CORRIGÉE
import customtkinter as ctk
from datetime import datetime, timedelta

class FormulaireProduit:
    def __init__(self, parent, produit_service, on_success=None, produit_existant=None):
        self.parent = parent
        self.produit_service = produit_service
        self.on_success = on_success
        self.produit_existant = produit_existant
        self.est_modification = produit_existant is not None
        
        # Créer la fenêtre plus grande pour tout voir
        self.fenetre = ctk.CTkToplevel(parent)
        self.fenetre.title("Modifier le produit" if self.est_modification else "Ajouter un produit")
        self.fenetre.geometry("500x650")  # ⬅️ PLUS HAUTE
        self.fenetre.resizable(True, True)  # ⬅️ REDIMENSIONNABLE
        self.fenetre.grab_set()
        self.fenetre.transient(parent)
        
        # Frame principal avec scroll si nécessaire
        self.main_frame = ctk.CTkScrollableFrame(self.fenetre)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
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
        # Titre
        titre = ctk.CTkLabel(
            self.main_frame,
            text="✏️ Modifier le produit" if self.est_modification else "➕ Ajouter un produit",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        titre.pack(pady=(0, 20))
        
        # Formulaire dans un frame séparé
        form_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=10)
        
        # Champ Nom (obligatoire)
        ctk.CTkLabel(form_frame, text="Nom du produit *", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        self.entry_nom = ctk.CTkEntry(form_frame, placeholder_text="Ex: Poulet entier")
        self.entry_nom.pack(fill="x", pady=(0, 15))
        
        # Champ Catégorie
        ctk.CTkLabel(form_frame, text="Catégorie").pack(anchor="w", pady=(10, 5))
        self.entry_categorie = ctk.CTkEntry(form_frame, placeholder_text="Ex: Viandes, Légumes...")
        self.entry_categorie.pack(fill="x", pady=(0, 15))
        
        # Suggestions de catégories
        categories = self.produit_service.get_categories()
        if categories:
            suggestions_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
            suggestions_frame.pack(fill="x", pady=(0, 15))
            ctk.CTkLabel(suggestions_frame, text="Catégories existantes:", 
                        font=ctk.CTkFont(size=11), text_color="gray").pack(anchor="w")
            suggestions_text = ", ".join(categories[:5])
            ctk.CTkLabel(suggestions_frame, text=suggestions_text,
                        font=ctk.CTkFont(size=10), text_color="gray").pack(anchor="w")
        
        # Champ Poids
        ctk.CTkLabel(form_frame, text="Poids (kg)").pack(anchor="w", pady=(10, 5))
        self.entry_poids = ctk.CTkEntry(form_frame, placeholder_text="Ex: 1.5")
        self.entry_poids.pack(fill="x", pady=(0, 15))
        
        # Champ Température
        ctk.CTkLabel(form_frame, text="Température de conservation (°C)").pack(anchor="w", pady=(10, 5))
        self.entry_temperature = ctk.CTkEntry(form_frame, placeholder_text="Ex: -18")
        self.entry_temperature.pack(fill="x", pady=(0, 15))
        
        # Champ Date de péremption (obligatoire)
        ctk.CTkLabel(form_frame, text="Date de péremption *", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        date_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        date_frame.pack(fill="x", pady=(0, 15))
        
        # Date par défaut = aujourd'hui + 30 jours
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
        
        # SECTION STOCK (uniquement pour l'ajout)
        if not self.est_modification:
            ctk.CTkLabel(form_frame, text="--- Stock initial ---", 
                        font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(20, 10))
            
            # Quantité initiale
            ctk.CTkLabel(form_frame, text="Quantité initiale").pack(anchor="w", pady=(10, 5))
            self.entry_quantite = ctk.CTkEntry(form_frame, placeholder_text="Ex: 50")
            self.entry_quantite.insert(0, "0")
            self.entry_quantite.pack(fill="x", pady=(0, 15))
            
            # Seuil d'alerte
            ctk.CTkLabel(form_frame, text="Seuil d'alerte stock bas").pack(anchor="w", pady=(10, 5))
            self.entry_seuil = ctk.CTkEntry(form_frame, placeholder_text="Ex: 5")
            self.entry_seuil.insert(0, "0")
            self.entry_seuil.pack(fill="x", pady=(0, 20))
        else:
            # Pour la modification, afficher le stock actuel
            ctk.CTkLabel(form_frame, text="--- Stock actuel ---", 
                        font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(20, 10))
            
            info_stock = ctk.CTkLabel(
                form_frame, 
                text=f"Quantité actuelle: {self.produit_existant.quantite} | Seuil alerte: {self.produit_existant.seuil_min}",
                font=ctk.CTkFont(size=12),
                text_color="gray"
            )
            info_stock.pack(anchor="w", pady=(0, 20))
        
        # Pré-remplir si modification
        if self.est_modification:
            self.pre_remplir_formulaire()
        
        # BOUTONS EN BAS - BIEN VISIBLE
        boutons_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        boutons_frame.pack(fill="x", pady=(20, 10))
        
        # Bouton Annuler
        btn_annuler = ctk.CTkButton(
            boutons_frame,
            text="❌ Annuler",
            command=self.fenetre.destroy,
            fg_color="transparent",
            border_width=1,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        btn_annuler.pack(side="left", padx=(0, 10))
        
        # Bouton Valider (grand et visible)
        btn_valider = ctk.CTkButton(
            boutons_frame,
            text="✅ Modifier" if self.est_modification else "✅ Ajouter le produit",
            command=self.valider_formulaire,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2E7D32"  # Vert foncé
        )
        btn_valider.pack(side="right")
        
        # Message d'erreur/succès
        self.label_message = ctk.CTkLabel(
            form_frame,
            text="* Champs obligatoires",
            text_color="gray",
            font=ctk.CTkFont(size=11)
        )
        self.label_message.pack(pady=(10, 0))
        
        # Focus sur le premier champ
        self.entry_nom.focus()
    
    def set_date(self, jours):
        """Définit une date rapidement"""
        nouvelle_date = (datetime.now() + timedelta(days=jours)).strftime('%Y-%m-%d')
        self.entry_date_peremption.delete(0, 'end')
        self.entry_date_peremption.insert(0, nouvelle_date)
    
    def pre_remplir_formulaire(self):
        """Pré-remplit le formulaire avec les données du produit existant"""
        p = self.produit_existant
        self.entry_nom.insert(0, p.nom or "")
        self.entry_categorie.insert(0, p.categorie or "")
        self.entry_poids.insert(0, str(p.poids) if p.poids else "")
        self.entry_temperature.insert(0, str(p.temperature_conservation) if p.temperature_conservation else "")
        
        if p.date_peremption:
            self.entry_date_peremption.delete(0, 'end')
            self.entry_date_peremption.insert(0, p.date_peremption.strftime('%Y-%m-%d'))
    
    def valider_formulaire(self):
        """Valide et enregistre le produit"""
        try:
            # Récupérer les valeurs
            nom = self.entry_nom.get().strip()
            categorie = self.entry_categorie.get().strip() or None
            poids_str = self.entry_poids.get().strip()
            temperature_str = self.entry_temperature.get().strip()
            date_peremption = self.entry_date_peremption.get().strip()
            
            # Validation des champs obligatoires
            if not nom:
                raise ValueError("Le nom du produit est obligatoire")
            
            if not date_peremption:
                raise ValueError("La date de péremption est obligatoire")
            
            # Validation des nombres
            poids = float(poids_str) if poids_str else 0.0
            temperature = float(temperature_str) if temperature_str else 0.0
            
            # Valider la date
            try:
                datetime.strptime(date_peremption, '%Y-%m-%d')
            except ValueError:
                raise ValueError("Format de date invalide. Utilisez YYYY-MM-DD")
            
            # Créer l'objet produit
            from models.produit import Produit
            produit = Produit(
                nom=nom,
                categorie=categorie,
                poids=poids,
                temperature_conservation=temperature,
                date_entree=datetime.now().date(),  # Date d'entrée aujourd'hui
                date_peremption=datetime.strptime(date_peremption, '%Y-%m-%d').date()
            )
            
            if self.est_modification:
                # Modification
                produit.id_produit = self.produit_existant.id_produit
                success, message = self.produit_service.modifier_produit(produit)
            else:
                # Ajout avec stock initial
                quantite_str = self.entry_quantite.get().strip()
                seuil_str = self.entry_seuil.get().strip()
                
                quantite = int(quantite_str) if quantite_str else 0
                seuil_min = int(seuil_str) if seuil_str else 0
                
                success, message = self.produit_service.ajouter_produit(produit, quantite, seuil_min)
            
            if success:
                self.label_message.configure(text=message, text_color="green")
                # Fermer après 1 seconde si succès
                self.fenetre.after(1000, self.fermer_apres_succes)
            else:
                self.label_message.configure(text=message, text_color="red")
                
        except ValueError as e:
            self.label_message.configure(text=f"Erreur: {str(e)}", text_color="red")
        except Exception as e:
            self.label_message.configure(text=f"Erreur inattendue: {str(e)}", text_color="red")
    
    def fermer_apres_succes(self):
        """Ferme la fenêtre après un succès"""
        if self.on_success:
            self.on_success()
        self.fenetre.destroy()