import streamlit as st
import json

# --- Configuration de la page ---
st.set_page_config(
    page_title="Questionnaire",
    page_icon="📋",
    layout="centered"
)

# --- CSS personnalisé ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500&display=swap');

        html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif;
            background: #ffffff;
            color: #000000;
        }

        h1, h2, h3 {
            font-family: 'Syne', sans-serif !important;
            color: #000000;
        }

        .stApp {
            background: #ffffff;
            color: #000000;
        }

        .quiz-header {
            text-align: center;
            padding: 2rem 0 1rem;
        }

        .quiz-header h1 {
            font-size: 3rem;
            font-weight: 800;
            color: #000000;
            letter-spacing: -1px;
        }

        .quiz-header p {
            color: #555;
            font-size: 1rem;
        }

        .question-card {
            background: #f9f9f9;
            border: 1px solid #e5e5e5;
            border-radius: 16px;
            padding: 1.8rem 2rem;
            margin-bottom: 1.5rem;
        }

        .question-label {
            font-family: 'Syne', sans-serif;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 3px;
            text-transform: uppercase;
            color: #d4a017;
            margin-bottom: 0.5rem;
        }

        .question-text {
            font-size: 1.1rem;
            font-weight: 500;
            color: #000000;
            margin-bottom: 1rem;
        }

        div.stButton > button {
            width: 100%;
            background: #d4a017;
            color: #ffffff;
            font-family: 'Syne', sans-serif;
            font-weight: 700;
            font-size: 1rem;
            letter-spacing: 1px;
            border: none;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            margin-top: 0.5rem;
            cursor: pointer;
            transition: all 0.2s;
        }

        div.stButton > button:hover {
            background: #e6b800;
            transform: translateY(-1px);
        }

        .result-box {
            background: #f9f9f9;
            border: 2px solid #d4a017;
            border-radius: 16px;
            padding: 2rem;
            text-align: center;
            margin-bottom: 1.5rem;
        }

        .result-title {
            font-family: 'Syne', sans-serif;
            font-size: 1.8rem;
            font-weight: 800;
            color: #d4a017;
        }

        .result-subtitle {
            color: #555;
            font-size: 0.9rem;
            margin-top: 0.4rem;
        }

        .answer-card {
            background: #f9f9f9;
            border: 1px solid #e5e5e5;
            border-radius: 12px;
            padding: 1.2rem 1.5rem;
            margin-bottom: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .answer-question {
            color: #666;
            font-size: 0.85rem;
            margin-bottom: 0.2rem;
        }

        .answer-value {
            font-size: 1rem;
            font-weight: 600;
            color: #000000;
        }

        .badge {
            background: #d4a017;
            color: #ffffff;
            font-family: 'Syne', sans-serif;
            font-weight: 700;
            font-size: 0.85rem;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            white-space: nowrap;
        }

        div[data-testid="stRadio"] > label {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)


# --- Données du questionnaire ---
questions = [
    {
        "question": "Comment évaluez-vous votre niveau en Python ?",
        "choices": ["A. Débutant", "B. Intermédiaire", "C. Avancé"],
    },
    {
        "question": "Quelle est votre méthode de travail préférée ?",
        "choices": ["A. En solo", "B. En binôme", "C. En équipe"],
    },
    {
        "question": "Quel environnement de développement utilisez-vous ?",
        "choices": ["A. VS Code", "B. PyCharm", "C. Jupyter Notebook"],
    },
    {
        "question": "À quelle fréquence utilisez-vous des outils d'IA dans votre travail ?",
        "choices": ["A. Rarement", "B. Quelques fois par semaine", "C. Tous les jours"],
    },
    {
        "question": "Quelle est votre priorité principale dans un projet ?",
        "choices": ["A. La rapidité de livraison", "B. La qualité du code", "C. L'expérience utilisateur"],
    },
]

# --- En-tête ---
st.markdown("""
    <div class="quiz-header">
        <h1>📋 Questionnaire</h1>
        <p>Répondez aux 5 questions — une seule réponse par question.</p>
    </div>
""", unsafe_allow_html=True)

# --- Initialisation de l'état ---
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "answers" not in st.session_state:
    st.session_state.answers = [None] * len(questions)

# --- Formulaire ---
if not st.session_state.submitted:
    for i, q in enumerate(questions):
        st.markdown(f"""
            <div class="question-card">
                <div class="question-label">Question {i + 1} / {len(questions)}</div>
                <div class="question-text">{q['question']}</div>
            </div>
        """, unsafe_allow_html=True)

        choice = st.radio(
            label=f"q{i}",
            options=q["choices"],
            index=None,
            key=f"q{i}",
            label_visibility="collapsed"
        )
        st.session_state.answers[i] = choice

    all_answered = all(a is not None for a in st.session_state.answers)

    if not all_answered:
        st.info("⬆️ Répondez à toutes les questions pour soumettre.")

    if st.button("✅ Soumettre mes réponses", disabled=not all_answered):
        st.session_state.submitted = True
        st.rerun()

# --- Récapitulatif des réponses ---
else:
    st.markdown("""
        <div class="result-box">
            <div class="result-title">✅ Réponses enregistrées</div>
            <div class="result-subtitle">Voici le récapitulatif de vos réponses.</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📄 Récapitulatif")

    for i, q in enumerate(questions):
        reponse = st.session_state.answers[i]
        # Extraire juste la lettre (A, B ou C)
        lettre = reponse.split(".")[0].strip() if reponse else "—"

        st.markdown(f"""
            <div class="answer-card">
                <div>
                    <div class="answer-question">Q{i+1} — {q['question']}</div>
                    <div class="answer-value">{reponse}</div>
                </div>
                <span class="badge">{lettre}</span>
            </div>
        """, unsafe_allow_html=True)

    # --- Export JSON ---
    export_data = {
        f"Q{i+1}": {
            "question": q["question"],
            "reponse": st.session_state.answers[i]
        }
        for i, q in enumerate(questions)
    }
    json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
    file_path = "data/preprocessing/reponses_questionnaire.json"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(json_str)

    st.markdown("### 💾 Exporter les réponses")
    st.download_button(
        label="⬇️ Télécharger en JSON",
        data=json_str,
        file_name="reponses_questionnaire.json",
        mime="data/preprocessing"
    )

    # Affichage brut pour intégration / debug
    with st.expander("🔍 Voir les données brutes (JSON)"):
        st.code(json_str, language="json")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔄 Recommencer"):
        st.session_state.submitted = False
        st.session_state.answers = [None] * len(questions)
        for i in range(len(questions)):
            if f"q{i}" in st.session_state:
                del st.session_state[f"q{i}"]
        st.rerun()
