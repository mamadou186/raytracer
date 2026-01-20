from vector import Vector
from io_scene import load_scene
from animation import render_image, run_animation


def main():
    """
    Point d'entrée du programme.

    Le rôle de main.py est volontairement simple :
    - Charger la scène (sphères + lumières) depuis un fichier texte
    - Proposer un petit menu utilisateur
    - Lancer soit :
        * un rendu statique (resultat.ppm)
        * une animation (suite d'images PPM dans frames/)
    """

    # 1) Chargement de la scène depuis le fichier texte
    # (Le chemin est "scene/scene.txt" car on a mis la scène dans un dossier dédié)
    spheres, lights = load_scene("scene/scene.txt")

    # Si aucune sphère n'a été chargée, c'est souvent :
    # - fichier manquant
    # - erreur de format
    # - scène vide
    if not spheres:
        print("Aucune sphère chargée. Vérifie scene/scene.txt.")
        return

    # 2) Menu simple demandé (rendu unique ou animation)
    print("Voulez-vous générer :")
    print("  0) Une image unique")
    print("  1) Une animation (frames PPM)")
    choice = input("Votre choix (0/1) : ").strip()

    # 3) Paramètres globaux de rendu (choisis pour un bon compromis qualité / temps)
    width, height = 600, 600

    # Caméra fixe à l'origine :
    # - Dans notre modèle simplifié, la caméra regarde vers +Z
    # - Le viewport (écran virtuel) est placé à z = 1
    camera_pos = Vector(0, 0, 0)

    # fov ici est un facteur "zoom" (pas un angle en degrés)
    # - plus petit => zoom avant (on voit moins large)
    # - plus grand => zoom arrière (on voit plus large)
    fov = 0.8

    # 4) Lancer le rendu en fonction du choix utilisateur
    if choice == "1":
        # Mode animation :
        # - génère num_frames images PPM dans frames/
        # - chaque image correspond à une frame de l'animation
        run_animation(spheres, lights, num_frames=30, fov=fov)

        print("\nFrames pour le GIF générées dans ./frames/")
        print("Note : on ne génère pas directement le GIF pour rester en Python natif (pas d'installation).")

    else:
        # Mode image unique :
        # - rend une seule image statique
        # - l'écrit dans resultat.ppm
        render_image(
            width, height,
            camera_pos,
            spheres, lights,
            out_filename="resultat.ppm",
            fov=fov,
            recursion_depth=3  # profondeur de réflexion (rebonds)
        )
        print("Image générée : resultat.ppm")

if __name__ == "__main__":
    main()