import math

class Vector:
    """Vecteur 3D minimal (x, y, z) avec opérations de base pour le ray tracing."""

    def __init__(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __truediv__(self, scalar):
        return Vector(self.x / scalar, self.y / scalar, self.z / scalar)

    def dot(self, other):
        """Produit scalaire (utile pour intersections et éclairage)."""
        return self.x * other.x + self.y * other.y + self.z * other.z

    def length(self):
        """Norme du vecteur."""
        return math.sqrt(self.dot(self))

    def normalize(self):
        """Renvoie un vecteur unitaire (même direction, norme 1)."""
        l = self.length()
        if l == 0:
            return Vector(0, 0, 0)
        return self / l
