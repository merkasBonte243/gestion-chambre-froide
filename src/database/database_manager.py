# src/database/database_manager.py
import sqlite3
import hashlib
import os
from datetime import datetime, timedelta

class DatabaseManager:
    def __init__(self, db_path="../data/chambre_froide.db"):
        # Créer le dossier data s'il n'existe pas
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = os.path.abspath(db_path)
        self.conn = None
        self.connect()
        self.create_tables()
        self.create_default_data()
        print(f"✓ Base de données initialisée: {self.db_path}")
    
    def connect(self):
        """Établit la connexion à la base de données"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
    
    def create_tables(self):
        """Crée toutes les tables selon VOTRE conception exacte"""
        tables = [
            # Table Utilisateur
            """
            CREATE TABLE IF NOT EXISTS Utilisateur (
                idUtilisateur INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                role TEXT NOT NULL,
                login TEXT UNIQUE NOT NULL,
                motDePasse TEXT NOT NULL
            )
            """,
            
            # Table Produit
            """
            CREATE TABLE IF NOT EXISTS Produit (
                idProduit INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                categorie TEXT,
                poids DECIMAL(10,2),
                temperatureConservation DECIMAL(5,2),
                dateEntree DATE NOT NULL,
                datePeremption DATE NOT NULL
            )
            """,
            
            # Table Stock
            """
            CREATE TABLE IF NOT EXISTS Stock (
                idStock INTEGER PRIMARY KEY AUTOINCREMENT,
                idProduit INTEGER NOT NULL,
                quantite INTEGER NOT NULL,
                seuilMin INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (idProduit) REFERENCES Produit(idProduit)
            )
            """,
            
            # Table Fournisseur
            """
            CREATE TABLE IF NOT EXISTS Fournisseur (
                idFournisseur INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                contact TEXT
            )
            """,
            
            # Table Client
            """
            CREATE TABLE IF NOT EXISTS Client (
                idClient INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                contact TEXT
            )
            """,
            
            # Table EntreeStock - CORRECTION ICI
            """
            CREATE TABLE IF NOT EXISTS EntreeStock (
                idEntree INTEGER PRIMARY KEY AUTOINCREMENT,
                idProduit INTEGER NOT NULL,
                idFournisseur INTEGER NOT NULL,
                quantite INTEGER NOT NULL,
                dateEntree DATE NOT NULL,
                datePeremption DATE,
                FOREIGN KEY (idProduit) REFERENCES Produit(idProduit),
                FOREIGN KEY (idFournisseur) REFERENCES Fournisseur(idFournisseur)
            )
            """,
            
            # Table SortieStock
            """
            CREATE TABLE IF NOT EXISTS SortieStock (
                idSortie INTEGER PRIMARY KEY AUTOINCREMENT,
                idProduit INTEGER NOT NULL,
                idClient INTEGER NOT NULL,
                quantite INTEGER NOT NULL,
                dateSortie DATE NOT NULL,
                FOREIGN KEY (idProduit) REFERENCES Produit(idProduit),
                FOREIGN KEY (idClient) REFERENCES Client(idClient)
            )
            """,
            
            # Table Facture
            """
            CREATE TABLE IF NOT EXISTS Facture (
                idFacture INTEGER PRIMARY KEY AUTOINCREMENT,
                idSortie INTEGER NOT NULL,
                dateFacture DATE NOT NULL DEFAULT CURRENT_DATE,
                montant DECIMAL(10,2) NOT NULL,
                FOREIGN KEY (idSortie) REFERENCES SortieStock(idSortie)
            )
            """,
            
            # Table TableauDeBord
            """
            CREATE TABLE IF NOT EXISTS TableauDeBord (
                idTableau INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT,
                dateGeneration DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        ]
        
        print("Création des tables...")
        for i, table in enumerate(tables, 1):
            try:
                self.conn.execute(table)
                print(f"  ✓ Table {i} créée")
            except Exception as e:
                print(f"  ✗ Erreur table {i}: {e}")
        
        self.conn.commit()
    
    def create_default_data(self):
        """Crée les données par défaut avec gestion d'erreur améliorée"""
        try:
            print("Création des données par défaut...")
            
            # Vérifier si les données existent déjà
            cursor = self.conn.cursor()
            
            # Vérifier les utilisateurs
            cursor.execute("SELECT COUNT(*) FROM Utilisateur")
            if cursor.fetchone()[0] == 0:
                # Créer utilisateur admin
                mot_de_passe_hash = hashlib.sha256("admin123".encode()).hexdigest()
                cursor.execute("""
                    INSERT INTO Utilisateur (nom, role, login, motDePasse)
                    VALUES (?, ?, ?, ?)
                """, ("Administrateur Principal", "admin", "admin", mot_de_passe_hash))
                
                # Utilisateur opérateur
                mot_de_passe_hash = hashlib.sha256("oper123".encode()).hexdigest()
                cursor.execute("""
                    INSERT INTO Utilisateur (nom, role, login, motDePasse)
                    VALUES (?, ?, ?, ?)
                """, ("Opérateur Standard", "operateur", "operateur", mot_de_passe_hash))
                print("✓ Utilisateurs créés")
            
            # Vérifier les fournisseurs
            cursor.execute("SELECT COUNT(*) FROM Fournisseur")
            if cursor.fetchone()[0] == 0:
                # Fournisseur par défaut
                cursor.execute("""
                    INSERT INTO Fournisseur (nom, contact)
                    VALUES (?, ?)
                """, ("Fournisseur Principal", "Jean Dupont - 01 23 45 67 89"))
                print("✓ Fournisseurs créés")
            
            # Vérifier les clients
            cursor.execute("SELECT COUNT(*) FROM Client")
            if cursor.fetchone()[0] == 0:
                # Client par défaut
                cursor.execute("""
                    INSERT INTO Client (nom, contact)
                    VALUES (?, ?)
                """, ("Client Général", "Point de vente principal"))
                print("✓ Clients créés")
            
            self.conn.commit()
            print("✓ Données par défaut créées")
            
        except Exception as e:
            print(f"⚠️ Avertissement données par défaut: {e}")
            # Ne pas rollback, peut-être que certaines données sont déjà créées
            self.conn.commit()
    
    # Méthodes pour implémenter VOS fonctionnalités
    def get_utilisateurs(self):
        """Récupère tous les utilisateurs"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Utilisateur")
        return cursor.fetchall()
    
    def get_produits_avec_stock(self):
        """Récupère les produits avec leur stock"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT p.*, s.quantite, s.seuilMin 
            FROM Produit p 
            LEFT JOIN Stock s ON p.idProduit = s.idProduit
        """)
        return cursor.fetchall()
    
    def get_alertes_peremption(self, jours=7):
        """Récupère les produits bientôt périmés"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT p.*, s.quantite, s.seuilMin,
                   julianday(p.datePeremption) - julianday('now') as jours_restants
            FROM Produit p 
            LEFT JOIN Stock s ON p.idProduit = s.idProduit
            WHERE jours_restants <= ?
            ORDER BY p.datePeremption
        """, (jours,))
        return cursor.fetchall()
    
    def get_alertes_stock_bas(self):
        """Récupère les produits en rupture de stock"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT p.*, s.quantite, s.seuilMin
            FROM Produit p 
            JOIN Stock s ON p.idProduit = s.idProduit
            WHERE s.quantite <= s.seuilMin
        """)
        return cursor.fetchall()
    
    def enregistrer_entree_stock(self, id_produit, id_fournisseur, quantite, date_entree=None):
        """Enregistre une entrée de stock selon votre conception"""
        if date_entree is None:
            date_entree = datetime.now().strftime('%Y-%m-%d')
        
        try:
            # Entrée dans EntreeStock
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO EntreeStock (idProduit, idFournisseur, quantite, dateEntree)
                VALUES (?, ?, ?, ?)
            """, (id_produit, id_fournisseur, quantite, date_entree))
            
            # Mise à jour du stock
            cursor.execute("""
                UPDATE Stock SET quantite = quantite + ? 
                WHERE idProduit = ?
            """, (quantite, id_produit))
            
            self.conn.commit()
            return True, "Entrée de stock enregistrée"
        except Exception as e:
            return False, str(e)
    
    def get_connection(self):
        """Retourne la connexion pour les opérations spécifiques"""
        return self.conn
    
    def close(self):
        """Ferme la connexion"""
        if self.conn:
            self.conn.close()

# Test de la base de données selon votre conception
if __name__ == "__main__":
    from datetime import timedelta
    
    db = DatabaseManager()
    print("✓ Base de données créée!")
    
    # Afficher les tables créées
    cursor = db.conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print("\nTables créées :")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Test des données
    print("\nDonnées de test:")
    print("Utilisateurs:", len(db.get_utilisateurs()))
    print("Produits avec stock:", len(db.get_produits_avec_stock()))
    print("Alertes péremption:", len(db.get_alertes_peremption()))
    
    db.close()