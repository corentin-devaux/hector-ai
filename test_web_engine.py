import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
import os

# Optionnel, mais souvent utile pour diagnostiquer les problèmes de QtWebEngine
os.environ['QTWEBENGINE_DISABLE_SANDBOX'] = '1' 
os.environ['QT_LOGGING_RULES'] = 'qt.webenginecontext.debug=true' # Pour des logs plus détaillés

app = QApplication(sys.argv)

# Créer une fenêtre simple
window = QWidget()
window.setWindowTitle("Test PyQt6 WebEngine")
window.setGeometry(100, 100, 800, 600)

layout = QVBoxLayout(window)

# Créer un QWebEngineView
web_view = QWebEngineView()
web_view.setUrl(QUrl("https://www.google.com")) # Essayer une URL simple

layout.addWidget(web_view)
window.show()
sys.exit(app.exec())    