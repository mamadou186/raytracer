from vector import Vector

class Sphere:
    """
    Sphère rendue par ray tracing.
    - center: Vector
    - radius: float
    - color: (r, g, b)
    - specular: -1 mat ou puissance (ex: 500)
    - reflective: 0..1 (miroir)
    """
    def __init__(self, center, radius, color, specular, reflective):
        self.center = center
        self.radius = float(radius)
        self.color = color
        self.specular = int(specular)
        self.reflective = float(reflective)

class Light:
    """
    Lumière:
    - ambient: intensité uniquement
    - point: position + intensité
    - directional: direction + intensité (position stocke une direction)
    """
    def __init__(self, l_type, intensity, position=None):
        self.l_type = l_type
        self.intensity = float(intensity)
        self.position = position
