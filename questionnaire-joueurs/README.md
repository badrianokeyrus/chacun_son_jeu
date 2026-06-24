# 🎲 Questionnaire — Profil Motivationnel du Joueur

## Structure

```
questionnaire-joueurs/
├── app/
│   └── main.py          # Point d'entrée Streamlit
├── src/
│   ├── data.py          # Données : questions, jeux, personas
│   ├── scoring.py       # Calcul des scores et profils
│   ├── storage.py       # Lecture/écriture CSV
│   └── ui.py            # Composants Streamlit réutilisables
├── data/
│   └── responses.csv    # Réponses collectées (auto-généré)
├── analysis/
│   ├── explore.py       # Exploration des données
│   └── README.md
├── pyproject.toml
└── README.md
```

## Démarrage rapide

```bash
# Installer les dépendances
uv sync

# Lancer l'app
uv run streamlit run app/main.py
```

## Développement

```bash
# Installer les dépendances de dev (pytest, ruff)
uv sync --dev

# Linter
uv run ruff check src/ app/

# Analyser les réponses
uv run python analysis/explore.py
```

## Déploiement sur Streamlit Community Cloud

1. Pousser sur GitHub (avec `requirements.txt` ou en utilisant `uv export`)
2. Connecter le repo sur [share.streamlit.io](https://share.streamlit.io)
3. Fichier principal : `app/main.py`

> ⚠️ Sur Streamlit Cloud, `data/responses.csv` ne persiste pas entre redémarrages.
> Pour une collecte durable, brancher Google Sheets via `gspread`.
