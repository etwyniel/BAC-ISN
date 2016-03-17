from random import randrange
from time import sleep
from os import system
from tkinter import *
from threading import Thread
from math import log
from PIL import Image


def base4(n):
    n = int(n)
    x = ''
    while n > 0:
        x = str(n % 4) + x
        n = int(n / 4)
    return x

def image_to_list(file, base=16):
    image = Image.open(file, 'r')
    dim = image.size
    data = image.load()
    values = []
    for column in range(dim[1]):
        for line in range(dim[0]):
            for p in range(3):
                if base == 16:
                    values.append(hex(data[line, column][p])[2:])
                elif base == 10:
                    values.append(data[line, column][p])
                elif base == 4:
                    values.append(base4(data[line, column][p]))
                elif base == 2:
                    values.append(bin(data[line, column][p])[2:])
    return dim, values

def ascii_ppm_to_list(file, base=16):
    #Initialisation de la variable:
    #Création de la variable image, qui permet de lire le code du fichier .ppm
    image = open(file, "r")
    #readline() lit les lignes à la suite, une à chaque itération
    f = image.readline()
    a = image.readline()
    l = ""
    h = ""
    #On ignore les commentaires éventuels, et on stocke les dimensions dans  l et h
    while a[0] == "#":
        a = image.readline()
    l = int(a.split(' ')[0])
    h = int(a.split(' ')[1])
    #On insère les dimensions dans la liste pixels
    dim = [l, h]
    image.readline()
    values = []
    #Cette boucle sépare les pixels en listes individuelles, contenues dans une une liste par ligne, selon les dimensions du fichier
    if base == 16:
        for d in range(l * h * 3):
            a = int(image.readline())
            values.append('0' * (4-len(hex(a))) + hex(a)[2:])
    elif base == 10:
        for d in range(l * h * 3):
            values.append(int(image.readline()))
    elif base == 4:
        for d in range(l * h * 3):
            a = int(image.readline())
            values.append('0' * (4-len(base4(a))) + base4(a))
    elif base == 2:
        for d in range(l * h * 3):
            a = int(image.readline())
            values.append('0' * (10-len(bin(a))) + bin(a)[2:])
    #Le fichier est fermé pour éviter la perte de données
    image.close()

    #La liste finale, de la forme [[x,y],[[[pix_aR,pix_aV,pix_aB],[pix_bR,pix_bV,pix_bB]],[[pix_cR,pix_cV,pix_cB],[pix_dR,pix_dV,pix_dB]],...]]
    #                                     ^-------------------ligne 1-------------------^ ^-------------------ligne 2-------------------^
    #est renvoyée comme résultat de la fonction
    return dim, values

def raw_ppm_to_list(file, base=16):
    #On ouver le ficher .ppm en tant qu'objet binaire (en non pas comme une chaîne de caractères)
    image = open(file, 'rb')
    #on stocke toutes les données dans une variable
    data = image.read()
    #On ferme le fichier
    image.close()
    #On décode les deux premiers octets du fichier, qui représentent le format (ici, P6)
    f = data[:2].decode()
    #On ignore les éventuelles lignes de commentaires, qui commencent par '#', codé par la valeur 35.
    i = 3
    while data[i] == 35:
                a = i
                while data[a] not in [10, 13]:
                        a+=1
                i = a + 1

    #On isole les dimensions de l'image, que l'on stocke dans un tableau
    #Les dimensions sont juste après les commentaires, sont sur la même ligne, et sont suivies d'un saut de ligne (b'\n')
    if f == 'P6':
        dim = data[i:data.index(b'\n', i)].decode().split(' ')
    else:
        dim = data[i:data.index('\n', i)].split(' ')
    #On convertit les chaînes de caractères obtenues en entiers pour pouvoir les utiliser plus tard
    dim[0] = int(dim[0])
    dim[1] = int(dim[1])

    #On saute les dimensions et la valeur maximale
    n = i
    c = 0
    while c < 2:                                                        #MODIFIER SI POSSIBLE
                if chr(data[n]) == '\n':
                        c += 1
                n += 1
    #Et on stocke les valeurs de tous les pixels dans un tableau sous forme hexadécimale (en rajoutant un 0 si la valeur est inférieure ou égale à 0xf)
    if base == 16:
        values = ['0' * (4-len(hex(d))) + hex(d)[2:] for d in data[n:]]
    elif base == 10:
        values = [int(d) for d in data[n:]]
    elif base == 4:
        values = ['0' * (4-len(base4(d))) + base4(d) for d in data[n:]]
    elif base == 2:
        values = ['0' * (10-len(bin(d))) + bin(d)[2:] for d in data[n:]]

    #On revoie les dimensions et les pixels dans un tuple
    return dim, values

def header(file, dim, raw=True):
    if raw:
        #Ouvrir en "wb+" permet d'effacer le contenu du fichier avant d'y accéder en mode binaire
        image = open(file, "wb+")
        image.write(b"P6\n# CREATOR: ETWYNIEL FILTER v2.0\n")
        #On utilise la liste dim qui contient la résolution de l'image à transformer, pour écrire l'en-tete
        #On encode ces données pour qu'elles puissent être stockées dans le fichier binaire
        image.write((str(dim[0])+" "+str(dim[1])+"\n").encode())
        image.write(b"255\n")
        #En mode écriture, close() est indispensable pour que le contenu des instructions write() soit écrit dans le fichier
    else:
        image = open(file, 'w+')
        image.write('P3\n# CREATOR: ETWYNIEL FILTER v2.0\n')
        image.write(str(dim[0]) + ' ' + str(dim[1]) + '\n')
        image.write('255\n')
    image.close()

def gray_levels(file, raw=True):
    image = open(file, 'rb')
    data = image.read()
    image.close()
    if data[1] == 51:
        data = ascii_ppm_to_list(file, 10)
    else:
        #On récupère les dimensions de l'image ainsi que les valeurs de ses pixels
        data = raw_ppm_to_list(file, 10)
    dim = data[0]
    pixels = data[1]

    new_filename = file.split('.')[0] + ' - gray.ppm'

    header(new_filename, dim, raw)

    if raw:
        image = open(new_filename, 'ab')
        new_pixels = []
    else:
        image = open(new_filename, 'a')
        new_pixels = ''

    for a in range(0, dim[0] * dim[1] * 3, 3):
        new_pixel = int(sum(pixels[a:a+3]) / 3)
        if raw:
            new_pixels += [new_pixel] * 3
        else:
            new_pixels += (str(new_pixel) + '\n') * 3
    if raw:
        image.write(bytes(new_pixels))
    else:
        image.write(new_pixels)
    image.close()

def outline(file, raw=True):
    image = open(file, 'rb')
    data = image.read()
    image.close()
    if data[1] == 51:
        data = ascii_ppm_to_list(file, 10)
    else:
        #On récupère les dimensions de l'image ainsi que les valeurs de ses pixels
        data = raw_ppm_to_list(file, 10)
    dim = data[0]
    pixels = data[1]

    #On crée un nouveau fichier dans lequel on écrit l'en-tête
    new_filename = file.split('.')[0] + ' - outline.ppm'
    header(new_filename, dim, raw)

    if raw:
        image = open(new_filename, 'ab')
        new_pixels = []
    else:
        image = open(new_filename, 'a')
        new_pixels = ''

    for h in range(dim[1]):
        for w in range(dim[0]):
            if w in [0, dim[0] - 1] or h in [0, dim[1] - 1]:
                new_pixel = 255
            else:
                new_pixel = 255 * (8 * pixels[(h * dim[0] + w) * 3] - sum([
                    pixels[((h-1) * dim[0] + w) * 3],
                    pixels[((h+1) * dim[0] + w) * 3],
                    pixels[(h * dim[0] + w - 1) * 3],
                    pixels[(h * dim[0] + w - 1) * 3],
                    pixels[((h-1) * dim[0] + w - 1) * 3],
                    pixels[((h-1) * dim[0] + w + 1) * 3],
                    pixels[((h+1) * dim[0] + w - 1) * 3],
                    pixels[((h+1) * dim[0] + w + 1) * 3]]
                    ) < 128)
            if raw:
                new_pixels += [int(new_pixel)] * 3
            else:
                new_pixels += (str(new_pixel) + '\n') * 3
    if raw:
        image.write(bytes(new_pixels))
    else:
        image.write(new_pixels)
    image.close()

def embossage(file, raw=True):
    image = open(file, 'rb')
    data = image.read()
    image.close()
    if data[1] == 51:
        data = ascii_ppm_to_list(file, 10)
    else:
        #On récupère les dimensions de l'image ainsi que les valeurs de ses pixels
        data = raw_ppm_to_list(file, 10)
    dim = data[0]
    pixels = data[1]

    #On crée un nouveau fichier dans lequel on écrit l'en-tête
    new_filename = file.split('.')[0] + ' - emb.ppm'
    header(new_filename, dim, raw)

    if raw:
        image = open(new_filename, 'ab')
        new_pixels = []
    else:
        image = open(new_filename, 'a')
        new_pixels = ''

    for h in range(dim[1]):
        for w in range(dim[0]):
            if w in [0, dim[0] - 1] or h in [0, dim[1] - 1]:
                new_pixel = 255
            else:
                new_pixel = sum([
                    pixels[((h+1) * dim[0] + w) * 3],
                    -pixels[(h * dim[0] + w - 1) * 3],
                    pixels[(h * dim[0] + w - 1) * 3],
                    -pixels[((h-1) * dim[0] + w) * 3]
                    -2 * pixels[((h-1) * dim[0] + w - 1) * 3],
                    2 * pixels[((h+1) * dim[0] + w + 1) * 3]]
                    )
                new_pixel = max(new_pixel, 0)
                new_pixel = min(new_pixel, 255)
            if raw:
                new_pixels += [int(new_pixel)] * 3
            else:
                new_pixels += (str(new_pixel) + '\n') * 3
    if raw:
        image.write(bytes(new_pixels))
    else:
        image.write(new_pixels)
    image.close()

def steg_encode(file, raw=True, base=16):
    image = open(file, 'rb')
    data = image.read()
    image.close()
    if data[1] == 51:
        data = ascii_ppm_to_list(file, base)
    else:
        #On récupère les dimensions de l'image ainsi que les valeurs de ses pixels
        data = raw_ppm_to_list(file, base)
    dim = data[0]
    pixels = data[1]

    #On crée un nouveau fichier dans lequel on écrit l'en-tête
    new_filename = file.split('.')[0] + ' - steg{}.ppm'.format(base)
    if base == 16:
        header(new_filename, [dim[0] * 2, dim[1]], raw)
    elif base == 4:
        header(new_filename, [dim[0] * 2, dim[1] * 2], raw)
    elif base == 2:
        header(new_filename, [dim[0] * 2, dim[1] * 4], raw)
    #On rouvre le fichier en mode 'ab' pour pouvoir ajouter de données à la suite de l'en-tête
    if raw:
        image = open(new_filename, 'ab')
        new_pixels = []
    else:
        image = open(new_filename, 'a')
        new_pixels = ''
    
    #On sépare chaque octet en deux digits hexadécimaux (4 bits chacuns) que l'on ajoute à la suite de deux digits hexadecimaux aléatoires
    
    for color in pixels:
        for a in color:
            if base == 16:
                byte = hex(randrange(16))[2:] + a
            elif base == 4:
                byte = base4(randrange(64)) + a
            elif base == 2:
                byte = bin(randrange(128)) + a
            #On convertit ce nouvel octet en entier, pour ensuite le convertir en octet binaire, qui peut être écrit dans le fichier.
            if raw:
                new_pixels += [int(byte, base)]
            else:
                new_pixels += str(int(byte, base)) + '\n'
    if raw:
        image.write(bytes(new_pixels))
    else:
        image.write(new_pixels)
    #Une fois la stéganographie terminée, on referme le fichier pour appliquer les changements
    image.close()

def steg_decode(file, raw=True, base=16):
    image = open(file, 'rb')
    data = image.read()
    image.close()
    if data[1] == 51:
        data = ascii_ppm_to_list(file, base)
    else:
        #On récupère les dimensions de l'image ainsi que les valeurs de ses pixels
        data = raw_ppm_to_list(file, base)
    dim = data[0]
    pixels = data[1]

    #On crée un nouveau fichier dans lequel on écrit l'en-tête
    new_filename = file.split('.')[0] + ' - decoded.ppm'
    if base == 16:
        header(new_filename, [dim[0] / 2, dim[1]], raw)
    elif base == 4:
        header(new_filename, [dim[0] / 2, dim[1] / 2], raw)
    elif base == 2:
        header(new_filename, [dim[0] / 2, dim[1] / 4], raw)
    #On rouvre le fichier en mode 'ab' pour pouvoir ajouter de données à la suite de l'en-tête
    if raw:
        image = open(new_filename, 'ab')
        new_pixels = []
    else:
        image = open(new_filename, 'a')
        new_pixels = ''

    #On prévient l'utilisateur que le traitement de son image a commencé
    print('Traitement de l\'image en cours...')
    
    #Pour chaque valeur de l'image finale, on recupère 8 LSBs consécutifs
    #                                           Least Significant Bit
    x = log(256) / log(base)
    for a in range(0, int(dim[1] * dim[0] * 3), x):
        byte = ''
        for bit in range(x):
            byte += pixels[a+bit][x-1]
        #On stocke les valeurs décodées dans le nouveau fichier
        if raw:
            new_pixels += [int(byte, base)]
        else:
            new_pixels += str(int(byte, base)) + '\n'
    if raw:
        image.write(bytes(new_pixels))
    else:
        image.write(new_pixels)

    #On ferme le fichier encodé et le fichier décodé
    image.close()

def negative(file, raw=True):
    image = open(file, 'rb')
    data = image.read()
    image.close()
    if data[1] == 51:
        data = ascii_ppm_to_list(file, 10)
    else:
        #On récupère les dimensions de l'image ainsi que les valeurs de ses pixels
        data = raw_ppm_to_list(file, 10)
    dim = data[0]
    pixels = data[1]

    new_filename = file.split('.')[0] + ' - negative.ppm'
    header(new_filename, dim, raw)

    if raw:
        image = open(new_filename, 'ab')
        new_pixels = []
    else:
        image = open(new_filename, 'a')
        new_pixels = ''

    for a in pixels:
        if raw:
            new_pixels += [255 - a]
        else:
            new_pixels += str(255 - a) + '\n'

    if raw:
        image.write(bytes(new_pixels))
    else:
        image.write(new_pixels)

    image.close()


def check_settings():
    file = filename.get()
    if file == '':
        if not no_file.winfo_ismapped():
            no_file.pack()
    elif operation.get() == 'Choisir une opération à réaliser':
            if not no_op.winfo_ismapped():
                no_op.pack()
    else:
        op = Thread(target=start_op)
        op.start()

def start_op():
    no_file.pack_forget()
    no_op.pack_forget()
    file = filename.get()
    accept.config(state=DISABLED)
    #On prévient l'utilisateur que le traitement de son image a commencé
    message.config(text='Traitement de l\'image en cours...')
    message.pack()
    if not file.endswith('.ppm'):
        file += ".ppm"
    if operation.get() == 'Conversion en niveaux de gris':
        gray_levels(file, raw.get())
    elif operation.get() == 'Détection des contours':
        outline(file, raw.get())
    elif operation.get() == 'Négatif':
        negative(file, raw.get())
    elif operation.get() == 'Stéganographie (encodage)':
        steg_encode(file, raw.get(), base.get())
    elif operation.get() == 'Stéganographie (décodage)':
        steg_decode(file, raw.get(), base.get())
    accept.config(state=NORMAL)
    message.config(text='Fini')
    filename.set('')
        
    

master = Tk()
message = Label(master)
no_file = Label(master, text='Merci d\'entrer un nom valide')
no_op = Label(master, text='Merci de choisir une opération')
master.iconbitmap('pouletwyniel.ico')
master.title('BERBAECA')
title = Label(master, text='Nom du fichier:').pack(anchor=N)
filename = StringVar()
filename_field = Entry(master, textvariable=filename, width=50).pack(side=TOP, anchor=N)

Label(master, text='Format de sortie:').pack(side=TOP, anchor=W)
raw = BooleanVar()
raw.set(True)
Radiobutton(master, text='Brut', variable=raw, value=True).pack(side=TOP, anchor=W)
Radiobutton(master, text='ASCII', variable=raw, value=False).pack(side=TOP, anchor=W)
operation = StringVar()
operation.set('Choisir une opération à réaliser')
OptionMenu(master, operation,
           'Conversion en niveaux de gris',
           'Détection des contours',
           'Négatif',
           'Stéganographie (encodage)',
           'Stéganographie (décodage)').pack()


accept = Button(master, text='Valider', command=check_settings)
base = IntVar()
base.set(2)
encoding_select = []
encoding_select.append(Label(master, text='Merci de choisir un base numérique pour l\'encodage:'))
encoding_select.append(Radiobutton(master, text='Binaire', variable=base, value=2))
encoding_select.append(Radiobutton(master, text='Base 4', variable=base, value=4))
encoding_select.append(Radiobutton(master, text='Hexadécimal', variable=base, value=16))

def if_steg():
    
    accept.pack(anchor=S)
    selected = False
    while 1:
        if stop:
            break
        if operation.get().startswith('Stéganographie') and not selected:
            selected = True
            accept.pack_forget()
            
            for i in encoding_select:
                i.pack(side=TOP, anchor=W)
            
            accept.pack(anchor=S)
            #accept = Button(master, text='Valider', command=check_settings).pack(anchor=S)
        elif not operation.get().startswith('Stéganographie') and selected:
            selected = False
            for i in encoding_select:
                i.pack_forget()

stop = False
steg = Thread(target=if_steg)
steg.start()


mainloop()

"""
#Cette commande est cosmétique, et sert à changer la couleur de la console
system("color 70")
#Boucle principale, où on demande à l'utilisateur de choisir une opération
try:
    while 1:
        #Début de l interface avec l utilisateur
        print("Veuillez entrer le nom du fichier .ppm à convertir. Il doit etre sous la forme: P6\nCommentaire(s)\nLongueur Hauteur\n255\nRVBRVBR...")
        
        file = input("Nom du fichier : ")
        
        if not file.endswith('.ppm'):
            file += ".ppm"
        system("cls")
        
        print("Opération à effectuer:"
            "\n1) Conversion en nuances de gris"
            "\n2) Détection des contours"
            "\n3) Stéganographie"
            "\n4) Décodage d'une stéganographie"
            "\n5) Embossage")
        choice = input("Opération : ")

        if choice == "1":
            print('Format de sortie:\n1) Brut\n2) ASCII')
            f = input('Format: ')
            
            while f not in ['1', '2']:
                print('Merci de choisir une des deux options.')
                f = input('Format: ')
            
            if f == '1':
                raw = True
            else:
                raw = False
            
            gray_levels(file, raw)
            break
        
        elif choice == "2":
            print('Format de sortie:\n1) Brut\n2) ASCII')
            f = input('Format: ')
            
            while f not in ['1', '2']:
                print('Merci de choisir une des deux options.')
                f = input('Format: ')
            
            if f == '1':
                raw = True
            else:
                raw = False
            
            outline(file, raw)
            break
        elif choice == "3":
            base = int(input('Base numérique: '))
            while base not in [2, 4, 16]:
                system('cls')
                print('Merci de choisir une base valide (2, 4 ou 16)')
                base = int(input('Base numérique: '))
            print('Format de sortie:\n1) Brut\n2) ASCII')
            f = input('Format: ')
            while f not in ['1', '2']:
                print('Merci de choisir une des deux options.')
                f = input('Format: ')
            if f == '1':
                raw = True
            else:
                raw = False
            steg_encode(file, raw, base)
            break
        elif choice == "4":
            base = int(input('Base numérique: '))
            while base not in [2, 4, 16]:
                system('cls')
                print('Merci de choisir une base valide (2, 4 ou 16)')
                base = int(input('Base numérique: '))
            print('Format de sortie:\n1) Brut\n2) ASCII')
            f = input('Format: ')
            while f not in ['1', '2']:
                print('Merci de choisir une des deux options.')
                f = input('Format: ')
            if f == '1':
                raw = True
            else:
                raw = False
            steg_decode(file, raw, base)
            break
        elif choisce == "5":
            print('Format de sortie:\n1) Brut\n2) ASCII')
            f = input('Format: ')
            while f not in ['1', '2']:
                print('Merci de choisir une des deux options.')
                f = input('Format: ')
            if f == '1':
                raw = True
            else:
                raw = False
            embossage(file, raw)
        else:
            system("cls")
            print("Merci d'entrer un choix valide")
    system("cls")
#Gestion des erreurs                      
except FileNotFoundError:
    print("Ce fichier n'existe pas. Veuillez entrer le nom d'un fichier .ppm (sans extension)")
except ValueError:
    print("Erreur. Veuillez vérifier que le format fichier correspond conditions requises")
except:
    print("Le programme a cessé de fonctionner.")            



print("Done")
#sleep(5)
"""
