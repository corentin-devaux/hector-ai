Hector AI Agent
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
🚀 Fonctionnalités
🗣️ Interaction Vocale Naturelle : Parlez à Hector et écoutez ses réponses grâce à une reconnaissance vocale (Whisper) et une synthèse vocale (gTTS) de haute qualité.
🧠 Raisonnement Avancé : Propulsé par un grand modèle de langage (Gemma) pour comprendre, planifier et exécuter des tâches complexes.
🌐 Navigation Web Autonome : Hector peut ouvrir un navigateur, analyser le contenu des pages, cliquer sur des éléments et remplir des formulaires pour atteindre ses objectifs.
🎬 Génération de Contenu Vidéo : Créez des vidéos uniques à partir d'une simple description textuelle grâce au modèle Wan-2.2.
💻 Architecture Client-Serveur Robuste : L'interface utilisateur (client) reste légère sur votre PC, tandis que les calculs IA intensifs sont déportés sur un serveur GPU puissant pour une performance maximale.
🏛️ Architecture du Projet
Le projet est conçu pour séparer l'interface de l'intelligence. Les deux composants communiquent via une API REST rapide construite avec FastAPI.
Composant	Description	Exécution
🤖 Serveur API	Le "cerveau" et les "muscles". Charge et exécute les modèles d'IA (LLM, Vidéo) sur le GPU.	Machine distante (ex: RunPod, AWS) avec GPU
🖥️ Client GUI	Le "visage" et les "sens". Gère l'interface graphique, le micro, les haut-parleurs et le navigateur web.	PC de l'utilisateur (Windows, macOS, Linux)
🛠️ Prérequis
Pour le Serveur (GPU)
Un serveur Linux (Ubuntu 22.04 recommandé) avec un GPU NVIDIA et les drivers CUDA.
Python 3.10+
Git et Git LFS
Pour le Client (Local)
Un ordinateur Windows, macOS ou Linux.
Python 3.10+
Git
Un microphone et des haut-parleurs fonctionnels.
⚙️ Guide d'Installation
1. Configuration du Serveur (Machine GPU distante)
Connectez-vous à votre serveur via SSH et suivez ces étapes.
a. Cloner le dépôt et naviguer dans le dossier :
code
Bash
git clone https://github.com/corentin-devaux/hector-ai-agent.git
cd hector-ai-agent
b. Installer les dépendances :
code
Bash
# Il est fortement recommandé d'utiliser un environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# Mettre à jour pip et installer les paquets
pip install --upgrade pip
pip install -r requirements.txt
⚠️ Note Cruciale sur la Performance GPU : Pour que le LLM utilise le GPU, llama-cpp-python doit être compilé avec le support CUDA. Si vous constatez que seul le CPU est utilisé, forcez la réinstallation :
code
Bash
pip uninstall -y llama-cpp-python
CMAKE_ARGS="-DLLAMA_CUBLAS=on" FORCE_CMAKE=1 pip install --no-cache-dir llama-cpp-python
c. Télécharger les modèles d'IA :
code
Bash
# Créez le dossier des modèles
mkdir -p models
cd models

# 1. Téléchargez le modèle LLM (Gemma)
# Assurez-vous que le nom du fichier de sortie (-O) correspond à `MODEL_FILE` dans src/config.py
wget "URL_DU_MODELE_GEMMA_GGUF" -O gemma-model.gguf

# 2. Téléchargez le modèle de génération vidéo (Wan-2.2)
# Wan-2.2 est souvent distribué sous forme de dépôt complet
git clone URL_DU_MODELE_WAN2.2 wan-2.2-model

# ... Ajoutez ici les commandes pour les autres modèles si nécessaire ...
Vérifiez que les chemins dans src/config.py pointent vers les bons noms de fichiers/dossiers.
2. Configuration du Client (Votre PC local)
a. Cloner le dépôt :
code
Bash
git clone https://github.com/corentin-devaux/hector-ai-agent.git
cd hector-ai-agent
b. Créer un environnement virtuel et installer les dépendances :
code
Bash
# Créez l'environnement virtuel
python -m venv .venv

# Activez-le (adaptez la commande à votre OS)
# Windows: .\.venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

# Installez les paquets
pip install -r requirements.txt
c. Configurer l'adresse du serveur :
Ouvrez le fichier src/gui/main_window.py et modifiez la variable SERVER_URL avec l'adresse IP et le port public de votre serveur :
code
Python
# Exemple
self.SERVER_URL = "http://123.45.67.89:12345"
▶️ Lancement
L'application se lance en deux temps : d'abord le serveur, puis le client.
Étape 1 : Démarrer le Serveur
Sur votre machine GPU distante, depuis la racine du projet :
code
Bash
# Activez l'environnement virtuel si ce n'est pas déjà fait
source .venv/bin/activate

# Lancez l'API
python src/server_api.py
Le serveur chargera les modèles et se mettra en écoute.
Étape 2 : Lancer le Client
Sur votre PC local, depuis la racine du projet :
code
Bash
# Activez votre environnement virtuel local
# .\.venv\Scripts\activate

# Lancez l'interface graphique
python src/gui/main_window.py
L'interface d'Hector apparaît. Vous êtes prêt à interagir !
🧠 Modèles d'IA Utilisés
Composant	Modèle	Rôle
Cerveau (LLM)	Gemma 9B GGUF	Raisonnement, planification, génération
Oreilles (STT)	OpenAI Whisper (large-v3)	Transcription de la parole en texte
Vidéo (Gen)	Wan-2.2 (Modèle de diffusion texte-vers-vidéo)	Création de vidéos à partir de prompts
Voix (TTS)	Google Text-to-Speech (gTTS)	Synthèse vocale
Tous les modèles sont configurables dans src/config.py.
🤝 Contribuer
Les contributions sont les bienvenues ! Pour toute suggestion ou amélioration, veuillez ouvrir une issue ou soumettre une pull request.
📄 Licence
Ce projet est distribué sous la Licence MIT. Voir le fichier LICENSE pour plus de détails.
