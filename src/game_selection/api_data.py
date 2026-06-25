# main.py
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
import duckdb
from typing import Optional

app = FastAPI(
    title="API Jeux de société",
    description="Requêtez votre collection de jeux depuis DuckDB",
    version="1.0.0"
)

DB_PATH = "data/db/collection.duckdb"

def get_con():
    return duckdb.connect(DB_PATH, read_only=True)


# ─── GET /jeux ─────────────────────────────────────────────────────────────────
# Liste tous les jeux avec filtres optionnels
@app.get("/jeux")
def lister_jeux(
    titre: Optional[str] = Query(None, description="Filtrer par titre (recherche partielle)"),
    categorie: Optional[str] = Query(None, description="Filtrer par catégorie"),
    theme: Optional[str] = Query(None, description="Filtrer par thème"),
    mecanisme: Optional[str] = Query(None, description="Filtrer par mécanisme"),
    joueurs: Optional[str] = Query(None, description="Filtrer par nombre de joueurs (ex: '2 — 4')"),
    note_min: Optional[float] = Query(None, description="Note moyenne minimale"),
    note_max: Optional[float] = Query(None, description="Note moyenne maximale"),
    tri: Optional[str] = Query("titre", description="Colonne de tri: titre, note_moyenne, duree"),
    ordre: Optional[str] = Query("asc", description="Ordre: asc ou desc"),
    limite: int = Query(50, ge=1, le=500, description="Nombre de résultats max"),
    offset: int = Query(0, ge=0, description="Pagination: décalage"),
):
    conditions = []
    params = []

    if titre:
        conditions.append("LOWER(titre) LIKE LOWER(?)")
        params.append(f"%{titre}%")
    if categorie:
        conditions.append("LOWER(categories) LIKE LOWER(?)")
        params.append(f"%{categorie}%")
    if theme:
        conditions.append("LOWER(themes) LIKE LOWER(?)")
        params.append(f"%{theme}%")
    if mecanisme:
        conditions.append("LOWER(mecanismes) LIKE LOWER(?)")
        params.append(f"%{mecanisme}%")
    if joueurs:
        conditions.append("joueurs = ?")
        params.append(joueurs)
    if note_min is not None:
        conditions.append("note_moyenne >= ?")
        params.append(note_min)
    if note_max is not None:
        conditions.append("note_moyenne <= ?")
        params.append(note_max)

    # Sécurisation du tri
    colonnes_valides = {"titre", "note_moyenne", "duree", "id"}
    if tri not in colonnes_valides:
        tri = "titre"
    ordre_sql = "DESC" if ordre.lower() == "desc" else "ASC"

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    query = f"""
        SELECT id, titre, joueurs, duree, categories, themes, mecanismes, note_moyenne
        FROM jeux
        {where_clause}
        ORDER BY {tri} {ordre_sql}
        LIMIT ? OFFSET ?
    """
    params += [limite, offset]

    con = get_con()
    rows = con.execute(query, params).fetchall()
    con.close()

    keys = ["id", "titre", "joueurs", "duree", "categories", "themes", "mecanismes", "note_moyenne"]
    return [dict(zip(keys, row)) for row in rows]


# ─── GET /jeux/{id} ─────────────────────────────────────────────────────────────
# Détail d'un jeu par ID
@app.get("/jeux/{jeu_id}")
def detail_jeu(jeu_id: int):
    con = get_con()
    row = con.execute("SELECT * FROM jeux WHERE id = ?", [jeu_id]).fetchone()
    con.close()

    if not row:
        raise HTTPException(status_code=404, detail=f"Jeu {jeu_id} introuvable")

    keys = ["id", "titre", "joueurs", "duree", "categories", "themes", "mecanismes", "note_moyenne"]
    return dict(zip(keys, row))


# ─── GET /stats ─────────────────────────────────────────────────────────────────
# Statistiques globales de la collection
@app.get("/stats")
def statistiques():
    con = get_con()
    duree_expr = "TRY_CAST(SPLIT_PART(duree, ' ', 1) AS DOUBLE)"
    stats = con.execute(f"""
        SELECT
            COUNT(*)                                    AS total_jeux,
            ROUND(AVG(note_moyenne), 2)                 AS note_moyenne_collection,
            MAX(note_moyenne)                           AS meilleure_note,
            MIN(note_moyenne)                           AS moins_bonne_note,
            COALESCE(ROUND(AVG({duree_expr}), 0), 0)   AS duree_moyenne_min
        FROM jeux
    """).fetchone()
    con.close()

    return {
        "total_jeux": stats[0],
        "note_moyenne_collection": stats[1],
        "meilleure_note": stats[2],
        "moins_bonne_note": stats[3],
        "duree_moyenne_min": stats[4],
    }


# ─── GET /top ───────────────────────────────────────────────────────────────────
# Top N jeux par note
@app.get("/top")
def top_jeux(n: int = Query(10, ge=1, le=100, description="Nombre de jeux à retourner")):
    con = get_con()
    rows = con.execute("""
        SELECT id, titre, note_moyenne, categories
        FROM jeux
        WHERE note_moyenne > 0
        ORDER BY note_moyenne DESC
        LIMIT ?
    """, [n]).fetchall()
    con.close()

    return [{"id": r[0], "titre": r[1], "note_moyenne": r[2], "categories": r[3]} for r in rows]


# ─── GET /search ────────────────────────────────────────────────────────────────
# Recherche full-text simplifiée sur titre + thèmes + mécanismes
@app.get("/search")
def recherche(
    q: str = Query(..., min_length=2, description="Terme de recherche")
):
    con = get_con()
    rows = con.execute("""
        SELECT id, titre, joueurs, note_moyenne, categories, themes, mecanismes
        FROM jeux
        WHERE LOWER(titre)      LIKE LOWER(?)
           OR LOWER(themes)     LIKE LOWER(?)
           OR LOWER(mecanismes) LIKE LOWER(?)
           OR LOWER(categories) LIKE LOWER(?)
        ORDER BY note_moyenne DESC
    """, [f"%{q}%"] * 4).fetchall()
    con.close()

    keys = ["id", "titre", "joueurs", "note_moyenne", "categories", "themes", "mecanismes"]
    return [dict(zip(keys, row)) for row in rows]