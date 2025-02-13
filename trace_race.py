# Fait par Alexandre

# ------/ Importations des bibliothèques \------

import pygame
import pygame.freetype
from math import sqrt
import random
import time
from os import sep

import assets.generic as generic


# ------/ Fonctions utiliatires \------

def normalize(vecteur: list) -> list:
    """
    Cette fonction permet de "normaliser" un vecteur donné. Elle sert lors des calculs du mouvement
    d'entités en diagonale. La fonction empêche un bug qui permet aux entités de se déplacer plus
    rapidement en diagonale qu'en marchant tout droit.

    Paramètres:
        - vecteur (list): un vecteur donné.
    Renvois:
        - list: un vecteur modifié à partir du vecteur donné.
    Pré-conditions:
        - vecteur doit être une liste.
    Post-conditions:
        - La fonction doit renvoyer un vecteur modifié uniquement lorsque les valeurs x et y du vecteur
        ne sont pas égales à 0, sinon elle doit renvoyer le même vecteur.
    """

    # Tests du type de vecteur
    assert type(vecteur) == list, "Erreur: Le 1er paramètre (vecteur) n'est pas une liste."

    # Initialisation d'un nouveau vecteur
    n_v = []

    # On fait les calculs sur les axes x et y s'ils ne sont pas égaux à 0
    if not 0 in vecteur:
        # sqrt(2) / 2 est longueur d'une diagonale dans un carré
        n_v = [elem * (sqrt(2) / 2) for elem in vecteur]
    else:
        # On ne fait pas de modification
        n_v = [elem for elem in vecteur]

    return n_v


# ------/ Classes \------

# Classe du joueur
class Joueur(generic.GenericJoueur):

    # ------/ Constructeur \------

    def __init__(self, perso: str, id: int, ia: bool, color: str) -> None:
        """
        Constructeur de la classe Joueur.

        Attributs à définir:
            - perso (str): Personnage choisit par le joueur.
            - id (int): id du joueur qui indique sa position dans l'ordre de jeu.
            - ia (bool): Indique si le joueur est une ia ou un joueur lambda.
            - color (str): Couleur du crayon du joueur (exclusif à ce mini-jeu).

        Attributs internes:
            - pos (list): Position du joueur.
            - velocity (list): Vélocité/Accélération du joueur.
            - speed (int): Vitesse du joueur.

            - is_drawing (bool): Indique si le joueur dessine ou non.

            - sprites (dict): Sprites du joueurs.
            - sprite (pygame.Surface): Sprite actuel du joueur.
            - frame (float): Indice du sprite à choisir.

            - pen (pygame.Surface): Sprite du crayon.
            - pen_pos (list): Position du crayon.

            - shadow (pygame.Surface): Sprite de l'ombre du joueur.
            - shadow_pos (list): Position de l'ombre.

            - collision (pygame.Rect): Boîte de collision du joueur.
        """

        # Tests du type des paramètres donnés
        assert type(color) == str, "Erreur: Le 4ème paramètre (color) est censé être une chaîne de caractères."


        # On initialise tous les attributs du constructeur parent
        super().__init__(perso, id, ia)

        # Définition du joueur
        self.color = color

        # Caractéristiques principales (stats)
        self.speed = 100

        # Définit si le joueur dessine ou non
        self.is_drawing = True

        # Définition des sprites automatiquement (pour les joueurs / ia)
        self.sprites = {
            "trace": [generic.scale_image_by(pygame.image.load(self.sprites_directory + "trace" + str(i) + ".png"), 3) for i in range(8)],
            "idle": generic.scale_image_by(pygame.image.load(self.sprites_directory + "walk_right0.png"), 3)
        }

        # Initialisation du sprite actuel et de la frame choisie
        self.sprite = self.sprites["trace"][0]

        # Initialisation et positionnement du stylo
        self.pen = generic.scale_image_by(pygame.image.load("assets" + sep + "sprites" + sep + "minigames" + sep + "trace_race" + sep + self.color + "_pen.png"), 3)
        self.pen_pos = list(self.pos)

        # Boîte de collision du personnage
        self.collision = pygame.Rect(0, 0, round((self.sprite.get_rect().w + 2) / 2), 20)


    # ------/ Getters \------

    def get_color(self) -> str:
        return self.color

    def get_is_drawing(self) -> bool:
        return self.is_drawing

    def get_pen(self) -> pygame.Surface: # type: ignore
        return self.pen

    def get_pen_pos(self) -> list:
        return self.pen_pos


    # ------/ Setters \------

    def set_is_drawing(self, new_is_drawing: bool) -> None:
        self.is_drawing = new_is_drawing


    # ------/ Méthodes \------

    def calculate_velocity(self, direction: list, delta_time: float) -> None:
        """
        Cette méthode permet de calculer la vélocité du joueur.

        Paramètres:
            - direction (list): Direction sous forme de vecteur dans laquelle le joueur se déplace.
            - delta_time (float): Valeur calculé dans le moteur de jeu qui permet l'indépendance de la vitesse au framerate.

        Pré-conditions:
            - direction doit être compris entre -1 et 1.
        """

        # Test des types de variables
        assert type(direction) == list, "Erreur: Le 1er paramètre (direction) n'est pas une liste."
        assert type(delta_time) == float, "Erreur: Le 2ème paramètre (delta_time) n'est pas un nombre flottant."

        # Le parent s'occupe du calcul
        super().calculate_velocity(direction, delta_time)

        # On normalise la vélocité
        self.velocity = normalize(self.velocity)


    def calculate_collisions(self, objets: list) -> None:
        """
        Cette méthode permet de calculer les collisions avec le joueur.

        Paramètres:
            - objets (list): Liste d'objets avec lesquels le joueur doit calculer les collisions.

        Pré-conditions:
            - objets doit contenir seulement des objets de type Collider ou Joueur.
        """

        # Test du type de objets
        assert type(objets) == list, "Erreur: Le paramètre donné (objets) n'est pas une liste."

        # Tests des éléments de objets
        for elem in objets:
            assert type(elem) == Collider or type(elem) == Joueur, "Erreur: La liste doit être seulement composée d'objets de type Collider ou Joueur."

        # Calcul des collisions pour chaque objets
        for objet in objets:
            if objet != self:
                rect_x = pygame.Rect(self.collision.x + round(self.velocity[0]), self.collision.y, self.collision.w, self.collision.h)
                rect_y = pygame.Rect(self.collision.x, self.collision.y + round(self.velocity[1]), self.collision.w, self.collision.h)

                for collision in objet.get_collisions():
                    if rect_x.colliderect(collision):
                        # Si l'objet suit la caméra, il s'agit forcément de l'arrivé
                        # (car c'est le seul collider qui suit la caméra)
                        try:
                            assert objet.get_following_camera(), "Erreur: Méthode introuvable (car pas collider) ou ne suit pas la caméra (donc pas arrivée)."

                            # Arrête de dessiner (car a touché l'arrivé)
                            self.is_drawing = False
                        except:
                            self.velocity[0] = 0.0

                    if rect_y.colliderect(collision):
                        # Pareil ici
                        try:
                            assert objet.get_following_camera(), "Erreur: Méthode introuvable (car pas collider) ou ne suit pas la caméra (donc pas arrivée)."

                            # Arrête de dessiner (car a touché l'arrivé)
                            self.is_drawing = False
                        except:
                            self.velocity[1] = 0.0


    def apply_velocity(self, cam_mov: int) -> None:
        """
        Cette méthode permet d'appliquer la vélocité à la position et à d'autres paramètres du joueur en fonction du
        mouvement de la caméra.

        Paramètres:
            - cam_mov (int): Vélocité de la caméra.
        """

        # Test du type de cam_mov
        assert type(cam_mov) == int, "Erreur: Le paramètre donné (cam_mov) n'est pas un nombre entier."

        # Le parent applique l'accélération à la position
        super().apply_velocity()

        # On déplace le joueur en fonction du mouvement de la caméra
        self.pos[0] -= cam_mov

        # Seulement s'il dessine parce que ça peut causer des problèmes lors des cinématiques
        if self.is_drawing:
            # Le joueur ne peut pas dépasser l'écran
            self.pos[0] = max(0, min(self.pos[0], 1280 - self.sprite.get_rect().w))

        # Positionnement du crayon
        self.pen_pos[0] = round(self.pos[0] + self.sprite.get_rect().w - self.pen.get_rect().w) + 6
        self.pen_pos[1] = round(self.pos[1] + self.sprite.get_rect().bottom - self.pen.get_rect().h) - 8

        # Positionnement de la boîte de collision
        self.collision.x = round(self.pos[0] + self.sprite.get_rect().w / 4)
        self.collision.y = round(self.pos[1] + self.sprite.get_rect().h - self.collision.h)

        # Positionnement de l'ombre
        self.shadow_pos[0] = round(self.pos[0] + (self.sprite.get_rect().w - self.shadow.get_rect().w) / 2)
        self.shadow_pos[1] = round(self.pos[1] + self.sprite.get_rect().h - self.shadow.get_rect().h)


    def animate(self, delta_time: float) -> None:
        """
        Cette méthode permet d'animer le sprite du joueur.

        Paramètres:
            - delta_time (float): Valeur calculé dans le moteur de jeu qui permet l'indépendance de la vitesse au framerate.

        Pré-conditions:
            - delta_time doit être un nombre flottant.
        """

        # Test du type de delta_time
        assert type(delta_time) == float, "Erreur: Le paramètre donné (delta_time) n'est pas un nombre flottant."

        # N'a pas d'animation s'il ne dessine pas
        if self.is_drawing:
            # L'animation reste figée si le joueur est immobile
            if self.velocity[0] == 0 and self.velocity[1] == 0:
                self.frame = 0

            # self.frame ne doit pas dépasser l'indice de la liste de sprites
            if self.frame > len(self.sprites["trace"]) - 1:
                self.frame = 0

            # Changement du sprite actuel
            self.sprite = self.sprites["trace"][round(self.frame)]

            # Le parent s'occupe de changer la frame en fonction de la vitesse
            super().animate(delta_time, 9)
        else:
            self.sprite = self.sprites["idle"]


    def draw(self, screen: pygame.Surface, show_collision: bool = False) -> None: # type: ignore
        """
        Cette méthode permet de dessiner le joueur sur l'écran.

        Paramètres:
            - screen (pygame.Surface): L'écran de jeu de pygame.
            - show_collision (bool): Paramètre optionnel permettant d'afficher les boîtes de collision.

        Pré-conditions:
            - screen doit être de type pygame.Surface.
        """

        # Tests des types de variables
        assert type(screen) == pygame.Surface, "Erreur: Le 1er paramètre (screen) n'est pas une surface pygame."
        assert type(show_collision) == bool, "Erreur: Le 2ème paramètre (show_collision) n'est pas un booléen."

        # Initialisation des facteurs pour la taille de l'écran avec le parent
        screen_factor = super().draw(screen, show_collision)

        # Affichage de l'ombre du joueur
        screen.blit(generic.scale_image_by(self.shadow, screen_factor), (round(self.shadow_pos[0] * screen_factor[0]), round(self.shadow_pos[1] * screen_factor[1])))

        # Affiche le crayon uniquement si le joueur dessine
        if self.is_drawing:
            screen.blit(generic.scale_image_by(self.pen, screen_factor), (round(self.pen_pos[0] * screen_factor[0]), round(self.pen_pos[1] * screen_factor[1])))

        # Affichage du sprite du joueur
        screen.blit(generic.scale_image_by(self.sprite, screen_factor), (round(self.pos[0] * screen_factor[0]), round(self.pos[1] * screen_factor[1])))



class Collider:

    # ------/ Constructeur \------

    def __init__(self, pos, taille, following_camera) -> None:
        """
        Constructeur de la classe Collider.

        Attributs à définir:
            - pos (list): Position du collider.
            - taille (list): Taille du collider.
            - following_camera (bool): Indique si le collider doit suivre le mouvement de la caméra.

        Attributs internes:
            - collision (pygame.Rect): Boîte de collision du collider.
        """

        # Test des types des paramètres donnés
        assert type(pos) == list, "Erreur: Le 1er paramètre (pos) n'est pas une liste."
        assert type(taille) == list, "Erreur: Le 2ème paramètre (taille) n'est pas une liste."
        assert type(following_camera) == bool, "Erreur: Le 3ème paramètre (following_camera) n'est pas un booléen."


        # Caractéristiques de la boîte de collision
        self.pos = pos
        self.taille = taille
        self.following_camera = following_camera

        # Boîte de collision
        self.collision = pygame.Rect(self.pos[0], self.pos[1], self.taille[0], self.taille[1])


    # ------/ Getters \------

    def get_collisions(self) -> list:
        return [self.collision]

    def get_following_camera(self) -> bool:
        return self.following_camera


    # ------/ Setter \------

    def set_pos(self, new_pos: list) -> None:
        self.pos = new_pos


    # ------/ Méthodes \------

    def update_positions(self, cam_mov: int) -> None:
        """
        Cette méthode permet de déplacer le collider en fonction de la vélocité de la caméra.

        Paramètres:
            - cam_mov (int): Vélocité de la caméra.
        """

        # Test du type de cam_mov
        assert type(cam_mov) == int, "Erreur: Le paramètre donné (cam_mov) n'est pas un nombre entier."

        # Suit le trajet de la caméra comme n'importe quel objet
        if self.following_camera:
            self.pos[0] -= cam_mov

        # Positionnement de la boîte de collision
        self.collision.x = round(self.pos[0])
        self.collision.y = round(self.pos[1])


    def draw(self, screen: pygame.Surface, show_collision: bool = False) -> None: # type: ignore
        """
        Cette méthode permet de dessiner le collider sur l'écran.

        Paramètres:
            - screen (pygame.Surface): L'écran de jeu de pygame.
            - show_collision (bool): Paramètre optionnel permettant d'afficher les boîtes de collision.

        Pré-conditions:
            - screen doit être de type pygame.Surface.
        """

        # Tests des types de variables
        assert type(screen) == pygame.Surface, "Erreur: Le 1er paramètre (screen) n'est pas une surface pygame."
        assert type(show_collision) == bool, "Erreur: Le 2ème paramètre (show_collision) n'est pas un booléen."

        if show_collision:
            pygame.draw.rect(screen, (0, 255, 0), self.collision, 1)



# Classe permettant de créer les points (hérité de la classe Sprite de pygame)
class Point(pygame.sprite.Sprite):

    # ------/ Constructeur \------

    def __init__(self, pos: list, color: str) -> None:
        """
        Constructeur de la classe Point, qui hérite de pygame.sprite.Sprite.

        Attributs à définir:
            - pos (list): Position du point.
            - color (str): Couleur du point.

        Attributs internes:
            - points (dict): Sprite de chaque couleur de point.
            - image (pygame.Surface): Sprite du point (hérité du parent).  
            - rect (pygame.Rect): Rectangle créé à partir du point (hérité du parent).  
        """

        # Test des types des paramètres donnés
        assert type(pos) == list, "Erreur: Le 1er paramètre (pos) n'est pas une liste."
        assert type(color) == str, "Erreur: Le 2ème paramètre (color) n'est pas une chaîne de caractères."


        # On initialise tous les attributs du constructeur parent
        super().__init__()

        # Sprites de chaque point
        minigame_directory = "assets" + sep + "sprites" + sep + "minigames" + sep + "trace_race" + sep
        self.points = {
            "red": pygame.image.load(minigame_directory + "red_point.png"),
            "blue": pygame.image.load(minigame_directory + "blue_point.png"),
            "green": pygame.image.load(minigame_directory + "green_point.png"),
            "yellow": pygame.image.load(minigame_directory + "yellow_point.png")
        }

        # Sprite actuel
        self.image = self.points[color]

        # Rectangle créé à partir du point
        self.rect = pygame.Rect(pos[0], pos[1], self.image.get_rect().w, self.image.get_rect().h)


    # ------/ Méthodes \------

    def update(self, cam_mov: int) -> None:
        """
        Cette méthode permet de déplacer le point en fonction de la vélocité de la caméra.

        Paramètres:
            - cam_mov (int): Vélocité de la caméra.
        """

        # Test du type de cam_mov
        assert type(cam_mov) == int, "Erreur: Le paramètre donné (cam_mov) n'est pas un nombre entier."

        self.rect.x -= cam_mov


    def draw(self, screen: pygame.Surface) -> None: # type: ignore
        """
        Cette méthode permet de dessiner le point sur l'écran.

        Paramètres:
            - screen (pygame.Surface): L'écran de jeu de pygame..
        """

        # Initialisation des facteurs pour la taille de l'écran
        screen_factor = ((screen.get_rect().size[0] / 1280), (screen.get_rect().size[1] / 720))

        # Tests du type de screen
        assert type(screen) == pygame.Surface, "Erreur: Le paramètre donné (screen) n'est pas une surface pygame."

        # On ne dessine pas les points s'il se trouvent en dehors de l'écran (plus d'optimisation)
        if self.rect.x > -10 and self.rect.x < 1280:
            screen.blit(generic.scale_image_by(self.image, screen_factor), (round(self.rect.x * screen_factor[0]), round(self.rect.y * screen_factor[1])))




# Classe du mini-jeu (enfin)
class MiniGame(generic.GenericMiniGame):

    # ------/ Constructeur \------

    def __init__(self, screen: pygame.Surface, clock, fps: int) -> None: # type: ignore
        """
        Constructeur de la classe MiniGame.

        Attributs à définir:
            - screen (pygame.Surface): L'écran de jeu de pygame.
            - clock: L'horloge de pygame (permet de placer une limite de fps au jeu).
            - fps (int): Le nombre de fps maximal du jeu.

        Attributs internes:
            - traces (dict): Tracés de tous les joueurs.

            - camera_pos (list): Position de la caméra.
            - camera_velocity (list): Vélocité/Accélération de la caméra.
            - camera_speed (int): Vitesse de la caméra.

            - bg (pygame.Surface): Image de fond pour le mini-jeu.
            - bg_traces (pygame.Surface): Image des tracés de référence.

            - colliders (list): Liste des boîtes de collision du mini-jeu.
        """

        # Tests du type des paramètres donnés
        assert type(screen) == pygame.Surface, "Erreur: Le 1er paramètre (screen) n'est pas une surface pygame."

        # type(clock) indique que l'horloge est de type "Clock", classe qui n'existe pas naturellement (même pas présente dans les classes de pygame)
        # Voilà la solution que j'ai trouvé pour résoudre ce problème (loin d'être parfaite, mais quand même une vérification)
        assert type(clock).__name__ == "Clock", "Erreur: Le 2ème paramètre (clock) est censé être une horloge pygame."

        assert type(fps) == int, "Erreur: Le 3ème paramètre (fps) est censé être une chaîne de caractères."


        # On initialise tous les attributs du constructeur parent
        super().__init__(screen, clock, fps)

        # Initialisation des tracés
        self.traces = {}

        # Initialisation de la caméra
        self.camera_pos = [0, 0]
        self.camera_velocity = [0, 0]
        self.camera_speed = 0

        # Sprites utilisés dans toute la classe
        minigame_directory = "assets" + sep + "sprites" + sep + "minigames" + sep + "trace_race" + sep

        self.bg = pygame.image.load((minigame_directory + "map.png"))
        self.bg_traces = pygame.image.load((minigame_directory + "traces.png"))

        # La position et la taille des colliders sont basés sur l'image du background
        self.colliders = [Collider([0, 0], [1280, 70], False),
                          Collider([0, 180], [1280, 50], False),
                          Collider([0, 335], [1280, 50], False),
                          Collider([0, 494], [1280, 50], False),
                          Collider([0, 650], [1280, 70], False),
                          Collider([2800, 59], [19, 603], True)]


    # ------/ Méthodes \------

    def game_engine(self, input_vectors: dict, prev_time: float) -> None:
        """
        Cette méthode gère à la fois l'affichage (des éléments principaux) et la physique présente dans le mini-jeu.

        Paramètres:
            - input_vectors (dict): Vecteurs de déplacement de chaque objets en fonction de leurs inputs.
            - prev_time (float): La valeur de temps passé avant l'appel de la méthode.

        Pré-conditions:
            - input_vectors doit uniquement contenir des listes.
        """

        # Tests du type des paramètres donnés
        assert type(input_vectors) == dict, "Erreur: Le 1er paramètre (input_vectors) n'est pas un dictionnaire."
        assert type(prev_time) == float, "Erreur: Le 2ème paramètre (prev_time) n'est pas un nombre flottant."

        # Test de la contenance de input_vectors
        for value in input_vectors.values():
            assert type(value) == list, "Erreur: Le dictionnaire donné doit uniquement contenir des listes."

        # Calcul de la vélocité de la caméra en x
        self.camera_velocity[0] = self.camera_speed * self.delta_time
        self.camera_velocity[0] = round(self.camera_velocity[0])

        # Mouvement de la caméra
        self.camera_pos[0] += self.camera_velocity[0]

        # Affichage du décor
        self.screen.blit(generic.scale_image_by(self.bg, self.screen_factor), (round(-self.camera_pos[0] * self.screen_factor[0]), 0))

        for joueur in self.joueurs:
            # Calcul de la vélocité et des collsisions de chaque joueur
            joueur.calculate_velocity(input_vectors[joueur], self.delta_time)
            joueur.calculate_collisions(self.objets)

            # Calcul de l'animation du joueur actuel (avec delta_time)
            joueur.animate(self.delta_time)

            # On applique le mouvement au joueur
            joueur.apply_velocity(self.camera_velocity[0])

        # Affichage des points colorés (ou du tracé entier à la fin du mini-jeu)
        for trace in self.traces.values():
            if type(trace) != pygame.Surface:
                # On les déplace tous vers la gauche en suivant la caméra
                trace.update(self.camera_velocity[0])

                # On affiche chacun des points crées
                for sprite in trace:
                    sprite.draw(self.screen)
            else:
                self.screen.blit(generic.scale_image_by(trace, self.screen_factor), (round(-self.camera_pos[0] * self.screen_factor[0]), 0))

        # Affichage des tracés de référence
        self.screen.blit(generic.scale_image_by(self.bg_traces, self.screen_factor), (round(-self.camera_pos[0] * self.screen_factor[0]), 0))

        # Affichage des objets sur l'écran
        for objet in self.objets:
            if type(objet) == Collider and objet.get_following_camera():
                objet.update_positions(self.camera_velocity[0])
            objet.draw(self.screen, self.show_collisions)

        # Le parent s'occupe du reste de la méthode
        super().game_engine(input_vectors, prev_time)


    def load(self, param_joueurs: dict) -> None:
        """
        Cette méthode représente la phase de chargement du mini-jeu.

        Paramètres:
            - param_joueurs (dict): Les paramètres de chaque joueur.

        Pré-conditions:
            - param_joueurs doit être composé de 4 éléments (car 4 joueurs).
        """

        # Test du type de param_joueurs
        assert type(param_joueurs) == dict, "Erreur: Le paramètre donné (param_joueurs) n'est pas un dictionnaire."

        # Test de la taille de param_joueurs
        assert len(param_joueurs.keys()) == 4, "Erreur: Le dictionnaire donné ne contient pas assez de joueurs."

        # Liste des noms des joueurs
        liste_joueurs = list(param_joueurs.keys())

        # Ordre aléatoire pour que chaque joueur puisse avoir une couleur aléatoire
        random.shuffle(liste_joueurs)

        # Liste des couleurs disponibles
        liste_couleurs = ["red", "blue", "green", "yellow"]

        # Création des joueurs dans la liste
        for i in range(len(liste_joueurs)):
            nom_joueur = liste_joueurs[i]
            id_joueur = param_joueurs[nom_joueur][0]
            ia_joueur = param_joueurs[nom_joueur][1]
            couleur_joueur = liste_couleurs[i]

            self.joueurs.append(Joueur(nom_joueur, id_joueur, ia_joueur, couleur_joueur))

        # Positionnement des joueurs
        self.joueurs[0].set_pos([600, 38])
        self.joueurs[1].set_pos([600, 170])
        self.joueurs[2].set_pos([600, 324])
        self.joueurs[3].set_pos([600, 486])

        # Initialisation de la liste des objets
        self.objets = self.colliders + self.joueurs

        # Création des tracés
        self.traces = {joueur: pygame.sprite.Group() for joueur in self.joueurs}

        # Textes pour la description du jeu
        description = ["Tracez votre ligne sur le sol",
                       "en suivant le chemin.",
                       "Le tracé qui ressemble le plus au",
                       "chemin d'origine gagne !"]

        # Le parent s'occupe du reste de la méthode
        super().load("assets" + sep + "musics" + sep + "minigames" + sep + "trace_race.ogg", "Trace Race", description)


    def during_game(self) -> None:
        """
        Cette méthode représente la phase de déroulement du mini-jeu.
        """

        # Initialisation des paramètres par défaut de la phase
        running = True
        prev_time = time.time()

        # Lancement du son de sifflet et la musique chargée
        pygame.mixer.Sound("assets" + sep + "sounds" + sep + "minigames" + sep + "start_sifflet.ogg").play()
        pygame.mixer.music.play()

        # Changement de la vitesse de la caméra
        self.camera_speed = 60

        # Initialisation d'un timer caché
        cooldown = 0

        # Boucle principale de cette phase du jeu
        while running:

            # Détection de la fermeture de fenêtre
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.quit = True

                # Changement de taille de la fenêtre
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)

            # Liste des joueurs dessinant (tous ceux avec un get_is_drawing() == True)
            joueurs_dessinant = list(filter(lambda x: x.get_is_drawing(), self.joueurs))

            # On stoppe la caméra si elle touche le bord du terrain et on arrête le mini-jeu
            if self.camera_pos[0] > self.bg.get_rect().w - 1280:
                self.camera_speed = 0
                for joueur in self.joueurs:
                    joueur.set_is_drawing(False)
                running = False

            # On accélère la vitesse de la caméra si tout le monde a fini de dessiner
            elif len(joueurs_dessinant) < 1:
                self.camera_speed = 480

            # Détection des inputs et réinitialisation des vecteurs de déplacement des joueurs
            inputs = pygame.key.get_pressed()
            input_vectors = {joueur: [0, 0] for joueur in self.joueurs}

            # Comportement des joueurs
            for joueur in self.joueurs:
                if joueur.get_is_drawing():
                    if not joueur.get_ia():
                        # Commandes joueur 1
                        if joueur.get_id() == 1:
                            # Selon la version de pygame et de python ça peut changer
                            if inputs[pygame.K_a] or inputs[pygame.K_q]:
                                input_vectors[joueur][0] -= 1
                            if inputs[pygame.K_s]:
                                input_vectors[joueur][1] += 1
                            if inputs[pygame.K_w] or inputs[pygame.K_z]:
                                input_vectors[joueur][1] -= 1
                            if inputs[pygame.K_d]:
                                input_vectors[joueur][0] += 1

                        # Commandes joueur 2
                        elif joueur.get_id() == 2:
                            if inputs[pygame.K_LEFT]:
                                input_vectors[joueur][0] -= 1
                            if inputs[pygame.K_DOWN]:
                                input_vectors[joueur][1] += 1
                            if inputs[pygame.K_UP]:
                                input_vectors[joueur][1] -= 1
                            if inputs[pygame.K_RIGHT]:
                                input_vectors[joueur][0] += 1

                    # Comportement des ia (pathfinding assez mid honnêtement)
                    else:
                        # Masque du crayon de l'ia
                        pen_mask = pygame.mask.from_surface(joueur.get_pen())

                        # Masque des tracés sur le terrain
                        bg_traces_mask = pygame.mask.from_surface(self.bg_traces)

                        # Calcul des offsets pour les opérations avec les masques
                        mask_x_offset = joueur.get_pen_pos()[0] + self.camera_pos[0]
                        mask_y_offset = joueur.get_pen_pos()[1] + self.camera_pos[1]

                        # On détecte si le tracé est proche du bas de la texture du crayon (donc doit aller vers le haut, difficile à expliquer)
                        if bg_traces_mask.overlap(pen_mask, (mask_x_offset, mask_y_offset - 9)):
                            input_vectors[joueur][1] -= 1

                        # On détecte si le tracé est proche du haut de la texture du crayon (donc doit aller vers le bas, difficile à expliquer)
                        elif bg_traces_mask.overlap(pen_mask, (mask_x_offset, mask_y_offset + joueur.get_pen().get_rect().h + 9)):
                            input_vectors[joueur][1] += 1

                        # On détecte si le tracé est se trouve au niveau de la pointe du crayon
                        if bg_traces_mask.overlap(pen_mask, (mask_x_offset + 5, mask_y_offset)):
                            input_vectors[joueur][0] += 1
                        else:
                            # Fait des mouvements aléatoires et prie pour que ça le décoince
                            input_vectors[joueur][random.randint(0, 1)] = random.randint(-1, 1)
                            input_vectors[joueur][random.randint(0, 1)] = random.randint(-1, 1)

            # Utilisation du moteur de jeu et mise à jour du temps passé
            self.game_engine(input_vectors, prev_time)
            prev_time = time.time()

            # Léger délai entre chaque placement de point sinon grosse baisse de performance
            if cooldown - time.time() <= 0:
                for joueur in self.joueurs:
                    if joueur.get_is_drawing():
                        # Chaque point ajouté au tracé est un objet que l'on ajoute dans le groupe de sprites présent dans self.traces
                        self.traces[joueur].add(Point([joueur.get_pen_pos()[0] + 4, joueur.get_pen_pos()[1] + 86], joueur.get_color()))

                # Délai de 0.02s
                cooldown = 0.02 + time.time()

            # Mise à jour de l'écran et limite de fps
            pygame.display.flip()
            self.clock.tick(self.fps)

        # Lancement de l'affichage de fin (si le joueur n'a pas fermé la fenêtre)
        if not self.quit:
            self.end_game()


    def calculate_score(self) -> None:
        """
        Cette méthode permet de calculer les scores de chaque joueur.
        """

        # Initialisation des paramètres par défaut de la phase
        running = True
        prev_time = time.time()

        # Réinitialisation des vecteurs de déplacement des joueurs
        input_vectors = {joueur: [0, 0] for joueur in self.joueurs}

        # Initialisation des tracés dessinés par chaque joueurs
        made_traces = {joueur: pygame.Surface((self.bg_traces.get_rect().w, self.bg_traces.get_rect().h), pygame.SRCALPHA) for joueur in self.joueurs}

        for joueur in self.joueurs:
            for sprite in self.traces[joueur]:
                # On regroupe chaque point dans un seul sprite de tracé
                made_traces[joueur].blit(sprite.image, (sprite.rect.x + self.bg_traces.get_rect().w - 1280, sprite.rect.y))

            # On supprime éventuellement le groupe de sprites pour optimiser les performances
            # et on le remplace par le nouveau tracé
            self.traces[joueur] = made_traces[joueur]

            # On positionne le joueur après la ligne d'arrivée
            joueur.set_pos([230 + self.bg.get_rect().w - 1280, joueur.get_pos()[1]])

        # Masque de chaque tracé de chaque joueur
        made_traces_masks = {joueur: pygame.mask.from_surface(made_traces[joueur]) for joueur in self.joueurs}

        # Masque des tracés sur le terrain
        bg_traces_mask = pygame.mask.from_surface(self.bg_traces)

        # Nombre de pixels repassés par le joueur
        # (overlap_area renvoie le nombre de pixels qui se superposent entre deux masques)
        nb_pixels_joueurs = {joueur: made_traces_masks[joueur].overlap_area(bg_traces_mask, (0, 0)) for joueur in self.joueurs}

        # On convertit l'image des tracés du terrain en tableau facilement compréhensible par le code
        bg_traces_tab = pygame.PixelArray(self.bg_traces)

        # Ou sinon je pouvais juste mettre nb_pixels_ligne = 7230 directement mais c'est plus intuitif de le calculer nous même
        nb_pixels_ligne = 0

        # Sur toute les dimensions de l'image:
        for i in range(self.bg_traces.get_rect().w):
            for j in range(self.bg_traces.get_rect().h):

                # On compte chaque pixel qui n'est pas vide
                if bg_traces_tab[i, j] != 0:
                    nb_pixels_ligne += 1

        # On suprime le tableau de pixel (sinon on ne peut plus afficher l'image)
        bg_traces_tab.close()

        # On divise par 4 parce qu'il y a 4 lignes dans l'image
        nb_pixels_ligne = round(nb_pixels_ligne / 4)

        # Un énième dictionnaire par compréhension pour stocker les pourcentages de réussite de chaque joueur
        pourcentages = {joueur: round((nb_pixels_joueurs[joueur] / nb_pixels_ligne) * 100, 1) for joueur in self.joueurs}

        # On utilise toujours la méthode simple: on trie automatiquement les clés du dictionnaire
        sorted_pourcentages = sorted(pourcentages, key=pourcentages.get, reverse=True)

        # On s'en sert pour directement créer le classement
        for i in range(len(sorted_pourcentages)):
            joueur = sorted_pourcentages[i]
            self.classement[joueur.get_perso()] = i + 1

        # Réinitialisation de la caméra
        self.camera_pos = [0, 0]
        self.camera_speed = 550

        # Sprite du fond des pourcentages
        pourcent_back = pygame.image.load("assets" + sep + "sprites" + sep + "minigames" + sep + "trace_race" + sep + "pourcent_back.png")

        # Les pourcentages qui seront utilisés pour l'affichage
        draw_pourcentages = {joueur: 0 for joueur in self.joueurs}

        # La méthode dure 5 secondes
        timer = 5 + time.time()

        # Roulements de tambour
        pygame.mixer.Sound("assets" + sep + "sounds" + sep + "minigames" + sep + "trace_race" + sep + "drum_roll.ogg").play()

        # Boucle principale de cette phase du jeu
        while running:

            # Détection de la fermeture de fenêtre
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.quit = True

                # Changement de taille de la fenêtre
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)

            # On arrête la caméra quand elle touche le bord du terrain
            if self.camera_pos[0] > self.bg.get_rect().w - 1280 - 500:
                self.camera_speed = 0

            # Arrêt de la méthode à la fin du temps imparti
            if timer - time.time() <= 0:
                running = False

            # Utilisation du moteur de jeu et mise à jour du temps passé
            self.game_engine(input_vectors, prev_time)
            prev_time = time.time()

            # Affichage des scores
            pourcent_pos_y = 90
            for joueur in self.joueurs:
                # La formule utilisé ici permet d'avoir a peu près le même temps d'attente pour n'importe quel pourcentage
                if draw_pourcentages[joueur] < pourcentages[joueur]:
                    draw_pourcentages[joueur] += (pourcentages[joueur] / 4) * self.delta_time
                else:
                    draw_pourcentages[joueur] = pourcentages[joueur]

                # Affichage des pourcentages
                self.screen.blit(generic.scale_image_by(pourcent_back, (4 * self.screen_factor[0], 4 * self.screen_factor[1])), (round(1000 * self.screen_factor[0]), round(pourcent_pos_y * self.screen_factor[1])))
                pourcentage_text = self.game_font.render(str(round(draw_pourcentages[joueur], 1)) + "%", (255, 255, 255))
                pourcentage_text_scaled = generic.scale_image_by(pourcentage_text[0], self.screen_factor)

                # Affichage du pourcentage
                self.screen.blit(pourcentage_text_scaled, (round(1013 * self.screen_factor[0]), round((pourcent_pos_y + 20) * self.screen_factor[1])))

                # Augmentation du décalage après chaque joueur
                pourcent_pos_y += 150

            # Mise à jour de l'écran et limite de fps
            pygame.display.flip()
            self.clock.tick(self.fps)

        # Le parent s'occupe de finir le mini-jeu
        super().calculate_score()