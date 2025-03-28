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

    def __init__(self, perso: str, id_minijeu: int, ia: bool, side: str) -> None:
        """
        Constructeur de la classe Joueur.

        Attributs à définir:
            - perso (str): Personnage choisit par le joueur.
            - id_minijeu (int): id du joueur qui sert uniquement lors des mini-jeux.
            - ia (bool): Indique si le joueur est une ia ou un joueur lambda.
            - side (str): Côté du joueur (left ou right) (exclusif à ce mini-jeu).

        Attributs internes:
            - pos (list): Position du joueur.
            - velocity (list): Vélocité/Accélération du joueur.
            - speed (int): Vitesse du joueur.

            - frame (float): Indice du sprite à choisir.

            - collision (pygame.Rect): Boîte de collision du joueur.
        """

        # Tests du type des paramètres donnés
        assert type(perso) == str, "Erreur: Le 1er paramètre (perso) est censé être une chaîne de caractères."
        assert type(id_minijeu) == int, "Erreur: Le 2ème paramètre (id) est censé être un entier."
        assert type(ia) == bool, "Erreur: Le 3ème paramètre (ia) est censé être un booléen."
        assert type(side) == str, "Erreur: Le 4ème paramètre (side) est censé être une chaîne de caractères."

        # Définition du joueur
        self.perso = perso
        self.id_minijeu = id_minijeu
        self.ia = ia
        self.side = side
        self.ready = False

        # Caractéristiques principales (stats)
        self.pos = [0, 0]
        self.velocity = [0, 0]
        self.speed = 10

        # Initialisation / positionnement du sprite actuel et de la frame choisie
        self.frame = 0

        # Taille de la plateforme (la taille est basée sur le sprite du client)
        plateforme = 69

        # Boîte de collision du personnage
        self.collision = pygame.Rect(0, 0, plateforme, plateforme - 10)

        # Initialisation des conditions du lancement des sons
        self.lancer_son_hit = False
        self.lancer_son_but = False


    # ------/ Getters \------

    def get_perso(self) -> str:
        return self.perso

    def get_id_minijeu(self) -> int:
        return self.id_minijeu

    def get_ia(self) -> bool:
        return self.ia

    def get_side(self) -> str:
        return self.side

    def get_ready(self) -> bool:
        return self.ready

    def get_pos(self) -> list:
        return self.pos

    def get_frame(self) -> float:
        return self.frame

    def get_collisions(self) -> list:
        return [self.collision]

    def get_lancer_son_hit(self) -> bool:
        return self.lancer_son_hit

    def get_lancer_son_but(self) -> bool:
        return self.lancer_son_but


    # ------/ Setter \------

    def set_ready(self, new_ready: bool) -> None:
        self.ready = new_ready

    def set_pos(self, new_pos: list) -> None:
        self.pos = new_pos

    def set_frame(self, new_frame: float) -> None:
        self.frame = new_frame

    def set_lancer_son_hit(self, new_lancer_son_hit) -> None:
        self.lancer_son_hit = new_lancer_son_hit

    def set_lancer_son_but(self, new_lancer_son_but) -> None:
        self.lancer_son_but = new_lancer_son_but


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

        # On change seulement la coordonnée y car le joueur se déplace uniquement en y
        self.velocity[1] = direction[1] * self.speed


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
        liste_objets = [Carapace, Collider, But, Joueur]
        for elem in objets:
            assert type(elem) in liste_objets, "Erreur: La liste doit être seulement composée d'objets."

        # Positionnement de la boîte de collision
        self.collision.x = round(self.pos[0])
        self.collision.y = round(self.pos[1] + 69 - self.collision.h)

        # Calcul des collisions pour chaque objets
        for objet in objets:
            if objet != self:
                # Pas de rect_x parce que le joueur est bloqué sur l'axe y
                rect_y = pygame.Rect(self.collision.x, round(self.collision.y + self.velocity[1]), self.collision.w, self.collision.h)

                # On stoppe la vélocité du joueur si il collisionne avec une boîte de collision
                for collision in objet.get_collisions():
                    if rect_y.colliderect(collision):
                        self.velocity[1] = 0


    def appliquer_velocite(self) -> None:
        """
        Cette méthode permet d'appliquer la vélocité à la position du joueur.
        """

        # On ajoute la vélocité à la position du personnage
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]

        # La position du joueur est bloquée entre ces deux intervalles
        self.pos[1] = max(200, min(self.pos[1], 488))

        # On réinitialise la vélocité (sinon effet Asteroids (le personnage glisse infiniment))
        self.velocity = [0, 0]



# Classe de la carapace
class Carapace:

    # ------/ Constructeur \------

    def __init__(self) -> None:
        """
        Constructeur de la classe Carapace.

        Attributs internes:
            - pos (list): Position de la carapace.
            - velocity (list): Vélocité/Accélération de la carapace.
            - speed (int): Vitesse de la carapace.
            - direction (list): Direction de la carapace.

            - cooldown_son (float): Délai entre chaque son.

            - collision (pygame.Rect ou None): Boîte de collision de la carapace.
        """

        # Caractéristiques principales
        self.pos = [0, 0]
        self.velocity = [0, 0]
        self.speed = 12
        self.direction = [0, 0]

        # Taille de la carapace (la taille est basée sur le sprite du client)
        carapace = 66

        # Paramètres du son
        self.cooldown_son = 0

        # Boîte de collision de la carapace
        self.collision = pygame.Rect(0, 0, carapace, carapace)


    # ------/ Getters \------

    def get_pos(self) -> list:
        return self.pos

    def get_direction(self) -> list:
        return self.direction

    def get_collisions(self) -> list:
        return [self.collision]


    # ------/ Setters \------

    def set_pos(self, new_pos: list) -> None:
        self.pos = new_pos

    def set_direction(self, new_direction: list) -> None:
        self.direction = new_direction


    # ------/ Méthodes \------

    def calculer_velocite(self) -> None:
        """
        Cette méthode permet de calculer la vélocité de la carapace.
        """

        # On calcule la vélocité
        self.velocity = normalize([self.direction[0] * self.speed, self.direction[1] * self.speed])


    def calculer_collisions(self, objets: list) -> bool:
        """
        Cette méthode permet de calculer les collisions avec le joueur.

        Paramètres:
            - objets (list): Liste d'objets avec lesquels le joueur doit calculer les collisions.

        Renvois:
            - bool: Indique si le son de hit peut être joué.

        Pré-conditions:
            - objets doit contenir seulement des objets de type Carapace, Collider, But et Joueur.

        Post-conditions:
            - La méthode doit indiquer à la fin de l'exécution si le son de hit peut être joué ou
            non par le client.
        """

        # Test du type de objets
        assert type(objets) == list, "Erreur: Le paramètre donné (objets) n'est pas une liste."

        # Tests des éléments de objets
        liste_objets = [Carapace, Collider, But, Joueur]
        for elem in objets:
            assert type(elem) in liste_objets, "Erreur: La liste doit être seulement composée d'objets."

        # On met à jour la collision à la position de la carapace
        self.collision.x = round(self.pos[0])
        self.collision.y = round(self.pos[1])

        # Initialisation de la variable de son
        lancer_son = False

        # Calcul des collisions pour chaque objets
        for objet in objets:
            if objet != self:
                rect_x = pygame.Rect(round(self.collision.x + self.velocity[0]), self.collision.y, self.collision.w, self.collision.h)
                rect_y = pygame.Rect(self.collision.x, round(self.collision.y + self.velocity[1]), self.collision.w, self.collision.h)

                for collision in objet.get_collisions():
                    # On stoppe la vélocité en x du joueur si il collisionne avec une boîte de collision en x
                    if rect_x.colliderect(collision):
                        self.velocity[0] = 0

                        # On inverse sa direction en x et on ajoute 20 à sa vitesse
                        self.direction[0] *= -1
                        self.speed += 0.3

                        # On met un cooldown de 0.2s ici pour éviter que le son se répète trop rapidement
                        if self.cooldown_son - time.time() <= 0:
                            lancer_son = True
                            self.cooldown_son = 0.2 + time.time()

                    # On stoppe la vélocité en y du joueur si il collisionne avec une boîte de collision en y
                    if rect_y.colliderect(collision):
                        self.velocity[1] = 0

                        # On inverse sa direction en y et on ajoute 20 à sa vitesse
                        self.direction[1] *= -1
                        self.speed += 0.3

                        # On met un cooldown de 0.2s ici pour éviter que le son se répète trop rapidement
                        if self.cooldown_son - time.time() <= 0:
                            lancer_son = True
                            self.cooldown_son = 0.2 + time.time()

        return lancer_son


    def appliquer_velocite(self) -> None:
        """
        Cette méthode permet d'appliquer la vélocité à la position et à d'autres paramètres du joueur.
        """

        # On ajoute la vélocité à la position de la carapace
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]

        # On réinitialise la vélocité (sinon impossible de pouvoir changer de direction)
        self.velocity = [0, 0]


    def reset(self) -> None:
        """
        Cette méthode sert à réinitialiser les caractéristiques de la carapace par défaut et à choisir
        une nouvelle direction aléatoire.
        """

        # Réinitialisation de la position / vitesse
        self.pos = [605, 344]
        self.speed = 12

        # Toutes les directions possibles empruntables par la carapace
        directions = ([1, 1], [1, 0.5], [0.5, 1])

        # On en choisit une aléatoirement puis on choisit le sens où elle va aller
        self.direction = random.choice(directions)
        self.direction[0] *= random.choice((1, -1))



# Classe d'un collider (juste une boîte de collision invisible)
class Collider:

    # ------/ Constructeur \------

    def __init__(self, pos: list, taille: list) -> None:
        """
        Constructeur de la classe Collider.

        Attributs à définir:
            - pos (list): Position du collider.
            - taille (list): Taille du collider.

        Attributs internes:
            - collision (pygame.Rect): Boîte de collision du collider.
        """

        # Test des types des paramètres donnés
        assert type(pos) == list, "Erreur: Le 1er paramètre (pos) n'est pas une liste."
        assert type(taille) == list, "Erreur: Le 2ème paramètre (taille) n'est pas une liste."

        # Caractéristiques de la boîte de collision
        self.pos = pos
        self.taille = taille

        # Boîte de collision
        self.collision = pygame.Rect(self.pos[0], self.pos[1], self.taille[0], self.taille[1])


    # ------/ Getter \------

    def get_collisions(self) -> list:
        return [self.collision]



# Classe d'un but
class But:

    # ------/ Constructeur \------

    def __init__(self, pos) -> None:
        """
        Constructeur de la classe But.

        Attributs à définir:
            - pos (list): Position du but.

        Attributs internes:
            - collisions (list): Liste des boîtes de collision du but.
        """

        # Test des types des paramètres donnés
        assert type(pos) == list, "Erreur: Le paramètre donné (pos) n'est pas une liste."

        # Caractéristiques du but
        self.pos = pos

        # Taille du but (la taille est basée sur le sprite du client)
        but = 100

        # Boîte de collision du but
        self.collisions = [pygame.Rect(self.pos[0], self.pos[1] - 48, but, 133),
                           pygame.Rect(self.pos[0], self.pos[1] + 513 - 133, but, 133)]


    # ------/ Getter \------

    def get_pos(self) -> list:
        return self.pos

    def get_collisions(self) -> list:
        return self.collisions



# Classe du serveur
class Server:
    def __init__(self, server_socket: socket.socket) -> None:
        """
        Documentation ici
            - timer (float): Durée du mini-jeu.

            - score (list): Stockage du score de la partie.
        """

        self.server_socket = server_socket
        print("Initialisation du mini-jeu: Speed Hockey")

        self.joueurs = {}
        self.inputs_joueurs = {}
        self.nb_joueurs_prets = 0

        # Initialisation d'un ordre aléatoire pour les mini-jeux
        self.ordre_minijeu = [i for i in range(4)]
        random.shuffle(self.ordre_minijeu)

        # La position et la taille des colliders sont basés sur l'image du background
        self.carapace = Carapace()
        self.carapace.set_pos([605, 344])

        self.colliders = [Collider([87, 108], [1106, 21]), Collider([87, 641], [1106, 28])]
        self.buts = [But([0, 156]), But([1180, 156])]
        self.objets = []

        # Initialisation du timer
        self.timer = 60

        # Stockage du score et du classement de la partie
        self.score = [0, 0]
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
        self.joueurs[address] = Joueur(perso, id_minijeu, ia, "left" if id_minijeu < 2 else "right")


    def client_thread(self, address: str, request: str) -> str:
            if request == "get_etat":
                reply = self.etat

            elif request == "desactive_son_hit":
                self.joueurs[address].set_lancer_son_hit(False)
                reply = "ok"

            elif request == "desactive_son_but":
                self.joueurs[address].set_lancer_son_but(False)
                reply = "ok"

            elif "|" in request:
                # Si la requête c'est ça: 1|1
                self.inputs_joueurs[address] = [int(coord) for coord in request.split("|")]

                infos_joueurs = {joueur: {
                    "perso": self.joueurs[joueur].get_perso(),
                    "side": self.joueurs[joueur].get_side(),
                    "pos": self.joueurs[joueur].get_pos(),
                    "frame": self.joueurs[joueur].get_frame(),
                    "lancer_son_hit": self.joueurs[joueur].get_lancer_son_hit(),
                    "lancer_son_but": self.joueurs[joueur].get_lancer_son_but()
                } for joueur in self.joueurs.keys()}

                reply = json.dumps({"joueurs": infos_joueurs, "carapace": self.carapace.get_pos(), "score": self.score, "timer": round(self.timer - time.time()), "classement": self.classement, "fps": self.current_fps})

            else:
                reply = "not_found"

            return reply


    def changer_etat(self, new_etat):
        self.etat = new_etat
        for ip in self.joueurs.keys():
            self.joueurs[ip].set_ready(False)

        print("[Speed Hockey] Passé à l'état", self.etat)


    def load_game(self):
        ids_to_ips = {self.joueurs[joueur].get_id_minijeu(): joueur for joueur in self.joueurs.keys()}
        pos_joueurs = [[180, 344], [380, 344], [832, 344], [1032, 344]]

        # On ajoute les joueurs dans le dictionnaires des inputs et on les positionne
        for i in range(4):
            self.inputs_joueurs[ids_to_ips[i]] = [0, 0, 0]
            self.joueurs[ids_to_ips[i]].set_pos(pos_joueurs[i])

        # On met à jour la liste d'objets
        self.objets = list(self.joueurs.values()) + [self.carapace] + self.colliders + self.buts


    def during_game(self):
        # Le mini-jeu s'arrête si le timer s'arrête ou si l'une des deux équipes a 3 points
        if self.timer - time.time() <= 0:
            # On immobilise la carapace à la fin du mini-jeu
            self.carapace.set_direction([0, 0])

            # On passe à l'état suivant
            self.changer_etat(self.etats[self.etats.index(self.etat) + 1])

            # Désactivation du timer
            self.timer = 0

        elif self.score[0] > 2 or self.score[1] > 2:
            # On immobilise la carapace à la fin du mini-jeu
            self.carapace.set_direction([0, 0])

            # On passe à l'état suivant
            self.changer_etat(self.etats[self.etats.index(self.etat) + 1])

            # Désactivation du timer
            self.timer = 0

        # Calcul de la physique de la carapace
        self.carapace.calculer_velocite()

        lancer_son_hit = self.carapace.calculer_collisions(self.objets)
        lancer_son_but = False

        self.carapace.appliquer_velocite()

        # Si la carapace rentre dans le but vert
        if self.carapace.get_pos()[0] > self.buts[1].get_pos()[0]:
            # Réinitialisation de la carapace
            self.carapace.reset()

            # Ajout du score pour l'équipe adverse
            self.score[0] += 1

            # On indique au client de lancer le son de but
            lancer_son_but = True

        # Si la carapace rentre dans le but rouge
        elif self.carapace.get_pos()[0] < self.buts[0].get_pos()[0]:
            # Réinitialisation de la carapace
            self.carapace.reset()

            # Ajout du score pour l'équipe adverse
            self.score[1] += 1

            # On indique au client de lancer le son de but
            lancer_son_but = True

        # Comportement des ia
        for joueur in self.joueurs.keys():
            if self.joueurs[joueur].get_ia():
                # On réinitialise leurs inputs
                self.inputs_joueurs[joueur] = [0, 0]

                # Joueur sur la ligne rouge la plus proche du centre
                if self.joueurs[joueur].get_pos()[0] == 380:

                    # L'ia suit la carapace si elle se trouve devant elle
                    if self.carapace.get_pos()[0] > self.joueurs[joueur].get_pos()[0]:
                        if self.joueurs[joueur].get_pos()[1] < self.carapace.get_pos()[1] + 25:
                            self.inputs_joueurs[joueur][1] += 1
                        elif self.joueurs[joueur].get_pos()[1] > self.carapace.get_pos()[1] - 25:
                            self.inputs_joueurs[joueur][1] -= 1

                    # Sinon l'ia s'éloigne le plus possible de la carapace
                    else:
                        if self.joueurs[joueur].get_pos()[1] < self.carapace.get_pos()[1]:
                            self.inputs_joueurs[joueur][1] -= 1
                        elif self.joueurs[joueur].get_pos()[1] > self.carapace.get_pos()[1]:
                            self.inputs_joueurs[joueur][1] += 1

                # Joueur sur la ligne verte la plus proche du centre
                elif self.joueurs[joueur].get_pos()[0] == 832:

                    # L'ia suit la carapace si elle se trouve devant elle
                    if self.carapace.get_pos()[0] < self.joueurs[joueur].get_pos()[0]:
                        if self.joueurs[joueur].get_pos()[1] < self.carapace.get_pos()[1] + 25:
                            self.inputs_joueurs[joueur][1] += 1
                        elif self.joueurs[joueur].get_pos()[1] > self.carapace.get_pos()[1] - 25:
                            self.inputs_joueurs[joueur][1] -= 1

                    # Sinon l'ia s'éloigne le plus possible de la carapace
                    else:
                        if self.joueurs[joueur].get_pos()[1] < self.carapace.get_pos()[1]:
                            self.inputs_joueurs[joueur][1] -= 1
                        elif self.joueurs[joueur].get_pos()[1] > self.carapace.get_pos()[1]:
                            self.inputs_joueurs[joueur][1] += 1


                # Joueur sur la ligne la plus éloignée du centre (rouge et verte)
                elif self.joueurs[joueur].get_pos()[0] == 180 or self.joueurs[joueur].get_pos()[0] == 1032:
                    # L'ia suit la carapace quoi qu'il arrive
                    if self.joueurs[joueur].get_pos()[1] < self.carapace.get_pos()[1] + 25:
                        self.inputs_joueurs[joueur][1] += 1
                    elif self.joueurs[joueur].get_pos()[1] > self.carapace.get_pos()[1] - 25:
                        self.inputs_joueurs[joueur][1] -= 1

            # Calcul de la physique des joueurs
            self.joueurs[joueur].calculer_velocite(self.inputs_joueurs[joueur])
            self.joueurs[joueur].calculer_collisions(self.objets)
            self.joueurs[joueur].appliquer_velocite()

            # Indique au client s'il peut lancer le son correspondant
            if lancer_son_hit:
                self.joueurs[joueur].set_lancer_son_hit(True)
            if lancer_son_but:
                self.joueurs[joueur].set_lancer_son_but(True)


    def calculate_score(self) -> None:
        """
        Cette méthode permet de calculer les scores de chaque joueur.
        """

        # En cas d'égalité
        if self.score[0] == self.score[1]:
            # Personne ne gagne
            for joueur in self.joueurs.keys():
                self.classement[joueur] = 0

        # Si l'équipe rouge gagne
        elif self.score[0] > self.score[1]:
            # Joueurs de l'équipe rouge
            for joueur in [ip for ip in self.joueurs.keys() if self.joueurs[ip].get_side() == "left"]:
                self.classement[joueur] = 1

            # Joueurs de l'équipe verte
            for joueur in [ip for ip in self.joueurs.keys() if self.joueurs[ip].get_side() == "right"]:
                self.classement[joueur] = 0

        # Si l'équipe verte gagne
        else:
            # Joueurs de l'équipe rouge
            for joueur in [ip for ip in self.joueurs.keys() if self.joueurs[ip].get_side() == "left"]:
                self.classement[joueur] = 0

            # Joueurs de l'équipe verte
            for joueur in [ip for ip in self.joueurs.keys() if self.joueurs[ip].get_side() == "right"]:
                self.classement[joueur] = 1

        # On saute une étape car pas nécessaire dans ce mini-jeu
        self.changer_etat(self.etats[self.etats.index(self.etat) + 1])


    def run(self, clock) -> None:
        self.is_running = True

        print("Lancement du mini-jeu: Speed Hockey")
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
                    # Réinitialisation de la carapace
                    self.carapace.reset()

                    # Lancement du timer
                    self.timer = time.time() + self.timer

            # Calcul des frames pour la vitesse d'animation des personnages
            if self.etat != "minigame_load" and self.etat != "minigame_select":
                for joueur in self.joueurs.keys():
                    frame = self.joueurs[joueur].get_frame() + 0.09

                    self.joueurs[joueur].set_frame(frame)

            # Exécution du code qui gère le mini-jeu
            if self.etat == "minigame_during":
                self.during_game()

            if self.etat == "minigame_score":
                self.calculate_score()

            self.current_fps = clock.get_fps()
            clock.tick(self.fps)