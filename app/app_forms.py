"""
Point d'entrée de l'application Streamlit.
Lance avec : uv run streamlit run app/main.py
"""

import sys
from pathlib import Path

# Permet l'import de src.* depuis la racine du projet
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

from src.data import GAME_CATALOG, QUESTIONS, SECTION_META, PROFILE_DESCRIPTIONS
from src.scoring import compute_all_scores, compute_game_type_match, compute_appetence, compute_persona
from src.storage import build_row, save_response, row_to_csv_bytes
from src.ui import inject_css, render_hero, render_scores, render_reco, render_persona


# ──────────────────────────────────────────────
# CONFIG PAGE
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Profil Motivationnel du Joueur",
    page_icon="🎲",
    layout="centered",
)

inject_css()


# ──────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────
if "game_states" not in st.session_state:
    st.session_state.game_states = {g.id: 0 for g in GAME_CATALOG}
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "show_results" not in st.session_state:
    st.session_state.show_results = False
if "info" not in st.session_state:
    st.session_state.info = {}


# ──────────────────────────────────────────────
# HERO
# ──────────────────────────────────────────────
render_hero()


# ──────────────────────────────────────────────
# SECTION INFOS GÉNÉRALES
# ──────────────────────────────────────────────
with st.container(border=True):
    st.markdown(
        '<div class="section-header sh-teal">👤 Informations générales '
        '<span style="font-weight:400;font-size:.8rem">— Votre profil de joueur</span></div>',
        unsafe_allow_html=True,
    )
    st.info(
        "**Définition :** Un jeu de société est une activité sociale ludique, structurée par des règles, "
        "qui se pratique à plusieurs. Certains jeux sont spécifiquement conçus pour encourager la coopération "
        "ou la compétition, favorisant l'interaction entre les joueurs.",
        icon="ℹ️",
    )
    col1, col2 = st.columns(2)
    with col1:
        age    = st.number_input("Âge", min_value=10, max_value=99, value=None, placeholder="ex. 32")
        niveau = st.selectbox("Niveau perçu", ["— Choisir —", "Débutant", "Intermédiaire", "Avancé", "Expert"])
    with col2:
        freq    = st.selectbox("Fréquence de jeu", ["— Choisir —", "Jamais ou presque", "Mensuel", "Hebdomadaire", "Plusieurs fois par semaine"])
        contexte = st.selectbox("Contexte principal", ["— Choisir —", "Amis", "Famille", "Club / association", "En couple", "En ligne"])

    types_jeux = st.multiselect(
        "Types de jeux préférés (plusieurs possibles)",
        ["Stratégie","Coopératif","Party game","Ambiance / social","Placement / gestion",
         "Deck building","Wargame","Rôle / narrative","Enquête","Abstrait"],
    )
    joue_pour = st.multiselect(
        "Je joue surtout pour… (plusieurs possibles)",
        ["Gagner","Réfléchir","Partager un moment","Découvrir de nouveaux jeux","Me détendre"],
    )


# ──────────────────────────────────────────────
# SECTION JEUX
# ──────────────────────────────────────────────
with st.container(border=True):
    st.markdown(
        '<div class="section-header sh-blue">🃏 Vos jeux '
        '<span style="font-weight:400;font-size:.8rem">— 1 clic = Connu · 2 clics = J\'adore ❤️ · 3 clics = Pas connu</span></div>',
        unsafe_allow_html=True,
    )
    st.caption("Cliquez sur les jeux pour indiquer ceux que vous connaissez ou adorez.")

    cols = st.columns(4)
    for idx, g in enumerate(GAME_CATALOG):
        state = st.session_state.game_states[g.id]
        labels = ["—", "✓ Connu", "❤️ Adoré"]
        niche_badge = " 🔍" if g.niche else ""
        btn_label = f"{g.emoji} {g.name}{niche_badge}\n{labels[state]}"
        with cols[idx % 4]:
            if st.button(btn_label, key=f"game_{g.id}", width='stretch'):
                st.session_state.game_states[g.id] = (state + 1) % 3
                st.rerun()

    known = sum(1 for g in GAME_CATALOG if st.session_state.game_states[g.id] >= 1)
    loved = sum(1 for g in GAME_CATALOG if st.session_state.game_states[g.id] == 2)
    st.caption(f"✓ {known} jeux connus · ❤️ {loved} coups de cœur")


# ──────────────────────────────────────────────
# SECTIONS LIKERT
# ──────────────────────────────────────────────
st.info(
    "**Pour chaque affirmation**, indiquez votre niveau d'accord de 1 à 7 :\n"
    "1 = Pas du tout d'accord · 4 = Neutre · 7 = Tout à fait d'accord",
    icon="📋",
)

SECTION_STYLES = {1: "sh-purple", 2: "sh-amber", 3: "sh-coral", 4: "sh-green"}
LIKERT_LABELS = {
    1: "1 — Pas du tout", 2: "2", 3: "3",
    4: "4 — Neutre", 5: "5", 6: "6", 7: "7 — Tout à fait",
}

q_index = 1
for sec_num in range(1, 5):
    meta = SECTION_META[sec_num]
    with st.container(border=True):
        st.markdown(
            f'<div class="section-header {SECTION_STYLES[sec_num]}">'
            f'{meta["icon"]} Section {sec_num} — {meta["label"]}</div>',
            unsafe_allow_html=True,
        )
        for q_text in QUESTIONS[sec_num]:
            current = st.session_state.answers.get(q_index, 4)
            val = st.select_slider(
                f"Q{q_index} — {q_text}",
                options=[1, 2, 3, 4, 5, 6, 7],
                value=current,
                format_func=lambda x: LIKERT_LABELS[x],
                key=f"q_{q_index}",
            )
            st.session_state.answers[q_index] = val
            q_index += 1


# ──────────────────────────────────────────────
# BOUTON SOUMETTRE
# ──────────────────────────────────────────────
st.markdown("---")
col_btn, col_reset = st.columns([3, 1])
with col_btn:
    if st.button("🎯 Voir mon profil motivationnel", type="primary", width='stretch'):
        st.session_state.info = {
            "age":       age,
            "freq":      freq     if freq     != "— Choisir —" else "",
            "niveau":    niveau   if niveau   != "— Choisir —" else "",
            "contexte":  contexte if contexte != "— Choisir —" else "",
            "types_jeux": types_jeux,
            "joue_pour":  joue_pour,
        }
        st.session_state.show_results = True
        st.rerun()
with col_reset:
    if st.button("🔄 Réinitialiser", width='stretch'):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


# ──────────────────────────────────────────────
# RÉSULTATS
# ──────────────────────────────────────────────
if st.session_state.get("show_results"):
    answers     = st.session_state.answers
    game_states = st.session_state.game_states
    info        = st.session_state.info

    scores     = compute_all_scores(answers)
    ranked     = compute_game_type_match(scores)
    appetence  = compute_appetence(game_states)
    persona    = compute_persona(scores, appetence)

    dom_color = persona["dominant"]
    dom_meta  = next(m for m in SECTION_META.values() if m["color"] == dom_color)

    st.markdown("---")
    st.markdown("## 🎯 Votre profil motivationnel")
    st.success(f"{dom_meta['icon']} **Profil dominant : {dom_meta['label']}**")
    st.write(PROFILE_DESCRIPTIONS[dom_color])

    st.markdown("#### 📊 Vos scores")
    render_scores(scores)

    st.markdown("#### 🗂 Types de jeux compatibles")
    render_reco(ranked)

    st.markdown("#### 📚 Votre appétence aux jeux modernes")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Jeux connus",        appetence["known_count"])
    c2.metric("Coups de cœur",      appetence["loved_count"])
    c3.metric("Jeux niche connus",  appetence["niche_known"])
    c4.metric("Profil appétence",   appetence["niveau"])

    if appetence["loved_games"]:
        st.write(
            "**Coups de cœur déclarés :**",
            " · ".join(f"{g.emoji} {g.name}" for g in appetence["loved_games"]),
        )

    render_persona(persona)

    # Sauvegarde + export
    row = build_row(answers, game_states, info, scores, persona["name"], ranked, appetence)
    save_response(row)

    st.markdown("---")
    from datetime import datetime
    st.download_button(
        label="⬇️ Télécharger mes réponses (CSV)",
        data=row_to_csv_bytes(row),
        file_name=f"joueur_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv",
        mime="text/csv",
    )


def main():
    """Appelé par `uv run app` (entry point défini dans pyproject.toml)."""
    pass  # L'app Streamlit s'exécute au niveau module
