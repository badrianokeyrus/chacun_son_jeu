"""
Logique de calcul des scores, matching de types de jeux et personas.
"""

from src.data import (
    QUESTIONS, GAME_CATALOG, GAME_TYPES, PERSONAS,
    GameType,
)


def get_section_score(sec_num: int, answers: dict[int, int]) -> float:
    """Calcule le score moyen d'une section (1–7)."""
    offset = sum(len(QUESTIONS[s]) for s in range(1, sec_num))
    n = len(QUESTIONS[sec_num])
    vals = [answers.get(offset + i + 1, 0) for i in range(n)]
    return sum(vals) / n if vals else 0.0


def compute_all_scores(answers: dict[int, int]) -> dict[str, float]:
    """Retourne les 4 scores (purple, amber, coral, green)."""
    return {
        "purple": get_section_score(1, answers),
        "amber":  get_section_score(2, answers),
        "coral":  get_section_score(3, answers),
        "green":  get_section_score(4, answers),
    }


def compute_game_type_match(scores: dict[str, float]) -> list[dict]:
    """
    Retourne les types de jeux triés par compatibilité décroissante.
    Chaque élément est un dict avec les champs du GameType + match_frac.
    """
    results = []
    for gt in GAME_TYPES:
        match_count = sum(
            1 for dim, rng in gt.match.items()
            if rng[0] <= scores[dim] <= rng[1]
        )
        results.append({
            "id": gt.id,
            "label": gt.label,
            "icon": gt.icon,
            "why": gt.why,
            "examples": gt.examples,
            "match_frac": match_count / len(gt.match),
        })
    return sorted(results, key=lambda x: -x["match_frac"])


def compute_appetence(game_states: dict[str, int]) -> dict:
    """Calcule les métriques d'appétence aux jeux modernes."""
    known   = [g for g in GAME_CATALOG if game_states.get(g.id, 0) >= 1]
    loved   = [g for g in GAME_CATALOG if game_states.get(g.id, 0) == 2]
    niche_known = [g for g in known if g.niche]
    loved_niche = [g for g in loved if g.niche]

    app_score = len(known) / len(GAME_CATALOG)
    niveau = "Confirmé" if app_score >= 0.5 else "Intermédiaire" if app_score >= 0.25 else "Découvreur"

    return {
        "score":        app_score,
        "niveau":       niveau,
        "known_count":  len(known),
        "loved_count":  len(loved),
        "niche_known":  len(niche_known),
        "loved_niche":  len(loved_niche),
        "loved_games":  loved,
    }


def compute_persona(scores: dict[str, float], appetence: dict) -> dict[str, str]:
    """Détermine le persona en fonction du profil dominant + appétence."""
    sorted_scores = sorted(scores.items(), key=lambda x: -x[1])
    dom = sorted_scores[0][0]
    sec = sorted_scores[1][0]
    key = f"{dom}-{sec}"

    base = PERSONAS.get(key, {
        "name": "Joueur polyvalent",
        "desc": "Votre profil est équilibré entre plusieurs motivations. Vous vous adaptez facilement à différents types de jeux et de contextes.",
    })

    suffix = ""
    if appetence["score"] >= 0.5 and appetence["loved_niche"] >= 1:
        suffix = " Curieux des sorties récentes et des jeux méconnus — un vrai dénicheur."
    elif appetence["score"] >= 0.5:
        suffix = " Sensible aux jeux modernes, vous vous tenez au courant des nouvelles sorties."
    elif appetence["loved_niche"] >= 1:
        suffix = " Attiré par les jeux moins connus, vous cherchez des expériences originales hors des sentiers battus."

    return {"name": base["name"], "desc": base["desc"] + suffix, "dominant": dom}
