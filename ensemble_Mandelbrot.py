# -*- coding: utf-8 -*-


from tkinter import *
from math import sqrt

########################### Définition des fonctions ##########################

def trace_ensemble (minx, maxx, miny, maxy) :
    "Fonction traçant l'ensemble de Mandelbrot pour la région de dimension donnée en argument"
    # Paramètres
    Nit = 100                 # Nombre d'itérations pour le test d'appartenance
    Kx = (maxx-minx)/largeur  # pente en x pour la transition pixel -> abscisse
    Ky = (maxy-miny)/hauteur  # pente en y pour la transition pixel -> ordonnée
    # Parcours des pixels pour la zone choisie
    for px in range(largeur) :
        x = Kx * px + minx
        for py in range(hauteur) :
            # Coordonnées du point courant
            y = Ky * py + miny
            # 1er test (le point appartient à la cardioïde ou au bourgeon principal) 
            p = sqrt ((x-0.25)**2 + y**2)
            if (x < p-2*p**2+0.25) or ((x+1)**2+y**2 < 1./16) :
                borne = 1
            # 2è test
            else :
                c = complex (x,y)
                # Calcul des Nit+1 termes de la suite
                z = complex(0,0)
                borne = 1
                for nit in range(1,Nit+1) :
                    z = z*z + c
                    if abs(z) > 2 :
                        borne = 0
                        break
            # Tracé
            if borne :
                canevas.create_rectangle(px,py,px,py)


def clic (event) :
    "Fonction destinée à définir le coin supérieur haut gauche du cadre de zoom"
    global ch_px, ch_py, iD_cadre_zoom
    ch_px = event.x
    ch_py = event.y
    iD_cadre_zoom = canevas.create_rectangle(ch_px, ch_py, ch_px, ch_py, outline='red')

def cadre_zoom (event) :
    "Fonction dessinant le cadre de zoom"
    global cb_px, cb_py
    cb_px = event.x
    cb_py = event.y
    canevas.coords(iD_cadre_zoom, ch_px, ch_py, cb_px, cb_py)

def zoom (event) :
    "Fonction effectuant un zoom sur la zone sélectionnée de la région actuellement représentée"
    # On calcule les coordonnées du cadre à partir de la sélection effectuée
    # puis on retrace l'ensemble dans la région créée
    global min_x_courant, max_x_courant, min_y_courant, max_y_courant
    canevas.delete(ALL)
    Kx = (max_x_courant-min_x_courant)/largeur
    Ky = (max_y_courant-min_y_courant)/hauteur
    # Suite d'équations dans cet ordre pour ne pas mettre à jour min_x_courant et min_y_courant trop tôt...
    max_x_courant = Kx * cb_px + min_x_courant
    max_y_courant = Ky * cb_py + min_y_courant
    min_x_courant = Kx * ch_px + min_x_courant
    min_y_courant = Ky * ch_py + min_y_courant
    trace_ensemble (min_x_courant, max_x_courant, min_y_courant, max_y_courant)


############################# Programme principal #############################

# Création des éléments graphiques
fenetre = Tk()
largeur = 400
hauteur = 400
canevas = Canvas (fenetre, width=largeur, height=hauteur, bg="white")
canevas.pack()

# Définition des gestionnaires d'événements
canevas.bind("<Button-1>", clic)
canevas.bind("<Button1-Motion>", cadre_zoom)
canevas.bind("<Button1-ButtonRelease>", zoom)

# Paramètres relatifs à la région représentée
min_x_init, max_x_init = -2., 1.
min_y_init, max_y_init = -1.5, 1.5
min_x_courant, max_x_courant = min_x_init, max_x_init
min_y_courant, max_y_courant = min_y_init, max_y_init

# Tracé
trace_ensemble (min_x_courant, max_x_courant, min_y_courant, max_y_courant)

fenetre.mainloop()
