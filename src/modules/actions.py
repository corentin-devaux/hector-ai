# --- FICHIER COMPLET MODIFIÉ : src/modules/actions.py ---

import time
import datetime
import requests
import json
from bs4 import BeautifulSoup

import config
from .video_generator import VideoGenerator # <--- NOUVEL IMPORT

class Actions:
    """
    Contient les actions (fonctions) qu'Hector peut exécuter.
    """
    def __init__(self):
        # Essaye d'initialiser le générateur vidéo, mais ne bloque pas si ça échoue.
        try:
            self.video_generator = VideoGenerator()
        except Exception as e:
            print(f"AVERTISSEMENT : Le module de génération vidéo n'a pas pu être initialisé : {e}")
            self.video_generator = None

    def get_current_time(self):
        """Retourne l'heure et la date actuelles."""
        now = datetime.datetime.now()
        return f"Il est {now.strftime('%H:%M:%S')} et nous sommes le {now.strftime('%d/%m/%Y')}."

    def search_web(self, query: str):
        """
        Effectue une recherche Google et retourne UNIQUEMENT l'URL du premier résultat.
        Le scraping est maintenant géré par le navigateur de l'interface graphique.
        """
        if not config.GOOGLE_API_KEY or "VOTRE_CLE_API" in config.GOOGLE_API_KEY:
            return "Erreur: La clé API Google n'est pas configurée."
        if not config.GOOGLE_CSE_ID or "VOTRE_ID_MOTEUR" in config.GOOGLE_CSE_ID:
            return "Erreur: L'ID du moteur de recherche Google n'est pas configuré."

        search_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'q': query,
            'key': config.GOOGLE_API_KEY,
            'cx': config.GOOGLE_CSE_ID,
            'num': 1 # On n'a besoin que du premier résultat
        }
        try:
            response = requests.get(search_url, params=params, timeout=5)
            response.raise_for_status()
            results = response.json()
            
            if "items" not in results or len(results["items"]) == 0:
                return "Je n'ai trouvé aucun résultat pour cette recherche."

            page_url = results["items"][0]['link']
            return f"URL: {page_url}"

        except requests.exceptions.RequestException as e:
            return f"Erreur de connexion lors de la recherche Google : {e}"
        except Exception as e:
            return f"Une erreur inattendue est survenue lors de la recherche : {e}"

    def create_video(self, prompt: str):
        """
        Crée une courte vidéo basée sur une description textuelle.
        Utilise le modèle Wan2.2.
        Retourne le chemin vers le fichier vidéo généré.
        """
        if self.video_generator is None:
            return "Désolé, le module de création vidéo n'est pas disponible en raison d'une erreur d'initialisation."
        
        return self.video_generator.generate_video(prompt)

    def click(self, element_id: str):
        """
        Simule un clic sur un élément identifié sur la page web.
        """
        return f"Tentative de clic sur l'élément avec l'ID/texte : {element_id}"

    def type_text(self, element_id: str, text: str):
        """
        Simule la saisie de texte dans un champ identifié sur la page web.
        """
        return f"Tentative de saisir '{text}' dans l'élément avec l'ID/texte : {element_id}"

    def navigate(self, url: str):
        """
        Navigue le navigateur vers une nouvelle URL.
        """
        return f"Tentative de naviguer vers : {url}"