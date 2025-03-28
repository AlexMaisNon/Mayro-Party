#Projet : Mayro Party
#Auteurs : Hinata Bouaziz, Antoine Desrues, Alexandre Guillaume, Matisse Moreau

# ------/ Importations des bibliothèques \------

import json
import random
import socket
from _thread import start_new_thread
import pygame
import time

# ------/ Importations des mini-jeux serveurs \------

import archer_ival_server
import hexagon_heat_server
import pushy_penguins_server
import speed_hockey_server
import trace_race_server


# ------/ Classes \------

# Classe du joueur
class Joueur():
    def __init__(self, perso: str, ia: bool = True, pseudo: str = "") -> None:
        """
        Constructeur de la classe Joueur.

        Attributs à définir:
            - perso (str): Personnage choisit par le joueur.
            - ia (bool): Indique si le joueur est une ia ou un joueur lambda.

        Attributs internes:
            - pieces (int): Nombre de pièces du joueur.
        """

        # Tests du type des paramètres donnés
        assert type(perso) == str, "Erreur: Le 1er paramètre (perso) est censé être une chaîne de caractères."
        assert type(ia) == bool, "Erreur: Le 2ème paramètre (ia) est censé être un booléen."
        assert type(pseudo) == str, "Erreur: Le 3ème paramètre (pseudo) est censé être une chaîne de caractères."

        # Initialisation des paramètres du personnage
        self.perso = perso
        self.ia = ia
        self.pseudo = pseudo

        # Nombre de pièces du joueur
        self.pieces = 0

        self.ready = False


    # ------/ Getters \------

    def get_perso(self) -> str:
        return self.perso

    def get_ia(self) -> bool:
        return self.ia

    def get_pseudo(self) -> str:
        return self.pseudo

    def get_pieces(self) -> int:
        return self.pieces

    def get_ready(self) -> bool:
        return self.ready


    # ------/ Setters \------

    def set_perso(self, new_perso) -> None:
        self.perso = new_perso

    def set_ia(self, new_ia: int) -> None:
        self.ia = new_ia

    def set_pieces(self, amount: int) -> None:
        self.pieces = amount

    def set_ready(self, new_ready: bool) -> None:
        self.ready = new_ready


# Classe du serveur
class Server:
    def __init__(self, adresse_serveur) -> None:
        """
        Documentation ici

        """

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server = adresse_serveur
        port = 5555

        try:
            self.server_socket.bind((server, port))

        except socket.error as e:
            print(str(e))

        self.server_socket.listen(4)
        print("Serveur lancé ! En attente de connexions...")


        self.joueurs = {}
        self.nb_joueurs_prets = 0
        self.classement = {}

        self.fps = 60
        self.current_fps = 0
        self.is_running = True
        self.clock = pygame.time.Clock()

        # Paramètres d'auto-fermeture du serveur
        self.timeout_timer = time.time()
        self.timeout = True

        # Initialisation du mini-jeu actuel
        self.minijeu_actuel = ""
        self.minijeux = {"archer_ival": archer_ival_server.Server(self.server_socket),
                         "hexagon_heat": hexagon_heat_server.Server(self.server_socket),
                         "pushy_penguins": pushy_penguins_server.Server(self.server_socket),
                         "speed_hockey": speed_hockey_server.Server(self.server_socket),
                         "trace_race": trace_race_server.Server(self.server_socket)}
        self.minijeux_options = list(self.minijeux.keys())

        # Initialisation des états du serveur
        self.etats = ["character_select", "minigame_select"]
        self.etat = self.etats[0]


    def client_thread(self, connection: socket.socket, address: str) -> None:
        connection.send(str.encode(address))
        pseudo = connection.recv(2048).decode("utf-8")

        is_connected = True

        self.joueurs[address] = Joueur("", False, pseudo)
        print(address + " (" + pseudo + ")" + " s'est connecté")

        # On désactive le timeout
        self.timeout = False

        while is_connected:
                # Attend une requête du client
                data = connection.recv(2048)

                # Une fois reçue, la décode
                request = data.decode("utf-8")

                # S'il n'a pas envoyé de requête, on coupe la connexion
                if not data:
                    print("Connexion perdu avec", address)
                    is_connected = False

                # Sinon, on envoie une réponse au client
                else:
                    if request == "get_etat":
                        reply = self.etat if self.minijeu_actuel == "" else self.minijeux[self.minijeu_actuel].get_etat()

                    elif request == "infos_serveur":
                        infos_joueurs = {joueur: {
                            "perso": self.joueurs[joueur].get_perso(),
                            "pseudo": self.joueurs[joueur].get_pseudo(),
                            "pieces": self.joueurs[joueur].get_pieces()
                        } for joueur in self.joueurs.keys()}

                        reply = json.dumps({
                            "nb_joueurs": len([joueur for joueur in self.joueurs.values() if not joueur.get_ia()]),
                            "nb_joueurs_prets": self.nb_joueurs_prets if self.minijeu_actuel == "" else self.minijeux[self.minijeu_actuel].get_nb_joueurs_prets() - len([joueur for joueur in self.joueurs.values() if joueur.get_ia()]),
                            "infos_joueurs": infos_joueurs,
                            "minijeu_actuel": self.minijeu_actuel,
                            "classement": self.classement
                        })

                    elif "set_perso" in request:
                        perso = json.loads(request)["set_perso"]
                        self.joueurs[address].set_perso(perso)

                        reply = "ok"

                    elif request == "ready_for_next_state":
                        self.joueurs[address].set_ready(True)
                        if self.minijeu_actuel != "":
                            self.minijeux[self.minijeu_actuel].get_player(address).set_ready(True)

                        reply = "ok"

                    elif request == "close":
                        reply = "closing"
                        is_connected = False

                    # Si on ne trouve pas la requête, on va la chercher dans le mini-jeu actuel
                    elif self.minijeu_actuel != "":
                        reply = self.minijeux[self.minijeu_actuel].client_thread(address, request)

                    else:
                        reply = "not_found"

                    connection.send(str.encode(reply))

        print("Connexion coupé avec", address)

        # Si la connexion est coupée, on laisse la place de libre pour un autre joueur (uniquement avant que le jeu commence)
        if self.etat == "character_select":
            del self.joueurs[address]

        if len(self.joueurs) == 0:
            self.timeout_timer = time.time()
            self.timeout = True

        connection.close()


    def accept_thread(self):
        id = 0
        while self.is_running:
            if self.etat == "character_select":
                connection, address = self.server_socket.accept()
                # start_new_thread(self.client_thread, (connection, address[0], id))

                # Temporaire
                start_new_thread(self.client_thread, (connection, str(id + 1)))
                id += 1


    def changer_etat(self, new_etat):
        self.etat = new_etat
        for ip in self.joueurs.keys():
            self.joueurs[ip].set_ready(False)

        print("Passé à l'état", self.etat)


    def select_minijeu(self): # type: ignore
        self.minijeu_actuel = random.choice(self.minijeux_options)

        for ip in self.joueurs.keys():
            self.minijeux[self.minijeu_actuel].add_player(ip, self.joueurs[ip].get_perso(), self.joueurs[ip].get_ia())

        # Lancement du mini-jeu sélectionné
        self.minijeux[self.minijeu_actuel].run(self.clock)

        # On supprime le mini-jeu déjà joué de la liste
        self.minijeux_options.remove(self.minijeu_actuel)

        # Liste des différents gains en fonction de la place
        score_to_pieces = [10, 5, 2, 0]

        for joueur in self.joueurs.keys():
            # On récupère le nombre de pièces en fonction du classement du joueur dans le mini-jeu
            nb_pieces = score_to_pieces[self.minijeux[self.minijeu_actuel].get_classement()[joueur] - 1]

            # Ajout des pièces dans la classe du joueur
            self.joueurs[joueur].set_pieces(self.joueurs[joueur].get_pieces() + nb_pieces)

        if len(self.minijeux_options) == 0:
            self.minijeu_actuel = ""
            self.is_running = False

        # On note le nombre de pièces de chaque joueur
        pieces_joueurs = {joueur: self.joueurs[joueur].get_pieces() for joueur in self.joueurs.keys()}

        # On trie automatiquement les clés du dictionnaire avec sorted
        classement_liste = sorted(pieces_joueurs, key=pieces_joueurs.get, reverse=True)

        for j in range(len(classement_liste)):
            # On attribue la position du classment en fonction de son nombre de pièces
            self.classement[classement_liste[j]] = j + 1

            # Si les deux derniers joueurs sont ex aequo, le joueur actuel prend la même place que le joueur avant lui
            if j > 0 and pieces_joueurs[classement_liste[j]] == pieces_joueurs[classement_liste[j - 1]]:
                self.classement[classement_liste[j]] = self.classement[classement_liste[j - 1]]


    def run(self) -> None:
        start_new_thread(self.accept_thread, ())

        while self.is_running:
            # On désactive le serveur si aucun joueur n'est connecté dessus pendant 2 minutes
            if time.time() - self.timeout_timer > 120 and self.timeout:
                self.is_running = False
                print("Aucune connexion depuis 2min, fermeture automatique du serveur")

            # On récupère le nombre de joueurs prêts (les ia sont automatiquement prêts)
            self.nb_joueurs_prets = len([joueur for joueur in self.joueurs.keys() if self.joueurs[joueur].get_ready() or self.joueurs[joueur].get_ia()])

            # Lorsque tous les joueurs sont prêts
            if len(self.joueurs.keys()) > 0 and self.nb_joueurs_prets == len(self.joueurs.keys()):
                # Si on a choisit les personnages, on passe aux mini-jeux
                if self.etat == "character_select":
                    self.changer_etat(self.etats[self.etats.index(self.etat) + 1])

                    # Liste de tous les personnages
                    liste_perso = ["mayro", "lugi", "wayro", "walugi"]

                    # Liste de tous les personnages sélectionnés
                    liste_perso_joueurs = [joueur.get_perso() for joueur in self.joueurs.values()]

                    # Liste de tous les personnages à créer
                    liste_perso_ia = [perso for perso in liste_perso if not perso in liste_perso_joueurs]

                    # Calcul du nombre de joueurs ia à créer
                    nb_joueurs_ia = 4 - len(self.joueurs.keys())

                    # Création des joueurs ia restants
                    for i in range(nb_joueurs_ia):
                        self.joueurs["ai" + str(i + 1)] = Joueur(liste_perso_ia[i])

                    # Initialisation du classement (tous les joueurs partent 1er)
                    self.classement = {joueur: 1 for joueur in self.joueurs.keys()}

                if self.etat == "minigame_select" and len(self.minijeux_options) > 0:
                    # On charge un mini-jeu aléatoire
                    self.select_minijeu()

            self.current_fps = self.clock.get_fps()
            self.clock.tick(self.fps)

if '__main__' == __name__:
    server = Server(input("Quel est l'adresse ip du serveur ? (exemple: 192.168.1.1): "))
    server.run()