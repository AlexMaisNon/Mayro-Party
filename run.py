# Fait par Antoine et Alexandre

# ------/ Importations des bibliothèques \------

import pygame, random
import pygame.freetype
from pygame import mixer
import time
from os import sep

import pygame.ftfont

# ------/ Importations des mini-jeux \------

import archer_ival
import hexagon_heat
import speed_hockey
import trace_race
import pushy_penguins


# ------/ Fonctions utiliatires \------

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

def center_text(text: str, font: pygame.font.Font, position: "list | tuple", echelle: "list | tuple | None" = None): # type: ignore
    """
    Cette fonction permet de créer un texte automatiquement centré sur la positon demandée.

    Paramètres:
        - text (str): une chaîne de caractères représentant le texte à créer.
        - font (pygame.font.Font): police d'écriture sur laquelle écrire le texte.
        - position (list ou tuple): position du texte à placer.

    Renvois:
        - list: une liste représentant le texte créé et son rectangle (sa position).

    Pré-conditions:
        - text ne doit pas être une chaîne de caractères vide.

    Post-conditions:
        - La fonction doit renvoyer dans une liste le texte centré ainsi que sa position, créé à partir
        de la police, de la chaîne de caractère et de la position souhaitée.
    """

    # Test des types de variables
    assert type(text) == str, "Erreur: le paramètre text donné n'est pas une chaîne de caractères."
    assert type(font) == pygame.font.Font, "Erreur: le paramètre text donné n'est pas une police d'écriture de pygame."
    assert type(position) == list or type(position) == tuple, "Erreur: le paramètre position donné n'est pas une liste."
    assert type(echelle) == list or type(echelle) == tuple or echelle == None, "Erreur: le paramètre echelle donné n'est pas une liste."

    # Test de la longueur de text
    assert len(text) > 0, "Erreur: Le paramètre text est une chaîne de caractères vide."

    # On crée une surface représentant le texte
    text_surface = font.render(text, True, (255, 255, 255))
    if echelle != None:
        text_surface = pygame.transform.scale(text_surface, (round(text_surface.get_rect().w * echelle[0]), round(text_surface.get_rect().h * echelle[1])))

    # On change le centre de son rectangle, le centrant à la position demandée
    text_rect = text_surface.get_rect()
    text_rect.center = position

    # On renvoie le tout dans une liste
    return [text_surface, text_rect]


# ------/ Classes \------

# Classe du joueur
class Character():
    def __init__(self, perso: str, id: int = 0, ia: bool = True) -> None:
        """
        Constructeur de la classe Joueur.

        Attributs à définir:
            - perso (str): Personnage choisit par le joueur.
            - id (int): id du joueur qui indique sa position dans l'ordre de jeu.
            - ia (bool): Indique si le joueur est une ia ou un joueur lambda.

        Attributs internes:
            - pieces (int): Nombre de pièces du joueur.
        """

        # Tests du type des paramètres donnés
        assert type(perso) == str, "Erreur: Le 1er paramètre (perso) est censé être une chaîne de caractères."
        assert type(id) == int, "Erreur: Le 2ème paramètre (id) est censé être un entier."
        assert type(ia) == bool, "Erreur: Le 3ème paramètre (ia) est censé être un booléen."

        # Initialisation des paramètres du personnage
        self.perso = perso
        self.ia = ia
        self.id = id            # un id de 0 indique qu'il n'a pas encore été défini
        self.pieces = 0


    # ------/ Getters \------

    def get_id(self) -> int:
        return self.id

    def get_ia(self) -> bool:
        return self.ia

    def get_pieces(self) -> int:
        return self.pieces


    # ------/ Setters \------

    def set_id(self, new_id) -> None:
        self.id = new_id

    def set_ia(self, new_ia: int) -> None:
        self.ia = new_ia

    def set_pieces(self, amount: int) -> None:
        self.pieces = amount



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

        # Paramètres du jeu
        self.screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE|pygame.HWSURFACE|pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()
        self.fps = 120

        # Police d'écriture
        self.font = pygame.font.Font("assets" + sep + "fonts" + sep + "mario-party.ttf", 60)

        # État du jeu
        self.run = True

        # Initialisation des joueurs et de leur instance
        self.joueurs = {
            "mayro": Character('mayro'),
            "lugi": Character('lugi'),
            "wayro": Character('wayro'),
            "walugi": Character('walugi')
        }

        # Liste des mini_jeux
        self.mini_jeux = {"archer_ival": archer_ival.MiniGame(self.screen, self.clock, self.fps),
                          "hexagon_heat": hexagon_heat.MiniGame(self.screen, self.clock, self.fps),
                          "speed_hockey": speed_hockey.MiniGame(self.screen, self.clock, self.fps),
                          "trace_race": trace_race.MiniGame(self.screen, self.clock, self.fps),
                          "pushy_penguins": pushy_penguins.MiniGame(self.screen, self.clock, self.fps)}

        # Initialisation du classement (tous les joueurs partent 1er)
        self.classement = {joueur: 1 for joueur in self.joueurs.keys()}

        # Écran actuel / sélectionné
        self.current_screen = "title_screen"

        # Écrans du menu principal
        self.title_screen = Title_screen(self.font)
        self.select_mode = Select_mode(self.font)
        self.select_character = Select_character(self.font)
        self.select_mini_jeux = Select_mini_jeux(self.font)

        # Boutons des personnages
        self.character_buttons = [self.select_character.mayro_button,
                                  self.select_character.lugi_button,
                                  self.select_character.wayro_button,
                                  self.select_character.walugi_button]

        # Sprites pour le menu principal
        self.background_title_screen = pygame.image.load("assets" + sep + "sprites" + sep + "main_menu" + sep + "wwmapflou.png")


    def main(self):
        # On lance la musique du menu principal
        self.title_screen.play_music_title_screen()

        # Initialisation du mode et du joueur actuels
        joueur_actuel = 1
        mode = 0

        # Liste des personnages (on en aura besoin)
        liste_perso = ["mayro", "lugi", "wayro", "walugi"]

        # Initialisation d'un nouveau format de dictionnaire pour les personnages
        # (cross-compatibilité avec les scripts des mini-jeux)
        joueurs_format = {}

        # Liste des différents gains en fonction de la place
        score_to_pieces = [10, 5, 2, 0]

        # Initialisation de l'indice de boucle et du timer de 5s
        cooldown = 0.0

        while self.run:
            # Affichage du fond
            self.screen.blit(pygame.transform.scale(self.background_title_screen, self.screen.get_rect().size), (0, 0))

            # Différents affichages selon le menu choisit
            if self.current_screen == "title_screen":
                self.title_screen.title_screen_affichage(self.screen)
            elif self.current_screen == "select_mode":
                self.select_mode.select_mode_affichage(self.screen)
            elif self.current_screen == "select_character":
                self.select_character.select_character_affichage(self.screen, self.joueurs)
            elif self.current_screen == "select_mini_jeux":
                self.select_mini_jeux.minijeu_affichage(self.screen, self.joueurs, self.classement)

                # Parcours de tous les mini-jeux si il reste des mini-jeux
                if len(self.mini_jeux.keys()) > 0 and cooldown - time.time() <= 0:
                    self.title_screen.stop_music()

                    # Initialisation et lancement du mini-jeu
                    mini_jeu = self.mini_jeux[self.select_mini_jeux.get_minijeu_actuel()]
                    mini_jeu.load(joueurs_format)

                    # On relance la musique d'attente
                    self.title_screen.play_music_attente()

                    # On détecte si le joueur a quitté la fenêtre dans le mini-jeu
                    if mini_jeu.get_quit():
                        pygame.quit()
                        quit()

                    for joueur in self.joueurs.keys():
                        # On récupère le nombre de pièces en fonction du classement du joueur dans le mini-jeu
                        nb_pieces = score_to_pieces[mini_jeu.get_classement()[joueur] - 1]

                        # Ajout des pièces dans la classe du joueur
                        self.joueurs[joueur].set_pieces(self.joueurs[joueur].get_pieces() + nb_pieces)

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

                    # On supprime le mini-jeu déjà joué du dictionnaire
                    del self.mini_jeux[self.select_mini_jeux.get_minijeu_actuel()]

                    # On relance l'animation de la roulette
                    self.select_mini_jeux.set_roll(True)

                    # Continuité de la boucle et réinitialisation du timer
                    cooldown = 5 + time.time()

                # Sinon s'il n'y a plus de mini-jeux, fin du jeu
                elif len(self.mini_jeux.keys()) == 0:
                    # Affichage du sublime écran de fin de la démo
                    self.screen.blit(pygame.transform.scale(pygame.image.load("assets" + sep + "sprites" + sep + "main_menu" + sep + "end_demo.png"), self.screen.get_rect().size), (0, 0))
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
                    son_fin = mixer.Sound("assets" + sep + "sounds" + sep + "main_menu" + sep + "mini_jeu_selected.ogg")
                    son_fin.play()

                    # On arrête l'animation de la roulette
                    self.select_mini_jeux.set_roll(False)

                # Sinon on active l'animation de la roulette
                elif self.select_mini_jeux.get_roll() == True:
                    self.select_mini_jeux.minijeu_rouler(self.mini_jeux)


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
                        if self.select_mode.joueur1_button.is_clicked(pos, self.screen):
                            # mode = 0 si mode 1 Joueur sélectionné
                            mode = 0
                            self.current_screen = "select_character"

                        elif self.select_mode.joueur2_button.is_clicked(pos, self.screen):
                            # mode = 1 si mode 2 Joueurs sélectionné
                            mode = 1
                            self.current_screen = "select_character"

                    # On détecte les clicks avec le bouton du choix de personnage
                    elif self.current_screen == "select_character":
                        # On détecte pour chaque bouton de joueur s'il est en collision avec le curseur
                        for j in range(len(self.character_buttons)):

                            # L'indice j est le même pour le bouton que pour le nom du personnage
                            if self.character_buttons[j].is_clicked(pos, self.screen) and self.joueurs[liste_perso[j]].get_id() == 0:
                                # id = 1 (joueur 1) | id = 2 (joueur 2) | id = 0 (non défini)
                                self.joueurs[liste_perso[j]].set_id(joueur_actuel)
                                self.joueurs[liste_perso[j]].set_ia(False)

                                joueur_actuel += 1

                                # On continue vers le menu suivant si le mode est 1 Joueur où si le 2ème joueur est déjà choisit
                                if mode == 0 or joueur_actuel > 2:
                                    # On active l'animation de la roulette
                                    self.select_mini_jeux.set_roll(True)
                                    self.current_screen = "select_mini_jeux"

                                    # On modifie le format du dictionnaire des joueurs pour qu'il fonctionne avec le code des mini-jeux
                                    for joueur in self.joueurs.keys():
                                        if self.joueurs[joueur].get_id() == 0:
                                            self.joueurs[joueur].set_id(joueur_actuel)
                                            joueur_actuel += 1

                                        joueurs_format[joueur] = (self.joueurs[joueur].get_id(), self.joueurs[joueur].get_ia())

                                    # Initialisation du timer de 5s
                                    cooldown = 5 + time.time()

                            # Ce joueur est déjà sélectionné
                            elif self.character_buttons[j].is_clicked(pos, self.screen) and self.joueurs[liste_perso[j]].get_id() > 0:
                                # On joue un son pour indiquer au joueur que son choix n'est pas valide
                                son_incorrect = mixer.Sound("assets" + sep + "sounds" + sep + "main_menu" + sep + "incorrect.ogg")
                                son_incorrect.play()

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
        self.logo = pygame.image.load("assets" + sep + "sprites" + sep + "main_menu" + sep + "mayroparty.png")

        #Initialisation du bouton text_button
        self.text_button = Button(color=(13, 24, 65), x=205, y=500, width=850, height=120, text="CLIQUER ICI POUR COMMENCER", font=self.font)

        #Initialisation de la musique d'attente
        self.son_attente = mixer.Sound("assets" + sep + "musics" + sep + "main_menu" + sep + "waiting_music.ogg")


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
        mixer.music.load("assets" + sep + "musics" + sep + "main_menu" + sep + "title_screen_music.ogg")
        mixer.music.play(-1)


    def play_music_attente(self) -> None:
        """
        Joue la musique d'attente.
        """

        # On arrête la musique précédente
        mixer.music.stop()

        # On charge la musique d'attente, et la répète en boucle
        mixer.music.load("assets" + sep + "musics" + sep + "main_menu" + sep + "waiting_music.ogg")
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

        # Initialisation et positionnement du texte de l'édition (celui en-dessous du titre)
        edition_text = center_text("(sans plateau édition)",
                                   self.font,
                                   [round(640 * screen_factor[0]), round(340 * screen_factor[1])],
                                   [screen_factor[0], screen_factor[1]])

        # Positionnement du logo
        logo_Rect = self.logo.get_rect()
        logo_Rect.center = (round(640 * screen_factor[0]), round(250 * screen_factor[1]))
        self.logo = pygame.transform.scale(self.logo, (round(800 * screen_factor[0]), round(150 * screen_factor[1])))

        # Affichage sur la fenêtre du texte et du logo
        screen.blit(edition_text[0], edition_text[1])
        screen.blit(self.logo, logo_Rect)
        self.text_button.draw(screen)



# Classe de la sélection de mode
class Select_mode():
    def __init__(self, font: pygame.font.Font) -> None: # type: ignore
        '''
        Cette classe sert à déterminer quel mode choisir (1 ou 2 joueur(s)).

        Attributs : 
            self.font : police du texte
            mode_1j_sprite/mode_2j_sprite : image du mode 1 joueur/2 joueurs
            mode_1j_rec/mode_2j_rect : créer une réctangle qui entoure la surface mode_1j_sprite/mode_2j_sprite
            self.joueur1_button/self.joueur2_button : créer un bouton pour le mode 1 joueur/2 joueurs
            self.joueur1_text/self.joueur2_text/self.text_mode : position et contenu du texte avec la police d'écriture donné

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

        #Initialisation et positionnement de l'image pour le mode 1 joueur
        mode_1j_sprite = pygame.image.load("assets" + sep + "sprites" + sep + "main_menu" + sep + "1_joueur.png")
        mode_1j_rect = mode_1j_sprite.get_rect()

        #Initialisation et positionnement de l'image pour le mode 2 joueurs
        mode_2j_sprite = pygame.image.load("assets" + sep + "sprites" + sep + "main_menu" + sep + "2_joueurs.png")
        mode_2j_rect = mode_2j_sprite.get_rect()

        #Création des boutons 1 Joueur et 2 Joueurs
        self.joueur1_button = Button(color=(0, 0, 0, 0), x=200, y=200, width=mode_1j_rect.w, height=mode_1j_rect.h, image=mode_1j_sprite)
        self.joueur2_button = Button(color=(0, 0, 0, 0), x=800, y=200, width=mode_1j_rect.w, height=mode_2j_rect.h, image=mode_2j_sprite)


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
        self.joueur1_button.draw(screen)
        self.joueur2_button.draw(screen)

        # Création de textes centrés à afficher
        joueur1_text = center_text('1 Joueur',
                                   self.font,
                                   [round((200 + self.joueur1_button.get_width() // 2) * screen_factor[0]), round(580 * screen_factor[1])],
                                   [screen_factor[0], screen_factor[1]])

        joueur2_text = center_text('2 Joueurs', 
                                   self.font,
                                   [round((800 + self.joueur2_button.get_width() // 2) * screen_factor[0]), round(580 * screen_factor[1])],
                                   [screen_factor[0], screen_factor[1]])

        text_mode = center_text('CHOISIR / CLIQUER SUR UN MODE DE JEU',
                                self.font,
                                [round(640 * screen_factor[0]), round(100 * screen_factor[1])],
                                [screen_factor[0], screen_factor[1]])

        #Affiche les différents textes (joueur1 et 2 et selection du mode)
        screen.blit(joueur1_text[0], joueur1_text[1])
        screen.blit(joueur2_text[0], joueur2_text[1])
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
        mayro_image = pygame.image.load("assets" + sep + "sprites" + sep + "main_menu" + sep + "mayro_box.png")
        lugi_image = pygame.image.load("assets" + sep + "sprites" + sep + "main_menu" + sep + "lugi_box.png")
        wayro_image = pygame.image.load("assets" + sep + "sprites" + sep + "main_menu" + sep + "wayro_box.png")
        walugi_image = pygame.image.load("assets" + sep + "sprites" + sep + "main_menu" + sep + "walugi_box.png")

        #Initialisation et création du bouton de mayro
        self.mayro_button = Button(color=(0, 0, 0, 0), x=200, y=250, width=mayro_image.get_rect().w * 4, height=mayro_image.get_rect().h * 4, image=mayro_image)

        #Initialisation et création du bouton de lugi
        self.lugi_button = Button(color=(0, 0, 0, 0), x=450, y=250, width=lugi_image.get_rect().w * 4, height=lugi_image.get_rect().h * 4, image=lugi_image)

        #Initialisation et création du bouton de wayro
        self.wayro_button = Button(color=(0, 0, 0, 0), x=700, y=250, width=wayro_image.get_rect().w * 4, height=wayro_image.get_rect().h * 4, image=wayro_image)

        #Initialisation et création du bouton de walugi
        self.walugi_button = Button(color=(0, 0, 0, 0), x=950, y=250, width=walugi_image.get_rect().w * 4, height=walugi_image.get_rect().h * 4, image=walugi_image)


    # Méthodes

    def select_character_affichage(self, screen: pygame.Surface, joueurs: dict) -> None: # type: ignore
        """
        Cette méthode affiche le menu de sélection du mode de jeu.

        Paramètres:
            - screen (pygame.Surface): écran de pygame.
            - joueurs (dict): un dictionnaire qui stockent les joueurs et leur info.
        """

        # Test des type des paramètres
        assert type(screen) == pygame.Surface, "Erreur: Le paramètre screen donné n'est pas un écran de pygame."
        assert type(joueurs) == dict, "Erreur: Le paramètre joueurs donné n'est pas un dictionnaire."

        # Initialisation des facteurs pour la taille de l'écran
        screen_factor = ((screen.get_rect().size[0] / 1280), (screen.get_rect().size[1] / 720))

        #Affiche les boutons des personnages
        self.mayro_button.draw(screen)
        self.lugi_button.draw(screen)
        self.wayro_button.draw(screen)
        self.walugi_button.draw(screen)

        #Initialisation du texte des boutons
        mayro_text = center_text("Mayro",
                                      self.font,
                                      [round((200 + self.mayro_button.get_width() // 2) * screen_factor[0]), round(500 * screen_factor[1])],
                                      [screen_factor[0], screen_factor[1]])

        lugi_text = center_text("Lugi",
                                     self.font,
                                     [round((450 + self.lugi_button.get_width() // 2) * screen_factor[0]), round(500 * screen_factor[1])],
                                     [screen_factor[0], screen_factor[1]])

        wayro_text = center_text("Wayro",
                                      self.font,
                                      [round((700 + self.wayro_button.get_width() // 2) * screen_factor[0]), round(500 * screen_factor[1])],
                                      [screen_factor[0], screen_factor[1]])

        walugi_text = center_text("Walugi",
                                       self.font,
                                       [round((950 + self.walugi_button.get_width() // 2) * screen_factor[0]), round(500 * screen_factor[1])],
                                       [screen_factor[0], screen_factor[1]])

        #Initialisation d'un dictionnaire contenant le nom des personnages
        texts = {"mayro": mayro_text, "lugi": lugi_text, "wayro": wayro_text, "walugi": walugi_text}

        #Centre le texte de séléction de personnages
        text_char = center_text('CHOISIR / CLIQUER SUR UN PERSONNAGE',
                                self.font,
                                [round(640 * screen_factor[0]), round(100 * screen_factor[1])],
                                [screen_factor[0], screen_factor[1]])

        #Initialise les textes des joueurs 1 et 2, et les redimensionne
        p1 = scale_image_by(pygame.image.load("assets" + sep + "sprites" + sep + "main_menu" + sep + "p1.png"), (4 * screen_factor[0], 4 * screen_factor[1]))
        p2 = scale_image_by(pygame.image.load("assets" + sep + "sprites" + sep + "main_menu" + sep + "p2.png"), (4 * screen_factor[0], 4 * screen_factor[1]))

        # Parcoure les toutes les clés du dictionnaire, et affiche l'image du texte du joueur1 et ou 2 en fonction de
        # l'identifiant du joueur, puis affiche le texte associé au personnage 
        for nom in texts.keys():
            if joueurs[nom].get_id() == 1 and not joueurs[nom].get_ia():
                screen.blit(p1, [texts[nom][1][0], texts[nom][1][1] - round(250 * screen_factor[1])])
            elif joueurs[nom].get_id() == 2 and not joueurs[nom].get_ia():
                screen.blit(p2, [texts[nom][1][0], texts[nom][1][1] - round(250 * screen_factor[1])])
            screen.blit(texts[nom][0], texts[nom][1])

        #Affiche les textes des personnages et du titre
        screen.blit(mayro_text[0], mayro_text[1])
        screen.blit(lugi_text[0], lugi_text[1])
        screen.blit(wayro_text[0], wayro_text[1])
        screen.blit(walugi_text[0], walugi_text[1])

        screen.blit(text_char[0], text_char[1])



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

        # Paramètres pour les mini-jeux
        self.minijeu_actuel = "archer_ival"

        # État de la roulette
        self.roll = False

        # Paramètres du son
        self.sound = mixer.Sound("assets" + sep + "sounds" + sep + "main_menu" + sep + "mini_jeu_roll.ogg")
        self.cooldown = 0.0


    # ------/ Getters \------

    def get_roll(self) -> bool:
        return self.roll

    def get_minijeu_actuel(self) -> str:
        return self.minijeu_actuel
    
    def get_sound(self) -> mixer.Sound: # type: ignore
        return self.sound


    # ------/ Setter \------

    def set_roll(self, changer_valeur) -> None:
        self.roll = changer_valeur


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
        minijeux = pygame.image.load("assets" + sep + "sprites" + sep + "main_menu" + sep + "" + self.minijeu_actuel + ".png")
        minijeux = pygame.transform.scale(minijeux, (round(minijeux.get_rect().w // 2 * screen_factor[0]), round(minijeux.get_rect().h // 2 * screen_factor[1])))
        minijeux_position = (round(60 * screen_factor[0]), round(200 * screen_factor[1]))
        screen.blit(minijeux, minijeux_position)

        # Textes et images à afficher
        text_classement = center_text("Classement",
                                      self.font,
                                      [round(640 * screen_factor[0]), round(50 * screen_factor[0])],
                                      [screen_factor[0], screen_factor[1]])

        piece = scale_image_by(pygame.image.load("assets" + sep + "sprites" + sep + "main_menu" + sep + "piece.png"), (4 * screen_factor[0], 4 * screen_factor[1]))
        p1 = scale_image_by(pygame.image.load("assets" + sep + "sprites" + sep + "main_menu" + sep + "p1.png"), (4 * screen_factor[0], 4 * screen_factor[1]))
        p2 = scale_image_by(pygame.image.load("assets" + sep + "sprites" + sep + "main_menu" + sep + "p2.png"), (4 * screen_factor[0], 4 * screen_factor[1]))

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
            piece_text = self.font.render("x" + str(joueurs[joueur].get_pieces()), True, (255, 255, 255))
            piece_text = pygame.transform.scale(piece_text, (round(piece_text.get_rect().w * screen_factor[0]), round(piece_text.get_rect().h * screen_factor[1])))

            # Affichage du texte des joueurs 1 et 2 (s'il existe)
            if joueurs[joueur].get_id() == 1 and not joueurs[joueur].get_ia():
                screen.blit(p1, (round(720 * screen_factor[0]), round((sprite_y + 50) * screen_factor[1])))
            elif joueurs[joueur].get_id() == 2 and not joueurs[joueur].get_ia():
                screen.blit(p2, (round(720 * screen_factor[0]), round((sprite_y + 50) * screen_factor[1])))

            # Affichage des personnages et de leur position dans le classement
            screen.blit(scale_image_by(pygame.image.load("assets" + sep + "sprites" + sep + "main_menu" + sep + "" + joueur + "_box.png"), (3 * screen_factor[0], 3 * screen_factor[1])), (round(800 * screen_factor[0]), round(sprite_y * screen_factor[1])))
            screen.blit(scale_image_by(pygame.image.load("assets" + sep + "sprites" + sep + "main_menu" + sep + "place_" + str(classement[joueur]) + ".png"), (3 * screen_factor[0], 3 * screen_factor[1])), (round(1150 * screen_factor[0]), round((sprite_y + 50) * screen_factor[1])))

            # Affichage du compteur de pièces
            screen.blit(piece_text, (round(930 * screen_factor[0]), round((sprite_y + 50) * screen_factor[1])))

            # On déplace le prochain texte 150 pixels plus loin
            sprite_y += 150


    def minijeu_rouler(self, mini_jeux: dict) -> None:
        """
        Cette méthode gère le roulement de la roulette des mini-jeux.

        Paramètres:
            - mini_jeux (dict): dictionnaire qui contient les noms et les mini-jeux.
        """

        # Test du type de mini_jeux
        assert type(mini_jeux) == dict, "Erreur: Le paramètre mini_jeux donné n'est pas un dictionnaire."

        # Toutes les 0.1s
        if self.cooldown - time.time() <= 0:
            # On joue le son
            self.sound.play()

            # On définit le jeu actuellement choisit
            self.minijeu_actuel = random.choice(list(mini_jeux.keys()))

            # On applique le délai
            self.cooldown = 0.1 + time.time()


# Initialisation et lancement du mini-jeu
game = Game()
game.main()

# Fin du programme
pygame.quit()