from vector import Vector
from io_scene import load_scene
from animation import render_image, run_animation


def main():
    """
    Point d'entrée du programme.

    - Charger la scène (sphères + lumières) depuis un fichier texte
    - Lancer soit :
        * un rendu statique (resultat.ppm)
        * une animation (suite d'images PPM dans frames/)
    """

    # Chargement de la scène depuis le fichier texte
    spheres, lights = load_scene("scene/scene.txt")

    # Sécurité
    if not spheres:
        print("Aucune sphère chargée. Vérifie scene/scene.txt.")
        return

    # Menu
    print("Voulez-vous générer :")
    print("  0) Une image unique")
    print("  1) Une animation (frames PPM)")
    choice = input("Votre choix (0/1) : ").strip()

    width, height = 600, 600 # 360 000 rayons

    camera_pos = Vector(0, 0, 0) # Caméra à l'origine

    fov = 0.8

    if choice == "1":
        run_animation(spheres, lights, num_frames=30, fov=fov)

        print("\nFrames pour le GIF générées dans ./frames/")
    else:
        render_image(
            width, height,
            camera_pos,
            spheres, lights,
            out_filename="resultat.ppm",
            fov=fov,
            recursion_depth=3
        )
        print("Image générée : resultat.ppm")

if __name__ == "__main__":
    main()