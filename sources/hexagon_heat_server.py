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
        self.invincibility = 0
        self.dead = False

        # Uniquement pour l'ia (utilisé pour que les ia ne se retrouvent pas toutes exactement à la même position)
        self.target_offsets = [random.randint(-10, 110), random.randint(-10, 110)]

        # Le premier offset doit être plus petit que le second, on utilise donc sort
        self.target_offsets.sort()

        # On ajoute un délai aléatoire qui correspond au temps que l'ordi va mettre pour sauter
        # (Les randints sont en millisecondes pour avoir plus de précision, on divise par 1000 pour avoir les secondes)
        self.target_offsets.append(random.randint(-1000, 1000) / 1000)

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

    def get_invincibility(self) -> int:
        return self.invincibility

    def get_dead(self) -> bool:
        return self.dead

    def get_target_offsets(self) -> list:
        return self.target_offsets

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

    def set_invincibility(self, new_invincibility: int) -> None:
        self.invincibility = new_invincibility

    def set_dead(self, new_dead: bool) -> None:
        self.dead = new_dead

    def set_target_offsets(self, new_offset: list) -> None:
        self.target_offsets = new_offset

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


    def collision3D(self, x: "int | float", y: "int | float", objet: "Joueur | Hexagon") -> bool:
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
        assert type(objet) == Joueur or type(objet) == Hexagon, "Erreur: Le 3ème paramètre (objet) n'est pas un objet de type Joueur ou Hexagon."

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


    def calculer_collisions(self, objets: list) -> "Joueur | Hexagon | None":       # renvoie un objet (donc soit Joueur soit Hexagon) ou rien
        """
        Cette méthode permet de calculer les collisions en 3D avec le joueur.

        Paramètres:
            - objets (list): Liste d'objets avec lesquels le joueur doit calculer les collisions.

        Renvois:
            - Joueur ou Hexagon ou None: L'objet qui collisionne en-dessous du joueur.

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
            assert type(elem) == Joueur or type(elem) == Hexagon, "Erreur: La liste doit être seulement composée d'objets."

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

                # Collision avec le dessous du bloc
                for collision in objet.get_collisions():
                    if self.collision.colliderect(collision):
                        if objet.get_pos()[2] < self.pos[2]:
                            self.priority = -self.collision.bottom + collision.h + self.pos[2]
                        if objet.get_pos()[2] - objet.get_height() + collision.h > self.pos[2] + self.velocity[2] and self.ground_height >= objet.get_pos()[2]:
                            if self.velocity[2] <= 0 and self.pos[2] > objet.get_pos()[2]:
                                if self.velocity[2] != 0:
                                    self.velocity[2] = 4        # Valeur arbitraire pour le faire "rebondir" en dessous du bloc
                                else:
                                    self.velocity[2] = 0

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


    def invicible_mode(self) -> None:
        """
        Cette méthode permet de gérer l'invulnérabilité du joueur.
        """

        # Baisse de vitesse tant qu'il est invulnérable
        if self.invincibility > 0:
            self.invincibility -= 1
            self.speed = 3.6

        # Sinon valeur par défaut
        else:
            self.invincibility = 0
            self.speed = 5.6


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


    def sauter(self) -> None:
        """
        Cette méthode permet au joueur de sauter dans l'axe z.
        """

        # Le joueur saute uniquement s'il est mort (car animation de saut) ou sur le sol
        if self.pos[2] == self.ground_height or self.dead:
            # On applique la puissance de saut à la vélocité
            self.velocity[2] = -self.jump_power



# Classe d'une plateforme sous la forme d'un hexagone
class Hexagon:

    # ------/ Constructeur \------

    def __init__(self, pos, color) -> None:
        """
        Constructeur de la classe Hexagon.

        Attributs à définir:
            - pos (list): Position de l'hexagone.
            - color (str): Couleur de l'hexagone.

        Attributs internes:
            - hidden (bool): Indique si le sprite est affiché ou non.

            - collisions (list): Boîtes de collision de l'hexagone.

            - height (int): Hauteur du sprite de l'hexagone.
        """

        # Caractéristiques par défaut
        self.pos = pos
        self.color = color
        self.velocity = [0, 0, 0]
        self.speed = 2

        # Initialisation de la variable hidden
        self.hidden = False

        # Boîtes de collision de l'hexagone
        self.collisions =  [pygame.Rect(0, 0, 15*4, 26*4),
                            pygame.Rect(0, 0, 12*4, 40*4),
                            pygame.Rect(0, 0, 15*4, 26*4)]

        # La position Z correspond au point le plus haut du bloc (en comptant seulement la plus haute collision, ici la 2ème)
        self.height = self.collisions[1].h - 212


    # ------/ Getters \------

    def get_pos(self) -> list:
        return self.pos

    def get_color(self) -> str:
        return self.color

    def get_hidden(self) -> bool:
        return self.hidden

    def get_collisions(self) -> list:
        return self.collisions

    def get_height(self) -> int:
        return self.height


    # ------/ Setters \------

    def set_pos(self, new_pos: list) -> None:
        self.pos = new_pos

    def set_velocity(self, new_velocity: list) -> None:
        self.velocity = new_velocity

    def set_hidden(self, new_hidden: bool) -> None:
        self.hidden = new_hidden


    # ------/ Méthodes \------

    def calculer_velocite(self) -> None:
        """
        Cette méthode permet de calculer la vélocité de la plateforme à partir de la vélocité définie à la base.
        """

        # On change la vitesse de la plateforme en fonction de si elle remonte ou redescend
        if self.velocity[2] > 0:
            self.speed = 2
        elif self.velocity[2] < 0:
            self.speed = 4

        # On change seulement la coordonnée z car la plateforme se déplace uniquement en z
        self.velocity[2] = self.velocity[2] * self.speed

    def calculer_collisions(self) -> None:
        """
        Cette méthode permet de mettre à jour les positions des collisions de l'hexagone.
        """

        # Récursivité pour calculer la position en x de chaque collision
        # Pour que chaque collision soit côte à côte, il faut la taille x de toutes les collisions avant la collision donnée
        # (j'utilise lambda pour éviter de mettre des def dans des def)
        get_collision_offset = lambda indice: 0 if indice == 0 else self.collisions[indice - 1].w + get_collision_offset(indice - 1)

        # Calculs et positionnement différents pour chaque collision
        for i in range(len(self.collisions)):
            self.collisions[i].x = round(self.pos[0])
            self.collisions[i].x += get_collision_offset(i)
            self.collisions[i].y = round(self.pos[1]) + 52 + 32 if i % 2 == 0 else round(self.pos[1]) + 52

    def appliquer_velocite(self) -> None:
        """
        Cette méthode permet d'appliquer la vélocité à la position.
        """

        # On ajoute la vélocité à la position du personnage
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        self.pos[2] += self.velocity[2]

        # On réinitialise la vélocité
        self.velocity = [0, 0, 0]



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



# Classe du serveur
class Server:
    def __init__(self, server_socket: socket.socket) -> None:
        """
        Documentation ici
            - score (list): Stockage du score de la partie.
        """

        self.server_socket = server_socket
        print("Initialisation du mini-jeu: Hexagon Heat")

        self.joueurs = {}
        self.inputs_joueurs = {}
        self.nb_joueurs_prets = 0

        # Initialisation d'un ordre aléatoire pour les mini-jeux
        self.ordre_minijeu = [i for i in range(4)]
        random.shuffle(self.ordre_minijeu)

        # Liste des couleurs des plateformes et couleur actuel du tour
        self.colors = ["blue", "green", "magenta", "pink", "cyan", "yellow", "red"]
        self.couleur_actuelle = random.choice(self.colors)

        # Initialisation d'une variable indiquant l'affichage de toad au client
        self.toad_actif = False

        # Initialisation des timers cachés pour le mini-jeu
        self.temps_total = 5
        self.timer_tour = 0

        # Initialisation des hexagones présents dans le mini-jeu
        positions_hexagones = {"blue": [450, 178, -60],
                               "green": [618, 178, -60],
                               "magenta": [366, 298, -60],
                               "pink": [534, 298, -60],
                               "cyan": [702, 298, -60],
                               "yellow": [450, 418, -60],
                               "red": [618, 418, -60]}
        self.hexagones = [Hexagon(pos, color) for color, pos in positions_hexagones.items()]

        self.objets = []

        # Stockage du score et du classement de la partie
        self.score = {}
        self.classement = Pile()

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

            elif "|" in request:
                # Si la requête c'est ça: 1|1|0
                self.inputs_joueurs[address] = [int(coord) for coord in request.split("|")]

                infos_joueurs = {joueur: {
                    "perso": self.joueurs[joueur].get_perso(),
                    "pos": self.joueurs[joueur].get_pos(),
                    "velocity": self.joueurs[joueur].get_velocity(),
                    "frame": self.joueurs[joueur].get_frame(),
                    "rotation": self.joueurs[joueur].get_rotation(),
                    "invincibility": self.joueurs[joueur].get_invincibility(),
                    "dead": self.joueurs[joueur].get_dead(),
                    "ground_height": self.joueurs[joueur].get_ground_height()
                } for joueur in self.joueurs.keys()}

                infos_hexagones = {hexagone.get_color(): {
                    "pos": hexagone.get_pos(),
                    "hidden": hexagone.get_hidden()
                } for hexagone in self.hexagones}

                reply = json.dumps({"joueurs": infos_joueurs, "hexagones": infos_hexagones, "couleur": (self.couleur_actuelle, self.toad_actif), "classement": {} if type(self.classement) == Pile else self.classement, "fps": self.current_fps})

            else:
                reply = "not_found"

            return reply


    def changer_etat(self, new_etat):
        self.etat = new_etat
        for ip in self.joueurs.keys():
            self.joueurs[ip].set_ready(False)

        print("[Hexagon Heat] Passé à l'état", self.etat)


    def load_game(self):
        ids_to_ips = {self.joueurs[joueur].get_id_minijeu(): joueur for joueur in self.joueurs.keys()}
        pos_joueurs = [[500, 450, -450], [664, 450, -450], [664, 250, -450], [500, 250, -450]]

        # On ajoute les joueurs dans le dictionnaires des inputs et on les positionne
        for i in range(4):
            self.inputs_joueurs[ids_to_ips[i]] = [0, 0, 0]
            self.joueurs[ids_to_ips[i]].set_pos(pos_joueurs[i])

        # On met à jour la liste d'objets
        self.objets = list(self.joueurs.values()) + self.hexagones


    def during_game(self):
        # Liste des joueurs vivants (tous ceux avec un get_dead() == False)
        joueurs_vivants = list(filter(lambda x: not self.joueurs[x].get_dead(), self.joueurs.keys()))

        # Le mini-jeu s'arrête s'il ne reste plus de joueurs à part le joueur solo
        if len(joueurs_vivants) <= 1:
            # On stocke le dernier survivant s'il n'est pas déjà mort
            if self.classement.taille() < 4 and len(joueurs_vivants) == 1:
                self.classement.empile(joueurs_vivants[0])

            # On fait remonter les hexagones s'ils ne le sont pas déjà
            for hexagone in self.hexagones:
                hexagone.set_hidden(False)
                hexagone.set_pos([hexagone.get_pos()[0], hexagone.get_pos()[1], -60])

            # On passe à l'état suivant
            self.changer_etat(self.etats[self.etats.index(self.etat) + 1])

        for joueur in self.joueurs.keys():
            # Comportement des ia
            if self.joueurs[joueur].get_ia():
                # On réinitialise leurs inputs
                self.inputs_joueurs[joueur] = [0, 0, 0]

                # Initialisation de l'hexagone visé
                current_hexagon = None
                for hexagon in self.hexagones:
                    # On choisit l'hexagone seulement s'il est complètement sortit du sol
                    if hexagon.get_color() == self.couleur_actuelle and hexagon.get_pos()[2] <= -60:
                        current_hexagon = hexagon

                # Pathfinding de l'ia
                if current_hexagon != None:

                    # Les targets offsets servent à mettre de l'aléatoire un peu partout dans les mouvements
                    # de l'ia pour qu'elle soit moins parfaite
                    x_offset_min = current_hexagon.get_pos()[0] + self.joueurs[joueur].get_target_offsets()[0]
                    x_offset_max = current_hexagon.get_pos()[0] + self.joueurs[joueur].get_target_offsets()[1]
                    y_offset_min = current_hexagon.get_pos()[1] + self.joueurs[joueur].get_target_offsets()[0]
                    y_offset_max = current_hexagon.get_pos()[1] + self.joueurs[joueur].get_target_offsets()[1]

                    # L'ia se déplace en fonction des coordonnées trouvées
                    if self.joueurs[joueur].get_pos()[0] < x_offset_min and self.joueurs[joueur].get_pos()[0] < x_offset_max:
                        self.inputs_joueurs[joueur][0] += 1
                        self.joueurs[joueur].set_rotation("right")

                    elif self.joueurs[joueur].get_pos()[0] > x_offset_min and self.joueurs[joueur].get_pos()[0] > x_offset_max:
                        self.inputs_joueurs[joueur][0] -= 1
                        self.joueurs[joueur].set_rotation("left")

                    if self.joueurs[joueur].get_pos()[1] < y_offset_min and self.joueurs[joueur].get_pos()[1] < y_offset_max:
                        self.inputs_joueurs[joueur][1] += 1
                        self.joueurs[joueur].set_rotation("down")

                    elif self.joueurs[joueur].get_pos()[1] > y_offset_min and self.joueurs[joueur].get_pos()[1] > y_offset_max:
                        self.inputs_joueurs[joueur][1] -= 1
                        self.joueurs[joueur].set_rotation("up")

                    # Délai aléatoire du saut
                    time_offset = 3 + self.joueurs[joueur].get_target_offsets()[2]

                    # L'ia saute un peu avant (dans un durée aléatoire) le moment où les hexagones s'enfoncent dans la lave
                    if time.time() - self.timer_tour > self.temps_total - time_offset and time.time() - self.timer_tour < self.temps_total - time_offset + 1:
                        self.joueurs[joueur].sauter()

            # On tire si le joueur client a envoyé l'input correspondant
            if self.inputs_joueurs[joueur][2] > 0:
                self.joueurs[joueur].sauter()

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
        if time.time() - self.timer_tour > self.temps_total:
            # Choix d'une nouvelle couleur aléatoire
            self.couleur_actuelle = random.choice(self.colors)

            # Réinitialisation du timer
            self.timer_tour = time.time()

            for joueur in self.joueurs.values():
                if joueur.get_ia():
                    # Définition de nouveau décalages pour les ias
                    new_target_offsets = [random.randint(-10, 110), random.randint(-10, 110)]
                    new_target_offsets.sort()
                    new_target_offsets.append(random.randint(-1000, 1000) / 1000)
                    joueur.set_target_offsets(new_target_offsets)

        # Affichage de la bulle de dialogue pendant une petite durée
        elif time.time() - self.timer_tour < self.temps_total - 2:
            self.toad_actif = True

        # Fin du temps imparti
        else:
            self.toad_actif = False

            # Descente de tous les hexagones (sauf celui de la couleur choisie)
            for hexagon in self.hexagones:
                if hexagon.get_color() != self.couleur_actuelle:
                    if hexagon.get_pos()[2] < 10:
                        # On applique de la vélocité pour les faire descendre
                        hexagon.set_velocity([0, 0, 1])
                    else:
                        # On cache les hexagones une fois qu'ils sont assez descendus
                        hexagon.set_hidden(True)

        # Dès que le timer se relance
        if time.time() - self.timer_tour < self.temps_total - 2:
            # Tous les hexagones remontent (et on les re-affiche accessoirement)
            for hexagon in self.hexagones:
                if hexagon.get_pos()[2] > -60:
                    hexagon.set_hidden(False)
                    hexagon.set_velocity([0, 0, -1])
                else:
                    hexagon.set_pos([hexagon.get_pos()[0], hexagon.get_pos()[1], -60])

        # Le temps diminue petit à petit jusqu'à atteindre 2.4s
        if self.temps_total > 2.4:
            self.temps_total -= 0.0012


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
            new_classement[self.classement.depile()] = position
            position += 1

        # On remplace le format du classement pour le récupérer ensuite
        self.classement = new_classement

        # On saute une étape car pas nécessaire dans ce mini-jeu
        self.changer_etat(self.etats[self.etats.index(self.etat) + 1])


    def run(self, clock) -> None:
        self.is_running = True

        print("Lancement du mini-jeu: Hexagon Heat")
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

                    # On peut utiliser calculate_collisions() pour récupérer l'entité avec laquelle le joueur collisionne
                    collision = self.joueurs[joueur].calculer_collisions(self.objets)

                    # Par exemple, ce petit bout de code permet au joueur de ralentir un autre joueur en sautant sur sa tête
                    if type(collision) == Joueur and self.joueurs[joueur].get_pos()[2] < collision.get_height() and self.joueurs[joueur].get_velocity()[2] == 0:
                        self.joueurs[joueur].sauter()

                        # S'il n'est pas déjà invulnérable
                        if collision.get_invincibility() == 0:
                            # Ici, 200 frames d'invulnérabilité
                            collision.set_invincibility(200)

                    # On réduit petit à petit l'invincibilité
                    if self.joueurs[joueur].get_invincibility() > -1:
                        self.joueurs[joueur].invicible_mode()

                    # On applique le mouvement au joueur
                    self.joueurs[joueur].appliquer_velocite()

                    # Détection de la mort
                    if self.joueurs[joueur].get_pos()[2] > -45 and not self.joueurs[joueur].get_dead():
                        self.joueurs[joueur].set_dead(True)
                        self.joueurs[joueur].sauter()

                        # On le stocke dans le classement sous forme de pile
                        if self.classement.taille() < 4:
                            self.classement.empile(joueur)

                # On calcule la physique de chaque hexagone
                for hexagone in self.hexagones: 
                    hexagone.calculer_velocite()
                    hexagone.calculer_collisions()
                    hexagone.appliquer_velocite()

            # Exécution du code qui gère le mini-jeu
            if self.etat == "minigame_during":
                self.during_game()

            if self.etat == "minigame_score":
                self.calculate_score()

            self.current_fps = clock.get_fps()
            clock.tick(self.fps)