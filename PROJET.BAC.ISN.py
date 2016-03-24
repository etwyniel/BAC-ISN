#Début du programme

#On déclare tous les commandes dont on aura besoin, et qui ne sont pas dans le python de base :
from random import randrange
#Pour générer des nombres aléatoires plus efficacement. 
from time import sleep
#Pour arrêter le déroulement du programme.
from os import system, getcwd
#Pour exécuter des commandes depuis la console, comme renommer un fichier.
from tkinter import *
#Pour une meilleure interface. 
from threading import Thread
#Pour effectuer simultanément des parties différentes du programme.
from math import log
#Pour éxécuter les calculs de changement de base. 
from PIL import Image
#Pour stocker les pixels d'une image dans une bibliothèque.


#On définit ici une commande essentielle qu'on utilisera plus loin :
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
    data = image.getdata()
    image.close()
    values = []
    for line in range(dim[1]):
        for column in range(dim[0]):
            for p in range(3):
                if base == 16:
                    val = hex(data[column+line*dim[0]][p])[2:]
                    values.append('0'*(2-len(val)) + val)
                elif base == 10:
                    values.append(data[column+line*dim[0]][p])
                elif base == 4:
                    val = base4(data[column+line*dim[0]][p])
                    values.append('0'*(4-len(val)) + val)
                elif base == 2:
                    val = bin(data[column+line*dim[0]][p])[2:]
                    values.append('0'*(8-len(val)) + val)
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
    dim, pixels = image_to_list(file, 10)
    values = []

    new_filename = file.split('.')[0] + ' - gray.jpg'

    for x in range(0, len(pixels), 3):
        new_color = int(sum(pixels[x:x+3]) / 3)
        new_pixel = new_color, new_color, new_color
        values += [new_pixel]
            
    image = Image.new('RGB', dim)
    image.putdata(values)
    image.save('D:/' + new_filename, 'jpeg')
    return image

def outline(file, raw=True):
    dim, pixels = image_to_list(file, 10)
    
    #On crée un nouveau fichier dans lequel on écrit l'en-tête
    new_filename = '.'.join(file.split('.')[:-1]) + ' - outline.jpg'

    values = []
    
    for h in range(dim[1]):
        for w in range(dim[0]):
            if w in [0, dim[0] - 1] or h in [0, dim[1] - 1]:
                new_pixel = 255
            else:
                new_pixel = 255 * (8 * pixels[h * dim[0] * 3 + w * 3] - sum([
                    pixels[(h-1) * dim[0] * 3 + w * 3],
                    pixels[(h+1) * dim[0] * 3 + w * 3],
                    pixels[h * dim[0] * 3 + (w - 1) * 3],
                    pixels[h * dim[0] * 3 + (w - 1) * 3],
                    pixels[(h-1) * dim[0] * 3 + (w - 1) * 3],
                    pixels[(h-1) * dim[0] * 3 + (w + 1) * 3],
                    pixels[(h+1) * dim[0] * 3 + (w - 1) * 3],
                    pixels[(h+1) * dim[0] * 3 + (w + 1) * 3]]
                    ) < 128)
                new_pixel = max(new_pixel, 0)
                new_pixel = min(new_pixel, 255)
            values.append((new_pixel, new_pixel, new_pixel))
                
    image = Image.new('RGB', dim)
    image.putdata(values)
    image.save(getcwd() + '\\' + new_filename, 'jpeg')
    return image

def embossage(file, raw=True):
    dim, pixels = image_to_list(file, 10)

    #On crée un nouveau fichier dans lequel on écrit l'en-tête
    new_filename = '.'.join(file.split('.')[:-1]) + ' - emb.jpg'

    values = []

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
            values.append((new_pixel, new_pixel, new_pixel))
    
    image = Image.new('RGB', dim)
    image.putdata(values)
    image.save(getcwd() + '\\' + new_filename, 'jpeg')
    return image


def steg_encode(file, raw=True, base=16):
    dim, pixels = image_to_list(file, base)

    #On crée un nouveau fichier dans lequel on écrit l'en-tête
    new_filename = '.'.join(file.split('.')[:-1]) + ' - steg{}.jpg'.format(base)

    values = []

    
    #On sépare chaque octet en deux digits hexadécimaux (4 bits chacuns) que l'on ajoute à la suite de deux digits hexadecimaux aléatoires
    new_pixel = tuple()
    
    for color in pixels:
        for a in color:
            if base == 16:
            	byte = hex(randrange(16)) + a
            elif base == 4:
                byte = base4(randrange(64)) + a
            elif base == 2:
                byte = bin(randrange(128)) + a
            new_pixel += tuple([int(byte, base)])
            if len(new_pixel) == 3:
                values.append(new_pixel)
                new_pixel = tuple()
            #On convertit ce nouvel octet en entier, pour ensuite le convertir en octet binaire, qui peut être écrit dans le fichier.
    if base == 16:
        new_dim = (dim[0]*2, dim[1])
    elif base == 4:
        new_dim = (dim[0]*2, dim[1]*2)
    elif base == 2:
        new_dim = (dim[0]*4, dim[1]*2)

    image = Image.new('RGB', new_dim)
    image.putdata(values)
    image.save(getcwd() + '\\' + new_filename, 'jpeg', subsampling=0)
    return image


def steg_decode(file, raw=True, base=16):
    dim, pixels = image_to_list(file, base)

    #On crée un nouveau fichier dans lequel on écrit l'en-tête
    new_filename = '.'.join(file.split('.')[:-1]) + ' - decoded.jpg'
  
    #On prévient l'utilisateur que le traitement de son image a commencé
    print('Traitement de l\'image en cours...')
    values = []
    
    #Pour chaque valeur de l'image finale, on recupère 8 LSBs consécutifs
    #                                           Least Significant Bit
    new_pixel = tuple()
    x = int(log(256) / log(base))
    for a in range(0, int(dim[1] * dim[0] * 3), x):
        byte = ''
        for bit in range(x):
            byte += pixels[a+bit][x-1]
        new_pixel += tuple([int(byte, base)])
        if len(new_pixel) == 3:
            values.append(new_pixel)
            new_pixel = tuple()
        #On stocke les valeurs décodées dans le nouveau fichier

    if base == 16:
        new_dim = (int(dim[0]/2), dim[1])
    elif base == 4:
        new_dim = (int(dim[0]/2), int(dim[1]/2))
    elif base == 2:
        new_dim = (int(dim[0]/4), int(dim[1]/2))

    image = Image.new('RGB', new_dim)
    image.putdata(values)
    image.save(getcwd() + '\\' + new_filename, 'jpeg')
    return image
    

def negative(file, raw=True):
    dim, pixels = image_to_list(file, 10)
    
    new_filename = file.split('.')[0] + ' - negative.jpg'

    values = []
    new_pixel = tuple()
    for a in pixels:
        new_pixel += tuple([255 - a])
        if len(new_pixel) == 3:
            values.append(new_pixel)
            new_pixel = tuple()

    image = Image.new('RGBA', dim)
    image.putdata(values)
    image.save(getcwd() + '\\' + new_filename, 'png')
    return image


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
