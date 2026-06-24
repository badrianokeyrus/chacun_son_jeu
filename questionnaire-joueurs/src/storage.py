"""
Gestion de la persistance des réponses en CSV.
"""

import csv
from datetime import datetime
from pathlib import Path

from src.data import GAME_CATALOG, QUESTIONS


RESPONSES_PATH = Path("data") / "responses.csv"


def build_row(
    answers: dict[int, int],
    game_states: dict[str, int],
    info: dict,
    scores: dict[str, float],
    persona_name: str,
    ranked: list[dict],
    appetence: dict,
) -> dict:
    """Construit le dictionnaire complet pour une ligne CSV."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    row: dict = {
        "Timestamp":  ts,
        "Age":        info.get("age", ""),
        "Frequence":  info.get("freq", ""),
        "Niveau":     info.get("niveau", ""),
        "Contexte":   info.get("contexte", ""),
        "TypesJeux":  ", ".join(info.get("types_jeux", [])),
        "JouePour":   ", ".join(info.get("joue_pour", [])),
    }

    # États des jeux
    state_labels = {0: "inconnu", 1: "connu", 2: "adoré"}
    for g in GAME_CATALOG:
        row[f"jeu_{g.id}"] = state_labels[game_states.get(g.id, 0)]

    # Réponses Likert
    for qi, val in answers.items():
        row[f"Q{qi}"] = val

    # Scores
    row["score_maitrise"]   = f"{scores['purple']:.2f}"
    row["score_competition"] = f"{scores['amber']:.2f}"
    row["score_conflit"]    = f"{scores['coral']:.2f}"
    row["score_social"]     = f"{scores['green']:.2f}"
    row["persona"]          = persona_name

    # Types compatibles
    row["types_compatibles"] = " | ".join(
        (("✅ Très compatible " if i < 2 else "~ Compatible ") + gt["label"])
        for i, gt in enumerate(ranked[:6])
    )
    row["types_compatibles_detail"] = " | ".join(
        f"{gt['label']} (ex: {', '.join(gt['examples'][:3])})"
        for gt in ranked[:6]
    )

    # Appétence
    row["appetence_niveau"]       = appetence["niveau"]
    row["appetence_jeux_connus"]  = appetence["known_count"]
    row["appetence_coups_coeur"]  = appetence["loved_count"]
    row["appetence_niche_connus"] = appetence["niche_known"]
    row["coups_de_coeur"]         = ", ".join(g.name for g in appetence["loved_games"])

    return row


def save_response(row: dict) -> None:
    """Ajoute une ligne dans data/responses.csv (crée le fichier si besoin)."""
    RESPONSES_PATH.parent.mkdir(parents=True, exist_ok=True)
    file_exists = RESPONSES_PATH.exists()
    with open(RESPONSES_PATH, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()), delimiter=";")
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def row_to_csv_bytes(row: dict) -> bytes:
    """Sérialise une ligne en bytes CSV (pour st.download_button)."""
    import io
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(row.keys()), delimiter=";")
    writer.writeheader()
    writer.writerow(row)
    return ("\ufeff" + buf.getvalue()).encode("utf-8")
