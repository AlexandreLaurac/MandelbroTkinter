from tkinter import *
from math import sqrt


#---------------------------------------- Modèle ----------------------------------------#

class Point():
    """Classe des coordonnées x et y (flottantes) d'un point du plan"""

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class DimPix():
    """Classe des dimensions x et y (entières) d'une image en pixels"""

    def __init__(self, x, y):
        self.x = x
        self.y = y


class Zone():
    """Classe de données géométriques modélisant une zone de représentation

    Un objet de cette classe possède :
    - un objet de type DimPix, contenant les dimensions en pixels de l'image de représentation sous-jacente
    - deux points A et B correspondant au point haut gauche et au point bas droit de la zone (l'ordonnée
      du point B est contrainte pour respecter les dimensions de l'image)
    - des relations de passage entre les pixels et les points du plan grâce à trois coefficients et des méthodes
    """

    def __init__(self, nb_points_x, nb_points_y, xa, xb, ya):
        # Dimensions en pixels de la zone
        self.dim_pix = DimPix(nb_points_x, nb_points_y)
        self.K = nb_points_y / nb_points_x  # rapport des dimensions, pour l'image ET la zone de représentation
        # Bornes de la zone
        self.A = Point()  # point haut gauche
        self.B = Point()  # point bas droit
        self.init_bornes(xa, xb, ya)

    def init_bornes(self, xa, xb, ya):
        self.Kxy = (xb - xa) / self.dim_pix.x  # Kxy == Kx == Ky
        # Axes des abscisses
        self.A.x = xa
        self.B.x = xb
        # Axes des ordonnées
        self.A.y = ya
        self.B.y = self.K * (xb - xa) + ya  # Valeur contrainte par le rapport des dimensions

    def maj_bornes(self, nxa, nxb, nya):
        xa, xb, ya = self.pix_to_x(nxa), self.pix_to_x(nxb), self.pix_to_y(nya)
        self.init_bornes(xa, xb, ya)

    def pix_to_x(self, px):
        return self.Kxy * px + self.A.x

    def pix_to_y(self, py):
        return self.Kxy * py + self.A.y        


class Mandelbrot():
    """Classe modélisant l'ensemble de Mandelbrot

    L'ensemble est représenté sur une zone du plan et les points qui lui appartiennent
    sont déterminés à partir du calcul d'une suite de récurrence avec au plus n_iter itérations
    """

    def __init__(self, nb_points_x, nb_points_y, xa, xb, ya, n_iter=100):
        self.zone = Zone(nb_points_x, nb_points_y, xa, xb, ya)
        self.n_iter = n_iter
        self.init_ensemble()

    def init_ensemble(self):
        self.ensemble = [False]*self.zone.dim_pix.y
        for ny in range(self.zone.dim_pix.y):
            self.ensemble[ny] = [False]*self.zone.dim_pix.x

    def get_ensemble(self):
        """Méthode déterminant l'ensemble de Mandelbrot pour la zone de représentation courante

        Attribue un booléen à tous les pixels de la zone selon que la relation de récurrence
        zn+1 = zn * zn + c converge ou non. Le critère de convergence est le non-dépassement
        de la valeur 2 en module après n_iter itérations
        """
        # Parcours des points pour la zone courante
        for ny in range(self.zone.dim_pix.y):
            y = self.zone.Kxy * ny + self.zone.A.y  # ordonnée du point courant
            for nx in range(self.zone.dim_pix.x):
                x = self.zone.Kxy * nx + self.zone.A.x  # abscisse du point courant
                # Premier test d'appartenance (à la cardioïde ou au bourgeon principal) 
                p = sqrt((x-0.25)**2 + y**2)
                if (x < p-2*p**2+0.25) or ((x+1)**2+y**2 < 1./16):
                    self.ensemble[ny][nx] = True
                # Deuxieme test d'appartenance
                else :
                    self.ensemble[ny][nx] = Mandelbrot.appartenance(x, y, self.n_iter)

    @staticmethod
    def appartenance(x, y, n_iter):
        c = complex(x, y)
        z = complex(0, 0)
        appartient = False
        n = 0
        while n < n_iter and abs(z) <= 2:
            z = z*z + c
            n = n + 1
        if n == n_iter:  # ou abs(z) <= 2
            appartient = True
        return appartient


#---------------------------------------- Callbacks ----------------------------------------#

def clic(event):
    "Callback destinée à définir le coin supérieur haut gauche du cadre de zoom"
    global px_min, py_min, iD_cadre_zoom
    px_min = event.x
    py_min = event.y
    iD_cadre_zoom = canevas.create_rectangle(px_min, py_min, px_min, py_min, outline='red')

def cadre_zoom(event):
    "Callback dessinant le cadre de zoom"
    global px_max
    px_max = event.x
    taille = px_max - px_min
    canevas.coords(iD_cadre_zoom, px_min, py_min, px_max, py_min+mandel.zone.K*taille) # on contraint le cadre à respecter les proportions de la fenêtre

def zoom(event):
    "Callback effectuant un zoom sur la zone sélectionnée de la région actuelle"
    # Modification du modèle
    mandel.zone.maj_bornes(px_min, px_max, py_min)
    mandel.get_ensemble()
    # Tracé
    canevas.delete(ALL)
    trace_ensemble(mandel)

def trace_ensemble(mandel):
    "Fonction de tracé effectif de l'ensemble de Mandelbrot"
    for py in range(hauteur):
        for px in range(largeur):
            if mandel.ensemble[py][px] == True:
                canevas.create_rectangle(px,py,px,py)


#---------------------------------- Programme principal ----------------------------------#

# Paramètres
largeur, hauteur = 800, 800
xa, xb = -2., 1.
ya = -1.5

# Création des éléments graphiques
fenetre = Tk()
canevas = Canvas(fenetre, width=largeur, height=hauteur, bg="white")
canevas.pack()

# Définition des gestionnaires d'événements
canevas.bind("<Button-1>", clic)
canevas.bind("<Button1-Motion>", cadre_zoom)
canevas.bind("<Button1-ButtonRelease>", zoom)

# Tracé
mandel = Mandelbrot(largeur, hauteur, xa, xb, ya)
mandel.get_ensemble()
trace_ensemble(mandel)

fenetre.mainloop()
