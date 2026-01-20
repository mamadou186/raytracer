from vector import Vector

class Sphere:
    """
    Représente une sphère dans la scène 3D.

    Pourquoi uniquement des sphères ?
    - La sphère est l'objet géométrique le plus simple à intersecter avec un rayon.
    - L'équation rayon-sphère est analytique (équation du second degré).
    - On peut détourner des sphères de très grand rayon pour simuler :
      - un sol
      - des murs
    => Cela permet de construire une scène complète sans gérer d'autres primitives.

    Attributs :
    - center (Vector) :
        Position du centre de la sphère dans l'espace.
    - radius (float) :
        Rayon de la sphère.
    - color (tuple[int, int, int]) :
        Couleur RGB (0–255) utilisée pour la couleur locale.
    - specular (int) :
        Paramètre de brillance spéculaire :
        * -1  → surface mate (pas de reflet spéculaire)
        * > 0 → surface brillante (exposant de Phong)
    - reflective (float) :
        Coefficient de réflexion :
        * 0.0 → pas de miroir
        * 1.0 → miroir parfait
        * entre 0 et 1 → mélange couleur locale / réflexion
    """

    def __init__(self, center, radius, color, specular, reflective):
        # Le centre est un vecteur 3D
        self.center = center

        # Le rayon est converti en float pour éviter
        # toute ambiguïté dans les calculs
        self.radius = float(radius)

        # Couleur RGB stockée telle quelle
        # (les calculs de lumière s'appliquent ensuite dessus)
        self.color = color

        # Puissance spéculaire (Phong)
        # -1 désactive complètement le calcul spéculaire
        self.specular = int(specular)

        # Coefficient de réflexion (0..1)
        # Utilisé lors de la récursion dans trace_ray
        self.reflective = float(reflective)


class Light:
    """
    Représente une source de lumière dans la scène.

    Trois types de lumière sont gérés :
    1) 'ambient'
       - Lumière uniforme
       - Ne dépend ni de la position ni de l'orientation
       - Sert à éviter des zones complètement noires

    2) 'point'
       - Source ponctuelle située à une position donnée
       - La lumière arrive depuis un point précis

    3) 'directional'
       - Source infiniment lointaine
       - Tous les rayons lumineux sont parallèles
       - La position stocke ici une *direction*

    Attributs :
    - l_type (str) :
        Type de la lumière ('ambient', 'point', 'directional')
    - intensity (float) :
        Intensité de la lumière (facteur multiplicatif)
    - position (Vector | None) :
        * None pour ambient
        * position pour point
        * direction pour directional
    """

    def __init__(self, l_type, intensity, position=None):
        # Type de lumière (choisit le comportement dans le calcul d'éclairage)
        self.l_type = l_type

        # Intensité (souvent entre 0 et 1, mais pas strictement limité)
        self.intensity = float(intensity)

        # Position ou direction selon le type
        # - ambient     → None
        # - point       → position dans l'espace
        # - directional → direction de la lumière
        self.position = position
