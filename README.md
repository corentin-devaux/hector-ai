Hector AI Agent
![alt text](https://img.shields.io/badge/Hector%20AI-v1.0-blue?style=for-the-badge&logo=appveyor)

![alt text](https://img.shields.io/badge/Python-3.11+-yellow.svg?style=for-the-badge&logo=python)

![alt text](https://img.shields.io/badge/PyTorch-GPU-orange?style=for-the-badge&logo=pytorch)

![alt text](https://img.shields.io/badge/FastAPI-Backend-green?style=for-the-badge&logo=fastapi)

![alt text](https://img.shields.io/badge/PyQt6-Frontend-purple?style=for-the-badge&logo=qt)
Hector AI Agent est un assistant IA multimodal capable d'interagir par la voix, de comprendre et d'exécuter des tâches complexes, y compris la navigation web et la génération de contenu. Ce projet est conçu sur une architecture client-serveur pour déporter les tâches de calcul intensif sur un GPU distant, tout en offrant une interface utilisateur fluide et réactive en local.
Table des Matières
Fonctionnalités
Architecture du Projet
Prérequis
Installation
1. Configuration du Serveur (GPU distant)
2. Configuration du Client (PC local)
Lancement
Étape 1 : Démarrer le Serveur
Étape 2 : Lancer le Client
Modèles d'IA utilisés
Contribuer
Licence
Fonctionnalités
Interaction Vocale : Parlez à Hector grâce à la reconnaissance vocale (Whisper) et écoutez ses réponses (gTTS).
Cerveau Intelligent : Propulsé par un grand modèle de langage (Gemma) pour comprendre, raisonner et planifier des actions.
Navigation Web Autonome : Hector peut ouvrir un navigateur, analyser le contenu des pages et interagir avec les éléments (cliquer, taper du texte) pour accomplir des tâches.
Génération de Contenu : Capacité à générer des vidéos à partir de prompts textuels (en utilisant un modèle de diffusion).
Architecture Client-Serveur : L'interface utilisateur (client) est légère et fonctionne sur n'importe quel PC, tandis que le traitement lourd de l'IA (serveur) est effectué sur une machine GPU dédiée pour des performances maximales.
Architecture du Projet
Le projet est divisé en deux composants principaux qui communiquent via une API REST :
Le Serveur (src/server_api.py)
Rôle : Le "cerveau" et les "muscles".
Tâches : Charge et exécute les modèles d'IA lourds (LLM, génération vidéo). Expose des endpoints FastAPI pour recevoir des ordres et renvoyer des résultats.
Destination : Doit être déployé sur une machine avec un GPU NVIDIA puissant (ex: RunPod, AWS, etc.).
Le Client (src/gui/main_window.py)
Rôle : Le "visage" et les "sens".
Tâches : Gère l'interface graphique (PyQt6), capture l'audio du microphone, joue les réponses audio, et envoie les requêtes de l'utilisateur au serveur API.
Destination : S'exécute sur l'ordinateur de l'utilisateur (Windows, macOS, Linux).
Prérequis
Pour le Serveur :
Un serveur Linux (Ubuntu 22.04 recommandé) avec un GPU NVIDIA et les drivers CUDA installés.
Python 3.10+
Git et Git LFS
Pour le Client :
Un ordinateur Windows, macOS ou Linux.
Python 3.10+
Git
Un microphone et des haut-parleurs fonctionnels.
Installation
1. Configuration du Serveur (GPU distant)
Connectez-vous à votre serveur via SSH et suivez ces étapes.
a. Cloner le dépôt :
code
Bash
git clone https://github.com/corentin-devaux/hector-ai-agent.git
cd hector-ai-agent
b. Installer les dépendances Python :
code
Bash
# Il est fortement recommandé d'utiliser un environnement virtuel
python -m venv .venv
source .venv/bin/activate

# Installez les dépendances
pip install -r requirements.txt
Note importante : Pour des performances optimales avec un GPU NVIDIA, il est crucial que llama-cpp-python soit compilé avec le support CUDA. Si vous rencontrez des problèmes de performance, désinstallez-le et réinstallez-le en forçant la compilation GPU :
code
Bash
pip uninstall -y llama-cpp-python
CMAKE_ARGS="-DLLAMA_CUBLAS=on" FORCE_CMAKE=1 pip install --no-cache-dir llama-cpp-python
c. Télécharger les modèles d'IA :
code
Bash
# Créez le dossier des modèles s'il n'existe pas
mkdir -p models
cd models

# Téléchargez le modèle LLM (Gemma)
wget "URL_DU_MODELE_GEMMA" -O gemma-model.gguf # Remplacez l'URL et le nom

# Téléchargez le modèle de génération vidéo (ex: I2VGen-XL)
git clone https://huggingface.co/ali-vilab/i2vgen-xl i2vgen-xl

# ... Ajoutez ici les commandes pour les autres modèles ...
Assurez-vous que les noms des fichiers et dossiers de modèles correspondent à ceux définis dans src/config.py.
2. Configuration du Client (PC local)
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

# Activez-le
# Sur Windows:
# .\.venv\Scripts\activate
# Sur macOS/Linux:
# source .venv/bin/activate

# Installez les dépendances
pip install -r requirements.txt
c. Configurer la connexion au serveur :
Ouvrez le fichier src/gui/main_window.py dans votre éditeur de code.
Trouvez la ligne suivante dans la méthode init_hector_modules et remplacez l'URL par l'adresse IP publique et le port de votre serveur :
code
Python
self.SERVER_URL = "http://VOTRE_IP_PUBLIQUE_RUNPOD:PORT"
Lancement
L'application doit être lancée en deux étapes : d'abord le serveur, puis le client.
Étape 1 : Démarrer le Serveur
Sur votre serveur distant, depuis la racine du projet (hector-ai-agent), lancez l'API :
code
Bash
# Assurez-vous que votre environnement virtuel est activé
source .venv/bin/activate

# Lancez le serveur FastAPI avec Uvicorn
python src/server_api.py
Le serveur va démarrer, charger les modèles en mémoire et attendre les requêtes sur le port 8000 (par défaut).
Étape 2 : Lancer le Client
Sur votre ordinateur local, depuis la racine du projet (hector-ai-agent), lancez l'interface graphique :
code
Bash
# Assurez-vous que votre environnement virtuel est activé
# .\.venv\Scripts\activate  (Windows)

# Lancez l'application cliente
python src/gui/main_window.py
L'interface d'Hector devrait apparaître. Vous pouvez maintenant commencer à interagir avec lui !
Modèles d'IA utilisés
Large Language Model (LLM) : Gemma 9B GGUF (configurable dans src/config.py).
Speech-to-Text (STT) : Whisper (large-v3) via la bibliothèque faster-whisper.
Video Generation : I2VGen-XL (configurable dans src/config.py).
Text-to-Speech (TTS) : Google Text-to-Speech (gTTS).
Contribuer
Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue pour signaler un bug ou proposer une nouvelle fonctionnalité, ou à soumettre une pull request avec vos améliorations.
Licence
Ce projet est distribué sous la licence MIT. Voir le fichier LICENSE pour plus de détails.
