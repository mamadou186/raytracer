from vector import Vector
from objects import Sphere, Light


def load_scene(filename):
    """
    Charge une scène depuis un fichier texte (scene.txt).

    Format attendu (une instruction par ligne) :

    1) Sphère :
       SPHERE x y z radius r g b specular reflective

       Exemple :
       SPHERE 0 -1 6 0.8 255 0 0 500 0.2
         - centre = (0, -1, 6)
         - rayon = 0.8
         - couleur = (255, 0, 0)
         - specular = 500 (spot brillant)
         - reflective = 0.2 (léger miroir)

    2) Lumière :
       LIGHT type intensity x y z

       type ∈ { ambient, point, directional }

       - ambient :
         LIGHT ambient 0.2 0 0 0
         -> position ignorée (on met 0 0 0 par convention)

       - point :
         LIGHT point 0.6 2 2 0
         -> position (2,2,0)

       - directional :
         LIGHT directional 0.2 1 4 4
         -> direction (1,4,4) (pas une position !)
         
    Retour :
    - spheres : liste d'objets Sphere
    - lights  : liste d'objets Light
    """
    spheres = []
    lights = []

    print(f"Chargement de la scène depuis {filename}...")

    try:
        with open(filename, 'r') as f:
            for line in f:
                # On enlève les espaces et on découpe la ligne en "mots"
                parts = line.strip().split()

                # Ligne vide ou commentaire => on ignore
                if not parts or parts[0].startswith("#"):
                    continue

                # MAJ
                cmd = parts[0].upper()

                # Sphère
                if cmd == "SPHERE":
                    # x, y, z, radius en float
                    x, y, z, radius = map(float, parts[1:5])

                    # Couleur RGB en int
                    r, g, b = map(int, parts[5:8])

                    # Specular en int (-1 = mat)
                    specular = int(parts[8])

                    # coefficient de miroir en float(0..1)
                    reflective = float(parts[9])

                    spheres.append(
                        Sphere(
                            Vector(x, y, z),
                            radius,
                            (r, g, b),
                            specular,
                            reflective
                        )
                    )

                # Lumière
                elif cmd == "LIGHT":
                    l_type = parts[1] # ambient / point / directional
                    intensity = float(parts[2])

                    x, y, z = map(float, parts[3:6])

                    pos = Vector(x, y, z) if l_type != 'ambient' else None

                    lights.append(Light(l_type, intensity, pos))
                    
        return spheres, lights

    except Exception as e:
        print(f"Erreur lecture fichier: {e}")
        return [], []


def save_ppm(filename, width, height, pixels):
    """
    Écrit une image PPM.

    pixels :
    - liste de lignes
    - chaque ligne est une liste de tuples (r,g,b)
    - valeurs attendues entre 0 et 255
    """
    with open(filename, 'w') as f:
        # En-tête PPM
        f.write(f"P3\n{width} {height}\n255\n")

        for row in pixels:
            # On convertit chaque pixel en "r g b"
            f.write(" ".join([f"{c[0]} {c[1]} {c[2]}" for c in row]) + "\n")

    print(f"Image sauvegardée sous {filename}")