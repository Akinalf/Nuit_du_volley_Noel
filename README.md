# Nuit du volley de Noël – site du tournoi

Site à page unique pour le tournoi de volley (rondes suisses, 12 équipes, 3 terrains) :
planning, matchs, classement et finales, mis à jour en direct sur les téléphones.

- `index.html` : le site du tournoi (lecture et saisie des scores ouvertes à tous ; code organisateur pour les droits étendus). C'est aussi la version hors ligne, voir plus bas.
- `setup.sql` : structure de la base Supabase (lecture publique, écriture par fonction `save_state` avec droits joueurs / organisateurs, historique des versions).

Le code organisateur n'est stocké que dans la base Supabase (table `tournoi_secret`), jamais dans ce dépôt (`__PIN__` dans `setup.sql`). Chaque enregistrement conserve l'état précédent dans la table `tournoi_history` (300 dernières versions), ce qui permet de restaurer le tournoi en cas d'erreur.

## Plan B (sans internet)

Il n'y a qu'un seul fichier : `index.html` contient les deux modes. Servi par le site, il lit et écrit dans la base. Enregistré sur un ordinateur et ouvert en double-clic, il passe en **mode hors ligne** : une seule personne saisit tous les résultats, et les données restent dans le navigateur de cet ordinateur (ouvrir toujours avec le même navigateur).

Avant le tournoi, sur l'ordinateur de la table de marque :

1. Ouvrir le site en mode organisateur.
2. Réglages > « Télécharger la version hors ligne ».

Pendant le tournoi, garder le site ouvert sur cet ordinateur et faire Réglages > « Télécharger une sauvegarde » après chaque ronde. Si le serveur ne répond plus, ce bouton enregistre le dernier état que la page a reçu.

Si la connexion tombe :

1. Ouvrir en double-clic le fichier `tournoi_hors_ligne.html` téléchargé.
2. Réglages > « Reprendre une sauvegarde », choisir le dernier fichier de sauvegarde.
3. Continuer le tournoi sur cet ordinateur.

Si la connexion revient : télécharger une sauvegarde depuis la version hors ligne, puis la reprendre sur le site (Réglages > « Reprendre une sauvegarde », mode organisateur).
