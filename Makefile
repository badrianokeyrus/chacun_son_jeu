.PHONY: help install data api forms select run lint analysis \
        docker-build docker-up docker-down docker-logs

help:
	@echo "Chacun Son Jeu — commandes disponibles"
	@echo ""
	@echo "  Développement local"
	@echo "  make install      Installer les dépendances (uv sync)"
	@echo "  make data         Alimenter la base DuckDB depuis data/input/collection.json"
	@echo "  make api          Lancer l'API FastAPI (port 8000)"
	@echo "  make forms        Lancer l'app questionnaire (port 8501)"
	@echo "  make select       Lancer l'app collection (port 8502)"
	@echo "  make run          Lancer les deux apps Streamlit en parallèle"
	@echo "  make lint         Vérifier le code avec ruff"
	@echo "  make analysis     Analyser les réponses collectées"
	@echo ""
	@echo "  Docker"
	@echo "  make docker-build Construire les images Docker"
	@echo "  make docker-up    Démarrer tous les services (API + apps)"
	@echo "  make docker-down  Arrêter tous les services"
	@echo "  make docker-logs  Afficher les logs en temps réel"

install:
	uv sync

data:
	uv run python -m src.game_selection.collect

api:
	uv run uvicorn src.game_selection.api_data:app --reload --port 8000

forms:
	uv run streamlit run app/app_forms.py --server.port 8501

select:
	uv run streamlit run app/app_select.py --server.port 8502

run:
	@echo "Lancement des deux apps Streamlit..."
	@echo "  Questionnaire : http://localhost:8501"
	@echo "  Collection    : http://localhost:8502"
	@uv run streamlit run app/app_forms.py --server.port 8501 & \
	 uv run streamlit run app/app_select.py --server.port 8502 & \
	 wait

lint:
	uv run ruff check src/ app/

analysis:
	uv run python analysis/explore.py

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f
