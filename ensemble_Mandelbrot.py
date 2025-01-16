from tkinter import *
from math import sqrt, copysign
import sys, getopt


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

    def maj_bornes_zoom(self, pxa, pxb, pya):
        """Calcul de nouvelles bornes à partir de pixels de zoom"""
        xa, xb, ya = self.pix_to_x(pxa), self.pix_to_x(pxb), self.pix_to_y(pya)
        self.init_bornes(xa, xb, ya)

    def maj_bornes_dezoom(self, pxa, pxb, pya, pyb):
        """Calcul des bornes précédentes à partir des bornes actuelles et des pixels de zoom ayant fait
        passer des premières aux secondes (résolution d'un système de deux équations à deux inconnues)
        """
        Kx = (self.B.x - self.A.x) / (pxb - pxa)
        xa = self.A.x - Kx * pxa
        xb = xa +  Kx * self.dim_pix.x
        Ky = (self.B.y - self.A.y) / (pyb - pya)
        ya = self.A.y - Ky * pya
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

    def calcul_ensemble(self):
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


#---------------------------------------- Vues ----------------------------------------#

class CanvasMandel(Canvas):

    etiquette_efface = "items_a_effacer"
    etiquette_garde = "items_a_garder"

    def __init__(self, parent, largeur, hauteur):
        # Classe et widget parents
        Canvas.__init__(self, parent, width=largeur, height=hauteur, bg='white')
        self.parent = parent
        # Dimensions du canevas
        self.largeur = largeur
        self.hauteur = hauteur
        self.K = hauteur / largeur  # idem que dans l'objet zone de la classe Mandelbrot
        # Stockage des bornes de zoom en pixels pour le retour en arrière par ctrl-z
        self.stockage_bornes = []
        # Gestion des événements
        self.bind("<Enter>", self.entree_canevas)
        self.bind("<Leave>", self.sortie_canevas)
        self.bind("<Motion>", self.survol_canevas)
        self.bind("<Button-1>", self.clic)
        self.bind("<Button1-Motion>", self.deplace)
        self.bind("<Button1-ButtonRelease>", self.relache)
        self.parent.bind("<Control-z>", self.retour)

    def ajoute_bornes(self, bornes):
        self.stockage_bornes.append(bornes) # format attendu : bornes = (pxa, pbx, pya, pyb)

    def retire_bornes(self):
        return self.stockage_bornes.pop()

    def entree_canevas(self, event):
        self.texte_coord = self.create_text(self.largeur-25, self.hauteur-10, text=f"{event.x}, {event.y}", fill="red", tags=CanvasMandel.etiquette_garde)

    def sortie_canevas(self, event):
        self.delete(self.texte_coord)

    def survol_canevas(self, event):
        self.itemconfigure(self.texte_coord, text=f"{event.x}, {event.y}")

    def clic(self, event):
        "Callback définissant le premier coin du cadre de zoom par clic de la souris"
        self.px1, self.py1 = event.x, event.y
        self.cadre_zoom = self.create_rectangle(self.px1, self.py1, self.px1, self.py1, outline='red', tags=CanvasMandel.etiquette_efface)

    def deplace(self, event):
        "Callback définissant le deuxième coin du cadre de zoom par déplacement de la souris"
        # Abscisse du deuxième point obtenu par déplacement de la souris
        self.px2 = event.x
        # Ordonnée du deuxième point, respectant les proportions de la fenêtre et le déplacement de la souris
        taille_abs = abs(self.px2 - self.px1)
        signe_y = copysign(1, event.y - self.py1)
        self.py2 = self.py1 + signe_y * self.K * taille_abs
        # Tracé du cadre
        self.coords(self.cadre_zoom, self.px1, self.py1, self.px2, self.py2)

    def relache(self, event):
        "Callback définissant le cadre de zoom définitif par relâchement de la souris"
        # On réordonne les valeurs des pixels pour avoir A et B aux bons endroits
        pxa, pya = (min(self.px1, self.px2), min(self.py1, self.py2))  # sur l'image, A (point haut gauche) a les plus petites valeurs en pixels
        pxb, pyb = (max(self.px1, self.px2), max(self.py1, self.py2))  # B (point bas droit) a les plus grandes valeurs en pixel
        # Ajout des bornes de zoom au stockage
        self.ajoute_bornes((pxa, pxb, pya, pyb))
        # Appel à la callback de zoom du parent
        self.parent.zoom_dezoom((pxa, pxb, pya), 1)

    def retour(self, event):
        try:
            bornes = self.retire_bornes()
            self.parent.zoom_dezoom(bornes, 2)
        except IndexError:
            print("Pas de dézoom possible")

    def trace_ensemble(self, ensemble):
        "Fonction de tracé effectif de l'ensemble de Mandelbrot"
        for py in range(self.hauteur):
            for px in range(self.largeur):
                if ensemble[py][px] == True:
                    self.create_rectangle(px,py,px,py, tags=CanvasMandel.etiquette_efface)

    def retrace_complet(self, ensemble):
        """Fonction de retracé du canevas : suppression des éléments marqués comme tels (ensemble
        courant, cadre de zoom), tracé d'un nouvel ensemble, et surélévation des éléments à conserver
        """
        self.delete(CanvasMandel.etiquette_efface)
        self.trace_ensemble(ensemble)
        self.tag_raise(CanvasMandel.etiquette_garde, CanvasMandel.etiquette_efface)


class Fenetre(Tk):

    def __init__(self, largeur, hauteur, xa, xb, ya, n_iter):
        Tk.__init__(self)
        # Création du canevas d'affichage
        self.canevas = CanvasMandel(self, largeur, hauteur)
        self.canevas.pack()
        # Création d'un objet Mandelbrot
        self.mandel = Mandelbrot(largeur, hauteur, xa, xb, ya, n_iter)

    def lancement(self):
        # Tracé de l'ensemble
        self.mandel.calcul_ensemble()
        self.canevas.trace_ensemble(self.mandel.ensemble)
        # Lancement de la boucle d'événements
        self.mainloop()      

    def zoom_dezoom(self, bornes, type):
        # Modification du modèle
        if type == 1:   # zoom
            pxa, pxb, pya = bornes
            self.mandel.zone.maj_bornes_zoom(pxa, pxb, pya)
        elif type == 2: # dezoom
            pxa, pxb, pya, pyb = bornes
            self.mandel.zone.maj_bornes_dezoom(pxa, pxb, pya, pyb)
        self.mandel.calcul_ensemble()
        # Tracé
        self.canevas.retrace_complet(self.mandel.ensemble)


#---------------------------------- Programme principal ----------------------------------#

def help():
    print("""
    Utilisation : ensemble_mandelbrot.py [-l <valeur_l>] [-h <valeur_h>] [-n <valeur_n>]
    -l, -h : largeur et hauteur du cadre de représentation en pixels
             si l'une des deux options est absente, la grandeur associée prend la valeur attribuée à l'autre option
             si les deux options sont absentes, largeur et hauteur prennent la valeur par défaut de 800 pixels
    -n : nombre d'itérations maximal dans le calcul de la suite définissant l'ensemble de Mandelbrot
         valeur par défaut : 100 itérations
    """)

def help_exit():
    help()
    sys.exit(2)


def main(argv):

    # Valeurs par défaut des paramètres
    largeur = hauteur = 800
    n_iter = 100
    xa, ya = (-2.0, 1.5)  # point haut gauche 
    xb = 1.0              # abscisse du point bas droite

    # Récupération des options de la ligne de commande
    try:
        options_et_valeurs, _ = getopt.getopt(argv, "n:l:h:", ["help"])
    except getopt.GetoptError as err:
        print(err)
        help_exit()

    # Récupération des valeurs
    options = [o for o, _ in options_et_valeurs]
    for option, valeur in options_et_valeurs:
        if option == "--help":
            help_exit()
        elif option == '-l':
            try:
                largeur = int(valeur)
                if '-h' not in options:
                    hauteur = largeur
            except:
                print("Mauvaise valeur pour l'option '-l'")
                help_exit()
        elif option == '-h':
            try:
                hauteur = int(valeur)
                if '-l' not in options:
                    largeur = hauteur
            except:
                print("Mauvaise valeur pour l'option '-h'")
                help_exit()
        elif option == '-n':
            try:
                n_iter = int(valeur)
            except:
                print("Mauvaise valeur pour l'option '-n'")
                help_exit()

    # Lancement de l'application
    Fenetre(largeur, hauteur, xa, xb, ya, n_iter).lancement()


if __name__ == "__main__":
    main(sys.argv[1:])
