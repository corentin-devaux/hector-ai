# Hector AI Agent

<div align="center">
  <img src="https://img.shields.io/badge/Hector%20AI-v1.0-blue?style=for-the-badge&logo=appveyor" alt="Version"/>
  <img src="https://img.shields.io/badge/Python-3.10+-yellow.svg?style=for-the-badge&logo=python" alt="Python"/>
  <img src="https://img.shields.io/badge/PyTorch-GPU%20Ready-orange?style=for-the-badge&logo=pytorch" alt="PyTorch"/>
</div>

<div align="center">
  <img src="https://img.shields.io/badge/FastAPI-Backend-green?style=for-the-badge&logo=fastapi" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/PyQt6-Frontend-purple?style=for-the-badge&logo=qt" alt="PyQt6"/>
</div>

<p align="center">
  <em>Un assistant IA multimodal capable d'interagir par la voix, de naviguer sur le web et de générer du contenu, le tout propulsé par une architecture client-serveur performante.</em>
</p>

---

## 🚀 Fonctionnalités

- 🗣️ **Interaction Vocale Naturelle** : Whisper (STT) + gTTS (TTS)  
- 🧠 **Raisonnement Avancé** : LLM Gemma pour compréhension et planification  
- 🌐 **Navigation Web Autonome** : Analyse, clics, formulaires  
- 🎬 **Génération Vidéo** : Modèle Wan-2.2 (texte → vidéo)  
- 💻 **Architecture Client-Serveur** : Calculs IA sur GPU distant, GUI légère en local  

---

## 🏛️ Architecture

| Composant   | Description | Exécution |
|-------------|-------------|-----------|
| 🤖 **Serveur API** | Le cerveau et les muscles (LLM, vidéo). | Machine distante avec GPU (RunPod, AWS, etc.) |
| 🖥️ **Client GUI** | Le visage et les sens (micro, audio, navigateur). | PC local (Windows/macOS/Linux) |

Communication via **FastAPI REST API**.

---

## 🛠️ Prérequis

### Serveur (GPU)
- Linux (Ubuntu 22.04 recommandé)  
- NVIDIA GPU + CUDA  
- Python 3.10+  
- Git + Git LFS  

### Client (Local)
- Windows, macOS ou Linux  
- Python 3.10+  
- Git  
- Micro + Haut-parleurs  

---

## ⚙️ Installation

### 1. Configuration du Serveur (GPU distant)

#### a. Cloner le dépôt
```bash
git clone https://github.com/corentin-devaux/hector-ai-agent.git
cd hector-ai-agent
b. Installer les dépendances
bash
Copier le code
# Créer et activer un venv
python3 -m venv .venv
source .venv/bin/activate

# Installer les paquets
pip install --upgrade pip
pip install -r requirements.txt
⚠️ GPU : Compilation de llama-cpp-python avec CUDA
bash
Copier le code
pip uninstall -y llama-cpp-python
CMAKE_ARGS="-DLLAMA_CUBLAS=on" FORCE_CMAKE=1 pip install --no-cache-dir llama-cpp-python
c. Télécharger les modèles
bash
Copier le code
# Créer dossier des modèles
mkdir -p models && cd models

# 1. LLM Gemma
wget "URL_DU_MODELE_GEMMA_GGUF" -O gemma-model.gguf

# 2. Vidéo Wan-2.2
git clone URL_DU_MODELE_WAN2.2 wan-2.2-model
📌 Vérifiez que les chemins dans src/config.py correspondent.

2. Configuration du Client (PC local)
a. Cloner le dépôt
bash
Copier le code
git clone https://github.com/corentin-devaux/hector-ai-agent.git
cd hector-ai-agent
b. Installer les dépendances
bash
Copier le code
# Créer et activer un venv
python -m venv .venv

# Activer (selon OS)
# Windows
.\.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Installer paquets
pip install -r requirements.txt
c. Configurer l’adresse du serveur
Modifier dans src/gui/main_window.py :

python
Copier le code
self.SERVER_URL = "http://123.45.67.89:12345"
▶️ Lancement
Étape 1 : Démarrer le Serveur (sur GPU distant)
bash
Copier le code
source .venv/bin/activate
python src/server_api.py
Étape 2 : Lancer le Client (sur PC local)
bash
Copier le code
# Activer venv
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate # macOS/Linux

# Lancer GUI
python src/gui/main_window.py
🧠 Modèles d’IA
Composant	Modèle	Rôle
Cerveau (LLM)	Gemma 9B GGUF	Raisonnement, génération
Oreilles (STT)	Whisper large-v3	Transcription vocale
Vidéo (Gen)	Wan-2.2	Texte → Vidéo
Voix (TTS)	gTTS	Synthèse vocale

Tous les chemins configurables dans src/config.py.

🤝 Contribution
Les contributions sont bienvenues !
👉 Ouvrez une issue ou une pull request.

📄 Licence
Distribué sous MIT License. Voir LICENSE.

yaml
Copier le code

---

Veux-tu que je t’ajoute aussi un **sommaire cliquable (table of contents)** en haut du README pour naviguer rapidement entre les sections ?
