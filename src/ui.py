"""
Composants UI Streamlit réutilisables.
"""

import streamlit as st

from src.data import SECTION_META


# Palettes couleurs par dimension
COLOR_HEX = {
    "purple": "#534AB7",
    "amber":  "#EF9F27",
    "coral":  "#993C1D",
    "green":  "#3B6D11",
}
BG_HEX = {
    "purple": "#EEEDFE",
    "amber":  "#FAEEDA",
    "coral":  "#FAECE7",
    "green":  "#EAF3DE",
}


def inject_css() -> None:
    st.markdown("""
    <style>
    .hero-box {
      background:#3C3489; color:#EEEDFE;
      padding:2rem 1.5rem; border-radius:12px;
      text-align:center; margin-bottom:1.5rem;
    }
    .hero-box h1 { font-size:1.6rem; margin-bottom:.3rem; }
    .hero-box p  { font-size:.9rem; color:#AFA9EC; margin:0; }
    .section-header {
      padding:.6rem 1rem; border-radius:10px 10px 0 0;
      font-weight:600; font-size:.92rem;
      display:flex; align-items:center; gap:8px;
    }
    .sh-teal   { background:#E1F5EE; border-bottom:1px solid #5DCAA5; }
    .sh-purple { background:#EEEDFE; border-bottom:1px solid #AFA9EC; }
    .sh-amber  { background:#FAEEDA; border-bottom:1px solid #FAC775; }
    .sh-coral  { background:#FAECE7; border-bottom:1px solid #F0997B; }
    .sh-green  { background:#EAF3DE; border-bottom:1px solid #C0DD97; }
    .sh-blue   { background:#E6F1FB; border-bottom:1px solid #85B7EB; }
    .profile-bar { height:10px; border-radius:99px; margin:4px 0 2px; }
    .score-card  { border-radius:10px; padding:.8rem 1rem; margin-bottom:.5rem; }
    .reco-card   { border-radius:10px; padding:.75rem .9rem;
                   border:.5px solid transparent; margin-bottom:.5rem; }
    .match-high  { border-color:#5DCAA5; background:#E1F5EE; }
    .match-med   { border-color:#D3D1C7; background:#F1EFE8; }
    .persona-box { background:#EEEDFE; border:.5px solid #AFA9EC;
                   border-radius:10px; padding:.9rem 1rem; margin-top:1rem; }
    </style>
    """, unsafe_allow_html=True)


def render_hero() -> None:
    st.markdown("""
    <div class="hero-box">
      <h1>🎲 Profil Motivationnel du Joueur</h1>
      <p>Buts motivationnels aux jeux de société · environ 8 à 10 minutes</p>
    </div>
    """, unsafe_allow_html=True)


def render_scores(scores: dict[str, float]) -> None:
    sorted_scores = sorted(scores.items(), key=lambda x: -x[1])
    cols = st.columns(2)
    for i, (color, score) in enumerate(sorted_scores):
        meta = next(m for m in SECTION_META.values() if m["color"] == color)
        pct = round((score - 1) / 6 * 100)
        with cols[i % 2]:
            st.markdown(
                f'<div class="score-card" style="background:{BG_HEX[color]}">'
                f'<strong>{meta["icon"]} {meta["label"]}</strong><br>'
                f'<div class="profile-bar" style="width:{pct}%;background:{COLOR_HEX[color]}"></div>'
                f'<small>Score : {score:.1f} / 7</small>'
                f'</div>',
                unsafe_allow_html=True,
            )


def render_reco(ranked: list[dict]) -> None:
    cols = st.columns(2)
    for i, gt in enumerate(ranked[:6]):
        cls   = "match-high" if i < 2 else "match-med"
        badge = "✅ Très compatible" if i < 2 else ("〜 Compatible" if i < 4 else "")
        examples = ", ".join(gt["examples"][:4])
        with cols[i % 2]:
            st.markdown(
                f'<div class="reco-card {cls}">'
                f'<small style="color:#0F6E56">{badge}</small><br>'
                f'<strong>{gt["icon"]} {gt["label"]}</strong><br>'
                f'<small style="color:#5F5E5A">{gt["why"]}</small><br>'
                f'<small style="color:#534AB7">ex : {examples}</small>'
                f'</div>',
                unsafe_allow_html=True,
            )


def render_persona(persona: dict) -> None:
    st.markdown(
        f'<div class="persona-box">'
        f'<small style="color:#534AB7;font-weight:500">Persona estimé</small><br>'
        f'<strong style="font-size:1rem;color:#3C3489">{persona["name"]}</strong><br>'
        f'<small style="color:#3C3489">{persona["desc"]}</small>'
        f'</div>',
        unsafe_allow_html=True,
    )
