import json
import duckdb
from pathlib import Path


DATA_JSON = Path("data/input/collection.json")
DB_PATH   = Path("data/db/collection.duckdb")


# ── Vérifications ─────────────────────────────────────────────────────────────
if not DATA_JSON.exists():
    raise FileNotFoundError(f"Fichier source introuvable : {DATA_JSON}")

DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# ── Migration ─────────────────────────────────────────────────────────────────
print(f"Lecture de {DATA_JSON} ...")
with open(DATA_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

# Filtrage sur type = "basegame"
basegames = [jeu for jeu in data if jeu.get("Type") == "basegame"]

# Extraction des champs souhaités
colonnes = ["ID", "Titre", "Joueur(s)", "Durée", "Catégorie(s)", "Thème(s)", "Mécanisme(s)", "Note moyenne"]

def extraire(jeu, champ):
    valeur = jeu.get(champ, None)
    # Les champs qui sont des listes → on les joint en chaîne
    if isinstance(valeur, list):
        return ", ".join(str(v) for v in valeur)
    return valeur

lignes = [
    tuple(extraire(jeu, champ) for champ in colonnes)
    for jeu in basegames
]

print(lignes[0])  # Affiche la première ligne pour vérification

# Création de la base DuckDB (fichier local ou en mémoire)
con = duckdb.connect(DB_PATH)  # Remplacer par ":memory:" pour une base en mémoire

con.execute("""
    CREATE TABLE IF NOT EXISTS jeux (
        id INTEGER,
        titre VARCHAR,
        joueurs VARCHAR,
        duree VARCHAR,
        categories VARCHAR,
        themes VARCHAR,
        mecanismes VARCHAR,
        note_moyenne DOUBLE
    )
""")

con.executemany("""
    INSERT INTO jeux VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", lignes)

# Vérification
print(f"{len(lignes)} jeux insérés.")
result = con.execute("SELECT * FROM jeux LIMIT 5").fetchdf()
print(result)

con.close()