import math
from vector import Vector

EPS = 0.001 # petit décalage utilisé pour éviter l'auto-intersection dû aux imprécisions numériques des float


def intersect_ray_sphere(origin, direction, sphere):
    """
    Calcule la ou les distances d'intersections entre un rayon et une sphère.

    Rayon :
        P(t) = O + tD
        - O : origin (Vector), point de départ du rayon
        - D : direction (Vector), direction du rayon
        - t : paramètre réel

    Sphère :
        ||P - C||^2 = r^2
        - C : center de la sphère
        - r : rayon

    On remplace P(t) dans l'équation de la sphère :
        ||(O + tD) - C||^2 = r^2
    => équation du second degré en t : at^2 + bt + c = 0

    Retour :
        (t1, t2) : les deux solutions potentielles.
        Si pas d'intersection, on renvoie (inf, inf).

    Important :
    - t peut être négatif (intersection "derrière" la caméra), on filtrera plus tard
      avec min_t / max_t.
    """
    # co = vecteur du centre de la sphère vers l'origine du rayon (O - C)
    co = origin - sphere.center

    # Coefficients de l'équation at^2 + bt + c = 0
    a = direction.dot(direction)

    # b = 2 * (O - C)·D
    b = 2 * co.dot(direction)

    # c = (O - C)·(O - C) - r^2
    c = co.dot(co) - sphere.radius * sphere.radius

    # Discriminant disc = b^2 - 4ac
    # - Si disc < 0 : pas de solution réelle = pas d'intersection
    disc = b * b - 4 * a * c
    if disc < 0:
        return float('inf'), float('inf')

    sqrt_disc = math.sqrt(disc)

    # Deux solutions :
    # t1 = (-b + sqrt(Δ)) / (2a)
    # t2 = (-b - sqrt(Δ)) / (2a)
    t1 = (-b + sqrt_disc) / (2 * a)
    t2 = (-b - sqrt_disc) / (2 * a)

    return t1, t2


def closest_intersection(origin, direction, min_t, max_t, spheres):
    """
    Trouve l'objet le plus proche intersecté par un rayon.

    Paramètres :
    - origin, direction : rayon (O, D)
    - min_t, max_t : intervalle de validité pour t
    - spheres : liste des sphères de la scène

    Retour :
    - (closest_sphere, closest_t)
      * closest_sphere = None si rien n'est touché
    """
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
    Calcule l'intensité lumineuse au point d'impact.

    Modèle d'éclairage utilisé :
    1) Ambient
    2) Diffuse
    3) Spéculaire :

    Ombres :
    - Pour chaque lumière non ambiante, on lance un "shadow ray"
      du point vers la lumière.
    - Si ce rayon touche un objet avant d'atteindre la lumière,
      alors la lumière est bloquée.

    Retour :
    - intensity (float), généralement entre 0 et 1 (mais on clamp ensuite).
    """
    intensity = 0.0

    # Ambient toujours présente
    for light in lights:
        if light.l_type == 'ambient':
            intensity += light.intensity
            continue

        if light.l_type == 'point':
            l_vec = light.position - point
            t_max = 1.0

        else:  # 'directional'
            l_vec = light.position
            t_max = float('inf')

        # Ombres
        shadow_origin = point + normal * EPS

        # Si on touche une sphère entre le point et la lumière = ombre
        shadow_sphere, _ = closest_intersection(
            shadow_origin,
            l_vec,
            EPS,
            t_max,
            spheres
        )
        if shadow_sphere is not None:
            continue # On ignore la lumière

        # Diffuse
        l_dir = l_vec.normalize()

        n_dot_l = normal.dot(l_dir) # 1 : face à la lumière 0 : perpendiculaire < 0 : on ignore
        if n_dot_l > 0:
            intensity += light.intensity * n_dot_l

        # Spéculaire
        if specular != -1:
            # Calcul du vecteur réfléchi de la lumière autour de la normale
            r_vec = (2 * normal * normal.dot(l_dir) - l_dir).normalize()

            # direction vers la caméra
            v_dir = view.normalize()

            r_dot_v = r_vec.dot(v_dir) # alignement avec le rayon réfléchi
            if r_dot_v > 0:
                intensity += light.intensity * (r_dot_v ** specular) # 1 : parfait alignement 0 : perpendiculaire <0 : on ignore

    return intensity


def trace_ray(origin, direction, min_t, max_t, spheres, lights, recursion_depth):
    """
    Trace un rayon et retourne une couleur RGB.

    1) Trouver l'objet le plus proche touché (closest_intersection)
       - si aucun => couleur de fond (noir)

    2) Calculer le point d'impact P et la normale N.
       - normale sphère : N = (P - C) normalisé

    3) Calculer la couleur locale via l'éclairage (compute_lighting).
       - ça donne la couleur "sans miroir"

    4) Si l'objet est réfléchissant et qu'il reste de la récursion :
       - calculer la direction du rayon réfléchi
       - lancer trace_ray récursivement
       - mélanger couleur locale + couleur réfléchie selon reflective

    recursion_depth :
    - sert à limiter le nombre de rebonds (sinon boucle infinie potentielle).
    - plus c'est grand, plus c'est réaliste mais plus le calcul est lent.
    """
    sphere, t = closest_intersection(origin, direction, min_t, max_t, spheres)

    if sphere is None:
        return (0, 0, 0)

    # Point d'intersection P
    point = origin + direction * t

    # Sphère : N = (P - C) normalisé
    normal = (point - sphere.center).normalize()

    # Direction vers la caméra opposé de D
    view = (-1) * direction

    # Eclairage
    lighting = compute_lighting(point, normal, view, sphere.specular, spheres, lights)

    # On clamp l'intensité pour éviter des couleurs > 255
    lighting = max(0.0, min(1.0, lighting))

    local_color = (
        sphere.color[0] * lighting,
        sphere.color[1] * lighting,
        sphere.color[2] * lighting
    )

    r = sphere.reflective
    # Si objet n'est pas miroir ou nb de recursion atteint on s'arrête
    if recursion_depth <= 0 or r <= 0:
        return (
            min(255, int(local_color[0])),
            min(255, int(local_color[1])),
            min(255, int(local_color[2]))
        )

    # Rayon réfléchi
    # R = 2N(N·V) - V
    reflected_dir = (2 * normal * normal.dot(view) - view).normalize()

    # Origine du rayon réfléchi
    reflect_origin = point + normal * EPS

    # Récursion
    reflected_color = trace_ray(
        reflect_origin,
        reflected_dir,
        EPS,
        float('inf'),
        spheres,
        lights,
        recursion_depth - 1
    )

    # Mélange couleur locale / réflexion
    # 0 = local 1 = reflet
    final_r = local_color[0] * (1 - r) + reflected_color[0] * r
    final_g = local_color[1] * (1 - r) + reflected_color[1] * r
    final_b = local_color[2] * (1 - r) + reflected_color[2] * r

    return (
        min(255, int(final_r)),
        min(255, int(final_g)),
        min(255, int(final_b))
    )