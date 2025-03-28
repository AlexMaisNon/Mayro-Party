#Projet : Mayro Party
#Auteurs : Hinata Bouaziz, Antoine Desrues, Alexandre Guillaume, Matisse Moreau

# ------/ Importations des bibliothèques \------

import pygame
import pygame.freetype
from math import floor
import time
from os import sep

from utils import Network, scale_image_by
import json

# ------/ Classes \------

# Classe du joueur
class Joueur:

    # ------/ Constructeur \------

    def __init__(self, perso: str, color: str) -> None:
        """
        Constructeur de la classe Joueur.

        Attributs à définir:
            - perso (str): Personnage choisit par le joueur.
            - color (str): Couleur du crayon du joueur (exclusif à ce mini-jeu).

        Attributs internes:
            - pos (list): Position du joueur.

            - is_drawing (bool): Indique si le joueur dessine ou non.

            - sprites_directory (str): Chemin du dossier des sprites du joueur.
            - sprites (dict): Sprites du joueurs.
            - sprite (pygame.Surface): Sprite actuel du joueur.

            - pen (pygame.Surface): Sprite du crayon.
            - pen_pos (list): Position du crayon.

            - shadow (pygame.Surface): Sprite de l'ombre du joueur.
            - shadow_pos (list): Position de l'ombre.

            - taille (list): Dimensions du sprite du joueur (fournis au serveur).
        """

        # Tests du type des paramètres donnés
        assert type(perso) == str, "Erreur: Le 1er paramètre (perso) est censé être une chaîne de caractères."
        assert type(color) == str, "Erreur: Le 2ème paramètre (color) est censé être une chaîne de caractères."


        # Définition du joueur
        self.perso = perso
        self.color = color

        # Caractéristiques principales (stats)
        self.pos = [0.0, 0.0]

        # Définit si le joueur dessine ou non
        self.is_drawing = True

        # Emplacement des sprites du joueur
        self.sprites_directory = sep.join(["..", "data", "sprites", "characters", self.perso])

        # Définition des sprites automatiquement
        self.sprites = {
            "trace": [scale_image_by(pygame.image.load(sep.join([self.sprites_directory, "trace" + str(i) + ".png"])), 3) for i in range(8)],
            "idle": scale_image_by(pygame.image.load(sep.join([self.sprites_directory, "walk_right0.png"])), 3)
        }

        # Initialisation / positionnement du sprite actuel et de la frame choisie
        self.sprite = self.sprites["trace"][0]
        self.sprite_pos = list(self.pos)

        # Initialisation et positionnement du stylo
        self.pen = scale_image_by(pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "trace_race", self.color + "_pen.png"])), 3)
        self.pen_pos = list(self.pos)

        # Initialisation et positionnement de l'ombre
        self.shadow = scale_image_by(pygame.image.load(sep.join([self.sprites_directory, "shadow.png"])), 3)
        self.shadow_pos = list(self.pos)

        # Initialisation de la taille du joueur (uniquement fournie au serveur)
        self.taille = [self.sprite.get_rect().w, self.sprite.get_rect().h]


    # ------/ Getters \------

    def get_perso(self) -> str:
        return self.perso

    def get_taille(self) -> list:
        return self.taille

    def get_is_drawing(self) -> bool:
        return self.is_drawing


    # ------/ Setters \------

    def set_is_drawing(self, new_is_drawing: bool) -> None:
        self.is_drawing = new_is_drawing


    # ------/ Méthodes \------

    def appliquer_positions(self, position) -> None:
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

        # Positionnement du crayon
        self.pen_pos[0] = round(self.pos[0] + self.sprite.get_rect().w - self.pen.get_rect().w) + 6
        self.pen_pos[1] = round(self.pos[1] + self.sprite.get_rect().bottom - self.pen.get_rect().h) - 8

        # Positionnement de l'ombre
        self.shadow_pos[0] = round(self.pos[0] + (self.sprite.get_rect().w - self.shadow.get_rect().w) / 2)
        self.shadow_pos[1] = round(self.pos[1] + self.sprite.get_rect().h - self.shadow.get_rect().h)


    def animer(self, frame: "int | float") -> None:
        """
        Cette méthode permet d'animer le sprite du joueur.

        Paramètres:
            - frame (int ou float): Indique la frame actuelle du serveur. Utilisée pour la vitesse
            des sprites de l'animation.
        """

        # Test du type de delta_time
        assert type(frame) == int or type(frame) == float, "Erreur: Le paramètre donné (frame) doit être un nombre."

        # N'a pas d'animation s'il ne dessine pas
        if self.is_drawing:
            # Changement du sprite actuel
            self.sprite = self.sprites["trace"][floor(frame % len(self.sprites["trace"]))]
        else:
            self.sprite = self.sprites["idle"]



    def afficher(self, screen: pygame.Surface) -> None: # type: ignore
        """
        Cette méthode permet de dessiner le joueur sur l'écran.

        Paramètres:
            - screen (pygame.Surface): L'écran de jeu de pygame.
        """

        # Tests des types de variables
        assert type(screen) == pygame.Surface, "Erreur: Le 1er paramètre (screen) n'est pas une surface pygame."

        # Initialisation des facteurs pour la taille de l'écran
        screen_factor = ((screen.get_rect().size[0] / 1280), (screen.get_rect().size[1] / 720))

        # Affichage de l'ombre du joueur
        screen.blit(scale_image_by(self.shadow, screen_factor), (round(self.shadow_pos[0] * screen_factor[0]), round(self.shadow_pos[1] * screen_factor[1])))

        # Affiche le crayon uniquement si le joueur dessine
        if self.is_drawing:
            screen.blit(scale_image_by(self.pen, screen_factor), (round(self.pen_pos[0] * screen_factor[0]), round(self.pen_pos[1] * screen_factor[1])))

        # Affichage du sprite du joueur
        screen.blit(scale_image_by(self.sprite, screen_factor), (round(self.pos[0] * screen_factor[0]), round(self.pos[1] * screen_factor[1])))



# Classe permettant de créer les points (hérité de la classe Sprite de pygame)
class Point(pygame.sprite.Sprite):

    # ------/ Constructeur \------

    def __init__(self, pos: list, color: str) -> None:
        """
        Constructeur de la classe Point, qui hérite de pygame.sprite.Sprite.

        Attributs à définir:
            - base_pos (list): Position de base du point.
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

        self.base_pos = pos

        # Sprites de chaque point
        minigame_directory = sep.join(["..", "data", "sprites", "minigames", "trace_race"])
        self.points = {
            "red": pygame.image.load(sep.join([minigame_directory, "red_point.png"])),
            "blue": pygame.image.load(sep.join([minigame_directory, "blue_point.png"])),
            "green": pygame.image.load(sep.join([minigame_directory, "green_point.png"])),
            "yellow": pygame.image.load(sep.join([minigame_directory, "yellow_point.png"]))
        }

        # Sprite actuel
        self.image = self.points[color]

        # Rectangle créé à partir du point
        self.rect = pygame.Rect(round(self.base_pos[0]), round(self.base_pos[1]), self.image.get_rect().w, self.image.get_rect().h)


    # ------/ Méthodes \------
    def update(self, cam_pos: list) -> None:
        """
        Cette méthode permet de déplacer le point en fonction de la caméra.

        Paramètres:
            - cam_pos (list): Position de la caméra.
        """

        # Test du type de cam_mov
        assert type(cam_pos) == list, "Erreur: Le paramètre donné (cam_mov) n'est pas une liste."

        self.rect.x = round(self.base_pos[0] - cam_pos[0])


    def afficher(self, screen: pygame.Surface) -> None: # type: ignore
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
            screen.blit(scale_image_by(self.image, screen_factor), (round(self.rect.x * screen_factor[0]), round(self.rect.y * screen_factor[1])))



# Classe du mini-jeu (enfin)
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

            - show_fps (bool): Paramètre de débug permettant d'afficher les fps du client.
            - show_server_fps (bool): Paramètre de débug permettant d'afficher les fps du serveur.

            - fps_font (pygame.freetype.Font): Police d'écriture pour les fps.
            - game_font (pygame.freetype.Font): Police d'écriture principale du mini-jeu.

            - joueurs (list): Liste des joueurs.
            - objets (list): Liste des objets.

            - toad (list): Images du Toad de l'écran de chargement.
            - toad_shadow (pygame.Surface): Image de l'ombre de Toad.
            - toad_bubble (pygame.Surface): Image de la bulle de dialogue de Toad. 

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
        self.objets = []

        # Sprites de toad (pour le chargement)
        self.toad = [pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "general", "toad", "toad.png"])),
                     pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "general", "toad", "toad_open.png"]))]
        self.toad_shadow = pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "general", "toad", "shadow.png"]))
        self.toad_bubble = pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "general", "toad", "bubble.png"]))

        # Initialisation de la caméra
        self.camera_pos = [0, 0]

        # Initialisation des tracés
        self.traces = {}

        self.bg = pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "trace_race", "map.png"]))
        self.bg_traces = pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "trace_race", "traces.png"]))

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
        infos_environnement = json.loads(self.net.send(str(input_joueur[0]) + "|" + str(input_joueur[1])))
        infos_joueurs = infos_environnement["joueurs"]
        infos_point = infos_environnement["point"]
        self.camera_pos = infos_environnement["camera"]
        fps = infos_environnement["fps"]

        # Affichage du décor
        self.screen.blit(scale_image_by(self.bg, self.screen_factor), (round(-self.camera_pos[0] * self.screen_factor[0]), 0))

        # Affichage des points colorés (ou du tracé entier à la fin du mini-jeu)
        for id_joueur in self.joueurs.keys():
            if len(infos_point[id_joueur]) > 1 and self.joueurs[id_joueur].get_is_drawing():
                self.traces[id_joueur].add(Point([self.camera_pos[0] + infos_point[id_joueur][0][0], infos_point[id_joueur][0][1]], infos_point[id_joueur][1]))

        for trace in self.traces.values():
            if type(trace) != pygame.Surface:
                # On les déplace tous vers la gauche en suivant la caméra
                trace.update(self.camera_pos)

                # On affiche chacun des points crées
                for sprite in trace:
                    sprite.afficher(self.screen)
            else:
                self.screen.blit(scale_image_by(trace, self.screen_factor), (round(-self.camera_pos[0] * self.screen_factor[0]), 0))

        # Affichage des tracés de référence
        self.screen.blit(scale_image_by(self.bg_traces, self.screen_factor), (round(-self.camera_pos[0] * self.screen_factor[0]), 0))

        # On met à jour la position des joueurs et des animations pour le client et on affiche les joueurs
        for id_joueur in self.joueurs.keys():
            self.joueurs[id_joueur].set_is_drawing(infos_joueurs[id_joueur]["is_drawing"])
            self.joueurs[id_joueur].appliquer_positions(infos_joueurs[id_joueur]["pos"])
            self.joueurs[id_joueur].animer(infos_joueurs[id_joueur]["frame"])
            self.joueurs[id_joueur].afficher(self.screen)

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
        description = ["Tracez votre ligne sur le sol",
                       "en suivant le chemin.",
                       "Le tracé qui ressemble le plus au",
                       "chemin d'origine gagne !"]

        nom = "Trace Race"
        chemin_musique = sep.join(["..", "data", "musics", "minigames", "trace_race.ogg"])

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

        # Envoi d'une requête au serveur pour obtenir les infos de chaque joueur
        infos_joueurs = json.loads(self.net.send("0|0"))["joueurs"]

        # Création des joueurs
        for ip in infos_joueurs.keys():
            self.joueurs[ip] = Joueur(infos_joueurs[ip]["perso"], infos_joueurs[ip]["color"])

        # Envoi de la taille du joueur au serveur
        self.net.send(json.dumps({"taille_joueurs": {joueur: self.joueurs[joueur].get_taille() for joueur in self.joueurs.keys()}}))

        # Initialisation de la liste des objets
        self.objets = self.joueurs

        # Initialisation des tracés de chaque joueur
        self.traces = {joueur: pygame.sprite.Group() for joueur in self.joueurs}

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
            self.game_engine([0, 0])

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

        # Lancement du son de sifflet et la musique chargée
        pygame.mixer.Sound(sep.join(["..", "data", "sounds", "minigames", "start_sifflet.ogg"])).play()
        pygame.mixer.music.play()

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
            running = etat == "minigame_during"

            # Détection des inputs et réinitialisation des vecteurs de déplacement des joueurs
            inputs = pygame.key.get_pressed()
            input_joueur = [0, 0]

            # Comportement du joueur
            if self.joueurs[self.net.adresse_client].get_is_drawing():
                if inputs[pygame.K_a] or inputs[pygame.K_q]:
                    input_joueur[0] -= 1
                if inputs[pygame.K_s]:
                    input_joueur[1] += 1
                if inputs[pygame.K_w] or inputs[pygame.K_z]:
                    input_joueur[1] -= 1
                if inputs[pygame.K_d]:
                    input_joueur[0] += 1

            # Utilisation du moteur de jeu et mise à jour du temps passé
            self.game_engine(input_joueur)

            """
            # Léger délai entre chaque placement de point sinon grosse baisse de performance
            if cooldown - time.time() <= 0:
                for joueur in self.joueurs:
                    if joueur.get_is_drawing():
                        # Chaque point ajouté au tracé est un objet que l'on ajoute dans le groupe de sprites présent dans self.traces
                        self.traces[joueur].add(Point([joueur.get_pen_pos()[0] + 4, joueur.get_pen_pos()[1] + 86], joueur.get_color()))

                # Délai de 0.02s
                cooldown = 0.02 + time.time()
            """

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
            self.game_engine([0, 0])

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

        # Lancement du calcul des scores (si le joueur n'a pas fermé la fenêtre)
        if not self.quit:
            self.calculate_score()


    def calculate_score(self) -> None:
        """
        Cette méthode permet de calculer les scores de chaque joueur.
        """

        # Initialisation des paramètres par défaut de la phase
        running = True
        prev_time = time.time()

        # Initialisation des tracés dessinés par chaque joueurs
        made_traces = {joueur: pygame.Surface((self.bg_traces.get_rect().w, self.bg_traces.get_rect().h), pygame.SRCALPHA) for joueur in self.joueurs.keys()}

        for joueur in self.joueurs.keys():
            for sprite in self.traces[joueur]:
                # On regroupe chaque point dans un seul sprite de tracé
                made_traces[joueur].blit(sprite.image, (sprite.rect.x + 20, sprite.rect.y))

            # On remplace le groupe de sprites par le nouveau tracé pour optimiser les performances
            self.traces[joueur] = made_traces[joueur]

        # Masque de chaque tracé de chaque joueur
        made_traces_masks = {joueur: pygame.mask.from_surface(made_traces[joueur]) for joueur in self.joueurs.keys()}

        # Masque des tracés sur le terrain
        bg_traces_mask = pygame.mask.from_surface(self.bg_traces)

        # Nombre de pixels repassés par le joueur
        # (overlap_area renvoie le nombre de pixels qui se superposent entre deux masques)
        nb_pixels_joueurs = {joueur: made_traces_masks[joueur].overlap_area(bg_traces_mask, (0, 0)) for joueur in self.joueurs.keys()}

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

        # On stocke les pourcentages de réussite de chaque joueur
        pourcentages = {joueur: round((nb_pixels_joueurs[joueur] / nb_pixels_ligne) * 100, 1) for joueur in self.joueurs.keys()}

        # On utilise toujours la méthode simple: on trie automatiquement les clés du dictionnaire
        sorted_pourcentages = sorted(pourcentages, key=pourcentages.get, reverse=True)

        # Sprite du fond des pourcentages
        pourcent_back = pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "trace_race", "pourcent_back.png"]))

        # Les pourcentages qui seront utilisés pour l'affichage
        draw_pourcentages = {joueur: 0 for joueur in self.joueurs.keys()}

        # La méthode dure 5 secondes
        timer = 5 + time.time()

        # Initialisation d'une variable qui détecte si la requête pour le serveur a déjà été envoyée
        sent = False

        # Roulements de tambour
        pygame.mixer.Sound(sep.join(["..", "data", "sounds", "minigames", "trace_race", "drum_roll.ogg"])).play()

        # Boucle principale de cette phase du jeu
        while running and not self.quit:

            # Détection de la fermeture de fenêtre
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit = True

                # Changement de taille de la fenêtre
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)

            # Arrêt de la méthode à la fin du temps imparti
            if timer - time.time() <= 0 and not sent:
                ids_minijeu = self.net.send(json.dumps({"pourcentages": list(sorted_pourcentages)}))
                sent = self.net.send("ready_for_next_state") == "ok"

            # Envoie d'une requête au serveur pour obtenir son etat
            etat = self.net.send("get_etat")
            running = etat == "minigame_score"

            # Utilisation du moteur de jeu et mise à jour du temps passé
            self.game_engine([0, 0])

            # Calcul rapide du delta_time (uniquement pour cette animation)
            delta_time = time.time() - prev_time
            prev_time = time.time()

            # Affichage des scores
            for joueur in self.joueurs.keys():
                # La formule utilisé ici permet d'avoir a peu près le même temps d'attente pour n'importe quel pourcentage
                if draw_pourcentages[joueur] < pourcentages[joueur]:
                    draw_pourcentages[joueur] += (pourcentages[joueur] / 4) * delta_time
                else:
                    draw_pourcentages[joueur] = pourcentages[joueur]

                # Définition du décalage pour chaque joueur
                ids_minijeu = json.loads(self.net.send("get_ids_minijeu"))
                pourcent_pos_y = 90 + (150 * int(ids_minijeu[joueur]))

                # Affichage des pourcentages
                self.screen.blit(scale_image_by(pourcent_back, (4 * self.screen_factor[0], 4 * self.screen_factor[1])), (round(1000 * self.screen_factor[0]), round(pourcent_pos_y * self.screen_factor[1])))
                pourcentage_text = self.game_font.render(str(round(draw_pourcentages[joueur], 1)) + "%", (255, 255, 255))
                pourcentage_text_scaled = scale_image_by(pourcentage_text[0], self.screen_factor)

                # Affichage du pourcentage
                self.screen.blit(pourcentage_text_scaled, (round(1013 * self.screen_factor[0]), round((pourcent_pos_y + 20) * self.screen_factor[1])))

            # Mise à jour de l'écran et limite de fps
            pygame.display.flip()
            self.clock.tick(self.fps)

        # Lancement de l'annonce des gagnants (si le joueur n'a pas fermé la fenêtre)
        if not self.quit:
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
                self.game_engine([0, 0])
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