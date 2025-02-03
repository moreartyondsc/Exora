# Exora Music

Exora Music est une application de gestion et de lecture de musique qui permet aux utilisateurs de créer des comptes, de gérer leurs playlists, et de lire des fichiers MP3 ou des vidéos YouTube.

## Objectif

L'objectif de ce projet est de fournir une application de bureau simple et conviviale pour la gestion et la lecture de musique. Les utilisateurs peuvent créer des comptes, ajouter des fichiers MP3 ou des liens YouTube à leurs playlists, et lire leurs chansons préférées.

## Fonctionnalités

- Création de compte utilisateur
- Connexion et déconnexion
- Ajout de fichiers MP3 à la playlist
- Ajout de liens YouTube à la playlist
- Lecture des chansons de la playlist
- Contrôles de lecture (play, pause, skip, back)
- Options de lecture (aléatoire, répéter, boucle)

## Bibliothèques Nécessaires

Pour exécuter ce projet, vous aurez besoin des bibliothèques suivantes :

- `tkinter` : Pour l'interface utilisateur graphique
- `mysql-connector-python` : Pour la connexion à la base de données MySQL
- `bcrypt` : Pour le hachage des mots de passe
- `pydub` : Pour la gestion et la lecture des fichiers audio
- `yt-dlp` : Pour le téléchargement et l'extraction des informations des vidéos YouTube

Vous pouvez installer ces bibliothèques en utilisant `pip` :

```sh
pip install mysql-connector-python bcrypt pydub yt-dlp
```

## Processus d'Installation

1. **Cloner le dépôt** :
   ```sh
   git clone https://github.com/moreartyondsc/exora.git
   cd exora-music
   ```

2. **Installer les dépendances** :
   ```sh
   pip install -r requirements.txt
   ```

3. **Configurer la base de données** :
   - Créez une base de données MySQL et un utilisateur avec les privilèges nécessaires.
   - Configurez les informations de connexion à la base de données dans le fichier `config.json` :
     ```json
     {
         "hostname": "votre_hostname",
         "database": "votre_database",
         "port": "votre_port",
         "username": "votre_username",
         "password": "votre_password"
     }
     ```

4. **Exécuter l'application** :
   ```sh
   python index.py
   ```

## Utilisation

1. **Création de compte** :
   - Lancez l'application et cliquez sur "Créer un compte".
   - Entrez un nom d'utilisateur et un mot de passe, puis cliquez sur "Créer".

2. **Connexion** :
   - Entrez votre nom d'utilisateur et votre mot de passe, puis cliquez sur "Connexion".

3. **Gestion de la playlist** :
   - Ajoutez des fichiers MP3 ou des liens YouTube à votre playlist en utilisant les boutons correspondants.
   - Cliquez sur une chanson dans la playlist pour la lire.

4. **Contrôles de lecture** :
   - Utilisez les boutons "Play", "Pause", "Skip", et "Back" pour contrôler la lecture des chansons.
   - Activez les options de lecture (aléatoire, répéter, boucle) selon vos préférences.

## Contribution

Les contributions sont les bienvenues ! Si vous souhaitez contribuer à ce projet, veuillez suivre ces étapes :

1. Forker le dépôt.
2. Créer une nouvelle branche (`git checkout -b feature-branch-name`).
3. Committer vos modifications (`git commit -am 'Add some feature'`).
4. Pusher la branche (`git push origin feature-branch-name`).
5. Créer une Pull Request.

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## Contact

Pour toute question ou suggestion, veuillez contacter [odevs.contact@gmail.com](mailto:odevs.contact@gmail.com).


Vous pouvez copier et coller ce contenu dans un fichier nommé `README.md` dans le répertoire racine de votre projet. Assurez-vous de remplacer `https://github.com/votre-utilisateur/exora-music.git` par l'URL de votre dépôt GitHub et `votre-email@example.com` par votre adresse e-mail de contact.
