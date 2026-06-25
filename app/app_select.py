# app/app_select.py
import os
import streamlit as st
import requests
import duckdb
import pandas as pd

API_URL = os.getenv("API_URL", "http://localhost:8000")
DB_PATH = "data/db/collection.duckdb"

st.set_page_config(
    page_title="🎲 Ma Collection",
    page_icon="🎲",
    layout="wide",
)

# ── CSS (aligné sur le design de app_forms.py) ────────────────────────────────
st.markdown("""
<style>
.hero-box {
  background: #3C3489; color: #EEEDFE;
  padding: 2rem 1.5rem; border-radius: 12px;
  text-align: center; margin-bottom: 1.5rem;
}
.hero-box h1 { font-size: 1.8rem; margin-bottom: .3rem; }
.hero-box p  { font-size: .9rem; color: #AFA9EC; margin: 0; }

.section-header {
  padding: .6rem 1rem; border-radius: 8px 8px 0 0;
  font-weight: 600; font-size: .92rem;
  margin-bottom: .75rem;
}
.sh-purple { background: #EEEDFE; border-bottom: 2px solid #AFA9EC; color: #3C3489; }
.sh-amber  { background: #FAEEDA; border-bottom: 2px solid #FAC775; color: #7A4E00; }
.sh-blue   { background: #E6F1FB; border-bottom: 2px solid #85B7EB; color: #1A4A7A; }
.sh-teal   { background: #E1F5EE; border-bottom: 2px solid #5DCAA5; color: #0F5C3C; }
.sh-green  { background: #EAF3DE; border-bottom: 2px solid #C0DD97; color: #2E5209; }

.metric-card {
  background: #EEEDFE;
  border: 1px solid #AFA9EC;
  border-radius: 12px;
  padding: 20px 16px;
  text-align: center;
}
.metric-card .value {
  font-size: 2rem;
  font-weight: 700;
  color: #3C3489;
  line-height: 1;
}
.metric-card .label {
  font-size: 11px;
  color: #534AB7;
  text-transform: uppercase;
  letter-spacing: .08em;
  margin-top: 6px;
}
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-box">
  <h1>🎲 Ma Collection de Jeux</h1>
  <p>Explorer, rechercher et enrichir votre bibliothèque ludique · Powered by DuckDB &amp; FastAPI</p>
</div>
""", unsafe_allow_html=True)


# ── Helpers API ───────────────────────────────────────────────────────────────
def api_get(endpoint: str, params: dict = None):
    try:
        r = requests.get(f"{API_URL}{endpoint}", params=params, timeout=5)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, (
            "❌ Impossible de joindre l'API. "
            "Lancez `uvicorn src.game_selection.api_data:app --reload`."
        )
    except Exception as e:
        return None, f"❌ Erreur API : {e}"


# ── Listes déroulantes depuis la DB ──────────────────────────────────────────
@st.cache_data(ttl=300)
def get_distinct_values(column: str) -> list:
    try:
        con = duckdb.connect(DB_PATH, read_only=True)
        rows = con.execute(f"""
            SELECT DISTINCT TRIM(val) AS v
            FROM (SELECT unnest(string_split({column}, ',')) AS val FROM jeux)
            WHERE TRIM(val) != ''
            ORDER BY v
        """).fetchall()
        con.close()
        return ["— Tout —"] + [r[0] for r in rows]
    except Exception:
        return ["— Tout —"]


# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2 = st.tabs(["🔍  Explorer la collection", "➕  Ajouter un jeu"])

# ══════════ ONGLET 1 — EXPLORER ═══════════════════════════════════════════════
with tab1:

    # ── Statistiques de la collection ─────────────────────────────────────────
    with st.container(border=True):
        st.markdown(
            '<div class="section-header sh-purple">📊 Statistiques de la collection</div>',
            unsafe_allow_html=True,
        )
        stats, err = api_get("/stats")
        if err:
            st.error(err)
        elif stats:
            c1, c2, c3, c4, c5 = st.columns(5)
            for col, val, label in [
                (c1, stats["total_jeux"],                       "Jeux"),
                (c2, stats["note_moyenne_collection"],           "Note moyenne"),
                (c3, stats["meilleure_note"],                    "Meilleure note"),
                (c4, stats["moins_bonne_note"],                  "Note la plus basse"),
                (c5, f'{int(stats["duree_moyenne_min"])} min',   "Durée moyenne"),
            ]:
                with col:
                    st.markdown(
                        f'<div class="metric-card">'
                        f'<div class="value">{val}</div>'
                        f'<div class="label">{label}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

    # ── Top jeux par note ─────────────────────────────────────────────────────
    with st.container(border=True):
        st.markdown(
            '<div class="section-header sh-amber">🏆 Top jeux par note</div>',
            unsafe_allow_html=True,
        )
        col_slider, _ = st.columns([1, 3])
        with col_slider:
            n_top = st.slider("Nombre de jeux", 3, 50, 10, key="top_n")

        top, err = api_get("/top", {"n": n_top})
        if err:
            st.error(err)
        elif top:
            df_top = pd.DataFrame(top)
            df_top.index = df_top.index + 1
            df_top.columns = ["ID", "Titre", "Note", "Catégorie(s)"]
            st.dataframe(df_top, use_container_width=True, hide_index=False)

    # ── Recherche & filtres ───────────────────────────────────────────────────
    with st.container(border=True):
        st.markdown(
            '<div class="section-header sh-blue">🔎 Recherche & filtres</div>',
            unsafe_allow_html=True,
        )

        categories_list = get_distinct_values("categories")
        themes_list     = get_distinct_values("themes")
        mecanismes_list = get_distinct_values("mecanismes")

        f1, f2, f3 = st.columns(3)
        with f1:
            f_titre     = st.text_input("Titre", placeholder="ex : Catan")
            f_categorie = st.selectbox("Catégorie", categories_list, key="sel_cat")
        with f2:
            f_theme     = st.selectbox("Thème", themes_list, key="sel_theme")
            f_mecanisme = st.selectbox("Mécanisme", mecanismes_list, key="sel_mec")
        with f3:
            f_note_min = st.number_input("Note min", 0.0, 10.0, 0.0, 0.5)
            f_note_max = st.number_input("Note max", 0.0, 10.0, 10.0, 0.5)
            f_limite   = st.number_input("Limite résultats", 5, 500, 50, 5)

        col_tri, col_ordre, col_btn = st.columns([2, 2, 1])
        with col_tri:
            f_tri   = st.selectbox("Trier par", ["titre", "note_moyenne", "duree", "id"])
        with col_ordre:
            f_ordre = st.selectbox("Ordre", ["asc", "desc"])
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            rechercher = st.button("🔍 Rechercher", use_container_width=True)

    if rechercher:
        params = {
            k: v for k, v in {
                "titre":     f_titre     or None,
                "categorie": f_categorie if f_categorie != "— Tout —" else None,
                "theme":     f_theme     if f_theme     != "— Tout —" else None,
                "mecanisme": f_mecanisme if f_mecanisme != "— Tout —" else None,
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
            df_res.columns = [
                "ID", "Titre", "Joueurs", "Durée (min)",
                "Catégorie(s)", "Thème(s)", "Mécanisme(s)", "Note",
            ]
            st.success(f"{len(df_res)} jeu(x) trouvé(s)")
            st.dataframe(df_res, use_container_width=True, hide_index=True)
        else:
            st.info("Aucun jeu ne correspond à ces critères.")

# ══════════ ONGLET 2 — AJOUTER ════════════════════════════════════════════════
with tab2:

    # ── Formulaire d'ajout ────────────────────────────────────────────────────
    with st.container(border=True):
        st.markdown(
            '<div class="section-header sh-teal">➕ Ajouter un jeu à la collection</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "Les champs avec \\* sont obligatoires. "
            "Les listes peuvent contenir plusieurs valeurs séparées par des virgules."
        )

        with st.form("form_ajout", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                jeu_id     = st.number_input("ID *", min_value=1, step=1)
                titre      = st.text_input("Titre *", placeholder="ex : Wingspan")
                joueurs    = st.text_input("Joueur(s) *", placeholder="ex : 1 — 5")
                duree      = st.number_input("Durée (min) *", min_value=1, step=5, value=60)
            with col_b:
                note       = st.number_input("Note moyenne", 0.0, 10.0, 0.0, 0.1)
                categories = st.text_input("Catégorie(s)", placeholder="ex : Jeu de plateau, Jeu de cartes")
                themes     = st.text_input("Thème(s)", placeholder="ex : Nature, Animaux")
                mecanismes = st.text_input("Mécanisme(s)", placeholder="ex : Gestion de ressources, Draft")

            submitted = st.form_submit_button("💾 Ajouter à la collection", use_container_width=True)

    if submitted:
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
                existe = con.execute(
                    "SELECT COUNT(*) FROM jeux WHERE id = ?", [int(jeu_id)]
                ).fetchone()[0]
                if existe:
                    st.warning(f"⚠️ Un jeu avec l'ID {jeu_id} existe déjà dans la collection.")
                    con.close()
                else:
                    con.execute(
                        """
                        INSERT INTO jeux
                            (id, titre, joueurs, duree, categories, themes, mecanismes, note_moyenne)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        [
                            int(jeu_id), titre.strip(), joueurs.strip(), int(duree),
                            categories.strip(), themes.strip(), mecanismes.strip(), float(note),
                        ],
                    )
                    con.close()
                    st.success(f"✅ **{titre}** a bien été ajouté à la collection !")
                    st.balloons()
                    st.cache_data.clear()
            except Exception as e:
                st.error(f"❌ Erreur lors de l'insertion : {e}")

    # ── Aperçu des derniers ajouts ────────────────────────────────────────────
    with st.container(border=True):
        st.markdown(
            '<div class="section-header sh-green">📋 Derniers jeux ajoutés</div>',
            unsafe_allow_html=True,
        )
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
