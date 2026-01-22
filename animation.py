import math
import os

from vector import Vector
from io_scene import save_ppm
from raytracer import trace_ray, EPS

FRAMES_DIR = "frames"

def orbit_ellipse(center, a, b, angle_rad, y):
    """
    Calcule la position d'un point qui tourne sur une ellipse dans le plan XZ.

    Paramètres :
    - center (Vector) : le centre de l'ellipse
    - a (float) : rayon sur l'axe X
    - b (float) : rayon sur l'axe Z 
    - angle_rad (float) : angle en radians (0..2pi) qui avance à chaque frame
    - y (float) : hauteur constante (les sphères orbitantes restent au même niveau)

    Sens :
    - x = cos(t), z = sin(t) -> rotation anti-horaire si on regarde du dessus (axe Y).
    """
    x = center.x + a * math.cos(angle_rad)
    z = center.z + b * math.sin(angle_rad)
    return Vector(x, y, z)

def find_sphere_by_color(spheres, rgb):
    """
    Retrouve une sphère dans la liste en fonction de sa couleur.
    """
    for s in spheres:
        if s.color == rgb:
            return s
    return None

def render_image(width, height, camera_pos, spheres, lights, out_filename, fov=0.8, recursion_depth=3):
    """
    Rend une image et l'enregistre en PPM.

    - On parcourt chaque pixel (x, y) de l'image.
    - Pour chaque pixel, on calcule un rayon partant de la caméra.
    - On trace ce rayon dans la scène (trace_ray), qui renvoie une couleur.

    Caméra utilisée :
    - caméra fixe à camera_pos (0,0,0)
    - écran virtuel placé à z = 1
    - direction du rayon = (sx, sy, 1) puis normalisée

    fov :
    - Ici, ce n'est pas un "vrai" angle de champ en degrés,
      mais un facteur d'échelle.
    - Plus fov est grand, plus on "zoome out".
    """
    pixels = []

    aspect = width / height # ratio

    for y in range(height):
        row = []

        for x in range(width):
            sx = (2 * x / width - 1) * aspect * fov # 1 = droite 0 = centre -1 = gauche
            sy = (1 - 2 * y / height) * fov # 1 = haut 0 = centre -1 = bas

            direction = Vector(sx, sy, 1).normalize()

            color = trace_ray(
                camera_pos,
                direction,
                EPS,               # min_t : évite l'auto-intersection
                float('inf'),      # max_t : rayon "infini" pour la caméra
                spheres,
                lights,
                recursion_depth
            )

            row.append(color)

        pixels.append(row)

    # Une fois qu'on a tout les pixels on sauvegarde en PPM
    save_ppm(out_filename, width, height, pixels)

def run_animation(spheres, lights, num_frames=30, fov=0.8):
    """
    Génère une animation sous forme de suite d'images PPM.
        - Caméra fixe.
        - 3 sphères (jaune, verte, bleue) tournent autour de la sphère rouge.
        - La sphère rouge monte et descend.
    """
    width, height = 600, 600

    camera_pos = Vector(0, 0, 0)

    # Crée le dossier frames/ s'il n'existe pas déjà
    os.makedirs(FRAMES_DIR, exist_ok=True)

    # On récup les sphères qui doivent être animés
    red = find_sphere_by_color(spheres, (255, 0, 0))
    yellow = find_sphere_by_color(spheres, (255, 255, 0))
    green = find_sphere_by_color(spheres, (0, 255, 0))
    blue = find_sphere_by_color(spheres, (0, 128, 255))

    # Sécurité fallback
    if not all([red, yellow, green, blue]):
        print("Erreur: impossible de trouver les sphères rouge/jaune/verte/bleue.")
        print("Vérifie que les couleurs dans scene.txt sont exactement celles-ci.")
        return

    # position initiale de la sphère rouge
    red_base_x = red.center.x
    red_base_y = red.center.y
    red_base_z = red.center.z

    # params d'animation
    bob_amp = 0.35 # amplitude de la montée/descente de la rouge
    a = 2.2 # rayon ellipse axe X (largeur)
    b = 1.3 # rayon ellipse axe Z (profondeur)
    orbit_y = -0.2 # hauteur fixe des sphères orbitantes
    phase = 2 * math.pi / 3 # décalage de 120 (360/3) degré entre les 3 sphères

    # Génération des frames
    for i in range(1, num_frames + 1):
        # t varie de 0 à 2pi sur l'ensemble de l'animation
        t = 2 * math.pi * (i / num_frames)

        # y(t) = base_y + amplitude * sin(t)
        red.center = Vector(red_base_x, red_base_y + bob_amp * math.sin(t), red_base_z)
        c = red.center

        # Déplacement des 3 sphères
        yellow.center = orbit_ellipse(c, a, b, t + 0 * phase, orbit_y)
        green.center = orbit_ellipse(c, a, b, t + 1 * phase, orbit_y)
        blue.center = orbit_ellipse(c, a, b, t + 2 * phase, orbit_y)

        # Rendu d'une frame
        out_path = f"{FRAMES_DIR}/frame_{i}.ppm"
        render_image(
            width, height,
            camera_pos,
            spheres, lights,
            out_filename=out_path,
            fov=fov,
            recursion_depth=3
        )

        print(f"[{i}/{num_frames}] OK -> {out_path}")
