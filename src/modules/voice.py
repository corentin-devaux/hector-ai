# --- FICHIER COMPLET : src/modules/voice.py ---

import os
import threading
import time
import subprocess
from gtts import gTTS
import config

class Voice:
    """
    Gère la synthèse vocale (Text-to-Speech) en utilisant gTTS (nécessite une connexion Internet)
    et ffplay pour la lecture.
    """
    def __init__(self):
        self.lock = threading.Lock()
        self.temp_audio_file = os.path.join(os.path.dirname(__file__), "temp_hector_speech.mp3")
        self.ffplay_path = str(config.BASE_DIR / "drivers" / "ffplay.exe")
        
        if not os.path.exists(self.ffplay_path):
            print(f"ERREUR: ffplay.exe non trouvé à : {self.ffplay_path}")
            print("Veuillez télécharger ffplay.exe (partie de FFmpeg) et le placer dans le dossier 'drivers/'.")
            self.ffplay_path = None
        else:
            print("Moteur vocal gTTS (via ffplay) prêt (nécessite Internet).")

    def speak(self, text, lang='fr'):
        """
        Prononce le texte fourni en français en générant un MP3, puis le lit avec ffplay.
        """
        if self.ffplay_path is None:
            print("Erreur: ffplay.exe n'est pas disponible pour la lecture audio.")
            return

        with self.lock:
            try:
                tts = gTTS(text=text, lang=lang, slow=False) 
                tts.save(self.temp_audio_file)
                
                command = [self.ffplay_path, "-nodisp", "-autoexit", "-loglevel", "quiet", self.temp_audio_file]
                subprocess.run(command, check=True)

            except subprocess.CalledProcessError as e:
                print(f"ERREUR ffplay : La commande ffplay a échoué. Code de sortie: {e.returncode}, Erreur: {e.stderr}")
            except Exception as e:
                print(f"Erreur lors de la synthèse ou de la lecture vocale avec gTTS/ffplay : {e}")
                print("Vérifiez votre connexion Internet.")
            finally:
                if os.path.exists(self.temp_audio_file):
                    try:
                        os.remove(self.temp_audio_file)
                    except OSError as e:
                        print(f"AVERTISSEMENT: Impossible de supprimer le fichier audio temporaire: {e}")
                time.sleep(0.1)