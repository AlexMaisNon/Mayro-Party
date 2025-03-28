#Projet : Mayro Party
#Auteurs : Hinata Bouaziz, Antoine Desrues, Alexandre Guillaume, Matisse Moreau

# ------/ Importations des bibliothèques \------

import pygame
from math import sqrt
import time
import random

import json
import socket

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
class Joueur:

    # ------/ Constructeur \------

    def __init__(self, perso: str, id_minijeu: int, ia: bool, type_joueur: str) -> None:
        """
        Constructeur de la classe Joueur.

        Attributs à définir:
            - perso (str): Personnage choisit par le joueur.
            - id_minijeu (int): id du joueur qui sert uniquement lors des mini-jeux.
            - ia (bool): Indique si le joueur est une ia ou un joueur lambda.
            - type_joueur (str): Si le joueur est en solo ou en équipe (solo ou panneau) (exclusif à ce mini-jeu).

        Attributs internes:
            - pos (list): Position du joueur.
            - velocity (list): Vélocité/Accélération du joueur.
            - speed (int): Vitesse du joueur.

            - frame (float): Indice du sprite à choisir.

            - collision (pygame.Rect): Boîte de collision du joueur.

            - taille (list): Dimensions du sprite du joueur (fournis par le client).
        """

        # Tests du type des paramètres donnés
        assert type(perso) == str, "Erreur: Le 1er paramètre (perso) est censé être une chaîne de caractères."
        assert type(id_minijeu) == int, "Erreur: Le 2ème paramètre (id) est censé être un entier."
        assert type(ia) == bool, "Erreur: Le 3ème paramètre (ia) est censé être un booléen."
        assert type(type_joueur) == str, "Erreur: Le 4ème paramètre (type_joueur) est censé être une chaîne de caractères."

        # Définition du joueur
        self.perso = perso
        self.id_minijeu = id_minijeu
        self.ia = ia
        self.type_joueur = type_joueur
        self.ready = False

        # Caractéristiques principales (stats)
        self.pos = [0, 0]
        self.velocity = [0, 0]
        self.speed = 1.2 if self.type_joueur == "panneau" else 3
        self.rotation = "left"
        self.dead = False

        # Un délai qui servira à faire se déplacer les ias aléatoirement
        self.cooldown_movement = 0

        # Initialisation des paramètres du tir
        self.etat_tir = "recharge"              # (change entre recharge et tir)
        self.cooldown_tir = 0

        # Initialisation de la frame choisie
        self.frame = 0

        # Boîte de collision du personnage
        self.collision = pygame.Rect(0, 0, 64, 124) if self.type_joueur == "panneau" else None

        # Initialisation de la taille du joueur (qui sera définie lors du début de partie)
        self.taille = [0, 0]

        # Initialisation des conditions du lancement du son de tir
        self.lancer_son_tir = False


    # ------/ Getters \------

    def get_perso(self) -> str:
        return self.perso

    def get_id_minijeu(self) -> int:
        return self.id_minijeu

    def get_ia(self) -> bool:
        return self.ia

    def get_type_joueur(self) -> str:
        return self.type_joueur

    def get_ready(self) -> bool:
        return self.ready

    def get_pos(self) -> list:
        return self.pos

    def get_rotation(self) -> str:
        return self.rotation

    def get_dead(self) -> bool:
        return self.dead

    def get_cooldown_movement(self) -> float:
        return self.cooldown_movement

    def get_etat_tir(self) -> str:
        return self.etat_tir

    def get_cooldown_tir(self) -> float:
        return self.cooldown_tir

    def get_frame(self) -> float:
        return self.frame

    def get_collisions(self) -> list:
        return [self.collision]

    def get_taille(self) -> list:
        return self.taille

    def get_lancer_son_tir(self) -> bool:
        return self.lancer_son_tir


    # ------/ Setter \------

    def set_ready(self, new_ready: bool) -> None:
        self.ready = new_ready

    def set_pos(self, new_pos: list) -> None:
        self.pos = new_pos

    def set_rotation(self, new_rotation: str) -> None:
        self.rotation = new_rotation

    def set_dead(self, new_dead: bool) -> None:
        self.dead = new_dead

    def set_cooldown_movement(self, new_cooldown_movement: float) -> None:
        self.cooldown_movement = new_cooldown_movement

    def set_etat_tir(self, new_etat_tir: str) -> None:
        self.etat_tir = new_etat_tir

    def set_frame(self, new_frame: float) -> None:
        self.frame = new_frame

    def set_taille(self, new_taille: list) -> None:
        self.taille = new_taille

    def set_lancer_son_tir(self, new_lancer_son_tir) -> None:
        self.lancer_son_tir = new_lancer_son_tir


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
        assert type(direction) == list, "Erreur: Le 1er paramètre (direction) n'est pas une liste."

        # Test des valeurs dans direction
        for elem in direction:
            assert elem >= -1 and elem <= 1, "Erreur: Une des valeurs dans la direction donnée n'est pas valide."

        # On change seulement la coordonnée x car le joueur se déplace uniquement en x
        self.velocity[0] = direction[0] * self.speed


    def calculer_collisions(self, objets: list) -> None:
        """
        Cette méthode permet de calculer les collisions avec le joueur.

        Paramètres:
            - objets (list): Liste d'objets avec lesquels le joueur doit calculer les collisions.

        Pré-conditions:
            - objets doit contenir seulement des objets de type Carapace, Collider, But et Joueur.
        """

        # Test du type de objets
        assert type(objets) == list, "Erreur: Le paramètre donné (objets) n'est pas une liste."

        # Tests des éléments de objets
        for elem in objets:
            assert type(elem) == Joueur or type(elem) == Ennemi or type(elem) == Fleche, "Erreur: La liste doit être seulement composée d'objets."

        if self.type_joueur == "panneau":
            # On positionne la boîte de collision par rapport à la position du joueur
            self.collision.x = round(self.pos[0])
            self.collision.y = round(self.pos[1])

            # Calcul des collisions pour chaque objets
            for objet in objets:
                # Pas mal de tests pour éviter de collisionner avec des élément indésirables
                if objet != self and type(objet) != Fleche and not objet.get_dead():
                    # On ne calcule pas si le joueur est le joueur solo
                    if self.collision != None:
                        # Pas de rect_y parce que le joueur est bloqué sur l'axe x
                        rect_x = pygame.Rect(round(self.collision.x + self.velocity[0]), self.collision.y, self.collision.w, self.collision.h)

                        # On stoppe la vélocité du joueur si il collisionne avec une boîte de collision
                        for collision in objet.get_collisions():
                            if collision != None and rect_x.colliderect(collision):
                                self.velocity[0] = 0


    def appliquer_velocite(self) -> None:
        """
        Cette méthode permet d'appliquer la vélocité à la position.
        """

        # On ajoute la vélocité à la position du personnage
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        
        # Applications différentes selon le type du joueur
        if self.type_joueur == "panneau":
            # La position du joueur est bloquée entre ces deux intervalles
            self.pos[0] = max(300, min(self.pos[0], 920))

        else:
            # La position du joueur est bloquée entre ces deux intervalles
            self.pos[0] = max(150, min(self.pos[0], 900))

        # On réinitialise la vélocité (sinon effet Asteroids (le personnage glisse infiniment))
        self.velocity = [0, 0]


    def tirer(self, objets: list) -> None:
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
        if self.cooldown_tir - time.time() <= 0:

            # Envoie le son au client et change le sprite actuel du pistolet
            self.lancer_son_tir = True
            self.etat_tir = "tir"

            # Initialisation d'une liste de flèches pour simplifier la suite
            fleches = {objet.get_id_fleche(): objet for objet in objets if type(objet) == Fleche}

            # Création du nouvel identifiant de la flèche
            new_id = 0
            while new_id in fleches.keys():
                new_id += 1

            # Création du projectile (à la base censé être une flèche) dans la liste d'objets
            objets.append(Fleche([round(self.pos[0] + self.taille[0] - 33), round(self.pos[1] + 89)], new_id))

            # Applique 2s de délai
            self.cooldown_tir = 2 + time.time()



# Classe de l'ennemi
class Ennemi:

    # ------/ Constructeur \------

    def __init__(self) -> None:
        """
        Constructeur de la classe Ennemi.

        Attributs internes:
            - pos (list): Position de l'ennemi.
            - velocity (list): Vélocité/Accélération de l'ennemi.
            - speed (int): Vitesse de l'ennemi.
            - rotation (str): Rotation de l'ennemi.
            - dead (bool): Définit si l'ennemi est mort ou non.

            - move_cooldown (float): Un délai aléatoire pour chaque mouvement de l'ennemi.

            - collision (pygame.Rect ou None): Boîte de collision de l'ennemi.
        """

        # Caractéristiques principales (stats)
        self.pos = [0, 0]
        self.velocity = [0, 0]
        self.speed = 1.2
        self.rotation = "left"
        self.dead = False

        # Un délai qui servira à faire se déplacer l'ennemi aléatoirement
        self.move_cooldown = 0

        # Boîte de collision de l'ennemi
        self.collision = pygame.Rect(0, 0, 64, 124)


    # ------/ Getters \------

    def get_pos(self) -> list:
        return self.pos

    def get_rotation(self) -> str:
        return self.rotation

    def get_collisions(self) -> list:
        return [self.collision]

    def get_dead(self) -> bool:
        return self.dead

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

    def calculer_velocite(self, direction: list) -> None:
        """
        Cette méthode permet de calculer la vélocité de l'ennemi (exactement la même méthode que dans la classe Joueur).

        Paramètres:
            - direction (list): Direction sous forme de vecteur dans laquelle l'ennemi se déplace.

        Pré-conditions:
            - direction doit être compris entre -1 et 1.
        """

        # Test des types de variables
        assert type(direction) == list, "Erreur: Le 1er paramètre (direction) n'est pas une liste."

        # Test des valeurs dans direction
        for elem in direction:
            assert elem >= -1 and elem <= 1, "Erreur: Une des valeurs dans la direction donnée n'est pas valide."

        # On change seulement la coordonnée x car l'ennemi se déplace uniquement en x
        self.velocity[0] = direction[0] * self.speed


    def calculer_collisions(self, objets: list) -> None:
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

        # On positionne la boîte de collision par rapport à la position de l'ennemi
        self.collision.x = round(self.pos[0])
        self.collision.y = round(self.pos[1])

        # Calcul des collisions pour chaque objets
        for objet in objets:
            # Pas mal de tests pour éviter de collisionner avec des élément indésirables
            if objet != self and type(objet) != Fleche and not objet.get_dead():
                # Pas de rect_y parce que l'ennemi est bloqué sur l'axe x
                rect_x = pygame.Rect(round(self.collision.x + self.velocity[0]), self.collision.y, self.collision.w, self.collision.h)

                # On stoppe la vélocité de l'ennemi si il collisionne avec une boîte de collision
                for collision in objet.get_collisions():
                    if collision != None and rect_x.colliderect(collision):
                        self.velocity[0] = 0


    def appliquer_velocite(self) -> None:
        """
        Cette méthode permet d'appliquer la vélocité à la position et à d'autres paramètres de l'ennemi.
        """

        # On ajoute la vélocité à la position du personnage
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]

        # La position de l'ennemi est bloquée entre ces deux intervalles
        self.pos[0] = max(300, min(self.pos[0], 920))

        # On réinitialise la vélocité (sinon effet Asteroids (le personnage glisse infiniment))
        self.velocity = [0, 0]



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

            - collision (pygame.Rect ou None): Boîte de collision de la flèche.
        """

        # Tests du type des paramètres donnés
        assert type(pos) == list, "Erreur: Le 1er paramètre (pos) est censé être une liste."
        assert type(id_fleche) == int, "Erreur: Le 2ème paramètre (id_fleche) est censé être un nombre entier."


        # Caractéristiques de la flèche
        self.pos = pos
        self.id_fleche = id_fleche
        self.velocity = [0, 0]
        self.speed = 5

        # Boîte de collision de la flèche
        self.collision = pygame.Rect(0, 0, 20, 46)


    # ------/ Getters \------

    def get_pos(self) -> list:
        return self.pos

    def get_id_fleche(self) -> int:
        return self.id_fleche

    def get_collisions(self) -> list:
        return [self.collision]


    # ------/ Méthodes \------

    def calculer_velocite(self, direction: list) -> None:
        """
        Cette méthode permet de calculer la vélocité de la flèche (méthode similaire avec celles des classes précédentes).

        Paramètres:
            - direction (list): Direction sous forme de vecteur dans laquelle la flèche se déplace.

        Pré-conditions:
            - direction doit être compris entre -1 et 1.
        """

        # Test des types de variables
        assert type(direction) == list, "Erreur: Le 1er paramètre (direction) n'est pas une liste."

        # Test des valeurs dans direction
        for elem in direction:
            assert elem >= -1 and elem <= 1, "Erreur: Une des valeurs dans la direction donnée n'est pas valide."

        # On change seulement la coordonnée y car la flèche se déplace uniquement en y
        self.velocity[1] = direction[1] * self.speed


    def calculer_collisions(self, objets: list) -> None:
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

        # On positionne la boîte de collision par rapport à la position de la flèche
        self.collision.x = round(self.pos[0])
        self.collision.y = round(self.pos[1] + 46)

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
                        # On tue l'objet
                        objet.set_dead(True)

                        # On supprime la flèche de la liste d'objets
                        if self in objets:
                            objets.remove(self)


    def appliquer_velocite(self) -> None:
        """
        Cette méthode permet d'appliquer la vélocité à la position et à d'autres paramètres de la flèche.
        """

        # On ajoute la vélocité à la position de la flèche (pas de vélocity[0] car se déplace qu'en y)
        self.pos[1] += self.velocity[1]

        # On réinitialise la vélocité (sinon effet Asteroids (la flèche glisse indéfiniment et contre le principe de vélocité))
        self.velocity = [0, 0]



# Classe du serveur
class Server:
    def __init__(self, server_socket: socket.socket) -> None:
        """
        Documentation ici
            - timer (float): Durée du mini-jeu.

            - score (list): Stockage du score de la partie.
        """

        self.server_socket = server_socket
        print("Initialisation du mini-jeu: Archer Ival")

        self.joueurs = {}
        self.inputs_joueurs = {}
        self.nb_joueurs_prets = 0

        # Initialisation d'un ordre aléatoire pour les mini-jeux
        self.ordre_minijeu = [i for i in range(4)]
        random.shuffle(self.ordre_minijeu)

        self.ennemis = []
        self.directions_ennemis = {}
        self.objets = []

        # Initialisation du timer
        self.timer = 30

        # Stockage du score et du classement de la partie
        self.score = {}
        self.classement = {}

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
        self.joueurs[address] = Joueur(perso, id_minijeu, ia, "solo" if id_minijeu == 0 else "panneau")


    def client_thread(self, address: str, request: str) -> str:
            if request == "get_etat":
                reply = self.etat

            elif "taille_joueurs" in request:
                taille = json.loads(request)["taille_joueurs"]
                for ip in taille.keys():
                    self.joueurs[ip].set_taille([taille[ip][0], taille[ip][1]])
                reply = "ok"

            elif request == "desactive_son_tir":
                self.joueurs[address].set_lancer_son_tir(False)
                reply = "ok"

            elif "|" in request:
                # Si la requête c'est ça: 1|1|0
                self.inputs_joueurs[address] = [int(coord) for coord in request.split("|")]

                infos_joueurs = {joueur: {
                    "perso": self.joueurs[joueur].get_perso(),
                    "type_joueur": self.joueurs[joueur].get_type_joueur(),
                    "pos": self.joueurs[joueur].get_pos(),
                    "frame": self.joueurs[joueur].get_frame(),
                    "rotation": self.joueurs[joueur].get_rotation(),
                    "dead": self.joueurs[joueur].get_dead(),
                    "etat_tir": self.joueurs[joueur].get_etat_tir(),
                    "lancer_son_tir": self.joueurs[joueur].get_lancer_son_tir()
                } for joueur in self.joueurs.keys()}

                infos_ennemis = [{
                    "pos": ennemi.get_pos(),
                    "rotation": ennemi.get_rotation(),
                    "dead": ennemi.get_dead()
                } for ennemi in self.ennemis]

                infos_fleches = {objet.get_id_fleche(): objet.get_pos() for objet in self.objets if type(objet) == Fleche}

                reply = json.dumps({"joueurs": infos_joueurs, "ennemis": infos_ennemis, "fleches": infos_fleches, "timer": round(self.timer - time.time()), "classement": self.classement, "fps": self.current_fps})

            else:
                reply = "not_found"

            return reply


    def changer_etat(self, new_etat):
        self.etat = new_etat
        for ip in self.joueurs.keys():
            self.joueurs[ip].set_ready(False)

        print("[Archer-Ival] Passé à l'état", self.etat)


    def load_game(self):
        ids_to_ips = {self.joueurs[joueur].get_id_minijeu(): joueur for joueur in self.joueurs.keys()}
        pos_joueurs = [[500, 400], [400, 216], [600, 216], [800, 216]]

        # On ajoute les joueurs dans le dictionnaires des inputs et on les positionne
        for i in range(4):
            self.inputs_joueurs[ids_to_ips[i]] = [0, 0, 0]
            self.joueurs[ids_to_ips[i]].set_pos(pos_joueurs[i])

        # Création / positionnement des ennemis dans la liste d'entités
        self.ennemis.append(Ennemi())
        self.ennemis[-1].set_pos([500, 216])

        self.ennemis.append(Ennemi())
        self.ennemis[-1].set_pos([700, 216])

        # On met à jour la liste d'objets
        self.objets = list(self.joueurs.values()) + self.ennemis


    def during_game(self):
        # Liste des joueurs vivants (tous ceux avec un get_dead() == False) sans compter le joueur solo
        joueurs_vivants = [joueur for joueur in self.joueurs.values() if not joueur.get_dead() and joueur.get_type_joueur() == "panneau"]

        # Le mini-jeu s'arrête si le timer s'arrête ou qu'il ne reste plus de joueurs à part le joueur solo
        if self.timer - time.time() <= 0 or len(joueurs_vivants) < 1:
            # On passe à l'état suivant
            self.changer_etat(self.etats[self.etats.index(self.etat) + 1])

            # Désactivation du timer
            self.timer = 0

        for joueur in self.joueurs.keys():
            # Comportement des ia (pathfinding assez mid honnêtement)
            if self.joueurs[joueur].get_ia():
                # On réinitialise leurs inputs
                self.inputs_joueurs[joueur] = [0, 0, 0]

                # Comportement ia du joueur solo
                if self.joueurs[joueur].get_type_joueur() == "solo":
                    # Ne peut pas bouger pendant ce délai
                    if self.joueurs[joueur].get_cooldown_movement() - time.time() <= 0:
                        # Vise uniquement le dernier joueur vivant de la liste
                        joueur_target = joueurs_vivants[-1]

                        # Suit la position du joueur visé (en fonction de la position du pistolet du joueur solo)
                        if joueur_target.get_pos()[0] - 10 > self.joueurs[joueur].get_pos()[0] + self.joueurs[joueur].get_taille()[0] - 48:
                            self.inputs_joueurs[joueur][0] += 1
                        elif joueur_target.get_pos()[0] + 10 < self.joueurs[joueur].get_pos()[0] + self.joueurs[joueur].get_taille()[0] - 48:
                            self.inputs_joueurs[joueur][0] -= 1

                        # Sinon tire car il est dans la zone de tir
                        else:
                            self.inputs_joueurs[joueur][2] = 1

                            # Nouveau délai entre 0.5s et 1s
                            nouveau_delai = random.randint(5, 10) / 10
                            self.joueurs[joueur].set_cooldown_movement(nouveau_delai + time.time())

                # Comportement de l'ia sur les panneaux
                else:
                    # Ne peut pas changer de direction pendant le délai
                    if self.joueurs[joueur].get_cooldown_movement() - time.time() <= 0:
                        # Choisit une rotation (direction) aléatoire
                        nouvelle_rotation = random.choice(("left", "right", "immobile"))
                        self.joueurs[joueur].set_rotation(nouvelle_rotation)

                        # Nouveau délai entre 0.5s et 1s
                        nouveau_delai = random.randint(5, 10) / 10
                        self.joueurs[joueur].set_cooldown_movement(nouveau_delai + time.time())

                    # Change les vecteurs de déplacement en fonction de la rotation
                    if self.joueurs[joueur].get_rotation() == "left":
                        self.inputs_joueurs[joueur][0] -= 1
                    elif self.joueurs[joueur].get_rotation() == "right":
                        self.inputs_joueurs[joueur][0] += 1

            # On tire si le joueur client a envoyé l'input correspondant
            if self.inputs_joueurs[joueur][2] > 0 and self.joueurs[joueur].get_type_joueur() == "solo":
                self.joueurs[joueur].tirer(self.objets)

            # Mise à jour de la rotation des joueurs
            if self.inputs_joueurs[joueur][0] > 0:
                self.joueurs[joueur].set_rotation("right")
            elif self.inputs_joueurs[joueur][0] < 0:
                self.joueurs[joueur].set_rotation("left")

            # Calcul de la physique des joueurs
            self.joueurs[joueur].calculer_velocite(self.inputs_joueurs[joueur])
            self.joueurs[joueur].calculer_collisions(self.objets)
            self.joueurs[joueur].appliquer_velocite()

            # Réinitialise le sprite du pistolet après un cours délai
            if self.joueurs[joueur].get_cooldown_tir() - time.time() <= 1.9:
                self.joueurs[joueur].set_etat_tir("recharge")

        # Pour chaque flèche, leur vecteur de déplacement se dirige vers le haut
        for objet in self.objets: 
            if type(objet) == Fleche:
                objet.calculer_velocite([0, -1])
                objet.calculer_collisions(self.objets)
                objet.appliquer_velocite()

                # On supprime toutes les flèches qui partent trop loin en hauteur
                if objet.get_pos()[1] < 250:
                    self.objets.remove(objet)

            # Comportement des ennemis (même que celui de l'ia)
            elif type(objet) == Ennemi:
                # Réinitialisation des directions des ennemis
                self.directions_ennemis[objet] = [0, 0]

                if not objet.get_dead():
                    # Ne peut pas changer de direction pendant le délai
                    if objet.get_move_cooldown() - time.time() <= 0:
                        # Choisit une rotation (direction) aléatoire
                        nouvelle_rotation = random.choice(("left", "right", "immobile"))
                        objet.set_rotation(nouvelle_rotation)

                        # Nouveau délai entre 0.5s et 1s
                        nouveau_delai = random.randint(5, 10) / 10
                        objet.set_move_cooldown(nouveau_delai + time.time())

                    # Change les vecteurs de déplacement en fonction de la rotation
                    if objet.get_rotation() == "left":
                        self.directions_ennemis[objet][0] -= 1
                    elif objet.get_rotation() == "right":
                        self.directions_ennemis[objet][0] += 1

                    # Calcul de la physique des ennemis
                    objet.calculer_velocite(self.directions_ennemis[objet])
                    objet.calculer_collisions(self.objets)
                    objet.appliquer_velocite()


    def calculate_score(self) -> None:
        """
        Cette méthode permet de calculer les scores de chaque joueur.
        """

        # Liste des joueurs vivants (tous ceux avec un get_dead() == False)
        joueurs_vivants = list(filter(lambda x: not x.get_dead(), self.joueurs.values()))
        ids_to_ips = {self.joueurs[joueur].get_id_minijeu(): joueur for joueur in self.joueurs.keys()}

        # Si le joueur solo est le seul en vie
        if len(joueurs_vivants) <= 1:
            # Il gagne et tous les autres perdent
            self.classement[ids_to_ips[0]] = 1
            for i in range(1, len(self.joueurs)):
                self.classement[ids_to_ips[i]] = 0
        else:
            # Il perd et tous les autres gagnent
            self.classement[ids_to_ips[0]] = 0
            for i in range(1, len(self.joueurs)):
                self.classement[ids_to_ips[i]] = 1

        # On saute une étape car pas nécessaire dans ce mini-jeu
        self.changer_etat(self.etats[self.etats.index(self.etat) + 1])


    def run(self, clock) -> None:
        self.is_running = True

        print("Lancement du mini-jeu: Archer Ival")
        while self.is_running:
            # On récupère le nombre de joueurs prêts (les ia sont automatiquement prêts)
            self.nb_joueurs_prets = len([joueur for joueur in self.joueurs.keys() if self.joueurs[joueur].get_ready() or self.joueurs[joueur].get_ia()])

            # Lorsque tous les joueurs sont prêts
            if len(self.joueurs.keys()) > 0 and self.nb_joueurs_prets == len(self.joueurs.keys()):
                # On finalise la création des joueurs avant que le jeu commence
                if self.etat == "minigame_load":
                    self.load_game()

                # Calcule le classement final
                if self.etat == "minigame_end":
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
                    frame = self.joueurs[joueur].get_frame() + 0.2

                    # N'a pas d'animation s'il ne dessine pas
                    if self.joueurs[joueur].get_type_joueur() == "solo":
                        # L'animation reste figée si le joueur est immobile
                        if self.inputs_joueurs[joueur][0] == 0 and self.inputs_joueurs[joueur][1] == 0: frame = 0
                    else:
                        frame = 0

                    self.joueurs[joueur].set_frame(frame)

            # Exécution du code qui gère le mini-jeu
            if self.etat == "minigame_during":
                self.during_game()

            if self.etat == "minigame_score":
                self.calculate_score()

            self.current_fps = clock.get_fps()
            clock.tick(self.fps)