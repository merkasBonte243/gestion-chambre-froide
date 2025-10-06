# check_entree_stock.py
import sqlite3

def verifier_entree_stock():
    conn = sqlite3.connect('data/chambre_froide.db')
    cursor = conn.cursor()
    
    print("=== STRUCTURE EXACTE de EntreeStock ===")
    cursor.execute("PRAGMA table_info(EntreeStock)")
    colonnes = cursor.fetchall()
    
    for colonne in colonnes:
        print(f"Colonne {colonne[0]}: '{colonne[1]}' ({colonne[2]})")
    
    conn.close()

if __name__ == "__main__":
    verifier_entree_stock()