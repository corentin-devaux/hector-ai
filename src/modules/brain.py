# --- FICHIER CORRIGÉ COMPLET : src/modules/brain.py ---

from llama_cpp import Llama
import config
import re

class Brain:
    """
    Gère le modèle de langage (LLM).
    """
    def __init__(self):
        print("Initialisation du cerveau (LLM)...")
        model_path = str(config.MODEL_PATH)
        try:
            self.llm = Llama(
                model_path=model_path,
                n_ctx=config.N_CTX,
                n_gpu_layers=config.N_GPU_LAYERS,
                use_mmap=True,
                verbose=False
            )
            print("Cerveau chargé.")
        except Exception as e:
            print(f"Échec CRITIQUE du chargement du cerveau : {e}")
            raise

    def think(self, history):
        if self.llm is None: return "Erreur interne."

        system_instruction = (
            "Tu es un assistant IA nommé Hector. Ton but est d'accomplir des tâches pour l'utilisateur en utilisant les outils à ta disposition : navigation web, création de contenu.\n"
            "**RÈGLES STRICTES (suis l'ordre de priorité) :**\n"
            "1. **GESTION DES POPUPS (PRIORITÉ ABSOLUE) :** Si la page web contient un popup de consentement (cookies, etc.), clique sur le bouton pour accepter (`Accepter`, `Continuer`, etc.). Ex: `click(element_id=\"Accepter\")`.\n"
            "2. **SAISIE DE TEXTE :** Si la tâche nécessite de taper du texte, utilise `type_text(element_id=\"ID ou placeholder\", text=\"texte à saisir\")`.\n"
            "4. **CLIC D'ACTION :** Pour activer des boutons, liens, etc., utilise `click(element_id=\"texte du bouton ou index\")`.\n"
            "5. **RECHERCHE WEB :** Si tu n'as pas l'information ou que tu n'es pas sur la bonne page, utilise `search_web(query=\"requête de recherche\")`.\n"
            "6. **CRÉATION VIDÉO :** Si l'utilisateur demande de créer une vidéo, utilise `create_video(prompt=\"description détaillée en anglais\")`.\n"
            "7. **RÉPONSE FINALE :** Si la tâche est accomplie ou si la réponse est visible, réponds directement à l'utilisateur. N'utilise AUCUN outil si ce n'est pas nécessaire.\n"
            "**FORMAT DE RÉPONSE (ACTION OU RÉPONSE, JAMAIS LES DEUX) :**\n"
            "- Action : `nom_outil(param1=\"valeur1\")`\n"
            "- Réponse : `Votre réponse ici.`\n"
            "Exemples : `click(element_id=\"Login Button\")`, `describe_image(image_id=\"photo_chat.jpg\")`, `Je n'ai pas trouvé de vol direct.`\n"
            "Sois direct et efficace. Ne génère jamais de phrases d'introduction comme 'Je vais faire cela.'."
        )
        
        messages_for_llm = [{"role": "system", "content": system_instruction}]
        
        for i, item in enumerate(history):
            if item["role"] == "tool_result":
                messages_for_llm.append({"role": "user", "content": f"Résultat d'outil:\n{item['content']}"})
            elif item["role"] == "user":
                if messages_for_llm and messages_for_llm[-1]["role"] == "user":
                    messages_for_llm[-1]["content"] += "\n\n" + item["content"]
                else:
                    messages_for_llm.append({"role": "user", "content": item["content"]})
            elif item["role"] == "assistant":
                if messages_for_llm and messages_for_llm[-1]["role"] == "assistant":
                    messages_for_llm[-1]["content"] += "\n\n" + item["content"]
                else:
                    messages_for_llm.append({"role": "assistant", "content": item["content"]})
        
        print("\n--- Contexte envoyé au LLM (APRES TRAITEMENT DES ROLES) ---")
        full_context_str = ""
        for msg in messages_for_llm:
            print(f"  {msg['role']}: {msg['content'][:200]}...")
            full_context_str += msg['content'] + " "
        print(f"Taille approximative du contexte (caractères) : {len(full_context_str)}")
        print(f"Nombre de messages : {len(messages_for_llm)}")
        print("----------------------------\n")

        try:
            output = self.llm.create_chat_completion(
                messages=messages_for_llm,
                max_tokens=2048, 
                temperature=0.1,
                stop=["<|eot_id|>", "<|end_of_turn|>", "###", "#", "\nUser:", "\nAssistant:"], 
                stream=False
            )
            response = output['choices'][0]['message']['content'].strip()
            
            if response.lower().startswith("hector:"): 
                response = response[len("hector:"):].strip()
            if "je réfléchis" in response.lower():
                response = "Désolé, j'ai eu un problème de réflexion ou la page est vide."
            
            print(f"DEBUG LLM RAW RESPONSE: {response}")

            if not response:
                return "Désolé, je n'ai pas pu générer de réponse claire pour cette étape."

            return response
        except Exception as e:
            print(f"ERREUR pendant la génération de la réponse : {e}")
            return "Désolé, j'ai eu un problème de réflexion."