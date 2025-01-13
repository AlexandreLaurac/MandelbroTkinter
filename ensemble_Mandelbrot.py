from tkinter import *
from math import sqrt, copysign


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
        # Point A
        self.A.x = xa
        self.A.y = ya
        # Point B
        self.B.x = xb
        self.B.y = -self.K * (xb - xa) + ya  # Valeur contrainte par le rapport des dimensions (et signe - : voir plus bas)

    def maj_bornes(self, pxa, pxb, pya):
        xa, xb, ya = self.pix_to_x(pxa), self.pix_to_x(pxb), self.pix_to_y(pya)
        self.init_bornes(xa, xb, ya)

    def pix_to_x(self, px):
        return self.Kxy * px + self.A.x

    def pix_to_y(self, py):
        return -self.Kxy * py + self.A.y  # signe - car l'axe des ordonnées en pixels pointe vers le bas


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
            y = self.zone.pix_to_y(ny)  # ordonnée du point courant
            for nx in range(self.zone.dim_pix.x):
                x = self.zone.pix_to_x(nx)  # abscisse du point courant
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


#---------------------------------------- Vue ----------------------------------------#

class Fenetre(Tk):

    def __init__(self, largeur, hauteur, xa, xb, ya):
        Tk.__init__(self)
        # Création du canevas d'affichage
        self.largeur = largeur
        self.hauteur = hauteur
        self.canevas = Canvas(self, width=largeur, height=hauteur, bg="white")
        self.canevas.pack()
        self.canevas.bind("<Button-1>", self.clic)
        self.canevas.bind("<Button1-Motion>", self.cadre_zoom)
        self.canevas.bind("<Button1-ButtonRelease>", self.zoom)
        # Création d'un objet Mandelbrot
        self.mandel = Mandelbrot(largeur, hauteur, xa, xb, ya)

    def clic(self, event):
        "Callback définissant le premier coin du cadre de zoom par clic de la souris"
        self.px1, self.py1 = event.x, event.y  # Coordonnées du premier point cliqué
        self.iD_cadre_zoom = self.canevas.create_rectangle(self.px1, self.py1, self.px1, self.py1, outline='red')

    def cadre_zoom(self, event):
        "Callback définissant le deuxième coin du cadre de zoom par déplacement de la souris"
        # Abscisse du deuxième point obtenu par déplacement de la souris
        self.px2 = event.x
        # Ordonnée du deuxième point, respectant les proportions de la fenêtre et le déplacement de la souris
        taille_abs = abs(self.px2 - self.px1)
        signe_y = copysign(1, event.y - self.py1)
        self.py2 = self.py1 + signe_y * self.mandel.zone.K * taille_abs
        # Tracé du cadre
        self.canevas.coords(self.iD_cadre_zoom, self.px1, self.py1, self.px2, self.py2)

    def zoom(self, event):
        "Callback déclenchant le zoom sur la zone sélectionnée de la région actuelle"
        # On réordonne les valeurs des pixels pour avoir A et B aux bons endroits
        pxa, pya = (min(self.px1, self.px2), min(self.py1, self.py2))  # sur l'image, A (point haut gauche) a les plus petites valeurs en pixels
        pxb = max(self.px1, self.px2)  # B (point bas droit) a la plus grande abscisse en pixels
        # Modification du modèle
        self.mandel.zone.maj_bornes(pxa, pxb, pya)
        self.mandel.get_ensemble()
        # Tracé
        self.canevas.delete(ALL)
        self.trace_ensemble()

    def trace_ensemble(self):
        "Fonction de tracé effectif de l'ensemble de Mandelbrot"
        for py in range(self.hauteur):
            for px in range(self.largeur):
                if self.mandel.ensemble[py][px] == True:
                    self.canevas.create_rectangle(px,py,px,py)

    def lancement(self):
        # Tracé de l'ensemble
        self.mandel.get_ensemble()
        self.trace_ensemble()
        # Lancement de la boucle d'événements
        self.mainloop()        


#---------------------------------- Programme principal ----------------------------------#

if __name__ == '__main__':

    # Paramètres
    largeur, hauteur = 800, 800
    xa, ya = (-2.0, 1.5)  # point haut gauche 
    xb = 1.0              # abscisse du point bas droite

    # Lancement de la fenêtre
    Fenetre(largeur, hauteur, xa, xb, ya).lancement()
