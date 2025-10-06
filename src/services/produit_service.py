# src/services/produit_service.py - CORRIGÉ
from datetime import datetime
from models.produit import Produit

class ProduitService:
    def __init__(self, db_connection):
        self.conn = db_connection
    
    def get_all_produits(self):
        """Récupère tous les produits avec leur stock"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                p.idProduit, p.nom, p.categorie, p.poids, p.temperatureConservation,
                p.dateEntree, p.datePeremption,
                s.quantite, s.seuilMin 
            FROM Produit p 
            LEFT JOIN Stock s ON p.idProduit = s.idProduit
            ORDER BY p.nom
        """)
        produits = []
        for row in cursor.fetchall():
            produit = Produit(
                id_produit=row[0],
                nom=row[1],
                categorie=row[2],
                poids=row[3],
                temperature_conservation=row[4],
                date_entree=datetime.strptime(row[5], '%Y-%m-%d').date() if row[5] else None,
                date_peremption=datetime.strptime(row[6], '%Y-%m-%d').date() if row[6] else None,
                quantite=row[7] or 0 if row[7] is not None else 0,
                seuil_min=row[8] or 0 if row[8] is not None else 0
            )
            produits.append(produit)
        return produits
    
    def ajouter_produit(self, produit, quantite_initial=0, seuil_min=0):
        """Ajoute un nouveau produit avec stock initial"""
        cursor = self.conn.cursor()
        try:
            # Ajouter le produit
            cursor.execute("""
                INSERT INTO Produit (nom, categorie, poids, temperatureConservation, dateEntree, datePeremption)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                produit.nom, produit.categorie, produit.poids, 
                produit.temperature_conservation, produit.date_entree, produit.date_peremption
            ))
            
            produit_id = cursor.lastrowid
            
            # Ajouter le stock initial
            cursor.execute("""
                INSERT INTO Stock (idProduit, quantite, seuilMin)
                VALUES (?, ?, ?)
            """, (produit_id, quantite_initial, seuil_min))
            
            self.conn.commit()
            return True, f"Produit '{produit.nom}' ajouté avec succès"
            
        except Exception as e:
            self.conn.rollback()
            return False, f"Erreur lors de l'ajout: {str(e)}"
    
    def modifier_produit(self, produit):
        """Modifie un produit existant"""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                UPDATE Produit 
                SET nom=?, categorie=?, poids=?, temperatureConservation=?, datePeremption=?
                WHERE idProduit=?
            """, (
                produit.nom, produit.categorie, produit.poids,
                produit.temperature_conservation, produit.date_peremption, produit.id_produit
            ))
            
            # Mettre à jour le seuil minimum
            cursor.execute("""
                UPDATE Stock SET seuilMin=? WHERE idProduit=?
            """, (produit.seuil_min, produit.id_produit))
            
            self.conn.commit()
            return True, f"Produit '{produit.nom}' modifié avec succès"
            
        except Exception as e:
            self.conn.rollback()
            return False, f"Erreur lors de la modification: {str(e)}"
    
    def supprimer_produit(self, produit_id):
        """Supprime un produit et ses données liées MANUELLEMENT"""
        cursor = self.conn.cursor()
        try:
            print(f"🔍 Début suppression MANUELLE produit ID: {produit_id}")
            
            # Vérifier d'abord si le produit existe
            cursor.execute("SELECT nom FROM Produit WHERE idProduit=?", (produit_id,))
            result = cursor.fetchone()
            
            if not result:
                print("❌ Produit non trouvé")
                return False, "Produit non trouvé"
            
            nom_produit = result[0]
            print(f"📋 Produit à supprimer: {nom_produit}")
            
            # Activer les clés étrangères
            cursor.execute("PRAGMA foreign_keys = ON")
            
            # SUPPRESSION MANUELLE dans l'ordre inverse des dépendances
            # 1. Vérifier s'il y a des données dans les tables liées
            cursor.execute("SELECT COUNT(*) FROM EntreeStock WHERE idProduit=?", (produit_id,))
            nb_entrees = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM SortieStock WHERE idProduit=?", (produit_id,))
            nb_sorties = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM Stock WHERE idProduit=?", (produit_id,))
            nb_stock = cursor.fetchone()[0]
            
            print(f"📊 Données liées - Entrées: {nb_entrees}, Sorties: {nb_sorties}, Stock: {nb_stock}")
            
            # 2. Supprimer d'abord les données des tables enfants
            if nb_entrees > 0:
                print("🗑️ Suppression des entrées de stock...")
                cursor.execute("DELETE FROM EntreeStock WHERE idProduit=?", (produit_id,))
                print(f"✅ {cursor.rowcount} entrée(s) supprimée(s)")
            
            if nb_sorties > 0:
                print("🗑️ Suppression des sorties de stock...")
                # D'abord supprimer les factures liées aux sorties
                cursor.execute("""
                    DELETE FROM Facture 
                    WHERE idSortie IN (SELECT idSortie FROM SortieStock WHERE idProduit = ?)
                """, (produit_id,))
                print(f"✅ {cursor.rowcount} facture(s) supprimée(s)")
                
                # Puis les sorties
                cursor.execute("DELETE FROM SortieStock WHERE idProduit=?", (produit_id,))
                print(f"✅ {cursor.rowcount} sortie(s) supprimée(s)")
            
            if nb_stock > 0:
                print("🗑️ Suppression du stock...")
                cursor.execute("DELETE FROM Stock WHERE idProduit=?", (produit_id,))
                print(f"✅ {cursor.rowcount} ligne(s) de stock supprimée(s)")
            
            # 3. Enfin supprimer le produit
            print("🗑️ Suppression du produit...")
            cursor.execute("DELETE FROM Produit WHERE idProduit=?", (produit_id,))
            rows_affected = cursor.rowcount
            
            self.conn.commit()
            
            if rows_affected > 0:
                print(f"✅ Produit '{nom_produit}' et toutes ses données supprimés avec succès")
                return True, f"Produit '{nom_produit}' supprimé avec succès"
            else:
                print("❌ Aucune ligne affectée lors de la suppression du produit")
                return False, "Aucun produit supprimé"
                
        except Exception as e:
            self.conn.rollback()
            error_msg = f"Erreur lors de la suppression: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
    
    def get_categories(self):
        """Récupère toutes les catégories existantes"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT categorie FROM Produit WHERE categorie IS NOT NULL ORDER BY categorie")
        return [row[0] for row in cursor.fetchall()]
    
    def rechercher_produits(self, terme):
        """Recherche des produits par nom ou catégorie"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                p.idProduit, p.nom, p.categorie, p.poids, p.temperatureConservation,
                p.dateEntree, p.datePeremption,
                s.quantite, s.seuilMin 
            FROM Produit p 
            LEFT JOIN Stock s ON p.idProduit = s.idProduit
            WHERE p.nom LIKE ? OR p.categorie LIKE ?
            ORDER BY p.nom
        """, (f'%{terme}%', f'%{terme}%'))
        produits = []
        for row in cursor.fetchall():
            produit = Produit(
                id_produit=row[0],
                nom=row[1],
                categorie=row[2],
                poids=row[3],
                temperature_conservation=row[4],
                date_entree=datetime.strptime(row[5], '%Y-%m-%d').date() if row[5] else None,
                date_peremption=datetime.strptime(row[6], '%Y-%m-%d').date() if row[6] else None,
                quantite=row[7] or 0 if row[7] is not None else 0,
                seuil_min=row[8] or 0 if row[8] is not None else 0
            )
            produits.append(produit)
        return produits


