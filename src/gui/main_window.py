# --- FICHIER COMPLET : src/gui/main_window.py ---

import sys
import threading
import time
import json
import os
import re

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLineEdit, QLabel, QFrame, QStackedWidget, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QPixmap, QIcon, QPalette, QBrush, QMovie, QRegion, QPainterPath
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl, QSize, QRect, QBuffer, QTimer # NOUVEL IMPORT
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage

from modules.brain import Brain
from modules.ears import Ears
from modules.voice import Voice
from modules.actions import Actions
import config

# ... (AudioListenThread inchangé) ...
class AudioListenThread(QThread):
    transcribed_text = pyqtSignal(str)
    def __init__(self, ears_module):
        super().__init__()
        self.ears = ears_module
    def run(self):
        user_input = self.ears.listen()
        if user_input: self.transcribed_text.emit(user_input)

class HectorWindow(QWidget):
    # ... (signaux inchangés) ...
    update_conversation_signal = pyqtSignal(str, str)
    enable_input_signal = pyqtSignal(bool)
    load_url_signal = pyqtSignal(str)
    switch_view_signal = pyqtSignal(int)
    set_loading_indicator_signal = pyqtSignal(bool)
    web_page_data_ready = pyqtSignal(str, str)
    execute_click_signal = pyqtSignal(str) # Signal pour le clic
    execute_type_text_signal = pyqtSignal(str, str) # NOUVEAU signal pour la saisie de texte

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hector AI Assistant")
        self.setGeometry(100, 100, 1200, 700)
        self.background_image_path = str(config.BASE_DIR / "src/gui/assets/background.png")
        
        # NOUVEAU : Initialisation du timer
        self.analysis_timer = QTimer(self)
        self.analysis_timer.setSingleShot(True) # Le timer ne se déclenche qu'une fois
        self.analysis_timer.timeout.connect(self._on_analysis_timeout)

        self.current_task = ""
        self._is_page_analysis_pending = False
        self.update_background()
        self.setup_ui()
        self.init_hector_modules()
        self.connect_signals()
        self.start_initial_greeting()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(50)
        self.conversation_panel_widget = QFrame()
        self.conversation_panel_widget.setStyleSheet("background-color: rgba(255, 255, 255, 0.9); border-radius: 20px;")
        left_panel_layout = QVBoxLayout(self.conversation_panel_widget)
        left_panel_layout.setContentsMargins(20, 20, 20, 20)
        title_bar_layout = QHBoxLayout()
        self.app_title_label = QLabel("HECTOR AI Assistant")
        self.app_title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333; background-color: transparent;")
        title_bar_layout.addWidget(self.app_title_label)
        self.loading_label = QLabel()
        self.loading_movie = QMovie(str(config.BASE_DIR / "src/gui/assets/loading.gif"))
        self.loading_movie.setScaledSize(QSize(30, 30))
        self.loading_label.setMovie(self.loading_movie)
        self.loading_label.setVisible(False)
        title_bar_layout.addWidget(self.loading_label)
        title_bar_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        left_panel_layout.addLayout(title_bar_layout)
        self.conversation_display = QTextEdit()
        self.conversation_display.setReadOnly(True)
        self.conversation_display.setStyleSheet("background-color: transparent; border: none; font-size: 14px; color: #333;")
        left_panel_layout.addWidget(self.conversation_display, 1)
        command_input_layout = QHBoxLayout()
        command_input_layout.setSpacing(10)
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Tapez votre commande ici...")
        self.text_input.setStyleSheet("QLineEdit { background-color: #f0f0f0; border: 1px solid #ccc; padding: 10px 15px; font-size: 14px; border-radius: 20px; color: #333; } QLineEdit::placeholder { color: #888; }")
        self.text_input.returnPressed.connect(self.send_text_command)
        command_input_layout.addWidget(self.text_input, 1)
        self.speak_button = QPushButton(QIcon(str(config.BASE_DIR / "src/gui/assets/mic_icon.png")), "")
        self.speak_button.clicked.connect(self.start_voice_command)
        self.speak_button.setFixedSize(40, 40)
        self.speak_button.setStyleSheet("QPushButton { background-color: #f0f0f0; border: 1px solid #ccc; border-radius: 20px; } QPushButton:hover { background-color: #e0e0e0; }")
        command_input_layout.addWidget(self.speak_button)
        left_panel_layout.addLayout(command_input_layout)
        main_layout.addWidget(self.conversation_panel_widget, 1)
        self.right_panel_container = QFrame()
        self.right_panel_container.setStyleSheet("background-color: transparent; border: none;")
        right_panel_layout = QVBoxLayout(self.right_panel_container)
        right_panel_layout.setContentsMargins(0, 0, 0, 0)
        self.right_panel_stack = QStackedWidget()
        right_panel_layout.addWidget(self.right_panel_stack)
        self.right_panel_stack.addWidget(QWidget())
        self.web_view = QWebEngineView()
        self.web_view.page().setBackgroundColor(Qt.GlobalColor.transparent)
        profile = QWebEngineProfile("hector-browser-profile", self.web_view)
        web_page = QWebEnginePage(profile, self.web_view)
        self.web_view.setPage(web_page)
        self.web_view.setUrl(QUrl("about:blank"))
        self.right_panel_stack.addWidget(self.web_view)
        main_layout.addWidget(self.right_panel_container, 2)
    
    def update_background(self):
        self.setAutoFillBackground(True)
        palette = self.palette()
        pixmap = QPixmap(self.background_image_path)
        palette.setBrush(QPalette.ColorRole.Window, QBrush(pixmap.scaled(self.size(), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)))
        self.setPalette(palette)
    
    def resizeEvent(self, event):
        self.update_background()
        super().resizeEvent(event)
        radius = 20
        if self.conversation_panel_widget.width() > radius * 2 and self.conversation_panel_widget.height() > radius * 2:
            path_left = QPainterPath()
            path_left.addRoundedRect(self.conversation_panel_widget.rect().toRectF(), radius, radius)
            self.conversation_panel_widget.setMask(QRegion(path_left.toFillPolygon().toPolygon()))
        else:
            self.conversation_panel_widget.clearMask()
        if self.right_panel_container.width() > radius * 2 and self.right_panel_container.height() > radius * 2:
            path_right = QPainterPath()
            path_right.addRoundedRect(self.right_panel_container.rect().toRectF(), radius, radius)
            self.right_panel_container.setMask(QRegion(path_right.toFillPolygon().toPolygon()))
        else:
            self.right_panel_container.clearMask()

    def init_hector_modules(self):
        try:
            self.brain = Brain()
            self.ears = Ears()
            self.voice = Voice()
            self.actions = Actions()
            self.conversation_history = []
        except Exception as e:
            self.append_conversation("System Error", f"Échec de l'initialisation: {e}")

    def connect_signals(self):
        self.update_conversation_signal.connect(self._append_conversation_thread_safe)
        self.enable_input_signal.connect(self.set_input_enabled)
        self.set_loading_indicator_signal.connect(self.set_loading_indicator_visible)
        self.switch_view_signal.connect(self.right_panel_stack.setCurrentIndex)
        self.switch_view_signal.connect(self._update_right_panel_style)
        self.load_url_signal.connect(self._load_url_thread_safe)
        self.web_view.loadFinished.connect(self._on_web_view_load_finished)
        self.web_page_data_ready.connect(self._process_web_page_data)
        self.execute_click_signal.connect(self._execute_web_action_click) # Connexion du nouveau signal
        self.execute_type_text_signal.connect(self._execute_web_action_type_text) # Connexion du signal de saisie

    def _update_right_panel_style(self, index):
        if index == 1:
            self.right_panel_container.setStyleSheet("background-color: white; border: none;")
        else:
            self.right_panel_container.setStyleSheet("background-color: transparent; border: none;")
    
    def _load_url_thread_safe(self, url):
        self.web_view.setUrl(QUrl(url))

    def _on_web_view_load_finished(self, ok):
        if self.web_view.url().toString() == "about:blank":
            return # Ignore les chargements "about:blank"
        
        # NOUVEAU : Empêche les analyses multiples après des loadFinished consécutifs
        # C'est une correction importante pour éviter de déclencher plusieurs analyses
        # si la page a des redirections ou charge des sous-frames.
        if self._is_page_analysis_pending:
            print("AVERTISSEMENT: loadFinished déclenché mais une analyse est déjà en attente. Ignoré.")
            return

        if ok:
            current_url = self.web_view.url().toString()
            self.append_conversation("System", f"Page web chargée : {current_url}")
            self.set_loading_indicator_signal.emit(True) # Affiche l'indicateur
            
            # Marque qu'une analyse est en attente
            self._is_page_analysis_pending = True 
            
            # Démarre le timer pour le timeout (5 secondes)
            self.analysis_timer.start(5000) 
            
            # Lance l'analyse du DOM
            self._capture_and_describe_web_page()
        else:
            self.append_conversation("System Error", f"Échec du chargement de la page web: {self.web_view.url().toString()}")
            self.voice.speak(f"Désolé, je n'ai pas pu charger la page {self.web_view.url().toString()}")
            self.enable_input_signal.emit(True)
            self.set_loading_indicator_signal.emit(False)
            self._is_page_analysis_pending = False # Réinitialise le drapeau en cas d'erreur
            
    def _on_analysis_timeout(self):
        self.append_conversation("System Error", "L'analyse de la page a expiré (timeout). La page est peut-être trop complexe ou a bloqué le script.")
        self.enable_input_signal.emit(True)
        self.set_loading_indicator_signal.emit(False)
        self._is_page_analysis_pending = False 

    def _capture_and_describe_web_page(self):
        self.append_conversation("Hector", "J'analyse la page web visible...")
        js_script = """
        (function() {
            try {
                const elements = Array.from(document.querySelectorAll('a, button, input:not([type="hidden"]), textarea, select, [role="button"], [tabindex="0"]'));
                let interactive_data = [];
                elements.forEach((el, index) => {
                    let text = el.innerText || el.value || el.placeholder || el.getAttribute('aria-label') || el.title || '';
                    text = text.replace(/\\n/g, ' ').replace(/\\s{2,}/g, ' ').trim();
                    if (text || (el.tagName === 'INPUT' && el.type !== 'hidden')) {
                        interactive_data.push({ index: index, tag: el.tagName.toLowerCase(), id: el.id || '', text: text });
                    }
                });
                let tempDoc = document.cloneNode(true);
                tempDoc.querySelectorAll('script, style, nav, footer, header, aside, form').forEach(el => el.remove());
                // Pour H100, on peut augmenter la limite du texte extrait. Augmenté à 8000 caractères.
                let main_text = (tempDoc.body.innerText || '').replace(/\\n+/g, ' ').replace(/\\s{2,}/g, ' ').trim().substring(0, 30000); 
                return JSON.stringify({ status: 'success', interactive_elements: interactive_data, text_content: main_text });
            } catch (error) { return JSON.stringify({ status: 'error', message: error.toString() }); }
        })();
        """
        self.web_view.page().runJavaScript(js_script, self._handle_dom_description_result)

    def _handle_dom_description_result(self, result):
        self.analysis_timer.stop() 
        try:
            if result is None: 
                raise ValueError("Le script JavaScript n'a rien retourné (peut-être une page vide ou un problème de sécurité du navigateur).")
            response = json.loads(result)
            if response.get('status') == 'error': 
                raise ValueError(f"Erreur JavaScript: {response.get('message', 'Inconnue')}")
            
            dom_elements = response.get('interactive_elements', [])
            text_content = response.get('text_content', '')
            current_url = self.web_view.url().toString()
            
            dom_description = f"URL ACTUELLE: {current_url}\n\n"
            dom_description += f"CONTENU TEXTUEL DE LA PAGE (extrait):\n{text_content}\n\n"
            
            # --- LOGIQUE AMÉLIORÉE DE DÉTECTION DE POPUP ---
            popup_keywords = ['accept', 'accepter', 'consent', 'cookies', 'continue', 'fermer', 'ok', 'got it', 'i agree']
            # Cherche des éléments avec ces mots-clés dans le texte, qui sont des boutons ou des liens.
            popup_elements = [el for el in dom_elements if el.get('tag') in ['button', 'a'] and any(kw in el.get('text','').lower() for kw in popup_keywords)]

            final_elements_for_llm = []
            if popup_elements:
                # SI UN POPUP EST DÉTECTÉ, ON NE MONTRE QUE SES ÉLÉMENTS !
                dom_description += "ATTENTION : Un popup de consentement a été détecté. Concentre-toi EXCLUSIVEMENT sur ces éléments pour accepter :\n"
                final_elements_for_llm = popup_elements
            else:
                # Si pas de popup, sélectionne les éléments les plus probables pour l'interaction
                dom_description += "ÉLÉMENTS INTERACTIFS DÉTECTÉS (avec index pour référence) :\n"
                # Priorité : inputs, boutons, liens non vides. Limite à un nombre raisonnable.
                for el in dom_elements:
                    text = el.get('text', '').strip()
                    tag = el.get('tag')
                    # Inclut les champs de saisie, et les boutons/liens avec texte
                    if tag in ['input', 'textarea', 'select'] or (tag in ['button', 'a'] and text):
                        final_elements_for_llm.append(el)
                    if len(final_elements_for_llm) >= 100: # Limite a 50 car H100 peut gérer plus, mais peut monter plus haut.
                        break

            if not final_elements_for_llm:
                 dom_description += "Aucun élément interactif pertinent trouvé sur la page."
            else:
                for el in final_elements_for_llm:
                    index = el.get('index')
                    tag = el.get('tag')
                    el_type = el.get('type')
                    el_id = el.get('id')
                    el_name = el.get('name')
                    text_display = el.get('text')
                    
                    identifying_info = []
                    if text_display: identifying_info.append(f"texte='{text_display}'")
                    if el_id: identifying_info.append(f"id='{el_id}'")
                    if el_name: identifying_info.append(f"name='{el_name}'")
                    if el_type: identifying_info.append(f"type='{el_type}'")
                    
                    dom_description += f"[{index}] <{tag}> ({', '.join(identifying_info)})\n"
            
            self.web_page_data_ready.emit(current_url, dom_description)
            self._is_page_analysis_pending = False 

        except Exception as e:
            self.append_conversation("System Error", f"Erreur lors de l'analyse du DOM : {e}")
            self.enable_input_signal.emit(True)
            self.set_loading_indicator_signal.emit(False)
            self._is_page_analysis_pending = False 

    def _process_web_page_data(self, url, dom_description):
        full_context_message_content = ""

        if self.current_task:
            full_context_message_content += f"Information: La page a changé. Mon objectif initial est toujours : '{self.current_task}'. "
            full_context_message_content += "Analyse la page ci-dessous et décide de la prochaine étape.\n\n"
        
        full_context_message_content += f"Résultat d'outil:\n{dom_description}" 
        self.conversation_history.append({"role": "user", "content": full_context_message_content})
        self.append_conversation("Hector", "Je décide de la prochaine action...")
        threading.Thread(target=self.process_command, daemon=True).start()

    def _execute_web_action_click(self, element_identifier: str):
        self.append_conversation("System", f"Exécution du clic sur l'élément '{element_identifier}'...")
        # Échappe correctement l'identifiant pour l'insertion dans la chaîne JS
        escaped_element_identifier = element_identifier.replace("'", "\\'").replace('"', '\\"') 
        
        # Le script JS recherche l'élément par plusieurs critères
        js_script = f"""
        (function() {{
            let targetElement = null;
            const allElements = Array.from(document.querySelectorAll('a, button, input:not([type="hidden"]), textarea, select, [role="button"], [tabindex="0"]'));
            const lowerCaseIdentifier = '{escaped_element_identifier}'.toLowerCase();
            const identifierAsInt = parseInt('{escaped_element_identifier}', 10);

            // 1. Recherche par index numérique (le plus précis si fourni par le LLM)
            if (!isNaN(identifierAsInt) && identifierAsInt >= 0 && identifierAsInt < allElements.length) {{
                targetElement = allElements[identifierAsInt];
            }}

            // 2. Recherche EXACTE par TEXTE visible (innerText), VALUE, PLACEHOLDER, ARIA-LABEL ou TITLE
            if (!targetElement) {{
                targetElement = allElements.find(el => 
                    (el.innerText && el.innerText.toLowerCase() === lowerCaseIdentifier) || 
                    (el.value && el.value.toLowerCase() === lowerCaseIdentifier) ||       
                    (el.placeholder && el.placeholder.toLowerCase() === lowerCaseIdentifier) || 
                    (el.getAttribute('aria-label') && el.getAttribute('aria-label').toLowerCase() === lowerCaseIdentifier) ||
                    (el.title && el.title.toLowerCase() === lowerCaseIdentifier)
                );
            }}

            // 3. Recherche par ID HTML original
            if (!targetElement && document.getElementById('{escaped_element_identifier}')) {{
                targetElement = document.getElementById('{escaped_element_identifier}');
            }}
            
            // 4. Recherche "floue" (contains) par texte, en dernier recours
            if (!targetElement) {{
                targetElement = allElements.find(el => 
                    (el.innerText && el.innerText.toLowerCase().includes(lowerCaseIdentifier)) ||
                    (el.value && el.value.toLowerCase().includes(lowerCaseIdentifier)) ||
                    (el.placeholder && el.placeholder.toLowerCase().includes(lowerCaseIdentifier)) ||
                    (el.getAttribute('aria-label') && el.getAttribute('aria-label').toLowerCase().includes(lowerCaseIdentifier)) ||
                    (el.title && el.title.toLowerCase().includes(lowerCaseIdentifier))
                );
            }}

            if (targetElement) {{
                // Pour certains éléments (comme les liens), un clic direct peut être préféré
                // Pour d'autres (boutons complexes), simuler un clic JS
                if (targetElement.tagName === 'A' && targetElement.href) {{
                     // Correction pour l'erreur 1 : Pas besoin d'accolades dans le JS si tu utilises une f-string Python pour le JS.
                     // On s'assure que 'href' est bien une chaîne.
                     window.location.href = targetElement.href; 
                }} else {{
                    targetElement.click(); // Simule un clic normal
                }}
                return 'Clic effectué sur ' + (targetElement.innerText || targetElement.value || targetElement.placeholder || targetElement.tagName || '{escaped_element_identifier}');
            }} else {{
                return 'Erreur : Élément "{escaped_element_identifier}" non trouvé pour le clic.';
            }}
        }})();
        """
        self.web_view.page().runJavaScript(js_script, self._handle_web_action_result)

    def _execute_web_action_type_text(self, element_identifier: str, text: str):
        
        self.append_conversation("System", f"Saisie de '{text}' dans l'élément '{element_identifier}'...")
        
        # Correction pour l'erreur 2 : Échappe le texte en Python avant de l'insérer dans la f-string JS.
        # On utilise une triple accolade pour que Python ne l'interprète pas comme une variable de f-string.
        # En JS, les backticks sont des template literals, donc on échappe les backticks à l'intérieur du texte.
        # On échappe aussi les guillemets simples et doubles pour la sécurité.
        escaped_element_identifier = element_identifier.replace("'", "\\'").replace('"', '\\"')
        escaped_text_to_type = text.replace("`", "\\`").replace("'", "\\'").replace('"', '\\"') 
        
        js_script = f"""
        (function() {{
            let targetElement = null;
            const allElements = Array.from(document.querySelectorAll('input:not([type="hidden"]), textarea, select')); // Seuls les champs de saisie
            const lowerCaseIdentifier = '{escaped_element_identifier}'.toLowerCase();
            const identifierAsInt = parseInt('{escaped_element_identifier}', 10);
            const textToType = `{escaped_text_to_type}`; // Utilisez les backticks JS pour une template string

            // 1. Recherche par index numérique
            if (!isNaN(identifierAsInt) && identifierAsInt >= 0 && identifierAsInt < allElements.length) {{
                targetElement = allElements[identifierAsInt];
            }}

            // 2. Recherche par ID HTML
            if (!targetElement && document.getElementById('{escaped_element_identifier}')) {{
                targetElement = document.getElementById('{escaped_element_identifier}');
            }}

            // 3. Recherche par NAME, PLACEHOLDER, ARIA-LABEL ou TEXTE visible (pour les selects)
            if (!targetElement) {{
                targetElement = allElements.find(el => 
                    (el.name && el.name.toLowerCase() === lowerCaseIdentifier) ||
                    (el.placeholder && el.placeholder.toLowerCase() === lowerCaseIdentifier) ||
                    (el.getAttribute('aria-label') && el.getAttribute('aria-label').toLowerCase() === lowerCaseIdentifier) ||
                    (el.innerText && el.innerText.toLowerCase() === lowerCaseIdentifier) // Pour les <select> par exemple
                );
            }}

            // 4. Recherche "floue" par NAME, PLACEHOLDER, ARIA-LABEL
            if (!targetElement) {{
                targetElement = allElements.find(el => 
                    (el.name && el.name.toLowerCase().includes(lowerCaseIdentifier)) ||
                    (el.placeholder && el.placeholder.toLowerCase().includes(lowerCaseIdentifier)) ||
                    (el.getAttribute('aria-label') && el.getAttribute('aria-label').toLowerCase().includes(lowerCaseIdentifier))
                );
            }}

            if (targetElement) {{
                if (targetElement.tagName === 'SELECT') {{
                    // Pour les selects, tente de trouver l'option par son texte ou sa valeur
                    let optionFound = Array.from(targetElement.options).find(opt => 
                        opt.text.toLowerCase() === textToType.toLowerCase() || 
                        opt.value.toLowerCase() === textToType.toLowerCase()
                    );
                    if (optionFound) {{
                        targetElement.value = optionFound.value;
                    }} else {{
                        // Si l'option n'est pas trouvée par texte/valeur, tente de mettre le texte directement
                        targetElement.value = textToType; 
                    }}
                }} else {{
                    targetElement.value = textToType;
                }}
                // Déclenche les événements pour s'assurer que les frameworks JS réagissent
                targetElement.dispatchEvent(new Event('input', {{ bubbles: true }}));
                targetElement.dispatchEvent(new Event('change', {{ bubbles: true }}));
                return 'Texte saisi dans ' + (targetElement.name || targetElement.placeholder || targetElement.tagName || '{escaped_element_identifier}');
            }} else {{
                return 'Erreur : Élément "{escaped_element_identifier}" non trouvé pour la saisie.';
            }}
        }})();
        """ # Correction pour l'erreur 3 : Assurez-vous que la f-string se termine ici avec les trois guillemets
        self.web_view.page().runJavaScript(js_script, self._handle_web_action_result)
       
    def _handle_web_action_result(self, result):
        if result and "Erreur" in result:
            self.append_conversation("System Error", result)
            self.voice.speak(result) # Fait parler Hector pour signaler l'erreur
            self.enable_input_signal.emit(True) # Si le clic échoue, on redonne la main
            self.set_loading_indicator_signal.emit(False)
        else:
            self.append_conversation("System", f"Action web exécutée : {result}. Je vais maintenant ré-analyser la page pour voir les changements.")
            
            # SOLUTION : DÉCLENCHER UNE NOUVELLE ANALYSE APRÈS L'ACTION
            # On attend un court instant (ex: 2 secondes) pour laisser le temps à la page
            # de se mettre à jour via JavaScript, puis on relance l'analyse du DOM.
            # QTimer.singleShot est parfait pour cela car il s'intègre à la boucle d'événements de Qt.
            QTimer.singleShot(2000, self._capture_and_describe_web_page)
            
    def start_initial_greeting(self):
        threading.Thread(target=self._initial_greeting_task, daemon=True).start()
    
    def _initial_greeting_task(self):
        time.sleep(1)
        self.voice.speak("Bonjour, je suis Hector. Comment puis-je vous aider ?")
        self.enable_input_signal.emit(True)
    
    def append_conversation(self, role, message):
        self.update_conversation_signal.emit(role, message)
    
    def _append_conversation_thread_safe(self, role, message):
        current_text = self.conversation_display.toHtml()
        colors = {"User": "#333", "Hector": "#007bff", "Tool": "#6c757d", "System Error": "#dc3545", "System": "#ffc107"} # Supprime web_page_vision car ce rôle n'est plus directement affiché ainsi.
        new_entry = f"<p style='color:{colors.get(role, '#333')};'><b>{role}:</b> {message.replace('<', '&lt;').replace('>', '&gt;')}</p>"
        self.conversation_display.setHtml(current_text + new_entry)
        self.conversation_display.verticalScrollBar().setValue(self.conversation_display.verticalScrollBar().maximum())
    
    def set_input_enabled(self, enabled):
        self.text_input.setEnabled(enabled)
        self.speak_button.setEnabled(enabled)
        self.text_input.setPlaceholderText("Tapez votre commande..." if enabled else "Hector réfléchit...")
        if enabled:
            self.set_loading_indicator_signal.emit(False)
    
    def set_loading_indicator_visible(self, visible):
        self.loading_label.setVisible(visible)
        if visible: self.loading_movie.start()
        else: self.loading_movie.stop()
    
    def send_text_command(self):
        command = self.text_input.text().strip()
        if command:
            self.current_task = command
            # Réinitialise l'historique pour une nouvelle tâche utilisateur
            self.conversation_history = [{"role": "user", "content": command}] 
            self.append_conversation("User", command)
            self.set_input_enabled(False)
            self.set_loading_indicator_signal.emit(True)
            threading.Thread(target=self.process_command, daemon=True).start()
        self.text_input.clear()
    
    def start_voice_command(self):
        self.append_conversation("System", "Écoute en cours...")
        self.set_input_enabled(False)
        self.set_loading_indicator_signal.emit(True)
        self.listen_thread = AudioListenThread(self.ears)
        self.listen_thread.transcribed_text.connect(self.process_voice_command)
        self.listen_thread.start()
    
    def process_voice_command(self, transcribed_text):
        if transcribed_text:
            self.current_task = transcribed_text 
            # Réinitialise l'historique pour une nouvelle tâche utilisateur
            self.conversation_history = [{"role": "user", "content": transcribed_text}]
            self.append_conversation("User", transcribed_text)
            self.set_loading_indicator_signal.emit(True)
            threading.Thread(target=self.process_command, daemon=True).start()
        else:
            self.append_conversation("System", "Je n'ai rien compris.")
            self.set_input_enabled(True)
       
    def _parse_tool_call(self, response_text):
        """
        Analyse le texte de réponse du LLM pour trouver un appel d'outil.
        Gère les backticks potentiellement générées par le LLM.
        Retourne (tool_name, tool_params) ou (None, None) si non trouvé.
        """
        known_tools = "|".join([name for name, func in self.actions.__class__.__dict__.items() if callable(func) and not name.startswith("__")])
        
        # Regex améliorée :
        # - Ajoute `?` au début et à la fin pour rendre les backticks optionnelles.
        # - S'assure de matcher le début/fin de la chaîne ou des retours à la ligne.
        match = re.search(rf'^(?:`?\s*)?({known_tools})\s*\((.*)\)(?:\s*`?)?$', response_text.strip(), re.IGNORECASE | re.DOTALL)
        
        if match:
            tool_name = match.group(1).lower() # Normalise le nom de l'outil
            params_str = match.group(2)
            
            tool_params = {}
            # Regex pour extraire key="value" ou key='value' ou key=value (si pas de guillemets)
            param_matches = re.findall(r'(\w+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|(\S+))', params_str)
            
            for key, val_double, val_single, val_unquoted in param_matches:
                value = val_double or val_single or val_unquoted
                tool_params[key] = value
                
            return tool_name, tool_params
        return None, None
    
    def _execute_web_action_type_text(self, element_identifier: str, text: str):
        self.append_conversation("System", f"Saisie de '{text}' dans l'élément '{element_identifier}'...")
        # Le script JS recherche l'élément par plusieurs critères
        js_script = f"""
        (function() {{
            let targetElement = null;
            const allElements = Array.from(document.querySelectorAll('input:not([type="hidden"]), textarea, select')); // Seuls les champs de saisie
            const lowerCaseIdentifier = '{element_identifier}'.toLowerCase();
            const identifierAsInt = parseInt('{element_identifier}', 10);
            const textToType = `{{text.replace(/`/g, '\\`')}}`; // Échappe les backticks dans le texte

            // 1. Recherche par index numérique
            if (!isNaN(identifierAsInt) && identifierAsInt >= 0 && identifierAsInt < allElements.length) {{
                targetElement = allElements[identifierAsInt];
            }}

            // 2. Recherche par ID HTML
            if (!targetElement && document.getElementById('{element_identifier}')) {{
                targetElement = document.getElementById('{element_identifier}');
            }}

            // 3. Recherche par NAME, PLACEHOLDER, ARIA-LABEL ou TEXTE visible (pour les selects)
            if (!targetElement) {{
                targetElement = allElements.find(el => 
                    (el.name && el.name.toLowerCase() === lowerCaseIdentifier) ||
                    (el.placeholder && el.placeholder.toLowerCase() === lowerCaseIdentifier) ||
                    (el.getAttribute('aria-label') && el.getAttribute('aria-label').toLowerCase() === lowerCaseIdentifier) ||
                    (el.innerText && el.innerText.toLowerCase() === lowerCaseIdentifier) // Pour les <select> par exemple
                );
            }}

            // 4. Recherche "floue" par NAME, PLACEHOLDER, ARIA-LABEL
            if (!targetElement) {{
                targetElement = allElements.find(el => 
                    (el.name && el.name.toLowerCase().includes(lowerCaseIdentifier)) ||
                    (el.placeholder && el.placeholder.toLowerCase().includes(lowerCaseIdentifier)) ||
                    (el.getAttribute('aria-label') && el.getAttribute('aria-label').toLowerCase().includes(lowerCaseIdentifier))
                );
            }}

            if (targetElement) {{
                if (targetElement.tagName === 'SELECT') {{
                    // Pour les selects, tente de trouver l'option par son texte ou sa valeur
                    let optionFound = Array.from(targetElement.options).find(opt => 
                        opt.text.toLowerCase() === textToType.toLowerCase() || 
                        opt.value.toLowerCase() === textToType.toLowerCase()
                    );
                    if (optionFound) {{
                        targetElement.value = optionFound.value;
                    }} else {{
                        // Si l'option n'est pas trouvée par texte/valeur, tente de mettre le texte directement
                        targetElement.value = textToType; 
                    }}
                }} else {{
                    targetElement.value = textToType;
                }}
                // Déclenche les événements pour s'assurer que les frameworks JS réagissent
                targetElement.dispatchEvent(new Event('input', {{ bubbles: true }}));
                targetElement.dispatchEvent(new Event('change', {{ bubbles: true }}));
                return 'Texte saisi dans ' + (targetElement.name || targetElement.placeholder || targetElement.tagName || '{element_identifier}');
            }} else {{
                return 'Erreur : Élément "{element_identifier}" non trouvé pour la saisie.';
            }}
        }})();
        """
        self.web_view.page().runJavaScript(js_script, self._handle_web_action_result)

    #def _prune_conversation_history(self):
    #    """
    #    Gère la taille de l'historique pour éviter de dépasser la fenêtre de contexte du LLM,
    #    en se basant sur la longueur totale du contenu.
    #    """
    #    # Seuil de sécurité en caractères. On le baisse à 8000 pour se déclencher avant le crash.
    #    MAX_CONTEXT_LENGTH = 32768   # <--- MODIFIE CETTE VALEUR DE 15000 À 8000
    #    
    #    current_length = 0
    #    for item in self.conversation_history:
    #        current_length += len(item.get("content", ""))
    #
    #    if current_length > MAX_CONTEXT_LENGTH:
    #        print(f"AVERTISSEMENT: La longueur de l'historique ({current_length}) dépasse le seuil de {MAX_CONTEXT_LENGTH}. Troncature...")
    #        
    #        # On garde toujours la première requête (objectif principal)
    #        first_user_request = self.conversation_history[0]
    #        
    #        # On prend les derniers messages en partant de la fin jusqu'à ce qu'on soit sous le seuil.
    #        new_history_end = []
    #        length_of_end_part = 0
    #        for item in reversed(self.conversation_history):
    #            item_length = len(item.get("content", ""))
    #            # On s'assure de ne pas dépasser une partie du seuil juste avec les derniers messages
    #            if length_of_end_part + item_length > MAX_CONTEXT_LENGTH * 0.75:
    #                break
    #            new_history_end.insert(0, item) # Insère au début pour garder l'ordre
    #            length_of_end_part += item_length
    #        
    #        # Crée un message pour informer le LLM que l'historique a été coupé
    #        truncation_notice = {
    #            "role": "user", 
    #            "content": "[...Historique intermédiaire tronqué pour gérer la longueur. Rappel de l'objectif initial ci-dessus...]"
    #        }
    #        
    #        # Reconstruit l'historique final
    #        self.conversation_history = [first_user_request, truncation_notice] + new_history_end
    #        
    #        final_length = 0
    #        for item in self.conversation_history:
    #            final_length += len(item.get("content", ""))
    #        print(f"Historique après troncature. Nouvelle longueur : {final_length}")

    def process_command(self):

        self._prune_conversation_history()
        self.append_conversation("Hector", "Je réfléchis...")
        
        try:
            # 1. Obtenir la décision du cerveau
            hector_action_or_response = self.brain.think(self.conversation_history)
            self.conversation_history.append({"role": "assistant", "content": hector_action_or_response}) # Garde la décision brute dans l'historique
            
            # 2. Analyser la réponse pour un appel d'outil
            tool_name, tool_params = self._parse_tool_call(hector_action_or_response)

            if tool_name and tool_params is not None:
                # C'est un appel d'outil
                self.append_conversation("Tool", f"Exécution : {tool_name}({json.dumps(tool_params)})") # Utilise json.dumps pour un affichage propre des params
                
                if tool_name == 'search_web':
                    query = tool_params.get("query")
                    if query:
                        tool_result_raw = self.actions.search_web(query=query)
                        self.conversation_history.append({"role": "tool_result", "content": tool_result_raw})
                        
                        url_match = re.search(r"URL:\s*(https?://[^\s]+)", tool_result_raw)
                        if url_match:
                            url = url_match.group(1)
                            self.append_conversation("System", f"URL trouvée : {url}. Chargement...")
                            self.switch_view_signal.emit(1) # Ouvre le navigateur
                            self.load_url_signal.emit(url)  # Charge l'URL
                            # Le reste du cycle est géré par _on_web_view_load_finished
                        else:
                            # Si search_web ne retourne pas d'URL (ex: aucun résultat)
                            self.append_conversation("System Error", tool_result_raw)
                            self.voice.speak(tool_result_raw)
                            self.enable_input_signal.emit(True)
                    else:
                        self.append_conversation("System Error", "Requête manquante pour search_web.")
                        self.voice.speak("Désolé, je ne sais pas quoi chercher.")
                        self.enable_input_signal.emit(True)
                
                elif tool_name == 'click':
                    element_id = tool_params.get("element_id")
                    if element_id is not None:
                        self.execute_click_signal.emit(element_id) # DÉCLENCHE LE CLIC !
                        # L'exécution _handle_web_action_result prendra le relais
                    else:
                        self.append_conversation("System Error", "ID d'élément manquant pour le clic.")
                        self.voice.speak("Désolé, je ne sais pas où cliquer.")
                        self.enable_input_signal.emit(True)

                elif tool_name == 'type_text':
                    element_id = tool_params.get("element_id")
                    text_to_type = tool_params.get("text")
                    if element_id is not None and text_to_type is not None:
                        self.execute_type_text_signal.emit(element_id, text_to_type) # DÉCLENCHE LA SAISIE !
                        # L'exécution _handle_web_action_result prendra le relais
                    else:
                        self.append_conversation("System Error", "ID d'élément ou texte manquant pour la saisie.")
                        self.voice.speak("Désolé, je ne sais pas où ou quoi écrire.")
                        self.enable_input_signal.emit(True)
                
                elif tool_name == 'navigate':
                    url = tool_params.get("url")
                    if url:
                        self.append_conversation("System", f"Navigation directe vers : {url}.")
                        self.switch_view_signal.emit(1) # Ouvre le navigateur
                        self.load_url_signal.emit(url)
                        # L'exécution _on_web_view_load_finished prendra le relais
                    else:
                        self.append_conversation("System Error", "URL manquante pour la navigation.")
                        self.voice.speak("Désolé, je ne sais pas où naviguer.")
                        self.enable_input_signal.emit(True)

                else: # Pour tout autre outil non web (ex: get_current_time)
                    # Utilise getattr pour appeler dynamiquement la méthode de self.actions
                    tool_function = getattr(self.actions, tool_name, None)
                    if tool_function:
                        tool_result = tool_function(**tool_params)
                        self.append_conversation("Tool", f"Résultat : {tool_result[:200]}...")
                        self.conversation_history.append({"role": "tool_result", "content": tool_result})
                        
                        # Demande au cerveau de formuler la réponse finale
                        self.append_conversation("Hector", "Je formule la réponse finale...")
                        final_response = self.brain.think(self.conversation_history)
                        self.conversation_history.append({"role": "assistant", "content": final_response})
                        
                        self.append_conversation("Hector", final_response)
                        self.voice.speak(final_response)
                        self.enable_input_signal.emit(True)
                    else:
                        self.append_conversation("System Error", f"Outil '{tool_name}' inconnu ou non implémenté.")
                        self.voice.speak(f"Désolé, je ne connais pas l'outil {tool_name}.")
                        self.enable_input_signal.emit(True)

            else:
                # Ce n'est pas un appel d'outil, c'est une réponse directe du cerveau.
                self.switch_view_signal.emit(0) # Assure que le navigateur est fermé si on ne l'utilise plus.
                self.append_conversation("Hector", hector_action_or_response)
                self.voice.speak(hector_action_or_response)
                self.enable_input_signal.emit(True)

        except Exception as e:
            error_message = f"Erreur lors du traitement de la commande : {e}"
            self.append_conversation("System Error", error_message)
            self.voice.speak("Oups, une erreur est survenue pendant ma réflexion. Veuillez réessayer.")
            self.enable_input_signal.emit(True)
            self.set_loading_indicator_signal.emit(False)

def start_gui():
    # os.environ['QTWEBENGINE_DISABLE_SANDBOX'] = '1' # Déjà défini dans config.py si nécessaire, mais parfois utile ici.
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    window = HectorWindow()
    window.show()
    sys.exit(app.exec())