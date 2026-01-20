# Ray Tracer – Projet Python

## Auteurs
- **Chamsedine AMOUCHE**
- **Mamadou BA**
- **Groupe : E3FI-1l**

---

## Description du projet

Ce projet consiste à implémenter un **ray tracer simple en Python natif**, sans bibliothèque externe, conformément aux consignes.

Le programme permet :
- le rendu d’**images statiques** au format **PPM**
- la génération d’une **animation** (suite de frames PPM) à partir d’une scène décrite dans un fichier texte

Le ray tracer gère :
- intersections rayon–sphère
- éclairage **ambient**, **diffus** (Lambert) et **spéculaire** (Phong)
- **ombres** (shadow rays)
- **réflexions** par récursion
- animation simple basée sur des transformations géométriques

---

## Architecture du projet

```bash
ray-tracer/
│
├── main.py # Point d’entrée du programme (menu, orchestration)
├── vector.py # Vecteur 3D et opérations mathématiques
├── objects.py # Objets de la scène (Sphere, Light)
├── raytracer.py # Cœur du ray tracer (intersections, shading, récursion)
├── animation.py # Animation des sphères et rendu image
├── io_scene.py # Chargement de la scène et sauvegarde PPM
│
├── scene/
│ └── scene.txt # Description textuelle de la scène
│
├── frames/ # Images PPM générées pour l’animation
├── resultat.ppm # Image PPM finale (rendu statique)
└── README.md
```

---

## Rôle de chaque fichier

### `vector.py`
- Implémente une classe `Vector` (vecteur 3D)
- Opérations essentielles : addition, soustraction, produit scalaire, normalisation
- Utilisé pour tous les calculs géométriques (rayons, normales, directions)

### `objects.py`
- Définit les objets de la scène :
  - `Sphere` (position, rayon, couleur, spéculaire, réflexion)
  - `Light` (ambient, point, directional)

### `raytracer.py`
- Cœur du moteur de ray tracing :
  - intersection rayon–sphère (équation du second degré)
  - calcul de l’éclairage (ambient + diffus + spéculaire)
  - gestion des ombres
  - gestion des réflexions par récursion
- Utilise un petit **epsilon (EPS)** pour éviter les auto-intersections

### `io_scene.py`
- Chargement de la scène depuis un fichier texte (`scene.txt`)
- Sauvegarde des images au format **PPM (P3)**

### `animation.py`
- Fonctions d’animation :
  - mouvement orbital des sphères sur une ellipse
  - animation sinusoidale de la sphère centrale
- Génération des frames PPM pour l’animation
- Fonction de rendu d’image (caméra fixe)

### `main.py`
- Point d’entrée du programme
- Menu utilisateur :
  - image statique
  - animation (frames)
- Appelle les fonctions de rendu appropriées

---

## Format de la scène (`scene.txt`)

La scène est définie textuellement, par exemple :

SPHERE x y z radius r g b specular reflective
LIGHT type intensity x y z


Cela permet de modifier facilement la scène sans toucher au code.

---

## Comment lancer le projet

Depuis le dossier racine du projet :

```bash
python main.py
```

Puis choisir :

0 → génération d’une image statique

1 → génération d’une animation (suite de frames)

## Résultats / Outputs

### Image statique :
- `resultat.ppm`

### Animation :
- images générées dans le dossier `frames/`
- chaque frame est une image PPM (`frame_1.ppm`, `frame_2.ppm`, …)

Pour générer le GIF nous avons utilisé `ImageMagick`