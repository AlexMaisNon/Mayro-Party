#Projet : Mayro Party
#Auteurs : Hinata Bouaziz, Antoine Desrues, Alexandre Guillaume, Matisse Moreau

# ------/ Importations des bibliothèques \------

import pygame, random
import pygame.freetype
import pygame.ftfont
from pygame import mixer

import time
from os import sep

from _thread import start_new_thread
from utils import Network, scale_image_by
import json
from server import Server

# ------/ Importations des mini-jeux clients \------

import archer_ival_client
import hexagon_heat_client
import pushy_penguins_client
import speed_hockey_client
import trace_race_client


# ------/ Fonctions utiliatires \------

def center_text(text: str, font: pygame.font.Font, position: "list | tuple", echelle: "list | tuple | None" = None, color: tuple = (255, 255, 255)): # type: ignore
    """
    Cette fonction permet de créer un texte automatiquement centré sur la positon demandée.

    Paramètres:
        - text (str): une chaîne de caractères représentant le texte à créer.
        - font (pygame.font.Font): police d'écriture sur laquelle écrire le texte.
        - position (list ou tuple): position du texte à placer.

    Renvois:
        - list: une liste représentant le texte créé et son rectangle (sa position).

    Post-conditions:
        - La fonction doit renvoyer dans une liste le texte centré ainsi que sa position, créé à partir
        de la police, de la chaîne de caractère et de la position souhaitée.
    """

    # Test des types de variables
    assert type(text) == str, "Erreur: le paramètre text donné n'est pas une chaîne de caractères."
    assert type(font) == pygame.font.Font, "Erreur: le paramètre text donné n'est pas une police d'écriture de pygame."
    assert type(position) == list or type(position) == tuple, "Erreur: le paramètre position donné n'est pas une liste."
    assert type(echelle) == list or type(echelle) == tuple or echelle == None, "Erreur: le paramètre echelle donné n'est pas une liste."
    assert type(color) == tuple, "Erreur: le paramètre color donné n'est pas un tuple."

    # On crée une surface représentant le texte
    text_surface = font.render(text, True, color)
    if echelle != None:
        text_surface = pygame.transform.scale(text_surface, (round(text_surface.get_rect().w * echelle[0]), round(text_surface.get_rect().h * echelle[1])))

    # On change le centre de son rectangle, le centrant à la position demandée
    text_rect = text_surface.get_rect()
    text_rect.center = position

    # On renvoie le tout dans une liste
    return [text_surface, text_rect]


# ------/ Classes \------

# Classe pour les boutons
class Button():
    def __init__(self, color: tuple, x: int, y: int, width: int, height: int, text: str = '', font: "pygame.font.Font | None" = None, image: "pygame.Surface | None" = None): # type: ignore
        '''
        Cette classe sert à créer des boutons avec ou sans image et ou texte.

        Attributs : 
            self.color (tuple) : couleur du bouton.
            self.x (int) : abscisse du bouton.
            self.y (int) : ordonnée du bouton.
            self.width (int) : largeur du bouton en pixel.
            self.height (int) : hauteur du bouton en pixel.
            self.text (str) : chaine de caractère.
            self.font (pygame.font.Font ou None) : police du texte.
            self.image (pygame.Surface ou None) : image pour un bouton.

        Pré-conditions:
            x doit être un entier positif.
            y doit être un entier positif.
            width doit être un entier positif non nul.
            height doit être un entier positif non nul.
            text doit être une chaine de caractère.
            image doit être une instance de pygame.Surface.
            font doit être une instance de pygame.font.Font.

        Post-conditions:
            Si toutes les pré-conditions sont vérifiés, alors le programme doit afficher un ou
            des boutons avec des coordonnées, du texte si il en a et une image si il y en a.
        '''

        # Tests de type des paramètres
        assert type(color) == tuple, "Erreur: Le paramètre color n'est pas un tuple."
        assert type(x) == int, "Erreur: Le paramètre x n'est pas un entier."
        assert type(y) == int, "Erreur: Le paramètre y n'est pas un entier."
        assert type(width) == int, "Erreur: Le paramètre width n'est pas un entier."
        assert type(height) == int, "Erreur: Le paramètre height n'est pas un entier."
        assert type(text) == str, "Erreur: Le paramètre text n'est pas une chaîne de caractères."
        assert type(font) == pygame.font.Font or font == None, "Erreur: Le paramètre font doit être une instance de pygame.font.Font ou None."
        assert type(image) == pygame.Surface or image == None, "Erreur: Le paramètre image doit être une instance de pygame.Surface ou None."

        # Test des valeurs des paramètres
        assert x >= 0, "Erreur: x doit être un entier positif."
        assert y >= 0, "Erreur: x doit être un entier positif."
        assert width > 0, "Erreur: x doit être un entier positif non nul."
        assert height > 0, "Erreur: x doit être un entier positif non nul."

        #Initialisation de la couleur
        self.color = color

        #Initialisation de la position, et dimention du bouton
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        #Initalisation d'un texte pour le bouton
        self.text = text

        #Initialisation d'une image pour le bouton
        self.image = image

        #Initialisation de la police pour le bouton
        self.font = font

    # Getters

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height


    # Setters

    def set_text(self, text):
        self.text = text


    # Méthodes

    def draw(self, screen: pygame.Surface) -> None: # type: ignore
        """
        Cette méthode permet d'afficher le bouton selon différents paramètres.

        Paramètres:
            - screen (pygame.Surface): écran de pygame.
        """

        # Test du type de screen
        assert type(screen) == pygame.Surface, "Erreur: Le paramètre screen donné n'est pas un écran de pygame."

        # Initialisation des facteurs pour la taille de l'écran
        screen_factor = ((screen.get_rect().size[0] / 1280), (screen.get_rect().size[1] / 720))

        #Si une image est donnée, elle est redimensionnée, puis affichée comme un bouton
        if self.image:
            scaled_image = pygame.transform.scale(self.image, (round(self.width * screen_factor[0]), round(self.height * screen_factor[1])))
            screen.blit(scaled_image, (round(self.x * screen_factor[0]), round(self.y * screen_factor[1])))

        #Sinon une surface est créée, puis remplie d'une couleur donné, puis affichée comme bouton
        else:
            surface = pygame.Surface((round(self.width * screen_factor[0]), round(self.height * screen_factor[1])), pygame.SRCALPHA)
            surface.fill(self.color)
            screen.blit(surface, (round(self.x * screen_factor[0]), round(self.y * screen_factor[1])))

        #Si un texte et une police d'écriture sont donnés, le texte a l'intéreur du bouton sera centré, puis affiché
        if self.text and self.font:
            text_surface = self.font.render(self.text, True, (255, 255, 255))
            text_surface = pygame.transform.scale(text_surface, (round(text_surface.get_rect().w * screen_factor[0]), round(text_surface.get_rect().h * screen_factor[1])))
            text_rect = text_surface.get_rect(center=(round((self.x + self.width // 2) * screen_factor[0]), round((self.y + self.height // 2) * screen_factor[1])))
            screen.blit(text_surface, text_rect)


    def is_clicked(self, pos: tuple, screen: pygame.Surface) -> bool: # type: ignore
        """
        Vérifie si la position de la souris se situe à l'intérieur du rectangle du bouton.

        Paramètres:
            - pos (tuple): Position de la souris.
            - screen (pygame.Surface): écran de pygame.
        Return:
            - bool: Indique si le bouton a été touché ou non.
        Post-conditions:
            - La méthode doit renvoyer True lorsque le bouton est en collision avec le point donné,
            ou False s'i n'y a aucune collision.
        """

        # Test du type de pos
        assert type(pos) == tuple, "Erreur: Le paramètre pos fournit n'est pas un tuple."

        # Initialisation des facteurs pour la taille de l'écran
        screen_factor = ((screen.get_rect().size[0] / 1280), (screen.get_rect().size[1] / 720))

        return pygame.Rect(round(self.x * screen_factor[0]), round(self.y * screen_factor[1]), round(self.width * screen_factor[0]), round(self.height * screen_factor[1])).collidepoint(pos)



# Classe pour les champs où on peut écrire
class InputField():
    def __init__(self, x: int, y: int, width: int, height: int, text: str = '', font: "pygame.font.Font | None" = None): # type: ignore
        '''
        Cette classe sert à créer des champs d'écriture avec ou sans texte par défaut.

        Attributs : 
            self.x (int) : abscisse du champ.
            self.y (int) : ordonnée du champ.
            self.width (int) : largeur du champ en pixel.
            self.height (int) : hauteur du champ en pixel.
            self.text (str) : chaine de caractère.
            self.font (pygame.font.Font ou None) : police du texte.
            self.active (bool) : indique si le champ est actif.
            self.text (str) : texte contenu dans le champ.

        Pré-conditions:
            x doit être un entier positif.
            y doit être un entier positif.
            width doit être un entier positif non nul.
            height doit être un entier positif non nul.
            text doit être une chaine de caractère.
            font doit être une instance de pygame.font.Font.

        Post-conditions:
            Si toutes les pré-conditions sont vérifiés, alors le programme doit afficher un ou
            des champs avec des coordonnées, du texte si il en a et une image si il y en a.
        '''

        # Tests de type des paramètres
        assert type(x) == int, "Erreur: Le paramètre x n'est pas un entier."
        assert type(y) == int, "Erreur: Le paramètre y n'est pas un entier."
        assert type(width) == int, "Erreur: Le paramètre width n'est pas un entier."
        assert type(height) == int, "Erreur: Le paramètre height n'est pas un entier."
        assert type(text) == str, "Erreur: Le paramètre text n'est pas une chaîne de caractères."
        assert type(font) == pygame.font.Font or font == None, "Erreur: Le paramètre font doit être une instance de pygame.font.Font ou None."

        # Test des valeurs des paramètres
        assert x >= 0, "Erreur: x doit être un entier positif."
        assert y >= 0, "Erreur: x doit être un entier positif."
        assert width > 0, "Erreur: x doit être un entier positif non nul."
        assert height > 0, "Erreur: x doit être un entier positif non nul."

        #Initialisation de la position, et dimention du champ
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        #Initalisation d'un par défaut texte pour le champ
        self.default_text = text

        #Initialisation de la police pour le champ
        self.font = font

        #Initialisation des paramètres du champ
        self.active = False
        self.text = ""

    # Getters

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_active(self):
        return self.active

    def get_text(self):
        return self.text


    # Setters

    def set_active(self, new_active):
        self.active = new_active


    # Méthodes

    def remove_character(self) -> None:
        """
        Cette méthode permet de supprimer le dernier caractère (avec le backspace).
        """

        if self.active:
            if len(self.text) > 1:
                self.text = self.text[:-1]
            else:
                self.text = ""

    def add_character(self, char: str) -> None:
        """
        Cette méthode permet d'ajouter un caractère au texte du champ.
        (Limite de 16 caratères)

        Paramètres:
            - char (str): caractère à ajouter.
        """

        if self.active and len(self.text) < 16:
            self.text += char

    def draw(self, screen: pygame.Surface) -> None: # type: ignore
        """
        Cette méthode permet d'afficher le bouton selon différents paramètres.

        Paramètres:
            - screen (pygame.Surface): écran de pygame.
        """

        # Test du type de screen
        assert type(screen) == pygame.Surface, "Erreur: Le paramètre screen donné n'est pas un écran de pygame."

        # Initialisation des facteurs pour la taille de l'écran
        screen_factor = ((screen.get_rect().size[0] / 1280), (screen.get_rect().size[1] / 720))

        #Une surface est créée, puis remplie d'une couleur
        surface = pygame.Surface((round(self.width * screen_factor[0]), round(self.height * screen_factor[1])), pygame.SRCALPHA)
        surface.fill((21, 34, 74))
        screen.blit(surface, (round(self.x * screen_factor[0]), round(self.y * screen_factor[1])))

        #Une autre surface est créée, puis remplie d'une deuxième couleur
        surface2 = pygame.Surface((round((self.width - 20) * screen_factor[0]), round((self.height - 20) * screen_factor[1])), pygame.SRCALPHA)
        surface2.fill((13, 24, 65))
        screen.blit(surface2, (round((self.x + 10) * screen_factor[0]), round((self.y + 10) * screen_factor[1])))

        #Si un texte et une police d'écriture sont donnés, le texte a l'intéreur du bouton sera centré, puis affiché
        if self.font:
            if self.text == "":
                default_text_color = (100, 100, 100) if self.active else (150, 150, 150)

                default_text_surface = self.font.render(self.default_text, True, default_text_color)
                default_text_surface = pygame.transform.scale(default_text_surface, (round(default_text_surface.get_rect().w * screen_factor[0]), round(default_text_surface.get_rect().h * screen_factor[1])))
                default_text_rect = default_text_surface.get_rect(center=(round((self.x + self.width // 2) * screen_factor[0]), round((self.y + self.height // 2) * screen_factor[1])))
                screen.blit(default_text_surface, default_text_rect)

            else:
                text_color = (230, 230, 230) if self.active else (255, 255, 255)

                text_surface = self.font.render(self.text, True, text_color)
                text_surface = pygame.transform.scale(text_surface, (round(text_surface.get_rect().w * screen_factor[0]), round(text_surface.get_rect().h * screen_factor[1])))
                text_rect = text_surface.get_rect(center=(round((self.x + self.width // 2) * screen_factor[0]), round((self.y + self.height // 2) * screen_factor[1])))
                screen.blit(text_surface, text_rect)



    def is_clicked(self, pos: tuple, screen: pygame.Surface) -> bool: # type: ignore
        """
        Vérifie si la position de la souris se situe à l'intérieur du rectangle du bouton.

        Paramètres:
            - pos (tuple): Position de la souris.
            - screen (pygame.Surface): écran de pygame.
        Return:
            - bool: Indique si le bouton a été touché ou non.
        Post-conditions:
            - La méthode doit renvoyer True lorsque le bouton est en collision avec le point donné,
            ou False s'i n'y a aucune collision.
        """

        # Test du type de pos
        assert type(pos) == tuple, "Erreur: Le paramètre pos fournit n'est pas un tuple."

        # Initialisation des facteurs pour la taille de l'écran
        screen_factor = ((screen.get_rect().size[0] / 1280), (screen.get_rect().size[1] / 720))

        return pygame.Rect(round(self.x * screen_factor[0]), round(self.y * screen_factor[1]), round(self.width * screen_factor[0]), round(self.height * screen_factor[1])).collidepoint(pos)



# Classe du jeu
class Game():
    def __init__(self) -> None:
        """
        Constructeur de la classe Game.

        Attributs internes:
            - screen (pygame.Surface): L'écran de jeu de pygame.
            - clock: L'horloge de pygame (permet de placer une limite de fps au jeu).
            - fps (int): Le nombre de fps maximal du jeu.

            - font (pygame.freetype.Font): Police d'écriture principale du jeu.
            - run (bool): Indique si le jeu est actif ou non.

            - joueurs (dict): Dictionnaire des joueurs en fonction de leur nom.
            - mini_jeux (dict): Dictionnaire des mini-jeux en fonction de leur nom.
            - classement (dict): Classement des joueurs à la fin du jeu.

            - current_screen (str): Indique l'écran actuel que voit le joueur.
            - title_screen (Title_screen): Écran titre du jeu.
            - select_mode (Select_mode): Écran de sélection du mode de jeu.
            - select_character (Select_character): Écran de sélection de personnages.
            - select_mini_jeux (Select_mini_jeux): Écran de sélection des mini-jeux.

            - character_buttons (list): Liste des boutons des personnages.

            - background_title_screen (pygame.Surface): Image de fond pour le menu principal.
        """

        # Initialisation des paramètres pygame
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.mixer.init()
        pygame.init()
        pygame.display.set_caption("MAYRO PARTY")
        pygame.display.set_icon(pygame.image.load(sep.join(["..", "data", "sprites", "icone.png"])))

        # Paramètres du jeu
        self.screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE|pygame.HWSURFACE|pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()
        self.fps = 120

        # Police d'écriture
        self.font = pygame.font.Font(sep.join(["..", "data", "fonts", "mario-party.ttf"]), 60)

        # État du jeu
        self.run = True

        # Liste des mini_jeux
        self.minijeux = {
            "archer_ival": archer_ival_client.MiniGame(self.screen, self.clock, self.fps),
            "hexagon_heat": hexagon_heat_client.MiniGame(self.screen, self.clock, self.fps),
            "pushy_penguins": pushy_penguins_client.MiniGame(self.screen, self.clock, self.fps),
            "speed_hockey": speed_hockey_client.MiniGame(self.screen, self.clock, self.fps),
            "trace_race": trace_race_client.MiniGame(self.screen, self.clock, self.fps)
        }
        self.minijeux_options = list(self.minijeux.keys())

        # Écran actuel / sélectionné
        self.current_screen = "title_screen"

        # Mode de jeu actuel
        self.mode = "solo"

        # Écrans du menu principal
        self.title_screen = Title_screen(self.font)
        self.select_mode = Select_mode(self.font)
        self.select_character = Select_character(self.font)
        self.select_ip = Select_ip(self.font)
        self.select_mini_jeux = Select_mini_jeux(self.font)

        # Boutons des personnages
        self.character_buttons = [self.select_character.get_mayro_button(),
                                  self.select_character.get_lugi_button(),
                                  self.select_character.get_wayro_button(),
                                  self.select_character.get_walugi_button()]

        # Sprites pour le menu principal
        self.background_title_screen = pygame.image.load(sep.join(["..", "data", "sprites", "main_menu", "wwmapflou.png"]))

        # Initialisation d'un son pour les choix incorrects
        self.son_incorrect = mixer.Sound(sep.join(["..", "data", "sounds", "main_menu", "incorrect.ogg"]))

        # Personnage choisit par le joueur
        self.perso = ""

        # Initialisation du réseau
        self.net = None

    def main(self):
        # On lance la musique du menu principal
        self.title_screen.play_music_title_screen()

        # Liste des personnages (on en aura besoin)
        liste_perso = ["mayro", "lugi", "wayro", "walugi"]

        # Initialisation de l'indice de boucle et du timer de 5s
        cooldown = 0.0

        while self.run:
            # Affichage du fond
            self.screen.blit(pygame.transform.scale(self.background_title_screen, self.screen.get_rect().size), (0, 0))

            # Si le serveur est actif
            if self.net != None:
                if len(self.minijeux_options) > 0:
                    infos_serveur = json.loads(self.net.send("infos_serveur"))
                    joueurs_persos = {joueur["perso"]: joueur["pseudo"] for joueur in infos_serveur["infos_joueurs"].values()}

            # Différents affichages selon le menu choisit
            if self.current_screen == "title_screen":
                self.title_screen.title_screen_affichage(self.screen)
            elif self.current_screen == "select_mode":
                self.select_mode.select_mode_affichage(self.screen)
            elif self.current_screen == "select_character":
                self.select_character.select_character_affichage(self.screen, joueurs_persos, self.mode, (infos_serveur["nb_joueurs_prets"], infos_serveur["nb_joueurs"]))

                etat = self.net.send("get_etat")
                if etat == "minigame_select":
                    # On passe sur l'écran des mini-jeux
                    self.current_screen = "select_mini_jeux"

                    # On active l'animation de la roulette
                    self.select_mini_jeux.set_roll(True)
                    self.current_screen = "select_mini_jeux"

                    # Initialisation du timer de 5s
                    cooldown = 5 + time.time()

            elif self.current_screen == "select_ip":
                self.select_ip.select_ip_affichage(self.screen)
            elif self.current_screen == "select_mini_jeux":
                self.select_mini_jeux.minijeu_affichage(self.screen, infos_serveur["infos_joueurs"], infos_serveur["classement"])

                # Parcours de tous les mini-jeux si il reste des mini-jeux
                if len(self.minijeux_options) > 0 and cooldown - time.time() <= 0:
                    self.title_screen.stop_music()

                    # Initialisation et lancement du mini-jeu
                    self.net.send("ready_for_next_state")
                    mini_jeu = self.minijeux[infos_serveur["minijeu_actuel"]]
                    mini_jeu.set_net(self.net)
                    mini_jeu.load()

                    # On relance la musique d'attente
                    self.title_screen.play_music_attente()

                    # On détecte si le joueur a quitté la fenêtre dans le mini-jeu
                    if mini_jeu.get_quit():
                        self.net.send("close")
                        pygame.quit()
                        quit()

                    # On supprime le mini-jeu des choix
                    self.minijeux_options.remove(infos_serveur["minijeu_actuel"])

                    # On relance l'animation de la roulette
                    self.select_mini_jeux.set_roll(True)

                    # Continuité de la boucle et réinitialisation du timer
                    cooldown = 5 + time.time()

                # Sinon s'il n'y a plus de mini-jeux, fin du jeu
                elif len(self.minijeux_options) == 0:
                    # On coupe la connexion avec le serveur
                    self.net.send("close")
                    self.net = None

                    # Affichage du sublime écran de fin de la démo
                    self.screen.blit(pygame.transform.scale(pygame.image.load(sep.join(["..", "data", "sprites", "main_menu", "end_demo.png"])), self.screen.get_rect().size), (0, 0))
                    pygame.display.flip()
                    pygame.time.wait(10000)

                    # Arrêt du programme
                    self.run = False

                # On arrête la roulette des mini-jeux 2s avant de lancer le-dit mini-jeu
                elif cooldown - time.time() <= 2 and self.select_mini_jeux.get_roll() == True:
                    # Arrêt du son de la roulette
                    son_roulette = self.select_mini_jeux.get_sound()
                    son_roulette.stop()

                    # On joue le son de sélection du mini-jeu
                    son_fin = mixer.Sound(sep.join(["..", "data", "sounds", "main_menu", "mini_jeu_selected.ogg"]))
                    son_fin.play()

                    # On arrête l'animation de la roulette
                    self.select_mini_jeux.set_roll(False)
                    self.select_mini_jeux.set_minijeu_affiche(infos_serveur["minijeu_actuel"])

                # Sinon on active l'animation de la roulette
                elif self.select_mini_jeux.get_roll() == True:
                    self.select_mini_jeux.minijeu_rouler(self.minijeux_options)


            for event in pygame.event.get():
                # Détection de la fermeture de fenêtre
                if event.type == pygame.QUIT:
                    self.run = False

                # Changement de taille de la fenêtre
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)

                # Détection des inputs du joueur
                elif event.type == pygame.MOUSEBUTTONUP:
                    # On note la position de la souris
                    pos = pygame.mouse.get_pos()

                    # On détecte les clicks avec le bouton de l'écran titre
                    if self.current_screen == "title_screen" and self.title_screen.get_text_button().is_clicked(pos, self.screen):
                        self.title_screen.play_music_attente()
                        self.current_screen = "select_mode"

                    # On détecte les clicks avec le bouton du mode de jeu
                    elif self.current_screen == "select_mode":
                        if self.select_mode.get_solo_button().is_clicked(pos, self.screen):
                            self.mode = "solo"
                            self.server = Server("localhost")
                            start_new_thread(self.server.run, ())
                            self.net = Network("localhost", "Joueur local")
                            self.current_screen = "select_character"

                        elif self.select_mode.get_multi_button().is_clicked(pos, self.screen):
                            self.mode = "multi"
                            self.current_screen = "select_ip"

                        elif self.select_mode.get_cancel_button().is_clicked(pos, self.screen):
                            self.title_screen.play_music_title_screen()
                            self.current_screen = "title_screen"

                    # On détecte les clicks avec le bouton du choix de personnage
                    elif self.current_screen == "select_character":
                        if self.select_character.get_start_button().is_clicked(pos, self.screen):
                            if self.perso == "":
                                # On joue un son pour indiquer au joueur que son choix n'est pas valide
                                self.son_incorrect.play()
                            else:
                                self.net.send("ready_for_next_state")

                        # On détecte pour chaque bouton de joueur s'il est en collision avec le curseur
                        for j in range(len(self.character_buttons)):
                            if self.character_buttons[j].is_clicked(pos, self.screen):
                                # Si le personnage est déjà choisit
                                if self.perso == liste_perso[j]:
                                    self.perso = ""
                                    self.net.send(json.dumps({"set_perso": ""}))

                                # L'indice j est le même pour le bouton que pour le nom du personnage
                                elif not liste_perso[j] in joueurs_persos.keys():
                                    self.perso = liste_perso[j]
                                    self.net.send(json.dumps({"set_perso": liste_perso[j]}))

                                # Ce joueur est déjà sélectionné
                                else:
                                    # On joue un son pour indiquer au joueur que son choix n'est pas valide
                                    self.son_incorrect.play()

                    # On détecte les clicks avec le bouton du choix de l'ip
                    elif self.current_screen == "select_ip":
                        if self.select_ip.get_cancel_button().is_clicked(pos, self.screen):
                            self.current_screen = "select_mode"
                        elif self.select_ip.get_join_button().is_clicked(pos, self.screen):
                            if len(self.select_ip.get_ip_field().get_text()) > 0 and len(self.select_ip.get_pseudo_field().get_text()) > 0:
                                adresse_serveur = self.select_ip.get_ip_field().get_text()
                                pseudo = self.select_ip.get_pseudo_field().get_text()
                            self.net = Network(adresse_serveur, pseudo)
                            self.current_screen = "select_character"

                        self.select_ip.get_ip_field().set_active(self.select_ip.get_ip_field().is_clicked(pos, self.screen))
                        self.select_ip.get_pseudo_field().set_active(self.select_ip.get_pseudo_field().is_clicked(pos, self.screen))

                # Détection des touches pour les champs d'écriture
                elif event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_RETURN:
                        self.select_ip.get_ip_field().set_active(False)
                        self.select_ip.get_pseudo_field().set_active(False)
                    elif event.key == pygame.K_BACKSPACE:
                        self.select_ip.get_ip_field().remove_character()
                        self.select_ip.get_pseudo_field().remove_character()
                    else:
                        self.select_ip.get_ip_field().add_character(event.unicode)
                        self.select_ip.get_pseudo_field().add_character(event.unicode)

            # Mise à jour de l'écran
            pygame.display.flip()

            # Limite des fps
            self.clock.tick(120)



# Classe de l'écran titre
class Title_screen():
    def __init__(self, font: pygame.font.Font) -> None: # type: ignore
        '''
        Cette classe sert à l'initialisation de l'écran titre et à son affichage.

        Attributs:
            self.font : police du bouton pour l'écran titre.
            self.logo : image du logo.
            self.text_button : bouton avec du texte.
            self.son_attente : musique de l'écran titre.
        
        Pré-conditions:
            La police doit être une instance de pygame.font.Font.
            Le logo chargé doit être une surface pygame valide.
            text_button doit être une instance de la classe Button.
            son_attente doit être une instance de pygame.mixer.Sound.

        Post-conditions:
            Si toutes les pré-conditions sont vérifiés, 
            alors le programme doit afficher le logo, le bouton, et la musique
        '''

        # Tests de types des différents paramètres
        assert type(font) == pygame.font.Font, "La police doit être une instance de pygame.font.Font"

        #Initialisation de la police pour l'écran titre
        self.font = font

        # Initialisation du logo (en chargeant l'image mayroparty.png), redimensionnement de l'image
        self.logo = pygame.image.load(sep.join(["..", "data", "sprites", "main_menu", "mayroparty.png"]))

        #Initialisation du bouton text_button
        self.text_button = Button(color=(13, 24, 65), x=205, y=500, width=850, height=120, text="CLIQUER ICI POUR COMMENCER", font=self.font)

        #Initialisation de la musique d'attente
        self.son_attente = mixer.Sound(sep.join(["..", "data", "musics", "main_menu", "waiting_music.ogg"]))


    # Getters

    def get_text_button(self) -> Button:
        return self.text_button

    def get_son_attente(self) -> mixer.Sound: # type: ignore
        return self.son_attente


    # Méthodes

    def stop_music(self) -> None:
        """
        Arrête la musique de l'écran titre.
        """

        mixer.music.stop()


    def play_music_title_screen(self) -> None:
        """
        Joue la musique de l'écran titre.
        """

        # On arrête la musique précédente
        mixer.music.stop()

        # On charge la musique de l'écran titre, et la répète en boucle
        mixer.music.load(sep.join(["..", "data", "musics", "main_menu", "title_screen_music.ogg"]))
        mixer.music.play(-1)


    def play_music_attente(self) -> None:
        """
        Joue la musique d'attente.
        """

        # On arrête la musique précédente
        mixer.music.stop()

        # On charge la musique d'attente, et la répète en boucle
        mixer.music.load(sep.join(["..", "data", "musics", "main_menu", "waiting_music.ogg"]))
        mixer.music.play(-1)


    def title_screen_affichage(self, screen: pygame.Surface) -> None: # type: ignore
        """
        Cette méthode permet d'afficher l'écran titre.

        Paramètres:
            - screen (pygame.Surface): écran de pygame.
        """

        # Test du type de screen
        assert type(screen) == pygame.Surface, "Erreur: Le paramètre screen donné n'est pas un écran de pygame."

        # Initialisation des facteurs pour la taille de l'écran
        screen_factor = ((screen.get_rect().size[0] / 1280), (screen.get_rect().size[1] / 720))

        # Positionnement du logo
        logo_Rect = self.logo.get_rect()
        logo_Rect.center = (round(640 * screen_factor[0]), round(250 * screen_factor[1]))
        self.logo = pygame.transform.scale(self.logo, (round(800 * screen_factor[0]), round(150 * screen_factor[1])))

        # Affichage sur la fenêtre du texte et du logo
        screen.blit(self.logo, logo_Rect)
        self.text_button.draw(screen)



# Classe de la sélection de mode
class Select_mode():
    def __init__(self, font: pygame.font.Font) -> None: # type: ignore
        '''
        Cette classe sert à déterminer quel mode choisir (1 ou 2 joueur(s)).

        Attributs : 
            self.font : police du texte
            mode_solo_sprite/mode_multi_sprite : image du mode 1 joueur/2 joueurs
            mode_1j_rec/mode_multi_rect : créer une réctangle qui entoure la surface mode_solo_sprite/mode_multi_sprite
            self.solo_button/self.multi_button : créer un bouton pour le mode 1 joueur/2 joueurs
            self.solo_text/self.multi_text/self.text_mode : position et contenu du texte avec la police d'écriture donné

        Pré-conditions:
            font doit être une instance de pygame.font.Font

        Post-conditions:
            Si toutes les pré-conditions sont vérifiés, 
            alors le programme doit afficher un ou des boutons pour le mode 1 joueur et 2 joueurs
        '''

        # Test du type de font
        assert type(font) == pygame.font.Font, "font doit être une instance de pygame.font.Font"

        #Initialisation de la police d'écriture
        self.font = font

        #Initialisation et positionnement de l'image pour le mode solo
        mode_solo_sprite = pygame.image.load(sep.join(["..", "data", "sprites", "main_menu", "solo.png"]))
        mode_solo_rect = mode_solo_sprite.get_rect()

        #Initialisation et positionnement de l'image pour le mode multijoueur
        mode_multi_sprite = pygame.image.load(sep.join(["..", "data", "sprites", "main_menu", "multijoueur.png"]))
        mode_multi_rect = mode_multi_sprite.get_rect()

        #Initialisation et positionnement de l'image pour le bouton annuler
        cancel_button_sprite = scale_image_by(pygame.image.load(sep.join(["..", "data", "sprites", "main_menu", "cancel_button.png"])), 2)
        cancel_button_rect = cancel_button_sprite.get_rect()

        #Création des boutons
        self.solo_button = Button(color=(0, 0, 0, 0), x=200, y=200, width=mode_solo_rect.w, height=mode_solo_rect.h, image=mode_solo_sprite)
        self.multi_button = Button(color=(0, 0, 0, 0), x=800, y=200, width=mode_multi_rect.w, height=mode_multi_rect.h, image=mode_multi_sprite)
        self.cancel_button = Button(color=(0, 0, 0, 0), x=10, y=10, width=cancel_button_rect.w, height=cancel_button_rect.h, image=cancel_button_sprite)


    # Getters

    def get_solo_button(self) -> Button:
        return self.solo_button

    def get_multi_button(self) -> Button:
        return self.multi_button

    def get_cancel_button(self) -> Button:
        return self.cancel_button


    # Méthodes

    def select_mode_affichage(self, screen: pygame.Surface) -> None: # type: ignore
        """
        Cette méthode affiche le menu de sélection du mode de jeu.

        Paramètres:
            - screen (pygame.Surface): écran de pygame.
        """

        # Test du type de screen
        assert type(screen) == pygame.Surface, "Erreur: Le paramètre screen donné n'est pas un écran de pygame."

        # Initialisation des facteurs pour la taille de l'écran
        screen_factor = ((screen.get_rect().size[0] / 1280), (screen.get_rect().size[1] / 720))

        #Affiche le bouton du joueur1 et du joueur2
        self.solo_button.draw(screen)
        self.multi_button.draw(screen)
        self.cancel_button.draw(screen)

        # Création de textes centrés à afficher
        solo_text = center_text('Solo',
                                   self.font,
                                   [round((200 + self.solo_button.get_width() // 2) * screen_factor[0]), round(580 * screen_factor[1])],
                                   [screen_factor[0], screen_factor[1]])

        multi_text = center_text('Multijoueur', 
                                   self.font,
                                   [round((800 + self.multi_button.get_width() // 2) * screen_factor[0]), round(580 * screen_factor[1])],
                                   [screen_factor[0], screen_factor[1]])

        text_mode = center_text('CHOISIR / CLIQUER SUR UN MODE DE JEU',
                                self.font,
                                [round(640 * screen_factor[0]), round(100 * screen_factor[1])],
                                [screen_factor[0], screen_factor[1]])

        #Affiche les différents textes (solo, multijoueur et selection du mode)
        screen.blit(solo_text[0], solo_text[1])
        screen.blit(multi_text[0], multi_text[1])
        screen.blit(text_mode[0], text_mode[1])



# Classe de la sélection de personnages
class Select_character():
    def __init__(self, font: pygame.font.Font) -> None: # type: ignore
        '''
        Cette classe sert à déterminer quel personnage est choisit.

        Attributs : 
            self.font : police du texte
            mayro/ligi/wayro/walugi_image : images des différents personnages
            self.mayro/lugi/wayro/walugi_button : créer un bouton pour chaque personnages
            self.mayro/lugi/wayro/walugi_text : position et contenu du texte avec la police d'écriture donné
            self.textes : un dictionnaire qui contient les noms des personnages
            self.text_char : texte de la séléction de personnage
            self.p1/p2 : images et redimentions des personnages de joueurs

        Pré-conditions:
            font doit être une instance de pygame.font.Font

        Post-conditions:
            Si toutes les pré-conditions sont vérifiés, 
            alors le programme doit afficher 4 boutons, et 5 textes
        '''

        # Test du type de font
        assert type(font) == pygame.font.Font, "font doit être une instance de pygame.font.Font"

        #Initialisation de la police d'écriture
        self.font = font

        #Initialisation et chargement des images des personnages
        mayro_image = pygame.image.load(sep.join(["..", "data", "sprites", "main_menu", "mayro_box.png"]))
        lugi_image = pygame.image.load(sep.join(["..", "data", "sprites", "main_menu", "lugi_box.png"]))
        wayro_image = pygame.image.load(sep.join(["..", "data", "sprites", "main_menu", "wayro_box.png"]))
        walugi_image = pygame.image.load(sep.join(["..", "data", "sprites", "main_menu", "walugi_box.png"]))

        #Initialisation et création du bouton des personnages
        self.mayro_button = Button(color=(0, 0, 0, 0), x=200, y=200, width=mayro_image.get_rect().w * 4, height=mayro_image.get_rect().h * 4, image=mayro_image)
        self.lugi_button = Button(color=(0, 0, 0, 0), x=450, y=200, width=lugi_image.get_rect().w * 4, height=lugi_image.get_rect().h * 4, image=lugi_image)
        self.wayro_button = Button(color=(0, 0, 0, 0), x=700, y=200, width=wayro_image.get_rect().w * 4, height=wayro_image.get_rect().h * 4, image=wayro_image)
        self.walugi_button = Button(color=(0, 0, 0, 0), x=950, y=200, width=walugi_image.get_rect().w * 4, height=walugi_image.get_rect().h * 4, image=walugi_image)

        # Création d'autres boutons
        self.start_button = Button(color=(13, 24, 65), x=205, y=500, width=850, height=120, text="COMMENCER", font=self.font)


    # Getters

    def get_mayro_button(self) -> Button:
        return self.mayro_button

    def get_lugi_button(self) -> Button:
        return self.lugi_button

    def get_wayro_button(self) -> Button:
        return self.wayro_button

    def get_walugi_button(self) -> Button:
        return self.walugi_button

    def get_start_button(self) -> Button:
        return self.start_button


    # Méthodes

    def select_character_affichage(self, screen: pygame.Surface, joueurs: dict, mode: str, nb_joueurs: tuple) -> None: # type: ignore
        """
        Cette méthode affiche le menu de sélection du mode de jeu.

        Paramètres:
            - screen (pygame.Surface): écran de pygame.
            - joueurs (dict): un dictionnaire qui stockent les joueurs et leur info.
            - mode (str): mode de jeu sélectionné par le client.
            - nb_joueurs (tuple): nombre de joueurs prêts et nombres de joueurs total.
        """

        # Test des type des paramètres
        assert type(screen) == pygame.Surface, "Erreur: Le paramètre screen donné n'est pas un écran de pygame."
        assert type(joueurs) == dict, "Erreur: Le paramètre joueurs donné n'est pas un dictionnaire."
        assert type(mode) == str, "Erreur: Le paramètre mode n'est pas une chaîne de caractères."
        assert type(nb_joueurs) == tuple, "Erreur: Le paramètre nb_joueurs n'est pas un tuple."

        # Initialisation des facteurs pour la taille de l'écran
        screen_factor = ((screen.get_rect().size[0] / 1280), (screen.get_rect().size[1] / 720))

        #Affiche les boutons
        self.mayro_button.draw(screen)
        self.lugi_button.draw(screen)
        self.wayro_button.draw(screen)
        self.walugi_button.draw(screen)

        if nb_joueurs[1] < 2: self.start_button.set_text("COMMENCER")
        else: self.start_button.set_text("COMMENCER (" + str(nb_joueurs[0]) +"/" + str(nb_joueurs[1]) + ")")

        self.start_button.draw(screen)

        #Initialisation du texte des boutons
        mayro_text = center_text(
            "Mayro",
            self.font,
            [round((200 + self.mayro_button.get_width() // 2) * screen_factor[0]), round(450 * screen_factor[1])],
            [screen_factor[0], screen_factor[1]]
        )

        lugi_text = center_text(
            "Lugi",
            self.font,
            [round((450 + self.lugi_button.get_width() // 2) * screen_factor[0]), round(450 * screen_factor[1])],
            [screen_factor[0], screen_factor[1]]
        )

        wayro_text = center_text(
            "Wayro",
            self.font,
            [round((700 + self.wayro_button.get_width() // 2) * screen_factor[0]), round(450 * screen_factor[1])],
            [screen_factor[0], screen_factor[1]]
        )

        walugi_text = center_text(
            "Walugi",
            self.font,
            [round((950 + self.walugi_button.get_width() // 2) * screen_factor[0]), round(450 * screen_factor[1])],
            [screen_factor[0], screen_factor[1]]
        )

        #Initialisation d'un dictionnaire contenant les boutons des personnages
        poses = {
            "mayro": (200 + self.mayro_button.get_width() // 2),
            "lugi": (450 + self.lugi_button.get_width() // 2),
            "wayro": (700 + self.wayro_button.get_width() // 2),
            "walugi": (950 + self.walugi_button.get_width() // 2)
        }

        #Centre le texte de sélection de personnages
        text_char = center_text('CHOISIR / CLIQUER SUR UN PERSONNAGE',
                                self.font,
                                [round(640 * screen_factor[0]), round(100 * screen_factor[1])],
                                [screen_factor[0], screen_factor[1]])

        for perso in joueurs.keys():
            if perso != "":
                text = center_text(
                    joueurs[perso],
                    self.font,
                    [round(poses[perso] * screen_factor[0]), round(180 * screen_factor[1])],
                    [0.5 * screen_factor[0], 0.5 * screen_factor[1]],
                    (0, 255, 0)
                )
                screen.blit(text[0], text[1])

        #Affiche les textes des personnages et du titre
        screen.blit(mayro_text[0], mayro_text[1])
        screen.blit(lugi_text[0], lugi_text[1])
        screen.blit(wayro_text[0], wayro_text[1])
        screen.blit(walugi_text[0], walugi_text[1])

        screen.blit(text_char[0], text_char[1])



# Classe de l'écran de sélection de l'ip du serveur
class Select_ip():
    def __init__(self, font: pygame.font.Font) -> None: # type: ignore
        '''
        Cette classe sert à l'initialisation de l'écran de sélection de l'ip du serveur et à son affichage.

        Attributs:
            self.font : police du bouton pour l'écran titre.
            self.join_button : bouton qui permet de rejoindre un serveur.

        Pré-conditions:
            La police doit être une instance de pygame.font.Font.
            join_button doit être une instance de la classe Button.

        Post-conditions:
            Si toutes les pré-conditions sont vérifiés, 
            alors le programme doit afficher le bouton
        '''

        # Tests de types des différents paramètres
        assert type(font) == pygame.font.Font, "La police doit être une instance de pygame.font.Font"

        #Initialisation de la police pour l'écran titre
        self.font = font

        #Initialisation et positionnement de l'image pour le bouton annuler
        cancel_button_sprite = scale_image_by(pygame.image.load(sep.join(["..", "data", "sprites", "main_menu", "cancel_button.png"])), 2)
        cancel_button_rect = cancel_button_sprite.get_rect()

        # Création des boutons et des champs d'écriture
        self.join_button = Button(color=(13, 24, 65), x=205, y=500, width=850, height=120, text="REJOINDRE LE SERVEUR", font=self.font)
        self.cancel_button = Button(color=(0, 0, 0, 0), x=10, y=10, width=cancel_button_rect.w, height=cancel_button_rect.h, image=cancel_button_sprite)
        self.ip_field = InputField(x=205, y=100, width=850, height=120, text="(adresse ip du serveur...)", font=self.font)
        self.pseudo_field = InputField(x=205, y=300, width=850, height=120, text="(pseudo...)", font=self.font)


    # Getters

    def get_join_button(self) -> Button:
        return self.join_button

    def get_cancel_button(self) -> Button:
        return self.cancel_button

    def get_ip_field(self) -> InputField:
        return self.ip_field

    def get_pseudo_field(self) -> InputField:
        return self.pseudo_field


    # Méthodes

    def select_ip_affichage(self, screen: pygame.Surface) -> None: # type: ignore
        """
        Cette méthode permet d'afficher l'écran de sélection de l'ip du serveur.

        Paramètres:
            - screen (pygame.Surface): écran de pygame.
        """

        # Test du type de screen
        assert type(screen) == pygame.Surface, "Erreur: Le paramètre screen donné n'est pas un écran de pygame."

        # Affichage des bouton/champs d'écriture
        self.join_button.draw(screen)
        self.cancel_button.draw(screen)
        self.ip_field.draw(screen)
        self.pseudo_field.draw(screen)



# Classe de la sélection des mini-jeux
class Select_mini_jeux():

    # ------/ Constructeur \------

    def __init__(self, font: pygame.font.Font) -> None: # type: ignore
        """
        Constructeur de la classe Select_mini_jeux.

        Attributs à définir:
            - font (pygame.font.Font): Police d'écriture du jeu.

        Attributs internes:
            - position (tuple): Position de l'image du mini-jeu.
            - roll (bool): Indique si la roulette des mini-jeux est active ou non.
            - minijeu_actuel (str): Mini-jeu sélectionné.

            - sound (mixer.Sound): Son de la roulette. 
            - cooldown (float): délai entre chaque son.

            - text_classement (list): Texte du classement.
            - piece (pygame.Surface): Image de pièce.
            - p1 (pygame.Surface): Image du texte du joueur 1.
            - p2 (pygame.Surface): Image du texte du joueur 2.
        """

        # Tests de types des différents paramètres
        assert type(font) == pygame.font.Font, "La police doit être une instance de pygame.font.Font"

        #Initialisation de la police d'écriture
        self.font = font

        # Mini-jeu à afficher (archer_ival car c'est le premier)
        self.minijeu_affiche = "archer_ival"

        # État de la roulette
        self.roll = False

        # Paramètres du son
        self.sound = mixer.Sound(sep.join(["..", "data", "sounds", "main_menu", "mini_jeu_roll.ogg"]))
        self.cooldown = 0.0


    # ------/ Getters \------

    def get_roll(self) -> bool:
        return self.roll
    
    def get_sound(self) -> mixer.Sound: # type: ignore
        return self.sound


    # ------/ Setter \------

    def set_roll(self, changer_valeur) -> None:
        self.roll = changer_valeur

    def set_minijeu_affiche(self, new_mini_jeu_affiche) -> None:
        self.minijeu_affiche = new_mini_jeu_affiche


    # ------/ Méthodes \------

    def minijeu_affichage(self, screen: pygame.Surface, joueurs: dict, classement: dict) -> None: # type: ignore
        """
        Cette méthode permet d'afficher le menu qui affiche la roulette des mini-jeux ainsi que le classment
        des joueurs.

        Paramètres:
            - screen (pygame.Surface): écran de pygame.
            - joueurs (dict): dictionnaire qui contient toutes les infos des joueurs.
            - classement (dict): dictionnaire de la quantité de pièces de chaque joueur.
        """

        # Test du type des paramètres
        assert type(screen) == pygame.Surface, "Erreur: Le paramètre screen donné n'est pas un écran de pygame."
        assert type(joueurs) == dict, "Erreur: Le paramètre joueurs donné n'est pas un dictionnaire."
        assert type(classement) == dict, "Erreur: Le paramètre classement donné n'est pas un dictionnaire."

        # Initialisation des facteurs pour la taille de l'écran
        screen_factor = ((screen.get_rect().size[0] / 1280), (screen.get_rect().size[1] / 720))

        # Affiche du mini-jeu en fonction de la valeur de minijeu_actuel
        minijeux = pygame.image.load(sep.join(["..", "data", "sprites", "main_menu", self.minijeu_affiche + ".png"]))
        minijeux = pygame.transform.scale(minijeux, (round(minijeux.get_rect().w // 2 * screen_factor[0]), round(minijeux.get_rect().h // 2 * screen_factor[1])))
        minijeux_position = (round(60 * screen_factor[0]), round(200 * screen_factor[1]))
        screen.blit(minijeux, minijeux_position)

        # Textes et images à afficher
        text_classement = center_text("Classement",
                                      self.font,
                                      [round(640 * screen_factor[0]), round(50 * screen_factor[0])],
                                      [screen_factor[0], screen_factor[1]])

        piece = scale_image_by(pygame.image.load(sep.join(["..", "data", "sprites", "main_menu", "piece.png"])), (4 * screen_factor[0], 4 * screen_factor[1]))

        # Affichage du texte du classmenet
        screen.blit(text_classement[0], text_classement[1])

        # Affichage des images de pièces
        screen.blit(piece, (round(1050 * screen_factor[0]), round(150 * screen_factor[1])))
        screen.blit(piece, (round(1050 * screen_factor[0]), round(300 * screen_factor[1])))
        screen.blit(piece, (round(1050 * screen_factor[0]), round(450 * screen_factor[1])))
        screen.blit(piece, (round(1050 * screen_factor[0]), round(600 * screen_factor[1])))
    
        # Position y du texte du 1er joueur
        sprite_y = 100

        for joueur in joueurs.keys():
            # Initialisation du compteur de pièces
            piece_text = self.font.render("x" + str(joueurs[joueur]["pieces"]), True, (255, 255, 255))
            piece_text = pygame.transform.scale(piece_text, (round(piece_text.get_rect().w * screen_factor[0]), round(piece_text.get_rect().h * screen_factor[1])))

            # Affichage des personnages et de leur position dans le classement
            screen.blit(scale_image_by(pygame.image.load(sep.join(["..", "data", "sprites", "main_menu", joueurs[joueur]["perso"] + "_box.png"])), (3 * screen_factor[0], 3 * screen_factor[1])), (round(800 * screen_factor[0]), round(sprite_y * screen_factor[1])))
            screen.blit(scale_image_by(pygame.image.load(sep.join(["..", "data", "sprites", "main_menu", "place_" + str(classement[joueur]) + ".png"])), (3 * screen_factor[0], 3 * screen_factor[1])), (round(1150 * screen_factor[0]), round((sprite_y + 50) * screen_factor[1])))

            # Affichage du compteur de pièces
            screen.blit(piece_text, (round(930 * screen_factor[0]), round((sprite_y + 50) * screen_factor[1])))

            # On déplace le prochain texte 150 pixels plus loin
            sprite_y += 150


    def minijeu_rouler(self, mini_jeux: list) -> None:
        """
        Cette méthode gère le roulement de la roulette des mini-jeux.

        Paramètres:
            - mini_jeux (list): liste qui contient les noms des mini-jeux.
        """

        # Test du type de mini_jeux
        assert type(mini_jeux) == list, "Erreur: Le paramètre mini_jeux donné n'est pas une liste."

        # Toutes les 0.1s
        if self.cooldown - time.time() <= 0:
            # On joue le son
            self.sound.play()

            # On choisit un mini-jeu aléatoire à afficher
            self.minijeu_affiche = random.choice(mini_jeux)

            # On applique le délai
            self.cooldown = 0.1 + time.time()


# Initialisation et lancement du mini-jeu
game = Game()
game.main()

# Fin du programme
pygame.quit()