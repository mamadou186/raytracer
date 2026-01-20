from vector import Vector
from io_scene import load_scene
from animation import render_image, run_animation

def main():
    spheres, lights = load_scene("scene/scene.txt")
    if not spheres:
        print("Aucune sphère chargée. Vérifie scene.txt.")
        return

    print("Voulez-vous générer :")
    print("  0) Une image unique")
    print("  1) Une animation (frames PPM)")
    choice = input("Votre choix (0/1) : ").strip()

    width, height = 600, 600
    camera_pos = Vector(0, 0, 0)
    fov = 0.8

    if choice == "1":
        run_animation(spheres, lights, num_frames=30, fov=fov)
        print("\nFrames pour le GIF générées dans ./frames/")
    else:
        render_image(width, height, camera_pos, spheres, lights, "resultat.ppm", fov=fov, recursion_depth=3)
        print("Image générée : resultat.ppm")

if __name__ == "__main__":
    main()
