# src/app.py
import streamlit as st
import requests
import duckdb
import pandas as pd
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
API_URL = "http://localhost:8000"
DB_PATH  = "data/db/collection.duckdb"

st.set_page_config(
    page_title="🎲 Ma Collection",
    page_icon="🎲",
    layout="wide",
)

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
h1, h2, h3 { font-family: 'Playfair Display', serif; }

[data-testid="stAppViewContainer"] {
    background: #eeeeee;
    color: #1a1825;
}
[data-testid="stSidebar"] { background: #eeeeee; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: transparent;
    border-bottom: 1px solid #2d2b3d;
    padding-bottom: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #a7a9be;
    font-family: 'DM Sans', sans-serif;
    font-size: 15px;
    font-weight: 500;
    letter-spacing: .04em;
    padding: 10px 24px;
    border-radius: 8px 8px 0 0;
    border: none;
}
.stTabs [aria-selected="true"] {
    background: #eeeeee !important;
    color: #ff8906 !important;
    border-bottom: 2px solid #ff8906 !important;
}

/* Cards */
.metric-card {
    background: #eeeeee;
    border: 1px solid #2d2b3d;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
}
.metric-card .value {
    font-family: 'Playfair Display', serif;
    font-size: 2.4rem;
    color: #ff8906;
    line-height: 1;
}
.metric-card .label {
    font-size: 12px;
    color: #a7a9be;
    text-transform: uppercase;
    letter-spacing: .08em;
    margin-top: 6px;
}

/* Section titles */
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    color: #1a1825;
    margin: 32px 0 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid #2d2b3d;
}

/* Buttons */
.stButton > button {
    background: #ff8906;
    color: #0f0e17;
    font-weight: 600;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-family: 'DM Sans', sans-serif;
    letter-spacing: .03em;
    transition: opacity .2s;
}
.stButton > button:hover { opacity: .85; }

/* Inputs */
.stTextInput input, .stNumberInput input,
.stSelectbox > div > div, .stSlider {
    background: #eeeeee !important;
    border-color: #2d2b3d !important;
    color: #1a1825 !important;
    border-radius: 8px !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border: 1px solid #2d2b3d;
    border-radius: 12px;
    overflow: hidden;
}

/* Success / error */
.stAlert { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='padding: 32px 0 8px'>
    <span style='font-family:Playfair Display,serif;font-size:2.2rem;color:#1a1825'>
        🎲 Ma Collection de Jeux
    </span>
    <span style='color:#a7a9be;font-size:14px;margin-left:16px'>
        Powered by DuckDB & FastAPI
    </span>
</div>
""", unsafe_allow_html=True)

# ── Helpers API ───────────────────────────────────────────────────────────────
def api_get(endpoint: str, params: dict = None):
    try:
        r = requests.get(f"{API_URL}{endpoint}", params=params, timeout=5)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, "❌ Impossible de joindre l'API. Lancez `uvicorn src.api_data:app --reload`."
    except Exception as e:
        return None, f"❌ Erreur API : {e}"

# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2 = st.tabs(["🔍  Explorer la collection", "➕  Ajouter un jeu"])

# ══════════ ONGLET 1 — EXPLORER ═══════════════════════════════════════════════
with tab1:

    # ── Stats globales ────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Statistiques de la collection</div>', unsafe_allow_html=True)
    stats, err = api_get("/stats")
    if err:
        st.error(err)
    elif stats:
        c1, c2, c3, c4, c5 = st.columns(5)
        for col, val, label in [
            (c1, stats["total_jeux"],               "Jeux"),
            (c2, stats["note_moyenne_collection"],   "Note moyenne"),
            (c3, stats["meilleure_note"],            "Meilleure note"),
            (c4, stats["moins_bonne_note"],          "Note la plus basse"),
            (c5, f'{int(stats["duree_moyenne_min"])} min', "Durée moyenne"),
        ]:
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="value">{val}</div>
                    <div class="label">{label}</div>
                </div>""", unsafe_allow_html=True)

    # ── Top jeux ──────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">🏆 Top jeux par note</div>', unsafe_allow_html=True)
    col_slider, _ = st.columns([1, 3])
    with col_slider:
        n_top = st.slider("Nombre de jeux", 3, 50, 10, key="top_n")

    top, err = api_get("/top", {"n": n_top})
    if err:
        st.error(err)
    elif top:
        df_top = pd.DataFrame(top)
        df_top.index = df_top.index + 1          # classement à partir de 1
        df_top.columns = ["ID", "Titre", "Note", "Catégorie(s)"]
        st.dataframe(df_top, use_container_width=True, hide_index=False)

    # ── Recherche & filtres ───────────────────────────────────────────────────
    st.markdown('<div class="section-title">🔎 Recherche & filtres</div>', unsafe_allow_html=True)

    with st.expander("Filtres avancés", expanded=True):
        f1, f2, f3 = st.columns(3)
        with f1:
            f_titre     = st.text_input("Titre", placeholder="ex : Catan")
            f_categorie = st.text_input("Catégorie", placeholder="ex : Jeu de plateau")
        with f2:
            f_theme     = st.text_input("Thème", placeholder="ex : Historique")
            f_mecanisme = st.text_input("Mécanisme", placeholder="ex : Gestion de ressources")
        with f3:
            f_note_min  = st.number_input("Note min", 0.0, 10.0, 0.0, 0.5)
            f_note_max  = st.number_input("Note max", 0.0, 10.0, 10.0, 0.5)
            f_limite    = st.number_input("Limite résultats", 5, 500, 50, 5)

        col_tri, col_ordre, col_btn = st.columns([2, 2, 1])
        with col_tri:
            f_tri   = st.selectbox("Trier par", ["titre", "note_moyenne", "duree", "id"])
        with col_ordre:
            f_ordre = st.selectbox("Ordre", ["asc", "desc"])
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            rechercher = st.button("Rechercher", use_container_width=True)

    if rechercher:
        params = {
            k: v for k, v in {
                "titre":     f_titre     or None,
                "categorie": f_categorie or None,
                "theme":     f_theme     or None,
                "mecanisme": f_mecanisme or None,
                "note_min":  f_note_min  if f_note_min > 0   else None,
                "note_max":  f_note_max  if f_note_max < 10  else None,
                "tri":       f_tri,
                "ordre":     f_ordre,
                "limite":    f_limite,
            }.items() if v is not None
        }
        resultats, err = api_get("/jeux", params)
        if err:
            st.error(err)
        elif resultats:
            df_res = pd.DataFrame(resultats)
            df_res.columns = ["ID", "Titre", "Joueurs", "Durée (min)",
                               "Catégorie(s)", "Thème(s)", "Mécanisme(s)", "Note"]
            st.success(f"{len(df_res)} jeu(x) trouvé(s)")
            st.dataframe(df_res, use_container_width=True, hide_index=True)
        else:
            st.info("Aucun jeu ne correspond à ces critères.")

# ══════════ ONGLET 2 — AJOUTER ════════════════════════════════════════════════
with tab2:

    st.markdown('<div class="section-title">➕ Ajouter un jeu à la collection</div>', unsafe_allow_html=True)
    st.caption("Les champs avec \\* sont obligatoires. Les listes peuvent contenir plusieurs valeurs séparées par des virgules.")

    with st.form("form_ajout", clear_on_submit=True):
        col_a, col_b = st.columns(2)

        with col_a:
            jeu_id    = st.number_input("ID *", min_value=1, step=1)
            titre     = st.text_input("Titre *", placeholder="ex : Wingspan")
            joueurs   = st.text_input("Joueur(s) *", placeholder="ex : 1 — 5")
            duree     = st.number_input("Durée (min) *", min_value=1, step=5, value=60)

        with col_b:
            note      = st.number_input("Note moyenne", 0.0, 10.0, 0.0, 0.1)
            categories = st.text_input("Catégorie(s)", placeholder="ex : Jeu de plateau, Jeu de cartes")
            themes    = st.text_input("Thème(s)", placeholder="ex : Nature, Animaux")
            mecanismes = st.text_input("Mécanisme(s)", placeholder="ex : Gestion de ressources, Draft")

        submitted = st.form_submit_button("💾 Ajouter à la collection", use_container_width=True)

    if submitted:
        # Validation
        errors = []
        if not titre.strip():
            errors.append("Le titre est obligatoire.")
        if not joueurs.strip():
            errors.append("Le champ Joueur(s) est obligatoire.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            try:
                con = duckdb.connect(str(DB_PATH), read_only=False)

                # Vérification doublon
                existe = con.execute("SELECT COUNT(*) FROM jeux WHERE id = ?", [int(jeu_id)]).fetchone()[0]
                if existe:
                    st.warning(f"⚠️ Un jeu avec l'ID {jeu_id} existe déjà dans la collection.")
                    con.close()
                else:
                    con.execute("""
                        INSERT INTO jeux
                            (id, titre, joueurs, duree, categories, themes, mecanismes, note_moyenne)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, [
                        int(jeu_id),
                        titre.strip(),
                        joueurs.strip(),
                        int(duree),
                        categories.strip(),
                        themes.strip(),
                        mecanismes.strip(),
                        float(note),
                    ])
                    con.close()
                    st.success(f"✅ **{titre}** a bien été ajouté à la collection !")
                    st.balloons()

            except Exception as e:
                st.error(f"❌ Erreur lors de l'insertion : {e}")

    # ── Aperçu des derniers ajouts ─────────────────────────────────────────────
    st.markdown('<div class="section-title">📋 Derniers jeux ajoutés</div>', unsafe_allow_html=True)
    try:
        con = duckdb.connect(str(DB_PATH), read_only=True)
        df_recent = con.execute("""
            SELECT id AS "ID", titre AS "Titre", joueurs AS "Joueurs",
                   duree AS "Durée (min)", categories AS "Catégorie(s)",
                   note_moyenne AS "Note"
            FROM jeux
            ORDER BY rowid DESC
            LIMIT 10
        """).df()
        con.close()
        st.dataframe(df_recent, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Impossible de charger les données : {e}")