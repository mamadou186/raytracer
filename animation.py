import math
import os

from vector import Vector
from io_scene import save_ppm
from raytracer import trace_ray, EPS

# Dossier où on écrit les images PPM de l'animation.
# (On garde ça en constante pour éviter de le répéter partout et rendre le code clair.)
FRAMES_DIR = "frames"


def orbit_ellipse(center, a, b, angle_rad, y):
    """
    Calcule la position d'un point qui tourne sur une ellipse dans le plan XZ.

    But :
    - On veut faire "tourner" des sphères autour de la sphère rouge.
    - Au lieu de bouger la caméra (plus complexe à expliquer),
      on déplace les objets suivant une trajectoire paramétrée.
    - Une ellipse donne un mouvement "piste d’athlétisme" (plus sympa qu’un cercle).

    Paramètres :
    - center (Vector) : le centre de l'ellipse (ici, la sphère rouge)
    - a (float) : rayon sur l'axe X (largeur de l'ellipse)
    - b (float) : rayon sur l'axe Z (profondeur de l'ellipse)
    - angle_rad (float) : angle en radians (0..2π) qui avance à chaque frame
    - y (float) : hauteur constante (les sphères orbitantes restent au même niveau)

    Sens :
    - x = cos(t), z = sin(t) -> rotation anti-horaire (CCW) si on regarde du dessus (axe Y).
    """
    x = center.x + a * math.cos(angle_rad)
    z = center.z + b * math.sin(angle_rad)
    return Vector(x, y, z)


def find_sphere_by_color(spheres, rgb):
    """
    Retrouve une sphère dans la liste en fonction de sa couleur.

    Pourquoi cette méthode ?
    - Si on dépend de l'ordre des sphères dans scene.txt, le code devient fragile :
      dès qu'on ajoute une sphère (mur, sol, etc.), l'indice change.
    - En utilisant la couleur, on repère nos "sphères animées" facilement.

    Limite :
    - Il faut que les couleurs soient EXACTEMENT celles attendues dans scene.txt.
    """
    for s in spheres:
        if s.color == rgb:
            return s
    return None


def render_image(width, height, camera_pos, spheres, lights, out_filename, fov=0.8, recursion_depth=3):
    """
    Rend une image et l'enregistre en PPM.

    Principe :
    - On parcourt chaque pixel (x, y) de l'image.
    - Pour chaque pixel, on calcule un rayon partant de la caméra.
    - On trace ce rayon dans la scène (trace_ray), qui renvoie une couleur.

    Caméra utilisée (simple volontairement) :
    - caméra fixe à camera_pos (souvent (0,0,0))
    - écran virtuel (viewport) placé à z = 1
    - direction du rayon = (sx, sy, 1) puis normalisée

    fov :
    - Ici, ce n'est pas un "vrai" angle de champ en degrés,
      mais un facteur d'échelle.
    - Plus fov est grand, plus on "zoome out" (on voit plus large).
    """
    pixels = []

    # aspect ratio : évite que l'image soit étirée si width != height
    aspect = width / height

    # Boucle sur tous les pixels de l'image
    for y in range(height):
        row = []

        # sy : coordonnée écran normalisée dans [-fov, +fov]
        # y=0 -> haut de l'écran, y=height -> bas de l'écran
        sy = (1 - 2 * y / height) * fov

        for x in range(width):
            # sx : coordonnée écran normalisée dans [-fov, +fov]
            # x=0 -> gauche, x=width -> droite
            sx = (2 * x / width - 1) * aspect * fov

            # Construction de la direction du rayon pour ce pixel
            # On prend un viewport à z=1, puis on normalise.
            direction = Vector(sx, sy, 1).normalize()

            # trace_ray renvoie une couleur RGB (0..255) pour ce pixel
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

    # Une fois tous les pixels calculés, on sauvegarde en PPM
    save_ppm(out_filename, width, height, pixels)


def run_animation(spheres, lights, num_frames=30, fov=0.8):
    """
    Génère une animation sous forme de suite d'images PPM.

    Concept de l'animation (bonus) :
    - Caméra fixe.
    - 3 sphères (jaune, verte, bleue) tournent autour de la sphère rouge.
    - La sphère rouge "bob" (monte/descend) avec une sinusoïde.

    Output :
    - frames/frame_1.ppm ... frames/frame_N.ppm

    Note :
    - On n'encode pas directement un GIF pour rester 100% "Python natif" et ne rien installer.
    - La conversion en GIF peut être faite ensuite via un outil externe si besoin.
    """
    width, height = 600, 600

    # Position de caméra : fixe et simple
    camera_pos = Vector(0, 0, 0)

    # Crée le dossier frames/ s'il n'existe pas déjà
    os.makedirs(FRAMES_DIR, exist_ok=True)

    # --- Retrouver les 4 sphères animées par leur couleur ---
    # (Ça évite de dépendre de l'ordre dans scene.txt)
    red = find_sphere_by_color(spheres, (255, 0, 0))
    yellow = find_sphere_by_color(spheres, (255, 255, 0))
    green = find_sphere_by_color(spheres, (0, 255, 0))
    blue = find_sphere_by_color(spheres, (0, 128, 255))

    if not all([red, yellow, green, blue]):
        print("Erreur: impossible de trouver les sphères rouge/jaune/verte/bleue.")
        print("Vérifie que les couleurs dans scene.txt sont exactement celles-ci.")
        return

    # --- Sauvegarder la position de base de la sphère rouge ---
    # On veut qu'elle monte/descende autour de sa position initiale.
    red_base_x = red.center.x
    red_base_y = red.center.y
    red_base_z = red.center.z

    # =========================================================
    # Paramètres d'animation (faciles à modifier)
    # =========================================================
    bob_amp = 0.35            # amplitude de la montée/descente de la rouge
    a = 2.2                   # rayon ellipse axe X (largeur)
    b = 1.3                   # rayon ellipse axe Z (profondeur)
    orbit_y = -0.2            # hauteur fixe des sphères orbitantes
    phase = 2 * math.pi / 3   # décalage de 120° entre les 3 sphères

    # Génération des frames
    # On commence à 1 pour coller au nom frame_1.ppm
    for i in range(1, num_frames + 1):
        # t varie de 0 à 2π sur l'ensemble de l'animation
        t = 2 * math.pi * (i / num_frames)

        # --- Faire "bob" la sphère rouge ---
        # y(t) = base_y + amplitude * sin(t)
        red.center = Vector(red_base_x, red_base_y + bob_amp * math.sin(t), red_base_z)

        # Le centre de l'orbite est la sphère rouge (qui bouge verticalement)
        c = red.center

        # --- Déplacer les 3 sphères orbitantes ---
        # Même sens (anti-horaire), mais décalées de phase pour qu'elles soient espacées.
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
