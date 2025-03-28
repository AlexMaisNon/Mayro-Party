#Projet : Mayro Party
#Auteurs : Hinata Bouaziz, Antoine Desrues, Alexandre Guillaume, Matisse Moreau

# ------/ Importations des bibliothèques \------

import pygame
import socket

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

# ------/ Classes utiliatires \------

# Classe du réseau
class Network:
    def __init__(self, adresse_serveur: str, pseudo: str):
        """
        Constructeur de la classe Network.
        """


        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.adresse_serveur = adresse_serveur
        self.port = 5555
        self.serveur = (self.adresse_serveur, self.port)
        self.adresse_client = self.connect()
        self.client.send(str.encode(pseudo))
        print("Connecté au serveur !")


    def connect(self) -> str:
        """
        Cette fonction permet de se connecter au serveur.
        """

        # On se connecte en attendant une réponse du serveur
        self.client.connect(self.serveur)
        return self.client.recv(2048).decode()


    def send(self, data: str) -> str:
        """
        Cette fonction permet d'envoyer des requêtes au serveur.
        """

        try:
            self.client.send(str.encode(data))
            reply = self.client.recv(2048).decode()
            return reply
        except socket.error as e:
            return str(e)
