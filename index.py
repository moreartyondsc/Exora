import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import mysql.connector
from mysql.connector import Error
import bcrypt
import json
import os
import yt_dlp
import threading
import pygame

# Initialisation de pygame
pygame.mixer.init()

# Chargement des informations de connexion à la base de données
def load_config():
    with open('config.json', 'r') as file:
        return json.load(file)

config = load_config()
hostname = config['hostname']
username = config['username']
password = config['password']
database = config['database']
port = config['port']

def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=password,
            db=database,
            port=port
        )
        if connection.is_connected():
            print("Connexion OK", connection.get_server_info())
            return connection, connection.cursor()
    except Error as e:
        print("Erreur de connexion", e)
        return None, None

# Initialisation de la connexion à la base de données
db_connection, db_cursor = connect_to_database()

# Fonctions de hachage et vérification de mot de passe
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(hashed_password, password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

# Fonction pour vérifier les informations de connexion de l'utilisateur
def check_login():
    username = entry_username.get()
    password = entry_password.get()

    if db_connection and db_cursor:
        query = "SELECT password FROM users WHERE username = %s"
        db_cursor.execute(query, (username,))
        result = db_cursor.fetchone()

        if result and check_password(result[0].encode('utf-8'), password):
            messagebox.showinfo("Connexion", "Connexion réussie!")
            root.withdraw()  # Cacher la fenêtre de connexion
            main_window(username)  # Ouvrir la fenêtre principale de l'application
        else:
            messagebox.showerror("Connexion", "Nom d'utilisateur ou mot de passe incorrect")
    else:
        messagebox.showerror("Connexion", "Erreur de connexion à la base de données")

# Fonction pour créer un compte utilisateur
def create_account():
    root.withdraw()  # Cacher la fenêtre de connexion
    create_account_window = tk.Toplevel(root)
    create_account_window.title("Créer un compte")
    create_account_window.geometry("400x250")
    create_account_window.resizable(False, False)

    # Widgets de la fenêtre de création de compte
    tk.Label(create_account_window, text="Nom d'utilisateur:").pack(pady=5)
    entry_new_username = tk.Entry(create_account_window)
    entry_new_username.pack(pady=5)

    tk.Label(create_account_window, text="Mot de passe:").pack(pady=5)
    entry_new_password = tk.Entry(create_account_window, show="*")
    entry_new_password.pack(pady=5)

    tk.Button(create_account_window, text="Créer", command=lambda: create_user(entry_new_username.get(), entry_new_password.get(), create_account_window)).pack(pady=20)
    tk.Button(create_account_window, text="Retour à la connexion", command=lambda: show_login(create_account_window)).pack(pady=5)

# Fonction pour créer un nouvel utilisateur
def create_user(username, password, create_account_window):
    if not username or not password:
        messagebox.showerror("Création de compte", "Veuillez remplir tous les champs")
        return

    hashed_password = hash_password(password)
    playlist_default = "{}"  # Playlist par défaut vide

    if db_connection and db_cursor:
        query = "INSERT INTO users (username, password, playlist) VALUES (%s, %s, %s)"
        try:
            db_cursor.execute(query, (username, hashed_password, playlist_default))
            db_connection.commit()
            messagebox.showinfo("Création de compte", "Compte créé avec succès!")
            create_account_window.destroy()  # Fermer la fenêtre de création de compte
            root.deiconify()  # Réafficher la fenêtre de connexion
        except mysql.connector.Error as err:
            messagebox.showerror("Création de compte", f"Erreur: {err}")
    else:
        messagebox.showerror("Création de compte", "Erreur de connexion à la base de données")

# Fonction pour réafficher la fenêtre de connexion
def show_login(window):
    window.destroy()  # Fermer la fenêtre actuelle
    root.deiconify()  # Réafficher la fenêtre de connexion

# Fonction pour la fenêtre principale de l'application
def main_window(username):
    global current_playlist, current_index, play_thread, is_paused
    current_playlist = []
    current_index = 0
    play_thread = None
    is_paused = False

    main_window_page = tk.Toplevel(root)
    main_window_page.title("Exora Music")
    main_window_page.geometry("1000x600")
    main_window_page.resizable(True, True)
    main_window_page.minsize(800, 600)

    # Bandeau de titre + connexion
    title_frame = tk.Frame(main_window_page, bg="blue", height=50)
    title_frame.pack(fill=tk.X, side=tk.TOP)

    tk.Label(title_frame, text="Exora Music", font=("Arial", 24), bg="blue", fg="white").pack(side=tk.LEFT, padx=10)
    tk.Label(title_frame, text=f"Connecté en tant que: {username}", font=("Arial", 14), bg="blue", fg="white").pack(side=tk.LEFT, padx=10)
    tk.Button(title_frame, text="Déconnexion", command=lambda: show_login(main_window_page)).pack(side=tk.RIGHT, padx=10)

    # Cadre de la playlist
    playlist_frame = tk.Frame(main_window_page, bg="lightgrey", width=300)
    playlist_frame.pack(fill=tk.Y, side=tk.LEFT)

    tk.Label(playlist_frame, text="Playlist", font=("Arial", 16), bg="lightgrey").pack(pady=10)

    # Cadre pour ajouter un nouveau son
    add_song_frame = tk.Frame(main_window_page, bg="lightgrey", width=300)
    add_song_frame.pack(fill=tk.Y, side=tk.RIGHT)

    tk.Label(add_song_frame, text="Ajouter un son", font=("Arial", 16), bg="lightgrey").pack(pady=10)
    tk.Button(add_song_frame, text="Ajouter un fichier MP3", command=lambda: add_mp3_song(username, playlist_frame, main_window_page, label_current_song)).pack(pady=5)
    tk.Button(add_song_frame, text="Ajouter un lien YouTube", command=lambda: add_youtube_song(username, playlist_frame, main_window_page, label_current_song)).pack(pady=5)

    # Cadre pour le lecteur de musique
    player_frame = tk.Frame(main_window_page, bg="lightgrey", height=100)
    player_frame.pack(fill=tk.X, side=tk.BOTTOM)

    label_current_song = tk.Label(player_frame, text="Aucune musique en lecture", font=("Arial", 14), bg="lightgrey")
    label_current_song.pack(pady=10)

    tk.Button(player_frame, text="Play", command=lambda: play_song(username, label_current_song)).pack(side=tk.LEFT, padx=5)
    tk.Button(player_frame, text="Pause", command=pause_song).pack(side=tk.LEFT, padx=5)
    tk.Button(player_frame, text="Skip", command=skip_song).pack(side=tk.LEFT, padx=5)
    tk.Button(player_frame, text="Back", command=back_song).pack(side=tk.LEFT, padx=5)

    # Options de lecture
    options_frame = tk.Frame(player_frame, bg="lightgrey")
    options_frame.pack(side=tk.RIGHT, padx=10)

    var_shuffle = tk.BooleanVar()
    tk.Checkbutton(options_frame, text="Aléatoire", variable=var_shuffle, bg="lightgrey").pack(side=tk.LEFT, padx=5)

    var_repeat = tk.BooleanVar()
    tk.Checkbutton(options_frame, text="Répéter", variable=var_repeat, bg="lightgrey").pack(side=tk.LEFT, padx=5)

    var_loop = tk.BooleanVar()
    tk.Checkbutton(options_frame, text="Boucle", variable=var_loop, bg="lightgrey").pack(side=tk.LEFT, padx=5)

    show_playlist(main_window_page, playlist_frame, username, label_current_song)

def show_playlist(main_window_page, playlist_frame, username, label_current_song):
    global current_playlist
    exora_dir = get_exora_directory()
    if not os.path.exists(exora_dir):
        os.makedirs(exora_dir)
        with open(os.path.join(exora_dir, "README.txt"), "w") as readme_file:
            readme_file.write("Ce répertoire contient les fichiers audio téléchargés pour l'application Exora Music.")

    current_playlist = []
    for filename in os.listdir(exora_dir):
        if filename.endswith(".mp3"):
            song_name = os.path.splitext(filename)[0]
            current_playlist.append(os.path.join(exora_dir, filename))
            tk.Button(playlist_frame, text=song_name, font=("Arial", 12), bg="lightgrey", command=lambda url=os.path.join(exora_dir, filename): play_song(username, label_current_song, url)).pack(pady=2)

def get_exora_directory():
    home_dir = os.path.expanduser("~")
    return os.path.join(home_dir, "exora")

def add_mp3_song(username, playlist_frame, main_window_page, label_current_song):
    file_path = filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3")])
    if file_path:
        exora_dir = get_exora_directory()
        song_name = os.path.basename(file_path)
        destination_path = os.path.join(exora_dir, song_name)

        if os.path.exists(destination_path):
            messagebox.showinfo("Ajout de son", "Le fichier existe déjà dans la playlist.")
        else:
            os.rename(file_path, destination_path)
            messagebox.showinfo("Ajout de son", "Son ajouté avec succès!")
            show_playlist(main_window_page, playlist_frame, username, label_current_song)

def add_youtube_song(username, playlist_frame, main_window_page, label_current_song):
    youtube_url = simpledialog.askstring("Ajouter un lien YouTube", "Entrez le lien YouTube:")
    if youtube_url:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(get_exora_directory(), '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=True)
            song_name = info_dict.get('title', None)
            artist = info_dict.get('uploader', None)
            album = "Unknown"  # Vous pouvez ajouter une logique pour extraire l'album de la vidéo YouTube
            date_ajout = "Unknown"  # Vous pouvez ajouter la date actuelle
            url = youtube_url

            exora_dir = get_exora_directory()
            destination_path = os.path.join(exora_dir, f"{song_name}.mp3")

            if os.path.exists(destination_path):
                messagebox.showinfo("Ajout de son", "Le fichier existe déjà dans la playlist.")
            else:
                messagebox.showinfo("Ajout de son", "Son ajouté avec succès!")
                show_playlist(main_window_page, playlist_frame, username, label_current_song)

def play_song(username, label_current_song, url=None):
    global current_index, play_thread, is_paused

    def play_audio(url):
        global is_paused
        pygame.mixer.music.load(url)
        pygame.mixer.music.play()
        is_paused = False

    if url:
        current_index = current_playlist.index(url)
    else:
        if current_index < len(current_playlist):
            url = current_playlist[current_index]
        else:
            messagebox.showinfo("Lecture", "Aucune musique à lire.")
            return

    label_current_song.config(text=f"Lecture en cours: {os.path.basename(url)}")
    if play_thread and play_thread.is_alive():
        play_thread.join()
    play_thread = threading.Thread(target=play_audio, args=(url,))
    play_thread.start()

def pause_song():
    global is_paused
    if pygame.mixer.music.get_busy():
        if is_paused:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
        is_paused = not is_paused

def skip_song():
    global current_index
    if current_index < len(current_playlist) - 1:
        current_index += 1
        play_song(None, None)
    else:
        messagebox.showinfo("Lecture", "Aucune musique suivante.")

def back_song():
    global current_index
    if current_index > 0:
        current_index -= 1
        play_song(None, None)
    else:
        messagebox.showinfo("Lecture", "Aucune musique précédente.")

# Création de la fenêtre de connexion
root = tk.Tk()
root.title("Connexion")
root.geometry("400x250")
root.resizable(False, False)

# Widgets de la fenêtre de connexion
tk.Label(root, text="Nom d'utilisateur:").pack(pady=5)
entry_username = tk.Entry(root)
entry_username.pack(pady=5)

tk.Label(root, text="Mot de passe:").pack(pady=5)
entry_password = tk.Entry(root, show="*")
entry_password.pack(pady=5)

tk.Button(root, text="Connexion", command=check_login).pack(pady=20)
tk.Button(root, text="Créer un compte", command=create_account).pack(pady=5)

# Lancement de la boucle principale de l'application
root.mainloop()

# Fermeture de la connexion à la base de données lorsque l'application se ferme
if db_connection:
    db_connection.close()