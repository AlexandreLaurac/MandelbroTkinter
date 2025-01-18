from ensemble_Mandelbrot import precision as prec

# Notations :
# - alv : après la virgule
# - PE : partie(s) entière(s)
# - 1c : 1 chiffre
# - 2c : 2 chiffres
# - nc : n chiffres

# Lorsqu'un test échoue, c'est en raison d'un codage de nombre différent
# de celui attentu (ex : 1.2 codé en 1.19999999999999996) et donc un oracle
# fourni différent du résultat retourné. Ce n'est en fait pas vraiment une
# erreur dans la fonction.


#-------------------- Tests sur les décimaux --------------------#

# Parties entières différentes

def test_decimaux_differents_1c_alv():
    x1 = 2.1
    x2 = 1.2
    precision = 2
    assert prec(x1, x2) == precision

def test_decimaux_differents_2c_alv():
    x1 = 2.1
    x2 = 1.23
    precision = 2
    assert prec(x1, x2) == precision

def test_decimaux_differents_nc_alv():
    x1 = 2.1
    x2 = 1.23456789
    precision = 2
    assert prec(x1, x2) == precision


# Parties entières identiques

def test_decimaux_differents_PE_egales_1c_alv():
    x1 = 2.1
    x2 = 2.2
    precision = 3
    assert prec(x1, x2) == precision

def test_decimaux_differents_PE_egales_2c_alv():
    x1 = 2.1
    x2 = 2.23
    precision = 3
    assert prec(x1, x2) == precision

def test_decimaux_differents_PE_egales_nc_alv():
    x1 = 2.1
    x2 = 2.23456789
    precision = 3
    assert prec(x1, x2) == precision


# Parties entières + 1 chiffre après la virgule identiques

def test_decimaux_differents_PE_1c_apl_identiques_1c_en_plus():
    x1 = 2.1
    x2 = 2.12
    precision = 4
    assert prec(x1, x2) == precision  # Ne passe pas selon les nombres choisis

def test_decimaux_differents_PE_1c_apl_identiques_2c_en_plus():
    x1 = 2.1
    x2 = 2.123
    precision = 4
    assert prec(x1, x2) == precision

def test_decimaux_differents_PE_1c_apl_identiques_nc_en_plus():
    x1 = 2.1
    x2 = 2.123456789
    precision = 4
    assert prec(x1, x2) == precision


# Parties entières + 2 chiffres après la virgule identiques

def test_decimaux_differents_PE_2c_apl_identiques_1c_en_plus():
    x1 = 2.12
    x2 = 2.123
    precision = 5
    assert prec(x1, x2) == precision

def test_decimaux_differents_PE_2c_apl_identiques_2c_en_plus():
    x1 = 2.12
    x2 = 2.1234
    precision = 5
    assert prec(x1, x2) == precision

def test_decimaux_differents_PE_2c_apl_identiques_nc_en_plus():
    x1 = 2.12
    x2 = 2.123456789
    precision = 5
    assert prec(x1, x2) == precision


# Parties entières + n chiffres après la virgule identiques

def test_decimaux_differents_PE_nc_apl_identiques_1c_en_plus():
    x1 = 2.123456
    x2 = 2.1234567
    precision = 9
    assert prec(x1, x2) == precision

def test_decimaux_differents_PE_nc_apl_identiques_2c_en_plus():
    x1 = 2.123456
    x2 = 2.12345678
    precision = 9
    assert prec(x1, x2) == precision

def test_decimaux_differents_PE_nc_apl_identiques_nc_en_plus():
    x1 = 2.123456
    x2 = 2.123456789101112
    precision = 9
    assert prec(x1, x2) == precision


# Nombres égaux

def test_decimaux_egaux_1c_alv():
    x1 = 2.1
    x2 = 2.1
    precision = 4
    assert prec(x1, x2) == precision

def test_decimaux_egaux_2c_alv():
    x1 = 1.23
    x2 = 1.23
    precision = 5
    assert prec(x1, x2) == precision

def test_decimaux_egaux_nc_alv():
    x1 = 1.23456789
    x2 = 1.23456789
    precision = 11
    assert prec(x1, x2) == precision



#--------------- Tests sur un entier et un décimal ---------------#

# Parties entières différentes

def test_entier_decimal_PE_differentes_1_alv():
    n = 0
    x = 1.2
    precision = 2
    assert prec(n, x) == precision

def test_entier_decimal_PE_differentes_2_alv():
    n = 0
    x = 1.23
    precision = 2
    assert prec(n, x) == precision

def test_entier_decimal_PE_differentes_n_alv():
    n = 0
    x = 1.23456789
    precision = 2
    assert prec(n, x) == precision


# Parties entières identiques

def test_entier_decimal_PE_egales_1_alv():
    n = 1
    x = 1.2
    precision = 3
    assert prec(n, x) == precision

def test_entier_decimal_PE_egales_2_alv():
    n = 1
    x = 1.23
    precision = 3
    assert prec(n, x) == precision

def test_entier_decimal_PE_egales_n_alv():
    n = 1
    x = 1.23456789
    precision = 3
    assert prec(n, x) == precision



#-------------------- Tests sur les entiers --------------------#

def test_entiers_egaux():
    n1 = 17
    n2 = 17
    precision = 2
    assert prec(n1, n2) == precision

def test_entiers_differents():
    n1 = 5
    n2 = 8
    precision = 2
    assert prec(n1, n2) == precision

def test_entiers_un_positif_un_negatif():
    n1 = -4
    n2 = 2
    precision = 2
    assert prec(n1, n2) == precision

def test_entiers_negatifs():
    n1 = -4
    n2 = -5
    precision = 2
    assert prec(n1, n2) == precision
