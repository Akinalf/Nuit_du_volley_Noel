# Nuit du volley de Noël – site du tournoi

Site à page unique pour le tournoi de volley (rondes suisses, 12 équipes, 3 terrains) :
planning, matchs, classement et finales, mis à jour en direct sur les téléphones.

- `index.html` : le site du tournoi (lecture et saisie des scores ouvertes à tous ; code organisateur pour les droits étendus). C'est aussi la version hors ligne, voir plus bas.
- `setup.sql` : structure de la base Supabase (lecture publique, écriture par fonction `save_state` avec droits joueurs / organisateurs, historique des versions).

Le code organisateur n'est stocké que dans la base Supabase (table `tournoi_secret`), jamais dans ce dépôt (`__PIN__` dans `setup.sql`). Chaque enregistrement conserve l'état précédent dans la table `tournoi_history` (300 dernières versions), ce qui permet de restaurer le tournoi en cas d'erreur.

## Plan B (sans internet)

Il n'y a qu'un seul fichier : `index.html` contient les deux modes. Servi par le site, il lit et écrit dans la base. Enregistré sur un ordinateur et ouvert en double-clic, il passe en **mode hors ligne** : une seule personne saisit tous les résultats, et les données restent dans le navigateur de cet ordinateur (ouvrir toujours avec le même navigateur).

Un seul bouton, un seul fichier : Réglages > « Télécharger la version hors ligne » enregistre la page **avec le tournoi dedans** (`tournoi_hors_ligne_<date>_<heure>.html`).

Pendant le tournoi, garder le site ouvert en mode organisateur sur l'ordinateur de la table de marque et télécharger ce fichier après chaque ronde. Si le serveur ne répond plus, le bouton fonctionne quand même, avec le dernier état que la page a reçu.

Si la connexion tombe : ouvrir en double-clic le dernier fichier téléchargé. Le tournoi reprend là où il en était, sur cet ordinateur ou sur un autre. Si le navigateur contient déjà un autre tournoi, la page demande lequel garder.

En mode hors ligne, le même bouton s'appelle « Télécharger une sauvegarde » et produit le même genre de fichier.

Si la connexion revient : télécharger une sauvegarde depuis la version hors ligne, puis sur le site, en mode organisateur, Réglages > « Reprendre un fichier ».
