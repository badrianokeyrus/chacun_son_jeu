"""
Persistance des réponses.

Deux backends disponibles, sélectionnés automatiquement :
  - Google Sheets  si st.secrets["gcp_service_account"] est présent (prod)
  - CSV local      sinon (dev local)

Configuration Google Sheets dans .streamlit/secrets.toml :
    SPREADSHEET_ID = "1AbC..."          # ID de votre Google Sheet

    [gcp_service_account]
    type = "service_account"
    project_id = "..."
    private_key_id = "..."
    private_key = "-----BEGIN RSA PRIVATE KEY-----\\n..."
    client_email = "questionnaire@projet.iam.gserviceaccount.com"
    client_id = "..."
    token_uri = "https://oauth2.googleapis.com/token"
"""

import csv
import io
import logging
from datetime import datetime
from pathlib import Path

import streamlit as st

from src.data import GAME_CATALOG

log = logging.getLogger(__name__)

RESPONSES_PATH = Path("data") / "responses.csv"
SHEET_NAME = "responses"


# ──────────────────────────────────────────────
# Construction de la ligne de données
# ──────────────────────────────────────────────

def build_row(
    answers: dict[int, int],
    game_states: dict[str, int],
    info: dict,
    scores: dict[str, float],
    persona_name: str,
    ranked: list[dict],
    appetence: dict,
) -> dict:
    """Construit le dictionnaire complet représentant une réponse."""
    row: dict = {
        "Timestamp":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Age":        info.get("age", ""),
        "Frequence":  info.get("freq", ""),
        "Niveau":     info.get("niveau", ""),
        "Contexte":   info.get("contexte", ""),
        "TypesJeux":  ", ".join(info.get("types_jeux", [])),
        "JouePour":   ", ".join(info.get("joue_pour", [])),
    }

    state_labels = {0: "inconnu", 1: "connu", 2: "adoré"}
    for g in GAME_CATALOG:
        row[f"jeu_{g.id}"] = state_labels[game_states.get(g.id, 0)]

    for qi, val in answers.items():
        row[f"Q{qi}"] = val

    row["score_maitrise"]    = f"{scores['purple']:.2f}"
    row["score_competition"] = f"{scores['amber']:.2f}"
    row["score_conflit"]     = f"{scores['coral']:.2f}"
    row["score_social"]      = f"{scores['green']:.2f}"
    row["persona"]           = persona_name

    row["types_compatibles"] = " | ".join(
        (("✅ Très compatible " if i < 2 else "~ Compatible ") + gt["label"])
        for i, gt in enumerate(ranked[:6])
    )
    row["types_compatibles_detail"] = " | ".join(
        f"{gt['label']} (ex: {', '.join(gt['examples'][:3])})"
        for gt in ranked[:6]
    )

    row["appetence_niveau"]       = appetence["niveau"]
    row["appetence_jeux_connus"]  = appetence["known_count"]
    row["appetence_coups_coeur"]  = appetence["loved_count"]
    row["appetence_niche_connus"] = appetence["niche_known"]
    row["coups_de_coeur"]         = ", ".join(g.name for g in appetence["loved_games"])

    return row


# ──────────────────────────────────────────────
# Backend Google Sheets
# ──────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def _get_sheet():
    """
    Ouvre la feuille Google Sheets via le compte de service.
    Mis en cache par Streamlit pour éviter une reconnexion à chaque rerun.
    """
    import gspread
    from google.oauth2.service_account import Credentials

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]),
        scopes=scopes,
    )
    client = gspread.authorize(creds)
    spreadsheet_id = st.secrets["SPREADSHEET_ID"]
    spreadsheet = client.open_by_key(spreadsheet_id)

    # Crée l'onglet "responses" s'il n'existe pas encore
    try:
        sheet = spreadsheet.worksheet(SHEET_NAME)
    except gspread.WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(title=SHEET_NAME, rows=10000, cols=100)

    return sheet


def _save_to_sheets(row: dict) -> None:
    """Ajoute une ligne dans Google Sheets. Crée l'en-tête si la feuille est vide."""
    sheet = _get_sheet()
    headers = sheet.row_values(1)  # ligne 1 = en-têtes

    if not headers:
        # Première écriture : on pose les en-têtes
        sheet.append_row(list(row.keys()), value_input_option="RAW")

    sheet.append_row(list(row.values()), value_input_option="USER_ENTERED")


# ──────────────────────────────────────────────
# Backend CSV local (fallback dev)
# ──────────────────────────────────────────────

def _save_to_csv(row: dict) -> None:
    """Sauvegarde dans data/responses.csv (dev local uniquement)."""
    RESPONSES_PATH.parent.mkdir(parents=True, exist_ok=True)
    file_exists = RESPONSES_PATH.exists()
    with open(RESPONSES_PATH, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()), delimiter=";")
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


# ──────────────────────────────────────────────
# Point d'entrée unique
# ──────────────────────────────────────────────

def save_response(row: dict) -> None:
    """
    Sauvegarde une réponse.
    - Google Sheets si les secrets sont configurés (production Streamlit Cloud)
    - CSV local sinon (développement)
    """
    if "gcp_service_account" in st.secrets:
        try:
            _save_to_sheets(row)
            log.info("Réponse enregistrée dans Google Sheets.")
        except Exception as exc:
            log.error("Échec Google Sheets, fallback CSV : %s", exc)
            _save_to_csv(row)
    else:
        _save_to_csv(row)
        log.info("Réponse enregistrée dans %s.", RESPONSES_PATH)


# ──────────────────────────────────────────────
# Export CSV individuel (bouton téléchargement)
# ──────────────────────────────────────────────

def row_to_csv_bytes(row: dict) -> bytes:
    """Sérialise une ligne en bytes CSV UTF-8 BOM (pour st.download_button)."""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(row.keys()), delimiter=";")
    writer.writeheader()
    writer.writerow(row)
    return ("\ufeff" + buf.getvalue()).encode("utf-8")
