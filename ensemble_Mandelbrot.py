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
        Canvas.__init__(self, parent, width=largeur, height=hauteur, bg='white', borderwidth=0, highlightthickness=0)
        self.parent = parent
        # Dimensions du canevas
        self.largeur = largeur
        self.hauteur = hauteur
        self.K = hauteur / largeur  # idem que dans l'objet zone de la classe Mandelbrot
        # Stockage des bornes de zoom en pixels pour le retour en arrière par ctrl-z
        self.stockage_bornes = []
        # Variables d'état
        self.souris_dedans = False  # souris dans le canevas ou non
        self.zoom = False  # on est en train de dessiner un cadre de zoom ou non
        # Gestion des événements
        self.bind("<Motion>", self.survol_canevas)
        self.bind("<Enter>", self.entree_canevas)
        self.bind("<Leave>", self.sortie_canevas)
        self.bind("<Button-1>", self.clic)
        self.bind("<Button1-Motion>", self.deplace)
        self.bind("<Button1-ButtonRelease>", self.relache)
        self.parent.bind("<Control-z>", self.retour)

    def ajoute_bornes(self, bornes):
        self.stockage_bornes.append(bornes) # format attendu : bornes = (pxa, pbx, pya, pyb)

    def retire_bornes(self):
        return self.stockage_bornes.pop()

    def entree_canevas(self, event):
        "Callback d'entrée de la souris dans le canevas, mise à jour de l'état"
        self.souris_dedans = True

    def survol_canevas(self, event):
        """Callback liée à l'événement de survol du canevas par la souris et conduisant à l'affichage
        des coordonnées réelles du point qu'elle désigne à partir de ses coordonnées en pixels dans
        le canevas.
        """
        # Stockage de la position de la souris en pixels pour affichage immédiat de la position réelle ...
        self.dernier_x, self.dernier_y = event.x, event.y # ... en cas de dezoom et absence de mouvement de la souris
        # Appel de la méthode associée du contrôleur
        self.parent.affiche_coordonnees_souris(event.x, event.y)

    def sortie_canevas(self, event):
        """Callback de sortie de la souris du canevas conduisant à effacer le texte des coordonnées
        réelles du point qu'elle désigne (valable lorsque l'on n'est pas en train de zoomer).
        """
        self.souris_dedans = False
        if not self.zoom:
            self.parent.efface_coordonnees_souris()

    def clic(self, event):
        "Callback définissant le premier coin du cadre de zoom par clic de la souris"
        self.zoom = True
        self.px1, self.py1 = event.x, event.y
        self.px2, self.py2 = self.px1, self.py1  # préparation du cas d'un cadre d'un seul pixel
        self.cadre_zoom = self.create_rectangle(self.px1, self.py1, self.px1, self.py1, outline='red', tags=CanvasMandel.etiquette_efface)

    def deplace(self, event):
        """Callback définissant le deuxième coin du cadre de zoom par déplacement de la souris et
        conduisant à l'affichage des coordonnées réelles de ce cadre à partir de ses différentes
        coordonnées en pixels dans le canevas.
        """
        # Abscisse du deuxième point obtenu par déplacement de la souris
        self.px2 = event.x
        # Ordonnée du deuxième point, respectant les proportions de la fenêtre et le déplacement de la souris
        taille_abs = abs(self.px2 - self.px1)
        signe_y = copysign(1, event.y - self.py1)
        self.py2 = self.py1 + signe_y * self.K * taille_abs
        # Tracé du cadre
        self.coords(self.cadre_zoom, self.px1, self.py1, self.px2, self.py2)
        # Stockage de la position de la souris en pixels pour affichage immédiat de la position réelle ...
        self.dernier_x, self.dernier_y = event.x, event.y  # ... après le zoom et en absence de mouvement de la souris
        # On réordonne les valeurs des pixels pour avoir A et B temporaires aux bons endroits
        pxaz, pyaz = (min(self.px1, self.px2), min(self.py1, self.py2))  # sur l'image, A (point haut gauche) a les plus petites valeurs en pixels
        pxbz, pybz = (max(self.px1, self.px2), max(self.py1, self.py2))  # B (point bas droit) a les plus grandes valeurs en pixel
        # Appel à la méthode d'affichage des coordonnées du cadre de zoom du parent
        self.parent.affiche_coordonnees_zoom(pxaz, pxbz, pyaz, pybz)

    def relache(self, event):
        "Callback définissant le cadre de zoom définitif par relâchement de la souris"
        self.zoom = False
        if self.px2 != self.px1 and self.py2 != self.py1 :  # On ne zoome que si le cadre n'est pas d'un seul pixel
            # On réordonne les valeurs des pixels pour avoir A et B définitifs aux bons endroits
            pxa, pya = (min(self.px1, self.px2), min(self.py1, self.py2))  # sur l'image, A (point haut gauche) a les plus petites valeurs en pixels
            pxb, pyb = (max(self.px1, self.px2), max(self.py1, self.py2))  # B (point bas droit) a les plus grandes valeurs en pixel
            # Ajout des bornes de zoom au stockage
            self.ajoute_bornes((pxa, pxb, pya, pyb))
            # Appel à la méthode de zoom du parent
            self.parent.zoom_dezoom((pxa, pxb, pya), 1)
        else:  # cadre d'un seul pixel (on n'a pas déplacé la souris ou on est revenu sur le pixel de départ)
            print("Cadre de zoom réduit à un pixel, impossible de zoomer")
            self.delete(self.cadre_zoom)

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
                    self.create_line(px, py, px+1, py, tags=CanvasMandel.etiquette_efface)

    def retrace_complet(self, ensemble):
        """Fonction de retracé du canevas : suppression des éléments marqués comme tels (ensemble
        courant, cadre de zoom), tracé d'un nouvel ensemble, et surélévation des éléments à conserver
        """
        self.delete(CanvasMandel.etiquette_efface)
        self.trace_ensemble(ensemble)


class CadreCoordonnees(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent, background="white")
        # Label pour les bornes de la zone de représentation
        self.label_bornes = Label(self, font="Arial 10", background="white")
        self.label_bornes.pack(side=LEFT)
        # Label pour les coordonnées du point désigné par la souris
        self.label_coord = Label(self, text="", justify= "right", font="Arial 10", background="white")
        self.label_coord.pack(side=RIGHT)
        # Type de disposition
        self.en_ligne = True

    def affiche_bornes(self, xa, xb, ya, yb):
        """Méthode d'affichage dans 'label_bornes' des bornes de la zone de représentation.
        Cette méthode étant appelée à chaque tracé de l'ensemble de Mandelbrot, et les précisions
        d'affichage ne dépendant que des bornes, on en profite pour calculer ces précisions et
        les stocker comme attributs pour utilisation par les autres méthodes.
        """
        # Précisions d'affichage en fonction de la partie commune des bornes
        self.prec_x = precision(xa, xb)
        self.prec_y = precision(ya, yb)
        # Affichage des bornes
        self.label_bornes.configure(text=f" x = [{xa:.{self.prec_x}f}, {xb:.{self.prec_x}f}], y = [{yb:.{self.prec_y}f}, {ya:.{self.prec_y}f}]")

    def affiche_coordonnees_souris(self, x, y, largeur_max):
        """Méthode d'affichage dans 'label_coord' des coordonnées réelles du point désigné par la souris dans le canevas
        
        Avant l'affichage des nouvelles coordonnées, on prépare la disposition des widgets 'label_bornes' et label_coord'.
        'label_coord' faisant à peu près la moitié de 'label_bornes' lors de l'affichage des coordonnées de la souris,
        c'est la valeur largeur_label_bornes + 0.5 x largeur_label_bornes = 1.5 x largeur_label_bornes (par rapport à la
        largeur du canevas) qui dicte l'agencement des widgets, d'où le facteur 1.5 (augmenté à 1.55 pour prévoir une marge)
        """
        self.prepare_disposition(1.55, largeur_max)
        self.label_coord.configure(text=f"x = {x:.{self.prec_x}f}, y = {y:.{self.prec_y}f} ")

    def efface_coordonnees_souris(self):
        "Méthode effaçant dans 'label_coord' le texte des coordonnées réelles du point désigné par la souris dans le canevas"
        self.label_coord.configure(text="")

    def affiche_coordonnees_zoom(self, xaz, xbz, yaz, ybz, largeur_max):
        """Méthode d'affichage dans 'label_coord' des coordonnées réelles du cadre de zoom créé par la souris dans le canevas
        
        Avant l'affichage des nouvelles coordonnées, on prépare la disposition des widgets 'label_bornes' et label_coord'.
        'label_coord' faisant à peu près la même largeur que 'label_bornes' lors de l'affichage des coordonnées du cadre de
        zoom, c'est la valeur 2 x largeur_label_bornes (par rapport à la largeur du canevas) qui dicte l'agencement des widgets,
        d'où le facteur 2 (augmenté à 2.05 pour prévoir une marge)
        """
        self.prepare_disposition(2.05, largeur_max)
        self.label_coord.configure(text=f"x = [{xaz:.{self.prec_x}f}, {xbz:.{self.prec_x}f}], y = [{ybz:.{self.prec_y}f}, {yaz:.{self.prec_y}f}] ")

    def prepare_disposition(self, facteur, largeur_max):
        """Méthode permettant de préparer la disposition (en ligne ou en colonne) des widgets 'label_bornes'
        et 'label_coord' dans ce widget en fonction de la largeur de 'label_bornes' et d'un facteur dépendant
        de l'information à afficher dans 'label_coord'.

        En effet, plutôt que de récupérer la largeur des widgets une fois dessinés et de réajuster l'agencement
        si les deux widgets dépassent la largeur du canevas (ce qui provoque une mise à jour rapide et désagréable
        de l'interface), on peut remarquer que 'label_coord' fait à peu près la moitié de la largeur de 'label_bornes'
        lorsqu'on affiche les coordonnées de la souris et à peu près la même largeur dans le cas où l'on affiche
        les coordonnées du cadre de zoom. On dispose donc d'une mesure de la largeur des deux widgets AVANT le tracé
        du second widget qu'il convient de comparer à la largeur du canevas pour déterminer comment les afficher : si
        la largeur totale des deux widgets est inférieure à celle du canevas, on les affiche en ligne ; si elle est
        supérieure, on les affiche en colonne. Un attribut booléen permet de modifier l'agencement seulement lorsque
        la largeur totale change de position par rapport à la largeur du canevas (passe de < à > ou de > à <) et pas
        à chaque appel de fonction.
        """
        largeur_label_bornes = self.label_bornes.winfo_width()
        # Disposition actuelle en ligne et largeur a priori des deux widgets qui dépasse celle du canevas => disposition en colonne
        if self.en_ligne and facteur * largeur_label_bornes > largeur_max:
            self.label_bornes.pack(side=TOP, anchor="w")
            self.label_coord.pack(side=TOP, anchor="e")
            self.en_ligne = False
        # Disposition actuelle en colonne et largeur a priori des deux widgets qui est inférieure à celle du canevas => disposition en ligne
        elif not self.en_ligne and facteur * largeur_label_bornes <= largeur_max:
            self.label_bornes.pack(side=LEFT)
            self.label_coord.pack(side=RIGHT)
            self.en_ligne = True


class Fenetre(Tk):

    def __init__(self, largeur, hauteur, xa, xb, ya, n_iter):
        Tk.__init__(self)
        self.title("Fractale de Mandelbrot")
        # Création du canevas d'affichage
        self.canevas = CanvasMandel(self, largeur, hauteur)
        self.canevas.pack()
        # Création du cadre de coordonnées
        self.cadre_coordonnees = CadreCoordonnees(self)
        self.cadre_coordonnees.pack(fill=X)
        # Création d'un objet Mandelbrot
        self.mandel = Mandelbrot(largeur, hauteur, xa, xb, ya, n_iter)

    def lancement(self):
        # Calcul de l'ensemble
        self.mandel.calcul_ensemble()
        # Tracé de l'ensemble et affichage des bornes
        self.canevas.trace_ensemble(self.mandel.ensemble)
        self.affiche_bornes()
        # Lancement de la boucle d'événements
        self.mainloop()

    def affiche_bornes(self):
        """Méthode d'affichage des bornes de la zone de représentation.
        Les bornes ne changent pas pour un même tracé de l'ensemble. La fonction
        est appelée au lancement de l'application et à chaque zoom ou dézoom.
        """
        # Récupération des bornes unes à unes
        xa, xb = self.mandel.zone.A.x, self.mandel.zone.B.x
        ya, yb = self.mandel.zone.A.y, self.mandel.zone.B.y
        # Affichage des bornes
        self.cadre_coordonnees.affiche_bornes(xa, xb, ya, yb)

    def affiche_coordonnees_souris(self, px, py):
        """Méthode appelée par la callback de survol du canevas par la souris.
        Déduit du modèle les coordonnées réelles du point désigné par la souris
        à partir de ses coordonnées en pixels px et py puis appelle la méthode
        d'affichage correspondante du widget de cadre de coordonnées.
        """
        # Calcul des coordonnées du point courant à partir du modèle
        x = self.mandel.zone.pix_to_x(px)
        y = self.mandel.zone.pix_to_y(py)
        # Affichage des coordonnées
        self.cadre_coordonnees.affiche_coordonnees_souris(x, y, self.canevas.winfo_width())

    def efface_coordonnees_souris(self):
        """Méthode appelée par la callback de sortie de la souris du canevas.
        Appelle la méthode correspondante du widget de cadre de coordonnées.
        """
        self.cadre_coordonnees.efface_coordonnees_souris()

    def affiche_coordonnees_zoom(self, pxaz, pxbz, pyaz, pybz):
        """Méthode appelée par la callback de déplacement de la souris dans le
        canevas, bouton appuyé. Déduit du modèle les coordonnées réelles du cadre
        de zoom à partir de ses différentes coordonnées en pixels puis appelle
        la méthode d'affichage correspondante du widget de cadre de coordonnées.
        """
        # Calcul des coordonnées du cadre de zoom à partir du modèle
        xaz, xbz = self.mandel.zone.pix_to_x(pxaz), self.mandel.zone.pix_to_x(pxbz)
        yaz, ybz = self.mandel.zone.pix_to_y(pyaz), self.mandel.zone.pix_to_y(pybz)
        # Affichage des coordonnées du cadre de zoom
        self.cadre_coordonnees.affiche_coordonnees_zoom(xaz, xbz, yaz, ybz, self.canevas.winfo_width())

    def zoom_dezoom(self, bornes, type):
        # Modification du modèle
        if type == 1:   # zoom
            pxa, pxb, pya = bornes
            self.mandel.zone.maj_bornes_zoom(pxa, pxb, pya)
        elif type == 2: # dezoom
            pxa, pxb, pya, pyb = bornes
            self.mandel.zone.maj_bornes_dezoom(pxa, pxb, pya, pyb)
        self.mandel.calcul_ensemble()
        # Modification de l'affichage
        self.canevas.retrace_complet(self.mandel.ensemble)
        self.affiche_bornes()
        if self.canevas.souris_dedans:  # if pour éviter d'afficher les précédentes coordonnées de la souris dans le cas "sortie du canevas puis ctrl-z"
            self.update_idletasks()  # Mise à jour de l'affichage pour avoir la bonne taille de 'label_bornes' dans 'cadre_coordonnees' et afficher correctement 'label_coord'
            self.affiche_coordonnees_souris(self.canevas.dernier_x, self.canevas.dernier_y)  # On force l'affichage des coordonnées de la souris à partir de sa dernière position (gestion du cas "absence d'événements")


def precision(x1, x2, log=False):
    """Fonction utilitaire permettant de déterminer le nombre de chiffres à afficher
    après la virgule à partir des chiffres communs à deux nombres fournis en argument.
    Valeur retournée : 3 chiffres en plus du nombre de chiffres commun après la virgule

    La fonction est écrite principalement pour des nombres décimaux, mais prend aussi
    en compte les nombres entiers s'ils se présentent. Les cas sont les suivants :
    1. pour deux nombres flottants :
    - les parties entières sont différentes : precision = 2
    - les parties entières sont égales : precision = nombre de chiffres communs après
      la virgule + 3
    2. pour un nombre flottant et un entier : le principe est le même, sachant que, si
    les parties entières sont égales, le nombre de chiffres communs après la virgule
    est nul (=> précision maximale de 3)
    3. pour deux nombres entiers, égaux ou différents : precision = 2

    La fonction ne donne pas toujours le résultat attendu en raison du codage des flottants
    (ex : 1.2 étant codé en 1.19999999999999996, l'appel de la fonction avec 1.1 donne
    une partie commune de 1.1 et une précision de 4 alors qu'on attend une partie commune
    de 1 et une précision de 3)

    Cette fonction est utilisée lors de l'affichage des coordonnées d'un point pour avoir :
    1. un même nombre de chiffres après la virgule pour ces coordonnées dans une même zone
       de zoom (et non un nombre de chiffres dépendant du point)
    2. et surtout un nombre de chiffres après la virgule dépendant du niveau de zoom, de
       sorte que la précision des coordonnées soit suffisamment grande pour que l'on puisse
       observer une variation de celles-ci entre les bornes
    """

    # Algorithme
    precision = 2  # initialement deux chiffres après la virgule
    ex1, ex2 = int(x1), int(x2)  # partie entière des deux nombres à comparer
    if ex1 == ex2 and (x1 != ex1 or x2 != ex2):  # si les deux nombres ont une partie entière différente, ou s'ils sont tous les deux entiers, on s'arrête à une précision de deux chiffres après la virgule, sinon...
        precision = precision + 1
        # ... on compare les chaines de chiffres après la virgule ...
        ch_x1 = str(x1)
        ip1 = ch_x1.find('.')
        ch1 = str(x1 - ex1)[ip1+1:]
        ch_x2 = str(x2)
        ip2 = ch_x2.find('.')
        ch2 = str(x2 - ex2)[ip2+1:]
        i = 0
        taille_min = min(len(ch1), len(ch2))
        while i<taille_min and ch1[i] == ch2[i]:  # ... et on ajoute un chiffre de précision à chaque chiffre identique
            precision = precision + 1
            i = i + 1

    # Log : affichage de la partie commune et de la précision obtenue
    if log == True:
        print(f"Nombres fournis :\n{x1}\n{x2}")
        # Un des deux nombres est un entier : la partie commune est au mieux l'entier
        if type(x1) == int or type(x2) == int:
            if ex1 == ex2:
                print(f"Partie commune :\n{ex1}")
            else:
                print("Pas de partie commune")
        # Les deux nombres fournis sont des flottants
        else:
            if precision == 2:  # les parties entières sont différentes
                print("Pas de partie commune")
            else:
                print(f"Partie commune :\n{ch_x1[0:ip1+i+1]}")  # +1 car borne finale non incluse en Python
        print(f"Précision : {precision}")

    return precision


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
