# check_table_structure.py
import sqlite3
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def verifier_structure_entree_stock():
    conn = sqlite3.connect('data/chambre_froide.db')
    cursor = conn.cursor()
    
    print("=== STRUCTURE DE LA TABLE EntreeStock ===")
    cursor.execute("PRAGMA table_info(EntreeStock)")
    colonnes = cursor.fetchall()
    
    for colonne in colonnes:
        print(f"Colonne {colonne[0]}: {colonne[1]} ({colonne[2]})")
    
    print("\n=== DONNÉES EXEMPLES ===")
    cursor.execute("SELECT * FROM EntreeStock LIMIT 3")
    for row in cursor.fetchall():
        print(row)
    
    conn.close()

if __name__ == "__main__":
    verifier_structure_entree_stock()