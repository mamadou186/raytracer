import math
from vector import Vector

# =========================================================
# raytracer.py
#
# Ce fichier contient le "coeur" du ray tracer :
# - intersection rayon / sphère
# - sélection de l'objet le plus proche touché par un rayon
# - calcul de la lumière au point d'impact (ambient + diffuse + specular)
# - gestion des ombres via un "shadow ray"
# - gestion des reflets via récursion (rayon réfléchi)
# =========================================================

# EPS ("epsilon") : petit décalage utilisé pour éviter l'auto-intersection.
#
# Problème :
# - Quand on calcule un point d'intersection P sur une sphère,
#   puis qu'on lance un nouveau rayon depuis P (ombre ou réflexion),
#   on risque de retoucher immédiatement la même sphère à cause des
#   imprécisions des floats (effet "shadow acne" / points noirs).
#
# Solution :
# - On décale légèrement le point d'origine du nouveau rayon le long de la normale :
#     P' = P + EPS * N
EPS = 0.001


def intersect_ray_sphere(origin, direction, sphere):
    """
    Calcule l'intersection entre un rayon et une sphère.

    Rayon :
        P(t) = O + tD
        - O : origin (Vector), point de départ du rayon
        - D : direction (Vector), direction du rayon (souvent normalisée)
        - t : paramètre réel (distance "le long" du rayon)

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
    #
    # a = D·D (si D est normalisé, a = 1, mais on ne suppose pas forcément)
    a = direction.dot(direction)

    # b = 2 * (O - C)·D
    b = 2 * co.dot(direction)

    # c = (O - C)·(O - C) - r^2
    c = co.dot(co) - sphere.radius * sphere.radius

    # Discriminant Δ = b^2 - 4ac
    # - Si Δ < 0 : pas de solution réelle => pas d'intersection
    disc = b * b - 4 * a * c
    if disc < 0:
        return float('inf'), float('inf')

    sqrt_disc = math.sqrt(disc)

    # Deux solutions :
    # t1 = (-b + sqrt(Δ)) / (2a)
    # t2 = (-b - sqrt(Δ)) / (2a)
    #
    # Note : t2 est souvent la plus petite, mais on ne suppose rien.
    t1 = (-b + sqrt_disc) / (2 * a)
    t2 = (-b - sqrt_disc) / (2 * a)

    return t1, t2


def closest_intersection(origin, direction, min_t, max_t, spheres):
    """
    Trouve l'objet le plus proche intersecté par un rayon.

    Pourquoi on fait ça ?
    - Un rayon peut toucher plusieurs sphères.
    - Ce qui compte pour l'image, c'est la première surface rencontrée
      (la plus proche dans la direction du rayon).

    Paramètres :
    - origin, direction : rayon (O, D)
    - min_t, max_t : intervalle de validité pour t
      * min_t sert à ignorer l'auto-intersection et les t trop petits
      * max_t sert par exemple pour les shadow rays (lumière ponctuelle)
    - spheres : liste des sphères de la scène

    Retour :
    - (closest_sphere, closest_t)
      * closest_sphere = None si rien n'est touché
    """
    closest_t = float('inf')
    closest_sphere = None

    for s in spheres:
        t1, t2 = intersect_ray_sphere(origin, direction, s)

        # On garde les t qui sont dans l'intervalle et on prend le plus petit.
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

    Modèle d'éclairage utilisé (classique) :
    1) Ambient :
       - Une lumière "uniforme" qui éclaire tout pareil
       - évite les zones totalement noires

    2) Diffuse (Lambert) :
       - dépend de l'angle entre la normale N et la direction de lumière L
       - intensité ∝ max(0, N·L)

    3) Spéculaire (Phong) :
       - "spot brillant" sur les surfaces lisses
       - intensité ∝ max(0, R·V)^p
         où R = direction réfléchie de la lumière, V = direction vers la caméra
         p = puissance spéculaire (plus grand => spot plus petit et plus intense)

    Ombres :
    - Pour chaque lumière non ambiante, on lance un "shadow ray"
      du point vers la lumière.
    - Si ce rayon touche un objet avant d'atteindre la lumière,
      alors la lumière est bloquée (point dans l'ombre pour cette lumière).

    Retour :
    - intensity (float), généralement entre 0 et 1 (mais on clamp ensuite).
    """
    intensity = 0.0

    for light in lights:
        # --- Lumière ambiante : ajout direct ---
        if light.l_type == 'ambient':
            intensity += light.intensity
            continue

        # --- Construire le vecteur vers la lumière ---
        #
        # Pour une lumière point :
        #   L = light_pos - point
        #   et la lumière est atteinte quand t=1 si on utilise L non normalisé
        #
        # Pour une lumière directionnelle :
        #   L = direction constante (pas de "distance finie")
        if light.l_type == 'point':
            l_vec = light.position - point
            t_max = 1.0
        else:  # 'directional'
            l_vec = light.position
            t_max = float('inf')

        # --- Ombres (shadow ray) ---
        #
        # On décale légèrement l'origine du shadow ray avec EPS pour éviter
        # qu'il retouche immédiatement la surface sur laquelle on est.
        shadow_origin = point + normal * EPS

        # Si on touche une sphère entre le point et la lumière => ombre
        shadow_sphere, _ = closest_intersection(
            shadow_origin,
            l_vec,
            EPS,
            t_max,
            spheres
        )
        if shadow_sphere is not None:
            # Cette lumière ne contribue pas (bloquée)
            continue

        # --- Diffuse (Lambert) ---
        # On utilise la direction normalisée vers la lumière
        l_dir = l_vec.normalize()

        n_dot_l = normal.dot(l_dir)
        if n_dot_l > 0:
            intensity += light.intensity * n_dot_l

        # --- Spéculaire (Phong) ---
        if specular != -1:
            # Calcul du vecteur réfléchi R de la lumière autour de la normale :
            # R = 2N(N·L) - L
            #
            # Ici on veut un R unitaire pour que le dot(R, V) soit stable.
            r_vec = (2 * normal * normal.dot(l_dir) - l_dir).normalize()

            # V : direction vers la caméra (view) - on la normalise
            v_dir = view.normalize()

            r_dot_v = r_vec.dot(v_dir)
            if r_dot_v > 0:
                # puissance = specular
                intensity += light.intensity * (r_dot_v ** specular)

    return intensity


def trace_ray(origin, direction, min_t, max_t, spheres, lights, recursion_depth):
    """
    Fonction principale du ray tracer : trace un rayon et retourne une couleur RGB.

    Étapes :
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
    - plus c'est grand, plus c'est réaliste mais plus c'est lent.
    """
    sphere, t = closest_intersection(origin, direction, min_t, max_t, spheres)

    # Si le rayon ne touche rien : couleur de fond
    if sphere is None:
        return (0, 0, 0)

    # --- Point d'intersection P ---
    point = origin + direction * t

    # --- Normale N ---
    # Pour une sphère : N = (P - C) normalisé
    normal = (point - sphere.center).normalize()

    # --- View vector V ---
    # Direction vers la caméra : c'est l'opposé de D
    view = (-1) * direction

    # --- Couleur locale (éclairage) ---
    lighting = compute_lighting(point, normal, view, sphere.specular, spheres, lights)

    # On clamp l'intensité pour éviter des couleurs > 255
    lighting = max(0.0, min(1.0, lighting))

    local_color = (
        sphere.color[0] * lighting,
        sphere.color[1] * lighting,
        sphere.color[2] * lighting
    )

    # --- Si pas de réflexion (ou recursion_depth épuisée) : on s'arrête ---
    r = sphere.reflective
    if recursion_depth <= 0 or r <= 0:
        return (
            min(255, int(local_color[0])),
            min(255, int(local_color[1])),
            min(255, int(local_color[2]))
        )

    # --- Rayon réfléchi ---
    #
    # On utilise la formule de réflexion d'un vecteur V autour d'une normale N :
    #   R = 2N(N·V) - V
    #
    # Ici V est la direction vers la caméra (view).
    reflected_dir = (2 * normal * normal.dot(view) - view).normalize()

    # Origine du rayon réfléchi légèrement décalée pour éviter l'auto-hit
    reflect_origin = point + normal * EPS

    # Récursion : on récupère la couleur du monde reflété
    reflected_color = trace_ray(
        reflect_origin,
        reflected_dir,
        EPS,
        float('inf'),
        spheres,
        lights,
        recursion_depth - 1
    )

    # --- Mélange couleur locale / réflexion ---
    #
    # reflective r :
    # - r = 0 -> uniquement local_color
    # - r = 1 -> uniquement reflected_color
    final_r = local_color[0] * (1 - r) + reflected_color[0] * r
    final_g = local_color[1] * (1 - r) + reflected_color[1] * r
    final_b = local_color[2] * (1 - r) + reflected_color[2] * r

    return (
        min(255, int(final_r)),
        min(255, int(final_g)),
        min(255, int(final_b))
    )