# Fait par Alexandre

# ------/ Importations des bibliothèques \------

import pygame
import pygame.freetype
from math import sqrt
import random
import time
from os import sep

import assets.generic as generic


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
class Joueur(generic.GenericJoueur):

    # ------/ Constructeur \------

    def __init__(self, perso: str, id: int, ia: bool, side: str) -> None:
        """
        Constructeur de la classe Joueur.

        Attributs à définir:
            - perso (str): Personnage choisit par le joueur.
            - id (int): id du joueur qui indique sa position dans l'ordre de jeu.
            - ia (bool): Indique si le joueur est une ia ou un joueur lambda.
            - side (str): Côté du joueur (left ou right) (exclusif à ce mini-jeu).

        Attributs internes:
            - speed (int): Vitesse du joueur.

            - platform (pygame.Surface): Sprite de la plateforme du joueur.
            - sprites (dict): Sprites du joueurs.
            - sprite (pygame.Surface): Sprite actuel du joueur.
            - sprite_pos (list): Position du sprite (du pistolet si solo ou du joueur sinon).

            - collision (pygame.Rect): Boîte de collision du joueur.
        """

        # Tests du type des paramètres donnés
        assert type(side) == str, "Erreur: Le 4ème paramètre (side) est censé être une chaîne de caractères."


        # On initialise tous les attributs du constructeur parent
        super().__init__(perso, id, ia)

        # Définition du joueur
        self.side = side

        # Caractéristiques principales (stats)
        self.speed = 500

        # Sprite de la plateforme du joueur
        self.platform = generic.scale_image_by(pygame.image.load("assets" + sep + "sprites" + sep + "minigames" + sep + "speed_hockey" + sep + self.side + "_platform.png"), 3)

        # Définition des sprites automatiquement (pour les joueurs / ia)
        self.sprites = {"left": [generic.scale_image_by(pygame.image.load(self.sprites_directory + "hockey_left" + str(i) + ".png"), 3) for i in range(4)],
                        "right": [generic.scale_image_by(pygame.image.load(self.sprites_directory + "hockey_right" + str(i) + ".png"), 3) for i in range(4)]
        }

        # Initialisation / positionnement du sprite actuel
        self.sprite = self.sprites[self.side][0]
        self.sprite_pos = list(self.pos)

        # Boîte de collision du personnage
        self.collision = pygame.Rect(0, 0, self.platform.get_rect().w, self.platform.get_rect().h - 10)


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

        # Le parent s'occupe du calcul en x et y
        super().calculate_velocity(direction, delta_time)

        # On réinitialise la vélocité en x (car il ne peut pas se déplacer en x)
        self.velocity[0] = 0


    def calculate_collisions(self, objets: list) -> None:
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

        # Calcul des collisions pour chaque objets
        for objet in objets:
            if objet != self:
                # Pas de rect_x parce que le joueur est bloqué sur l'axe y
                rect_y = pygame.Rect(self.collision.x, round(self.collision.y + self.velocity[1]), self.collision.w, self.collision.h)

                # On stoppe la vélocité du joueur si il collisionne avec une boîte de collision
                for collision in objet.get_collisions():
                    if rect_y.colliderect(collision):
                        self.velocity[1] = 0.0


    def apply_velocity(self) -> None:
        """
        Cette méthode permet d'appliquer la vélocité à la position et à d'autres paramètres du joueur.
        """

        # Le parent applique l'accélération à la position
        super().apply_velocity()

        # La position du joueur est bloquée entre ces deux intervalles
        self.pos[1] = max(200, min(self.pos[1], 488))

        # Positionnement du sprite du joueur sur la plateforme
        self.sprite_pos[0] = round(self.pos[0] - (self.sprite.get_rect().w - self.platform.get_rect().w) / 2)
        self.sprite_pos[1] = round(self.pos[1] - self.sprite.get_rect().bottom + self.platform.get_rect().h / 2)

        # Positionnement de la boîte de collision
        self.collision.x = round(self.pos[0])
        self.collision.y = round(self.pos[1] + self.platform.get_rect().bottom - self.collision.h)

        # Positionnement de l'ombre
        self.shadow_pos[0] = round(self.sprite_pos[0] + (self.sprite.get_rect().w - self.shadow.get_rect().w) / 2)
        self.shadow_pos[1] = round(self.sprite_pos[1] + self.sprite.get_rect().h - self.shadow.get_rect().h)


    def animate(self, delta_time: float) -> None:
        """
        Cette méthode permet d'animer le sprite du joueur.

        Paramètres:
            - delta_time (float): Valeur calculé dans le moteur de jeu qui permet l'indépendance de la vitesse au framerate.

        Pré-conditions:
            - delta_time doit être un nombre flottant.
        """

        # Test du type de delta_time
        assert type(delta_time) == float, "Erreur: Le paramètre donné (delta_time) n'est pas un nombre flottant."

        # self.frame ne doit pas dépasser l'indice de la liste de sprites
        if self.frame > len(self.sprites[self.side]) - 1:
            self.frame = 0

        # Changement du sprite actuel
        self.sprite = self.sprites[self.side][round(self.frame)]

        # Le parent s'occupe de changer la frame en fonction de la vitesse
        super().animate(delta_time, 5)


    def draw(self, screen: pygame.Surface, show_collision: bool = False) -> None: # type: ignore
        """
        Cette méthode permet de dessiner le joueur sur l'écran.

        Paramètres:
            - screen (pygame.Surface): L'écran de jeu de pygame.
            - show_collision (bool): Paramètre optionnel permettant d'afficher les boîtes de collision.

        Pré-conditions:
            - screen doit être de type pygame.Surface.
        """

        # Tests des types de variables
        assert type(screen) == pygame.Surface, "Erreur: Le 1er paramètre (screen) n'est pas une surface pygame."
        assert type(show_collision) == bool, "Erreur: Le 2ème paramètre (show_collision) n'est pas un booléen."

        # Initialisation des facteurs pour la taille de l'écran avec le parent
        screen_factor = super().draw(screen, show_collision)

        # Affichage des sprites
        screen.blit(generic.scale_image_by(self.platform, screen_factor), (round(self.pos[0] * screen_factor[0]), round(self.pos[1] * screen_factor[1])))
        screen.blit(generic.scale_image_by(self.shadow, screen_factor), (round(self.shadow_pos[0] * screen_factor[0]), round(self.shadow_pos[1] * screen_factor[1])))
        screen.blit(generic.scale_image_by(self.sprite, screen_factor), (round(self.sprite_pos[0] * screen_factor[0]), round(self.sprite_pos[1] * screen_factor[1])))



# Classe de la carapace
class Carapace:

    # ------/ Constructeur \------

    def __init__(self) -> None:
        """
        Constructeur de la classe Joueur.

        Attributs internes:
            - pos (list): Position de la carapace.
            - velocity (list): Vélocité/Accélération de la carapace.
            - speed (int): Vitesse de la carapace.
            - direction (list): Direction de la carapace.

            - sprite (pygame.Surface): Sprite actuel de la carapace.

            - hit_sound (pygame.mixer.Sound): Son de collision avec la carapace.
            - sound_cooldown (float): Un délai entre chaque son.

            - collision (pygame.Rect ou None): Boîte de collision du joueur.
        """

        # Caractéristiques principales
        self.pos = [0.0, 0.0]
        self.velocity = [0.0, 0.0]
        self.speed = 600
        self.direction = [0, 0]

        # Emplacement des sprites du mini-jeu
        minigame_directory = "assets" + sep + "sprites" + sep + "minigames" + sep + "speed_hockey" + sep

        # Sprite actuel
        self.sprite = generic.scale_image_by(pygame.image.load(minigame_directory + "carapace.png"), 3)

        # Paramètres du son
        self.hit_sound = pygame.mixer.Sound("assets" + sep + "sounds" + sep + "minigames" + sep + "speed_hockey" + sep + "carapace.ogg")
        self.sound_cooldown = 0.0

        # Boîte de collision de la carapace
        self.collision = pygame.Rect(0, 0, self.sprite.get_rect().w, self.sprite.get_rect().h)


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

    def calculate_velocity(self, delta_time: float) -> None:
        """
        Cette méthode permet de calculer la vélocité de la carapace.

        Paramètres:
            - delta_time (float): Valeur calculé dans le moteur de jeu qui permet l'indépendance de la vitesse au framerate.

        Pré-conditions:
            - direction doit être compris entre -1 et 1.
        """

        # Test du type de delta_time
        assert type(delta_time) == float, "Erreur: Le paramètre donné (delta_time) n'est pas un nombre flottant."

        # Calcul de la vélocité
        self.velocity[0] += self.direction[0] * self.speed * delta_time
        self.velocity[1] += self.direction[1] * self.speed * delta_time

        # On normalise la vélocité
        self.velocity = normalize(self.velocity)


    def calculate_collisions(self, objets: list) -> None:
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

        # Calcul des collisions pour chaque objets
        for objet in objets:
            if objet != self:
                rect_x = pygame.Rect(round(self.collision.x + self.velocity[0]), self.collision.y, self.collision.w, self.collision.h)
                rect_y = pygame.Rect(self.collision.x, round(self.collision.y + self.velocity[1]), self.collision.w, self.collision.h)

                for collision in objet.get_collisions():
                    # On stoppe la vélocité en x du joueur si il collisionne avec une boîte de collision en x
                    if rect_x.colliderect(collision):
                        self.velocity[0] = 0.0

                        # On inverse sa direction en x et on ajoute 20 à sa vitesse
                        self.direction[0] *= -1
                        self.speed += 20

                        # On met un cooldown de 0.2s ici pour éviter que le son se répète trop rapidement
                        if self.sound_cooldown - time.time() <= 0:
                            self.hit_sound.play()
                            self.sound_cooldown = 0.2 + time.time()

                    # On stoppe la vélocité en y du joueur si il collisionne avec une boîte de collision en y
                    if rect_y.colliderect(collision):
                        self.velocity[1] = 0.0

                        # On inverse sa direction en y et on ajoute 20 à sa vitesse
                        self.direction[1] *= -1
                        self.speed += 20
        
                        # On met un cooldown de 0.2s ici pour éviter que le son se répète trop rapidement
                        if self.sound_cooldown - time.time() <= 0:
                            self.hit_sound.play()
                            self.sound_cooldown = 0.2 + time.time()


    def apply_velocity(self) -> None:
        """
        Cette méthode permet d'appliquer la vélocité à la position et à d'autres paramètres du joueur.
        """

        # On ajoute la vélocité à la position de la carapace
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]

        # On met à jour la collision à la position de la carapace
        self.collision.x = round(self.pos[0])
        self.collision.y = round(self.pos[1])

        # On réinitialise la vélocité (sinon effet Asteroids (le personnage glisse infiniment))
        self.velocity = [0.0, 0.0]


    def reset(self) -> None:
        """
        Cette méthode sert à réinitialiser les caractéristiques de la carapace par défaut et à choisir
        une nouvelle direction aléatoire.
        """

        # Réinitialisation de la position / vitesse
        self.pos = [605, 344]
        self.speed = 600

        # Toutes les directions possibles empruntables par la carapace
        directions = ([1, 1], [1, 0.5], [0.5, 1])

        # On en choisit une aléatoirement puis on choisit le sens où elle va aller
        self.direction = random.choice(directions)
        self.direction[0] *= random.choice((1, -1))


    def draw(self, screen: pygame.Surface, show_collision: bool = False) -> None: # type: ignore
        """
        Cette méthode permet de dessiner le joueur sur l'écran.

        Paramètres:
            - screen (pygame.Surface): L'écran de jeu de pygame.
            - show_collision (bool): Paramètre optionnel permettant d'afficher les boîtes de collision.

        Pré-conditions:
            - screen doit être de type pygame.Surface.
        """

        # Tests des types de variables
        assert type(screen) == pygame.Surface, "Erreur: Le 1er paramètre (screen) n'est pas une surface pygame."
        assert type(show_collision) == bool, "Erreur: Le 2ème paramètre (show_collision) n'est pas un booléen."

        # Initialisation des facteurs pour la taille de l'écran
        screen_factor = ((screen.get_rect().size[0] / 1280), (screen.get_rect().size[1] / 720))

        # Affichage de la carapace
        screen.blit(generic.scale_image_by(self.sprite, screen_factor), (round(self.pos[0] * screen_factor[0]), round(self.pos[1] * screen_factor[1])))

        # Paramètre de débug pour afficher les collisions
        if show_collision:
            pygame.draw.rect(screen, (0, 255, 0), self.collision, 1)



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


    # ------/ Méthode \------

    def draw(self, screen: pygame.Surface, show_collision: bool = False) -> None: # type: ignore
        """
        Cette méthode permet de dessiner le collider sur l'écran.

        Paramètres:
            - screen (pygame.Surface): L'écran de jeu de pygame.
            - show_collision (bool): Paramètre optionnel permettant d'afficher les boîtes de collision.

        Pré-conditions:
            - screen doit être de type pygame.Surface.
        """

        # Tests des types de variables
        assert type(screen) == pygame.Surface, "Erreur: Le 1er paramètre (screen) n'est pas une surface pygame."
        assert type(show_collision) == bool, "Erreur: Le 2ème paramètre (show_collision) n'est pas un booléen."

        if show_collision:
            pygame.draw.rect(screen, (0, 255, 0), self.collision, 1)



# Classe d'un but
class But:

    # ------/ Constructeur \------

    def __init__(self, pos, sprite) -> None:
        """
        Constructeur de la classe But.

        Attributs à définir:
            - pos (list): Position du but.
            - taille (list): Taille du but.

        Attributs internes:
            - collisions (list): Liste des boîtes de collision du but.
        """

        # Test des types des paramètres donnés
        assert type(pos) == list, "Erreur: Le 1er paramètre (pos) n'est pas une liste."
        assert type(sprite) == pygame.Surface, "Erreur: Le 2ème paramètre (sprite) n'est pas une image pygame."

        # Caractéristiques du but
        self.pos = pos
        self.sprite = sprite

        # Boîte de collision du but
        self.collisions = [pygame.Rect(self.pos[0], self.pos[1] - 48, self.sprite.get_rect().w, 133),
                           pygame.Rect(self.pos[0], self.pos[1] + 513 - 133, self.sprite.get_rect().w, 133)]


    # ------/ Getter \------

    def get_pos(self) -> list:
        return self.pos

    def get_collisions(self) -> list:
        return self.collisions


    # ------/ Méthode \------

    def draw(self, screen: pygame.Surface, show_collision: bool = False) -> None: # type: ignore
        """
        Cette méthode permet de dessiner le collider sur l'écran.

        Paramètres:
            - screen (pygame.Surface): L'écran de jeu de pygame.
            - show_collision (bool): Paramètre optionnel permettant d'afficher les boîtes de collision.

        Pré-conditions:
            - screen doit être de type pygame.Surface.
        """

        # Tests des types de variables
        assert type(screen) == pygame.Surface, "Erreur: Le 1er paramètre (screen) n'est pas une surface pygame."
        assert type(show_collision) == bool, "Erreur: Le 2ème paramètre (show_collision) n'est pas un booléen."

        # Initialisation des facteurs pour la taille de l'écran
        screen_factor = ((screen.get_rect().size[0] / 1280), (screen.get_rect().size[1] / 720))

        # Affichage du but
        screen.blit(generic.scale_image_by(self.sprite, screen_factor), (round(self.pos[0] * screen_factor[0]), round(self.pos[1] * screen_factor[1])))

        # Paramètre de débug pour afficher les collisions
        if show_collision:
            for collision in self.collisions:
                pygame.draw.rect(screen, (0, 255, 0), collision, 1)



# Classe du mini-jeu
class MiniGame(generic.GenericMiniGame):

    # ------/ Constructeur \------

    def __init__(self, screen: pygame.Surface, clock, fps: int) -> None: # type: ignore
        """
        Constructeur de la classe MiniGame.

        Attributs à définir:
            - screen (pygame.Surface): L'écran de jeu de pygame.
            - clock: L'horloge de pygame (permet de placer une limite de fps au jeu).
            - fps (int): Le nombre de fps maximal du jeu.

        Attributs internes:
            - timer (float): Durée du mini-jeu.

            - score (list): Stockage du score de la partie.

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


        # On initialise tous les attributs du constructeur parent
        super().__init__(screen, clock, fps)

        # Initialisation des paramètres pour la partie gameplay
        self.timer = 60

        # Stockage du score de la partie
        self.score = [0, 0]

        # Sprites utilisés dans toute la classe
        minigame_directory = "assets" + sep + "sprites" + sep + "minigames" + sep + "speed_hockey" + sep
        self.bg = pygame.image.load((minigame_directory + "hockey.png"))
        self.ligne_rouge = pygame.image.load(minigame_directory + "ligne_rouge.png")
        self.ligne_verte = pygame.image.load(minigame_directory + "ligne_verte.png")
        self.lampes_rouges = [pygame.image.load(minigame_directory + "lampe_rouge_eteinte.png"),
                              pygame.image.load(minigame_directory + "lampe_rouge.png")]
        self.lampes_vertes = [pygame.image.load(minigame_directory + "lampe_verte_eteinte.png"),
                              pygame.image.load(minigame_directory + "lampe_verte.png")]

        self.carapace = Carapace()

        # La position et la taille des colliders sont basés sur l'image du background
        self.colliders = [Collider([87, 108], [1106, 21]), Collider([87, 641], [1106, 28])]

        self.buts = [But([0, 156], generic.scale_image_by(pygame.image.load(minigame_directory + "but_rouge.png"), 4)),
                     But([1180, 156], generic.scale_image_by(pygame.image.load(minigame_directory + "but_vert.png"), 4))]

        # Initialisation du son du sifflet des buts
        self.son_but = pygame.mixer.Sound("assets" + sep + "sounds" + sep + "minigames" + sep + "speed_hockey" + sep + "sifflet.ogg")


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

        # Tests du type des paramètres donnés
        assert type(input_vectors) == dict, "Erreur: Le 1er paramètre (input_vectors) n'est pas un dictionnaire."
        assert type(prev_time) == float, "Erreur: Le 2ème paramètre (prev_time) n'est pas un nombre flottant."

        # Test de la contenance de input_vectors
        for value in input_vectors.values():
            assert type(value) == list, "Erreur: Le dictionnaire donné doit uniquement contenir des listes."

        # On affiche les sprites du jeu dans un ordre d'affichage prédéfini
        self.screen.blit(generic.scale_image_by(self.bg, self.screen_factor), (0, 0))

        # Placement des lignes sur le terrain
        self.screen.blit(generic.scale_image_by(self.ligne_rouge, (4 * self.screen_factor[0], 4 * self.screen_factor[1])), (round(200 * self.screen_factor[0]), round(200 * self.screen_factor[1])))
        self.screen.blit(generic.scale_image_by(self.ligne_rouge, (4 * self.screen_factor[0], 4 * self.screen_factor[1])), (round(400 * self.screen_factor[0]), round(200 * self.screen_factor[1])))

        self.screen.blit(generic.scale_image_by(self.ligne_verte, (4 * self.screen_factor[0], 4 * self.screen_factor[1])), (round(852 * self.screen_factor[0]), round(200 * self.screen_factor[1])))
        self.screen.blit(generic.scale_image_by(self.ligne_verte, (4 * self.screen_factor[0], 4 * self.screen_factor[1])), (round(1052 * self.screen_factor[0]), round(200 * self.screen_factor[1])))

        # Placement des lampes sur le terrain
        offset = 0
        for i in range(3):
            # On allume les lampes en fonction de la taille du score par rapport à i
            if i < self.score[0]:
                self.screen.blit(generic.scale_image_by(self.lampes_rouges[1], (2 * self.screen_factor[0], 2 * self.screen_factor[1])), (round((80 + offset) * self.screen_factor[0]), round(8 * self.screen_factor[1])))
            else:
                self.screen.blit(generic.scale_image_by(self.lampes_rouges[0], (2 * self.screen_factor[0], 2 * self.screen_factor[1])), (round((80 + offset) * self.screen_factor[0]), round(8 * self.screen_factor[1])))
            # Augmentation du décalage de chaque lampe
            offset += 100

        offset = 0
        for i in range(3):
            # On allume les lampes en fonction de la taille du score par rapport à i
            if i < self.score[1]:
                self.screen.blit(generic.scale_image_by(self.lampes_vertes[1], (2 * self.screen_factor[0], 2 * self.screen_factor[1])),(round((920 + offset) * self.screen_factor[0]), round(8 * self.screen_factor[1])))
            else:
                self.screen.blit(generic.scale_image_by(self.lampes_vertes[0], (2 * self.screen_factor[0], 2 * self.screen_factor[1])), (round((920 + offset) * self.screen_factor[0]), round(8 * self.screen_factor[1])))
            # Augmentation du décalage de chaque lampe
            offset += 100

        # Calcul de la physique de chaque joueur
        for plr in self.joueurs:
            # Calcul de la vélocité et des collsisions des joueurs
            plr.calculate_velocity(input_vectors[plr], self.delta_time)
            plr.calculate_collisions(self.objets)

            # Calcul de l'animation du joueur actuel
            plr.animate(self.delta_time)

            # On applique le mouvement au joueur
            plr.apply_velocity()

        # Calcul des physiques de la carapace
        self.carapace.calculate_velocity(self.delta_time)
        self.carapace.calculate_collisions(self.objets)
        self.carapace.apply_velocity()

        # Affichage des objets sur l'écran
        for objet in self.objets:
            objet.draw(self.screen, self.show_collisions)

        # Le parent s'occupe du reste de la méthode
        super().game_engine(input_vectors, prev_time)


    def load(self, param_joueurs: dict) -> None:
        """
        Cette méthode représente la phase de chargement du mini-jeu.

        Paramètres:
            - param_joueurs (dict): Les paramètres de chaque joueur.

        Pré-conditions:
            - param_joueurs doit être composé de 4 éléments (car 4 joueurs).
        """

        # Test du type de param_joueurs
        assert type(param_joueurs) == dict, "Erreur: Le paramètre donné (param_joueurs) n'est pas un dictionnaire."

        # Test de la taille de param_joueurs
        assert len(param_joueurs.keys()) == 4, "Erreur: Le dictionnaire donné ne contient pas assez de joueurs."

        # Liste des noms des joueurs
        liste_joueurs = list(param_joueurs.keys())

        # Ordre aléatoire pour que chaque joueur puisse avoir une équipe aléatoire
        random.shuffle(liste_joueurs)

        # Création des joueurs dans la liste
        for i in range(len(liste_joueurs)):
            nom_joueur = liste_joueurs[i]
            id_joueur = param_joueurs[nom_joueur][0]
            ia_joueur = param_joueurs[nom_joueur][1]

            # Les deux premiers joueurs de la liste sont dans l'équipe rouge, les autres chez les verts
            side_joueur = "left" if i < 2 else "right"

            self.joueurs.append(Joueur(nom_joueur, id_joueur, ia_joueur, side_joueur))

        # Positionnement des joueurs + carapace
        self.joueurs[0].set_pos([180, 344])
        self.joueurs[1].set_pos([380, 344])
        self.joueurs[2].set_pos([832, 344])
        self.joueurs[3].set_pos([1032, 344])

        self.carapace.set_pos([605, 344])

        # Initialisation de la liste des objets
        self.objets = [self.carapace] + self.colliders + self.buts + self.joueurs

        # Textes pour la description du jeu
        description = ["Joueurs en équipe:",
                       "Faites rebondir la carapace",
                       "pour la faire rentrer dans les",
                       "buts adverses !"]

        # Le parent s'occupe du reste de la méthode
        super().load("assets" + sep + "musics" + sep + "minigames" + sep + "speed_hockey.ogg", "Speed Hockey", description)


    def during_game(self) -> None:
        """
        Cette méthode représente la phase de déroulement du mini-jeu.
        """

        # Initialisation des paramètres par défaut de la phase
        running = True
        prev_time = time.time()

        # Réinitialisation de la carapace
        self.carapace.reset()

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

            # Le mini-jeu s'arrête si le timer s'arrête ou si l'une des deux équipes a 3 points
            if self.timer - time.time() <= 0:
                running = False
            elif self.score[0] > 2:
                running = False
            elif self.score[1] > 2:
                running = False

            # Détection des inputs et réinitialisation des vecteurs de déplacement des objets
            inputs = pygame.key.get_pressed()
            input_vectors = {joueur: [0, 0] for joueur in self.joueurs}

            # Comportement des joueurs
            for joueur in self.joueurs:
                if not joueur.get_ia():
                    # Commandes joueur 1
                    if joueur.get_id() == 1:
                        # Selon la version de pygame et de python ça peut changer
                        if inputs[pygame.K_w] or inputs[pygame.K_z]:
                            input_vectors[joueur][1] -= 1
                        if inputs[pygame.K_s]:
                            input_vectors[joueur][1] += 1

                    # Commandes joueur 2
                    elif joueur.get_id() == 2:
                        if inputs[pygame.K_UP]:
                            input_vectors[joueur][1] -= 1
                        if inputs[pygame.K_DOWN]:
                            input_vectors[joueur][1] += 1

                # Comportement des ia
                else:
                    # Joueur sur la ligne rouge la plus proche du centre
                    if joueur.get_pos()[0] == 380:

                        # L'ia suit la carapace si elle se trouve devant elle
                        if self.carapace.get_pos()[0] > joueur.get_pos()[0]:
                            if joueur.get_pos()[1] < self.carapace.get_pos()[1] + 50:
                                input_vectors[joueur][1] += 1
                            elif joueur.get_pos()[1] > self.carapace.get_pos()[1] - 50:
                                input_vectors[joueur][1] -= 1

                        # Sinon l'ia s'éloigne le plus possible de la carapace
                        else:
                            if joueur.get_pos()[1] < self.carapace.get_pos()[1]:
                                input_vectors[joueur][1] -= 1
                            elif joueur.get_pos()[1] > self.carapace.get_pos()[1]:
                                input_vectors[joueur][1] += 1


                    # Joueur sur la ligne verte la plus proche du centre
                    elif joueur.get_pos()[0] == 832:

                        # L'ia suit la carapace si elle se trouve devant elle
                        if self.carapace.get_pos()[0] < joueur.get_pos()[0]:
                            if joueur.get_pos()[1] < self.carapace.get_pos()[1] + 50:
                                input_vectors[joueur][1] += 1
                            elif joueur.get_pos()[1] > self.carapace.get_pos()[1] - 50:
                                input_vectors[joueur][1] -= 1

                        # Sinon l'ia s'éloigne le plus possible de la carapace
                        else:
                            if joueur.get_pos()[1] < self.carapace.get_pos()[1]:
                                input_vectors[joueur][1] -= 1
                            elif joueur.get_pos()[1] > self.carapace.get_pos()[1]:
                                input_vectors[joueur][1] += 1


                    # Joueur sur la ligne la plus éloignée du centre (rouge et verte)
                    elif joueur.get_pos()[0] == 180 or joueur.get_pos()[0] == 1032:
                        # L'ia suit la carapace quoi qu'il arrive
                        if joueur.get_pos()[1] < self.carapace.get_pos()[1] + 50:
                            input_vectors[joueur][1] += 1
                        elif joueur.get_pos()[1] > self.carapace.get_pos()[1] - 50:
                            input_vectors[joueur][1] -= 1

            # Utilisation du moteur de jeu et mise à jour du temps passé
            self.game_engine(input_vectors, prev_time)
            prev_time = time.time()

            # Si la carapace rentre dans le but vert
            if self.carapace.get_pos()[0] > self.buts[1].get_pos()[0]:
                # Réinitialisation de la carapace
                self.carapace.reset()

                # Ajout du score pour l'équipe adverse + Son du sifflet
                self.score[0] += 1
                self.son_but.play()

            # Si la carapace rentre dans le but rouge
            elif self.carapace.get_pos()[0] < self.buts[0].get_pos()[0]:
                # Réinitialisation de la carapace
                self.carapace.reset()

                # Ajout du score pour l'équipe adverse + Son du sifflet
                self.score[1] += 1
                self.son_but.play()

            # Le parent s'occupe du timer
            super().during_game()

            # Mise à jour de l'écran et limite de fps
            pygame.display.flip()
            self.clock.tick(self.fps)

        # Lancement de l'affichage de fin (si le joueur n'a pas fermé la fenêtre)
        if not self.quit:

            # On immobilise la carapace
            self.carapace.set_direction([0, 0])

            self.end_game()


    def calculate_score(self) -> None:
        """
        Cette méthode permet de calculer les scores de chaque joueur.
        """

        # En cas d'égalité
        if self.score[0] == self.score[1]:
            # Personne ne gagne
            for joueur in self.joueurs:
                self.classement[joueur.get_perso()] = 0

        # Si l'équipe rouge gagne
        elif self.score[0] > self.score[1]:
            # Joueurs de l'équipe rouge
            self.classement[self.joueurs[0].get_perso()] = 1
            self.classement[self.joueurs[1].get_perso()] = 1

            # Joueurs de l'équipe verte
            self.classement[self.joueurs[2].get_perso()] = 0
            self.classement[self.joueurs[3].get_perso()] = 0

        # Si l'équipe verte gagne
        else:
            # Joueurs de l'équipe rouge
            self.classement[self.joueurs[0].get_perso()] = 0
            self.classement[self.joueurs[1].get_perso()] = 0

            # Joueurs de l'équipe verte
            self.classement[self.joueurs[2].get_perso()] = 1
            self.classement[self.joueurs[3].get_perso()] = 1

        # Le parent s'occupe de finir le mini-jeu
        super().calculate_score()