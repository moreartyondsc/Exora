import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import mysql.connector
from mysql.connector import Error
import bcrypt
import json
from pydub import AudioSegment
from pydub.playback import play
import os
import yt_dlp
import json

# Informations de connexion à la base de données
with open('config.json', 'r') as file:
    config = json.load(file)

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
            db_Info = connection.get_server_info()
            print("Connexion OK", db_Info)
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            record = cursor.fetchone()
            print("Vous êtes connecté à la base de données:", record)
            return connection, cursor
    except Error as e:
        print("Erreur de connexion", e)
        return None, None

# Initialisation de la connexion à la base de données
db_connection, db_cursor = connect_to_database()

# Fonction pour hacher un mot de passe
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Fonction pour vérifier un mot de passe
def check_password(hashed_password, password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# Fonction pour vérifier les informations de connexion de l'utilisateur
def check_login():
    username = entry_username.get()
    password = entry_password.get()

    if db_connection and db_cursor:
        query = "SELECT password FROM users WHERE username = %s"
        db_cursor.execute(query, (username,))
        result = db_cursor.fetchone()

        if result:
            hashed_password = result[0]
            if check_password(hashed_password, password):
                messagebox.showinfo("Connexion", "Connexion réussie!")
                root.withdraw()  # Cacher la fenêtre de connexion
                main_window(username)  # Ouvrir la fenêtre principale de l'application
            else:
                messagebox.showerror("Connexion", "Nom d'utilisateur ou mot de passe incorrect")
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
    label_username = tk.Label(create_account_window, text="Nom d'utilisateur:")
    label_username.pack(pady=5)

    entry_new_username = tk.Entry(create_account_window)
    entry_new_username.pack(pady=5)

    label_password = tk.Label(create_account_window, text="Mot de passe:")
    label_password.pack(pady=5)

    entry_new_password = tk.Entry(create_account_window, show="*")
    entry_new_password.pack(pady=5)

    button_create = tk.Button(create_account_window, text="Créer", command=lambda: create_user(entry_new_username.get(), entry_new_password.get(), create_account_window))
    button_create.pack(pady=20)

    login_button = tk.Button(create_account_window, text="Retour à la connexion", command=lambda: show_login(create_account_window))
    login_button.pack(pady=5)

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
def show_login(create_account_window):
    create_account_window.destroy()  # Fermer la fenêtre de création de compte
    root.deiconify()  # Réafficher la fenêtre de connexion

# Fonction pour la fenêtre principale de l'application
def main_window(username):
    main_window_page = tk.Toplevel(root)
    main_window_page.title("Exora Music")
    main_window_page.geometry("1000x600")
    main_window_page.resizable(True, True)
    main_window_page.minsize(800, 600)

    # Bandeau de titre + connexion
    title_frame = tk.Frame(main_window_page, bg="blue", height=50)
    title_frame.pack(fill=tk.X, side=tk.TOP)

    label_title = tk.Label(title_frame, text="Exora Music", font=("Arial", 24), bg="blue", fg="white")
    label_title.pack(side=tk.LEFT, padx=10)

    label_username = tk.Label(title_frame, text=f"Connecté en tant que: {username}", font=("Arial", 14), bg="blue", fg="white")
    label_username.pack(side=tk.LEFT, padx=10)

    button_logout = tk.Button(title_frame, text="Déconnexion", command=lambda: show_login(main_window_page))
    button_logout.pack(side=tk.RIGHT, padx=10)

    # Cadre de la playlist
    playlist_frame = tk.Frame(main_window_page, bg="lightgrey", width=300)
    playlist_frame.pack(fill=tk.Y, side=tk.LEFT)

    label_playlist = tk.Label(playlist_frame, text="Playlist", font=("Arial", 16), bg="lightgrey")
    label_playlist.pack(pady=10)

    show_playlist(main_window_page, playlist_frame, username)

    # Cadre pour ajouter un nouveau son
    add_song_frame = tk.Frame(main_window_page, bg="lightgrey", width=300)
    add_song_frame.pack(fill=tk.Y, side=tk.RIGHT)

    label_add_song = tk.Label(add_song_frame, text="Ajouter un son", font=("Arial", 16), bg="lightgrey")
    label_add_song.pack(pady=10)

    button_add_mp3 = tk.Button(add_song_frame, text="Ajouter un fichier MP3", command=lambda: add_mp3_song(username))
    button_add_mp3.pack(pady=5)

    button_add_youtube = tk.Button(add_song_frame, text="Ajouter un lien YouTube", command=lambda: add_youtube_song(username))
    button_add_youtube.pack(pady=5)

    # Cadre pour le lecteur de musique
    player_frame = tk.Frame(main_window_page, bg="lightgrey", height=100)
    player_frame.pack(fill=tk.X, side=tk.BOTTOM)

    label_current_song = tk.Label(player_frame, text="Aucune musique en lecture", font=("Arial", 14), bg="lightgrey")
    label_current_song.pack(pady=10)

    button_play = tk.Button(player_frame, text="Play", command=play_song)
    button_play.pack(side=tk.LEFT, padx=5)

    button_pause = tk.Button(player_frame, text="Pause", command=pause_song)
    button_pause.pack(side=tk.LEFT, padx=5)

    button_skip = tk.Button(player_frame, text="Skip", command=skip_song)
    button_skip.pack(side=tk.LEFT, padx=5)

    button_back = tk.Button(player_frame, text="Back", command=back_song)
    button_back.pack(side=tk.LEFT, padx=5)

    # Options de lecture
    options_frame = tk.Frame(player_frame, bg="lightgrey")
    options_frame.pack(side=tk.RIGHT, padx=10)

    var_shuffle = tk.BooleanVar()
    check_shuffle = tk.Checkbutton(options_frame, text="Aléatoire", variable=var_shuffle, bg="lightgrey")
    check_shuffle.pack(side=tk.LEFT, padx=5)

    var_repeat = tk.BooleanVar()
    check_repeat = tk.Checkbutton(options_frame, text="Répéter", variable=var_repeat, bg="lightgrey")
    check_repeat.pack(side=tk.LEFT, padx=5)

    var_loop = tk.BooleanVar()
    check_loop = tk.Checkbutton(options_frame, text="Boucle", variable=var_loop, bg="lightgrey")
    check_loop.pack(side=tk.LEFT, padx=5)

def show_playlist(main_window_page, playlist_frame, username):
    if db_connection and db_cursor:
        query = "SELECT playlist FROM users WHERE username = %s"
        db_cursor.execute(query, (username,))
        result = db_cursor.fetchone()

        if result:
            playlist = json.loads(result[0])
            for playlist_name, songs in playlist.items():
                label_playlist_name = tk.Label(playlist_frame, text=playlist_name, font=("Arial", 14), bg="lightgrey")
                label_playlist_name.pack(pady=5)
                for song_name, song_details in songs.items():
                    label_song = tk.Label(playlist_frame, text=f"{song_name} - {song_details['artist']}", font=("Arial", 12), bg="lightgrey")
                    label_song.pack(pady=2)

def add_mp3_song(username):
    file_path = filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3")])
    if file_path:
        song_name = os.path.basename(file_path)
        artist = "Unknown"  # Vous pouvez ajouter une logique pour extraire l'artiste du fichier MP3
        album = "Unknown"  # Vous pouvez ajouter une logique pour extraire l'album du fichier MP3
        date_ajout = "Unknown"  # Vous pouvez ajouter la date actuelle
        url = file_path

        add_song_to_playlist(username, song_name, artist, album, date_ajout, url)

def add_youtube_song(username):
    youtube_url = simpledialog.askstring("Ajouter un lien YouTube", "Entrez le lien YouTube:")
    if youtube_url:
        ydl_opts = {'format': 'bestaudio'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=False)
            song_name = info_dict.get('title', None)
            artist = info_dict.get('uploader', None)
            album = "Unknown"  # Vous pouvez ajouter une logique pour extraire l'album de la vidéo YouTube
            date_ajout = "Unknown"  # Vous pouvez ajouter la date actuelle
            url = youtube_url

            add_song_to_playlist(username, song_name, artist, album, date_ajout, url)

def add_song_to_playlist(username, song_name, artist, album, date_ajout, url):
    if db_connection and db_cursor:
        query = "SELECT playlist FROM users WHERE username = %s"
        db_cursor.execute(query, (username,))
        result = db_cursor.fetchone()

        if result:
            playlist = json.loads(result[0])
            playlist_name = "Default Playlist"  # Vous pouvez ajouter une logique pour sélectionner une playlist spécifique
            if playlist_name not in playlist:
                playlist[playlist_name] = {}
            playlist[playlist_name][song_name] = {
                "artist": artist,
                "album": album,
                "date_ajout": date_ajout,
                "url": url
            }
            playlist_json = json.dumps(playlist)
            update_query = "UPDATE users SET playlist = %s WHERE username = %s"
            db_cursor.execute(update_query, (playlist_json, username))
            db_connection.commit()
            messagebox.showinfo("Ajout de son", "Son ajouté avec succès!")
        else:
            messagebox.showerror("Ajout de son", "Erreur lors de l'ajout du son")
    else:
        messagebox.showerror("Ajout de son", "Erreur de connexion à la base de données")

def play_song():
    # Logique pour lire la musique
    pass

def pause_song():
    # Logique pour mettre en pause la musique
    pass

def skip_song():
    # Logique pour passer à la musique suivante
    pass

def back_song():
    # Logique pour revenir à la musique précédente
    pass

# Création de la fenêtre de connexion
root = tk.Tk()
root.title("Connexion")
root.geometry("400x250")
root.resizable(False, False)

# Widgets de la fenêtre de connexion
label_username = tk.Label(root, text="Nom d'utilisateur:")
label_username.pack(pady=5)

entry_username = tk.Entry(root)
entry_username.pack(pady=5)

label_password = tk.Label(root, text="Mot de passe:")
label_password.pack(pady=5)

entry_password = tk.Entry(root, show="*")
entry_password.pack(pady=5)

button_login = tk.Button(root, text="Connexion", command=check_login)
button_login.pack(pady=20)

button_create_account = tk.Button(root, text="Créer un compte", command=create_account)
button_create_account.pack(pady=5)

# Lancement de la boucle principale de l'application
root.mainloop()

# Fermeture de la connexion à la base de données lorsque l'application se ferme
if db_connection:
    db_connection.close()
