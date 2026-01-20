import math


class Vector:
    """
    Représente un vecteur 3D (x, y, z).

    Pourquoi on en a besoin dans un ray tracer ?
    - Un "rayon" (ray) est défini par une origine O et une direction D.
      On manipule donc énormément des vecteurs.
    - Les positions des objets (centres de sphères), les directions vers les lumières,
      les normales aux surfaces, etc. sont toutes des vecteurs.
    - Les calculs clés (intersection rayon-sphère, éclairage) reposent sur
      le produit scalaire et la normalisation.

    Convention :
    - On stocke x, y, z en float pour éviter les problèmes de division entière.
    - Les opérations retournent de NOUVEAUX vecteurs (on ne modifie pas l'objet courant).
    """

    def __init__(self, x, y, z):
        # On convertit en float pour garantir un comportement cohérent
        # lors des divisions et des calculs mathématiques.
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    # --------- Opérations "mathématiques" de base ---------

    def __add__(self, other):
        """
        Addition vectorielle : v + w

        Utilisation typique dans le ray tracer :
        - Calcul d'un point sur un rayon : P = O + t * D
        - Déplacement/combinaison de vecteurs.
        """
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        """
        Soustraction vectorielle : v - w

        Utilisation typique :
        - Vecteur entre deux points : (point - centre_sphere)
        - Direction vers la lumière : (light_pos - point)
        """
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        """
        Multiplication par un scalaire : v * k

        Utilisation typique :
        - t * D dans l'équation du rayon P(t) = O + tD
        - Intensité / coefficients
        """
        return Vector(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar):
        """
        Multiplication "à gauche" : k * v

        Python appelle __rmul__ quand on fait "2 * v" (et pas "v * 2").
        Ça évite de devoir toujours écrire v * 2.
        """
        return self.__mul__(scalar)

    def __truediv__(self, scalar):
        """
        Division par un scalaire : v / k

        Utilisation typique :
        - Normalisation : v_normalisé = v / ||v||
        """
        return Vector(self.x / scalar, self.y / scalar, self.z / scalar)

    # --------- Outils géométriques ---------

    def dot(self, other):
        """
        Produit scalaire (dot product) : v · w

        Utilisation dans le ray tracer :
        1) Intersection rayon-sphère :
           on développe des expressions du type (O - C) · D
        2) Éclairage diffus (Lambert) :
           intensité ∝ max(0, N · L)
        3) Éclairage spéculaire (Phong) :
           intensité ∝ max(0, R · V)^p
        """
        return self.x * other.x + self.y * other.y + self.z * other.z

    def length(self):
        """
        Norme (longueur) du vecteur : ||v||

        ||v|| = sqrt(v · v)

        Utilisation :
        - Calculer la distance (via un vecteur différence)
        - Normalisation (obtenir un vecteur unitaire)
        """
        return math.sqrt(self.dot(self))

    def normalize(self):
        """
        Renvoie un vecteur unitaire (même direction, norme 1).

        Pourquoi normaliser ?
        - Beaucoup de formules (éclairage, réflexion) supposent des vecteurs unitaires.
        - Ça stabilise les calculs (par ex. N·L devient directement cos(theta)).

        Cas particulier :
        - Si le vecteur est nul (longueur = 0), on renvoie (0,0,0)
          pour éviter une division par zéro.
        """
        l = self.length()
        if l == 0:
            return Vector(0, 0, 0)
        return self / l
