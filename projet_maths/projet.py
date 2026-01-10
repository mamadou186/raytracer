import math

# --- 1. Classes de base (Maths & Objets) ---

class Vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar): # Multiplication par un scalaire (v * 2)
        return Vector(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar): # Multiplication inversée (2 * v)
        return self.__mul__(scalar)

    def __truediv__(self, scalar):
        return Vector(self.x / scalar, self.y / scalar, self.z / scalar)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def length(self):
        return math.sqrt(self.dot(self))

    def normalize(self):
        l = self.length()
        return Vector(self.x / l, self.y / l, self.z / l)

class Sphere:
    def __init__(self, center, radius, color, specular, reflective):
        self.center = center
        self.radius = radius
        self.color = color      # (r, g, b)
        self.specular = specular # Entier: -1 (mat) ou ex: 500 (très brillant)
        self.reflective = reflective # Float: 0.0 (pas miroir) à 1.0 (miroir parfait)

class Light:
    def __init__(self, l_type, intensity, position=None):
        self.l_type = l_type 
        self.intensity = intensity
        self.position = position

# --- 2. Moteur de Raytracing ---

def intersect_ray_sphere(origin, direction, sphere):
    r = sphere.radius
    co = origin - sphere.center
    
    a = direction.dot(direction)
    b = 2 * co.dot(direction)
    c = co.dot(co) - r*r
    
    discriminant = b*b - 4*a*c
    if discriminant < 0:
        return float('inf'), float('inf')
    
    t1 = (-b + math.sqrt(discriminant)) / (2*a)
    t2 = (-b - math.sqrt(discriminant)) / (2*a)
    return t1, t2

def compute_lighting(point, normal, view, specular, spheres, lights):
    intensity = 0.0
    for light in lights:
        if light.l_type == 'ambient':
            intensity += light.intensity
        else:
            if light.l_type == 'point':
                l_vec = light.position - point
                t_max = 1.0 # La lumière est à distance 1 (relativement au vecteur calculé)
            else:
                l_vec = light.position
                t_max = float('inf') # Lumière infiniment loin
            
            # Gestion des Ombres
            # On lance un rayon depuis le point vers la lumière pour voir si c'est bloqué
            shadow_sphere, shadow_t = closest_intersection(point, l_vec, 0.001, t_max, spheres)
            if shadow_sphere is not None:
                continue # Si on touche quelque chose, on passe à la lumière suivante (ce point est à l'ombre)

            # Diffuse
            n_dot_l = normal.dot(l_vec.normalize())
            if n_dot_l > 0:
                intensity += light.intensity * n_dot_l
            
            # Spéculaire (Brillance)
            if specular != -1:
                vec_r = 2 * normal * normal.dot(l_vec.normalize()) - l_vec.normalize()
                r_dot_v = vec_r.dot(view)
                if r_dot_v > 0:
                    intensity += light.intensity * (r_dot_v ** specular)
                    
    return intensity

def closest_intersection(origin, direction, min_t, max_t, spheres):
    closest_t = float('inf')
    closest_sphere = None
    
    for sphere in spheres:
        t1, t2 = intersect_ray_sphere(origin, direction, sphere)
        if min_t < t1 < max_t and t1 < closest_t:
            closest_t = t1
            closest_sphere = sphere
        if min_t < t2 < max_t and t2 < closest_t:
            closest_t = t2
            closest_sphere = sphere
            
    return closest_sphere, closest_t

def trace_ray(origin, direction, min_t, max_t, spheres, lights, recursion_depth):
    closest_sphere, closest_t = closest_intersection(origin, direction, min_t, max_t, spheres)
            
    if closest_sphere is None:
        return (0, 0, 0) # Fond noir

    # Calcul du point d'intersection et de la normale
    point = origin + direction * closest_t
    normal = (point - closest_sphere.center).normalize()
    view = direction * -1 # Vecteur vers la caméra
    
    # Calcul couleur locale (Diffuse + Spéculaire + Ombres)
    lighting = compute_lighting(point, normal, view, closest_sphere.specular, spheres, lights)
    local_color = (
        closest_sphere.color[0] * lighting,
        closest_sphere.color[1] * lighting,
        closest_sphere.color[2] * lighting
    )

    # Si on a atteint la limite de récursion ou que l'objet n'est pas un miroir
    r = closest_sphere.reflective
    if recursion_depth <= 0 or r <= 0:
        return (min(255, int(local_color[0])), min(255, int(local_color[1])), min(255, int(local_color[2])))

    # Calcul de la réflexion (Miroir)
    # Formule: R = 2*N*(N.V) - V
    reflected_ray = 2 * normal * normal.dot(view) - view
    reflected_color = trace_ray(point, reflected_ray, 0.001, float('inf'), spheres, lights, recursion_depth - 1)

    # Mélange de la couleur locale et de la réflexion
    final_r = local_color[0] * (1 - r) + reflected_color[0] * r
    final_g = local_color[1] * (1 - r) + reflected_color[1] * r
    final_b = local_color[2] * (1 - r) + reflected_color[2] * r

    return (min(255, int(final_r)), min(255, int(final_g)), min(255, int(final_b)))

# --- 3. Gestion Scène & Fichier ---

def load_scene(filename):
    spheres = []
    lights = []
    
    print(f"Chargement de la scène depuis {filename}...")
    try:
        with open(filename, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if not parts or parts[0].startswith("#"): continue
                
                command = parts[0].upper()
                if command == "SPHERE":
                    # SPHERE x y z radius r g b specular reflective
                    x, y, z, radius = map(float, parts[1:5])
                    r, g, b = map(int, parts[5:8])
                    specular = int(parts[8])
                    reflective = float(parts[9])
                    spheres.append(Sphere(Vector(x, y, z), radius, (r, g, b), specular, reflective))
                    
                elif command == "LIGHT":
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
    with open(filename, 'w') as f:
        f.write(f"P3\n{width} {height}\n255\n")
        for row in pixels:
            line = " ".join([f"{c[0]} {c[1]} {c[2]}" for c in row])
            f.write(line + "\n")
    print(f"Image sauvegardée sous {filename}")

# --- 4. Main Loop ---

def main():
    width = 600
    height = 600
    camera_pos = Vector(0, 0, 0)
    spheres, lights = load_scene("scene.txt")
    
    pixels = []
    print("Calcul du rendu en cours (ça peut prendre quelques secondes)...")
    
    for y in range(height):
        row = []
        sy = 1 - 2 * y / height 
        for x in range(width):
            sx = (2 * x / width - 1) * (width/height)
            direction = Vector(sx, sy, 1).normalize()
            
            # On lance le rayon avec une profondeur de récursion de 3 rebonds
            color = trace_ray(camera_pos, direction, 1, float('inf'), spheres, lights, 3)
            row.append(color)
        pixels.append(row)
        
    save_ppm("resultat.ppm", width, height, pixels)

if __name__ == "__main__":
    main()