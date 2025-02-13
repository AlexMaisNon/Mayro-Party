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

    # On fait les calculs uniquement sur les axes x et y s'ils ne sont pas égaux à 0 (on exclut l'axe z)
    if not 0 in vecteur[:-1]:
        # sqrt(2) / 2 est longueur d'une diagonale dans un carré
        n_v = [elem * (sqrt(2) / 2) for elem in vecteur[:-1]]
    else:
        # On ne fait pas de modification
        n_v = [elem for elem in vecteur[:-1]]

    # On ajoute l'axe z non modifié au nouveau vecteur
    n_v.append(vecteur[-1])

    return n_v


# ------/ Classes \------

# Classe du joueur
class Joueur(generic.GenericJoueur):

    # ------/ Constructeur \------

    def __init__(self, perso: str, id: int, ia: bool) -> None:
        """
        Constructeur de la classe Joueur.

        Attributs à définir:
            - perso (str): Personnage choisit par le joueur.
            - id (int): id du joueur qui indique sa position dans l'ordre de jeu.
            - ia (bool): Indique si le joueur est une ia ou un joueur lambda.

        Attributs internes:
            - pos (list): Position du joueur.
            - velocity (list): Vélocité/Accélération du joueur.
            - speed (int): Vitesse du joueur.
            - jump_power (float): Puissance du saut du joueur.
            - gravity_speed (float): Vitesse de gravité.
            - rotation (str): Rotation du joueur.
            - invincibility (int): Timer qui détermine l'invincibilité du joueur.
            - dead (bool): Définit si le joueur est mort ou non.

            - target_offsets (list): Liste de décalages ajoutés au mouvement des ias pour donner de l'aléatoire.

            - sprites (dict): Sprites du joueurs.
            - sprite (pygame.Surface): Sprite actuel du joueur.

            - shadow_pos (list): Position de l'ombre.

            - collision (pygame.Rect): Boîte de collision du joueur.

            - priority (float): Valeur représentant la priorité d'affichage du sprite.

            - death_sound (pygame.Sound): Son de mort du joueur.

            - height (int): Hauteur du sprite du personnage.
            - ground_height (float): Hauteur du sol au niveau du joueur.
        """

        # On initialise tous les attributs du constructeur parent
        super().__init__(perso, id, ia)

        # Caractéristiques principales (stats)
        self.pos = [0.0, 0.0, 0.0]
        self.velocity = [0.0, 0.0, 0.0]
        self.speed = 300
        self.jump_power = 7.5
        self.gravity_speed = .249
        self.rotation = "down"
        self.dead = False

        # Uniquement pour l'ia (utilisé pour avoir un peu d'aléatoire sinon les ia se chevauchent toutes)
        self.target_offsets = [random.randint(-10, 110), random.randint(-10, 110)]

        # Le premier offset doit être plus petit que le second, on utilise donc sort
        self.target_offsets.sort()

        # On ajoute un dernier offset qui correspond au temps que l'ordi va mettre pour sauter
        # (Les randints sont en millisecondes pour la précision, on divise par 1000 pour avoir les secondes)
        self.target_offsets.append(random.randint(-1000, 1000) / 1000)

        # Définition des sprites automatiquement (pour les joueurs / ia)
        self.sprites = {
            "walk": {
                "left": [generic.scale_image_by(pygame.image.load(self.sprites_directory + "walk_left" + str(i) + ".png"), 3) for i in range(8)],
                "down": [generic.scale_image_by(pygame.image.load(self.sprites_directory + "walk_down" + str(i) + ".png"), 3) for i in range(8)],
                "up": [generic.scale_image_by(pygame.image.load(self.sprites_directory + "walk_up" + str(i) + ".png"), 3) for i in range(8)],
                "right": [generic.scale_image_by(pygame.image.load(self.sprites_directory + "walk_right" + str(i) + ".png"), 3) for i in range(8)]
            },
            "jump": {
                "left": [generic.scale_image_by(pygame.image.load(self.sprites_directory + "jump_left" + str(i) + ".png"), 3) for i in range(2)],
                "down": [generic.scale_image_by(pygame.image.load(self.sprites_directory + "jump_down" + str(i) + ".png"), 3) for i in range(2)],
                "up": [generic.scale_image_by(pygame.image.load(self.sprites_directory + "jump_up" + str(i) + ".png"), 3) for i in range(2)],
                "right": [generic.scale_image_by(pygame.image.load(self.sprites_directory + "jump_right" + str(i) + ".png"), 3) for i in range(2)]
            },
            "death": [generic.scale_image_by(pygame.image.load(self.sprites_directory + "death" + str(i) + ".png"), 3) for i in range(4)]
        }

        # Initialisation du sprite actuel
        self.sprite = self.sprites["walk"]["down"][0]

        # Positionnement de l'ombre (on le modifie ici car 3d)
        self.shadow_pos = list(self.pos)

        # Boîte de collision du personnage
        self.collision = pygame.Rect(0, 0, round((self.sprite.get_rect().w + 2) / 2), 20)

        # Initialisation et mise à jour de la priorité d'affichage
        self.priority = 0.0
        self.update_priority()

        # Emplacement des sons du joueur
        sounds_directory = "assets" + sep + "sounds" + sep + self.perso + sep

        # Sons du joueur
        self.death_sound = pygame.mixer.Sound(sounds_directory + "death.ogg")

        # Éléments importants pour la 3D
        self.height = -100 + self.collision.h
        self.ground_height = 0.0        # (variable car environnement 3D)


    # ------/ Getters \------

    def get_velocity(self) -> list:
        return self.velocity

    def get_priority(self) -> float:
        return self.priority

    def get_height(self) -> int:
        return self.height

    def get_target_offsets(self) -> list:
        return self.target_offsets

    def get_dead(self) -> bool:
        return self.dead

    def get_death_sound(self) -> pygame.mixer.Sound: # type: ignore
        return self.death_sound


    # ------/ Setters \------

    def set_velocity(self, new_velocity) -> None:
        self.velocity = new_velocity

    def set_rotation(self, new_rotation: str) -> None:
        self.rotation = new_rotation

    def set_target_offsets(self, new_offset: list) -> None:
        self.target_offsets = new_offset

    def set_dead(self, new_dead: bool) -> None:
        self.dead = new_dead


    # ------/ Méthodes \------

    def update_priority(self) -> None:
        """
        Cette méthode permet de calculer et de mettre à jour la priorité d'affichage.
        """

        # On prend le bas du sprite et on ajoute sa position en z
        self.priority = -self.collision.bottom + self.pos[2]


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

        # Calcul de la vélocité en z
        # Le maximum de la vélocité en z est self.jump_power * 2
        if self.velocity[2] > self.jump_power * 2:
            self.velocity[2] = self.jump_power * 2

        # Si le joueur est plus haut que la hauteur du sol, il subit la gravité
        elif self.pos[2] + self.velocity[2] < self.ground_height or self.dead:
            if self.velocity[2] < 0:
                self.velocity[2] += self.gravity_speed 
            else:
                self.velocity[2] += self.gravity_speed * (delta_time * 100)

        # Sinon immobile en z
        else:
            self.velocity[2] = 0.0
            self.pos[2] = self.ground_height

        # On normalise la vélocité
        self.velocity = normalize(self.velocity)


    def update_positions(self) -> None:
        """
        Cette méthode permet de mettre à jour les positions de l'ombre et de la collision du joueur.
        """

        # Positionnement de la boîte de collision (au niveau des pieds du joueur)
        self.collision.x = round(self.pos[0] + self.sprite.get_rect().w / 4)
        self.collision.y = round(self.pos[1] + self.sprite.get_rect().h - self.collision.h)

        # Positionnement de l'ombre
        self.shadow_pos[0] = round(self.pos[0] + (self.sprite.get_rect().w - self.shadow.get_rect().w) / 2)
        self.shadow_pos[1] = round(self.pos[1] + self.sprite.get_rect().h - self.shadow.get_rect().h)
        self.shadow_pos[2] = 0


    def collision3D(self, x: "int | float", y: "int | float", objet: "Joueur | Banquise | Pingouin") -> bool:
        """
        Cette méthode permet de calculer les collisions en 3D entre les côtés d'un bloc et le joueur.

        Paramètres:
            - x (int ou float): Coordonnée x donnée.
            - y (int ou float): Coordonnée y donnée.
            - objet (Joueur, Banquise ou Pingouin): Objet avec lequel le joueur doit calculer les collisions.

        Renvois:
            - bool: Indique si il y a une collision ou non.

        Post-conditions:
            - La méthode doit renvoyer True si le bloc est touché par la boîte de collision du joueur,
            seulement si il se situe au niveau du bloc, renvoie False s'il se trouve au-dessus ou en-dessous
            du bloc.
        """

        # Test du type des variables
        assert type(x) == int or type(x) == float, "Erreur: Le 1er paramètre (x) n'est pas un nombre."
        assert type(y) == int or type(y) == float, "Erreur: Le 2ème paramètre (y) n'est pas un nombre."
        assert type(objet) == Joueur or type(objet) == Banquise or type(objet) == Pingouin, "Erreur: Le 3ème paramètre (objet) n'est pas un objet valide."

        # Création d'une boîte de collision avec les coordonnées x et y
        rect = pygame.Rect(round(x), round(y), self.collision.w, self.collision.h)

        # Initialisation de l'état de la collision
        collided = False

        for collision in objet.get_collisions():
            # On active la collision si le joueur touche la boîte de collision
            if rect.colliderect(collision):
                collided = True
            # Si le joueur se situe en-dessous ou au-dessus du bloc, on désactive la collision
            if self.pos[2] > objet.get_pos()[2] or self.pos[2] + self.height < objet.get_pos()[2] + objet.get_height():
                collided = False

        # On renvoie l'état de la collision
        return collided


    def calculate_collisions(self, objets: list) -> None:      # renvoie un objet (donc soit Joueur soit Banquise soit Pingouin) ou rien
        """
        Cette méthode permet de calculer les collisions en 3D avec le joueur.
        (Pas de super() ici car incompatible avec la 3d.)

        Paramètres:
            - objets (list): Liste d'objets avec lesquels le joueur doit calculer les collisions.

        Pré-conditions:
            - objets doit contenir seulement des objets de type Joueur, Banquise ou Pingouin.
        """

        # Test du type de objets
        assert type(objets) == list, "Erreur: Le paramètre donné (objets) n'est pas une liste."

        # Tests des éléments de objets
        for elem in objets:
            assert type(elem) == Joueur or type(elem) == Banquise or type(elem) == Pingouin, "Erreur: La liste doit être seulement composée d'objets."

        # Calcul des collisions pour chaque objets (sauf soi-même)
        for objet in objets:
            if objet != self:
                # Collision avec les côtés du bloc (x et y)
                if self.collision3D(self.collision.x + self.velocity[0], self.collision.y, objet):
                    if self.collision3D(self.collision.x, self.collision.y, objet):
                        self.pos[0] -= self.velocity[0]
                    self.velocity[0] = 0.0

                if self.collision3D(self.collision.x, self.collision.y + self.velocity[1], objet):
                    if self.collision3D(self.collision.x, self.collision.y, objet):
                        self.pos[1] -= self.velocity[1]
                    self.velocity[1] = 0.0

        # Initialisation de l'objet collisionné
        collided_object = None

        # Calcul des collisions avec le sol (ou sur un objet) pour chaque objets (sauf soi-même)
        for objet in objets:
            if objet != self:
                for collision in objet.get_collisions():

                    # Si il y a collision avec un objet
                    if self.collision.colliderect(collision):
                        # Calcule la hauteur du sol avec l'objet actuel
                        new_ground_height = objet.get_pos()[2] + objet.get_height()

                        if new_ground_height >= self.pos[2]:
                            # On remplace la hauteur du sol et l'objet collisionné uniquement s'il n'y a pas de collision ou si
                            # la hauteur du sol actuelle est plus haute qu'avec la hauteur du sol avec l'objet déjà collisionné
                            if collided_object == None or new_ground_height < collided_object.get_pos()[2] + collided_object.get_height():
                                self.ground_height = new_ground_height
                                collided_object = objet

                    # S'il n'y a pas de collision avec un objet, on met la hauteur du sol à 0 par défaut
                    elif collided_object == None:
                        self.ground_height = 0


    def apply_velocity(self) -> None:
        """
        Cette méthode permet d'appliquer la vélocité à la position du joueur.
        (Pas de super() ici car incompatible avec la 3d.)
        """

        # On ajoute la vélocité à la position du personnage
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        self.pos[2] += self.velocity[2]

        # On réinitialise la vélocité (sinon effet Asteroids (le personnage glisse infiniment))
        self.velocity = [0.0, 0.0, self.velocity[2]]


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

        # On détecte si le joueur est mort en priorité
        if self.dead:
            # self.frame ne doit pas dépasser l'indice de la liste de sprites
            if self.frame > len(self.sprites["death"]) - 1:
                self.frame = 0

            # Changement du sprite actuel
            self.sprite = self.sprites["death"][round(self.frame)]

        # On détecte si le joueur est sur le sol
        elif self.velocity[2] == 0:
            # L'animation reste figée si le joueur est immobile
            if self.velocity[0] == 0 and self.velocity[1] == 0:
                self.frame = 0

            # self.frame ne doit pas dépasser l'indice de la liste de sprites
            if self.frame > len(self.sprites["walk"][self.rotation]) - 1:
                self.frame = 0
            
            # Changement du sprite actuel
            self.sprite = self.sprites["walk"][self.rotation][round(self.frame)]

        # Le joueur est en dehors du sol
        else:
            self.frame = 0

            # En train de sauter
            if self.velocity[2] <= 0:
                self.sprite = self.sprites["jump"][self.rotation][0]
            # En chute libre
            else:
                self.sprite = self.sprites["jump"][self.rotation][1]

        # Le parent s'occupe de changer la frame en fonction de la vitesse
        super().animate(delta_time, 15)


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

        # Affichage de l'ombre du personnage (dépend de la hauteur du sol)
        if not self.dead:
            screen.blit(generic.scale_image_by(self.shadow, screen_factor), (round(self.shadow_pos[0] * screen_factor[0]), round((self.shadow_pos[1] + self.ground_height) * screen_factor[1])))

        screen.blit(generic.scale_image_by(self.sprite, screen_factor), (round(self.pos[0] * screen_factor[0]), round((self.pos[1] + self.pos[2]) * screen_factor[1])))



# Classe de la banquise
class Banquise:

    # ------/ Constructeur \------

    def __init__(self) -> None:
        """
        Constructeur de la classe Banquise.

        Attributs internes:
            - pos (list): Position de la banquise.
            - sprite (pygame.Surface): Sprite de la banquise.

            - collision (list): Boîte de collision de la banquise.

            - height (int): Hauteur du sprite de l'hexagone.

            - priority (float): Valeur représentant la priorité d'affichage du sprite.
        """

        # Caractéristiques par défaut
        self.pos = [184.0, 74.0, 0.0]

        # Sprite de la banquise
        self.sprite = pygame.image.load("assets" + sep + "sprites" + sep + "minigames" + sep + "pushy_penguins" + sep + "banquise.png")

        # Boîtes de collision de l'hexagone
        self.collision =  pygame.Rect(0, 0, self.sprite.get_rect().w, self.sprite.get_rect().h - 120)

        # La position Z correspond au point le plus haut du bloc (en comptant seulement la plus haute collision, ici la 2ème)
        self.height = -self.sprite.get_rect().h + self.collision.h

        # Initialisation et mise à jour de la priorité d'affichage
        self.priority = 0.0
        self.update_priority()


    # ------/ Getters \------

    def get_pos(self) -> list:
        return self.pos

    def get_collisions(self) -> list:
        return [self.collision]

    def get_priority(self) -> float:
        return self.priority

    def get_height(self) -> int:
        return self.height


    # ------/ Setters \------

    def set_pos(self, new_pos: list) -> None:
        self.pos = new_pos


    # ------/ Méthodes \------

    def update_priority(self) -> None:
        """
        Cette méthode permet de calculer et de mettre à jour la priorité d'affichage.
        """

        # On prend la plus haute collision et on ajoute sa position et sa hauteur en z
        self.priority = -self.collision.top + self.height + self.pos[2]


    def update_positions(self) -> None:
        """
        Cette méthode permet de mettre à jour la position de la collision de la banquise.
        """

        # Positionnement de la boîte de collision
        self.collision.x = round(self.pos[0])
        self.collision.y = round(self.pos[1] + self.sprite.get_rect().h - self.collision.h)


    def draw(self, screen: pygame.Surface, show_collision: bool = False) -> None: # type: ignore
        """
        Cette méthode permet de dessiner l'hexagone sur l'écran.

        Paramètres:
            - screen (pygame.Surface): L'écran de jeu de pygame.
            - show_collision (bool): Paramètre optionnel permettant d'afficher les boîtes de collision.

        Pré-conditions:
            - screen doit être de type pygame.Surface.
        """

        # Tests des types de variables
        assert type(screen) == pygame.Surface, "Erreur: Le 1er paramètre (screen) n'est pas une surface pygame."
        assert type(show_collision) == bool, "Erreur: Le 2ème paramètre (show_collision) n'est pas un booléen."

        # Initialisation des facteurs pour la taille de l'écran
        screen_factor = ((screen.get_rect().size[0] / 1280), (screen.get_rect().size[1] / 720))

        screen.blit(generic.scale_image_by(self.sprite, screen_factor), (round(self.pos[0] * screen_factor[0]), round((self.pos[1] + self.pos[2]) * screen_factor[1])))

        # Paramètre de débug pour afficher les collisions
        if show_collision:
            pygame.draw.rect(screen, (0, 255, 0), self.collision, 1)



# Classe du pingouin
class Pingouin:

    # ------/ Constructeur \------

    def __init__(self, pos: list, speed: int, size: int) -> None:
        """
        Constructeur de la classe Pingouin.

        Attributs à définir:
            - pos (list): Position du pingouin.
            - speed (int): Vitesse du pingouin.
            - size (int): Taille du pingouin.

        Attributs internes:
            - velocity (list): Vélocité/Accélération du pingouin.
            - gravity_speed (float): Vitesse de gravité.

            - sprites (list): Sprites du pingouin.
            - sprite (pygame.Surface): Sprite actuel du pingouin.
            - frame (float): Indice du sprite à choisir.

            - shadow_pos (list): Position de l'ombre.

            - collision (pygame.Rect): Boîte de collision du pingouin.

            - priority (float): Valeur représentant la priorité d'affichage du sprite.

            - splash_sound (pygame.Sound): Son du pingouin quand il saute dans l'eau.

            - height (int): Hauteur du sprite du pingouin.
            - ground_height (float): Hauteur du sol au niveau du pingouin.
        """

        # Tests du type des paramètres donnés
        assert type(pos) == list, "Erreur: Le 1er paramètre (pos) est censé être une liste."
        assert type(speed) == int, "Erreur: Le 2ème paramètre (speed) est censé être un entier."
        assert type(size) == int, "Erreur: Le 3ème paramètre (size) est censé être un entier."

        # Caractéristiques principales (stats)
        self.pos = list(pos)
        self.speed = speed
        self.size = size

        self.velocity = [0.0, 0.0, 0.0]
        self.gravity_speed = .249

        # Emplacement des sprites du pingouin
        sprites_directory = "assets" + sep + "sprites" + sep + "minigames" + sep + "pushy_penguins" + sep + "pingouin" + sep

        # Définition des sprites automatiquement (pour les joueurs / ia)
        self.sprites = {"walk": [generic.scale_image_by(pygame.image.load(sprites_directory + "pingouin" + str(i) + ".png"), self.size) for i in range(2)],
                        "splash": generic.scale_image_by(pygame.image.load(sprites_directory + "pingouin_splash.png"), self.size * 2)}

        # Initialisation du sprite actuel
        self.sprite = self.sprites["walk"][0]
        self.frame = 0.0

        # Initialisation et positionnement de l'ombre
        self.shadow = generic.scale_image_by(pygame.image.load(sprites_directory + "shadow.png"), 3.75 * size)
        self.shadow_pos = list(self.pos)

        # Boîte de collision du personnage
        self.collision = pygame.Rect(0, 0, round((self.sprite.get_rect().w + 2) / 2), 40 * size)

        # Initialisation et mise à jour de la priorité d'affichage
        self.priority = 0.0
        self.update_priority()

        # Son du pingouin
        self.splash_sound = pygame.mixer.Sound("assets" + sep + "sounds" + sep + "minigames" + sep + "pushy_penguins" + sep + "pingouin_splash.ogg")

        # Éléments importants pour la 3D
        self.height = (-200 * self.size) + self.collision.h
        self.ground_height = 0.0        # (variable car environnement 3D)


    # ------/ Getters \------

    def get_pos(self) -> list:
        return self.pos

    def get_velocity(self) -> list:
        return self.velocity

    def get_priority(self) -> float:
        return self.priority

    def get_collisions(self) -> list:
        return [self.collision]

    def get_height(self) -> int:
        return self.height

    def get_splash_sound(self) -> pygame.mixer.Sound: # type: ignore
        return self.splash_sound


    # ------/ Méthodes \------

    def update_priority(self) -> None:
        """
        Cette méthode permet de calculer et de mettre à jour la priorité d'affichage.
        """

        # On prend le bas du sprite et on ajoute sa position en z
        self.priority = -self.collision.bottom + self.pos[2]


    def calculate_velocity(self, direction: list, delta_time: float) -> None:
        """
        Cette méthode permet de calculer la vélocité du pingouin.

        Paramètres:
            - direction (list): Direction sous forme de vecteur dans laquelle le pingouin se déplace.
            - delta_time (float): Valeur calculé dans le moteur de jeu qui permet l'indépendance de la vitesse au framerate.

        Pré-conditions:
            - direction doit être compris entre -1 et 1.
        """

        # Test des types de variables
        assert type(direction) == list, "Erreur: Le 1er paramètre (direction) n'est pas une liste."
        assert type(delta_time) == float, "Erreur: Le 2ème paramètre (delta_time) n'est pas un nombre flottant."

        # Calcul de la velocité en x et y
        self.velocity[0] += direction[0] * self.speed * delta_time
        self.velocity[1] += direction[1] * self.speed * delta_time

        # Si le pingouin est plus haut que la hauteur du sol, il subit la gravité
        if self.pos[2] + self.velocity[2] < self.ground_height:
            if self.velocity[2] < 0:
                self.velocity[2] += self.gravity_speed 
            else:
                self.velocity[2] += self.gravity_speed * (delta_time * 100)

        # Sinon immobile en z
        else:
            self.velocity[2] = 0.0
            self.pos[2] = self.ground_height

        # On normalise la vélocité
        self.velocity = normalize(self.velocity)


    def update_positions(self) -> None:
        """
        Cette méthode permet de mettre à jour les positions de l'ombre et de la collision du pingouin.
        """

        # Positionnement de la boîte de collision (au niveau des pieds du pingouin)
        self.collision.x = round(self.pos[0] + self.sprite.get_rect().w / 4)
        self.collision.y = round(self.pos[1] + self.sprite.get_rect().h - self.collision.h)

        # Positionnement de l'ombre
        self.shadow_pos[0] = round(self.pos[0] + (self.sprite.get_rect().w - self.shadow.get_rect().w) / 2)
        self.shadow_pos[1] = round(self.pos[1] + self.sprite.get_rect().h - self.shadow.get_rect().h)
        self.shadow_pos[2] = 0


    def collision3D(self, x: "int | float", y: "int | float", objet: "Joueur | Banquise | Pingouin") -> bool:
        """
        Cette méthode permet de calculer les collisions en 3D entre les côtés d'un bloc et le joueur.

        Paramètres:
            - x (int ou float): Coordonnée x donnée.
            - y (int ou float): Coordonnée y donnée.
            - objet (Joueur ou Hexagon): Objet avec lequel le joueur doit calculer les collisions.

        Renvois:
            - bool: Indique si il y a une collision ou non.

        Post-conditions:
            - La méthode doit renvoyer True si le bloc est touché par la boîte de collision du joueur,
            seulement si il se situe au niveau du bloc, renvoie False s'il se trouve au-dessus ou en-dessous
            du bloc.
        """

        # Test du type des variables
        assert type(x) == int or type(x) == float, "Erreur: Le 1er paramètre (x) n'est pas un nombre."
        assert type(y) == int or type(y) == float, "Erreur: Le 2ème paramètre (y) n'est pas un nombre."
        assert type(objet) == Joueur or type(objet) == Banquise or type(objet) == Pingouin, "Erreur: Le 3ème paramètre (objet) n'est pas un objet de type Joueur ou Banquise."

        # Création d'une boîte de collision avec les coordonnées x et y
        rect = pygame.Rect(round(x), round(y), self.collision.w, self.collision.h)

        # Initialisation de l'état de la collision
        collided = False

        for collision in objet.get_collisions():
            # On active la collision si le joueur touche la boîte de collision
            if rect.colliderect(collision):
                collided = True
            if type(objet) == Banquise:
                collided = False

        # On renvoie l'état de la collision
        return collided


    def calculate_collisions(self, objets: list) -> None:
        """
        Cette méthode permet de calculer les collisions en 3D avec le pingouin.

        Paramètres:
            - objets (list): Liste d'objets avec lesquels le pingouin doit calculer les collisions.

        Pré-conditions:
            - objets doit contenir seulement des objets de type Joueur, Banquise ou Pingouin.
        """

        # Test du type de objets
        assert type(objets) == list, "Erreur: Le paramètre donné (objets) n'est pas une liste."

        # Tests des éléments de objets
        for elem in objets:
            assert type(elem) == Joueur or type(elem) == Banquise or type(elem) == Pingouin, "Erreur: La liste doit être seulement composée d'objets."

        # Calcul des collisions pour chaque objets (sauf soi-même)
        for objet in objets:
            if objet != self:
                # Collision avec les côtés du bloc (x et y)
                if self.collision3D(self.collision.x + self.velocity[0], self.collision.y, objet) and not type(objet) == Pingouin:
                    objet.set_pos([objet.get_pos()[0] + self.velocity[0], objet.get_pos()[1], objet.get_pos()[2]])

                if self.collision3D(self.collision.x, self.collision.y + self.velocity[1], objet):
                    self.velocity[1] = 0.0

        # Initialisation de l'objet collisionné
        collided_object = None

        # Calcul des collisions avec le sol (ou sur un objet) pour chaque objets (sauf soi-même)
        for objet in objets:
            if objet != self:
                for collision in objet.get_collisions():

                    # Si il y a collision avec un objet
                    if self.collision.colliderect(collision):
                        # Calcule la hauteur du sol avec l'objet actuel
                        new_ground_height = objet.get_pos()[2] + objet.get_height()

                        if new_ground_height >= self.pos[2]:
                            # On remplace la hauteur du sol et l'objet collisionné uniquement s'il n'y a pas de collision ou si
                            # la hauteur du sol actuelle est plus haute qu'avec la hauteur du sol avec l'objet déjà collisionné
                            if collided_object == None or new_ground_height < collided_object.get_pos()[2] + collided_object.get_height():
                                self.ground_height = new_ground_height
                                collided_object = objet

                    # S'il n'y a pas de collision avec un objet, on met la hauteur du sol à 0 par défaut
                    elif collided_object == None:
                        self.ground_height = 0


    def apply_velocity(self) -> None:
        """
        Cette méthode permet d'appliquer la vélocité à la position du pingouin.
        """

        # On ajoute la vélocité à la position du pingouin
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        self.pos[2] += self.velocity[2]

        # On réinitialise la vélocité (sinon effet Asteroids (le pingouin glisse infiniment))
        self.velocity = [0.0, 0.0, self.velocity[2]]


    def animate(self, delta_time: float) -> None:
        """
        Cette méthode permet d'animer le sprite du pingouin.

        Paramètres:
            - delta_time (float): Valeur calculé dans le moteur de jeu qui permet l'indépendance de la vitesse au framerate.

        Pré-conditions:
            - delta_time doit être un nombre flottant.
        """

        # Test du type de delta_time
        assert type(delta_time) == float, "Erreur: Le paramètre donné (delta_time) n'est pas un nombre flottant."

        # On détecte si le pingouin est sur le sol
        if self.velocity[2] == 0:
            # self.frame ne doit pas dépasser l'indice de la liste de sprites
            if self.frame > len(self.sprites["walk"]) - 1:
                self.frame = 0
            
            # Changement du sprite actuel
            self.sprite = self.sprites["walk"][round(self.frame)]

        # Le pingouin est en dehors du sol
        else:
            self.frame = 0
            self.sprite = self.sprites["splash"]

        # Changement de l'indice choisit avec une indépendance au framerate
        self.frame += 8 * delta_time


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
        screen_factor = ((screen.get_rect().size[0] / 1280), (screen.get_rect().size[1] / 720))

        # Affichage des sprites du pingouin
        screen.blit(generic.scale_image_by(self.shadow, screen_factor), (round(self.shadow_pos[0] * screen_factor[0]), round((self.shadow_pos[1] + self.ground_height) * screen_factor[1])))
        screen.blit(generic.scale_image_by(self.sprite, screen_factor), (round(self.pos[0] * screen_factor[0]), round((self.pos[1] + self.pos[2]) * screen_factor[1])))

        # Paramètre de débug pour afficher les collisions
        if show_collision:
            pygame.draw.rect(screen, (0, 255, 0), self.collision, 1)



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
            - timer (int): Durée du mini-jeu
            - classement (Pile ou dict): Classement des joueurs à la fin du mini-jeu.
            - priorities (dict): Priorité d'affichage pour chaque objet.

            - bg (pygame.Surface): Image de fond pour le mini-jeu.
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
        self.timer = 30

        # Initialisation des paramètres pour la partie gameplay
        self.classement = Pile()
        self.priorities = {}

        # Emplacement des sprites du mini-jeu
        minigame_directory = "assets" + sep + "sprites" + sep + "minigames" + sep + "pushy_penguins" + sep

        # Sprites utilisés dans la classe
        self.bg = pygame.image.load((minigame_directory + "water.png"))


    # ------/ Méthodes \------

    def game_engine(self, input_vectors: dict, prev_time: float) -> None: # type: ignore
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

        # On affiche les sprites du jeu dans un ordre d'affichage prédéfini
        self.screen.blit(generic.scale_image_by(self.bg, self.screen_factor), (0, 0))

        # Calcul de la physique de chaque joueur
        for objet in self.objets:
            # On met à jour la position de chaque objet
            objet.update_positions()

            if type(objet) != Banquise:
                # Calcul de la vélocité des objets
                if type(objet) == Joueur:
                    objet.calculate_velocity(input_vectors[objet], self.delta_time)
                else:
                    objet.calculate_velocity([-1, 0], self.delta_time)

                # Calcul des collisions
                objet.calculate_collisions(self.objets)

                # Calcul de l'animation de l'objet actuel (avec la valeur de delta_time)
                objet.animate(self.delta_time)

                # On applique le mouvement à l'objet
                objet.apply_velocity()

            # On calcule la priorité d'affichage pour tous les objets existants (y compris des joueurs)
            self.priorities[objet] = objet.get_priority()
            objet.update_priority()

            # Détection de la mort des joueurs/pingouins
            if type(objet) != Banquise:
                # Supprime le joueur quand il sort de l'écran (1000 est totalement arbitraire)
                if objet.get_pos()[2] > 1000 and type(objet) == Joueur:
                    # On le retire à la fois des joueurs et des objets
                    self.joueurs.remove(objet)
                    self.objets.remove(objet)

                # Détection de la mort
                if objet.get_pos()[2] > -45:
                    if type(objet) == Joueur and not objet.get_dead():
                        objet.get_death_sound().play()
                        objet.set_dead(True)

                        # On le stocke dans le classement sous forme de pile
                        if type(self.classement) != dict:
                            self.classement.empile(objet.get_perso())
                    elif type(objet) == Pingouin:
                        self.objets.remove(objet)
                        objet.get_splash_sound().play()

                        # On supprime le pingouin de l'existence
                        del self.priorities[objet]
                        del objet

        # sorted permet ici de trier les clés du dictionnaire automatiquement en fonction de la valeur d'affichage
        # (sorted c'est beaucoup plus simple j'avoue)
        for priority in sorted(self.priorities, key=self.priorities.get, reverse=True):
            priority.draw(self.screen, self.show_collisions)

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

        # Liste des noms des joueurs
        liste_joueurs = list(param_joueurs.keys())

        # Ordre aléatoire pour que chaque joueur puisse avoir une position aléatoire
        random.shuffle(liste_joueurs)

        # Création des joueurs dans la liste
        for nom_joueur in liste_joueurs:
            id_joueur = param_joueurs[nom_joueur][0]
            ia_joueur = param_joueurs[nom_joueur][1]
            self.joueurs.append(Joueur(nom_joueur, id_joueur, ia_joueur))

        # Positionnement des joueurs
        self.joueurs[0].set_pos([500.0, 450.0, -120])
        self.joueurs[1].set_pos([664.0, 450.0, -120])
        self.joueurs[2].set_pos([664.0, 250.0, -120])
        self.joueurs[3].set_pos([500.0, 250.0, -120])

        # Initialisation de la liste des objets
        self.objets = self.joueurs + [Banquise()]

        # Textes pour la description du jeu
        description = ["Esquivez les pingouins pour ne",
                       "pas tomber dans la mer !",
                       "Le dernier survivant avant",
                       "la fin du temps imparti gagne !"]

        # Le parent s'occupe du reste de la méthode
        super().load("assets" + sep + "musics" + sep + "minigames" + sep + "pushy_penguins.ogg", "Pushy Penguins", description)


    def during_game(self) -> None:
        """
        Cette méthode représente la phase de déroulement du mini-jeu.
        """

        # Initialisation des paramètres par défaut de la phase
        running = True
        prev_time = time.time()

        # Initialisation de 2 timers cachés
        cooldown = 0
        total_time = 0.095

        ia_cooldown = 1 + time.time()
        ia_pos = {joueur: [random.randint(800, 1100), random.randint(200, 600)] for joueur in self.joueurs}

        # Listes aléatoires pour les pingouins
        pingouin_sizes = [1 for i in range(15)] + [3]

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

            # Le mini-jeu s'arrête s'il reste qu'un seul joueur en vie ou si le timer s'arrête 
            if len(self.joueurs) <= 1 or self.timer - time.time() <= 0:
                if self.classement.taille() < 4:
                    # On stocke le dernier survivant s'il n'est pas déjà mort
                    if len(self.joueurs) > 0:
                        self.classement.empile(self.joueurs[0].get_perso())
                running = False

            # Détection des inputs et réinitialisation des vecteurs de déplacement des joueurs
            inputs = pygame.key.get_pressed()
            input_vectors = {joueur: [0, 0] for joueur in self.joueurs}

            # Comportement des joueurs
            for joueur in self.joueurs:
                if not joueur.get_dead():
                    if not joueur.get_ia():
                        # Commandes joueur 1
                        if joueur.get_id() == 1:
                            # Selon la version de pygame et de python ça peut changer
                            if inputs[pygame.K_a] or inputs[pygame.K_q]:
                                input_vectors[joueur][0] -= 1
                                joueur.set_rotation("left")
                            if inputs[pygame.K_s]:
                                input_vectors[joueur][1] += 1
                                joueur.set_rotation("down")
                            if inputs[pygame.K_w] or inputs[pygame.K_z]:
                                input_vectors[joueur][1] -= 1
                                joueur.set_rotation("up")
                            if inputs[pygame.K_d]:
                                input_vectors[joueur][0] += 1
                                joueur.set_rotation("right")

                        # Commandes joueur 2
                        elif joueur.get_id() == 2:
                            if inputs[pygame.K_LEFT]:
                                input_vectors[joueur][0] -= 1
                                joueur.set_rotation("left")
                            if inputs[pygame.K_DOWN]:
                                input_vectors[joueur][1] += 1
                                joueur.set_rotation("down")
                            if inputs[pygame.K_UP]:
                                input_vectors[joueur][1] -= 1
                                joueur.set_rotation("up")
                            if inputs[pygame.K_RIGHT]:
                                input_vectors[joueur][0] += 1
                                joueur.set_rotation("right")

                    # Comportement des ia
                    else:
                        # Initialisation d'une position aléatoire choisie
                        if ia_cooldown - time.time() < 0:
                            ia_pos = {joueur: [random.randint(800, 1100), random.randint(300, 500)] for joueur in self.joueurs}
                            ia_cooldown = 1 + time.time()

                        # Pathfinding de l'ia (comme Hexagon Heat)
                        # Les targets offsets servent à mettre de l'aléatoire un peu partout dans les mouvements
                        # de l'ia pour qu'elle soit moins parfaite
                        x_offset_min = ia_pos[joueur][0] + joueur.get_target_offsets()[0]
                        x_offset_max = ia_pos[joueur][0] + joueur.get_target_offsets()[1]
                        y_offset_min = ia_pos[joueur][1] + joueur.get_target_offsets()[0]
                        y_offset_max = ia_pos[joueur][1] + joueur.get_target_offsets()[1]

                        # L'ia se déplace en fonction des coordonnées trouvées
                        if joueur.get_pos()[0] < x_offset_min and joueur.get_pos()[0] < x_offset_max:
                            input_vectors[joueur][0] += 1
                            joueur.set_rotation("right")

                        elif joueur.get_pos()[0] > x_offset_min and joueur.get_pos()[0] > x_offset_max:
                            input_vectors[joueur][0] -= 1
                            joueur.set_rotation("left")

                        if joueur.get_pos()[1] < y_offset_min and joueur.get_pos()[1] < y_offset_max:
                            input_vectors[joueur][1] += 1
                            joueur.set_rotation("down")

                        elif joueur.get_pos()[1] > y_offset_min and joueur.get_pos()[1] > y_offset_max:
                            input_vectors[joueur][1] -= 1
                            joueur.set_rotation("up")

            # Logique du mini-jeu en elle même
            if time.time() - cooldown > total_time and self.timer - time.time() > 5:
                # Caractéristiques aléatoires du pingouin
                current_x = 1250.0
                current_y = random.randint(150.0, 650.0)
                current_speed = random.randint(200, 400)
                current_size = random.choice(pingouin_sizes)

                # On décale le gros pingouin pour pas qu'il tombe instantanément de la plateforme
                if current_size > 1:
                    current_x -= 25 * current_size
                    current_y -= 25 * current_size

                # On crée le pingouin
                self.objets.append(Pingouin([current_x, current_y, -120], current_speed, current_size))

                # Réinitialisation du timer
                cooldown = time.time()

                # Le temps que met chaque pingouin pour spawn se réduit
                total_time -= 0.00014

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
            pygame.mixer.stop()
            self.end_game()


    def calculate_score(self) -> None:
        """
        Cette méthode permet de calculer les scores de chaque joueur.
        """

        # Place du premier joueur
        position = 1

        # Classement sous la forme d'un dictionnaire
        new_classement = {}

        # On dépile les joueurs dans l'ordre et on note leur position dans le classement
        while not self.classement.est_vide():
            joueur = self.classement.depile()
            if type(joueur) == list:
                for j in joueur:
                    new_classement[j.get_perso()] = position
            else:
                new_classement[joueur] = position
            position += 1

        # On remplace le format du classement pour le récupérer ensuite
        self.classement = new_classement

        # Si tout le monde est gagnant
        if all([self.classement[joueur] == 1 for joueur in self.classement.keys()]):
            # Personne ne gagne car égalité (règle que je viens d'inventer)
            self.classement = {joueur: 0 for joueur in self.classement.keys()}

        print(self.classement)

        # Le parent s'occupe de finir le mini-jeu
        super().calculate_score()