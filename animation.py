import math
import os
from vector import Vector
from io_scene import save_ppm
from raytracer import trace_ray, EPS

def orbit_ellipse(center, a, b, angle_rad, y):
    """Ellipse CCW dans le plan XZ autour de center."""
    x = center.x + a * math.cos(angle_rad)
    z = center.z + b * math.sin(angle_rad)
    return Vector(x, y, z)

def find_sphere_by_color(spheres, rgb):
    """Retrouve une sphère via sa couleur (robuste si ordre scene.txt change)."""
    for s in spheres:
        if s.color == rgb:
            return s
    return None

def render_image(width, height, camera_pos, spheres, lights, out_filename, fov=0.8, recursion_depth=3):
    """
    Rendu d'une image PPM.
    Caméra fixe à camera_pos, viewport implicite à z=1.
    """
    pixels = []
    aspect = width / height

    for y in range(height):
        row = []
        sy = (1 - 2 * y / height) * fov
        for x in range(width):
            sx = (2 * x / width - 1) * aspect * fov
            direction = Vector(sx, sy, 1).normalize()
            color = trace_ray(camera_pos, direction, EPS, float('inf'), spheres, lights, recursion_depth)
            row.append(color)
        pixels.append(row)

    save_ppm(out_filename, width, height, pixels)

def run_animation(spheres, lights, num_frames=30, fov=0.8):
    """
    - Caméra fixe
    - 3 sphères orbitent autour de la rouge (CCW)
    - la rouge monte/descend (sinus)
    """
    width, height = 600, 600
    camera_pos = Vector(0, 0, 0)
    os.makedirs("frames", exist_ok=True)

    red = find_sphere_by_color(spheres, (255, 0, 0))
    yellow = find_sphere_by_color(spheres, (255, 255, 0))
    green = find_sphere_by_color(spheres, (0, 255, 0))
    blue = find_sphere_by_color(spheres, (0, 128, 255))

    if not all([red, yellow, green, blue]):
        print("Erreur: impossible de trouver les sphères rouge/jaune/verte/bleue.")
        return

    red_base_x = red.center.x
    red_base_y = red.center.y
    red_base_z = red.center.z

    bob_amp = 0.35
    a = 2.2
    b = 1.3
    orbit_y = -0.2
    phase = 2 * math.pi / 3

    for i in range(1, num_frames + 1):
        t = 2 * math.pi * (i / num_frames)

        red.center = Vector(red_base_x, red_base_y + bob_amp * math.sin(t), red_base_z)
        c = red.center

        yellow.center = orbit_ellipse(c, a, b, t + 0 * phase, orbit_y)
        green.center  = orbit_ellipse(c, a, b, t + 1 * phase, orbit_y)
        blue.center   = orbit_ellipse(c, a, b, t + 2 * phase, orbit_y)

        render_image(width, height, camera_pos, spheres, lights,
                     out_filename=f"frames/frame_{i}.ppm",
                     fov=fov,
                     recursion_depth=3)
        print(f"[{i}/{num_frames}] OK")
