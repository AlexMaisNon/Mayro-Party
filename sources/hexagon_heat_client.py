#Projet : Mayro Party
#Auteurs : Hinata Bouaziz, Antoine Desrues, Alexandre Guillaume, Matisse Moreau

# ------/ Importations des bibliothèques \------

import pygame
import pygame.freetype
from math import floor
import random
import time
from os import sep

from utils import Network, scale_image_by
import json

# ------/ Classes \------

# Classe du joueur
class Joueur:

    # ------/ Constructeur \------

    def __init__(self, perso: str) -> None:
        """
        Constructeur de la classe Joueur.

        Attributs à définir:
            - perso (str): Personnage choisit par le joueur.

        Attributs internes:
            - pos (list): Position du joueur.
            - rotation (str): Rotation du joueur.
            - invincibility (int): Timer qui détermine l'invincibilité du joueur.
            - dead (bool): Définit si le joueur est mort ou non.

            - sprites_directory (str): Chemin du dossier des sprites du joueur.
            - sprites (dict): Sprites du joueurs.
            - sprite (pygame.Surface): Sprite actuel du joueur.
            - sprite_pos (list): Position du sprite.

            - shadow (pygame.Surface): Sprite de l'ombre du joueur.
            - shadow_pos (list): Position de l'ombre.

            - frame (float): Indice du sprite à choisir.

            - priority (float): Valeur représentant la priorité d'affichage du sprite.

            - sounds (dict): Sons du joueur.

            - taille (list): Dimensions du sprite du joueur (fournis au serveur).

            - ground_height (float): Représente la plus haute coordonnée du sol par rapport au joueur.
        """


        # Définition du joueur
        self.perso = perso

        # Caractéristiques principales (stats)
        self.pos = [0.0, 0.0, 0.0]
        self.rotation = "down"
        self.invincibility = 0
        self.dead = False

        # Emplacement des sprites du joueur
        self.sprites_directory = sep.join(["..", "data", "sprites", "characters", self.perso])

        # Définition des sprites automatiquement (pour les joueurs / ia)
        self.sprites = {
            "walk": {
                "left": [scale_image_by(pygame.image.load(sep.join([self.sprites_directory, "walk_left" + str(i) + ".png"])), 3) for i in range(8)],
                "down": [scale_image_by(pygame.image.load(sep.join([self.sprites_directory, "walk_down" + str(i) + ".png"])), 3) for i in range(8)],
                "up": [scale_image_by(pygame.image.load(sep.join([self.sprites_directory, "walk_up" + str(i) + ".png"])), 3) for i in range(8)],
                "right": [scale_image_by(pygame.image.load(sep.join([self.sprites_directory, "walk_right" + str(i) + ".png"])), 3) for i in range(8)]
            },
            "jump": {
                "left": [scale_image_by(pygame.image.load(sep.join([self.sprites_directory, "jump_left" + str(i) + ".png"])), 3) for i in range(2)],
                "down": [scale_image_by(pygame.image.load(sep.join([self.sprites_directory, "jump_down" + str(i) + ".png"])), 3) for i in range(2)],
                "up": [scale_image_by(pygame.image.load(sep.join([self.sprites_directory, "jump_up" + str(i) + ".png"])), 3) for i in range(2)],
                "right": [scale_image_by(pygame.image.load(sep.join([self.sprites_directory, "jump_right" + str(i) + ".png"])), 3) for i in range(2)]
            },
            "death": [scale_image_by(pygame.image.load(sep.join([self.sprites_directory, "death" + str(i) + ".png"])), 3) for i in range(4)]
        }

        # Initialisation et positionnement du sprite actuel
        self.sprite = self.sprites["walk"]["down"][0]
        self.sprite_pos = list(self.pos)

        # Initialisation et positionnement de l'ombre
        self.shadow = scale_image_by(pygame.image.load(sep.join([self.sprites_directory, "shadow.png"])), 3)
        self.shadow_pos = list(self.pos)

        # Initialisation de la frame choisie
        self.frame = 0.0

        # Initialisation et mise à jour de la priorité d'affichage
        self.priority = 0.0
        self.update_priorite()

        # Sons du joueur
        self.sounds = {
            "jump": [pygame.mixer.Sound(sep.join(["..", "data", "sounds", self.perso, "jump" + str(i) + ".ogg"])) for i in range(2)],
            "death": pygame.mixer.Sound(sep.join(["..", "data", "sounds", self.perso, "death.ogg"]))
        }

        # Initialisation de la taille du joueur (uniquement fournie au serveur)
        self.taille = [self.sprite.get_rect().w, self.sprite.get_rect().h]

        # Uniquement utilisé ici pour pouvoir afficher l'ombre en dessous du joueur
        self.ground_height = 0.0

        # Initialisation des paramètres du son de saut
        self.delai_son_saut = 0.0
        self.lancer_son_saut = False


    # ------/ Getters \------

    def get_perso(self) -> str:
        return self.perso

    def get_pos(self) -> list:
        return self.pos

    def get_invincibility(self) -> int:
        return self.invincibility

    def get_dead(self) -> bool:
        return self.dead

    def get_priority(self) -> float:
        return self.priority

    def get_sounds(self) -> dict:
        return self.sounds

    def get_taille(self) -> list:
        return self.taille

    def get_delai_son_saut(self) -> float:
        return self.delai_son_saut

    def get_lancer_son_saut(self) -> bool:
        return self.lancer_son_saut


    # ------/ Setters \------

    def set_pos(self, new_pos: list) -> None:
        self.pos = new_pos

    def set_rotation(self, new_rotation: str) -> None:
        self.rotation = new_rotation

    def set_invincibility(self, new_invincibility: int) -> None:
        self.invincibility = new_invincibility

    def set_dead(self, new_dead: bool) -> None:
        self.dead = new_dead

    def set_ground_height(self, new_ground_height) -> None:
        self.ground_height = new_ground_height

    def set_delai_son_saut(self, new_delai_son_saut) -> None:
        self.delai_son_saut = new_delai_son_saut

    def set_lancer_son_saut(self, new_lancer_son_saut) -> None:
        self.lancer_son_saut = new_lancer_son_saut


    # ------/ Méthodes \------

    def update_priorite(self) -> None:
        """
        Cette méthode permet de calculer et de mettre à jour la priorité d'affichage.
        """

        # On calcule le bas de la position y (en ajoutant la taille du sprite) on ajoute sa position en z
        self.priority = -(self.pos[1] + self.sprite.get_rect().h) + self.pos[2]


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

        # Positionnement de l'ombre
        self.shadow_pos[0] = round(self.pos[0] + (self.sprite.get_rect().w - self.shadow.get_rect().w) / 2)
        self.shadow_pos[1] = round(self.pos[1] + self.sprite.get_rect().h - self.shadow.get_rect().h)
        self.shadow_pos[2] = 0


    def animer(self, frame: "int | float", velocite: list) -> None:
        """
        Cette méthode permet d'animer le sprite du joueur.

        Paramètres:
            - frame (int ou float): Indique la frame actuelle du serveur. Utilisée pour la vitesse
            des sprites de l'animation.
            - velocite (list): Vélocité fournie par le serveur.
        """

        # Test du type des variables
        assert type(frame) == int or type(frame) == float, "Erreur: Le 1er paramètre (frame) doit être un nombre."
        assert type(velocite) == list, "Erreur: Le 2ème paramètre (velocite) doit être une liste."

        # On détecte si le joueur est mort en priorité
        if self.dead:
            # Changement du sprite actuel
            self.sprite = self.sprites["death"][floor(frame % len(self.sprites["death"]))]

        # On détecte si le joueur est sur le sol
        elif velocite[2] == 0:
            # Changement du sprite actuel
            self.sprite = self.sprites["walk"][self.rotation][floor(frame % len(self.sprites["walk"][self.rotation]))]

        # Le joueur est en dehors du sol
        else:
            # En train de sauter
            if velocite[2] <= 0:
                self.sprite = self.sprites["jump"][self.rotation][0]
            # En chute libre
            else:
                self.sprite = self.sprites["jump"][self.rotation][1]


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

        # Affichage de l'ombre du personnage (dépend de la hauteur du sol)
        if not self.dead:
            screen.blit(scale_image_by(self.shadow, screen_factor), (round(self.shadow_pos[0] * screen_factor[0]), round((self.shadow_pos[1] + self.ground_height) * screen_factor[1])))

        # Ici, self.invincibility % 5 == 0 permet de créer un effet de clignotement uniquement lors de l'invincibilité
        if self.invincibility % 5 == 0:
            screen.blit(scale_image_by(self.sprite, screen_factor), (round(self.pos[0] * screen_factor[0]), round((self.pos[1] + self.pos[2]) * screen_factor[1])))



# Classe d'une plateforme sous la forme d'un hexagone
class Hexagon:

    # ------/ Constructeur \------

    def __init__(self, pos, color, sprite) -> None:
        """
        Constructeur de la classe Hexagon.

        Attributs à définir:
            - pos (list): Position de l'hexagone.
            - color (str): Couleur de l'hexagone.
            - sprite (pygame.Surface): Sprite de l'hexagone.

        Attributs internes:
            - shadow (pygame.Surface): Sprite de l'ombre de l'hexagone.
            - shadow_pos (list): Position de l'ombre.

            - hidden (bool): Indique si le sprite est affiché ou non.

            - height (int): Hauteur du sprite de l'hexagone.

            - priority (float): Valeur représentant la priorité d'affichage du sprite.
        """

        # Caractéristiques par défaut
        self.pos = pos
        self.color = color
        self.sprite = scale_image_by(pygame.image.load(sprite), 4)

        # Initialisation et positionnement de l'ombre
        self.shadow = scale_image_by(pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "hexagon_heat", "hexagons", "shadow.png"])), 4)
        self.shadow_pos = list(self.pos)

        # Initialisation de la variable hidden
        self.hidden = False

        # La position Z correspond au point le plus haut du bloc (en comptant seulement la plus haute collision qui a une hauteur de 160)
        self.height = -self.sprite.get_rect().h + 160

        # Initialisation et mise à jour de la priorité d'affichage
        self.priority = 0.0
        self.update_priorite()


    # ------/ Getters \------

    def get_pos(self) -> list:
        return self.pos

    def get_color(self) -> str:
        return self.color

    def get_priority(self) -> float:
        return self.priority

    def get_height(self) -> int:
        return self.height


    # ------/ Setters \------

    def set_pos(self, new_pos: list) -> None:
        self.pos = new_pos

    def set_hidden(self, new_hidden: bool) -> None:
        self.hidden = new_hidden


    # ------/ Méthodes \------

    def update_priorite(self) -> None:
        """
        Cette méthode permet de calculer et de mettre à jour la priorité d'affichage.
        """

        # On prend la plus haute collision (se situant en self.pos[1] + 52) et on ajoute sa position en z et sa hauteur
        self.priority = -(self.pos[1] + 52) + self.height + self.pos[2]


    def appliquer_positions(self, position: list) -> None:
        """
        Cette méthode permet d'appliquer toutes les positions nécessaire pour la plateforme.

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

        # On applique la nouvelle position à l'hexagone
        self.pos = position

        # Positionnement de l'ombre
        self.shadow_pos[0] = self.pos[0]
        self.shadow_pos[1] = self.pos[1] - self.height
        self.shadow_pos[2] = 0


    def afficher(self, screen: pygame.Surface) -> None: # type: ignore
        """
        Cette méthode permet d'afficher l'hexagone sur l'écran.

        Paramètres:
            - screen (pygame.Surface): L'écran de jeu de pygame.
        """

        # Tests des types de variables
        assert type(screen) == pygame.Surface, "Erreur: Le paramètre (screen) n'est pas une surface pygame."

        # Initialisation des facteurs pour la taille de l'écran
        screen_factor = ((screen.get_rect().size[0] / 1280), (screen.get_rect().size[1] / 720))

        # On ne l'affiche pas s'il est caché
        if not self.hidden:
            # On n'affiche pas l'ombre si l'hexagone est posé sur le sol
            if self.pos[2] != 0:
                screen.blit(scale_image_by(self.shadow, screen_factor), (round(self.shadow_pos[0] * screen_factor[0]), round(self.shadow_pos[1] * screen_factor[1])))

            screen.blit(scale_image_by(self.sprite, screen_factor), (round(self.pos[0] * screen_factor[0]), round((self.pos[1] + self.pos[2]) * screen_factor[1])))



# Classe d'une Pile (toujours très utile les piles)
class Pile:

    # ------/ Constructeur \------

    def __init__(self) -> None:
        """
        Constructeur de la classe Pile.

        Attributs internes:
            - contenu (list): Représente le contenu de la pile.
        """

        self.contenu = []


    # ------/ Méthodes \------

    def empile(self, item: any) -> None:
        """
        Cette méthode permet d'empiler un élément sur la pile.

        Paramètres:
            - item (any): N'importe quel élément.
        """

        self.contenu.append(item)


    def depile(self) -> any:
        """
        Cette méthode permet de dépiler un élément de la pile.

        Returns:
            - item (any): N'importe quel élément.

        Post-conditions:
            - La méthode renvoie l'élément au sommet de la pile et le retire de la pile.
            Si il n'y a pas d'élément, on renvoie None.
        """

        # Initialisation de l'élément à renvoyer
        elem = None

        if len(self.contenu) > 0:
            elem = self.contenu.pop()

        return elem


    def est_vide(self) -> bool:
        """
        Cette méthode indique si la pile est vide ou non.

        Returns:
            - bool: Indique si la pile est vide ou non.

        Post-conditions:
            - Si la pile est vide, on renvoie True, sinon on renvoie False.
        """

        return len(self.contenu) == 0


    def taille(self) -> int:
        """
        Cette méthode indique la taille de la pile.

        Returns:
            - int: représente la taille de la pile.

        Post-conditions:
            - La méthode renvoie un nombre entier qui représente le nombre d'éléments qui
            constituent la pile.
        """

        return len(self.contenu)



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
            - priorities (dict): Priorité d'affichage pour chaque objet.

            - toad (list): Images du Toad de l'écran de chargement.
            - toad_shadow (pygame.Surface): Image de l'ombre de Toad.
            - toad_bubble (pygame.Surface): Image de la bulle de dialogue de Toad. 

            - bg (pygame.Surface): Image de fond pour le mini-jeu.
            - current_toad (pygame.Surface): Sprite actuel de Toad.
            - toad_platform (pygame.Surface): Image de la plateforme de Toad.
            - hexagons (list): Liste des hexagones.

            - lava_sound (pygame.mixer.Sound): Son d'ambience de lave.

            - classement (Pile ou dict): Classement des joueurs à la fin du mini-jeu.
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
        self.hexagones = {}
        self.objets = []
        self.priorities = {}

        # Sprites de toad (pour le chargement)
        self.toad = [pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "general", "toad", "toad.png"])),
                     pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "general", "toad", "toad_open.png"]))]
        self.toad_shadow = pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "general", "toad", "shadow.png"]))
        self.toad_bubble = pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "general", "toad", "bubble.png"]))

        # Emplacement des sprites du mini-jeu
        minigame_directory = sep.join(["..", "data", "sprites", "minigames", "hexagon_heat"])

        # Sprites utilisés dans la classe
        self.bg = pygame.image.load(sep.join([minigame_directory, "lava.png"]))
        self.current_toad = self.toad[0]
        self.toad_platform = pygame.image.load(sep.join([minigame_directory, "hexagons", "toad.png"]))

        # Création des bulles de dialogues où s'affichent les plateformes à partir d'une liste de couleurs
        colors = ["blue", "green", "magenta", "pink", "cyan", "yellow", "red"]
        self.bubbles = {color: pygame.image.load(sep.join([minigame_directory, "toad", color + "_bubble.png"])) for color in colors}

        # Son de lave
        self.lava_sound = pygame.mixer.Sound(sep.join(["..", "data", "sounds", "minigames", "hexagon_heat", "lava_ambient.ogg"]))

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
        infos_hexagones = infos_environnement["hexagones"]
        infos_couleur = infos_environnement["couleur"]
        fps = infos_environnement["fps"]

        # Changement du sprite de Toad en fonction des infos du serveur
        self.current_toad = self.toad[1] if infos_couleur[1] else self.toad[0]

        # On affiche les sprites du jeu dans un ordre d'affichage prédéfini
        self.screen.blit(scale_image_by(self.bg, self.screen_factor), (0, 0))
        self.screen.blit(scale_image_by(self.toad_platform, (4 * self.screen_factor[0], 4 * self.screen_factor[1])), (round(1100 * self.screen_factor[0]), round(348 * self.screen_factor[1])))
        self.screen.blit(scale_image_by(self.toad_shadow, (4 * self.screen_factor[0], 4 * self.screen_factor[1])), (round(1134 * self.screen_factor[0]), round(382 * self.screen_factor[1])))
        self.screen.blit(scale_image_by(self.current_toad, (3 * self.screen_factor[0], 3 * self.screen_factor[1])), (round(1128 * self.screen_factor[0]), round(300 * self.screen_factor[1])))

        # Affichage de la bulle de Toad correspondante
        if infos_couleur[1]:
            self.screen.blit(scale_image_by(self.bubbles[infos_couleur[0]], (3 * self.screen_factor[0], 3 * self.screen_factor[1])), (round(1000 * self.screen_factor[0]), round(116 * self.screen_factor[1])))

        for id_joueur in self.joueurs.keys():
            # On met à jour la position des joueurs et des animations pour le client
            self.joueurs[id_joueur].appliquer_positions(infos_joueurs[id_joueur]["pos"])
            self.joueurs[id_joueur].set_rotation(infos_joueurs[id_joueur]["rotation"])
            self.joueurs[id_joueur].set_ground_height(infos_joueurs[id_joueur]["ground_height"])

            # On détecte si le joueur est mort
            ancien_dead = self.joueurs[id_joueur].get_dead()
            self.joueurs[id_joueur].set_dead(infos_joueurs[id_joueur]["dead"])

            # Si l'état de mort n'est pas le même qu'avant, il a été changé, donc il est mort
            if ancien_dead != self.joueurs[id_joueur].get_dead():
                self.joueurs[id_joueur].get_sounds()["death"].play()

            # Même style de détection avec l'invincibilité
            ancien_invincibilite = self.joueurs[id_joueur].get_invincibility()
            self.joueurs[id_joueur].set_invincibility(infos_joueurs[id_joueur]["invincibility"])
            if ancien_invincibilite - self.joueurs[id_joueur].get_invincibility() < 0:
                self.joueurs[id_joueur].get_sounds()["death"].play()

            # Même style de détection avec le saut
            self.joueurs[id_joueur].set_invincibility(infos_joueurs[id_joueur]["invincibility"])

            # On lance le son uniquement lors du début du saut (lorsque la vélocité est négative)
            if infos_joueurs[id_joueur]["velocity"][2] < 0 and self.joueurs[id_joueur].get_lancer_son_saut():
                # Tant que le joueur n'est pas mort et que le délai est dépassé
                if not self.joueurs[id_joueur].get_dead() and self.joueurs[id_joueur].get_delai_son_saut() - time.time() <= 0:
                    # Choix aléatoire entre 2 sons de saut
                    random.choice(self.joueurs[id_joueur].get_sounds()["jump"]).play()

                    # On empêche le jeu de relancer le son tant que le joueur n'a pas atterrit
                    self.joueurs[id_joueur].set_lancer_son_saut(False)

                    # On met un délai de 0.2s ici pour éviter que le son se répète trop rapidement
                    self.joueurs[id_joueur].set_delai_son_saut(0.2 + time.time())

            # On réactive le son de saut si le joueur est en train d'atterrir sur le sol
            if infos_joueurs[id_joueur]["velocity"][2] > 0 and not self.joueurs[id_joueur].get_lancer_son_saut():
                self.joueurs[id_joueur].set_lancer_son_saut(True)

            self.joueurs[id_joueur].animer(infos_joueurs[id_joueur]["frame"], infos_joueurs[id_joueur]["velocity"])

        # On met à jour la position des hexagones pour le client
        for couleur in self.hexagones.keys():
            self.hexagones[couleur].appliquer_positions(infos_hexagones[couleur]["pos"])
            self.hexagones[couleur].set_hidden(infos_hexagones[couleur]["hidden"])

        # On calcule la priorité d'affichage pour tous les objets existants (y compris des joueurs)
        for objet in self.objets:
            self.priorities[objet] = objet.get_priority()
            objet.update_priorite()

        # sorted permet ici de trier les clés du dictionnaire automatiquement en fonction de la valeur d'affichage
        # (sorted c'est beaucoup plus simple j'avoue)
        for priority in sorted(self.priorities, key=self.priorities.get, reverse=True):
            priority.afficher(self.screen)

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
        description = ["Restez sur la plateforme donnée",
                       "par Toad avant que les autres",
                       "s'enfoncent dans la lave !",
                       "Le dernier survivant gagne !"]

        nom = "Hexagon Heat"
        chemin_musique = sep.join(["..", "data", "musics", "minigames", "hexagon_heat.ogg"])

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

        # Activation du son de lave
        self.lava_sound.play()

        # Envoi d'une requête au serveur pour obtenir les infos de chaque joueur
        infos_environnement = json.loads(self.net.send("0|0|0"))
        infos_joueurs = infos_environnement["joueurs"]
        infos_hexagones = infos_environnement["hexagones"]

        # Création des joueurs
        for ip in infos_joueurs.keys():
            self.joueurs[ip] = Joueur(infos_joueurs[ip]["perso"])

        # Initialisation des hexagones présents dans le mini-jeu
        for color in infos_hexagones.keys():
            self.hexagones[color] = Hexagon(infos_hexagones[color]["pos"], color, sep.join(["..", "data", "sprites", "minigames", "hexagon_heat", "hexagons", color + ".png"]))

        # Envoi de la taille du joueur au serveur
        self.net.send(json.dumps({"taille_joueurs": {joueur: self.joueurs[joueur].get_taille() for joueur in self.joueurs.keys()}}))

        # Initialisation de la liste des objets
        self.objets = list(self.joueurs.values()) + list(self.hexagones.values())

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
        running = True

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

            # Détection des inputs et réinitialisation des vecteurs de déplacement des joueurs
            inputs = pygame.key.get_pressed()
            input_joueur = [0, 0, 0]

            # Comportement du joueur
            if not self.joueurs[self.net.adresse_client].get_dead():
                if inputs[pygame.K_a] or inputs[pygame.K_q]:
                    input_joueur[0] -= 1
                if inputs[pygame.K_s]:
                    input_joueur[1] += 1
                if inputs[pygame.K_w] or inputs[pygame.K_z]:
                    input_joueur[1] -= 1
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
            # Arrêt du son d'ambience de lave
            self.lava_sound.stop()

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