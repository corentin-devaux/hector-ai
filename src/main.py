import sys
import time
import config
from modules.brain import Brain
from modules.ears import Ears
from modules.voice import Voice
# L'import de sys est déjà fait en haut.
# from gui.main_window import start_gui # Commenté pour le mode console

def main():
    """
    Fonction principale qui lance et orchestre Hector.
    """
    # Initialisation des modules essentiels
    try:
        brain = Brain()
        ears = Ears()
        voice = Voice()

    except Exception as e:
        print(f"Une erreur est survenue lors de l'initialisation des modules: {e}")
        sys.exit(1)

    voice.speak("Bonjour, je suis Hector. Je vous écoute.")
    print("Hector est prêt. Dites 'Hector' suivi de votre commande.")

    while True:
        try:
            time.sleep(0.1) # Petite pause pour ne pas surcharger la boucle

            print("\nEn attente de votre commande...")
            user_input = ears.listen()

            if not user_input:
                # print("Aucune entrée détectée.") # Décommenter pour debug si ears.listen() ne renvoie rien
                continue
            
            print(f"Vous: {user_input}")

            # Traitement du mot d'activation
            prompt = ""
            if config.ACTIVATION_KEYWORD.lower() in user_input.lower():
                prompt = user_input.lower().replace(config.ACTIVATION_KEYWORD.lower(), "").strip()
            else:
                prompt = user_input.lower().strip() # Traite tout l'input comme prompt si pas de mot d'activation

            if not prompt:
                print("Commande vide après traitement.")
                continue
            
            # Commandes d'arrêt
            if prompt in ["arrête-toi", "stop", "au revoir", "quitter"]:
                voice.speak("Au revoir. À bientôt !")
                print("Arrêt d'Hector.")
                break
            
            print("Hector: Je réfléchis...")

            # Le cerveau pense
            # Pour le mode console, l'historique n'est pas géré ici, il faudrait l'implémenter si tu veux une vraie conversation
            # Pour un simple tour, on envoie juste le prompt.
            # Pour simuler l'historique (très basique pour ce mode):
            # history = [{"role": "user", "content": prompt}]
            # response = brain.think(history) # Appelle le brain avec un historique simple

            # Ou pour un seul tour de conversation, sans historique complexe
            response = brain.think([{"role": "user", "content": prompt}])


            if response:
                print(f"Hector: {response}")
                voice.speak(response)
            else:
                voice.speak("Désolé, je n'ai pas pu générer de réponse.")
                print("Hector: Désolé, je n'ai pas pu générer de réponse.")

        except KeyboardInterrupt:
            print("\nArrêt demandé par l'utilisateur.")
            voice.speak("Arrêt demandé par l'utilisateur. Au revoir.")
            break
        except Exception as e:
            print(f"Une erreur inattendue est survenue dans la boucle principale: {e}")
            voice.speak("Oups, j'ai rencontré un problème inattendu. Essayons encore.")
            time.sleep(2) # Attendre un peu avant de retenter

    # La ligne start_gui() reste commentée pour le mode console
    # start_gui()

if __name__ == "__main__":
    main()