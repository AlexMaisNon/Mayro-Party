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

    def __init__(self, perso: str, side: str) -> None:
        """
        Constructeur de la classe Joueur.

        Attributs à définir:
            - perso (str): Personnage choisit par le joueur.
            - side (str): Côté du joueur (left ou right) (exclusif à ce mini-jeu).

        Attributs internes:
            - speed (int): Vitesse du joueur.

            - sprites_directory (str): Chemin du dossier des sprites du joueur.
            - sprites (dict): Sprites du joueurs.
            - sprite (pygame.Surface): Sprite actuel du joueur.
            - sprite_pos (list): Position du sprite (du pistolet si solo ou du joueur sinon).
            - platforme (pygame.Surface): Sprite de la plateforme du joueur.

            - shadow (pygame.Surface): Sprite de l'ombre du joueur.
            - shadow_pos (list): Position de l'ombre.
        """

        # Tests du type des paramètres donnés
        assert type(perso) == str, "Erreur: Le 1er paramètre (perso) est censé être une chaîne de caractères."
        assert type(side) == str, "Erreur: Le 2ème paramètre (side) est censé être une chaîne de caractères."


        # Définition du joueur
        self.perso = perso
        self.side = side

        # Caractéristiques principales (stats)
        self.pos = [0.0, 0.0]

        # Emplacement des sprites du joueur
        self.sprites_directory = sep.join(["..", "data", "sprites", "characters", self.perso])

        # Définition des sprites automatiquement
        self.sprites = {"left": [scale_image_by(pygame.image.load(sep.join([self.sprites_directory, "hockey_left" + str(i) + ".png"])), 3) for i in range(4)],
                        "right": [scale_image_by(pygame.image.load(sep.join([self.sprites_directory, "hockey_right" + str(i) + ".png"])), 3) for i in range(4)]
        }

        # Initialisation / positionnement du sprite actuel
        self.sprite = self.sprites[self.side][0]
        self.sprite_pos = list(self.pos)

        # Sprite de la plateforme du joueur
        self.platforme = scale_image_by(pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "speed_hockey", self.side + "_platform.png"])), 3)

        # Initialisation et positionnement de l'ombre
        self.shadow = scale_image_by(pygame.image.load(sep.join([self.sprites_directory, "shadow.png"])), 3)
        self.shadow_pos = list(self.pos)


    # ------/ Getters \------

    def get_perso(self) -> str:
        return self.perso


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

        # Positionnement du sprite du joueur sur la plateforme
        self.sprite_pos[0] = round(self.pos[0] - (self.sprite.get_rect().w - self.platforme.get_rect().w) / 2)
        self.sprite_pos[1] = round(self.pos[1] - self.sprite.get_rect().bottom + self.platforme.get_rect().h / 2)

        # Positionnement de l'ombre
        self.shadow_pos[0] = round(self.sprite_pos[0] + (self.sprite.get_rect().w - self.shadow.get_rect().w) / 2)
        self.shadow_pos[1] = round(self.sprite_pos[1] + self.sprite.get_rect().h - self.shadow.get_rect().h)


    def animer(self, frame: "int | float") -> None:
        """
        Cette méthode permet d'animer le sprite du joueur.

        Paramètres:
            - frame (int ou float): Indique la frame actuelle du serveur. Utilisée pour la vitesse
            des sprites de l'animation.
        """

        # Test du type de frame
        assert type(frame) == float, "Erreur: Le paramètre donné (frame) doit être un nombre."

        # Changement du sprite actuel
        self.sprite = self.sprites[self.side][floor(frame % len(self.sprites[self.side]))]


    def afficher(self, screen: pygame.Surface) -> None: # type: ignore
        """
        Cette méthode permet de dessiner le joueur sur l'écran.

        Paramètres:
            - screen (pygame.Surface): L'écran de jeu de pygame.
        """

        # Tests des types de variables
        assert type(screen) == pygame.Surface, "Erreur: Le paramètre donné (screen) n'est pas une surface pygame."

        # Initialisation des facteurs pour la taille de l'écran
        screen_factor = ((screen.get_rect().size[0] / 1280), (screen.get_rect().size[1] / 720))

        # Affichage des sprites
        screen.blit(scale_image_by(self.platforme, screen_factor), (round(self.pos[0] * screen_factor[0]), round(self.pos[1] * screen_factor[1])))
        screen.blit(scale_image_by(self.shadow, screen_factor), (round(self.shadow_pos[0] * screen_factor[0]), round(self.shadow_pos[1] * screen_factor[1])))
        screen.blit(scale_image_by(self.sprite, screen_factor), (round(self.sprite_pos[0] * screen_factor[0]), round(self.sprite_pos[1] * screen_factor[1])))



# Classe de la carapace
class Carapace:

    # ------/ Constructeur \------

    def __init__(self) -> None:
        """
        Constructeur de la classe Carapace.

        Attributs internes:
            - pos (list): Position de la carapace.

            - sprite (pygame.Surface): Sprite actuel de la carapace.

            - hit_sound (pygame.mixer.Sound): Son de collision avec la carapace.
        """

        # Caractéristiques principales
        self.pos = [0.0, 0.0]

        # Sprite actuel
        self.sprite = scale_image_by(pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "speed_hockey", "carapace.png"])), 3)

        # Paramètres du son
        self.hit_sound = pygame.mixer.Sound(sep.join(["..", "data", "sounds", "minigames", "speed_hockey", "carapace.ogg"]))


    # ------/ Getters \------

    def get_pos(self) -> list:
        return self.pos

    def get_hit_sound(self) -> pygame.mixer.Sound: # type: ignore
        return self.hit_sound


    # ------/ Méthodes \------
    def appliquer_positions(self, position) -> None:
        """
        Cette méthode permet d'appliquer la position à la carapace.

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

        # On applique la nouvelle position à la carapace
        self.pos = position


    def afficher(self, screen: pygame.Surface) -> None: # type: ignore
        """
        Cette méthode permet de dessiner le joueur sur l'écran.

        Paramètres:
            - screen (pygame.Surface): L'écran de jeu de pygame.
        """

        # Tests des types de variables
        assert type(screen) == pygame.Surface, "Erreur: Le paramètre donné (screen) n'est pas une surface pygame."

        # Initialisation des facteurs pour la taille de l'écran
        screen_factor = ((screen.get_rect().size[0] / 1280), (screen.get_rect().size[1] / 720))

        # Affichage de la carapace
        screen.blit(scale_image_by(self.sprite, screen_factor), (round(self.pos[0] * screen_factor[0]), round(self.pos[1] * screen_factor[1])))



# Classe d'un but
class But:

    # ------/ Constructeur \------

    def __init__(self, pos, sprite) -> None:
        """
        Constructeur de la classe But.

        Attributs à définir:
            - pos (list): Position du but.
            - sprite (pygame.Surface): Sprite du but.
        """

        # Test des types des paramètres donnés
        assert type(pos) == list, "Erreur: Le 1er paramètre (pos) n'est pas une liste."
        assert type(sprite) == pygame.Surface, "Erreur: Le 2ème paramètre (sprite) n'est pas une image pygame."

        # Caractéristiques du but
        self.pos = pos
        self.sprite = sprite


    # ------/ Getter \------

    def get_pos(self) -> list:
        return self.pos


    # ------/ Méthode \------

    def afficher(self, screen: pygame.Surface) -> None: # type: ignore
        """
        Cette méthode permet de dessiner le collider sur l'écran.

        Paramètres:
            - screen (pygame.Surface): L'écran de jeu de pygame.
        """

        # Tests des types de variables
        assert type(screen) == pygame.Surface, "Erreur: Le 1er paramètre (screen) n'est pas une surface pygame."

        # Initialisation des facteurs pour la taille de l'écran
        screen_factor = ((screen.get_rect().size[0] / 1280), (screen.get_rect().size[1] / 720))

        # Affichage du but
        screen.blit(scale_image_by(self.sprite, screen_factor), (round(self.pos[0] * screen_factor[0]), round(self.pos[1] * screen_factor[1])))



# Classe du mini-jeu
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

            - show_fps (bool): Paramètre de débug permettant d'afficher les fps.
            - show_server_fps (bool): Paramètre de débug permettant d'afficher les fps du serveur.

            - fps_font (pygame.freetype.Font): Police d'écriture pour les fps.
            - game_font (pygame.freetype.Font): Police d'écriture principale du mini-jeu.

            - joueurs (list): Liste des joueurs.
            - objets (list): Liste des objets.

            - timer_background (pygame.Surface): Image de fond du timer.

            - toad (list): Images du Toad de l'écran de chargement.
            - toad_shadow (pygame.Surface): Image de l'ombre de Toad.
            - toad_bubble (pygame.Surface): Image de la bulle de dialogue de Toad. 

            - bg (pygame.Surface): Image de fond pour le mini-jeu.
            - ligne_rouge (pygame.Surface): Image de la ligne rouge.
            - ligne_verte (pygame.Surface): Image de la ligne verte.
            - lampes_rouges (list): Image des lampes rouges.
            - lampes_vertes (list): Image des lampes vertes.

            - carapace (Carapace): Carapace.
            - colliders (list): Liste des boîtes de collision du mini-jeu.
            - buts (list): Liste des deux buts du mini-jeu.

            - son_but (pygame.mixer.Sound): Son du sifflet des buts.
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

        # Image de fond du timer
        self.timer_background = pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "general", "timer_back.png"]))

        # Sprites de toad (pour le chargement)
        self.toad = [pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "general", "toad", "toad.png"])),
                     pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "general", "toad", "toad_open.png"]))]
        self.toad_shadow = pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "general", "toad", "shadow.png"]))
        self.toad_bubble = pygame.image.load(sep.join(["..", "data", "sprites", "minigames", "general", "toad", "bubble.png"]))

        # Sprites utilisés dans toute la classe
        minigame_directory = sep.join(["..", "data", "sprites", "minigames", "speed_hockey"])
        self.bg = pygame.image.load(sep.join([minigame_directory, "hockey.png"]))
        self.ligne_rouge = pygame.image.load(sep.join([minigame_directory, "ligne_rouge.png"]))
        self.ligne_verte = pygame.image.load(sep.join([minigame_directory, "ligne_verte.png"]))
        self.lampes_rouges = [pygame.image.load(sep.join([minigame_directory, "lampe_rouge_eteinte.png"])),
                              pygame.image.load(sep.join([minigame_directory, "lampe_rouge.png"]))]
        self.lampes_vertes = [pygame.image.load(sep.join([minigame_directory, "lampe_verte_eteinte.png"])),
                              pygame.image.load(sep.join([minigame_directory, "lampe_verte.png"]))]

        self.carapace = Carapace()

        self.buts = [But([0, 156], scale_image_by(pygame.image.load(sep.join([minigame_directory, "but_rouge.png"])), 4)),
                     But([1180, 156], scale_image_by(pygame.image.load(sep.join([minigame_directory, "but_vert.png"])), 4))]

        # Initialisation du son du sifflet des buts
        self.son_but = pygame.mixer.Sound(sep.join(["..", "data", "sounds", "minigames", "speed_hockey", "sifflet.ogg"]))

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
        pos_carapace = infos_environnement["carapace"]
        score = infos_environnement["score"]
        timer = infos_environnement["timer"]
        fps = infos_environnement["fps"]

        # On affiche les sprites du jeu dans un ordre d'affichage prédéfini
        self.screen.blit(scale_image_by(self.bg, self.screen_factor), (0, 0))

        # Placement des lignes sur le terrain
        self.screen.blit(scale_image_by(self.ligne_rouge, (4 * self.screen_factor[0], 4 * self.screen_factor[1])), (round(200 * self.screen_factor[0]), round(200 * self.screen_factor[1])))
        self.screen.blit(scale_image_by(self.ligne_rouge, (4 * self.screen_factor[0], 4 * self.screen_factor[1])), (round(400 * self.screen_factor[0]), round(200 * self.screen_factor[1])))

        self.screen.blit(scale_image_by(self.ligne_verte, (4 * self.screen_factor[0], 4 * self.screen_factor[1])), (round(852 * self.screen_factor[0]), round(200 * self.screen_factor[1])))
        self.screen.blit(scale_image_by(self.ligne_verte, (4 * self.screen_factor[0], 4 * self.screen_factor[1])), (round(1052 * self.screen_factor[0]), round(200 * self.screen_factor[1])))

        # Placement des lampes sur le terrain
        offset = 0
        for i in range(3):
            # On allume les lampes en fonction de la taille du score par rapport à i
            if i < score[0]:
                self.screen.blit(scale_image_by(self.lampes_rouges[1], (2 * self.screen_factor[0], 2 * self.screen_factor[1])), (round((80 + offset) * self.screen_factor[0]), round(8 * self.screen_factor[1])))
            else:
                self.screen.blit(scale_image_by(self.lampes_rouges[0], (2 * self.screen_factor[0], 2 * self.screen_factor[1])), (round((80 + offset) * self.screen_factor[0]), round(8 * self.screen_factor[1])))
            # Augmentation du décalage de chaque lampe
            offset += 100

        offset = 0
        for i in range(3):
            # On allume les lampes en fonction de la taille du score par rapport à i
            if i < score[1]:
                self.screen.blit(scale_image_by(self.lampes_vertes[1], (2 * self.screen_factor[0], 2 * self.screen_factor[1])),(round((920 + offset) * self.screen_factor[0]), round(8 * self.screen_factor[1])))
            else:
                self.screen.blit(scale_image_by(self.lampes_vertes[0], (2 * self.screen_factor[0], 2 * self.screen_factor[1])), (round((920 + offset) * self.screen_factor[0]), round(8 * self.screen_factor[1])))
            # Augmentation du décalage de chaque lampe
            offset += 100

        # On met à jour la position des joueurs et des animations pour le client
        for id_joueur in self.joueurs.keys():
            self.joueurs[id_joueur].appliquer_positions(infos_joueurs[id_joueur]["pos"])
            self.joueurs[id_joueur].animer(infos_joueurs[id_joueur]["frame"])

        # On met à jour la position de la carapace
        self.carapace.appliquer_positions(pos_carapace)

        # On active les sons si le serveur l'a indiqué
        if infos_joueurs[self.net.adresse_client]["lancer_son_hit"]:
            self.carapace.get_hit_sound().play()
            self.net.send("desactive_son_hit")
        if infos_joueurs[self.net.adresse_client]["lancer_son_but"]:
            self.son_but.play()
            self.net.send("desactive_son_but")

        # Affichage des objets sur l'écran
        for objet in self.objets:
            objet.afficher(self.screen)

        # Affichage du timer seulement s'il est actuellement en train de compter
        if timer >= 0:
            # Affichage du fond du timer
            timer_sprite = scale_image_by(self.timer_background, self.screen_factor)
            timer_background_textRect = timer_sprite.get_rect()
            timer_background_textRect.center = (self.screen.get_rect().w // 2, round(37 * self.screen_factor[1]))
            self.screen.blit(timer_sprite, timer_background_textRect)

            # Positionnement du timer au centre-haut de l'écran
            timer_text = self.game_font.render(str(timer), (255, 255, 255))
            timer_text_scaled = scale_image_by(timer_text[0], self.screen_factor)
            timer_textRect = timer_text_scaled.get_rect()
            timer_textRect.center = (self.screen.get_rect().w // 2, round(37 * self.screen_factor[1]))

            # Affichage du timer
            self.screen.blit(timer_text_scaled, timer_textRect)

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
        description = ["Joueurs en équipe:",
                       "Faites rebondir la carapace",
                       "pour la faire rentrer dans les",
                       "buts adverses !"]

        nom = "Speed Hockey"
        chemin_musique = sep.join(["..", "data", "musics", "minigames", "speed_hockey.ogg"])

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
            self.joueurs[ip] = Joueur(infos_joueurs[ip]["perso"], infos_joueurs[ip]["side"])

        # Initialisation de la liste des objets
        self.objets = [self.carapace] + self.buts + list(self.joueurs.values())

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

            # Détection des inputs et réinitialisation des vecteurs de déplacement des objets
            inputs = pygame.key.get_pressed()
            input_joueur = [0, 0]

            # Comportement du joueur
            if inputs[pygame.K_w] or inputs[pygame.K_z]:
                input_joueur[1] -= 1
            if inputs[pygame.K_s]:
                input_joueur[1] += 1

            # Utilisation du moteur de jeu
            self.game_engine(input_joueur)

            # Si la carapace rentre dans le but vert
            if self.carapace.get_pos()[0] > self.buts[1].get_pos()[0]:
                # Son du sifflet
                self.son_but.play()

            # Si la carapace rentre dans le but rouge
            elif self.carapace.get_pos()[0] < self.buts[0].get_pos()[0]:
                # Son du sifflet
                self.son_but.play()

            # Mise à jour de l'écran et limite de fps
            pygame.display.flip()
            self.clock.tick(self.fps)

        # Lancement de l'affichage de fin (si le joueur n'a pas fermé la fenêtre)
        if not self.quit:

            # On arrête le mini-jeu
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