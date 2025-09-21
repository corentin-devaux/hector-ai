# --- NOUVEAU FICHIER : src/server_api.py ---

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import logging

# Importez vos modules IA
from modules.brain import Brain
from modules.actions import Actions
# NOTE : On n'importe PAS Ears et Voice, car ils tourneront sur le client !

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Initialisation de l'API et des Modèles ---
logger.info("Démarrage de l'application serveur Hector...")

# Crée l'application FastAPI
app = FastAPI()

# Modèles de données pour les requêtes (sécurise les entrées/sorties)
class ThinkRequest(BaseModel):
    history: list

class ActionRequest(BaseModel):
    tool_name: str
    tool_params: dict

# Chargement des modèles IA UNE SEULE FOIS au démarrage du serveur
# C'est la partie la plus importante pour la performance
try:
    logger.info("Chargement des modules IA...")
    brain = Brain()
    actions = Actions()
    logger.info("Modules IA chargés avec succès !")
except Exception as e:
    logger.critical(f"ERREUR CRITIQUE au chargement des modules IA : {e}")
    brain = None
    actions = None

# --- Définition des Endpoints de l'API ---

@app.get("/")
def read_root():
    """ Endpoint de base pour vérifier que le serveur est en ligne. """
    return {"status": "Hector Server API is running"}

@app.post("/think")
def think_endpoint(request: ThinkRequest):
    """
    Endpoint principal pour faire réfléchir le cerveau.
    Reçoit l'historique de la conversation et retourne la pensée de l'agent.
    """
    if not brain:
        return {"error": "Le module Brain n'a pas pu être initialisé."}
    
    try:
        logger.info(f"Requête /think reçue avec {len(request.history)} messages.")
        response = brain.think(request.history)
        logger.info(f"Réponse générée : {response[:100]}...")
        return {"response": response}
    except Exception as e:
        logger.error(f"Erreur dans l'endpoint /think : {e}")
        return {"error": str(e)}

@app.post("/execute_action")
def execute_action_endpoint(request: ActionRequest):
    """
    Endpoint pour exécuter une action qui doit se faire côté serveur (ex: créer une vidéo).
    """
    if not actions:
        return {"error": "Le module Actions n'a pas pu être initialisé."}
        
    try:
        tool_function = getattr(actions, request.tool_name, None)
        if tool_function and callable(tool_function):
            logger.info(f"Exécution de l'action : {request.tool_name} avec les paramètres {request.tool_params}")
            result = tool_function(**request.tool_params)
            return {"result": result}
        else:
            logger.warning(f"Tentative d'appel d'une action inconnue : {request.tool_name}")
            return {"error": f"Action '{request.tool_name}' non trouvée."}
    except Exception as e:
        logger.error(f"Erreur dans l'endpoint /execute_action : {e}")
        return {"error": str(e)}

# --- Point d'entrée pour lancer le serveur ---
if __name__ == "__main__":
    # Uvicorn est un serveur ASGI qui fait tourner notre application FastAPI
    # host="0.0.0.0" est crucial pour que le serveur soit accessible depuis l'extérieur du Pod
    uvicorn.run(app, host="0.0.0.0", port=8000)