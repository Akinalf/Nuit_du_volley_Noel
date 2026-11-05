# Nuit du volley de Noël – site du tournoi

Site à page unique pour le tournoi de volley (rondes suisses, 12 équipes, 3 terrains) :
planning, matchs, classement et finales, mis à jour en direct sur les téléphones.

- `index.html` : le site du tournoi (lecture et saisie des scores ouvertes à tous ; code organisateur pour les droits étendus).
- `demo.html` : version de démonstration avec boutons de simulation. Rien n'est enregistré, tout reste dans le navigateur.
- `setup.sql` : structure de la base Supabase (lecture publique, écriture par fonction `save_state` avec droits joueurs / organisateurs, historique des versions).

Le code organisateur n'est stocké que dans la base Supabase (table `tournoi_secret`), jamais dans ce dépôt (`__PIN__` dans `setup.sql`). Chaque enregistrement conserve l'état précédent dans la table `tournoi_history` (300 dernières versions), ce qui permet de restaurer le tournoi en cas d'erreur.

## Plan B (sans internet)

`secours/tournoi_secours.py` fait tourner sur un ordinateur la même page que le site (arbitrage, verrouillage des rondes, droits joueurs / organisateurs).
Les téléphones s'y connectent par le wifi ou un partage de connexion, sans internet.

```
python tournoi_secours.py                          # le code organisateur est demandé au démarrage
python tournoi_secours.py --etat sauvegarde.json   # reprendre l'état du site (Réglages > Télécharger une sauvegarde)
```
