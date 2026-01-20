from vector import Vector
from objects import Sphere, Light

def load_scene(filename):
    """
    Charge une scène depuis un .txt.
    Format:
      SPHERE x y z radius r g b specular reflective
      LIGHT type intensity x y z
    """
    spheres = []
    lights = []

    print(f"Chargement de la scène depuis {filename}...")
    try:
        with open(filename, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if not parts or parts[0].startswith("#"):
                    continue

                cmd = parts[0].upper()

                if cmd == "SPHERE":
                    x, y, z, radius = map(float, parts[1:5])
                    r, g, b = map(int, parts[5:8])
                    specular = int(parts[8])
                    reflective = float(parts[9])
                    spheres.append(Sphere(Vector(x, y, z), radius, (r, g, b), specular, reflective))

                elif cmd == "LIGHT":
                    l_type = parts[1]
                    intensity = float(parts[2])
                    x, y, z = map(float, parts[3:6])
                    pos = Vector(x, y, z) if l_type != 'ambient' else None
                    lights.append(Light(l_type, intensity, pos))

        return spheres, lights

    except Exception as e:
        print(f"Erreur lecture fichier: {e}")
        return [], []


def save_ppm(filename, width, height, pixels):
    """Écrit une image PPM ASCII (P3)."""
    with open(filename, 'w') as f:
        f.write(f"P3\n{width} {height}\n255\n")
        for row in pixels:
            f.write(" ".join([f"{c[0]} {c[1]} {c[2]}" for c in row]) + "\n")
    print(f"Image sauvegardée sous {filename}")
