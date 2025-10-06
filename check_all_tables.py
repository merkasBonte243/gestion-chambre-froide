# check_all_tables.py
import sqlite3
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def verifier_toutes_tables():
    conn = sqlite3.connect('data/chambre_froide.db')
    cursor = conn.cursor()
    
    print("=== TOUTES LES TABLES EXISTANTES ===")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        print(f"\n--- TABLE: {table_name} ---")
        
        # Structure
        cursor.execute(f"PRAGMA table_info({table_name})")
        colonnes = cursor.fetchall()
        
        if colonnes:
            for colonne in colonnes:
                print(f"  Colonne {colonne[0]}: {colonne[1]} ({colonne[2]})")
        else:
            print("  (table vide ou inexistante)")
        
        # Nombre de lignes
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  Lignes: {count}")
        except:
            print("  Erreur compte lignes")
    
    conn.close()

if __name__ == "__main__":
    verifier_toutes_tables()