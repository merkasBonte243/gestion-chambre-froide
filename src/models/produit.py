# src/models/produit.py
from datetime import datetime, timedelta

class Produit:
    def __init__(self, id_produit=None, nom="", categorie="", description="", 
                 poids=0.0, temperature_conservation=0.0, date_entree=None, 
                 date_peremption=None, quantite=0, seuil_min=0):
        self.id_produit = id_produit
        self.nom = nom
        self.categorie = categorie
        self.description = description
        self.poids = poids
        self.temperature_conservation = temperature_conservation
        self.date_entree = date_entree or datetime.now().date()
        self.date_peremption = date_peremption or (datetime.now() + timedelta(days=30)).date()
        self.quantite = quantite
        self.seuil_min = seuil_min
    
    def jours_avant_peremption(self):
        """Calcule le nombre de jours avant péremption"""
        if not self.date_peremption:
            return None
        aujourdhui = datetime.now().date()
        delta = self.date_peremption - aujourdhui
        return delta.days
    
    def est_bientot_perime(self, jours_alerte=7):
        """Vérifie si le produit est bientôt périmé"""
        jours_restants = self.jours_avant_peremption()
        return jours_restants is not None and jours_restants <= jours_alerte
    
    def est_en_rupture(self):
        """Vérifie si le produit est en rupture de stock"""
        return self.quantite <= self.seuil_min
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        return {
            'id_produit': self.id_produit,
            'nom': self.nom,
            'categorie': self.categorie,
            'description': self.description,
            'poids': self.poids,
            'temperature_conservation': self.temperature_conservation,
            'date_entree': self.date_entree.isoformat() if self.date_entree else None,
            'date_peremption': self.date_peremption.isoformat() if self.date_peremption else None,
            'quantite': self.quantite,
            'seuil_min': self.seuil_min,
            'jours_restants': self.jours_avant_peremption()
        }