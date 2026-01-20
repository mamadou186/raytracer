import math
from vector import Vector

# Petit epsilon pour éviter l'auto-intersection (ombres/reflets)
EPS = 0.001

def intersect_ray_sphere(origin, direction, sphere):
    """
    Intersection rayon-sphère.
    Rayon: P(t) = O + tD
    Sphère: ||P - C||^2 = r^2
    => équation du 2nd degré en t.
    """
    co = origin - sphere.center
    a = direction.dot(direction)
    b = 2 * co.dot(direction)
    c = co.dot(co) - sphere.radius * sphere.radius

    disc = b*b - 4*a*c
    if disc < 0:
        return float('inf'), float('inf')

    sqrt_disc = math.sqrt(disc)
    t1 = (-b + sqrt_disc) / (2*a)
    t2 = (-b - sqrt_disc) / (2*a)
    return t1, t2


def closest_intersection(origin, direction, min_t, max_t, spheres):
    """Renvoie (sphère la plus proche, t associé) dans [min_t, max_t]."""
    closest_t = float('inf')
    closest_sphere = None

    for s in spheres:
        t1, t2 = intersect_ray_sphere(origin, direction, s)

        if min_t < t1 < max_t and t1 < closest_t:
            closest_t = t1
            closest_sphere = s
        if min_t < t2 < max_t and t2 < closest_t:
            closest_t = t2
            closest_sphere = s

    return closest_sphere, closest_t


def compute_lighting(point, normal, view, specular, spheres, lights):
    """
    Calcule l'intensité lumineuse au point:
    - ambient
    - diffuse Lambert: max(0, N·L)
    - specular (Phong): max(0, R·V)^p
    + gestion des ombres par shadow ray.
    """
    intensity = 0.0

    for light in lights:
        if light.l_type == 'ambient':
            intensity += light.intensity
            continue

        if light.l_type == 'point':
            l_vec = light.position - point
            t_max = 1.0  # car on garde l_vec non normalisé pour l'ombre
        else:  # directional
            l_vec = light.position
            t_max = float('inf')

        # Ombres : vérifier si un objet bloque la lumière
        shadow_origin = point + normal * EPS
        shadow_sphere, _ = closest_intersection(shadow_origin, l_vec, EPS, t_max, spheres)
        if shadow_sphere is not None:
            continue

        # Diffuse
        l_dir = l_vec.normalize()
        n_dot_l = normal.dot(l_dir)
        if n_dot_l > 0:
            intensity += light.intensity * n_dot_l

        # Spéculaire
        if specular != -1:
            r_vec = (2 * normal * normal.dot(l_dir) - l_dir).normalize()
            v_dir = view.normalize()
            r_dot_v = r_vec.dot(v_dir)
            if r_dot_v > 0:
                intensity += light.intensity * (r_dot_v ** specular)

    return intensity


def trace_ray(origin, direction, min_t, max_t, spheres, lights, recursion_depth):
    """
    Lance un rayon et retourne une couleur (r,g,b).
    - Trouve l'intersection la plus proche.
    - Calcule la couleur locale (éclairage).
    - Si l'objet est réfléchissant, calcule un rayon réfléchi récursif.
    """
    sphere, t = closest_intersection(origin, direction, min_t, max_t, spheres)
    if sphere is None:
        return (0, 0, 0)

    point = origin + direction * t
    normal = (point - sphere.center).normalize()
    view = (-1) * direction

    lighting = compute_lighting(point, normal, view, sphere.specular, spheres, lights)
    lighting = max(0.0, min(1.0, lighting))

    local_color = (
        sphere.color[0] * lighting,
        sphere.color[1] * lighting,
        sphere.color[2] * lighting
    )

    r = sphere.reflective
    if recursion_depth <= 0 or r <= 0:
        return (min(255, int(local_color[0])),
                min(255, int(local_color[1])),
                min(255, int(local_color[2])))

    reflected_dir = (2 * normal * normal.dot(view) - view).normalize()
    reflect_origin = point + normal * EPS
    reflected_color = trace_ray(reflect_origin, reflected_dir, EPS, float('inf'),
                                spheres, lights, recursion_depth - 1)

    final_r = local_color[0] * (1 - r) + reflected_color[0] * r
    final_g = local_color[1] * (1 - r) + reflected_color[1] * r
    final_b = local_color[2] * (1 - r) + reflected_color[2] * r

    return (min(255, int(final_r)),
            min(255, int(final_g)),
            min(255, int(final_b)))
