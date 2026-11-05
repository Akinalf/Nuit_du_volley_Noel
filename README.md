# Nuit du volley de Noël – site du tournoi

Site à page unique pour le tournoi de volley (rondes suisses, 12 équipes, 3 terrains) :
planning, matchs, classement et finales, mis à jour en direct sur les téléphones.

- `index.html` : le site du tournoi (lecture et saisie des scores ouvertes à tous, sans code).
- `demo.html` : version de démonstration avec boutons de simulation. Rien n'est enregistré, tout reste dans le navigateur.
- `setup.sql` : structure de la base Supabase (lecture publique, écriture par fonction `save_state`, historique des versions).

Chaque enregistrement conserve l'état précédent dans la table `tournoi_history` (300 dernières versions), ce qui permet de restaurer le tournoi en cas d'erreur.
