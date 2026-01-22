import math


class Vector:
    """
    Représente un vecteur 3D (x, y, z).

    - On stocke x, y, z en float pour éviter les problèmes de division entière.
    - Les opérations retournent de NOUVEAUX vecteurs (on ne modifie pas l'objet courant).
    """

    def __init__(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __add__(self, other):
        """
        Addition vectorielle : v + w

        - Calcul d'un point sur un rayon : P = O + t * D
        - Déplacement/combinaison de vecteurs.
        """
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        """
        Soustraction vectorielle : v - w

        - Vecteur entre deux points : (point - centre_sphere)
        - Direction vers la lumière : (light_pos - point)
        """
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        """
        Multiplication par un scalaire : v * k

        - t * D dans l'équation du rayon P(t) = O + tD
        - Intensité / coefficients
        """
        return Vector(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar):
        """
        Multiplication à gauche : k * v
        """
        return self.__mul__(scalar)

    def __truediv__(self, scalar):
        """
        Division par un scalaire : v / k

        - Normalisation : v_normalisé = v / ||v||
        """
        return Vector(self.x / scalar, self.y / scalar, self.z / scalar)

    def dot(self, other):
        """
        Produit scalaire (dot product) : v · w

        - Intersection rayon-sphère :
           on développe des expressions du type (O - C) · D
        - Éclairage diffuse :
           intensité ∝ max(0, N · L)
        - Éclairage specular :
           intensité ∝ max(0, R · V)^p
        """
        return self.x * other.x + self.y * other.y + self.z * other.z

    def length(self):
        """
        Norme du vecteur : ||v||

        ||v|| = sqrt(v · v)

        - Calculer la distance
        - Normalisation
        """
        return math.sqrt(self.dot(self))

    def normalize(self):
        """
        Renvoie un vecteur unitaire.

        - Si le vecteur est nul (longueur = 0), on renvoie (0,0,0)
          pour éviter une division par zéro.
        """
        l = self.length()
        if l == 0:
            return Vector(0, 0, 0)
        return self / l
