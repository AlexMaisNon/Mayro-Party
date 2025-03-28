#Projet : Mayro Party
#Auteurs : Hinata Bouaziz, Antoine Desrues, Alexandre Guillaume, Matisse Moreau

# ------/ Importations des bibliothèques \------

import pygame
import pygame.freetype
from math import floor
import time
from os import sep

from utils import Network, scale_image_by
import json

# ------/ Classes \------

# Classe du joueur
class Joueur:

    # ------/ Constructeur \------

    def __init__(self, perso: str, type_joueur: str) -> None:
        """
        Constructeur de la classe Joueur.

        Attributs à définir:
            - perso (str): Personnage choisit par le joueur.
            - type_joueur (str): Si le joueur est en solo ou en équipe (solo ou panneau) (exclusif à ce mini-jeu).

        Attributs internes:
            - pos (list): Position du joueur.
            - rotation (str): Rotation du joueur.
            - dead (bool): Définit si le joueur est mort ou non.

            - panneau (pygame.Surface): Sprite du panneau.
            - guns (list): Sprites du pistolet.
            - gun (pygame.Surface): Sprite actuel du pistolet.
            - sprites (dict): Sprites du joueurs.
            - sprite (pygame.Surface): Sprite actuel du joueur.
            - sprite_pos (list): Position du sprite (du pistolet si solo ou du joueur sinon).

            - shadow (pygame.Surface): Sprite de l'ombre du joueur.
            - shadow_pos (list): Position de l'ombre.

            - son_mort (pygame.mixer.Sound): Son de mort du joueur.

            - taille (list): Dimensions du sprite du joueur (fournis au serveur).
        """

        # Tests du type des paramètres donnés
        assert type(type_joueur) == str, "Erreur: Le 4ème paramètre (type_joueur) est censé être une chaîne de caractères."


        # Définition du joueur
        self.perso = perso
        self.type_joueur = type_joueur

        # Caractéristiques principales du joueur
        self.pos = [0.0, 0.0]
        self.rotation = "left"
        self.dead = False

        # Sprite du panneau
        self.panneau = scale_image_by(pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "archer_ival", "panneau_joueur.png"])), 2)

        # Sprites pour le fusil
        self.guns = [pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "archer_ival", "gun.png"])),
                     pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "archer_ival", "gun_shot.png"]))]
        self.gun = self.guns[0]

        # Emplacement des sprites du joueur
        self.sprites_directory = sep.join(["..", "data", "sprites", "characters", self.perso])

        # Définition des sprites automatiquement (pour les joueurs / ia)
        self.sprites = {
            "panneau": {
                "left": scale_image_by(pygame.image.load(sep.join([self.sprites_directory, "walk_left2.png"])), 2),
                "right": scale_image_by(pygame.image.load(sep.join([self.sprites_directory, "walk_right2.png"])), 2)
            },
            "solo": [scale_image_by(pygame.image.load(sep.join([self.sprites_directory, "archer" + str(i) + ".png"])), 8) for i in range(8)]}

        # Changement du sprite actuel en fonction du type du joueur
        if self.type_joueur == "panneau":
            self.sprite = self.sprites["panneau"]["left"]
        else:
            self.sprite = self.sprites["solo"][0]

        # Initialisation de la position du sprites
        self.sprite_pos = list(self.pos)

        # Paramètres de l'ombre pour le joueur solo uniquement
        if self.type_joueur == "solo":
            self.shadow = scale_image_by(pygame.image.load(sep.join([self.sprites_directory, "shadow.png"])), 8)
        else:
            self.shadow = None
        self.shadow_pos = list(self.pos)

        # Initialisation de la frame choisie
        self.frame = 0.0

        # Initialisation des sons
        self.son_mort = pygame.mixer.Sound(sep.join(["..", "data", "sounds", self.perso, "death.ogg"]))

        # Initialisation de la taille du joueur (uniquement fournie au serveur)
        self.taille = [self.sprite.get_rect().w, self.sprite.get_rect().h]


    # ------/ Getters \------

    def get_perso(self) -> str:
        return self.perso

    def get_type_joueur(self) -> str:
        return self.type_joueur

    def get_pos(self) -> list:
        return self.pos

    def get_rotation(self) -> str:
        return self.rotation

    def get_dead(self) -> bool:
        return self.dead

    def get_move_cooldown(self) -> float:
        return self.move_cooldown

    def get_sprite_pos(self) -> list:
        return self.sprite_pos

    def get_son_mort(self) -> pygame.mixer.Sound: # type: ignore
        return self.son_mort

    def get_taille(self) -> list:
        return self.taille


    # ------/ Setters \------

    def set_pos(self, new_pos: list) -> None:
        self.pos = new_pos

    def set_rotation(self, new_rotation: str) -> None:
        self.rotation = new_rotation

    def set_dead(self, new_dead: bool) -> None:
        self.dead = new_dead

    def set_move_cooldown(self, new_move_cooldown: float) -> None:
        self.move_cooldown = new_move_cooldown


    # ------/ Méthodes \------

    def appliquer_positions(self, position: list) -> None:
        """
        Cette méthode permet d'appliquer toutes les positions nécessaire pour le joueur.

        Paramètres:
            - position (list): Position fournie par le serveur.

        Pré-conditions:
            - position doit être une liste de nombres.
        """

        # Test du type de position
        assert type(position) == list, "Erreur: Le paramètre donné (position) n'est pas une liste."

        # Test du contenu de position
        for elem in position:
            assert type(elem) == int or type(elem) == float, "Erreur: La liste donnée doit uniquement contenir des nombres."

        # On applique la nouvelle position au personnage
        self.pos = position

        # Applications différentes selon le type du joueur
        if self.type_joueur == "panneau":
            # On positionne le sprite du joueur sur le panneau
            self.sprite_pos[0] = round(self.pos[0] - (self.sprite.get_rect().w - self.panneau.get_rect().w) / 2)
            self.sprite_pos[1] = round(self.pos[1] - self.sprite.get_rect().bottom + self.panneau.get_rect().h / 2) + 35

        else:
            # On positionne ici le sprite du pistolet par rapport au joueur
            self.sprite_pos[0] = round(self.pos[0] + self.sprite.get_rect().w - self.gun.get_rect().w)
            self.sprite_pos[1] = round(self.pos[1] + 74)

            # On positionne l'ombre par rapport au personnage
            self.shadow_pos[0] = round(self.pos[0] + (self.sprite.get_rect().w - self.shadow.get_rect().w) / 2)
            self.shadow_pos[1] = round(self.pos[1] + self.sprite.get_rect().h - self.shadow.get_rect().h) + 10


    def animer(self, frame: "int | float", etat_tir: str) -> None:
        """
        Cette méthode permet d'animer le sprite du joueur.

        Paramètres:
            - frame (int ou float): Indique la frame actuelle du serveur. Utilisée pour la vitesse
            des sprites de l'animation.
            - etat_tir (str): Etat du pistolet.
        Pré-conditions:
            - etat_tir doit avoir soit "recharge", soit "tir" comme valeurs possibles.
        """

        # Test du type de frame
        assert type(frame) == int or type(frame) == float, "Erreur: Le 1er paramètre (frame) doit être un nombre."
        assert type(etat_tir) == str, "Erreur: Le 2ème paramètre (etat_tir) doit être une chaîne de caractères."

        # Test de la valeur de etat_tir
        assert etat_tir == "recharge" or etat_tir == "tir", "Erreur: La valeur de etat_tir n'est pas correcte."

        # N'a pas d'animation s'il ne dessine pas
        if self.type_joueur == "solo":
            # Changement du sprite actuel
            self.sprite = self.sprites["solo"][floor(frame % len(self.sprites["solo"]))]
        elif self.rotation != "immobile":
            # Changement du sprite actuel
            self.sprite = self.sprites["panneau"][self.rotation]

        if etat_tir == "recharge":
            self.gun = self.guns[0]
        else:
            self.gun = self.guns[1]


    def afficher(self, screen: pygame.Surface) -> None: # type: ignore
        """
        Cette méthode permet de dessiner le joueur sur l'écran.

        Paramètres:
            - screen (pygame.Surface): L'écran de jeu de pygame.
        """

        # Tests des types de variables
        assert type(screen) == pygame.Surface, "Erreur: Le paramètre donné (screen) n'est pas une surface pygame."

        # Initialisation des facteurs pour la taille de l'écran
        screen_factor = ((screen.get_rect().size[0] / 1280), (screen.get_rect().size[1] / 720))

        # Affiche le joueur uniquement s'il est vivant
        if not self.dead:
            # L'affichage change en fonction du type du joueur
            if self.type_joueur == "solo":
                # Affichage des sprites à leur positions respectives
                screen.blit(scale_image_by(self.shadow, screen_factor), (round(self.shadow_pos[0] * screen_factor[0]), round(self.shadow_pos[1] * screen_factor[1])))
                screen.blit(scale_image_by(self.gun, screen_factor), (round(self.sprite_pos[0] * screen_factor[0]), round(self.sprite_pos[1] * screen_factor[1])))
                screen.blit(scale_image_by(self.sprite, screen_factor), (round(self.pos[0] * screen_factor[0]), round(self.pos[1] * screen_factor[1])))
            else:
                # Affichage des sprites à leur positions respectives
                screen.blit(scale_image_by(self.panneau, screen_factor), (round(self.pos[0] * screen_factor[0]), round(self.pos[1] * screen_factor[1])))
                screen.blit(scale_image_by(self.sprite, screen_factor), (round(self.sprite_pos[0] * screen_factor[0]), round(self.sprite_pos[1] * screen_factor[1])))



# Classe de l'ennemi
class Ennemi:

    # ------/ Constructeur \------

    def __init__(self, perso: str) -> None:
        """
        Constructeur de la classe Ennemi.

        Attributs à définir:
            - perso (str): Personnage qui représente l'ennemi.

        Attributs internes:
            - pos (list): Position de l'ennemi.
            - dead (bool): Définit si l'ennemi est mort ou non.

            - sprites (dict): Sprites de l'ennemi.
            - sprite (pygame.Surface): Sprite actuel de l'ennemi.

            - son_mort (pygame.mixer.Sound): Son de mort de l'ennemi.
        """

        # Tests du type des paramètres donnés
        assert type(perso) == str, "Erreur: Le paramètre (perso) est censé être une chaîne de caractères."


        # Définition de l'ennemi
        self.perso = perso

        # Caractéristiques principales (stats)
        self.pos = [0.0, 0.0]
        self.rotation = "immobile"
        self.dead = False

        # Emplacement des sprites du mini-jeu
        self.sprites_directory = sep.join(["..", "data", "sprites", "minigames", "archer_ival"])

        # Définition des sprites de l'ennemi
        self.sprites = {
            "left": scale_image_by(pygame.image.load(sep.join([self.sprites_directory, "panneau_" + self.perso + "_left.png"])), 2),
            "right": scale_image_by(pygame.image.load(sep.join([self.sprites_directory, "panneau_" + self.perso + "_right.png"])), 2)
        }

        # Initialisation du sprite actuel
        self.sprite = self.sprites["left"]

        # Initialisation du son de mort
        self.son_mort = pygame.mixer.Sound(sep.join(["..", "data", "sounds", "minigames", "archer_ival", self.perso + "_death.ogg"]))


    # ------/ Getters \------

    def get_dead(self) -> bool:
        return self.dead

    def get_son_mort(self) -> pygame.mixer.Sound: # type: ignore
        return self.son_mort


    # ------/ Setters \------

    def set_pos(self, new_pos: list) -> None:
        self.pos = new_pos

    def set_rotation(self, new_rotation: str) -> None:
        self.rotation = new_rotation

    def set_dead(self, new_dead: bool) -> None:
        self.dead = new_dead


    # ------/ Méthodes \------

    def appliquer_positions(self, position: list) -> None:
        """
        Cette méthode permet d'appliquer toutes les positions nécessaire pour le joueur.

        Paramètres:
            - position (list): Position fournie par le serveur.

        Pré-conditions:
            - position doit être une liste de nombres.
        """

        # Test du type de position
        assert type(position) == list, "Erreur: Le paramètre donné (position) n'est pas une liste."

        # Test du contenu de position
        for elem in position:
            assert type(elem) == int or type(elem) == float, "Erreur: La liste donnée doit uniquement contenir des nombres."

        # On applique la nouvelle position au personnage
        self.pos = position


    def animer(self) -> None:
        """
        Cette méthode permet d'animer le sprite de l'ennemi.
        """

        # Ne change pas le sprite s'il reste immobile
        if self.rotation != "immobile":
            self.sprite = self.sprites[self.rotation]


    def afficher(self, screen: pygame.Surface) -> None: # type: ignore
        """
        Cette méthode permet de dessiner la flèche sur l'écran.

        Paramètres:
            - screen (pygame.Surface): L'écran de jeu de pygame.
        """

        # Tests des types de variables
        assert type(screen) == pygame.Surface, "Erreur: Le paramètre donné (screen) n'est pas une surface pygame."

        # Initialisation des facteurs pour la taille de l'écran
        screen_factor = ((screen.get_rect().size[0] / 1280), (screen.get_rect().size[1] / 720))

        # Affiche l'ennemi uniquement s'il est vivant
        if not self.dead:
            screen.blit(scale_image_by(self.sprite, screen_factor), (round(self.pos[0] * screen_factor[0]), round(self.pos[1] * screen_factor[1])))



# Classe de la flèche (ou de la balle plutôt, la classe s'appelle Fleche car c'était censé être une flèche et un arc à la base)
class Fleche:

    # ------/ Constructeur \------

    def __init__(self, pos: list, id_fleche: int) -> None:
        """
        Constructeur de la classe Fleche.

        Attributs à définir:
            - pos (list): Position de la flèche.
            - id_fleche (int): Identifiant qui permet de retrouver plus facilement les flèches
            créées par le serveur.

        Attributs internes:
            - velocity (list): Vélocité/Accélération de la flèche.
            - speed (int): Vitesse de la flèche.

            - sprite (pygame.Surface): Sprite actuel de la flèche.

            - collision (pygame.Rect ou None): Boîte de collision de la flèche.
        """

        # Tests du type des paramètres donnés
        assert type(pos) == list, "Erreur: Le 1er paramètre (pos) est censé être une liste."
        assert type(id_fleche) == int, "Erreur: Le 2ème paramètre (id_fleche) est censé être un nombre entier."


        # Caractéristiques de la flèche
        self.pos = pos
        self.id_fleche = id_fleche

        # Initialisation du sprite de la flèche
        self.sprite = scale_image_by(pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "archer_ival", "fleche.png"])), 2)


    # ------/ Getters \------

    def get_pos(self) -> list:
        return self.pos

    def get_id_fleche(self) -> int:
        return self.id_fleche


    # ------/ Méthodes \------

    def appliquer_positions(self, position) -> None:
        """
        Cette méthode permet de mettre à jour la position de la flèche.

        Paramètres:
            - position (list): Position fournie par le serveur.

        Pré-conditions:
            - position doit être une liste de nombres.
        """

        # Test du type de position
        assert type(position) == list, "Erreur: Le paramètre donné (position) n'est pas une liste."

        # Test du contenu de position
        for elem in position:
            assert type(elem) == int or type(elem) == float, "Erreur: La liste donnée doit uniquement contenir des nombres."

        # On applique la nouvelle position à la flèche
        self.pos = position


    def afficher(self, screen: pygame.Surface) -> None: # type: ignore
        """
        Cette méthode permet de dessiner la flèche sur l'écran.

        Paramètres:
            - screen (pygame.Surface): L'écran de jeu de pygame.
        """

        # Tests des types de variables
        assert type(screen) == pygame.Surface, "Erreur: Le paramètre donné (screen) n'est pas une surface pygame."

        # Initialisation des facteurs pour la taille de l'écran
        screen_factor = ((screen.get_rect().size[0] / 1280), (screen.get_rect().size[1] / 720))

        # Affichage de la flèche
        screen.blit(scale_image_by(self.sprite, screen_factor), (round(self.pos[0] * screen_factor[0]), round(self.pos[1] * screen_factor[1])))



# Classe du mini-jeu
class MiniGame:

    # ------/ Constructeur \------

    def __init__(self, screen: pygame.Surface, clock, fps: int) -> None: # type: ignore
        """
        Constructeur de la classe MiniGame.

        Attributs à définir:
            - screen (pygame.Surface): L'écran de jeu de pygame.
            - clock: L'horloge de pygame (permet de placer une limite de fps au jeu).
            - fps (int): Le nombre de fps maximal du jeu.

        Attributs internes:
            - quit (bool): Variable qui permet de détecter si le joueur a manuellement fermé le jeu.
            - screen_factor: Les multiplicateurs pour la taille de l'écran.

            - show_fps (bool): Paramètre de débug permettant d'afficher les fps.
            - show_server_fps (bool): Paramètre de débug permettant d'afficher les fps du serveur.

            - fps_font (pygame.freetype.Font): Police d'écriture pour les fps.
            - game_font (pygame.freetype.Font): Police d'écriture principale du mini-jeu.

            - joueurs (list): Liste des joueurs.
            - objets (list): Liste des objets.

            - timer_background (pygame.Surface): Image de fond du timer.

            - toad (list): Images du Toad de l'écran de chargement.
            - toad_shadow (pygame.Surface): Image de l'ombre de Toad.
            - toad_bubble (pygame.Surface): Image de la bulle de dialogue de Toad. 

            - entities (list): Liste des entités.

            - bg (pygame.Surface): Image de fond pour le mini-jeu.
            - nappe (pygame.Surface): Image de nappe jaune pour le mini-jeu.
            - mur_briques (pygame.Surface): Image d'un mur de briques pour le mini-jeu.
            - buisson (pygame.Surface): Image d'un buisson pour le mini-jeu.

            - son_tir (pygame.mixer.Sound): Son du tir.
        """

        # Tests du type des paramètres donnés
        assert type(screen) == pygame.Surface, "Erreur: Le 1er paramètre (screen) n'est pas une surface pygame."

        # type(clock) indique que l'horloge est de type "Clock", classe qui n'existe pas naturellement (même pas présente dans les classes de pygame)
        # Voilà la solution que j'ai trouvé pour résoudre ce problème (loin d'être parfaite, mais quand même une vérification)
        assert type(clock).__name__ == "Clock", "Erreur: Le 2ème paramètre (clock) est censé être une horloge pygame."

        assert type(fps) == int, "Erreur: Le 3ème paramètre (fps) est censé être une chaîne de caractères."


        # Initialisation des paramètres du jeu
        self.screen = screen
        self.clock = clock
        self.fps = fps

        self.quit = False
        self.screen_factor = (0, 0)

        # Paramètres de débug
        self.show_fps = True
        self.show_server_fps = True

        # Polices d'écritures
        self.fps_font = pygame.freetype.Font(sep.join(["..", "data", "fonts", "ComicSansMS3.ttf"]), 20)
        self.game_font = pygame.freetype.Font(sep.join(["..", "data", "fonts", "mario-party.ttf"]), 50)

        # Initialisation des paramètres pour la partie gameplay
        self.joueurs = {}
        self.entities = []
        self.objets = []
        self.classement = {}

        # Image de fond du timer
        self.timer = 30
        self.timer_background = pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "general", "timer_back.png"]))

        # Sprites de toad (pour le chargement)
        self.toad = [pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "general", "toad", "toad.png"])),
                     pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "general", "toad", "toad_open.png"]))]
        self.toad_shadow = pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "general", "toad", "shadow.png"]))
        self.toad_bubble = pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "general", "toad", "bubble.png"]))

        # Emplacement des sprites du mini-jeu
        minigame_directory = sep.join(["..", "data", "sprites", "minigames", "archer_ival"])

        # Sprites utilisés dans la classe
        self.bg = pygame.image.load(sep.join([minigame_directory, "background.png"]))
        self.nappe = pygame.image.load(sep.join([minigame_directory, "nappe_jaune.png"]))
        self.mur_briques = pygame.image.load(sep.join([minigame_directory, "mur_de_briques.png"]))
        self.buisson = pygame.image.load(sep.join([minigame_directory, "buisson.png"]))

        # Son du tir
        self.son_tir = pygame.mixer.Sound(sep.join(["..", "data", "sounds", "minigames", "archer_ival", "shot.ogg"]))

        # Initialisation du réseau
        self.net = None


    # ------/ Getters \------

    def get_quit(self) -> bool:
        return self.quit


    # ------/ Setters \------

    def set_net(self, new_net) -> Network:
        self.net = new_net


    # ------/ Méthodes \------

    def game_engine(self, input_joueur: list) -> None:
        """
        Cette méthode gère à la fois l'affichage (des éléments principaux) et la physique présente dans le mini-jeu.

        Paramètres:
            - input_joueur (list): Représente les inputs du joueur sous forme d'un vecteur.

        Pré-conditions:
            - input_joueur doit uniquement des entiers compris entre -1 et 1.
        """

        # Test du type de input_joueur
        assert type(input_joueur) == list, "Erreur: Le paramètre donné (input_joueur) doit être une liste."

        # Test du contenu de input_joueur
        for elem in input_joueur:
            assert type(elem) == int, "Erreur: La liste donnée doit uniquement contenir des entiers."
            assert elem >= -1 and elem <= 1, "Erreur: La liste donnée doit uniquement contenir des entiers compris entre -1 et 1"

        # Envoie les inputs au serveur et demande des infos sur l'environnement
        infos_environnement = json.loads(self.net.send(str(input_joueur[0]) + "|" + str(input_joueur[1]) + "|" + str(input_joueur[2])))
        infos_joueurs = infos_environnement["joueurs"]
        infos_ennemis = infos_environnement["ennemis"]
        infos_fleches = infos_environnement["fleches"]
        timer = infos_environnement["timer"]
        fps = infos_environnement["fps"]

        # On affiche les sprites du jeu dans un ordre d'affichage prédéfini
        self.screen.blit(scale_image_by(self.bg, self.screen_factor), (0, 0))

        # Affichage de buissons de tailles variables
        self.screen.blit(scale_image_by(self.buisson, (4 * self.screen_factor[0], 4 * self.screen_factor[1])), (round(370 * self.screen_factor[0]), round(380 * self.screen_factor[1])))
        self.screen.blit(scale_image_by(self.buisson, (5 * self.screen_factor[0], 5 * self.screen_factor[1])), (round(900 * self.screen_factor[0]), round(370 * self.screen_factor[1])))
        self.screen.blit(scale_image_by(self.buisson, (6 * self.screen_factor[0], 6 * self.screen_factor[1])), (round(80 * self.screen_factor[0]), round(360 * self.screen_factor[1])))

        self.screen.blit(scale_image_by(self.nappe, (5 * self.screen_factor[0], 5 * self.screen_factor[1])), (round(159 * self.screen_factor[0]), round(460 * self.screen_factor[1])))
        self.screen.blit(scale_image_by(self.mur_briques, (3 * self.screen_factor[0], 3 * self.screen_factor[1])), (round(275 * self.screen_factor[0]), round(340 * self.screen_factor[1])))

        # On met à jour la position des joueurs et des animations pour le client
        for id_joueur in self.joueurs.keys():
            self.joueurs[id_joueur].appliquer_positions(infos_joueurs[id_joueur]["pos"])
            self.joueurs[id_joueur].set_rotation(infos_joueurs[id_joueur]["rotation"])

            # On détecte si le joueur est mort
            ancien_dead = self.joueurs[id_joueur].get_dead()
            self.joueurs[id_joueur].set_dead(infos_joueurs[id_joueur]["dead"])

            # Si l'état de mort n'est pas le même qu'avant, il a été changé, donc il est mort
            if ancien_dead != self.joueurs[id_joueur].get_dead():
                self.joueurs[id_joueur].get_son_mort().play()

            self.joueurs[id_joueur].animer(infos_joueurs[id_joueur]["frame"], infos_joueurs[id_joueur]["etat_tir"])

        # Initialisation d'une liste de flèches pour simplifier la suite
        fleches = {str(objet.get_id_fleche()): objet for objet in self.objets if type(objet) == Fleche}

        # On détecte si des flèches ont despawn côté serveur
        for id_fleche in fleches.keys():
            if not id_fleche in infos_fleches.keys():
                if fleches[id_fleche] in self.objets:
                    self.objets.remove(fleches[id_fleche])

        # On détecte si des flèches ont été crée côté serveur
        for id_fleche in infos_fleches.keys():
            if not id_fleche in fleches:
                self.objets.append(Fleche(infos_fleches[id_fleche], int(id_fleche)))


        # Calcul de la physique de chaque objet
        for objet in self.objets:
            # On met à jour la position des objets et des animations pour le client
            if type(objet) == Ennemi:
                # Calcul de la vélocité et des collsisions de chaque objet
                objet.appliquer_positions(infos_ennemis[self.entities.index(objet)]["pos"])
                objet.set_rotation(infos_ennemis[self.entities.index(objet)]["rotation"])

                # On détecte si l'ennemi est mort
                ancien_dead = objet.get_dead()
                objet.set_dead(infos_ennemis[self.entities.index(objet)]["dead"])

                # Si l'état de mort n'est pas le même qu'avant, il a été changé, donc il est mort
                if ancien_dead != objet.get_dead():
                    objet.get_son_mort().play()

                objet.animer()
            elif type(objet) == Fleche:
                objet.appliquer_positions(infos_fleches[str(objet.get_id_fleche())])

            # On affiche tous les objets sauf le joueur solo (le 1er joueur du dictionnaire self.joueurs)
            if type(objet) != Joueur or objet.get_type_joueur() == "panneau":
                objet.afficher(self.screen)

        # On active les sons si le serveur l'a indiqué
        if infos_joueurs[self.net.adresse_client]["lancer_son_tir"]:
            self.son_tir.play()
            self.net.send("desactive_son_tir")

        # On affiche le joueur solo à la fin pour la priorité d'affichage
        for joueur in self.joueurs.values():
            if joueur.get_type_joueur() == "solo":
                joueur.afficher(self.screen)

        # Affichage du timer seulement s'il est actuellement en train de compter
        if timer >= 0:
            # Affichage du fond du timer
            timer_sprite = scale_image_by(self.timer_background, self.screen_factor)
            timer_background_textRect = timer_sprite.get_rect()
            timer_background_textRect.center = (self.screen.get_rect().w // 2, round(37 * self.screen_factor[1]))
            self.screen.blit(timer_sprite, timer_background_textRect)

            # Positionnement du timer au centre-haut de l'écran
            timer_text = self.game_font.render(str(timer), (255, 255, 255))
            timer_text_scaled = scale_image_by(timer_text[0], self.screen_factor)
            timer_textRect = timer_text_scaled.get_rect()
            timer_textRect.center = (self.screen.get_rect().w // 2, round(37 * self.screen_factor[1]))

            # Affichage du timer
            self.screen.blit(timer_text_scaled, timer_textRect)

        # Initialisation des facteurs pour la taille de l'écran
        self.screen_factor = ((self.screen.get_rect().size[0] / 1280), (self.screen.get_rect().size[1] / 720))

        # Debug pour afficher les fps
        if self.show_fps:
            self.fps_font.render_to(self.screen, (0, 0), "FPS: " + str(round(self.clock.get_fps())), (0, 0, 0))

        # Debug pour afficher les fps du serveur
        if self.show_server_fps:
            self.fps_font.render_to(self.screen, (0, 20), "S-FPS: " + str(round(fps)), (0, 0, 0))


    def load(self) -> None:
        """
        Cette méthode représente la phase de chargement du mini-jeu.
        """

        # Textes pour la description du jeu
        description = ["Joueur solo:",
                       "Tirez sur les joueurs adverses",
                       "avec ESPACE !",
                       "",
                       "Joueurs en équipe:",
                       "Esquivez les tirs et survivez le",
                       "plus longtemps possible !"]

        nom = "Archer-Ival"
        chemin_musique = sep.join(["..", "data", "musics", "minigames", "archer_ival.ogg"])

        # État de la phase (True veut dire qu'elle est en cours)
        running = True

        # On charge la musique en avance (réduction légère du lag)
        pygame.mixer.music.load(chemin_musique)

        # Initialisation du timer
        cooldown = 3 + time.time()

        # Boucle principale de cette phase du jeu
        while running and not self.quit:

            # Détection de la fermeture de fenêtre
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit = True

                # Changement de taille de la fenêtre
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)

                # Détection des inputs du joueur
                elif event.type == pygame.MOUSEBUTTONUP and cooldown - time.time() < 0:
                    self.net.send("ready_for_next_state")

            # Envoi d'une requête au serveur pour obtenir le nombre de joueurs et lance la partie si tous les joueurs sont prêts
            infos_serveur = json.loads(self.net.send("infos_serveur"))
            nb_joueurs = infos_serveur["nb_joueurs"]
            nb_joueurs_prets = infos_serveur["nb_joueurs_prets"]

            etat = self.net.send("get_etat")
            running = etat == "minigame_load" or etat == "minigame_select"

            # Initialisation des facteurs pour la taille de l'écran
            self.screen_factor = ((self.screen.get_rect().size[0] / 1280), (self.screen.get_rect().size[1] / 720))

            # Affichage de l'écran de chargement et du texte
            self.screen.fill((0, 0, 0))

            # Redimension des textes
            nom_text = scale_image_by(self.game_font.render(nom, (255, 255, 255))[0], self.screen_factor)
            nom_textRect = nom_text.get_rect()
            nom_textRect.center = (round(640 * self.screen_factor[0]), round(70 * self.screen_factor[1]))
            if cooldown - time.time() > 0:
                chargement = "CHARGEMENT..." 
            elif nb_joueurs > 1:
                chargement = "Cliquez si vous êtes prêt pour le mini-jeu ! (" + str(nb_joueurs_prets) + "/" + str(nb_joueurs) + ")"
            else:
                chargement = "Cliquez pour lancer le mini-jeu !"
            chargement_text = scale_image_by(self.game_font.render(chargement, (255, 255, 255))[0], (0.8 * self.screen_factor[0], 0.8 * self.screen_factor[1]))
            chargement_textRect = chargement_text.get_rect()
            chargement_textRect.center = (round(640 * self.screen_factor[0]), round(680 * self.screen_factor[1]))

            # Création du texte "controles" qui s'affiche au-dessus des touches du jouers
            controles_text = scale_image_by(self.game_font.render("Contrôles:", (255, 255, 255))[0], self.screen_factor)

            # Affichage des textes
            self.screen.blit(nom_text, nom_textRect)
            self.screen.blit(chargement_text, chargement_textRect)
            self.screen.blit(controles_text, (round(960 * self.screen_factor[0]), round(200 * self.screen_factor[1])))

            # Affichage de Toad (pour présenter le mini-jeu)
            self.screen.blit(scale_image_by(self.toad_shadow, (6 * self.screen_factor[0], 6 * self.screen_factor[1])), (round(114 * self.screen_factor[0]), round(535 * self.screen_factor[1])))
            self.screen.blit(scale_image_by(self.toad[1], (5 * self.screen_factor[0], 5 * self.screen_factor[1])), (round(100 * self.screen_factor[0]), round(400 * self.screen_factor[1])))
            self.screen.blit(scale_image_by(self.toad_bubble, (5 * self.screen_factor[0], 5 * self.screen_factor[1])), (round(240 * self.screen_factor[0]), round(150 * self.screen_factor[1])))

            # Affichage de la description
            for line in description:
                description_text = scale_image_by(self.game_font.render(line, (0, 0, 0))[0], (0.7 * self.screen_factor[0], 0.7 * self.screen_factor[1]))
                self.screen.blit(description_text, (round(260 * self.screen_factor[0]), round((170 + description.index(line) * 37) * self.screen_factor[1])))

            # Création et affichage des touches du clavier pour le joueur
            layout_joueur = scale_image_by(pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "general", "layout_joueur.png"])), self.screen_factor)
            self.screen.blit(layout_joueur, (round(930 * self.screen_factor[0]), round(300 * self.screen_factor[1])))

            # Mise à jour de l'écran et limite de fps
            pygame.display.flip()
            self.clock.tick(self.fps)

        # Lancement de l'intro du mini-jeu (si le joueur n'a pas fermé la fenêtre)
        if not self.quit:
            self.start_game()


    def start_game(self) -> None:
        """
        Cette méthode représente la phase de lancement du mini-jeu.
        """

        # ---------------------------------------

        # Envoi d'une requête au serveur pour obtenir les infos de chaque joueur
        infos_joueurs = json.loads(self.net.send("0|0|0"))["joueurs"]

        # Création des joueurs
        for ip in infos_joueurs.keys():
            self.joueurs[ip] = Joueur(infos_joueurs[ip]["perso"], infos_joueurs[ip]["type_joueur"])

        # Envoi de la taille du joueur au serveur
        self.net.send(json.dumps({"taille_joueurs": {joueur: self.joueurs[joueur].get_taille() for joueur in self.joueurs.keys()}}))

        # Ajout des ennemis dans la liste des entités
        self.entities.append(Ennemi("boo"))
        self.entities.append(Ennemi("thwomp"))
        self.entities += list(self.joueurs.values())

        # Initialisation de la liste des objets
        self.objets = list(self.entities)

        # Initialisation des paramètres par défaut de la phase
        running = True
        prev_time = time.time()

        # Initialisation du texte start et de ses coordonnées de départ
        start_image = pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "general", "start.png"]))
        start_image_x = -start_image.get_rect().w
        start_image_y = round((640 - start_image.get_rect().h) / 2)

        # Initialisation du timer
        cooldown = 0

        # Initialisation d'une variable qui détecte si la requête pour le serveur a déjà été envoyée
        sent = False

        # Boucle principale de cette phase du jeu
        while running and not self.quit:

            # Détection de la fermeture de fenêtre
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit = True

                # Changement de taille de la fenêtre
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)

            # Envoie d'une requête au serveur pour obtenir son etat
            etat = self.net.send("get_etat")
            running = etat == "minigame_start"

            # Utilisation du moteur de jeu
            self.game_engine([0, 0, 0])

            # Calcul rapide du delta_time (uniquement pour cette animation)
            delta_time = time.time() - prev_time
            prev_time = time.time()

            # Affichage du texte start
            self.screen.blit(scale_image_by(start_image, (4 * self.screen_factor[0], 4 * self.screen_factor[1])), (round(start_image_x * self.screen_factor[0]), round(start_image_y * self.screen_factor[1])))

            # Arrête la phase d'intro si le texte sort de l'écran
            if not sent:
                if start_image_x > 1280:
                    sent = self.net.send("ready_for_next_state") == "ok"

                # Si le texte se trouve au milieu de l'écran et que le timer n'est pas encore lancé
                elif (start_image_x + 2000 * delta_time) > (1000 - start_image.get_rect().w) / 2 and cooldown == 0:
                    cooldown = time.time()
                    pygame.mixer.Sound(sep.join(["..", "data", "sounds", "minigames", "start.ogg"])).play()

                # Si le timer a duré 0.5s ou qu'il n'est pas encore lancé
                elif time.time() - cooldown > 0.5 or cooldown == 0:
                    # Déplacement de l'image
                    start_image_x += 2000 * delta_time
                    start_image_x = round(start_image_x)

            # Mise à jour de l'écran et limite de fps
            pygame.display.flip()
            self.clock.tick(self.fps)

        # Lancement du mini-jeu en lui même (si le joueur n'a pas fermé la fenêtre)
        if not self.quit:

            # Lancement du son de sifflet et la musique chargée
            pygame.mixer.Sound(sep.join(["..", "data", "sounds", "minigames", "start_sifflet.ogg"])).play()
            pygame.mixer.music.play(loops=-1)

            self.during_game()


    def during_game(self) -> None:
        """
        Cette méthode représente la phase de déroulement du mini-jeu.
        """

        # Initialisation des paramètres par défaut de la phase
        running =  True

        # Boucle principale de cette phase du jeu
        while running and not self.quit:

            # Détection de la fermeture de fenêtre
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.quit = True

                # Changement de taille de la fenêtre
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)

            # Envoie d'une requête au serveur pour obtenir son etat
            etat = self.net.send("get_etat")
            running = etat == "minigame_during"

            # Détection des inputs et réinitialisation des vecteurs de déplacement des objets
            inputs = pygame.key.get_pressed()
            input_joueur = [0, 0, 0]

            # Comportement du joueur
            if not self.joueurs[self.net.adresse_client].get_dead():
                if inputs[pygame.K_a] or inputs[pygame.K_q]:
                    input_joueur[0] -= 1
                if inputs[pygame.K_d]:
                    input_joueur[0] += 1
                if inputs[pygame.K_SPACE]:
                    input_joueur[2] = 1

            # Utilisation du moteur de jeu
            self.game_engine(input_joueur)

            # Mise à jour de l'écran et limite de fps
            pygame.display.flip()
            self.clock.tick(self.fps)

        # Lancement de l'affichage de fin (si le joueur n'a pas fermé la fenêtre)
        if not self.quit:
            self.end_game()


    def end_game(self) -> None:
        """
        Cette méthode représente la phase de fin du mini-jeu.
        """

        # Initialisation des paramètres par défaut de la phase
        running = True
        prev_time = time.time()

        # Arrêt de la musique et son de fin
        pygame.mixer.music.stop()
        pygame.mixer.Sound(sep.join(["..", "data", "sounds", "minigames", "finish.ogg"])).play()

        # Initialisation du texte finish et de ses coordonnées de départ
        finish_image = pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "general", "finish.png"]))
        finish_image_x = -finish_image.get_rect().w
        finish_image_y = round((640 - finish_image.get_rect().h) / 2)

        # Initialisation du timer
        cooldown = 0

        # Initialisation d'une variable qui détecte si la requête pour le serveur a déjà été envoyée
        sent = False

        # Boucle principale de cette phase du jeu
        while running and not self.quit:

            # Détection de la fermeture de fenêtre
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit = True

                # Changement de taille de la fenêtre
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)

            # Envoie d'une requête au serveur pour obtenir son etat
            etat = self.net.send("get_etat")
            running = etat == "minigame_end"

            # Utilisation du moteur de jeu
            self.game_engine([0, 0, 0])

            # Calcul rapide du delta_time (uniquement pour cette animation)
            delta_time = time.time() - prev_time
            prev_time = time.time()

            # Affichage du texte finish
            self.screen.blit(scale_image_by(finish_image, (4 * self.screen_factor[0], 4 * self.screen_factor[1])), (round(finish_image_x * self.screen_factor[0]), round(finish_image_y * self.screen_factor[1])))

            # Arrête la phase de fin au bout de 1.5s si le timer est déjà lancé
            if not sent:
                if time.time() - cooldown > 1.5 and cooldown > 0:
                    sent = self.net.send("ready_for_next_state") == "ok"

                # Si le texte se trouve au milieu de l'écran et que le timer n'est pas encore lancé
                elif (finish_image_x + 2000 * delta_time) > (1000 - finish_image.get_rect().w) / 2 and cooldown == 0:
                    cooldown = time.time()

                # Si le timer n'est pas encore lancé
                elif cooldown == 0:
                    finish_image_x += 2000 * delta_time
                    finish_image_x = round(finish_image_x)

            # Mise à jour de l'écran et limite de fps
            pygame.display.flip()
            self.clock.tick(self.fps)

        # Lancement de l'annonce des gagnants (si le joueur n'a pas fermé la fenêtre)
        if not self.quit:
            self.announce_winners()


    def announce_winners(self) -> None:
        """
        Cette méthode permet d'annoncer les gagnants du mini-jeu à l'aide d'un affichage spécial
        sur l'écran.
        """

        # Initialisation des paramètres par défaut de la phase
        running = True

        # Envoie d'une requête au serveur pour obtenir les infos du classement
        classement = json.loads(self.net.send("0|0"))["classement"]

        # On note tous les gagnants de la partie
        gagnants = []
        for ip in self.joueurs.keys():
            if classement[ip] == 1:
                gagnants.append(self.joueurs[ip].get_perso())

        # Initialisation du texte win
        win_image = None

        # Changement du texte et de la musique jouée selon différents cas
        if len(gagnants) == 0:
            win_image = pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "general", "tie.png"]))
            pygame.mixer.music.load(sep.join(["..", "data", "musics", "minigames", "draw.ogg"]))
        elif len(gagnants) > 1:
            win_image = pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "general", "wins.png"]))
            pygame.mixer.music.load(sep.join(["..", "data", "musics", "minigames", "win.ogg"]))
        else:
            win_image = pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "general", "win.png"]))
            pygame.mixer.music.load(sep.join(["..", "data", "musics", "minigames", "win.ogg"]))

        # Timer de 5s
        cooldown = 5 + time.time()

        # Lancement de la musique
        pygame.mixer.music.play()

        # Initialisation d'une variable qui détecte si la requête pour le serveur a déjà été envoyée
        sent = False

        # Boucle principale de cette phase du jeu
        while running and not self.quit:

            # Détection de la fermeture de fenêtre
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit = True

                # Changement de taille de la fenêtre
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)

            # Envoie d'une requête au serveur pour obtenir son etat
            etat = self.net.send("get_etat")
            running = etat == "minigame_winners"

            # Utilisation du moteur de jeu
            try:
                self.game_engine([0, 0, 0])
            except:
                break

            # Position x du texte du 1er gagnant
            image_x = 120 if len(gagnants) > 2 else 320

            for gagnant in gagnants:
                # Initialisation et positionnement du texte de chaque gagnant
                image_gagnant = scale_image_by(pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "general", gagnant + ".png"])), 4)
                image_rect = image_gagnant.get_rect()
                image_rect.center = (640, 400)

                # On positionne le texte en x avec image_x seulement si plusieurs joueurs gagnent
                if len(gagnants) > 1:
                    image_rect.x = image_x

                # Affichage du texte de chaque gagnant
                self.screen.blit(scale_image_by(image_gagnant, self.screen_factor), (round(image_rect.x * self.screen_factor[0]), round(image_rect.y * self.screen_factor[1])))

                # On déplace le prochain texte 50 pixels plus loin
                image_x += image_rect.w + 50

            # Positionnement du texte win
            scaled_win = scale_image_by(win_image, (4 * self.screen_factor[0], 4 * self.screen_factor[1]))
            win_rect = scaled_win.get_rect()
            win_rect.center = (round(640 * self.screen_factor[0]), round(520 * self.screen_factor[1]))

            # Affichage du texte win
            self.screen.blit(scaled_win, win_rect)

            # Arrêt du script au bout du timer
            if cooldown - time.time() <= 0 and not sent:
                sent = self.net.send("ready_for_next_state") == "ok"

            # Mise à jour de l'écran et limite de fps
            pygame.display.flip()
            self.clock.tick(self.fps)