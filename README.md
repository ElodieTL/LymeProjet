## Développement d'un algorithme d'intégration et de fusion de données géospatiales relatives aux déterminants environnementaux de la maladie de Lyme et du Virus du Nil occidental

#### Comment cloner ce projet
1. Télécharger Git à l'adresse suivante https://git-scm.com/.
2. Créer un répertoire à l'endroit voulu sur le disque de l'ordinateur.
3. Cliquer-droit sur le répertoire et sélectionner *Git Bash Here*.
4. Taper `git clone https://github.com/ElodieTL/LymeProjet.git` dans la fenêtre de commande. Le projet sera entièrement copié dans un répertoire nommé *LymeProjet*.

#### Comment vérifier si des fichiers ont été mis à jour sur GitHub (et les télécharger)
1. Cliquer-droit sur le répertoire *LymeProjet* et sélectionner *Git Bash Here*.
2. Taper `git pull` afin de vérifier si des fichiers ont été ajoutés/supprimés/modifiés.

#### Comment déposer des fichiers sur GitHub
1. Cliquer-droit sur le répertoire *LymeProjet* et sélectionner *Git Bash Here*.
2. Taper `git add <fichier>` pour ajouter un fichier.
3. Taper `git commit -m '<message>'` pour confirmer l'ajout d'un ou plusieurs fichiers.
4. Taper `git push` pour déposer les fichiers sur GitHub. 

Note: La taille maximale d'un fichier téléversé est de 100 Mo.

#### Comment vérifier le statut du dossier *LymeProjet*
1. Cliquer-droit sur le répertoire *LymeProjet* et sélectionner *Git Bash Here*.
2. Taper `git status` afin de voir quel(s) fichier(s) a (ont) été ajouté(s) a l'aide de l'appel `git add`.

#### Comment installer un environnement
1. Déposer le fichier .yml dans le répertoire où se trouve le dossier Anaconda3.
2. Dans la console Anaconda, taper `conda env create -f <nom>.yml`
3. Pour activer l'environnement, taper `conda activate <env>`.

#### Comment revenir en arrière si un fichier est trop gros après un `git push`
1. Cliquer-droit sur le répertoire *LymeProjet* et sélectionner *Git Bash Here*.
2. Taper `git reset HEAD~#` où # est le nombre de commits à annuler (souvent 1).
