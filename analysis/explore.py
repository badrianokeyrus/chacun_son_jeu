"""
Exploration rapide des réponses collectées.
Usage : uv run python analysis/explore.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd

RESPONSES = Path("data") / "responses.csv"


def load() -> pd.DataFrame:
    if not RESPONSES.exists():
        print("Aucune réponse collectée pour l'instant (data/responses.csv introuvable).")
        sys.exit(0)
    return pd.read_csv(RESPONSES, sep=";", encoding="utf-8-sig")


def summary(df: pd.DataFrame) -> None:
    print(f"\n{'='*50}")
    print(f"  {len(df)} répondant(s)")
    print(f"{'='*50}\n")

    score_cols = ["score_maitrise", "score_competition", "score_conflit", "score_social"]
    print("── Scores moyens ──")
    for col in score_cols:
        if col in df.columns:
            vals = pd.to_numeric(df[col], errors="coerce")
            print(f"  {col:25s}  {vals.mean():.2f}  (σ={vals.std():.2f})")

    if "persona" in df.columns:
        print("\n── Personas ──")
        print(df["persona"].value_counts().to_string())

    if "appetence_niveau" in df.columns:
        print("\n── Appétence ──")
        print(df["appetence_niveau"].value_counts().to_string())

    if "Frequence" in df.columns:
        print("\n── Fréquence de jeu ──")
        print(df["Frequence"].value_counts().to_string())


if __name__ == "__main__":
    df = load()
    summary(df)
