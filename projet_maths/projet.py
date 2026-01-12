import math
import os

# --- 1. Classes de base (Maths & Objets) ---

class Vector:
    def __init__(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):  # v * 2
        return Vector(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar):  # 2 * v
        return self.__mul__(scalar)

    def __truediv__(self, scalar):
        return Vector(self.x / scalar, self.y / scalar, self.z / scalar)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Vector(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def length(self):
        return math.sqrt(self.dot(self))

    def normalize(self):
        l = self.length()
        if l == 0:
            return Vector(0, 0, 0)
        return self / l


class Sphere:
    def __init__(self, center, radius, color, specular, reflective):
        self.center = center
        self.radius = float(radius)
        self.color = color
        self.specular = int(specular)
        self.reflective = float(reflective)


class Light:
    def __init__(self, l_type, intensity, position=None):
        self.l_type = l_type
        self.intensity = float(intensity)
        self.position = position


# --- 2. Moteur de Raytracing ---

def intersect_ray_sphere(origin, direction, sphere):
    r = sphere.radius
    co = origin - sphere.center

    a = direction.dot(direction)
    b = 2 * co.dot(direction)
    c = co.dot(co) - r * r

    discriminant = b * b - 4 * a * c
    if discriminant < 0:
        return float('inf'), float('inf')

    sqrt_disc = math.sqrt(discriminant)
    t1 = (-b + sqrt_disc) / (2 * a)
    t2 = (-b - sqrt_disc) / (2 * a)
    return t1, t2


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


def compute_lighting(point, normal, view, specular, spheres, lights):
    intensity = 0.0

    for light in lights:
        if light.l_type == 'ambient':
            intensity += light.intensity
            continue

        if light.l_type == 'point':
            l_vec = light.position - point   # vecteur vers la lumière
            t_max = 1.0                      # car on utilise l_vec non normalisé
        else:  # 'directional'
            l_vec = light.position
            t_max = float('inf')

        # Ombres (shadow ray)
        shadow_origin = point + normal * 0.001
        shadow_sphere, _ = closest_intersection(shadow_origin, l_vec, 0.001, t_max, spheres)
        if shadow_sphere is not None:
            continue

        # Diffuse
        l_dir = l_vec.normalize()
        n_dot_l = normal.dot(l_dir)
        if n_dot_l > 0:
            intensity += light.intensity * n_dot_l

        # Spéculaire
        if specular != -1:
            # R = 2N(N·L) - L
            r_vec = (2 * normal * normal.dot(l_dir) - l_dir).normalize()
            r_dot_v = r_vec.dot(view.normalize())
            if r_dot_v > 0:
                intensity += light.intensity * (r_dot_v ** specular)

    return intensity


def trace_ray(origin, direction, min_t, max_t, spheres, lights, recursion_depth):
    closest_sphere, closest_t = closest_intersection(origin, direction, min_t, max_t, spheres)
    if closest_sphere is None:
        return (0, 0, 0)

    point = origin + direction * closest_t
    normal = (point - closest_sphere.center).normalize()
    view = (-1) * direction

    lighting = compute_lighting(point, normal, view, closest_sphere.specular, spheres, lights)
    # clamp lighting (évite valeurs > 1.0 qui crament l'image)
    if lighting < 0:
        lighting = 0
    if lighting > 1.0:
        lighting = 1.0

    local_color = (
        closest_sphere.color[0] * lighting,
        closest_sphere.color[1] * lighting,
        closest_sphere.color[2] * lighting
    )

    r = closest_sphere.reflective
    if recursion_depth <= 0 or r <= 0:
        return (min(255, int(local_color[0])),
                min(255, int(local_color[1])),
                min(255, int(local_color[2])))

    # Réflexion
    reflected_ray = (2 * normal * normal.dot(view) - view).normalize()
    reflect_origin = point + normal * 0.001
    reflected_color = trace_ray(reflect_origin, reflected_ray, 0.001, float('inf'),
                                spheres, lights, recursion_depth - 1)

    final_r = local_color[0] * (1 - r) + reflected_color[0] * r
    final_g = local_color[1] * (1 - r) + reflected_color[1] * r
    final_b = local_color[2] * (1 - r) + reflected_color[2] * r

    return (min(255, int(final_r)),
            min(255, int(final_g)),
            min(255, int(final_b)))

def rotate_around_y(point, center, angle_rad):
    # on translate pour mettre center à l'origine
    p = point - center
    cos_t = math.cos(angle_rad)
    sin_t = math.sin(angle_rad)

    x = p.x * cos_t + p.z * sin_t
    z = -p.x * sin_t + p.z * cos_t

    # on re-translate
    return Vector(x, p.y, z) + center

# --- 3. Gestion Scène & Fichier ---

def load_scene(filename):
    spheres = []
    lights = []

    print(f"Chargement de la scène depuis {filename}...")
    try:
        with open(filename, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if not parts or parts[0].startswith("#"):
                    continue

                command = parts[0].upper()
                if command == "SPHERE":
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
            f.write(" ".join([f"{c[0]} {c[1]} {c[2]}" for c in row]) + "\n")
    print(f"Image sauvegardée sous {filename}")


# --- 4. Caméra orbitale & rendu frame ---

def get_camera_basis(camera_pos, target, world_up=Vector(0, 1, 0)):
    forward = (target - camera_pos).normalize()
    # right = up x forward (choix stable si up pas parallèle à forward)
    right = world_up.cross(forward).normalize()
    up = forward.cross(right).normalize()
    return right, up, forward


def render_frame(width, height, camera_pos, target, spheres, lights, recursion_depth=3):
    right, up, forward = get_camera_basis(camera_pos, target)

    pixels = []
    aspect = width / height

    for y in range(height):
        row = []
        sy = 1 - 2 * y / height  # [-1..1]
        for x in range(width):
            sx = (2 * x / width - 1) * aspect  # [-aspect..aspect]

            # direction monde via base caméra (viewport à distance 1)
            direction = (right * sx + up * sy + forward * 1.0).normalize()

            color = trace_ray(camera_pos, direction, 0.001, float('inf'), spheres, lights, 3)

            row.append(color)
        pixels.append(row)

    return pixels


def render_image(width, height, camera_pos, spheres, lights, out_filename):
    pixels = []
    for y in range(height):
        row = []
        sy = 1 - 2 * y / height
        for x in range(width):
            sx = (2 * x / width - 1) * (width/height)
            direction = Vector(sx, sy, 1).normalize()
            color = trace_ray(camera_pos, direction, 0.001, float('inf'), spheres, lights, 3)
            row.append(color)
        pixels.append(row)
    save_ppm(out_filename, width, height, pixels)

def run_animation_orbit(spheres, lights, num_frames=30):
    width, height = 600, 600
    camera_pos = Vector(0, 0, 0)

    os.makedirs("frames", exist_ok=True)

    red = spheres[0]
    blue = spheres[1]
    green = spheres[2]

    blue_start = blue.center
    green_start = green.center
    center = red.center  # pivot

    for i in range(num_frames + 1):
        theta = 2 * math.pi * (i / num_frames)

        blue.center = rotate_around_y(blue_start, center, theta)
        green.center = rotate_around_y(green_start, center, -theta)

        render_image(width, height, camera_pos, spheres, lights, f"frames/frame_{i}.ppm")
        print(f"[{i}/{num_frames}] frame_{i}.ppm OK")

# --- 5. Main ---
def main():
    spheres, lights = load_scene("scene.txt")

    print("Voulez-vous générer :")
    print("  0) Une image unique")
    print("  1) Une animation (sphères bleue/verte orbitent)")
    choice = input("Votre choix (0/1) : ").strip()

    if choice == "1":
        run_animation_orbit(spheres, lights, num_frames=30)
        print("Frames générées dans ./frames/")
    else:
        render_image(600, 600, Vector(0,0,0), spheres, lights, "resultat.ppm")

if __name__ == "__main__":
    main()