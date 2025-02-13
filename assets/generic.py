# Fait par Alexandre

# ------/ Importations des bibliothèques \------

import pygame
import pygame.freetype
import random
import time
from os import sep


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


# ------/ Classes \------

# Classe du Joueur
class GenericJoueur:

    # ------/ Constructeur \------

    def __init__(self, perso: str, id: int, ia: bool) -> None:
        """
        Constructeur de la classe Joueur.

        Attributs à définir:
            - perso (str): Personnage choisit par le joueur.
            - id (int): id du joueur qui indique sa position dans l'ordre de jeu.
            - ia (bool): Indique si le joueur est une ia ou un joueur lambda.

        Attributs internes:
            - pos (list): Position du joueur.
            - velocity (list): Vélocité/Accélération du joueur.
            - speed (int): Vitesse du joueur.

            - sprites_directory (str): Chemin du dossier des sprites du joueur.
            - sprites (dict): Sprites du joueurs.
            - sprite_pos (list): Position du sprite.
            - sprite (pygame.Surface): Sprite actuel du joueur.
            - frame (float): Indice du sprite à choisir.

            - shadow (pygame.Surface): Sprite de l'ombre du joueur.
            - shadow_pos (list): Position de l'ombre.

            - collision (pygame.Rect): Boîte de collision du joueur.
        """

        # Tests du type des paramètres donnés
        assert type(perso) == str, "Erreur: Le 1er paramètre (perso) est censé être une chaîne de caractères."
        assert type(id) == int, "Erreur: Le 2ème paramètre (id) est censé être un entier."
        assert type(ia) == bool, "Erreur: Le 3ème paramètre (ia) est censé être un booléen."


        # Définition du joueur
        self.perso = perso
        self.id = id
        self.ia = ia

        # Caractéristiques principales (stats)
        self.pos = [0.0, 0.0]
        self.velocity = [0.0, 0.0]
        self.speed = 0

        # Emplacement des sprites du joueur
        self.sprites_directory = "assets" + sep + "sprites" + sep + "characters" + sep + self.perso + sep

        # Définition des sprites (à définir dans les classes respectives)
        self.sprites = {}

        # Initialisation / positionnement du sprite actuel et de la frame choisie (à définir dans les classes respectives)
        self.sprite = None
        self.sprite_pos = list(self.pos)
        self.frame = 0.0

        # Initialisation et positionnement de l'ombre
        self.shadow = scale_image_by(pygame.image.load(self.sprites_directory + "shadow.png"), 3)
        self.shadow_pos = list(self.pos)

        # Boîte de collision du personnage (à définir dans les classes respectives)
        self.collision = None


    # ------/ Getters \------

    def get_pos(self) -> list:
        return self.pos

    def get_collisions(self) -> list:
        return [self.collision]

    def get_perso(self) -> str:
        return self.perso

    def get_id(self) -> int:
        return self.id

    def get_ia(self) -> bool:
        return self.ia


    # ------/ Setter \------

    def set_pos(self, new_pos: list) -> None:
        self.pos = new_pos


    # ------/ Méthodes \------

    def calculate_velocity(self, direction: list, delta_time: float) -> None:
        """
        Cette méthode permet de calculer la vélocité du joueur.

        Paramètres:
            - direction (list): Direction sous forme de vecteur dans laquelle le joueur se déplace.
            - delta_time (float): Valeur calculé dans le moteur de jeu qui permet l'indépendance de la vitesse au framerate.

        Pré-conditions:
            - direction doit être compris entre -1 et 1.
        """

        # Test des types de variables
        assert type(direction) == list, "Erreur: Le 1er paramètre (direction) n'est pas une liste."
        assert type(delta_time) == float, "Erreur: Le 2ème paramètre (delta_time) n'est pas un nombre flottant."

        # Test des valeurs dans direction
        for elem in direction:
            assert elem >= -1 and elem <= 1, "Erreur: Une des valeurs dans la direction donnée n'est pas valide."

        self.velocity[0] += direction[0] * self.speed * delta_time
        self.velocity[1] += direction[1] * self.speed * delta_time


    def apply_velocity(self) -> None:
        """
        Cette méthode permet d'appliquer la vélocité à la position et à d'autres paramètres du joueur.
        """

        # On ajoute la vélocité à la position du personnage
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]

        # On réinitialise la vélocité (sinon effet Asteroids (le personnage glisse infiniment))
        self.velocity = [0.0, 0.0]


    def animate(self, delta_time: float, speed: int) -> None:
        """
        Cette méthode permet d'animer le sprite du joueur. (Ici on augmente seulement la valeur qui permet d'afficher
        les animations).

        Paramètres:
            - delta_time (float): Valeur calculé dans le moteur de jeu qui permet l'indépendance de la vitesse au framerate.
            - speed (int): Vitesse de l'animation.
        """

        # Test du type des paramètres donnés
        assert type(delta_time) == float, "Erreur: Le 1er paramètre (delta_time) n'est pas un nombre flottant."
        assert type(speed) == int, "Erreur: Le 2ème paramètre (speed) n'est pas un nombre entier."

        # Changement de l'indice choisit avec une indépendance au framerate
        self.frame += speed * delta_time


    def draw(self, screen: pygame.Surface, show_collision: bool = False) -> tuple: # type: ignore
        """
        Cette méthode permet de dessiner le joueur sur l'écran.

        Paramètres:
            - screen (pygame.Surface): L'écran de jeu de pygame.
            - show_collision (bool): Paramètre optionnel permettant d'afficher les boîtes de collision.

        Returns:
            - tuple: Les multiplicateurs pour la taille de l'écran.
        """

        # Tests des types de variables
        assert type(screen) == pygame.Surface, "Erreur: Le 1er paramètre (screen) n'est pas une surface pygame."
        assert type(show_collision) == bool, "Erreur: Le 2ème paramètre (show_collision) n'est pas un booléen."

        # Initialisation des facteurs pour la taille de l'écran
        screen_factor = ((screen.get_rect().size[0] / 1280), (screen.get_rect().size[1] / 720))

        # Paramètre de débug pour afficher les collisions
        if show_collision:
            pygame.draw.rect(screen, (0, 255, 0), self.collision, 1)

        # On renvoie les multiplicateurs pour les classes enfants
        return screen_factor



# Classe du mini-jeu
class GenericMiniGame:

    # ------/ Constructeur \------

    def __init__(self, screen: pygame.Surface, clock, fps: int) -> None: # type: ignore
        """
        Constructeur de la classe GenericMiniGame.

        Attributs à définir:
            - screen (pygame.Surface): L'écran de jeu de pygame.
            - clock: L'horloge de pygame (permet de placer une limite de fps au jeu).
            - fps (int): Le nombre de fps maximal du jeu.

        Attributs internes:
            - delta_time (float): Valeur calculé dans le moteur de jeu qui permet l'indépendance de la vitesse au framerate.
            - quit (bool): Variable qui permet de détecter si le joueur a manuellement fermé le jeu.
            - screen_factor: Les multiplicateurs pour la taille de l'écran.

            - show_fps (bool): Paramètre de débug permettant d'afficher les fps.
            - show_collisions (bool): Paramètre de débug permettant d'afficher les boîtes de collision.

            - fps_font (pygame.freetype.Font): Police d'écriture pour les fps.
            - game_font (pygame.freetype.Font): Police d'écriture principale du mini-jeu.

            - joueurs (list): Liste des joueurs.
            - objets (list): Liste des objets.
            - classement (dict): Classement des joueurs à la fin du mini-jeu.
            - timer (float): Durée du timer du mini-jeu (si il en possède un).
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

        self.delta_time = 0.0
        self.quit = False
        self.screen_factor = (0, 0)

        # Paramètres de débug
        self.show_fps = False
        self.show_collisions = False

        # Polices d'écritures
        self.fps_font = pygame.freetype.Font("assets" + sep + "fonts" + sep + "ComicSansMS3.ttf", 20)
        self.game_font = pygame.freetype.Font("assets" + sep + "fonts" + sep + "mario-party.ttf", 50)

        # Initialisation des paramètres pour la partie gameplay
        self.joueurs = []
        self.objets = []
        self.classement = {}

        # Paramètres du timer (si il y en a un, self.timer > 0)
        self.timer = 0
        self.timer_background = pygame.image.load("assets" + sep + "sprites" + sep + "minigames" + sep + "general" + sep + "timer_back.png")

        # Sprites de toad (pour le chargement)
        self.toad = [pygame.image.load("assets" + sep + "sprites" + sep + "minigames" + sep + "general" + sep + "toad" + sep + "toad.png"),
                     pygame.image.load("assets" + sep + "sprites" + sep + "minigames" + sep + "general" + sep + "toad" + sep + "toad_open.png")]
        self.toad_shadow = pygame.image.load("assets" + sep + "sprites" + sep + "minigames" + sep + "general" + sep + "toad" + sep + "shadow.png")
        self.toad_bubble = pygame.image.load("assets" + sep + "sprites" + sep + "minigames" + sep + "general" + sep + "toad" + sep + "bubble.png")


    # ------/ Getters \------

    def get_quit(self) -> bool:
        return self.quit

    def get_classement(self) -> dict:
        return self.classement


    # ------/ Méthodes \------

    def game_engine(self, input_vectors: dict, prev_time: float) -> None:
        """
        Cette méthode gère à la fois l'affichage (des éléments principaux) et la physique présente dans le mini-jeu.

        Paramètres:
            - input_vectors (dict): Vecteurs de déplacement de chaque objets en fonction de leurs inputs.
            - prev_time (float): La valeur de temps passé avant l'appel de la méthode.

        Pré-conditions:
            - input_vectors doit uniquement contenir des listes.
        """

        # Tests du type de prev_time
        assert type(input_vectors) == dict, "Erreur: Le 1er paramètre (input_vectors) n'est pas un dictionnaire."
        assert type(prev_time) == float, "Erreur: Le 2ème paramètre (prev_time) n'est pas un nombre flottant."

        # Test de la contenance de input_vectors
        for value in input_vectors.values():
            assert type(value) == list, "Erreur: Le dictionnaire donné doit uniquement contenir des listes."

        # Initialisation des facteurs pour la taille de l'écran
        self.screen_factor = ((self.screen.get_rect().size[0] / 1280), (self.screen.get_rect().size[1] / 720))

        # Debug pour afficher les fps
        if self.show_fps:
            self.fps_font.render_to(self.screen, (0, 0), "FPS: " + str(round(self.clock.get_fps())), (0, 0, 0))

        # Calcul du delta time (infos précisées ci-dessous)
        # Le "delta time" est une valeur utilisée pour empêcher les problèmes de vitesse lié au framerate
        # (par exemple: 60 fps est 2x plus rapide que 30 fps, donc le jeu tourne 2x plus vite et le
        # personnage est censé bouger 2x plus rapidement, ce qui cause beaucoup de problèmes)
        # Pour régler ce problème, on calcule le temps entre 2 frames et on le multiplie à n'importe quelle
        # valeur voulue (principalement des valeurs liées au déplacement d'objets ou en fonction du temps).
        # Cela a pour effet de corriger ces bugs de vitesse car le delta time varie en fonction des fps.
        self.delta_time = time.time() - prev_time


    def load(self, chemin_musique, nom, description) -> None:
        """
        Cette méthode représente la phase de chargement du mini-jeu.
        """

        # État de la phase (True veut dire qu'elle est en cours)
        running = True

        # On charge la musique en avance (réduction légère du lag)
        pygame.mixer.music.load(chemin_musique)

        # Initialisation du timer
        cooldown = 3 + time.time()

        # Initialisation du temps passé pour calculer le delta time
        prev_time = time.time()

        # Boucle principale de cette phase du jeu
        while running:

            # Détection de la fermeture de fenêtre
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.quit = True

                # Changement de taille de la fenêtre
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)

                # Détection des inputs du joueur
                elif event.type == pygame.MOUSEBUTTONUP and cooldown - time.time() < 0:
                    running = False

            # Initialisation des facteurs pour la taille de l'écran
            self.screen_factor = ((self.screen.get_rect().size[0] / 1280), (self.screen.get_rect().size[1] / 720))

            # Affichage de l'écran de chargement et du texte
            self.screen.fill((0, 0, 0))

            # Redimension des textes
            nom_text = scale_image_by(self.game_font.render(nom, (255, 255, 255))[0], self.screen_factor)
            nom_textRect = nom_text.get_rect()
            nom_textRect.center = (round(640 * self.screen_factor[0]), round(70 * self.screen_factor[1]))
            chargement = "CHARGEMENT..." if cooldown - time.time() > 0 else "(Cliquez pour lancer le mini-jeu !)"
            chargement_text = scale_image_by(self.game_font.render(chargement, (255, 255, 255))[0], (0.8 * self.screen_factor[0], 0.8 * self.screen_factor[1]))
            chargement_textRect = chargement_text.get_rect()
            chargement_textRect.center = (round(640 * self.screen_factor[0]), round(680 * self.screen_factor[1]))

            joueur1_text = scale_image_by(self.game_font.render("Joueur 1:", (255, 255, 255))[0], self.screen_factor)
            joueur2_text = scale_image_by(self.game_font.render("Joueur 2:", (255, 255, 255))[0], self.screen_factor)

            # Affichage des textes
            self.screen.blit(nom_text, nom_textRect)
            self.screen.blit(chargement_text, chargement_textRect)
            self.screen.blit(joueur1_text, (round(980 * self.screen_factor[0]), round(70 * self.screen_factor[1])))
            self.screen.blit(joueur2_text, (round(980 * self.screen_factor[0]), round(370 * self.screen_factor[1])))

            # Affichage de Toad (pour présenter le mini-jeu)
            self.screen.blit(scale_image_by(self.toad_shadow, (6 * self.screen_factor[0], 6 * self.screen_factor[1])), (round(114 * self.screen_factor[0]), round(535 * self.screen_factor[1])))
            self.screen.blit(scale_image_by(self.toad[1], (5 * self.screen_factor[0], 5 * self.screen_factor[1])), (round(100 * self.screen_factor[0]), round(400 * self.screen_factor[1])))
            self.screen.blit(scale_image_by(self.toad_bubble, (5 * self.screen_factor[0], 5 * self.screen_factor[1])), (round(240 * self.screen_factor[0]), round(150 * self.screen_factor[1])))

            # Affichage de la description
            for line in description:
                description_text = scale_image_by(self.game_font.render(line, (0, 0, 0))[0], (0.7 * self.screen_factor[0], 0.7 * self.screen_factor[1]))
                self.screen.blit(description_text, (round(260 * self.screen_factor[0]), round((170 + description.index(line) * 37) * self.screen_factor[1])))

            # Image des touches du clavier pour chaque joueur
            layout_joueur_1 = scale_image_by(pygame.image.load("assets" + sep + "sprites" + sep + "minigames" + sep + "general" + sep + "layout_joueur_1.png"), self.screen_factor)
            layout_joueur_2 = scale_image_by(pygame.image.load("assets" + sep + "sprites" + sep + "minigames" + sep + "general" + sep + "layout_joueur_2.png"), self.screen_factor)

            # Affichages des touches de clavier pour chaque joueur
            self.screen.blit(layout_joueur_1, (round(930 * self.screen_factor[0]), round(150 * self.screen_factor[1])))
            self.screen.blit(layout_joueur_2, (round(930 * self.screen_factor[0]), round(480 * self.screen_factor[1])))

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

        # Initialisation des paramètres par défaut de la phase
        running = True
        prev_time = time.time()

        # Initialisation du texte start et de ses coordonnées de départ
        start_image = pygame.image.load("assets" + sep + "sprites" + sep + "minigames" + sep + "general" + sep + "start.png")
        start_image_x = -start_image.get_rect().w
        start_image_y = round((640 - start_image.get_rect().h) / 2)

        # Initialisation du timer
        cooldown = 0

        # Réinitialisation des vecteurs de déplacement des objets
        input_vectors = {objet: [0, 0] for objet in self.objets}

        # Boucle principale de cette phase du jeu
        while running:

            # Détection de la fermeture de fenêtre
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.quit = True

                # Changement de taille de la fenêtre
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)

            # Utilisation du moteur de jeu et mise à jour du temps passé
            self.game_engine(input_vectors, prev_time)
            prev_time = time.time()

            # Affichage du texte start
            self.screen.blit(scale_image_by(start_image, (4 * self.screen_factor[0], 4 * self.screen_factor[1])), (round(start_image_x * self.screen_factor[0]), round(start_image_y * self.screen_factor[1])))

            # Arrête la phase d'intro si le texte sort de l'écran
            if start_image_x > 1280:
                running = False

            # Si le texte se trouve au milieu de l'écran et que le timer n'est pas encore lancé
            elif (start_image_x + 2000 * self.delta_time) > (1000 - start_image.get_rect().w) / 2 and cooldown == 0:
                cooldown = time.time()
                pygame.mixer.Sound("assets" + sep + "sounds" + sep + "minigames" + sep + "start.ogg").play()

            # Si le timer a duré 0.5s ou qu'il n'est pas encore lancé
            elif time.time() - cooldown > 0.5 or cooldown == 0:
                # Déplacement de l'image
                start_image_x += 2000 * self.delta_time
                start_image_x = round(start_image_x)

            # Mise à jour de l'écran et limite de fps
            pygame.display.flip()
            self.clock.tick(self.fps)

        # Lancement du mini-jeu en lui même (si le joueur n'a pas fermé la fenêtre)
        if not self.quit:

            # Lancement du son de sifflet et la musique chargée
            pygame.mixer.Sound("assets" + sep + "sounds" + sep + "minigames" + sep + "start_sifflet.ogg").play()
            pygame.mixer.music.play(loops=-1)

            # Mise en place d'un timer pour le mini-jeu (s'il y en a un)
            if self.timer > 0:
                self.timer = time.time() + self.timer

            self.during_game()


    def during_game(self) -> None:
        """
        Cette méthode représente la phase de déroulement du mini-jeu.
        (Elle est peu complète ici car elle est différente dans chaque mini-jeu)
        """

        if self.timer > 0:
            # Affichage du fond du timer
            timer_sprite = scale_image_by(self.timer_background, self.screen_factor)
            timer_background_textRect = timer_sprite.get_rect()
            timer_background_textRect.center = (self.screen.get_rect().w // 2, round(37 * self.screen_factor[1]))
            self.screen.blit(timer_sprite, timer_background_textRect)

            # Positionnement du timer au centre-haut de l'écran
            timer_text = self.game_font.render(str(round(self.timer - time.time())), (255, 255, 255))
            timer_text_scaled = scale_image_by(timer_text[0], self.screen_factor)
            timer_textRect = timer_text_scaled.get_rect()
            timer_textRect.center = (self.screen.get_rect().w // 2, round(37 * self.screen_factor[1]))

            # Affichage du timer
            self.screen.blit(timer_text_scaled, timer_textRect)


    def end_game(self) -> None:
        """
        Cette méthode représente la phase de fin du mini-jeu.
        """

        # Initialisation des paramètres par défaut de la phase
        running = True
        prev_time = time.time()

        # Arrêt de la musique et son de fin
        pygame.mixer.music.stop()
        pygame.mixer.Sound("assets" + sep + "sounds" + sep + "minigames" + sep + "finish.ogg").play()

        # Initialisation du texte finish et de ses coordonnées de départ
        finish_image = pygame.image.load("assets" + sep + "sprites" + sep + "minigames" + sep + "general" + sep + "finish.png")
        finish_image_x = -finish_image.get_rect().w
        finish_image_y = round((640 - finish_image.get_rect().h) / 2)

        # Initialisation du timer
        cooldown = 0

        # Réinitialisation des vecteurs de déplacement des objets
        input_vectors = {objet: [0, 0] for objet in self.objets}

        # Boucle principale de cette phase du jeu
        while running:

            # Détection de la fermeture de fenêtre
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.quit = True

                # Changement de taille de la fenêtre
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)

            # Utilisation du moteur de jeu et mise à jour du temps passé
            self.game_engine(input_vectors, prev_time)
            prev_time = time.time()

            # Affichage du texte finish
            self.screen.blit(scale_image_by(finish_image, (4 * self.screen_factor[0], 4 * self.screen_factor[1])), (round(finish_image_x * self.screen_factor[0]), round(finish_image_y * self.screen_factor[1])))

            # Arrête la phase de fin au bout de 1.5s si le timer est déjà lancé
            if time.time() - cooldown > 1.5 and cooldown > 0:
                running = False

            # Si le texte se trouve au milieu de l'écran et que le timer n'est pas encore lancé
            elif (finish_image_x + 2000 * self.delta_time) > (1000 - finish_image.get_rect().w) / 2 and cooldown == 0:
                cooldown = time.time()

            # Si le timer n'est pas encore lancé
            elif cooldown == 0:
                finish_image_x += 2000 * self.delta_time
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
        (Elle est vide ici car elle est différente dans chaque mini-jeu)
        """

        # Lancement de l'annonce des gagnants
        self.announce_winners()


    def announce_winners(self) -> None:
        """
        Cette méthode permet d'annoncer les gagnants du mini-jeu à l'aide d'un affichage spécial
        sur l'écran.
        """

        # Initialisation des paramètres par défaut de la phase
        running = True
        prev_time = time.time()

        # On note tous les gagnants de la partie
        gagnants = []
        for joueur in self.classement.keys():
            if self.classement[joueur] == 1:
                gagnants.append(joueur)

        # Initialisation du texte win
        win_image = None

        # Changement du texte et de la musique jouée selon différents cas
        if len(gagnants) == 0:
            win_image = pygame.image.load("assets" + sep + "sprites" + sep + "minigames" + sep + "general" + sep + "tie.png")
            pygame.mixer.music.load("assets" + sep + "musics" + sep + "minigames" + sep + "draw.ogg")
        elif len(gagnants) > 1:
            win_image = pygame.image.load("assets" + sep + "sprites" + sep + "minigames" + sep + "general" + sep + "wins.png")
            pygame.mixer.music.load("assets" + sep + "musics" + sep + "minigames" + sep + "win.ogg")
        else:
            win_image = pygame.image.load("assets" + sep + "sprites" + sep + "minigames" + sep + "general" + sep + "win.png")
            pygame.mixer.music.load("assets" + sep + "musics" + sep + "minigames" + sep + "win.ogg")

        # Timer de 5s
        cooldown = 5 + time.time()

        # Lancement de la musique
        pygame.mixer.music.play()

        # Réinitialisation des vecteurs de déplacement des objets
        input_vectors = {objet: [0, 0] for objet in self.objets}

        # Boucle principale de cette phase du jeu
        while running:

            # Détection de la fermeture de fenêtre
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.quit = True

                # Changement de taille de la fenêtre
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)

            # Utilisation du moteur de jeu et mise à jour du temps passé
            self.game_engine(input_vectors, prev_time)
            prev_time = time.time()

            # Position x du texte du 1er gagnant
            image_x = 120 if len(gagnants) > 2 else 320

            for gagnant in gagnants:
                # Initialisation et positionnement du texte de chaque gagnant
                image_gagnant = scale_image_by(pygame.image.load("assets" + sep + "sprites" + sep + "minigames" + sep + "general" + sep + gagnant + ".png"), 4)
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
            if cooldown - time.time() <= 0:
                running = False

            # Mise à jour de l'écran et limite de fps
            pygame.display.flip()
            self.clock.tick(self.fps)
