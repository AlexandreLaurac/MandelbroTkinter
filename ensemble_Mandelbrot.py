from tkinter import *
from math import sqrt


#---------------------------------------- Modèle ----------------------------------------#

class Mandelbrot():
    """Classe modélisant l'ensemble de Mandelbrot pour une zone du plan donnée
    et un nombre de points en abscisse et en ordonnée sur cette zone
    """

    def __init__(self, tuple_nb_points, tuple_zone_init, n_iter=100):
        self.nb_points_x = tuple_nb_points[0]
        self.nb_points_y = tuple_nb_points[1]
        self.K = self.nb_points_y / self.nb_points_x  # rapport des dimensions, pour les pixels ET pour la zone de représentation
        self.init_zone_repr(tuple_zone_init)
        self.init_ensemble()
        self.n_iter = n_iter

    def init_zone_repr(self, tuple_zone_repr):
        self.x_min = tuple_zone_repr[0]
        self.x_max = tuple_zone_repr[1]
        self.Kxy = (self.x_max - self.x_min) / self.nb_points_x  # Kxy == Kx == Ky
        self.y_min = tuple_zone_repr[2]
        self.y_max = self.K * (self.x_max - self.x_min) + self.y_min  # Valeur contrainte par le rapport des dimensions

    def init_ensemble(self):
        self.ensemble = [False]*self.nb_points_y
        for ny in range(self.nb_points_y):
            self.ensemble[ny] = [False]*self.nb_points_x

    def maj_zone_repr(self, nx_min, nx_max, ny_min):
        tuple_zone_repr = (self.pix_to_x(nx_min), self.pix_to_x(nx_max), self.pix_to_y(ny_min))
        self.init_zone_repr(tuple_zone_repr)

    def get_ensemble(self):
        """Méthode déterminant l'ensemble de Mandelbrot pour la zone de représentation courante

        Attribue un booléen à tous les points de la zone selon que le point appartient
        à l'ensemble de Mandelbrot ou non
        """
        # Parcours des points pour la zone courante
        for ny in range(self.nb_points_y):
            y = self.Kxy * ny + self.y_min  # ordonnée du point courant
            for nx in range(self.nb_points_x):
                x = self.Kxy * nx + self.x_min  # abscisse du point courant
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

    def pix_to_x(self, px):
        return self.Kxy * px + self.x_min

    def pix_to_y(self, py):
        return self.Kxy * py + self.y_min        


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
    canevas.coords(iD_cadre_zoom, px_min, py_min, px_max, py_min+mandel.K*taille) # on contraint le cadre à respecter les proportions de la fenêtre

def zoom(event):
    "Callback effectuant un zoom sur la zone sélectionnée de la région actuelle"
    # Modification du modèle
    mandel.maj_zone_repr(px_min, px_max, py_min)
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
nb_points = (largeur, hauteur)
zone_init = (-2., 1., -1.5) # (x_min, x_max, y_min), y_max est contraint par le rapport de longueur des axes

# Création des éléments graphiques
fenetre = Tk()
canevas = Canvas(fenetre, width=largeur, height=hauteur, bg="white")
canevas.pack()

# Définition des gestionnaires d'événements
canevas.bind("<Button-1>", clic)
canevas.bind("<Button1-Motion>", cadre_zoom)
canevas.bind("<Button1-ButtonRelease>", zoom)

# Tracé
mandel = Mandelbrot(nb_points, zone_init)
mandel.get_ensemble()
trace_ensemble(mandel)

fenetre.mainloop()
