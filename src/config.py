# --- FICHIER COMPLET : src/config.py ---

import pathlib
import os # Ajout de l'import os

# Pour désactiver le sandbox de QtWebEngine si vous rencontrez des problèmes.
# ATTENTION: Cela peut avoir des implications de sécurité. À utiliser avec prudence.
# os.environ['QTWEBENGINE_DISABLE_SANDBOX'] = '1'

# --- CHEMINS ---
# Le dossier racine du projet
BASE_DIR = pathlib.Path(__file__).parent.parent

# Chemin vers le dossier des modèles
MODELS_DIR = BASE_DIR / "models"

# --- CERVEAU (LLM) ---
MODEL_FILE = "gemma-3-4b-it-Q4_K_M.gguf"
MODEL_PATH = MODELS_DIR / MODEL_FILE

# Paramètres du modèle
N_CTX = 131072 
N_GPU_LAYERS = -1 #-1 pour un H100

# --- OREILLES (SPEECH-TO-TEXT) ---
WHISPER_MODEL_SIZE = "large-v3"  # Options : tiny, base, small, medium, large, large-v2, large-v3

# --- GENERATION VIDEO (NOUVEAU) ---
VIDEO_MODEL_DIR = MODELS_DIR / "diffusion_pytorch_model-00006-of-00006.safetensors"

# --- ACTIVATION ---
ACTIVATION_KEYWORD = "hector"

# --- WEB SEARCH (NOUVEAU) ---
# Mettez vos propres clés ici !
GOOGLE_API_KEY = "AIzaSyD-17wYs4uiSDsMVICA2QFuuTS_OvcVm40" # Assurez-vous que c'est une clé valide
GOOGLE_CSE_ID = "d7106557d78434ea1" # Assurez-vous que c'est un ID valide