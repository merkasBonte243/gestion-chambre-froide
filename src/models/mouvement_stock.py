# src/models/mouvement_stock.py
from datetime import datetime
from enum import Enum

class TypeMouvement(Enum):
    ENTREE = "entree"
    SORTIE = "sortie"

class MouvementStock:
    def __init__(self, id_mouvement=None, type_mouvement=None, produit=None, fournisseur=None, 
                 client=None, quantite=0, date_mouvement=None, prix_unitaire=0.0, 
                 date_peremption=None, description=""):
        self.id_mouvement = id_mouvement
        self.type_mouvement = type_mouvement
        self.produit = produit
        self.fournisseur = fournisseur
        self.client = client
        self.quantite = quantite
        self.date_mouvement = date_mouvement or datetime.now().date()
        self.prix_unitaire = prix_unitaire
        self.date_peremption = date_peremption
        self.description = description
    
    def est_entree(self):
        return self.type_mouvement == TypeMouvement.ENTREE
    
    def est_sortie(self):
        return self.type_mouvement == TypeMouvement.SORTIE
    
    def get_montant_total(self):
        return self.quantite * self.prix_unitaire
    
    def to_dict(self):
        return {
            'id_mouvement': self.id_mouvement,
            'type_mouvement': self.type_mouvement.value if self.type_mouvement else None,
            'produit': self.produit.to_dict() if self.produit else None,
            'quantite': self.quantite,
            'date_mouvement': self.date_mouvement.isoformat() if self.date_mouvement else None,
            'prix_unitaire': self.prix_unitaire,
            'montant_total': self.get_montant_total(),
            'description': self.description
        }