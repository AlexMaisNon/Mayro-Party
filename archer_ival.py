# Fait par Alexandre

# ------/ Importations des bibliothèques \------

import pygame
import pygame.freetype
import random
import time
from os import sep

import assets.generic as generic


# ------/ Classes \------

# Classe du joueur
class Joueur(generic.GenericJoueur):

    # ------/ Constructeur \------

    def __init__(self, perso: str, id: int, ia: bool, type_joueur: str) -> None:
        """
        Constructeur de la classe Joueur.

        Attributs à définir:
            - perso (str): Personnage choisit par le joueur.
            - id (int): id du joueur qui indique sa position dans l'ordre de jeu.
            - ia (bool): Indique si le joueur est une ia ou un joueur lambda.
            - type_joueur (str): Si le joueur est en solo ou en équipe (solo ou panneau) (exclusif à ce mini-jeu).

        Attributs internes:
            - speed (int): Vitesse du joueur.
            - rotation (str): Rotation du joueur.
            - dead (bool): Définit si le joueur est mort ou non.

            - move_cooldown (float): Un délai aléatoire pour chaque mouvement d'ia.

            - panneau (pygame.Surface): Sprite du panneau.
            - guns (list): Sprites du pistolet.
            - gun (pygame.Surface): Sprite actuel du pistolet.
            - sprites (dict): Sprites du joueurs.
            - sprite (pygame.Surface): Sprite actuel du joueur.
            - sprite_pos (list): Position du sprite (du pistolet si solo ou du joueur sinon).

            - collision (pygame.Rect ou None): Boîte de collision du joueur.

            - shadow (pygame.Surface): Sprite de l'ombre du joueur.

            - death_sound (pygame.mixer.Sound): Son de mort du joueur.
            - shot_sound (pygame.mixer.Sound): Son de tir du pistolet.

            - shot_cooldown (float): Un délai entre chaque tir de pistolet.
        """

        # Tests du type des paramètres donnés
        assert type(type_joueur) == str, "Erreur: Le 4ème paramètre (type_joueur) est censé être une chaîne de caractères."


        # On initialise tous les attributs du constructeur parent
        super().__init__(perso, id, ia)

        # Définition du joueur
        self.type_joueur = type_joueur

        # Caractéristiques principales du joueur
        self.speed = 70 if self.type_joueur == "panneau" else 200
        self.rotation = "left"
        self.dead = False

        # Un timer qui servira à faire se déplacer les ias aléatoirement
        self.move_cooldown = 0.0

        # Sprite du panneau
        self.panneau = generic.scale_image_by(pygame.image.load("assets" + sep + "sprites" + sep + "minigames" + sep + "archer_ival" + sep + "panneau_joueur.png"), 2)

        # Sprites pour le fusil
        self.guns = [pygame.image.load("assets" + sep + "sprites" + sep + "minigames" + sep + "archer_ival" + sep + "gun.png"),
                     pygame.image.load("assets" + sep + "sprites" + sep + "minigames" + sep + "archer_ival" + sep + "gun_shot.png")]
        self.gun = self.guns[0]

        # Définition des sprites automatiquement (pour les joueurs / ia)
        self.sprites = {
            "panneau": {
                "left": generic.scale_image_by(pygame.image.load(self.sprites_directory + "walk_left2.png"), 2),
                "right": generic.scale_image_by(pygame.image.load(self.sprites_directory + "walk_right2.png"), 2)
            },
            "solo": [generic.scale_image_by(pygame.image.load(self.sprites_directory + "archer" + str(i) + ".png"), 8) for i in range(8)]}

        # Changement du sprite actuel en fonction du type du joueur
        if self.type_joueur == "panneau":
            self.sprite = self.sprites["panneau"]["left"]

            # Boîte de collision du personnage (si en équipe)
            self.collision = pygame.Rect(0, 0, self.panneau.get_rect().w, self.panneau.get_rect().h)
        else:
            self.sprite = self.sprites["solo"][0]

            # Boîte de collision du personnage (si en solo, n'a pas de collision)
            self.collision = None

        # Initialisation de la position du sprites
        self.sprite_pos = list(self.pos)

        # Paramètres de l'ombre pour le joueur solo uniquement
        if self.type_joueur == "solo":
            self.shadow = generic.scale_image_by(pygame.image.load(self.sprites_directory + "shadow.png"), 8)
        else:
            self.shadow = None

        # Initialisation des sons
        self.death_sound = pygame.mixer.Sound("assets" + sep + "sounds" + sep + self.perso + sep + "death.ogg")

        # Caractéristiques du tir
        self.shot_sound = pygame.mixer.Sound("assets" + sep + "sounds" + sep + "minigames" + sep + "archer_ival" + sep + "shot.ogg")
        self.shot_cooldown = 0.0


    # ------/ Getters \------

    def get_type_joueur(self) -> str:
        return self.type_joueur

    def get_rotation(self) -> str:
        return self.rotation

    def get_dead(self) -> bool:
        return self.dead

    def get_move_cooldown(self) -> float:
        return self.move_cooldown

    def get_sprite_pos(self) -> list:
        return self.sprite_pos

    def get_death_sound(self) -> pygame.mixer.Sound: # type: ignore
        return self.death_sound


    # ------/ Setters \------

    def set_rotation(self, new_rotation: str) -> None:
        self.rotation = new_rotation

    def set_dead(self, new_dead: bool) -> None:
        self.dead = new_dead

    def set_move_cooldown(self, new_move_cooldown: float) -> None:
        self.move_cooldown = new_move_cooldown


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

        # Le parent s'occupe du calcul en x et y
        super().calculate_velocity(direction, delta_time)

        # On réinitialise la vélocité en y (car il ne peut pas se déplacer en y)
        self.velocity[1] = 0


    def calculate_collisions(self, objets: list) -> None:
        """
        Cette méthode permet de calculer les collisions avec le joueur.

        Paramètres:
            - objets (list): Liste d'objets avec lesquels le joueur doit calculer les collisions.

        Pré-conditions:
            - objets doit contenir seulement des objets de type Joueur, Ennemi ou Fleche.
        """

        # Test du type de objets
        assert type(objets) == list, "Erreur: Le paramètre donné (objets) n'est pas une liste."

        # Tests des éléments de objets
        for elem in objets:
            assert type(elem) == Joueur or type(elem) == Ennemi or type(elem) == Fleche, "Erreur: La liste doit être seulement composée d'objets."

        # Calcul des collisions pour chaque objets
        for objet in objets:
            # Pas mal de tests pour éviter de collisionner avec des élément indésirables
            if objet != self and type(objet) != Fleche and not objet.get_dead():
                # On ne calcule pas si le joueur est le joueur solo
                if self.collision != None:
                    # Pas de rect_x parce que le joueur est bloqué sur l'axe x
                    rect_x = pygame.Rect(round(self.collision.x + self.velocity[0]), self.collision.y, self.collision.w, self.collision.h)

                    # On stoppe la vélocité du joueur si il collisionne avec une boîte de collision
                    for collision in objet.get_collisions():
                        if collision != None and rect_x.colliderect(collision):
                            self.velocity[0] = 0.0


    def apply_velocity(self) -> None:
        """
        Cette méthode permet d'appliquer la vélocité à la position et à d'autres paramètres du joueur.
        """

        # Le parent applique l'accélération à la position
        super().apply_velocity()

        # Applications différentes selon le type du joueur
        if self.type_joueur == "panneau":
            # La position du joueur est bloquée entre ces deux intervalles
            self.pos[0] = max(300, min(self.pos[0], 920))

            # On positionne le sprite du joueur sur le panneau
            self.sprite_pos[0] = round(self.pos[0] - (self.sprite.get_rect().w - self.panneau.get_rect().w) / 2)
            self.sprite_pos[1] = round(self.pos[1] - self.sprite.get_rect().bottom + self.panneau.get_rect().h / 2) + 35

            # On positionne la boîte de collision par rapport à la position du joueur
            self.collision.x = round(self.pos[0])
            self.collision.y = round(self.pos[1])

        else:
            # La position du joueur est bloquée entre ces deux intervalles
            self.pos[0] = max(150, min(self.pos[0], 900))

            # On positionne ici le sprite du pistolet par rapport au joueur
            self.sprite_pos[0] = round(self.pos[0] + self.sprite.get_rect().w - self.gun.get_rect().w)
            self.sprite_pos[1] = round(self.pos[1] + 74)

            # On positionne l'ombre par rapport au personnage
            self.shadow_pos[0] = round(self.pos[0] + (self.sprite.get_rect().w - self.shadow.get_rect().w) / 2)
            self.shadow_pos[1] = round(self.pos[1] + self.sprite.get_rect().h - self.shadow.get_rect().h) + 10


    def shoot(self, objets: list) -> None:
        """
        Cette méthode permet au joueur solo de tirer.

        Paramètres:
            - objets (list): Liste d'objets avec lesquels le joueur doit calculer les collisions.

        Pré-conditions:
            - objets doit contenir seulement des objets de type Joueur, Ennemi ou Fleche.
        """

        # Test du type de objets
        assert type(objets) == list, "Erreur: Le paramètre donné (objets) n'est pas une liste."

        # Tests des éléments de objets
        for elem in objets:
            assert type(elem) == Joueur or type(elem) == Ennemi or type(elem) == Fleche, "Erreur: La liste doit être seulement composée d'objets."

        # Ne tire uniquement si le délai est depassé
        if self.shot_cooldown - time.time() <= 0:

            # Joue le son et change le sprite actuel du pistolet
            self.shot_sound.play()
            self.gun = self.guns[1]

            # Création du projectile (à la base censé être une flèche) dans la liste d'objets
            objets.append(Fleche([self.sprite_pos[0] + 15.0, self.sprite_pos[1] + 15.0]))

            # Applique 2s de délai
            self.shot_cooldown = 2 + time.time()


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

        # Ne change pas le sprite s'il n'a pas de rotation (ia)
        if self.rotation != None:
            # L'animation change en fonction du type du joueur
            if self.type_joueur == "solo":
                # L'animation reste figée si le joueur est immobile
                if self.velocity[0] == 0 and self.velocity[1] == 0:
                    self.frame = 0.0

                # self.frame ne doit pas dépasser l'indice de la liste de sprites
                if self.frame > len(self.sprites["solo"]) - 1:
                    self.frame = 0

                # Changement du sprite actuel
                self.sprite = self.sprites["solo"][round(self.frame)]

                # Le parent s'occupe de changer la frame en fonction de la vitesse
                super().animate(delta_time, 12)
            else:
                # Changement du sprite actuel
                self.sprite = self.sprites["panneau"][self.rotation]

        # Réinitialise le sprite du pistolet après un cours délai
        if self.shot_cooldown - time.time() <= 1.9:
            self.gun = self.guns[0]


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

        # Affiche le joueur uniquement s'il est vivant
        if not self.dead:
            # L'affichage change en fonction du type du joueur
            if self.type_joueur == "solo":
                # Affichage des sprites à leur positions respectives
                screen.blit(generic.scale_image_by(self.shadow, screen_factor), (round(self.shadow_pos[0] * screen_factor[0]), round(self.shadow_pos[1] * screen_factor[1])))
                screen.blit(generic.scale_image_by(self.gun, screen_factor), (round(self.sprite_pos[0] * screen_factor[0]), round(self.sprite_pos[1] * screen_factor[1])))
                screen.blit(generic.scale_image_by(self.sprite, screen_factor), (round(self.pos[0] * screen_factor[0]), round(self.pos[1] * screen_factor[1])))
            else:
                # Affichage des sprites à leur positions respectives
                screen.blit(generic.scale_image_by(self.panneau, screen_factor), (round(self.pos[0] * screen_factor[0]), round(self.pos[1] * screen_factor[1])))
                screen.blit(generic.scale_image_by(self.sprite, screen_factor), (round(self.sprite_pos[0] * screen_factor[0]), round(self.sprite_pos[1] * screen_factor[1])))



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
            - velocity (list): Vélocité/Accélération de l'ennemi.
            - speed (int): Vitesse de l'ennemi.
            - rotation (str): Rotation de l'ennemi.
            - dead (bool): Définit si l'ennemi est mort ou non.

            - move_cooldown (float): Un délai aléatoire pour chaque mouvement de l'ennemi.

            - sprites (dict): Sprites de l'ennemi.
            - sprite (pygame.Surface): Sprite actuel de l'ennemi.

            - collision (pygame.Rect ou None): Boîte de collision de l'ennemi.

            - death_sound (pygame.mixer.Sound): Son de mort de l'ennemi.
        """

        # Tests du type des paramètres donnés
        assert type(perso) == str, "Erreur: Le paramètre (perso) est censé être une chaîne de caractères."


        # Définition de l'ennemi
        self.perso = perso

        # Caractéristiques principales (stats)
        self.pos = [0.0, 0.0]
        self.velocity = [0.0, 0.0]
        self.speed = 70
        self.rotation = "left"
        self.dead = False

        # Un timer qui servira à faire se déplacer l'ennemi aléatoirement
        self.move_cooldown = 0.0

        # Emplacement des sprites du mini-jeu
        sprites_directory = "assets" + sep + "sprites" + sep + "minigames" + sep + "archer_ival" + sep

        # Définition des sprites de l'ennemi
        self.sprites = {
            "left": generic.scale_image_by(pygame.image.load(sprites_directory + "panneau_" + self.perso + "_left.png"), 2),
            "right": generic.scale_image_by(pygame.image.load(sprites_directory + "panneau_" + self.perso + "_right.png"), 2)
        }

        # Initialisation du sprite actuel
        self.sprite = self.sprites["left"]

        # Boîte de collision de l'ennemi
        self.collision = pygame.Rect(0, 0, self.sprite.get_rect().w, self.sprite.get_rect().h)

        # Initialisation du son de mort
        self.death_sound = pygame.mixer.Sound("assets" + sep + "sounds" + sep + "minigames" + sep + "archer_ival" + sep + self.perso + "_death.ogg")


    # ------/ Getters \------

    def get_rotation(self) -> str:
        return self.rotation

    def get_collisions(self) -> list:
        return [self.collision]

    def get_dead(self) -> bool:
        return self.dead

    def get_death_sound(self) -> pygame.mixer.Sound: # type: ignore
        return self.death_sound

    def get_move_cooldown(self) -> float:
        return self.move_cooldown


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

    def calculate_velocity(self, direction: list, delta_time: float) -> None:
        """
        Cette méthode permet de calculer la vélocité de l'ennemi (exactement la même méthode que dans la classe Joueur).

        Paramètres:
            - direction (list): Direction sous forme de vecteur dans laquelle l'ennemi se déplace.
            - delta_time (float): Valeur calculé dans le moteur de jeu qui permet l'indépendance de la vitesse au framerate.

        Pré-conditions:
            - direction doit être compris entre -1 et 1.
        """

        # Test des types de variables
        assert type(direction) == list, "Erreur: Le 1er paramètre (direction) n'est pas une liste."
        assert type(delta_time) == float, "Erreur: Le 2ème paramètre (delta_time) n'est pas un nombre flottant."

        # Test des valeurs dans direction
        for elem in direction:
            assert elem >= -1 and elem <= 1, "Erreur: Une des valeurs dans la direction donnée n'est pas valide."

        # On change seulement la coordonnée x car l'ennemi ne peut pas se déplacer en y
        self.velocity[0] += direction[0] * self.speed * delta_time


    def calculate_collisions(self, objets: list) -> None:
        """
        Cette méthode permet de calculer les collisions avec l'ennemi (très similaire avec la même méthode dans la classe Joueur).

        Paramètres:
            - objets (list): Liste d'objets avec lesquels l'ennemi doit calculer les collisions.

        Pré-conditions:
            - objets doit contenir seulement des objets de type Joueur, Ennemi ou Fleche.
        """

        # Test du type de objets
        assert type(objets) == list, "Erreur: Le paramètre donné (objets) n'est pas une liste."

        # Tests des éléments de objets
        for elem in objets:
            assert type(elem) == Joueur or type(elem) == Ennemi or type(elem) == Fleche, "Erreur: La liste doit être seulement composée d'objets."

        # Calcul des collisions pour chaque objets
        for objet in objets:
            # Pas mal de tests pour éviter de collisionner avec des élément indésirables
            if objet != self and type(objet) != Fleche and not objet.get_dead():
                # Pas de rect_x parce que l'ennemi est bloqué sur l'axe x
                rect_x = pygame.Rect(round(self.collision.x + self.velocity[0]), self.collision.y, self.collision.w, self.collision.h)

                # On stoppe la vélocité du joueur si il collisionne avec une boîte de collision
                for collision in objet.get_collisions():
                    if collision != None and rect_x.colliderect(collision):
                        self.velocity[0] = 0.0


    def apply_velocity(self) -> None:
        """
        Cette méthode permet d'appliquer la vélocité à la position et à d'autres paramètres de l'ennemi.
        """

        # On ajoute la vélocité à la position du personnage (pas de vélocity[1] car se déplace qu'en x)
        self.pos[0] += self.velocity[0]

        # La position de l'ennemi est bloquée entre ces deux intervalles
        self.pos[0] = max(300, min(self.pos[0], 920))

        # On positionne la boîte de collision par rapport à la position de l'ennemi
        self.collision.x = round(self.pos[0])
        self.collision.y = round(self.pos[1])

        # On réinitialise la vélocité (sinon effet Asteroids (le personnage glisse indéfiniment))
        self.velocity = [0.0, 0.0]


    def animate(self) -> None:
        """
        Cette méthode permet d'animer le sprite de l'ennemi.
        """

        # Ne change pas le sprite s'il n'a pas de rotation
        if self.rotation != None:
            self.sprite = self.sprites[self.rotation]


    def draw(self, screen: pygame.Surface, show_collision: bool = False) -> None: # type: ignore
        """
        Cette méthode permet de dessiner le joueur sur l'écran.

        Paramètres:
            - screen (pygame.Surface): L'écran de jeu de pygame.
            - show_collision (bool): Paramètre optionnel permettant d'afficher les boîtes de collision.

        Pré-conditions:
            - screen doit être de type pygame.Surface.
        """

        # Tests des type de variables
        assert type(screen) == pygame.Surface, "Erreur: Le 1er paramètre (screen) n'est pas une surface pygame."
        assert type(show_collision) == bool, "Erreur: Le 2ème paramètre (show_collision) n'est pas un booléen."

        # Initialisation des facteurs pour la taille de l'écran
        screen_factor = ((screen.get_rect().size[0] / 1280), (screen.get_rect().size[1] / 720))

        # Affiche l'ennemi uniquement s'il est vivant
        if not self.dead:
            screen.blit(generic.scale_image_by(self.sprite, screen_factor), (round(self.pos[0] * screen_factor[0]), round(self.pos[1] * screen_factor[1])))

            # Paramètre de débug pour afficher les collisions
            if show_collision:
                pygame.draw.rect(screen, (0, 255, 0), self.collision, 1)



# Classe de la flèche (ou de la balle plutôt, la classe s'appelle Fleche car c'était censé être une flèche et un arc à la base)
class Fleche:

    # ------/ Constructeur \------

    def __init__(self, pos: list) -> None:
        """
        Constructeur de la classe Fleche.

        Attributs à définir:
            - pos (list): Position de la flèche.

        Attributs internes:
            - velocity (list): Vélocité/Accélération de la flèche.
            - speed (int): Vitesse de la flèche.

            - sprite (pygame.Surface): Sprite actuel de la flèche.

            - collision (pygame.Rect ou None): Boîte de collision de la flèche.
        """

        # Tests du type des paramètres donnés
        assert type(pos) == list, "Erreur: Le paramètre (pos) est censé être une liste."


        # Caractéristiques de la flèche
        self.pos = pos
        self.velocity = [0.0, 0.0]
        self.speed = 200

        # Initialisation du sprite de la flèche
        self.sprite = generic.scale_image_by(pygame.image.load("assets" + sep + "sprites" + sep + "minigames" + sep + "archer_ival" + sep + "fleche.png"), 2)

        # Boîte de collision de la flèche
        self.collision = pygame.Rect(0, 0, self.sprite.get_rect().w, self.sprite.get_rect().h - 20)


    # ------/ Getters \------

    def get_pos(self) -> list:
        return self.pos

    def get_collisions(self) -> list:
        return [self.collision]


    # ------/ Méthodes \------

    def calculate_velocity(self, direction: list, delta_time: float) -> None:
        """
        Cette méthode permet de calculer la vélocité de la flèche (méthode similaire avec celles des classes précédentes).

        Paramètres:
            - direction (list): Direction sous forme de vecteur dans laquelle la flèche se déplace.
            - delta_time (float): Valeur calculé dans le moteur de jeu qui permet l'indépendance de la vitesse au framerate.

        Pré-conditions:
            - direction doit être compris entre -1 et 1.
        """

        # Test des types de variables
        assert type(direction) == list, "Erreur: Le 1er paramètre (direction) n'est pas une liste."
        assert type(delta_time) == float, "Erreur: Le 2ème paramètre (delta_time) n'est pas un nombre flottant."

        # Test des valeurs dans direction
        for elem in direction:
            assert elem >= -1 and elem <= 1, "Erreur: Une des valeurs dans la direction donnée n'est pas valide."

        # On change seulement la coordonnée y car la flèche ne peut pas se déplacer en x
        self.velocity[1] += direction[1] * self.speed * delta_time


    def calculate_collisions(self, objets: list) -> None:
        """
        Cette méthode permet de calculer les collisions avec la flèche (méthode similaire avec celles des classes précédentes).

        Paramètres:
            - objets (list): Liste d'objets avec lesquels la flèche doit calculer les collisions.

        Pré-conditions:
            - objets doit contenir seulement des objets de type Joueur, Ennemi ou Fleche.
        """

        # Test du type de objets
        assert type(objets) == list, "Erreur: Le paramètre donné (objets) n'est pas une liste."

        # Tests des éléments de objets
        for elem in objets:
            assert type(elem) == Joueur or type(elem) == Ennemi or type(elem) == Fleche, "Erreur: La liste doit être seulement composée d'objets."

        # Calcul des collisions pour chaque objets
        for objet in objets:
            # Pas mal de tests pour éviter de collisionner avec des élément indésirables
            if objet != self and type(objet) != Fleche and not objet.get_dead():
                # Pas de rect_x parce que la flèche est bloquée sur l'axe y
                rect_y = pygame.Rect(self.collision.x, round(self.collision.y + self.velocity[1]), self.collision.w, self.collision.h)

                # On détecte la collision de l'objet
                for collision in objet.get_collisions():
                    # Ne collisionne pas avec le joueur solo
                    if collision != None and rect_y.colliderect(collision):
                        # On tue l'objet et on joue le son de mort
                        objet.set_dead(True)
                        objet.get_death_sound().play()

                        # On supprime la flèche de la liste d'objets
                        if self in objets:
                            objets.remove(self)


    def apply_velocity(self) -> None:
        """
        Cette méthode permet d'appliquer la vélocité à la position et à d'autres paramètres de la flèche.
        """

        # On ajoute la vélocité à la position de la flèche (pas de vélocity[0] car se déplace qu'en y)
        self.pos[1] += self.velocity[1]

        # On positionne la boîte de collision par rapport à la position de la flèche
        self.collision.x = round(self.pos[0])
        self.collision.y = round(self.pos[1] + self.sprite.get_rect().bottom)

        # On réinitialise la vélocité (sinon effet Asteroids (la flèche glisse indéfiniment et contre le principe de vélocité))
        self.velocity = [0.0, 0.0]


    def draw(self, screen: pygame.Surface, show_collision: bool = False) -> None: # type: ignore
        """
        Cette méthode permet de dessiner la flèche sur l'écran.

        Paramètres:
            - screen (pygame.Surface): L'écran de jeu de pygame.
            - show_collision (bool): Paramètre optionnel permettant d'afficher les boîtes de collision.

        Pré-conditions:
            - screen doit être de type pygame.Surface.
        """

        # Tests des type de variables
        assert type(screen) == pygame.Surface, "Erreur: Le 1er paramètre (screen) n'est pas une surface pygame."
        assert type(show_collision) == bool, "Erreur: Le 2ème paramètre (show_collision) n'est pas un booléen."

        # Initialisation des facteurs pour la taille de l'écran
        screen_factor = ((screen.get_rect().size[0] / 1280), (screen.get_rect().size[1] / 720))

        # Affichage de la flèche
        screen.blit(generic.scale_image_by(self.sprite, screen_factor), (round(self.pos[0] * screen_factor[0]), round(self.pos[1] * screen_factor[1])))

        # Paramètre de débug pour afficher les collisions
        if show_collision:
            pygame.draw.rect(screen, (0, 255, 0), self.collision, 1)



# Classe du mini-jeu
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
            - entities (list): Liste des entités.
            - timer (float): Durée du mini-jeu.

            - bg (pygame.Surface): Image de fond pour le mini-jeu.
            - nappe (pygame.Surface): Image de nappe jaune pour le mini-jeu.
            - mur_briques (pygame.Surface): Image d'un mur de briques pour le mini-jeu.
            - buisson (pygame.Surface): Image d'un buisson pour le mini-jeu.
        """

        # Tests du type des paramètres donnés
        assert type(screen) == pygame.Surface, "Erreur: Le 1er paramètre (screen) n'est pas une surface pygame."

        # type(clock) indique que l'horloge est de type "Clock", classe qui n'existe pas naturellement (même pas présente dans les classes de pygame)
        # Voilà la solution que j'ai trouvé pour résoudre ce problème (loin d'être parfaite, mais quand même une vérification)
        assert type(clock).__name__ == "Clock", "Erreur: Le 2ème paramètre (clock) est censé être une horloge pygame."

        assert type(fps) == int, "Erreur: Le 3ème paramètre (fps) est censé être une chaîne de caractères."


        # On initialise tous les attributs du constructeur parent
        super().__init__(screen, clock, fps)

        # Initialisation des paramètres pour la partie gameplay
        self.entities = []
        self.timer = 30

        # Emplacement des sprites du mini-jeu
        minigame_directory = "assets" + sep + "sprites" + sep + "minigames" + sep + "archer_ival" + sep

        # Sprites utilisés dans la classe
        self.bg = pygame.image.load(minigame_directory + "background.png")
        self.nappe = pygame.image.load(minigame_directory + "nappe_jaune.png")
        self.mur_briques = pygame.image.load(minigame_directory + "mur_de_briques.png")
        self.buisson = pygame.image.load(minigame_directory + "buisson.png")


    # ------/ Méthodes \------

    def game_engine(self, input_vectors: dict, prev_time: float) -> tuple:
        """
        Cette méthode gère à la fois l'affichage (des éléments principaux) et la physique présente dans le mini-jeu.

        Paramètres:
            - input_vectors (dict): Vecteurs de déplacement de chaque objets en fonction de leurs inputs.
            - prev_time (float): La valeur de temps passé avant l'appel de la méthode.

        Returns:
            - tuple: Les multiplicateurs pour la taille de l'écran.

        Pré-conditions:
            - input_vectors doit uniquement contenir des listes.
        """

        # Tests du type des paramètres donnés
        assert type(input_vectors) == dict, "Erreur: Le 1er paramètre (input_vectors) n'est pas un dictionnaire."
        assert type(prev_time) == float, "Erreur: Le 2ème paramètre (prev_time) n'est pas un nombre flottant."

        # Test de la contenance de input_vectors
        for value in input_vectors.values():
            assert type(value) == list, "Erreur: Le dictionnaire donné doit uniquement contenir des listes."

        # On affiche les sprites du jeu dans un ordre d'affichage prédéfini
        self.screen.blit(generic.scale_image_by(self.bg, self.screen_factor), (0, 0))

        # Affichage de buissons de tailles variables
        self.screen.blit(generic.scale_image_by(self.buisson, (4 * self.screen_factor[0], 4 * self.screen_factor[1])), (round(370 * self.screen_factor[0]), round(380 * self.screen_factor[1])))
        self.screen.blit(generic.scale_image_by(self.buisson, (5 * self.screen_factor[0], 5 * self.screen_factor[1])), (round(900 * self.screen_factor[0]), round(370 * self.screen_factor[1])))
        self.screen.blit(generic.scale_image_by(self.buisson, (6 * self.screen_factor[0], 6 * self.screen_factor[1])), (round(80 * self.screen_factor[0]), round(360 * self.screen_factor[1])))

        self.screen.blit(generic.scale_image_by(self.nappe, (5 * self.screen_factor[0], 5 * self.screen_factor[1])), (round(159 * self.screen_factor[0]), round(460 * self.screen_factor[1])))
        self.screen.blit(generic.scale_image_by(self.mur_briques, (3 * self.screen_factor[0], 3 * self.screen_factor[1])), (round(275 * self.screen_factor[0]), round(340 * self.screen_factor[1])))

        # Calcul de la physique de chaque objet
        for objet in self.objets:
            # Calcul de la vélocité et des collsisions de chaque objet
            objet.calculate_velocity(input_vectors[objet], self.delta_time)
            objet.calculate_collisions(self.objets)

            # Calcul de l'animation de l'objet actuel (avec la valeur de delta_time si nécessaire)
            if objet in self.joueurs:
                objet.animate(self.delta_time)
            elif objet in self.entities:
                objet.animate()

            # On applique le mouvement à l'objet
            objet.apply_velocity()

            # On affiche tous les objets sauf le joueur solo (le 1er joueur de la liste self.joueurs)
            if objet != self.joueurs[0]:
                objet.draw(self.screen, self.show_collisions)

            # On supprime toutes les flèches qui partent trop loin en hauteur
            if type(objet) == Fleche:
                if objet.get_pos()[1] < 250:
                    if objet in self.objets:
                        self.objets.remove(objet)

        # On affiche le joueur solo à la fin pour la priorité d'affichage
        self.joueurs[0].draw(self.screen, self.show_collisions)

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

        # Ordre aléatoire pour que chaque joueur puisse avoir un rôle aléatoire
        random.shuffle(liste_joueurs)

        # Création des joueurs dans la liste
        for i in range(len(liste_joueurs)):
            nom_joueur = liste_joueurs[i]
            id_joueur = param_joueurs[nom_joueur][0]
            ia_joueur = param_joueurs[nom_joueur][1]

            # Le 1er joueur de la liste est le joueur solo, sinon les autres sont des panneaux
            if i == 0:
                self.joueurs.append(Joueur(nom_joueur, id_joueur, ia_joueur, "solo"))
            else:
                self.joueurs.append(Joueur(nom_joueur, id_joueur, ia_joueur, "panneau"))

        # Initialisation de la liste des entités
        self.entities = list(self.joueurs)

        # Création / positionnement des ennemis dans la liste
        self.entities.append(Ennemi("boo"))
        self.entities[-1].set_pos([500, 216])

        self.entities.append(Ennemi("thwomp"))
        self.entities[-1].set_pos([700, 216])

        # Positionnement des joueurs
        self.joueurs[0].set_pos([500, 400])
        self.joueurs[1].set_pos([400, 216])
        self.joueurs[2].set_pos([600, 216])
        self.joueurs[3].set_pos([800, 216])

        # Initialisation de la liste des objets
        self.objets = list(self.entities)

        # Textes pour la description du jeu
        description = ["Joueur solo:",
                       "Tirez sur les joueurs adverses",
                       "avec ESPACE/ENTRÉE !",
                       "",
                       "Joueurs en équipe:",
                       "Esquivez les tirs et survivez le",
                       "plus longtemps possible !"]

        # Le parent s'occupe du reste de la méthode
        super().load("assets" + sep + "musics" + sep + "minigames" + sep + "archer_ival.ogg", "Archer-Ival", description)


    def during_game(self) -> None:
        """
        Cette méthode représente la phase de déroulement du mini-jeu.
        """

        # Initialisation des paramètres par défaut de la phase
        running =  True
        prev_time = time.time()

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

            # Liste des joueurs vivants (tous ceux avec un get_dead() == False)
            joueurs_vivants = list(filter(lambda x: not x.get_dead(), self.joueurs))

            # Le mini-jeu s'arrête si le timer s'arrête ou qu'il ne reste plus de joueurs à part le joueur solo
            if self.timer - time.time() <= 0:
                running = False
            elif(len(joueurs_vivants) <= 1):
                running = False

            # Détection des inputs et réinitialisation des vecteurs de déplacement des objets
            inputs = pygame.key.get_pressed()
            input_vectors = {objet: [0, 0] for objet in self.objets}

            # Comportement des entités
            for entity in self.entities:

                if not entity.get_dead():
                    # Comportement des joueurs non ia
                    if entity in self.joueurs and not entity.get_ia():
                        # Commandes joueur 1
                        if entity.get_id() == 1:
                            # Selon la version de pygame et de python ça peut changer
                            if inputs[pygame.K_a] or inputs[pygame.K_q]:
                                input_vectors[entity][0] -= 1
                                entity.set_rotation("left")
                            if inputs[pygame.K_d]:
                                input_vectors[entity][0] += 1
                                entity.set_rotation("right")
                            if inputs[pygame.K_SPACE] and entity.get_type_joueur() == "solo":
                                entity.shoot(self.objets)

                        # Commandes joueur 2
                        elif entity.get_id() == 2:
                            if inputs[pygame.K_LEFT]:
                                input_vectors[entity][0] -= 1
                                entity.set_rotation("left")
                            if inputs[pygame.K_RIGHT]:
                                input_vectors[entity][0] += 1
                                entity.set_rotation("right")
                            if inputs[pygame.K_RETURN] and entity.get_type_joueur() == "solo":
                                entity.shoot(self.objets)

                    # Comportement des ia / ennemis
                    else:
                        # Comportement ia du joueur solo
                        if entity in self.joueurs and entity.get_type_joueur() == "solo":
                            # Ne peut pas bouger pendant ce délai
                            if entity.get_move_cooldown() - time.time() <= 0:
                                # Vise uniquement le dernier joueur vivant de la liste
                                joueur_target = joueurs_vivants[-1]

                                # Suit la position du joueur visé
                                if joueur_target.get_pos()[0] - 10 > entity.get_sprite_pos()[0]:
                                    input_vectors[entity][0] += 1
                                elif joueur_target.get_pos()[0] + 10 < entity.get_sprite_pos()[0]:
                                    input_vectors[entity][0] -= 1

                                # Sinon tire car il est dans la zone de tir
                                else:
                                    entity.shoot(self.objets)

                                    # Nouveau timer entre 0.5s et 1s
                                    nouveau_timer = random.randint(5, 10) / 10
                                    entity.set_move_cooldown(nouveau_timer + time.time())

                        # Comportement de l'ia sur les panneaux
                        else:
                            # Ne peut pas changer de direction pendant le délai
                            if entity.get_move_cooldown() - time.time() <= 0:
                                # Choisit une rotation (direction) aléatoire
                                nouvelle_rotation = random.choice(("left", "right", None))
                                entity.set_rotation(nouvelle_rotation)

                                # Nouveau timer entre 0.5s et 1s
                                nouveau_timer = random.randint(5, 10) / 10
                                entity.set_move_cooldown(nouveau_timer + time.time())

                            # Change les vecteurs de déplacement en fonction de la rotation
                            if entity.get_rotation() == "left":
                                input_vectors[entity][0] -= 1
                            elif entity.get_rotation() == "right":
                                input_vectors[entity][0] += 1

            # Pour chaque flèche, leur vecteur de déplacement se dirige vers le haut
            for objet in self.objets: 
                if type(objet) == Fleche:
                    input_vectors[objet] = [0, -1]

            # Utilisation du moteur de jeu et mise à jour du temps passé
            self.game_engine(input_vectors, prev_time)
            prev_time = time.time()

            # Le parent s'occupe du timer
            super().during_game()

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

        # Liste des joueurs vivants (tous ceux avec un get_dead() == False)
        joueurs_vivants = list(filter(lambda x: not x.get_dead(), self.joueurs))

        # Si le joueur solo est le seul en vie
        if len(joueurs_vivants) <= 1:
            # Il gagne et tous les autres perdent
            self.classement[self.joueurs[0].get_perso()] = 1
            for i in range(1, len(self.joueurs)):
                self.classement[self.joueurs[i].get_perso()] = 0
        else:
            # Il perd et tous les autres gagnent
            self.classement[self.joueurs[0].get_perso()] = 0
            for i in range(1, len(self.joueurs)):
                self.classement[self.joueurs[i].get_perso()] = 1

        # Le parent s'occupe de finir le mini-jeu
        super().calculate_score()