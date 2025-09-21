# --- FICHIER CORRIGÉ COMPLET : src/modules/video_generator.py ---

import torch
from diffusers import I2VGenXLPipeline
from diffusers.utils import export_to_video
import os
import datetime
import config

class VideoGenerator:
    """
    Gère le modèle de génération de vidéo (Wan2.2).
    """
    def __init__(self):
        print("Initialisation du générateur de vidéo (Wan2.2) depuis le chemin local...")
        self.output_dir = config.BASE_DIR / "outputs" / "videos"
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.pipe = None
        
        if not config.VIDEO_MODEL_DIR.exists():
            print(f"ERREUR : Le dossier du modèle vidéo n'existe pas : {config.VIDEO_MODEL_DIR}")
            print("Veuillez télécharger le modèle Wan2.2 manuellement comme indiqué dans les instructions.")
            raise FileNotFoundError(f"Modèle vidéo non trouvé à : {config.VIDEO_MODEL_DIR}")

        if not torch.cuda.is_available():
            print("AVERTISSEMENT CRITIQUE : PyTorch n'a pas accès au GPU (CUDA). La génération vidéo est impossible.")
            raise RuntimeError("CUDA non disponible pour le générateur vidéo.")

        try:
            # Charger le modèle depuis le chemin local spécifié dans config.py
            self.pipe = I2VGenXLPipeline.from_pretrained(
                str(config.VIDEO_MODEL_DIR), # Utilise le chemin local
                torch_dtype=torch.float16, 
                variant="fp16"
            )
            self.pipe.to("cuda")
            print(f"Générateur de vidéo 'Wan2.2' chargé depuis {config.VIDEO_MODEL_DIR} sur le GPU.")
        except Exception as e:
            print(f"Échec CRITIQUE du chargement du modèle vidéo : {e}")
            print("Assurez-vous d'avoir assez de VRAM et que les bibliothèques sont correctement installées.")
            raise

    def generate_video(self, prompt: str):
        """
        Génère une vidéo à partir d'un prompt textuel et la sauvegarde.
        Retourne le chemin du fichier vidéo.
        """
        if self.pipe is None:
            return "Erreur : Le modèle de génération vidéo n'est pas chargé."

        print(f"Génération d'une vidéo pour le prompt : '{prompt}'...")
        try:
            # Paramètres de génération
            num_frames = 32
            
            # Lancement de la génération
            frames = self.pipe(
                prompt=prompt, 
                num_inference_steps=75, 
                num_frames=num_frames
            ).frames[0]
            
            # Création d'un nom de fichier unique
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"video_{timestamp}.mp4"
            output_path = self.output_dir / filename
            
            # Exportation des frames en fichier vidéo
            export_to_video(frames, str(output_path), fps=8)
            
            print(f"Vidéo générée et sauvegardée ici : {output_path}")
            return f"Vidéo créée avec succès. Elle est disponible ici : {output_path}"
        
        except Exception as e:
            print(f"ERREUR lors de la génération de la vidéo : {e}")
            return f"Désolé, une erreur est survenue lors de la création de la vidéo : {e}"