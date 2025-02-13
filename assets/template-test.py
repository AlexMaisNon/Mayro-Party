# Les imports ici
import pygame
import random


# Import ça aussi (faut que le fichier generic.py soit dans le même dossier que le fichier de ton mini-jeu)
import assets.generic as generic





# Classe du joueur
# (bon là j'avoue que ça va être un peu chaud, ça change pas beaucoup comparé à la dernière fois et c'est probablement encore plus complexe)
# (mais au moins c'est opti et on recopie pas 50 fois la même chose)
class Joueur(generic.GenericJoueur):

    # ------/ Constructeur \------

    def __init__(self, perso: str, comp_id: int) -> None:
        """
        Constructeur de la classe Joueur.

        Attributs à définir:
            - perso (str): Personnage choisit par le joueur.
            - comp_id (int): Comportement du joueur (0 = ia | 1 = Joueur 1 | 2 = Joueur 2).

        Attributs internes:
            (met ici tout les attributs que tu définiras)
        """

        # Tests du type des paramètres donnés
        assert type(perso) == str, "Erreur: Le 1er paramètre (perso) est censé être une chaîne de caractères."
        assert type(comp_id) == int, "Erreur: Le 2ème paramètre (comp_id) est censé être un entier."

        # On initialise tous les attributs du constructeur parent
        super().__init__(perso, comp_id)

        # En gros tu veras qu'il y a beaucoup moins de choses ici, mais c'est uniquement parce que tous les attributs
        # sont stockés dans une classe à part qui sert pour tous les mini-jeux (ceux que j'ai codé en tout cas)
        # (en gros tu "importes" la classe GenericJoueur et tout ce qu'elle contient pour le foutre dans cette classe Joueur,
        # comme ça pas besoin de réécrire 50 fois la même chose)

        # (t'as qu'à regarder la classe GenericJoueur du fichier generic pour voir tous les attributs disponibles (attention ça pique un peu les yeux))

        # Ici je te conseille juste de modifier la vitesse de déplacement
        self.speed = 300

        # Exemple de définition des sprites (pour chaque joueur, y compris ia)
        self.sprites = [generic.scale_image_by(pygame.image.load(self.sprites_directory + "walk_left" + str(i) + ".png"), 3) for i in range(8)]

        # En gros ici je te conseille de faire une liste de tous les sprites que tu vas utiliser (voire un dictionnaire de listes) que tu stockeras dans self.sprites
        # Les sprites sont trouvables dans le même dossier que tout les autres avec self.sprites_directory

        # Initialisation du sprite actuel (celui que tu afficheras)
        self.sprite = self.sprites[0]

        # Exemple d'une boîte de collision (t'en auras peut être même pas besoin pour ton mini-jeu)
        #self.collision = pygame.Rect(0, 0, round((self.sprite.get_rect().w + 2) / 2), 20)


    # Pas d'accesseurs obligatoires car ils sont déjàs définits dans le GenericJoueur
    # (tu peux toujours en rajouter toi-même stv)


    # Les méthodes (elles sont (un peu moins) vides pour que tu puisses les modifier/supprimer/etc. parce que c'est à toi de créer leur fonctionnement (connard))
    # N'hésite pas a en rajouter (Vu que tes persos se déplacent automatiquement vers les interrupteurs, tu peux par exemple créer une autre méthode
    # qui le fait se déplacer sur une coordonnée précise)

    # Si jamais tu veux modifier le fonctionnement d'une classe de GenericJoueur dans cette classe, tu le fais en créant des méthodes avec le même nom (comme en dessous)
    # Mais si pour une raison ou une autre tu veux réutiliser son fonctionnement dans ces méthodes, appelle la méthode avec super().methode(paramètres)
    # (jsp si tu voudras utiliser ça par contre)


    def calculate_collisions(self) -> None:
        # Ici pour gérer les collisions
        pass

    def apply_velocity(self) -> None:
        # Ici pour gérer le mouvement
        pass

    def animate(self, delta_time) -> None:
        # Ici pour animer le joueur
        # L'idée ici c'est que t'as un attribut self.frame que tu peut utiliser (en l'arrondissant à l'entier) en indice sur ta liste de sprites
        # pour selectionner la frame de l'animation

        # (delta_time est extrêmement important mais si jamais t'arrives pas à l'utiliser (ce que je comprend totalement) mets juste 0.01 à la place et prie pour que ça passe,
        # je repasserai derrière pour réparer les dégats dans le pire des cas) (mais si tu fais ça retire le des paramètres)

        # Tu peux appeler la méthode animate de la classe GenericJoueur qui changera la valeur de self.frame automatiquement
        super().animate(delta_time, 10)


    # Pour le draw, n'utilise pas celui de la classe GenericJoueur (ça sert juste pour redimensionner la fenêtre et ça c'est à moi de m'en charger)
    # Contente toi juste d'afficher le joueur
    def draw(self, screen: pygame.Surface) -> None: # type: ignore
        # Ici pour gérer l'affichage
        # Conseil: utilise screen.blit()
        pass



# Ici tu peux faire d'autres classes pour d'autres objets de ton mini-jeu
# (genre une classe interrupteur pour les interrupteurs que les joueurs vont utiliser, etc... (jai pas d'idées) )



# Classe du mini-jeu
# (là c'est un peu mieux, et t'as des méthodes déjà toutes préparées dans la classe GenericMinigame)
class MiniGame(generic.GenericMiniGame):

    # Constructeur (tout ce qui a déjà dedans est quasi obligatoire)

    def __init__(self, screen: pygame.Surface, clock, fps: int) -> None: # type: ignore
        """
        Constructeur de la classe MiniGame.

        Attributs à définir:
            - screen (pygame.Surface): L'écran de jeu de pygame.
            - clock: L'horloge de pygame (permet de placer une limite de fps au jeu).
            - fps (int): Le nombre de fps maximal du jeu.

        Attributs internes:
            (mets tout les attributs que tu définiras ici)
        """

        # Tests du type des paramètres donnés
        assert type(screen) == pygame.Surface, "Erreur: Le 1er paramètre (screen) n'est pas une surface pygame."

        # type(clock) indique que l'horloge est de type "Clock", classe qui n'existe pas naturellement (même pas présente dans les classes de pygame)
        # Voilà la solution que j'ai trouvé pour résoudre ce problème (loin d'être parfaite, mais quand même une vérification)
        assert type(clock).__name__ == "Clock", "Erreur: Le 2ème paramètre (clock) est censé être une horloge pygame."

        assert type(fps) == int, "Erreur: Le 3ème paramètre (fps) est censé être une chaîne de caractères."


        # On initialise tous les attributs du constructeur parent
        super().__init__(screen, clock, fps)

        # Emplacement des sprites du mini-jeu
        minigame_directory = "assets\\sprites\\minigames\\pushy_penguins\\"

        # Sprites utilisés dans la classe
        self.bg = pygame.image.load((minigame_directory + "water.png"))


    # Pas d'accesseurs pour les mêmes raisons que la classe au dessus


    # Méthodes

    def load(self, param_joueurs: dict) -> None:
        # Liste des noms des joueurs
        liste_joueurs = list(param_joueurs.keys())

        # Ordre aléatoire pour que chaque joueur puisse avoir une position aléatoire
        random.shuffle(liste_joueurs)

        # Création des joueurs dans la liste
        for nom_joueur in liste_joueurs:
            comp_id_joueur = param_joueurs[nom_joueur]
            self.joueurs.append(Joueur(nom_joueur, comp_id_joueur))

        # Positionnement des joueurs
        # (généralement tu fais des set_pos pour chaque joueur pour les placer sur l'écran)

        # Initialisation de la liste des objets
        # (avec self.objets, tu stockes tous les objets du mini-jeu (donc joueurs + interrupteurs par exemple))

        # Textes pour la description du jeu
        # Ici 1 chaine de caratères = 1 ligne dans l'affichage de l'écran de chargement
        description = ["ligne 1",
                       "ligne 2",
                       "ligne 3",
                       "ligne 4"]

        # Le parent s'occupe du reste de la méthode
        super().load("assets\\musics\\minigames\\nom_de_la_musique.mp3", "(nom du mini-jeu)", description)

    def during_game(self) -> None:
        # Initialisation des paramètres par défaut de la phase
        running = True

        # Boucle principale de cette phase du jeu
        while running:
            # Détection de la fermeture de fenêtre
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.quit = True

            # Mets ici tout ce qui se passe pendant que le jeu se déroule
            # (fait pas trop gaffe a ce qu'il y a au dessus ça sert juste à faire quitter le jeu et à changer la taille de la fenêtre)
            # (mais stv tu peux faire de la détection d'inputs avec en rajoutant des elifs après le elif de la fenêtre)

        # Laisse ça pour afficher le message finish
        # Lancement de l'affichage de fin (si le joueur n'a pas fermé la fenêtre)
        if not self.quit:
            self.end_game()



    def calculate_score(self) -> None:
        # Calcule le score réalisé par chaque joueur et détermine le classement dans self.classement

        # Le but c'est qu'à la fin t'as un dictionnaire dans ce style:
        # {"mayro": 2, "lugi": 3, "wayro": 1, "walugi": 4}
        # avec le nom des joueurs et la position dans le classement

        # Laisse ça à la fin de la méthode et magie magie ça va afficher le gagnant automatiquement
        super().calculate_score()





# Petit débug pour pouvoir lancer le jeu direct (je sais je sais pas besoin de me remercier)

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()
pygame.init()
pygame.display.set_caption("MAYRO PARTY: Debug Zone")

# Paramètres du jeu
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
fps = 120

minigame = MiniGame(screen, clock, fps)
minigame.load({"mayro": 1, "lugi": 0, "wayro": 0, "walugi": 0})


# ET PUIS SI T'ES PAS CONTENT TU TE DÉMERDES ET TU CRÉE TES PROPRES CLASSES C'EST PAS A MOI DE FAIRE TON TRAVAIL (connard)
