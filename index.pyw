import sys
import os
import yt_dlp
import threading
import pygame
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QFileDialog, QMenu,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QListWidget, QSlider, QWidget
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QIcon
from mutagen.mp3 import MP3
from mutagen import MutagenError

# Initialisation de pygame
pygame.mixer.init()

# Variables globales
current_playlist = []
current_index = 0
play_thread = None
is_paused = False
current_pos = 0
download_thread = None  # Thread pour le téléchargement
check_timer = None  # Timer pour vérifier la fin de la chanson

# Classe pour gérer les signaux
class SignalHandler(QObject):
    download_finished = pyqtSignal()
    download_error = pyqtSignal(str)

signal_handler = SignalHandler()

# Fonction pour obtenir le répertoire des fichiers audio
def get_exora_directory():
    home_dir = os.path.expanduser("~")
    exora_dir = os.path.join(home_dir, "exora")
    if not os.path.exists(exora_dir):
        os.makedirs(exora_dir)
    return exora_dir

# Fonction pour vérifier si un fichier est un véritable MP3
def is_valid_mp3(file_path):
    try:
        audio = MP3(file_path)
        return True
    except MutagenError:
        return False

# Fonction pour afficher la playlist dans la ListWidget
def show_playlist(playlist_listbox, playing_label, search_query=""):
    global current_playlist
    # Supprimer les éléments existants dans la ListWidget
    playlist_listbox.clear()

    exora_dir = get_exora_directory()
    current_playlist = []
    for filename in os.listdir(exora_dir):
        if filename.endswith(".mp3"):
            song_path = os.path.join(exora_dir, filename)
            if is_valid_mp3(song_path):
                song_name = os.path.splitext(filename)[0]
                if search_query.lower() in song_name.lower() or not search_query:
                    current_playlist.append(song_path)
                    # Tronquer le nom de la chanson à 100 caractères
                    truncated_song_name = song_name[:100]
                    playlist_listbox.addItem(truncated_song_name)
            else:
                handle_invalid_mp3(song_path, filename)

# Fonction pour gérer les fichiers MP3 invalides
def handle_invalid_mp3(song_path, filename):
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.setWindowTitle("Format non pris en charge")
    msg_box.setText(f"Le fichier '{filename}' n'est pas un fichier MP3 valide.")
    msg_box.setInformativeText("Que souhaitez-vous faire ?")

    # Ajouter des boutons personnalisés
    delete_button = msg_box.addButton("Supprimer", QMessageBox.DestructiveRole)
    open_folder_button = msg_box.addButton("Accéder au dossier", QMessageBox.ActionRole)
    ignore_button = msg_box.addButton("Ignorer", QMessageBox.RejectRole)

    msg_box.exec_()

    if msg_box.clickedButton() == delete_button:
        os.remove(song_path)
        QMessageBox.information(None, "Suppression", f"Le fichier '{filename}' a été supprimé.")
    elif msg_box.clickedButton() == open_folder_button:
        open_music_folder()
    elif msg_box.clickedButton() == ignore_button:
        pass  # Ignorer et ne rien faire

# Fonction pour télécharger une chanson depuis un lien YouTube en arrière-plan
def download_youtube_song(youtube_url, playlist_listbox, playing_label):
    global download_thread
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(get_exora_directory(), '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=True)
            song_name = info_dict.get('title', None)
            if song_name:
                signal_handler.download_finished.emit()
    except Exception as e:
        signal_handler.download_error.emit(str(e))
    finally:
        download_thread = None

# Fonction pour lancer le téléchargement en arrière-plan
def start_download(youtube_url, playlist_listbox, playing_label):
    global download_thread
    if download_thread and download_thread.is_alive():
        QMessageBox.warning(None, "Téléchargement", "Un téléchargement est déjà en cours.")
        return
    download_thread = threading.Thread(target=download_youtube_song, args=(youtube_url, playlist_listbox, playing_label))
    download_thread.start()

# Fonction pour lire une chanson
def play_song(playing_label, url=None):
    global current_index, play_thread, is_paused, current_pos, check_timer

    try:
        def play_audio(url):
            global is_paused, current_pos
            pygame.mixer.music.load(url)
            pygame.mixer.music.play(start=current_pos / 1000.0)
            is_paused = False
    except Exception as e:
        QMessageBox.critical(None, "Erreur de lecture", f"Erreur lors de la lecture de la chanson: {e}")

    if url:
        current_index = current_playlist.index(url)
    else:
        if current_index < len(current_playlist):
            url = current_playlist[current_index]
        else:
            QMessageBox.information(None, "Lecture", "Aucune musique à lire.")
            return

    playing_label.setText(f"Lecture en cours: {os.path.basename(url)}")
    if play_thread and play_thread.is_alive():
        play_thread.join()
    play_thread = threading.Thread(target=play_audio, args=(url,))
    play_thread.start()

    # Démarrer le timer pour vérifier la fin de la chanson
    if check_timer is not None:
        check_timer.stop()
    check_timer = QTimer()
    check_timer.timeout.connect(lambda: check_end_of_song(playing_label))
    check_timer.start(100)  # Vérifier toutes les 100 ms

# Fonction pour vérifier si la chanson est terminée et passer à la suivante
def check_end_of_song(playing_label):
    if not pygame.mixer.music.get_busy():
        next_song(playing_label)

# Fonction pour lire la chanson suivante automatiquement
def next_song(playing_label):
    global current_index, current_pos
    current_pos = 0
    if current_index < len(current_playlist) - 1:
        current_index += 1
    else:
        current_index = 0  # Relancer la première chanson si la playlist est terminée
    play_song(playing_label)

# Fonction pour lire la chanson sélectionnée dans la playlist
def play_selected_song(playing_label, playlist_listbox):
    selected_index = playlist_listbox.currentRow()
    if selected_index >= 0:
        url = current_playlist[selected_index]
        play_song(playing_label, url)

# Fonction pour mettre en pause ou reprendre la lecture
def pause_song():
    global is_paused, current_pos, check_timer
    if pygame.mixer.music.get_busy():
        if is_paused:
            pygame.mixer.music.unpause()
            if check_timer is not None:
                check_timer.start()  # Redémarrer le timer
        else:
            current_pos = pygame.mixer.music.get_pos()
            pygame.mixer.music.pause()
            if check_timer is not None:
                check_timer.stop()  # Arrêter le timer
        is_paused = not is_paused

# Fonction pour passer à la chanson suivante
def skip_song(playing_label):
    next_song(playing_label)

# Fonction pour revenir à la chanson précédente
def back_song(playing_label):
    global current_index, current_pos
    current_pos = 0
    if current_index > 0:
        current_index -= 1
        pygame.mixer.music.stop()
        play_song(playing_label)
    else:
        QMessageBox.information(None, "Lecture", "Aucune musique précédente.")

# Fonction pour mettre à jour le volume
def update_volume(value):
    pygame.mixer.music.set_volume(value / 100)

# Fonction pour ouvrir le dossier où sont stockées les musiques
def open_music_folder():
    exora_dir = get_exora_directory()
    if os.path.exists(exora_dir):
        if sys.platform == "win32":
            os.startfile(exora_dir)
        else:
            subprocess.Popen(['xdg-open', exora_dir])
    else:
        QMessageBox.warning(None, "Dossier introuvable", "Le dossier des musiques n'existe pas.")

# Fonction pour supprimer une chanson de la playlist
def delete_song(playlist_listbox):
    selected_index = playlist_listbox.currentRow()
    if selected_index >= 0:
        if current_index == selected_index:
            QMessageBox.warning(None, "Erreur", "Vous ne pouvez pas supprimer la chanson actuellement en lecture.")
            return
        # Supprimer le fichier physique
        os.remove(current_playlist[selected_index])
        # Supprimer l'élément de la playlist
        current_playlist.pop(selected_index)
        # Mettre à jour l'affichage de la playlist
        show_playlist(playlist_listbox, None)

# Classe principale de l'application
class MusicPlayerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Exora Music")
        self.setWindowIcon(QIcon("exora.ico"))
        self.setGeometry(800, 600, 800, 600)
        self.setStyleSheet("background-color: #222; color: white;")

        # Layout principal
        main_layout = QVBoxLayout()

        # Bandeau de titre
        title_layout = QHBoxLayout()
        title_label = QLabel("Exora Music")
        title_label.setStyleSheet("font-size: 24px; color: white; font-weight: bold;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        quit_button = QPushButton("Déconnexion")
        quit_button.setStyleSheet("background-color: purple; color: white; border: none; padding: 5px 10px;")
        title_layout.addWidget(quit_button)
        main_layout.addLayout(title_layout)

        # Champ de recherche
        search_layout = QHBoxLayout()
        search_label = QLabel("Rechercher un son")
        search_label.setStyleSheet("font-size: 18px; color: white;")
        search_layout.addWidget(search_label)
        self.search_song_input = QLineEdit()
        self.search_song_input.setStyleSheet("background-color: #333; color: white; border: 1px solid #444; padding: 5px;")
        self.search_song_input.setPlaceholderText("Nom du son")
        search_layout.addWidget(self.search_song_input)
        main_layout.addLayout(search_layout)

        # Champ pour ajouter un son
        add_layout = QHBoxLayout()
        add_label = QLabel("Ajouter un son")
        add_label.setStyleSheet("font-size: 18px; color: white;")
        add_layout.addWidget(add_label)
        self.add_song_input = QLineEdit()
        self.add_song_input.setStyleSheet("background-color: #333; color: white; border: 1px solid #444; padding: 5px;")
        self.add_song_input.setPlaceholderText("Ajouter un lien YouTube")
        add_layout.addWidget(self.add_song_input)
        main_layout.addLayout(add_layout)

        # Playlist
        playlist_layout = QHBoxLayout()
        playlist_label = QLabel("Playlist")
        playlist_label.setStyleSheet("font-size: 18px; color: white;")
        playlist_layout.addWidget(playlist_label)
        self.playlist = QListWidget()
        self.playlist.setStyleSheet("background-color: #333; color: white; border: 1px solid #444; padding: 5px;")
        playlist_layout.addWidget(self.playlist)
        main_layout.addLayout(playlist_layout)

        # Contrôles
        controls_layout = QHBoxLayout()
        controls_layout.addStretch()
        self.play_button = QPushButton("Play")
        self.play_button.setStyleSheet("background-color: purple; color: white; border: none; padding: 10px 20px;")
        controls_layout.addWidget(self.play_button)
        self.pause_button = QPushButton("Pause")
        self.pause_button.setStyleSheet("background-color: purple; color: white; border: none; padding: 10px 20px;")
        controls_layout.addWidget(self.pause_button)
        self.skip_button = QPushButton("Skip")
        self.skip_button.setStyleSheet("background-color: purple; color: white; border: none; padding: 10px 20px;")
        controls_layout.addWidget(self.skip_button)
        self.back_button = QPushButton("Back")
        self.back_button.setStyleSheet("background-color: purple; color: white; border: none; padding: 10px 20px;")
        controls_layout.addWidget(self.back_button)
        self.actualiser_button = QPushButton("Actualiser")
        self.actualiser_button.setStyleSheet("background-color: purple; color: white; border: none; padding: 10px 20px;")
        controls_layout.addWidget(self.actualiser_button)
        self.open_folder_button = QPushButton("Ouvrir le dossier")
        self.open_folder_button.setStyleSheet("background-color: purple; color: white; border: none; padding: 10px 20px;")
        controls_layout.addWidget(self.open_folder_button)
        controls_layout.addStretch()
        main_layout.addLayout(controls_layout)

        # Volume
        volume_layout = QHBoxLayout()
        volume_label = QLabel("Volume")
        volume_label.setStyleSheet("font-size: 18px; color: white;")
        volume_layout.addWidget(volume_label)
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setStyleSheet("background-color: #333; color: white;")
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(100)
        volume_layout.addWidget(self.volume_slider)
        main_layout.addLayout(volume_layout)

        # Chanson en cours de lecture
        self.playing_label = QLabel("Aucune musique en lecture")
        self.playing_label.setStyleSheet("font-size: 16px; color: white; margin-top: 20px;")
        self.playing_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.playing_label)

        # Crédits
        credits_label = QLabel("Créé par Morearty")
        credits_label.setStyleSheet("font-size: 12px; color: white; margin-top: 20px; text-align: center;")
        credits_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(credits_label)

        # Définir le layout principal
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Connecter les boutons aux fonctions
        self.play_button.clicked.connect(lambda: play_song(self.playing_label))
        self.pause_button.clicked.connect(pause_song)
        self.skip_button.clicked.connect(lambda: skip_song(self.playing_label))
        self.back_button.clicked.connect(lambda: back_song(self.playing_label))
        self.actualiser_button.clicked.connect(lambda: show_playlist(self.playlist, self.playing_label))
        self.open_folder_button.clicked.connect(open_music_folder)

        # Connecter le champ de texte pour ajouter une chanson
        self.add_song_input.returnPressed.connect(self.add_song)

        # Connecter le champ de texte pour rechercher une chanson
        self.search_song_input.returnPressed.connect(self.search_song)

        # Connecter le slider pour le volume
        self.volume_slider.valueChanged.connect(update_volume)
        self.volume_slider.setValue(100)  # Volume maximal par défaut

        # Connecter le clic droit sur la playlist pour supprimer une chanson
        self.playlist.setContextMenuPolicy(Qt.CustomContextMenu)
        self.playlist.customContextMenuRequested.connect(self.show_context_menu)

        # Lier l'événement de sélection à la fonction play_selected_song
        self.playlist.itemClicked.connect(lambda: play_selected_song(self.playing_label, self.playlist))

        # Connecter les signaux aux slots
        signal_handler.download_finished.connect(lambda: show_playlist(self.playlist, self.playing_label))
        signal_handler.download_error.connect(lambda error: QMessageBox.critical(None, "Erreur de téléchargement", f"Erreur lors du téléchargement: {error}"))

        # Afficher la playlist au démarrage
        show_playlist(self.playlist, self.playing_label)

    def add_song(self):
        youtube_url = self.add_song_input.text()
        start_download(youtube_url, self.playlist, self.playing_label)
        self.add_song_input.clear()  # Effacer le champ après l'ajout

    def search_song(self):
        search_query = self.search_song_input.text()
        show_playlist(self.playlist, self.playing_label, search_query)

    def show_context_menu(self, position):
        menu = QMenu(self)
        delete_action = menu.addAction("Supprimer")
        delete_action.triggered.connect(lambda: delete_song(self.playlist))
        menu.exec_(self.playlist.mapToGlobal(position))

# Lancer l'application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MusicPlayerApp()
    window.show()
    sys.exit(app.exec_())
