import json
from pathlib import Path

def determiner_profil(reponses: list[str]) -> dict:
    """
    Détermine le profil type à partir d'une liste de réponses A, B ou C.

    Règles :
    - Majorité de A           → Profil 1
    - Majorité de B           → Profil 2
    - Majorité de C           → Profil 3
    - Mix dominant A + C      → Profil 4
    - Mix dominant A + B      → Profil 5
    - Mix dominant B + C      → Profil 6

    Paramètre :
        reponses : liste de chaînes, chaque élément est "A", "B" ou "C"
                   (ou format "A. Texte..." — la lettre est extraite automatiquement)

    Retourne un dict avec :
        - comptes     : {'A': n, 'B': n, 'C': n}
        - profil      : numéro du profil (1 à 6)
        - description : libellé du profil
        - dominant    : lettre(s) dominante(s)
    """

    # --- Normalisation : extraire la lettre (A, B ou C) ---
    lettres = []
    for r in reponses:
        lettre = r.strip()[0].upper()
        if lettre not in ("A", "B", "C"):
            raise ValueError(f"Réponse invalide : '{r}'. Valeurs acceptées : A, B ou C.")
        lettres.append(lettre)

    # --- Comptage ---
    comptes = {"A": lettres.count("A"), "B": lettres.count("B"), "C": lettres.count("C")}
    total = len(lettres)

    # --- Seuil de majorité (stricte > 50%) et de mix (les 2 plus représentées) ---
    seuil_majorite = total / 2  # strictement supérieur → majorité absolue

    def majorite(lettre):
        return comptes[lettre] > seuil_majorite

    # Trouver les 2 lettres les plus représentées (pour les profils mix)
    classement = sorted(comptes, key=lambda l: comptes[l], reverse=True)
    top1, top2 = classement[0], classement[1]

    def est_mix(l1, l2):
        """Vrai si les 2 lettres dominantes sont l1 et l2 (sans majorité absolue)."""
        paire = {top1, top2}
        return paire == {l1, l2} and not majorite(top1)

    # --- Règles de profil ---
    profils = {
        1: ("Profil 1", "Majorité de A"),
        2: ("Profil 2", "Majorité de B"),
        3: ("Profil 3", "Majorité de C"),
        4: ("Profil 4", "Mix A + C"),
        5: ("Profil 5", "Mix A + B"),
        6: ("Profil 6", "Mix B + C"),
    }

    if majorite("A"):
        profil = 1
        dominant = "A"
    elif majorite("B"):
        profil = 2
        dominant = "B"
    elif majorite("C"):
        profil = 3
        dominant = "C"
    elif est_mix("A", "C"):
        profil = 4
        dominant = "A + C"
    elif est_mix("A", "B"):
        profil = 5
        dominant = "A + B"
    elif est_mix("B", "C"):
        profil = 6
        dominant = "B + C"
    else:
        # Cas d'égalité parfaite entre les 3 (ex: 5 questions → impossible,
        # mais prévu pour des questionnaires à nombre variable de questions)
        profil = None
        dominant = "Indéterminé (égalité parfaite)"

    nom_profil, desc_profil = profils.get(profil, (None, None)) if profil else ("—", "Indéterminé")

    return {
        "comptes": comptes,
        "profil": profil,
        "nom": nom_profil,
        "description": desc_profil,
        "dominant": dominant,
    }


# ---------------------------------------------------------------------------
# Exemples de test
# ---------------------------------------------------------------------------
if __name__ == "__main__":

    path = Path("data/preprocessing/reponses_questionnaire.json")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extraire toutes les réponses
    reponses = [v["reponse"] for v in data.values()]

    # Calcul du profil
    r = determiner_profil(reponses)

    print("Réponses :", reponses)
    print(f"Comptes  : A={r['comptes']['A']}  B={r['comptes']['B']}  C={r['comptes']['C']}")
    print(f"Dominant : {r['dominant']}")
    print(f"→ {r['nom']} — {r['description']}")