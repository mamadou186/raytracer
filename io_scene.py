from vector import Vector
from objects import Sphere, Light


def load_scene(filename):
    """
    Charge une scène depuis un fichier texte (scene.txt).

    Pourquoi un fichier texte ?
    - Les consignes demandent une scène "chargée depuis un fichier txt".
    - C'est simple à écrire/modifier sans toucher au code.
    - Ça permet de tester rapidement différentes configurations.

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

    Commentaires :
    - Les lignes vides et les lignes commençant par # sont ignorées.

    Retour :
    - spheres : liste d'objets Sphere
    - lights  : liste d'objets Light
    """
    spheres = []
    lights = []

    print(f"Chargement de la scène depuis {filename}...")

    try:
        # Ouverture du fichier de scène en lecture
        with open(filename, 'r') as f:
            for line in f:
                # On enlève les espaces et on découpe la ligne en "mots"
                parts = line.strip().split()

                # Ligne vide ou commentaire => on ignore
                if not parts or parts[0].startswith("#"):
                    continue

                # On met la commande en majuscule pour éviter les erreurs de casse
                cmd = parts[0].upper()

                # ---------------------------------------------------------
                # Définition d'une SPHERE
                # ---------------------------------------------------------
                if cmd == "SPHERE":
                    # On lit les 4 premiers paramètres comme des floats :
                    # x, y, z, radius
                    x, y, z, radius = map(float, parts[1:5])

                    # Couleur RGB en entiers (0..255)
                    r, g, b = map(int, parts[5:8])

                    # Specular : puissance de Phong (-1 = mat)
                    specular = int(parts[8])

                    # Reflective : coefficient de miroir (0..1)
                    reflective = float(parts[9])

                    # Création de l'objet Sphere et ajout à la liste
                    spheres.append(
                        Sphere(
                            Vector(x, y, z),
                            radius,
                            (r, g, b),
                            specular,
                            reflective
                        )
                    )

                # ---------------------------------------------------------
                # Définition d'une LIGHT
                # ---------------------------------------------------------
                elif cmd == "LIGHT":
                    l_type = parts[1]         # ambient / point / directional
                    intensity = float(parts[2])

                    # On lit x, y, z même si ambiant (même si ça ne sert pas),
                    # pour garder un format de ligne uniforme.
                    x, y, z = map(float, parts[3:6])

                    # Pour la lumière ambiante, on n'a pas besoin de position/direction.
                    # Pour point/directional, on stocke un Vector(x,y,z).
                    pos = Vector(x, y, z) if l_type != 'ambient' else None

                    lights.append(Light(l_type, intensity, pos))

                # Si une commande inconnue est dans le fichier, on pourrait :
                # - ignorer
                # - ou afficher un warning
                # Ici on ignore silencieusement pour rester simple.

        # Retourne la scène chargée
        return spheres, lights

    except Exception as e:
        # En cas d'erreur (fichier manquant, mauvaise ligne, etc.)
        print(f"Erreur lecture fichier: {e}")
        return [], []


def save_ppm(filename, width, height, pixels):
    """
    Écrit une image PPM ASCII (format P3).

    Pourquoi PPM ?
    - C'est le format recommandé par les consignes (simple à implémenter).
    - Pas de compression, pas de librairies nécessaires.
    - C'est juste :
      * un en-tête
      * puis les valeurs RGB en texte

    Format PPM P3 :
      P3
      <width> <height>
      255
      r g b r g b r g b ...

    pixels :
    - liste de lignes
    - chaque ligne est une liste de tuples (r,g,b)
    - valeurs attendues entre 0 et 255
    """
    with open(filename, 'w') as f:
        # En-tête PPM
        f.write(f"P3\n{width} {height}\n255\n")

        # Corps de l'image : une ligne par rangée de pixels
        for row in pixels:
            # On convertit chaque pixel en "r g b"
            f.write(" ".join([f"{c[0]} {c[1]} {c[2]}" for c in row]) + "\n")

    print(f"Image sauvegardée sous {filename}")