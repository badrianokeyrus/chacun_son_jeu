# Configuration Google Sheets

## Vue d'ensemble

L'app détecte automatiquement l'environnement :
- **Streamlit Cloud** (secrets présents) → écrit dans Google Sheets
- **Local** (pas de secrets) → écrit dans `data/responses.csv`

Aucun changement de code n'est nécessaire entre les deux modes.

---

## Étape 1 — Créer un projet Google Cloud

1. Aller sur [console.cloud.google.com](https://console.cloud.google.com)
2. Créer un nouveau projet (ex: `questionnaire-joueurs`)
3. Activer les deux APIs suivantes :
   - **Google Sheets API**
   - **Google Drive API**

   *(Rechercher chacune dans "APIs & Services → Bibliothèque")*

---

## Étape 2 — Créer un compte de service

1. "APIs & Services → Identifiants → Créer des identifiants → Compte de service"
2. Donner un nom (ex: `questionnaire-bot`)
3. Rôle : **Éditeur** (ou "Viewer" si lecture seule)
4. Une fois créé, cliquer sur le compte → onglet **Clés**
5. "Ajouter une clé → Créer une clé JSON" → télécharger le fichier `.json`

---

## Étape 3 — Créer le Google Sheet

1. Aller sur [sheets.google.com](https://sheets.google.com) et créer une feuille vide
2. Nommer l'onglet **`responses`** (ou laisser "Feuille 1", l'app le crée automatiquement)
3. Récupérer l'**ID du Sheet** dans l'URL :
   ```
   https://docs.google.com/spreadsheets/d/  ← ID ici →  /edit
   ```
4. **Partager la feuille** avec l'adresse `client_email` du compte de service
   (droits : **Éditeur**)

---

## Étape 4 — Configurer les secrets

### En local

Copier le template et remplir avec les valeurs du fichier JSON téléchargé :

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Éditer .streamlit/secrets.toml
```

### Sur Streamlit Cloud

1. Ouvrir votre app → **⋮ → Settings → Secrets**
2. Coller le contenu de `secrets.toml` (sans les commentaires) :

```toml
SPREADSHEET_ID = "1AbCdEfGhIj..."

[gcp_service_account]
type = "service_account"
project_id = "questionnaire-joueurs"
private_key_id = "abc123"
private_key = "-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----\n"
client_email = "questionnaire-bot@questionnaire-joueurs.iam.gserviceaccount.com"
client_id = "123456789"
token_uri = "https://oauth2.googleapis.com/token"
```

> ⚠️ Les `\n` dans `private_key` doivent rester sur **une seule ligne** dans l'interface Streamlit Cloud.

---

## Vérification

Au premier lancement avec les secrets configurés, l'app :
1. Se connecte au Sheet via le compte de service
2. Crée l'onglet `responses` s'il n'existe pas
3. Écrit les en-têtes à la première soumission
4. Ajoute une ligne par répondant

En cas d'erreur Google Sheets, l'app se rabat automatiquement sur le CSV local et logue l'erreur.
