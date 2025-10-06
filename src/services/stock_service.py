# src/services/stock_service.py
from datetime import datetime
from models.mouvement_stock import MouvementStock, TypeMouvement
from models.produit import Produit
from database.database_manager import DatabaseManager

class StockService:
    def __init__(self, db_connection):
        self.conn = db_connection
    
    def get_mouvements_stock(self, limit=100):
        """Récupère l'historique des mouvements de stock"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                es.idEntree as id_mouvement, 'entree' as type_mouvement,
                p.idProduit, p.nom as produit_nom, 
                f.idFournisseur, f.nom as fournisseur_nom,
                es.quantite, es.dateEntree as date_mouvement,
                NULL as client_id, NULL as client_nom,
                NULL as prix_unitaire, es.datePeremption
            FROM EntreeStock es
            JOIN Produit p ON es.idProduit = p.idProduit
            LEFT JOIN Fournisseur f ON es.idFournisseur = f.idFournisseur
            
            UNION ALL
            
            SELECT 
                ss.idSortie as id_mouvement, 'sortie' as type_mouvement,
                p.idProduit, p.nom as produit_nom, 
                NULL as fournisseur_id, NULL as fournisseur_nom,
                ss.quantite, ss.dateSortie as date_mouvement,
                c.idClient, c.nom as client_nom,
                f.montant / ss.quantite as prix_unitaire, NULL as datePeremption
            FROM SortieStock ss
            JOIN Produit p ON ss.idProduit = p.idProduit
            JOIN Client c ON ss.idClient = c.idClient
            LEFT JOIN Facture f ON ss.idSortie = f.idSortie
            
            ORDER BY date_mouvement DESC
            LIMIT ?
        """, (limit,))
        
        mouvements = []
        for row in cursor.fetchall():
            mouvement = MouvementStock(
                id_mouvement=row[0],
                type_mouvement=TypeMouvement(row[1]),
                quantite=row[6],
                date_mouvement=datetime.strptime(row[7], '%Y-%m-%d').date() if row[7] else None,
                prix_unitaire=row[10] or 0.0,
                date_peremption=datetime.strptime(row[11], '%Y-%m-%d').date() if row[11] else None
            )
            mouvements.append(mouvement)
        
        return mouvements
    
    def enregistrer_entree_stock(self, id_produit, id_fournisseur, quantite, date_peremption=None, prix_unitaire=0.0, description=""):
        """Enregistre une entrée de stock"""
        cursor = self.conn.cursor()
        try:
            # VÉRIFIER SI LE FOURNISSEUR EXISTE
            cursor.execute("SELECT idFournisseur FROM Fournisseur WHERE idFournisseur = ?", (id_fournisseur,))
            if not cursor.fetchone():
                print("⚠️ Fournisseur non trouvé, utilisation du fournisseur par défaut")
                cursor.execute("SELECT idFournisseur FROM Fournisseur LIMIT 1")
                result = cursor.fetchone()
                if result:
                    id_fournisseur = result[0]
                else:
                    cursor.execute("INSERT INTO Fournisseur (nom, contact) VALUES (?, ?)", 
                                ("Fournisseur par défaut", "Contact à définir"))
                    id_fournisseur = cursor.lastrowid
                    print(f"🏢 Fournisseur par défaut créé: ID={id_fournisseur}")
            
            # CORRECTION ICI : utiliser le bon nom de colonne
            date_entree = datetime.now().date()
            cursor.execute("""
                INSERT INTO EntreeStock (idProduit, idFournisseur, quantite, dateEntree, datePeremption)
                VALUES (?, ?, ?, ?, ?)
            """, (id_produit, id_fournisseur, quantite, date_entree, date_peremption))
            
            # Mettre à jour le stock
            cursor.execute("""
                UPDATE Stock 
                SET quantite = quantite + ? 
                WHERE idProduit = ?
            """, (quantite, id_produit))
            
            self.conn.commit()
            return True, "Entrée de stock enregistrée avec succès"
            
        except Exception as e:
            self.conn.rollback()
            return False, f"Erreur lors de l'entrée de stock: {str(e)}"

    # ⬇️⬇️⬇️ CORRECTION ICI - Cette méthode doit être AU MÊME NIVEAU que enregistrer_entree_stock
    def enregistrer_sortie_stock(self, id_produit, id_client, quantite, prix_unitaire=0.0, description=""):
        """Enregistre une sortie de stock"""
        cursor = self.conn.cursor()
        try:
            # Vérifier le stock disponible
            cursor.execute("SELECT quantite FROM Stock WHERE idProduit = ?", (id_produit,))
            result = cursor.fetchone()
            
            if not result or result[0] < quantite:
                return False, "Stock insuffisant pour cette sortie"
            
            # Enregistrer la sortie
            date_sortie = datetime.now().date()
            cursor.execute("""
                INSERT INTO SortieStock (idProduit, idClient, quantite, dateSortie)
                VALUES (?, ?, ?, ?)
            """, (id_produit, id_client, quantite, date_sortie))
            
            sortie_id = cursor.lastrowid
            
            # Enregistrer la facture
            montant_total = quantite * prix_unitaire
            cursor.execute("""
                INSERT INTO Facture (idSortie, dateFacture, montant)
                VALUES (?, ?, ?)
            """, (sortie_id, date_sortie, montant_total))
            
            # Mettre à jour le stock
            cursor.execute("""
                UPDATE Stock 
                SET quantite = quantite - ? 
                WHERE idProduit = ?
            """, (quantite, id_produit))
            
            self.conn.commit()
            return True, f"Sortie de stock enregistrée. Facture #{sortie_id} créée."
            
        except Exception as e:
            self.conn.rollback()
            return False, f"Erreur lors de la sortie de stock: {str(e)}"
    
    def get_stock_actuel(self):
        """Récupère l'état actuel du stock pour tous les produits"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                p.idProduit, p.nom, p.categorie, 
                s.quantite, s.seuilMin,
                p.datePeremption
            FROM Produit p
            JOIN Stock s ON p.idProduit = s.idProduit
            ORDER BY p.nom
        """)
        
        stocks = []
        for row in cursor.fetchall():
            produit = Produit(
                id_produit=row[0],
                nom=row[1],
                categorie=row[2],
                quantite=row[3],
                seuil_min=row[4],
                date_peremption=datetime.strptime(row[5], '%Y-%m-%d').date() if row[5] else None
            )
            stocks.append(produit)
        
        return stocks
    
    def get_alertes_stock(self):
        """Récupère les alertes de stock (rupture et péremption)"""
        cursor = self.conn.cursor()
        
        # Produits en rupture
        cursor.execute("""
            SELECT p.idProduit, p.nom, s.quantite, s.seuilMin
            FROM Produit p
            JOIN Stock s ON p.idProduit = s.idProduit
            WHERE s.quantite <= s.seuilMin
        """)
        alertes_rupture = cursor.fetchall()
        
        # Produits bientôt périmés (7 jours)
        cursor.execute("""
            SELECT p.idProduit, p.nom, p.datePeremption, s.quantite,
                   julianday(p.datePeremption) - julianday('now') as jours_restants
            FROM Produit p
            JOIN Stock s ON p.idProduit = s.idProduit
            WHERE jours_restants <= 7 AND jours_restants >= 0
        """)
        alertes_peremption = cursor.fetchall()
        
        return {
            'rupture': alertes_rupture,
            'peremption': alertes_peremption
        }
    