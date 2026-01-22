from vector import Vector

class Sphere:
    """
    Représente une sphère dans la scène 3D.

    Attributs :
    - center (Vector) :
        Position du centre de la sphère dans l'espace.
    - radius (float) :
        Rayon de la sphère.
    - color (tuple[int, int, int]) :
        Couleur RGB (0–255) utilisée pour la couleur locale.
    - specular (int) :
        Paramètre de brillance spéculaire :
        * -1  → surface mate
        * > 0 → surface brillante
    - reflective (float) :
        Coefficient de réflexion :
        * 0.0 → pas de miroir
        * 1.0 → miroir parfait
        * entre 0 et 1 → mélange couleur locale / réflexion
    """

    def __init__(self, center, radius, color, specular, reflective):
        self.center = center
        self.radius = float(radius)
        self.color = color
        self.specular = int(specular)
        self.reflective = float(reflective)


class Light:
    """
    Représente une source de lumière dans la scène.

    Attributs :
    - l_type (str) :
        Type de la lumière ('ambient', 'point', 'directional')
    - intensity (float) :
        Intensité de la lumière
    - position (Vector | None) :
        * None pour ambient
        * position pour point
        * direction pour directional
    """

    def __init__(self, l_type, intensity, position=None):
        self.l_type = l_type
        self.intensity = float(intensity)
        self.position = position
