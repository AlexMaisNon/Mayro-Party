#Projet : Mayro Party
#Auteurs : Hinata Bouaziz, Antoine Desrues, Alexandre Guillaume, Matisse Moreau

# ------/ Importations des bibliothèques \------

import json
import socket
import pygame
from math import sqrt
import random
from os import sep

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

def scale_image_by(image: pygame.Surface, taille: "int | float | tuple") -> pygame.Surface: # type: ignore
    """
    Cette fonction permet d'agrandir une image par un nombre taille.

    Paramètres:
        - image (pygame.Surface): une image chargé avec pygame.
        - taille (int, float ou tuple): un nombre ou une liste de 2 nombres représentant le facteur pour agrandir l'image.
    Renvois:
        - pygame.Surface: la même image agrandie.
    Pré-conditions:
        - image doit être une image chargé avec pygame.
    Post-conditions:
        - La fonction doit renvoyer la même image donnée par l'utilisateur, mais agrandie par
        le nombre taille donné.
    """

    # Tests de type de variables
    assert type(image) == pygame.Surface, "Erreur: Le 1er paramètre (image) n'est pas une image chargé avec pygame."
    assert type(taille) == int or type(taille) == float or type(taille) == tuple, "Erreur: Le 2ème paramètre (taille) n'est pas un nombre ou un tuple."

    # On renvoie l'image transformée
    if type(taille) != tuple:
        return pygame.transform.scale(image, (round(image.get_rect().w * taille), round(image.get_rect().h * taille)))
    else:
        # On fait les modifications nécessaires si on renvoie une liste de deux tailles différentes
        return pygame.transform.scale(image, (round(image.get_rect().w * taille[0]), round(image.get_rect().h * taille[1])))


# ------/ Classes \------

# Classe du joueur
class Joueur:

    # ------/ Constructeur \------

    def __init__(self, perso: str, id_minijeu: int, ia: bool, color: str) -> None:
        """
        Constructeur de la classe Joueur.

        Attributs à définir:
            - perso (str): Personnage choisit par le joueur.
            - id_minijeu (int): id du joueur qui sert uniquement lors des mini-jeux.
            - ia (bool): Indique si le joueur est une ia ou un joueur lambda.
            - color (str): Couleur du crayon du joueur (exclusif à ce mini-jeu).

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
        assert type(color) == str, "Erreur: Le 4ème paramètre (color) est censé être une chaîne de caractères."

        # Définition du joueur
        self.perso = perso
        self.id_minijeu = id_minijeu
        self.ia = ia
        self.color = color
        self.ready = False

        # Caractéristiques principales (stats)
        self.pos = [0, 0]
        self.velocity = [0, 0]
        self.speed = 1.6

        # Définit si le joueur dessine ou non
        self.is_drawing = True

        # Initialisation de la frame choisie
        self.frame = 0

        # Boîte de collision du personnage
        self.collision = pygame.Rect(0, 0, 42, 20)

        # Initialisation de la taille du joueur (qui sera définie lors du début de partie)
        self.taille = [0, 0]


    # ------/ Getters \------

    def get_perso(self) -> str:
        return self.perso

    def get_id_minijeu(self) -> int:
        return self.id_minijeu

    def get_ia(self) -> bool:
        return self.ia

    def get_color(self) -> str:
        return self.color

    def get_ready(self) -> bool:
        return self.ready

    def get_pos(self) -> list:
        return self.pos

    def get_is_drawing(self) -> bool:
        return self.is_drawing

    def get_frame(self) -> float:
        return self.frame

    def get_taille(self) -> list:
        return self.taille

    def get_collisions(self) -> list:
        return [self.collision]


    # ------/ Setter \------

    def set_ready(self, new_ready: bool) -> None:
        self.ready = new_ready

    def set_pos(self, new_pos: list) -> None:
        self.pos = new_pos

    def set_is_drawing(self, new_is_drawing: bool) -> None:
        self.is_drawing = new_is_drawing

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
        assert type(direction) == list, "Erreur: Le 1er paramètre (direction) n'est pas une liste."

        # Test des valeurs dans direction
        for elem in direction:
            assert elem >= -1 and elem <= 1, "Erreur: Une des valeurs dans la direction donnée n'est pas valide."

        self.velocity = normalize([axe * self.speed for axe in direction])


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
            assert type(elem) == Collider or type(elem) == Joueur, "Erreur: La liste doit être seulement composée d'objets de type Collider ou Joueur."

        # Positionnement de la boîte de collision
        self.collision.x = round(self.pos[0] + self.taille[0] / 4)
        self.collision.y = round(self.pos[1] + self.taille[1] - self.collision.h)

        # Calcul des collisions pour chaque objets
        for objet in objets:
            if objet != self:
                coef_ia = 20 if self.ia else 0
                rect_x = pygame.Rect(self.collision.x + round(self.velocity[0]) + coef_ia, self.collision.y, self.collision.w, self.collision.h)
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
                            self.velocity[0] = 0

                    if rect_y.colliderect(collision):
                        # Pareil ici
                        try:
                            assert objet.get_following_camera(), "Erreur: Méthode introuvable (car pas collider) ou ne suit pas la caméra (donc pas arrivée)."

                            # Arrête de dessiner (car a touché l'arrivé)
                            self.is_drawing = False
                        except:
                            self.velocity[1] = 0


    def appliquer_velocite(self, cam_mov: "int | float") -> None:
        """
        Cette méthode permet d'appliquer la vélocité à la position et à d'autres paramètres du joueur en fonction du
        mouvement de la caméra.

        Paramètres:
            - cam_mov (int ou float): Vélocité de la caméra.
        """

        # Test du type de cam_mov
        assert type(cam_mov) == int or type(cam_mov) == float, "Erreur: Le paramètre donné (cam_mov) n'est pas un nombre."

        # On ajoute la vélocité à la position du personnage
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]

        # On déplace le joueur en fonction du mouvement de la caméra
        self.pos[0] -= cam_mov

        # Seulement s'il dessine parce que ça peut causer des problèmes lors des cinématiques
        if self.is_drawing:
            # Le joueur ne peut pas dépasser l'écran
            self.pos[0] = max(0, min(self.pos[0], 1280 - self.taille[0]))

        # On réinitialise la vélocité (sinon effet Asteroids (le personnage glisse infiniment))
        self.velocity = [0, 0]



# Classe d'un collider (juste une boîte de collision invisible)
class Collider:

    # ------/ Constructeur \------

    def __init__(self, pos: list, taille: list, following_camera: bool) -> None:
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


    # ------/ Getter \------

    def get_collisions(self) -> list:
        return [self.collision]

    def get_following_camera(self) -> bool:
        return self.following_camera


    # ------/ Setter \------

    def set_pos(self, new_pos: list) -> None:
        self.pos = new_pos


    # ------/ Méthodes \------

    def update_positions(self, cam_mov: "int | float") -> None:
        """
        Cette méthode permet de déplacer le collider en fonction de la vélocité de la caméra.

        Paramètres:
            - cam_mov (int ou float): Vélocité de la caméra.
        """

        # Test du type de cam_mov
        assert type(cam_mov) == int or type(cam_mov) == float, "Erreur: Le paramètre donné (cam_mov) n'est pas un nombre."

        # Suit le trajet de la caméra comme n'importe quel objet
        if self.following_camera:
            self.pos[0] -= cam_mov

            # Repositionnement de la boîte de collision
            self.collision.x = round(self.pos[0])
            self.collision.y = round(self.pos[1])



# Classe du serveur
class Server:
    def __init__(self, server_socket: socket.socket) -> None:
        """
        Documentation ici
            - timer (float): Durée du mini-jeu.

            - score (list): Stockage du score de la partie.
        """

        self.server_socket = server_socket
        print("Initialisation du mini-jeu: Trace Race")

        self.joueurs = {}
        self.inputs_joueurs = {}
        self.nb_joueurs_prets = 0

        # Initialisation d'un ordre aléatoire pour les mini-jeux
        self.ordre_minijeu = [i for i in range(4)]
        random.shuffle(self.ordre_minijeu)

        self.liste_couleurs = ["red", "blue", "green", "yellow"]

        # La position et la taille des colliders sont basés sur l'image du background
        self.colliders = [Collider([0, 0], [1280, 70], False),
                          Collider([0, 180], [1280, 50], False),
                          Collider([0, 335], [1280, 50], False),
                          Collider([0, 494], [1280, 50], False),
                          Collider([0, 650], [1280, 70], False),
                          Collider([2800, 59], [19, 603], True)]
        self.objets = []

        # Stockage du score et du classement de la partie
        self.score = {}
        self.classement = {}

        self.fps = 60
        self.current_fps = 0
        self.is_running = False

        # Initialisation des états de la partie
        self.etats = ["minigame_select", "minigame_load", "minigame_start", "minigame_during", "minigame_end", "minigame_score", "minigame_winners"]
        self.etat = self.etats[0]

        # Initialisation de la caméra
        self.camera_pos = [0, 0]
        self.camera_speed = 0

        # Initialisation des derniers points de chaque joueur
        self.last_point = {}

        # Chargement des tracés d'origines pour pouvoir les traiter
        self.bg_traces = pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "trace_race", "traces.png"]))
        self.crayon_joueur = scale_image_by(pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "trace_race", "blue_pen.png"])), 3)

        # Masques à définir pour l'ia
        self.pen_mask = pygame.mask.from_surface(self.crayon_joueur)
        self.bg_traces_mask = pygame.mask.from_surface(self.bg_traces)


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
        self.joueurs[address] = Joueur(perso, id_minijeu, ia, self.liste_couleurs[id_minijeu])


    def client_thread(self, address: str, request: str) -> str:
            if request == "get_etat":
                reply = self.etat

            elif "taille_joueurs" in request:
                taille = json.loads(request)["taille_joueurs"]
                for ip in taille.keys():
                    self.joueurs[ip].set_taille([taille[ip][0], taille[ip][1]])
                reply = "ok"

            elif "pourcentages" in request:
                sorted_pourcentages = json.loads(request)["pourcentages"]

                # On s'en sert créer le classement
                for i in range(len(sorted_pourcentages)):
                    joueur = sorted_pourcentages[i]
                    self.classement[joueur] = i + 1
                reply = "ok"

            elif request == "get_ids_minijeu":
                reply = json.dumps({joueur: self.joueurs[joueur].get_id_minijeu() for joueur in self.joueurs.keys()})

            elif "|" in request:
                # Si la requête c'est ça: 1|1
                self.inputs_joueurs[address] = [int(coord) for coord in request.split("|")]

                infos_joueurs = {joueur: {
                    "perso": self.joueurs[joueur].get_perso(),
                    "color": self.joueurs[joueur].get_color(),
                    "pos": self.joueurs[joueur].get_pos(),
                    "frame": self.joueurs[joueur].get_frame(),
                    "is_drawing": self.joueurs[joueur].get_is_drawing()
                } for joueur in self.joueurs.keys()}

                reply = json.dumps({"joueurs": infos_joueurs, "camera": self.camera_pos, "point": self.last_point, "score": self.score, "classement": self.classement, "fps": self.current_fps})

            else:
                reply = "not_found"

            return reply


    def changer_etat(self, new_etat):
        self.etat = new_etat
        for ip in self.joueurs.keys():
            self.joueurs[ip].set_ready(False)

        print("[Trace Race] Passé à l'état", self.etat)


    def load_game(self):
        ids_to_ips = {self.joueurs[joueur].get_id_minijeu(): joueur for joueur in self.joueurs.keys()}
        pos_joueurs = [[600, 38], [600, 170], [600, 324], [600, 486]]

        # On ajoute les joueurs dans le dictionnaires des inputs et on les positionne
        for i in range(4):
            self.inputs_joueurs[ids_to_ips[i]] = [0, 0, 0]
            self.joueurs[ids_to_ips[i]].set_pos(pos_joueurs[i])

        # On met à jour la liste d'objets
        self.objets = list(self.joueurs.values()) + self.colliders

        # Initialisation du dernier point des tracés de chaque joueur
        self.last_point = {joueur: [] for joueur in self.joueurs}


    def during_game(self):
        # Liste des joueurs dessinant (tous ceux avec un get_is_drawing() == True)
        nb_joueurs_dessinant = len([joueur for joueur in self.joueurs.values() if joueur.get_is_drawing()])

        # Le mini-jeu s'arrête si le timer s'arrête ou si l'une des deux équipes a 3 points
        if self.camera_pos[0] > 2621:       # (2621 = taille du background - taille de l'écran)
            self.camera_speed = 0
            for joueur in self.joueurs.values():
                joueur.set_is_drawing(False)

            # On passe à l'état suivant
            self.changer_etat(self.etats[self.etats.index(self.etat) + 1])

        # On accélère la vitesse de la caméra si tout le monde a fini de dessiner
        elif nb_joueurs_dessinant < 1:
            self.camera_speed = 8.2

        # Comportement des ia (pathfinding assez mid honnêtement)
        for joueur in self.joueurs.keys():

            # On récupère la position du crayon
            pen_pos = [round(self.joueurs[joueur].get_pos()[0] + self.joueurs[joueur].get_taille()[0] - self.crayon_joueur.get_rect().w) + 6,
                       round(self.joueurs[joueur].get_pos()[1] + self.joueurs[joueur].get_taille()[1] - self.crayon_joueur.get_rect().h) - 8]

            if self.joueurs[joueur].get_ia():
                # On réinitialise leurs inputs
                self.inputs_joueurs[joueur] = [0, 0]

                if self.joueurs[joueur].get_is_drawing():
                    # Calcul des offsets pour les opérations avec les masques
                    mask_x_offset = pen_pos[0] + round(self.camera_pos[0])
                    mask_y_offset = pen_pos[1] + round(self.camera_pos[1])

                    # On détecte si le tracé est proche du haut de la texture du crayon (donc doit aller vers le bas, difficile à expliquer)
                    if self.bg_traces_mask.overlap(self.pen_mask, (mask_x_offset, mask_y_offset + self.crayon_joueur.get_rect().h)):
                        self.inputs_joueurs[joueur][1] += 1

                    # On détecte si le tracé est proche du bas de la texture du crayon (donc doit aller vers le haut, difficile à expliquer)
                    elif self.bg_traces_mask.overlap(self.pen_mask, (mask_x_offset, mask_y_offset - 5)):
                        self.inputs_joueurs[joueur][1] -= 1

                    # On détecte si le tracé est se trouve au niveau de la pointe du crayon
                    if self.bg_traces_mask.overlap(self.pen_mask, (mask_x_offset + 5, mask_y_offset)):
                        self.inputs_joueurs[joueur][0] += 1
                    else:
                        # Fait des mouvements aléatoires et prie pour que ça le décoince
                        self.inputs_joueurs[joueur][random.randint(0, 1)] = random.randint(-1, 1)
                        self.inputs_joueurs[joueur][random.randint(0, 1)] = random.randint(-1, 1)

            # Léger délai entre chaque placement de point sinon grosse baisse de performance
            if self.joueurs[joueur].get_is_drawing():
                # On crée le dernier point de chaque tracé
                self.last_point[joueur] = [[pen_pos[0] + 4, pen_pos[1] + 86], self.joueurs[joueur].get_color()]


    def calculate_score(self) -> None:
        """
        Cette méthode permet de calculer les scores de chaque joueur.
        """

        # On arrête la caméra quand elle touche le bord du terrain
        if self.camera_pos[0] > 2121:       # (2121 = taille du background - taille de l'écran - 500)
            self.camera_speed = 0


    def run(self, clock) -> None:
        self.is_running = True

        print("Lancement du mini-jeu: Trace Race")
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
                    # Réinitialisation de la caméra
                    self.camera_pos = [0, 0]
                    self.camera_speed = 10

                    # On positionne tous les joueurs après la ligne d'arrivée
                    for joueur in self.joueurs.values():
                        joueur.set_pos([2851, joueur.get_pos()[1]])     # (2851 = taille du background - taille de l'écran + 230)

                # Si on a fini le mini-jeu, on stoppe ce serveur
                if self.etat == "minigame_winners":
                    self.is_running = False

                # Sinon on passe à l'état suivant
                else:
                    self.changer_etat(self.etats[self.etats.index(self.etat) + 1])

                if self.etat == "minigame_during":
                    # Changement de la vitesse de la caméra
                    self.camera_speed = 1

            # Calcul des frames pour la vitesse d'animation des personnages
            if self.etat != "minigame_load" and self.etat != "minigame_select":
                for joueur in self.joueurs.keys():
                    frame = self.joueurs[joueur].get_frame() + 0.18

                    # N'a pas d'animation s'il ne dessine pas
                    if self.joueurs[joueur].get_is_drawing():
                        # L'animation reste figée si le joueur est immobile
                        if self.inputs_joueurs[joueur][0] == 0 and self.inputs_joueurs[joueur][1] == 0: frame = 0
                    else:
                        frame = 0

                    self.joueurs[joueur].set_frame(frame)

                    # Calcul de la physique des joueurs
                    self.joueurs[joueur].calculer_velocite(self.inputs_joueurs[joueur])
                    self.joueurs[joueur].calculer_collisions(self.objets)
                    self.joueurs[joueur].appliquer_velocite(self.camera_speed)

                # On met à jour la position de tous les colliders qui suivent la caméra
                for collider in self.colliders:
                    if collider.get_following_camera():
                        collider.update_positions(self.camera_speed)

                # Mouvement de la caméra
                self.camera_pos[0] += self.camera_speed

            # Exécution du code qui gère le mini-jeu
            if self.etat == "minigame_during":
                self.during_game()

            if self.etat == "minigame_score":
                self.calculate_score()

            self.current_fps = clock.get_fps()
            clock.tick(self.fps)