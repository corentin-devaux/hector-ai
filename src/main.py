import sys # Déjà importé normalement
import time # Déjà importé normalement
import config
from modules.brain import Brain
from modules.ears import Ears
from modules.voice import Voice
from modules.actions import Actions
import re

# L'import de sys est déjà fait en haut.
# from gui.main_window import start_gui # Commenté pour le mode console

def main():
    """
    Fonction principale qui lance et orchestre Hector.
    """
    # Initialisation des modules essentiels
    try:
        brain = Brain()
        # ears = Ears() # COMMENTEZ CETTE LIGNE
        # voice = Voice() # COMMENTEZ CETTE LIGNE
        actions = Actions() # Ajoutez ceci si ce n'est pas déjà fait
        conversation_history = [] # Pour un historique basique en console

    except Exception as e:
        print(f"Une erreur est survenue lors de l'initialisation des modules: {e}")
        sys.exit(1)

    # voice.speak("Bonjour, je suis Hector. Je vous écoute.") # COMMENTEZ CETTE LIGNE
    print("Hector est prêt. Tapez votre commande (ou 'quitter' pour arrêter).")

    while True:
        try:
            # time.sleep(0.1) # Petite pause pour ne pas surcharger la boucle

            print("\nVous: ")
            user_input = input().strip() # Remplace ears.listen() par une entrée texte

            if not user_input:
                print("Commande vide.")
                continue
             
            # Traitement du mot d'activation (gardez-le si vous voulez)
            prompt = user_input
            # if config.ACTIVATION_KEYWORD.lower() in user_input.lower():
            #     prompt = user_input.lower().replace(config.ACTIVATION_KEYWORD.lower(), "").strip()
            # else:
            #     prompt = user_input.lower().strip()

            if not prompt:
                print("Commande vide après traitement.")
                continue
             
            # Commandes d'arrêt
            if prompt.lower() in ["arrête-toi", "stop", "au revoir", "quitter"]:
                # voice.speak("Au revoir. À bientôt !") # COMMENTEZ CETTE LIGNE
                print("Arrêt d'Hector.")
                break
             
            print("Hector: Je réfléchis...")

            # Ajouter la requête utilisateur à l'historique
            conversation_history.append({"role": "user", "content": prompt})

            # Le cerveau pense
            hector_action_or_response = brain.think(conversation_history)
            conversation_history.append({"role": "assistant", "content": hector_action_or_response})

            print(f"Hector: {hector_action_or_response}")
            # voice.speak(hector_action_or_response) # COMMENTEZ CETTE LIGNE

            # --- GESTION DES OUTILS EN MODE CONSOLE (Simplifié) ---
            # Pour un test console simple, on ne gère pas les outils complexes comme click/type_text/navigate.
            # On se concentre sur les réponses directes ou les outils simples (get_current_time, create_video).
            tool_name, tool_params = None, None
            
            # Simple regex pour détecter un appel d'outil pour la console
            match = re.search(r'^(\w+)\s*\((.*)\)$', hector_action_or_response.strip())
            if match:
                tool_name = match.group(1).lower()
                params_str = match.group(2)
                tool_params = {}
                param_matches = re.findall(r'(\w+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|(\S+))', params_str)
                for key, val_double, val_single, val_unquoted in param_matches:
                    value = val_double or val_single or val_unquoted
                    tool_params[key] = value

            if tool_name and tool_params is not None:
                print(f"Hector (Tool): Exécution de {tool_name}({tool_params})")
                if tool_name == "get_current_time":
                    result = actions.get_current_time()
                    print(f"Résultat de l'outil : {result}")
                    conversation_history.append({"role": "tool_result", "content": result})
                    # Redemander au brain de formuler la réponse finale
                    final_response = brain.think(conversation_history)
                    conversation_history.append({"role": "assistant", "content": final_response})
                    print(f"Hector: {final_response}")
                elif tool_name == "create_video":
                    prompt_video = tool_params.get("prompt")
                    if prompt_video:
                        print(f"Génération vidéo en cours pour : '{prompt_video}'")
                        result = actions.create_video(prompt_video)
                        print(f"Résultat de l'outil : {result}")
                        conversation_history.append({"role": "tool_result", "content": result})
                        final_response = brain.think(conversation_history)
                        conversation_history.append({"role": "assistant", "content": final_response})
                        print(f"Hector: {final_response}")
                    else:
                        print("Erreur : Le prompt de la vidéo est manquant.")
                elif tool_name in ["search_web", "click", "type_text", "navigate"]:
                    print(f"NOTE: L'outil {tool_name} n'est pas entièrement simulé en mode console. Il a été appelé avec les paramètres : {tool_params}")
                    conversation_history.append({"role": "tool_result", "content": f"Outil {tool_name} appelé en mode console avec {tool_params}. (Pas de simulation réelle des résultats web)." })
                    # Pour permettre la continuation, demander au brain de formuler la prochaine étape ou réponse.
                    final_response = brain.think(conversation_history)
                    conversation_history.append({"role": "assistant", "content": final_response})
                    print(f"Hector: {final_response}")
                else:
                    print(f"Outil inconnu ou non géré en mode console: {tool_name}")
            # --- FIN GESTION DES OUTILS ---


        except KeyboardInterrupt:
            print("\nArrêt demandé par l'utilisateur.")
            # voice.speak("Arrêt demandé par l'utilisateur. Au revoir.") # COMMENTEZ CETTE LIGNE
            break
        except Exception as e:
            print(f"Une erreur inattendue est survenue dans la boucle principale: {e}")
            # voice.speak("Oups, j'ai rencontré un problème inattendu. Essayons encore.") # COMMENTEZ CETTE LIGNE
            time.sleep(2) # Attendre un peu avant de retenter

    # La ligne start_gui() reste commentée pour le mode console
    # start_gui()

if __name__ == "__main__":
     main()