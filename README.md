
![Logo](https://raw.githubusercontent.com/AlexMaisNon/Mayro-Patry/refs/heads/mini-jeux-old/assets/sprites/main_menu/mayroparty.png)

# MAYRO PARTY

## Résumé
Ce projet est un jeu vidéo multi-joueur, composé d’un plateau et de 5 mini-jeux. Le jeu de plateau est un jeu solo avec des IA et les mini-jeux se jouent en multi-joueur. Les mini-jeux peuvent être en équipe ou en tournois.Le jeu de plateaux est composé de différents éléments qui permettent d’acquérir aux fils de tours différents objets ainsi que des étoiles et des pièces. L’objectif de notre projet est d’obtenir le plus de pièces et d’étoiles à la fin des quinze tours.

- Les touches sont rappelées mais il s'agit de "ZQSD et ESPACE".
- Les mini-jeux sont assez gourmands et peuvent faire freezer le jeu de temps en temps. C'est pour cela qu'il est recommandé de lancer plusieurs parties complètes afin de charger le jeu en mémoire, ce qui diminuera (normalement) les freezes.

Amusez-vous bien !


## Installation

- Installez Python
- Installez les bibliothèques requises avec la commande ci-dessous:

```bash
  pip install -r requirements.txt
```

Lancez le programme "main.py" (se trouvant dans sources) pour lancer le jeu.

## Instructions pour pouvoir lancer le serveur

- Créer un réseau local en branchant plusieurs ordinateurs entre eux avec des câbles réseaux.
- Lancer le programme "server.py" (se trouvant dans sources) sur l'une des machines qui jouera le rôle de serveur.
- Lorsque le programme le demande, entrer (dans la console, ou terminal) l'adresse IP de la machine exécutant le script cité plus haut (cette adresse IP est maintenant l'adresse du serveur).
- Lancer le jeu sur les autres machines et aller dans le menu "Multijoueur".
- Entrer l'adresse IP du serveur tournant le script "server.py" et entrer un pseudonyme de votre choix.
- Vous êtes maintenant connecté au serveur ! Attendez juste que les autres joueurs le rejoignent (il y a une limite de 4 joueurs, mais on peut toujours lancer une partie avec moins de 4 joueurs).

## Equipe qui travaille sur le projet

- [@Guerrier-du-salami](https://github.com/Guerrier-du-salami)
- [@AlexMaisNon](https://www.github.com/AlexMaisNon)
- Matisse
- Hinata


[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)
