# --- FICHIER COMPLET : src/modules/ears.py ---

import speech_recognition as sr
from faster_whisper import WhisperModel
import config
import os
import time

class Ears:
    """
    Gère la reconnaissance vocale (Speech-to-Text).
    Version avec réglage manuel de la sensibilité et gestion améliorée des ressources.
    """
    def __init__(self, model_size=config.WHISPER_MODEL_SIZE):
        print("Initialisation des oreilles (STT)...")
        self.temp_dir = config.BASE_DIR / "temp_data"
        os.makedirs(self.temp_dir, exist_ok=True)
        self.temp_audio_path = self.temp_dir / "temp_audio.wav"

        try:
            self.stt_model = WhisperModel(model_size, device="cuda", compute_type="float16")
            print(f"Modèle Whisper '{model_size}' chargé sur CUDA (float16).")
        except Exception as e:
            print(f"Erreur lors du chargement du modèle Whisper : {e}")
            raise

        self.recognizer = sr.Recognizer()

        try:
            mic_index = 1 # Ton micro (que tu as trouvé)
            self.microphone = sr.Microphone(device_index=mic_index)
            self.recognizer.energy_threshold = 600
            self.recognizer.pause_threshold = 1.5

            print(f"Oreilles prêtes. (Micro: {mic_index}, Seuil: {self.recognizer.energy_threshold}, Pause: {self.recognizer.pause_threshold}s)")

        except Exception as e:
            print(f"ERREUR CRITIQUE lors de l'initialisation du microphone : {e}")
            raise

    def listen(self):
        """
        Écoute l'utilisateur, enregistre, transcrit et retourne le texte.
        """
        with self.microphone as source:
            print("\nVous: (parlez...)")
            try:
                audio = self.recognizer.listen(source, timeout=30, phrase_time_limit=45)
            except sr.WaitTimeoutError:
                return ""
            except Exception as e:
                print(f"Erreur pendant l'écoute audio : {e}")
                return ""

        with open(self.temp_audio_path, "wb") as f:
            f.write(audio.get_wav_data())

        try:
            segments, _ = self.stt_model.transcribe(str(self.temp_audio_path), beam_size=5, language="fr")
            text = "".join(segment.text for segment in segments).strip()
            if text:
                print(f"(Transcription: {text})")
            return text
        except Exception as e:
            print(f"Erreur de transcription : {e}")
            return ""