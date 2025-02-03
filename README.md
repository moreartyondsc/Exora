# Exora Music

Exora Music est une application de gestion et de lecture de musique permettant aux utilisateurs de créer des comptes, de gérer leurs playlists et d’écouter des fichiers MP3 ou des vidéos YouTube.

## Objectif

L'objectif de ce projet est de fournir une application de bureau simple et conviviale pour la gestion et la lecture de musique. Les utilisateurs peuvent créer des comptes, ajouter des fichiers MP3 ou des liens YouTube à leurs playlists et écouter leurs chansons préférées.

## Fonctionnalités

- Création de compte utilisateur
- Connexion et déconnexion
- Ajout de fichiers MP3 à la playlist
- Ajout de liens YouTube à la playlist
- Lecture des chansons de la playlist
- Contrôles de lecture (lecture, pause, suivant, précédent)
- Options de lecture (aléatoire, répétition, boucle)

## Index du Projet

- [README.md](https://github.com/moreartyondsc/Exora/blob/main/README.md)
- [CHANGELOG.md](https://github.com/moreartyondsc/Exora/blob/main/CHANGELOG.md)
- [CODE_OF_CONDUCT.md](https://github.com/moreartyondsc/Exora/blob/main/CODE_OF_CONDUCT.md)
- [CONTRIBUTING.md](https://github.com/moreartyondsc/Exora/blob/main/CONTRIBUTING.md)
- [LICENSE.md](https://github.com/moreartyondsc/Exora/blob/main/LICENSE.md)
- [SECURITY.md](https://github.com/moreartyondsc/Exora/blob/main/SECURITY.md)

## Bibliothèques Nécessaires

Pour exécuter ce projet, vous aurez besoin des bibliothèques suivantes :

- `tkinter` : pour l'interface utilisateur graphique
- `mysql-connector-python` : pour la connexion à la base de données MySQL
- `bcrypt` : pour le hachage des mots de passe
- `pygame` : pour la gestion et la lecture des fichiers audio
- `yt-dlp` : pour le téléchargement et l'extraction des informations des vidéos YouTube

Vous pouvez installer ces bibliothèques avec `pip` :

```sh
pip install mysql-connector-python bcrypt pygame yt-dlp
```

## Processus d'Installation

1. **Cloner le dépôt** :
   ```sh
   git clone https://github.com/moreartyondsc/Exora.git
   cd Exora
   ```

2. **Installer les dépendances** :
   ```sh
   pip install -r requirements.txt
   ```

3. **Configurer la base de données** :
   - Créez une base de données MySQL et un utilisateur avec les privilèges nécessaires.
   - Configurez les informations de connexion dans le fichier `config.json` :
     ```json
     {
         "hostname": "votre_hostname",
         "database": "votre_database",
         "port": "votre_port",
         "username": "votre_username",
         "password": "votre_password"
     }
     ```

4. **Créer la table `users`** :
   
   ```sql
   CREATE TABLE users (
     id INT(11) NOT NULL AUTO_INCREMENT,
     username VARCHAR(250) NOT NULL,
     password VARCHAR(250) NOT NULL,
     playlist LONGTEXT NOT NULL,
     PRIMARY KEY (id)
   ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
   ```

5. **Exécuter l'application** :
   ```sh
   python index.py
   ```

## Utilisation

1. **Création de compte** :
   - Lancez l'application et cliquez sur "Créer un compte".
   - Saisissez un nom d'utilisateur et un mot de passe, puis cliquez sur "Créer".

2. **Connexion** :
   - Entrez votre nom d'utilisateur et votre mot de passe, puis cliquez sur "Connexion".

3. **Gestion de la playlist** :
   - Ajoutez des fichiers MP3 ou des liens YouTube à votre playlist via les boutons correspondants.
   - Cliquez sur une chanson dans la playlist pour la lire.

4. **Contrôles de lecture** :
   - Utilisez les boutons "Lecture", "Pause", "Suivant" et "Précédent" pour contrôler la lecture.
   - Activez les options de lecture (aléatoire, répétition, boucle) selon vos préférences.

## Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Forkez le dépôt.
2. Créez une nouvelle branche (`git checkout -b feature-branch-name`).
3. Effectuez vos modifications et committez-les (`git commit -am 'Ajout d'une fonctionnalité'`).
4. Poussez la branche (`git push origin feature-branch-name`).
5. Ouvrez une Pull Request.

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## Contact

Pour toute question ou suggestion, contactez [odevs.contact@gmail.com](mailto:odevs.contact@gmail.com).
