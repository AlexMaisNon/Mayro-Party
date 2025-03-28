#Projet : Mayro Party
#Auteurs : Hinata Bouaziz, Antoine Desrues, Alexandre Guillaume, Matisse Moreau

# ------/ Importations des bibliothèques \------

import json
import socket
import pygame
from math import sqrt
import time
import random

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
class Joueur:

    # ------/ Constructeur \------

    def __init__(self, perso: str, id_minijeu: int, ia: bool) -> None:
        """
        Constructeur de la classe Joueur.

        Attributs à définir:
            - perso (str): Personnage choisit par le joueur.
            - id_minijeu (int): id du joueur qui sert uniquement lors des mini-jeux.
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

            - frame (float): Indice du sprite à choisir.

            - collision (pygame.Rect): Boîte de collision du joueur.

            - taille (list): Dimensions du sprite du joueur (fournis par le client).

            - height (int): Hauteur du sprite du personnage.
            - ground_height (float): Représente la plus haute coordonnée du sol par rapport au joueur.
        """

        # Tests du type des paramètres donnés
        assert type(perso) == str, "Erreur: Le 1er paramètre (perso) est censé être une chaîne de caractères."
        assert type(id_minijeu) == int, "Erreur: Le 2ème paramètre (id) est censé être un entier."
        assert type(ia) == bool, "Erreur: Le 3ème paramètre (ia) est censé être un booléen."

        # Définition du joueur
        self.perso = perso
        self.id_minijeu = id_minijeu
        self.ia = ia
        self.ready = False

        # Caractéristiques principales (stats)
        self.pos = [0, 0, 0]
        self.velocity = [0, 0, 0]
        self.speed = 5.6
        self.jump_power = 11.4
        self.gravity_speed = .6
        self.rotation = "down"
        self.dead = False

        # Initialisation des paramètres pour le déplacement de l'ia
        self.delai_ia = 1
        self.ia_target_pos = [0, 0, 0]

        # Initialisation de la frame choisie
        self.frame = 0

        # Boîte de collision du personnage
        self.collision = pygame.Rect(0, 0, 42, 20)

        # Initialisation de la taille du joueur (qui sera définie lors du début de partie)
        self.taille = [0, 0]

        # Éléments importants pour la 3D
        self.height = -100 + self.collision.h
        self.ground_height = 0


    # ------/ Getters \------

    def get_perso(self) -> str:
        return self.perso

    def get_id_minijeu(self) -> int:
        return self.id_minijeu

    def get_ia(self) -> bool:
        return self.ia

    def get_ready(self) -> bool:
        return self.ready

    def get_pos(self) -> list:
        return self.pos

    def get_velocity(self) -> list:
        return self.velocity

    def get_rotation(self) -> str:
        return self.rotation

    def get_dead(self) -> bool:
        return self.dead

    def get_delai_ia(self) -> float:
        return self.delai_ia

    def get_ia_target_pos(self) -> list:
        return self.ia_target_pos

    def get_frame(self) -> float:
        return self.frame

    def get_collisions(self) -> list:
        return [self.collision]

    def get_height(self) -> int:
        return self.height

    def get_ground_height(self) -> float:
        return self.ground_height


    # ------/ Setter \------

    def set_ready(self, new_ready: bool) -> None:
        self.ready = new_ready

    def set_pos(self, new_pos: list) -> None:
        self.pos = new_pos

    def set_rotation(self, new_rotation: str) -> None:
        self.rotation = new_rotation

    def set_dead(self, new_dead: bool) -> None:
        self.dead = new_dead

    def set_delai_ia(self, new_delai_ia) -> float:
        self.delai_ia = new_delai_ia

    def set_ia_target_pos(self, new_ia_target_pos) -> list:
        self.ia_target_pos = new_ia_target_pos

    def set_frame(self, new_frame: float) -> None:
        self.frame = new_frame

    def set_taille(self, new_taille: list) -> None:
        self.taille = new_taille


    # ------/ Méthodes \------

    def calculer_velocite(self, direction: list) -> None:
        """
        Cette méthode permet de calculer la vélocité du joueur.

        Paramètres:
            - direction (list): Direction sous forme de vecteur dans laquelle le joueur se déplace.

        Pré-conditions:
            - direction doit être compris entre -1 et 1.
        """

        # Test des types de variables
        assert type(direction) == list, "Erreur: Le paramètre (direction) n'est pas une liste."

        # Test des valeurs dans direction
        for elem in direction:
            assert elem >= -1 and elem <= 1, "Erreur: Une des valeurs dans la direction donnée n'est pas valide."

        self.velocity[0] += direction[0] * self.speed
        self.velocity[1] += direction[1] * self.speed

        # Calcul de la vélocité en z
        # Le maximum de la vélocité en z est self.jump_power * 2
        if self.velocity[2] > self.jump_power * 2:
            self.velocity[2] = self.jump_power * 2

        # Si le joueur est plus haut que la hauteur du sol, il subit la gravité
        elif self.pos[2] + self.velocity[2] < self.ground_height or self.dead:
            self.velocity[2] += self.gravity_speed 

        # Sinon immobile en z
        else:
            self.velocity[2] = 0
            self.pos[2] = self.ground_height

        # On normalise la vélocité
        self.velocity = normalize(self.velocity)


    def collision3D(self, x: "int | float", y: "int | float", objet: "Joueur | Banquise | Pingouin") -> bool:
        """
        Cette méthode permet de calculer les collisions en 3D entre les côtés d'un bloc et le joueur.

        Paramètres:
            - x (int ou float): Coordonnée x donnée.
            - y (int ou float): Coordonnée y donnée.
            - objet (Joueur ou Banquise ou Pingouin): Objet avec lequel le joueur doit calculer les collisions.

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
        assert type(objet) == Joueur or type(objet) == Banquise or type(objet) == Pingouin, "Erreur: Le 3ème paramètre (objet) n'est pas un objet de type Joueur ou Hexagon."

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


    def calculer_collisions(self, objets: list) -> "Joueur | Banquise | Pingouin | None":       # renvoie un objet (donc soit Joueur, soit Banquise soit Pingouin) ou rien
        """
        Cette méthode permet de calculer les collisions en 3D avec le joueur.

        Paramètres:
            - objets (list): Liste d'objets avec lesquels le joueur doit calculer les collisions.

        Renvois:
            - Joueur ou Banquise ou Pingouin ou None: L'objet qui collisionne en-dessous du joueur.

        Pré-conditions:
            - objets doit contenir seulement des objets de type Joueur ou Hexagon.

        Post-conditions:
            - La méthode doit renvoyer l'objet de type Joueur ou Hexagon qui collisionne en-dessous du joueur
            ou renvoie None s'il n'y a pas de collision.
        """

        # Test du type de objets
        assert type(objets) == list, "Erreur: Le paramètre donné (objets) n'est pas une liste."

        # Tests des éléments de objets
        for elem in objets:
            assert type(elem) == Joueur or type(elem) == Banquise or type(elem) == Pingouin, "Erreur: La liste doit être seulement composée d'objets."

        # Positionnement de la boîte de collision (au niveau des pieds du joueur)
        self.collision.x = round(self.pos[0] + self.taille[0] / 4)
        self.collision.y = round(self.pos[1] + self.taille[1] - self.collision.h)

        # Calcul des collisions pour chaque objets (sauf soi-même)
        for objet in objets:
            if objet != self:
                # Collision avec les côtés du bloc (x et y)
                if self.collision3D(self.collision.x + self.velocity[0], self.collision.y, objet):
                    if self.collision3D(self.collision.x, self.collision.y, objet):
                        self.pos[0] -= self.velocity[0]
                    self.velocity[0] = 0

                if self.collision3D(self.collision.x, self.collision.y + self.velocity[1], objet):
                    if self.collision3D(self.collision.x, self.collision.y, objet):
                        self.pos[1] -= self.velocity[1]
                    self.velocity[1] = 0

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

        # On renvoie l'objet collisionné
        return collided_object


    def appliquer_velocite(self) -> None:
        """
        Cette méthode permet d'appliquer la vélocité à la position du joueur.
        """

        # On ajoute la vélocité à la position du personnage
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        self.pos[2] += self.velocity[2]

        # On réinitialise la vélocité (sauf l'axe z qui est géré plus haut avec la gravité)
        self.velocity = [0, 0, self.velocity[2]]



# Classe de la banquise
class Banquise:

    # ------/ Constructeur \------

    def __init__(self) -> None:
        """
        Constructeur de la classe Banquise.

        Attributs internes:
            - pos (list): Position de la banquise.

            - collision (list): Boîte de collision de la banquise.

            - height (int): Hauteur du sprite de la banquise.
        """

        # Position par défaut
        self.pos = [184, 74, 0]

        # Boîte de collision de la banquise
        self.collision =  pygame.Rect(round(self.pos[0]), round(self.pos[1] + 120), 1096, 526)   # Hauteur de la collision (646 - 120 = 526)

        # La hauteur correspond au point le plus haut de la banquise
        self.height = self.collision.h - 646


    # ------/ Getters \------

    def get_pos(self) -> list:
        return self.pos

    def get_collisions(self) -> list:
        return [self.collision]

    def get_height(self) -> int:
        return self.height



# Classe du pingouin
class Pingouin:

    # ------/ Constructeur \------

    def __init__(self, pos: list, speed: int, size: int, id_pingouin: int) -> None:
        """
        Constructeur de la classe Pingouin.

        Attributs à définir:
            - pos (list): Position du pingouin.
            - speed (int): Vitesse du pingouin.
            - size (int): Taille du pingouin.
            - id_pingouin (int): Identifiant qui permet de retrouver plus facilement les pingouins
            créés par le serveur.

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
        assert type(id_pingouin) == int, "Erreur: Le 4ème paramètre (id_pingouin) est censé être un entier."

        # Caractéristiques principales (stats)
        self.pos = list(pos)
        self.speed = speed
        self.size = size
        self.id_pingouin = id_pingouin

        self.velocity = [0, 0, 0]
        self.gravity_speed = .6

        # Initialisation de la frame choisie
        self.frame = 0

        # Boîte de collision du pingouin
        self.collision = pygame.Rect(0, 0, 38 * size, 20)

        # Éléments importants pour la 3D
        self.height = -100 + self.collision.h
        self.ground_height = 0        # (variable car environnement 3D)


    # ------/ Getters \------

    def get_pos(self) -> list:
        return self.pos

    def get_size(self) -> list:
        return self.size

    def get_id_pingouin(self) -> list:
        return self.id_pingouin

    def get_frame(self) -> list:
        return self.frame

    def get_collisions(self) -> list:
        return [self.collision]

    def get_height(self) -> int:
        return self.height

    def get_ground_height(self) -> float:
        return self.ground_height


    # ------/ Setters \------

    def set_frame(self, new_frame: float) -> None:
        self.frame = new_frame


    # ------/ Méthodes \------

    def calculer_velocite(self, direction: list) -> None:
        """
        Cette méthode permet de calculer la vélocité du joueur.

        Paramètres:
            - direction (list): Direction sous forme de vecteur dans laquelle le joueur se déplace.

        Pré-conditions:
            - direction doit être compris entre -1 et 1.
        """

        # Test des types de variables
        assert type(direction) == list, "Erreur: Le paramètre (direction) n'est pas une liste."

        # Test des valeurs dans direction
        for elem in direction:
            assert elem >= -1 and elem <= 1, "Erreur: Une des valeurs dans la direction donnée n'est pas valide."

        self.velocity[0] += direction[0] * self.speed
        self.velocity[1] += direction[1] * self.speed

        # Calcul de la vélocité en z
        # Si le pingouin est plus haut que la hauteur du sol, il subit la gravité
        if self.pos[2] + self.velocity[2] < self.ground_height:
            self.velocity[2] += self.gravity_speed 

        # Sinon immobile en z
        else:
            self.velocity[2] = 0
            self.pos[2] = self.ground_height

        # On normalise la vélocité
        self.velocity = normalize(self.velocity)


    def collision3D(self, x: "int | float", y: "int | float", objet: "Joueur | Banquise | Pingouin") -> bool:
        """
        Cette méthode permet de calculer les collisions en 3D entre les côtés d'un bloc et le joueur.

        Paramètres:
            - x (int ou float): Coordonnée x donnée.
            - y (int ou float): Coordonnée y donnée.
            - objet (Joueur ou Banquise ou Pingouin): Objet avec lequel le joueur doit calculer les collisions.

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
        assert type(objet) == Joueur or type(objet) == Banquise or type(objet) == Pingouin, "Erreur: Le 3ème paramètre (objet) n'est pas un objet de type Joueur ou Hexagon."

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


    def calculer_collisions(self, objets: list) -> "Joueur | Banquise | Pingouin | None":       # renvoie un objet (donc soit Joueur, soit Banquise soit Pingouin) ou rien
        """
        Cette méthode permet de calculer les collisions en 3D avec le joueur.

        Paramètres:
            - objets (list): Liste d'objets avec lesquels le joueur doit calculer les collisions.

        Renvois:
            - Joueur ou Banquise ou Pingouin ou None: L'objet qui collisionne en-dessous du joueur.

        Pré-conditions:
            - objets doit contenir seulement des objets de type Joueur ou Hexagon.

        Post-conditions:
            - La méthode doit renvoyer l'objet de type Joueur ou Hexagon qui collisionne en-dessous du joueur
            ou renvoie None s'il n'y a pas de collision.
        """

        # Test du type de objets
        assert type(objets) == list, "Erreur: Le paramètre donné (objets) n'est pas une liste."

        # Tests des éléments de objets
        for elem in objets:
            assert type(elem) == Joueur or type(elem) == Banquise or type(elem) == Pingouin, "Erreur: La liste doit être seulement composée d'objets."


        # Positionnement de la boîte de collision (au niveau des pieds du pingouin)
        self.collision.x = round(self.pos[0] + (38 * self.size) / 4)
        self.collision.y = round(self.pos[1] + (84 * self.size) - self.collision.h)

        # Calcul des collisions pour chaque objets (sauf soi-même)
        for objet in objets:
            if objet != self:
                # Collision avec les côtés du bloc (x et y)
                if self.collision3D(self.collision.x + self.velocity[0], self.collision.y, objet) and type(objet) == Joueur:
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

        # On renvoie l'objet collisionné
        return collided_object


    def appliquer_velocite(self) -> None:
        """
        Cette méthode permet d'appliquer la vélocité à la position du pingouin.
        """

        # On ajoute la vélocité à la position du personnage
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        self.pos[2] += self.velocity[2]

        # On réinitialise la vélocité (sauf l'axe z qui est géré plus haut avec la gravité)
        self.velocity = [0, 0, self.velocity[2]]



# Classe d'une File (toujours très utile les files)
class File:

    # ------/ Constructeur \------

    def __init__(self) -> None:
        """
        Constructeur de la classe File.

        Attributs internes:
            - contenu (list): Représente le contenu de la file.
        """

        self.contenu = []


    # ------/ Méthodes \------

    def enfile(self, item: any) -> None:
        """
        Cette méthode permet d'enfiler un élément dans la file.

        Paramètres:
            - item (any): N'importe quel élément.
        """

        self.contenu = [item] + self.contenu


    def defile(self) -> any:
        """
        Cette méthode permet de défiler un élément de la file.

        Returns:
            - item (any): N'importe quel élément.

        Post-conditions:
            - La méthode renvoie l'élément à la fin de la file et le retire de la file.
            Si il n'y a pas d'élément, on renvoie None.
        """

        # Initialisation de l'élément à renvoyer
        elem = None

        if len(self.contenu) > 0:
            elem = self.contenu.pop()

        return elem


    def est_vide(self) -> bool:
        """
        Cette méthode indique si la file est vide ou non.

        Returns:
            - bool: Indique si la file est vide ou non.

        Post-conditions:
            - Si la file est vide, on renvoie True, sinon on renvoie False.
        """

        return len(self.contenu) == 0


    def taille(self) -> int:
        """
        Cette méthode indique la taille de la file.

        Returns:
            - int: représente la taille de la file.

        Post-conditions:
            - La méthode renvoie un nombre entier qui représente le nombre d'éléments qui
            constituent la file.
        """

        return len(self.contenu)



# Classe du serveur
class Server:
    def __init__(self, server_socket: socket.socket) -> None:
        """
        Documentation ici
            - score (list): Stockage du score de la partie.
        """

        self.server_socket = server_socket
        print("Initialisation du mini-jeu: Pushy Penguins")

        self.joueurs = {}
        self.inputs_joueurs = {}
        self.nb_joueurs_prets = 0

        # Initialisation d'un ordre aléatoire pour les mini-jeux
        self.ordre_minijeu = [i for i in range(4)]
        random.shuffle(self.ordre_minijeu)

        # Initialisation de la liste aléatoire de la taille possible des pingouins (il y a 1/16 chances de tomber sur une taille 3)
        self.pingouin_sizes = [1 for _ in range(15)] + [3]

        # Initialisation des timers cachés pour le mini-jeu
        self.temps_total = 0.155
        self.timer_pingouin = 0

        self.objets = []

        # Initialisation du timer
        self.timer = 30

        # Stockage du score et du classement de la partie
        self.score = {}
        self.classement = File()

        self.fps = 60
        self.current_fps = 0
        self.is_running = False

        # Initialisation des états de la partie
        self.etats = ["minigame_select", "minigame_load", "minigame_start", "minigame_during", "minigame_end", "minigame_score", "minigame_winners"]
        self.etat = self.etats[0]


    def get_classement(self):
        return self.classement

    def get_etat(self):
        return self.etat

    def get_nb_joueurs_prets(self):
        return self.nb_joueurs_prets


    def get_player(self, address: str):
        return self.joueurs[address]

    def add_player(self, address: str, perso: str, ia: bool):
        id_minijeu = self.ordre_minijeu[len(self.joueurs)]
        self.joueurs[address] = Joueur(perso, id_minijeu, ia)


    def client_thread(self, address: str, request: str) -> str:
            if request == "get_etat":
                reply = self.etat

            elif "taille_joueurs" in request:
                taille = json.loads(request)["taille_joueurs"]
                for ip in taille.keys():
                    self.joueurs[ip].set_taille([taille[ip][0], taille[ip][1]])
                reply = "ok"

            elif request == "get_pingouins":
                infos_pingouins = {objet.get_id_pingouin(): [
                    objet.get_pos(), objet.get_size(), round(objet.get_frame(), 5), objet.get_ground_height()
                ] for objet in self.objets if type(objet) == Pingouin}

                reply = json.dumps(infos_pingouins)

            elif "|" in request:
                # Si la requête c'est ça: 1|1|0
                self.inputs_joueurs[address] = [int(coord) for coord in request.split("|")]

                infos_joueurs = {joueur: {
                    "perso": self.joueurs[joueur].get_perso(),
                    "pos": self.joueurs[joueur].get_pos(),
                    "velocity": self.joueurs[joueur].get_velocity(),
                    "frame": self.joueurs[joueur].get_frame(),
                    "rotation": self.joueurs[joueur].get_rotation(),
                    "dead": self.joueurs[joueur].get_dead(),
                    "ground_height": self.joueurs[joueur].get_ground_height()
                } for joueur in self.joueurs.keys()}

                reply = json.dumps({"joueurs": infos_joueurs, "timer": round(self.timer - time.time()), "classement": {} if type(self.classement) == File else self.classement, "fps": self.current_fps})

            else:
                reply = "not_found"

            return reply


    def changer_etat(self, new_etat):
        self.etat = new_etat
        for ip in self.joueurs.keys():
            self.joueurs[ip].set_ready(False)

        print("[Pushy Penguins] Passé à l'état", self.etat)


    def load_game(self):
        ids_to_ips = {self.joueurs[joueur].get_id_minijeu(): joueur for joueur in self.joueurs.keys()}
        pos_joueurs = [[500, 450, -140], [664, 450, -140], [664, 250, -140], [500, 250, -140]]

        # On ajoute les joueurs dans le dictionnaires des inputs et on les positionne
        for i in range(4):
            self.inputs_joueurs[ids_to_ips[i]] = [0, 0, 0]
            self.joueurs[ids_to_ips[i]].set_pos(pos_joueurs[i])

        # On met à jour la liste d'objets
        self.objets = list(self.joueurs.values()) + [Banquise()]


    def during_game(self):
        # Liste des joueurs vivants (tous ceux avec un get_dead() == False)
        joueurs_vivants = list(filter(lambda x: not self.joueurs[x].get_dead(), self.joueurs.keys()))

        # Le mini-jeu s'arrête s'il ne reste plus de joueurs à part le joueur solo
        if self.timer - time.time() <= 0 or len(joueurs_vivants) <= 1:
            # On passe à l'état suivant
            self.changer_etat(self.etats[self.etats.index(self.etat) + 1])

            # Désactivation du timer
            self.timer = 0

        for joueur in self.joueurs.keys():
            # Comportement des ia
            if self.joueurs[joueur].get_ia():
                # On réinitialise leurs inputs
                self.inputs_joueurs[joueur] = [0, 0, 0]

                # Initialisation d'une position aléatoire choisie
                if self.joueurs[joueur].get_delai_ia() - time.time() < 0:
                    self.joueurs[joueur].set_ia_target_pos([random.randint(800, 1100), random.randint(300, 500)])
                    self.joueurs[joueur].set_delai_ia(1 + time.time())

                # Pathfinding de l'ia
                if self.joueurs[joueur].get_pos()[0] < self.joueurs[joueur].get_ia_target_pos()[0] - 10:
                    self.inputs_joueurs[joueur][0] += 1
                    self.joueurs[joueur].set_rotation("right")

                elif self.joueurs[joueur].get_pos()[0] > self.joueurs[joueur].get_ia_target_pos()[0] + 10:
                    self.inputs_joueurs[joueur][0] -= 1
                    self.joueurs[joueur].set_rotation("left")

                if self.joueurs[joueur].get_pos()[1] < self.joueurs[joueur].get_ia_target_pos()[1] - 10:
                    self.inputs_joueurs[joueur][1] += 1
                    self.joueurs[joueur].set_rotation("down")

                elif self.joueurs[joueur].get_pos()[1] > self.joueurs[joueur].get_ia_target_pos()[1] + 10:
                    self.inputs_joueurs[joueur][1] -= 1
                    self.joueurs[joueur].set_rotation("up")

            # Mise à jour de la rotation des joueurs
            if self.inputs_joueurs[joueur][0] > 0:
                self.joueurs[joueur].set_rotation("right")
            elif self.inputs_joueurs[joueur][0] < 0:
                self.joueurs[joueur].set_rotation("left")
            if self.inputs_joueurs[joueur][1] > 0:
                self.joueurs[joueur].set_rotation("down")
            elif self.inputs_joueurs[joueur][1] < 0:
                self.joueurs[joueur].set_rotation("up")

        # Logique du mini-jeu en elle même
        if time.time() - self.timer_pingouin > self.temps_total and self.timer - time.time() > 5:
            # Caractéristiques aléatoires du pingouin
            current_x = 1250
            current_y = random.randint(150, 650)
            current_speed = random.randint(4, 8)
            current_size = random.choice(self.pingouin_sizes)

            # On décale le gros pingouin pour pas qu'il tombe instantanément de la plateforme
            if current_size > 1:
                current_x -= 25 * current_size
                current_y -= 25 * current_size

            # Initialisation d'une liste de pingouins pour simplifier la suite
            pingouins = {objet.get_id_pingouin(): objet for objet in self.objets if type(objet) == Pingouin}

            # Création du nouvel identifiant du pingouin
            new_id = 0
            while new_id in pingouins.keys():
                new_id += 1

            # On crée le pingouin
            self.objets.append(Pingouin([current_x, current_y, -120], current_speed, current_size, new_id))

            # Réinitialisation du timer
            self.timer_pingouin = time.time()

            # Le temps que met chaque pingouin pour spawn se réduit
            self.temps_total -= 0.00028


    def calculate_score(self) -> None:
        """
        Cette méthode permet de calculer les scores de chaque joueur.
        """

        # Place du dernier joueur
        position = 4

        # Classement sous la forme d'un dictionnaire
        new_classement = {}

        # On défile les joueurs dans l'ordre et on note leur position dans le classement
        while not self.classement.est_vide():
            new_classement[self.classement.defile()] = position
            position -= 1

        # On remplace le format du classement pour le récupérer ensuite
        self.classement = new_classement

        # On détecte si des joueurs sont manquants et on les rajoute
        for joueur in self.joueurs.keys():
            if not joueur in self.classement:
                self.classement[joueur] = 1

        # Si tout le monde est gagnant
        if all([self.classement[joueur] == 1 for joueur in self.classement.keys()]):
            # Personne ne gagne car égalité (règle que je viens d'inventer)
            self.classement = {joueur: 0 for joueur in self.classement.keys()}

        # On saute une étape car pas nécessaire dans ce mini-jeu
        self.changer_etat(self.etats[self.etats.index(self.etat) + 1])


    def run(self, clock) -> None:
        self.is_running = True

        print("Lancement du mini-jeu: Pushy Penguins")
        while self.is_running:
            # On récupère le nombre de joueurs prêts (les ia sont automatiquement prêts)
            self.nb_joueurs_prets = len([joueur for joueur in self.joueurs.keys() if self.joueurs[joueur].get_ready() or self.joueurs[joueur].get_ia()])

            # Lorsque tous les joueurs sont prêts
            if len(self.joueurs.keys()) > 0 and self.nb_joueurs_prets == len(self.joueurs.keys()):
                # On finalise la création des joueurs avant que le jeu commence
                if self.etat == "minigame_load":
                    self.load_game()

                # Calcule le classement final
                elif self.etat == "minigame_end":
                    self.calculate_score()

                # Si on a fini le mini-jeu, on stoppe ce serveur
                if self.etat == "minigame_winners":
                    self.is_running = False

                # Sinon on passe à l'état suivant
                else:
                    self.changer_etat(self.etats[self.etats.index(self.etat) + 1])

                if self.etat == "minigame_during":
                    # Lancement du timer
                    self.timer = time.time() + self.timer

            # Calcul des frames pour la vitesse d'animation des personnages
            if self.etat != "minigame_load" and self.etat != "minigame_select":
                for joueur in self.joueurs.keys():
                    frame = self.joueurs[joueur].get_frame() + 0.24

                    # L'animation reste figée si le joueur est immobile
                    if self.inputs_joueurs[joueur][0] == 0 and self.inputs_joueurs[joueur][1] == 0:
                        frame = 0
                    elif self.joueurs[joueur].get_velocity()[2] != 0:
                        frame = 0

                    self.joueurs[joueur].set_frame(frame)

                    # On réinitialise les inputs des ia (pour éviter qu'ils de déplacent pendant le start ou le finish)
                    if self.joueurs[joueur].get_ia() and self.etat != "minigame_during":
                        self.inputs_joueurs[joueur] = [0, 0, 0]

                    # Calcul de la physique des joueurs
                    self.joueurs[joueur].calculer_velocite(self.inputs_joueurs[joueur])
                    self.joueurs[joueur].calculer_collisions(self.objets)
                    self.joueurs[joueur].appliquer_velocite()

                    # Détection de la mort
                    if self.joueurs[joueur].get_pos()[2] > -45 and not self.joueurs[joueur].get_dead():
                        self.joueurs[joueur].set_dead(True)

                        # On le stocke dans le classement sous forme de file
                        if type(self.classement) == File and self.classement.taille() < 4:
                            self.classement.enfile(joueur)

                for objet in self.objets:
                    if type(objet) == Pingouin:
                        # On met à jour la frame du pingouin
                        objet.set_frame(objet.get_frame() + 0.24)

                        # Calcul de la physique des pingouins
                        objet.calculer_velocite([-1, 0, 0])
                        objet.calculer_collisions(self.objets)
                        objet.appliquer_velocite()

                        # Détection de la mort
                        if objet.get_pos()[2] > -45:
                            self.objets.remove(objet)

            # Exécution du code qui gère le mini-jeu
            if self.etat == "minigame_during":
                self.during_game()

            if self.etat == "minigame_score":
                self.calculate_score()

            self.current_fps = clock.get_fps()
            clock.tick(self.fps)