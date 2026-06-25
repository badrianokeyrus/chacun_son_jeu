# Chacun Son Jeu

Système complet de profilage motivationnel du joueur de jeux de société, avec gestion de collection.

## Architecture

```
                  ┌─────────────────────────┐
                  │  data/input/            │
                  │  ├── collection.json    │
                  │  └── wishlist.json      │
                  └────────────┬────────────┘
                               │ src/game_selection/collect.py
                               ▼
                  ┌─────────────────────────┐
                  │  data/db/               │
                  │  └── collection.duckdb  │
                  └────────────┬────────────┘
                               │ src/game_selection/api_data.py (FastAPI)
                               ▼
          ┌────────────────────────────────────────┐
          │           Applications Streamlit        │
          │                                        │
          │  app/app_forms.py   app/app_select.py  │
          │  :8501              :8502               │
          └────────────────────────────────────────┘
```

**Stack :**
- **Streamlit** — deux apps web interactives
- **FastAPI + DuckDB** — API REST sur la collection de jeux
- **CSV / Google Sheets** — persistance des réponses au questionnaire
- **uv** — gestionnaire de dépendances

---

## Structure du projet

```
chacun_son_jeu/
├── app/
│   ├── app_forms.py          # App questionnaire motivationnel (port 8501)
│   └── app_select.py         # App navigateur de collection (port 8502)
├── src/
│   ├── data.py               # Questions, catalogue jeux, personas, types de jeux
│   ├── scoring.py            # Calcul des scores et matching profil/type
│   ├── storage.py            # Persistance CSV et Google Sheets
│   ├── ui.py                 # Composants Streamlit réutilisables
│   └── game_selection/
│       ├── collect.py        # Script d'alimentation DuckDB depuis JSON
│       └── api_data.py       # API FastAPI sur la collection (DuckDB)
├── data/
│   ├── input/
│   │   ├── collection.json   # Catalogue complet (source)
│   │   └── wishlist.json     # Liste de souhaits (source)
│   ├── db/
│   │   └── collection.duckdb # Base DuckDB (générée par collect.py)
│   ├── responses.csv         # Réponses collectées (auto-généré)
│   └── summary_results.csv   # Statistiques résumées
├── analysis/
│   └── explore.py            # Analyse des réponses collectées
├── Makefile
├── pyproject.toml
└── GOOGLE_SHEETS_SETUP.md
```

---

## Prérequis

- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/)

---

## Installation

```bash
uv sync
```

---

## Pipeline de données

### 1. Alimenter la base DuckDB

Lit `data/input/collection.json`, filtre les jeux de base (`Type=basegame`) et peuple `data/db/collection.duckdb` :

```bash
make data
# ou manuellement :
uv run python -m src.game_selection.collect
```

La table créée s'appelle `jeux` avec les colonnes : `id`, `titre`, `joueurs`, `duree`, `categories`, `themes`, `mecanismes`, `note_moyenne`.

### 2. Lancer l'API FastAPI (optionnel)

L'app `app_select.py` se connecte à `http://localhost:8000`. Sans l'API, elle affiche un message d'erreur informatif.

```bash
make api
# ou manuellement :
uv run uvicorn src.game_selection.api_data:app --reload
```

---

## Lancer les applications

### App questionnaire (`app_forms.py`) — port 8501

Questionnaire en 4 sections (28 questions Likert) + reconnaissance de 24 jeux.
Génère un profil motivationnel et des recommandations de types de jeux.

```bash
make forms
```

### App collection (`app_select.py`) — port 8502

Navigateur de la collection DuckDB : statistiques, recherche, filtres, ajout de jeux.
**Nécessite l'API FastAPI** (`make api`) lancée en parallèle.

```bash
make select
```

### Les deux apps en même temps

```bash
make run
```

---

## Développement

```bash
# Linter
make lint

# Analyser les réponses collectées
make analysis

# Tout installer (dépendances dev incluses)
uv sync --dev
```

---

## Persistance des réponses

Par défaut les réponses sont sauvegardées dans `data/responses.csv`.

Pour utiliser Google Sheets en production, voir [GOOGLE_SHEETS_SETUP.md](GOOGLE_SHEETS_SETUP.md).

> Sur Streamlit Cloud, `data/responses.csv` ne persiste pas entre redémarrages.
> Configurer Google Sheets pour une collecte durable.

---

## Docker Compose

Lance les 3 services d'un coup (API + les deux apps Streamlit) :

```bash
# 1. Construire les images
make docker-build

# 2. Alimenter la base DuckDB (à faire une seule fois)
make data

# 3. Démarrer tous les services
make docker-up
```

| Service | URL |
|---------|-----|
| Questionnaire | http://localhost:8501 |
| Collection | http://localhost:8502 |
| API FastAPI | http://localhost:8000 |
| Docs API | http://localhost:8000/docs |

```bash
# Voir les logs en temps réel
make docker-logs

# Arrêter tous les services
make docker-down
```

> Le dossier `data/` est monté en volume : la base DuckDB et les réponses CSV persistent sur l'hôte.
> En Docker, `app_select.py` communique avec l'API via le réseau interne (`http://api:8000`),
> configurable via la variable d'environnement `API_URL`.

---

## Déploiement sur Streamlit Community Cloud

1. Pousser sur GitHub
2. Connecter le repo sur [share.streamlit.io](https://share.streamlit.io)
3. Fichier principal : `app/app_forms.py` ou `app/app_select.py` selon l'app à déployer
4. Configurer les secrets Streamlit Cloud (voir [GOOGLE_SHEETS_SETUP.md](GOOGLE_SHEETS_SETUP.md))
