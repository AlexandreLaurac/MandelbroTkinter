from ensemble_Mandelbrot import Mandelbrot

def trace_ensemble_classique(ensemble, largeur, hauteur):
    # Simulation du tracé classique et stockage des pixels correspondant
    liste_pixels_traces = []
    for py in range(hauteur):
        for px in range(largeur):
            if ensemble[py][px] == True:
                # Ajout du pixel à la liste
                liste_pixels_traces.append((px, py))
    return liste_pixels_traces

def trace_ensemble_ameliore(ensemble, largeur, hauteur):
    # Simulation du tracé amelioré et idem
    liste_pixels_traces = []
    for py in range(hauteur):
        px = 0
        while px < largeur:
            nb_points = 1
            if ensemble[py][px] == True:
                while px+nb_points < largeur and ensemble[py][px+nb_points] == True:
                    nb_points += 1
                # Ajout des pixels à la liste
                for p_x in range(px, px+nb_points):
                    liste_pixels_traces.append((p_x, py))
                nb_points += 1
            px += nb_points
    return liste_pixels_traces

def test_egalite_zone_usuelle_200x200():
    # Paramètres
    largeur = hauteur = 200
    xa, ya, xb = -2.0, 1.5, 1.0
    n_iter = 100
    # Objet et ensemble de Mandelbrot
    mandelbrot = Mandelbrot(largeur, hauteur, xa, xb, ya, n_iter)
    mandelbrot.calcul_ensemble()
    # Test
    liste_classique = trace_ensemble_classique(mandelbrot.ensemble, largeur, hauteur)
    liste_amelioree = trace_ensemble_ameliore(mandelbrot.ensemble, largeur, hauteur)
    assert liste_classique == liste_amelioree

def test_egalite_zone_usuelle_400x400():
    # Paramètres
    largeur = hauteur = 400
    xa, ya, xb = -2.0, 1.5, 1.0
    n_iter = 100
    # Objet et ensemble de Mandelbrot
    mandelbrot = Mandelbrot(largeur, hauteur, xa, xb, ya, n_iter)
    mandelbrot.calcul_ensemble()
    # Test
    liste_classique = trace_ensemble_classique(mandelbrot.ensemble, largeur, hauteur)
    liste_amelioree = trace_ensemble_ameliore(mandelbrot.ensemble, largeur, hauteur)
    assert liste_classique == liste_amelioree

def test_egalite_zone_zoomee_800x800_niter_1000():
    # Paramètres
    largeur = hauteur = 800
    xa, ya, xb = -1.50, -0.337, -0.75
    n_iter = 1000
    # Objet et ensemble de Mandelbrot
    mandelbrot = Mandelbrot(largeur, hauteur, xa, xb, ya, n_iter)
    mandelbrot.calcul_ensemble()
    # Test
    liste_classique = trace_ensemble_classique(mandelbrot.ensemble, largeur, hauteur)
    liste_amelioree = trace_ensemble_ameliore(mandelbrot.ensemble, largeur, hauteur)
    assert liste_classique == liste_amelioree
