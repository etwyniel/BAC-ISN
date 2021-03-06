"""
Copyright (C) <2016> <Berbaecai>

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION
OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
"""

#Début du programme

#On déclare tous les commandes dont on aura besoin, et qui ne sont pas dans le language python de base :
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
import sys


class InvalidEncoding(Exception):
    """
    Erreur qui est levée si l'encodage demandé n'est pas valide.
    """
    
    pass

#On définit ici une commande essentielle qu'on utilisera plus loin :
def base4(n):
    """
    Cette fonction convertit un entier en base 10 en entier en base 4.
    """
    
    n = int(n) #Dans le cas où n n'est pas un entier.
    x = ''
    while n > 0:
        x = str(n % 4) + x
        n = int(n / 4)
    return x

def image_to_list(file, base=16):
    """
    Cette fonction lit un fichier image et renvoie une liste contenant les
    valeurs dans la base spécifiée.
    """
    
    image = Image.open(file, 'r') #On utilise l'objet image de PIL
    dim = image.size #On stocke les dimensions de l'image
    data = image.getdata() #On récupère les valeurs de l'image
    image.close() #On ferme l'image pour éviter la perte de données
    
    values = [] #On initialise une variable qui va contenir les variables encodées
    for line in range(dim[1]):
        for column in range(dim[0]):
            for p in range(3):    #Pour chaque valeur de chaque pixel de chaque ligne:
                
                if base == 16: #On vérifie le paramètre base
                    val = hex(data[column+line*dim[0]][p])[2:] #On convertit la valeur en hexadécimal
                    values.append('0'*(2-len(val)) + val) #On complète avec des 0 pour que la chaîne ait une longueur de 2
                    
                elif base == 10:
                    values.append(data[column+line*dim[0]][p]) #On ajoute la valeur à la fin de values
                    
                elif base == 4:
                    val = base4(data[column+line*dim[0]][p]) #On convertit la valeur en base 4
                    values.append('0'*(4-len(val)) + val) #On complète avec des 0 pour que la chaîne ait une longueur de 4
                    
                elif base == 2:
                    val = bin(data[column+line*dim[0]][p])[2:] #On convertit la valeur en binaire
                    values.append('0'*(8-len(val)) + val) #On complète avec des 0 pour que la chaîne ait une longueur de 8
                    
    return dim, values #On renvoie les dimensions et les valeurs dans un tuple

def gray_levels(file, f='PNG'):
    """
    Cette fonction convertit une image fournie et la convertit en niveaux de gris.
    """
    
    dim, pixels = image_to_list(file, 10) #On récupère les dimensions et les valeurs du fichier.
    
    #On vérifie le paramètre f (le format de sortie demandé) et on en déduit l'extension que le fichier doit avoir
    if f == 'JPEG':
        ext = 'jpg'
    elif f == 'PNG':
        ext = 'png'
        
    new_filename = file.split('.')[0] + ' - gray.' + ext #On crée le nom du fichier de sortie

    values = [] #On initialise une variable qui va contenir les valeurs traitées
    for x in range(0, len(pixels), 3): #Pour chaque pixel:
        new_color = int(sum(pixels[x:x+3]) / 3)  #On fait la moyenne des trois valeurs
        new_pixel = new_color, new_color, new_color
        values += [new_pixel] #On ajoute la valeur trois fois à la fin du tableau de valeurs
            
    image = Image.new('RGB', dim) #On crée un nouvel objet image de PIL des mêmes dimensions que l'image fournie
    image.putdata(values) #On stocke les valeurs traitées dans le nouvel objet
    image.save('D:/' + new_filename, f) #On sauvegarde le nouveau fichier
    return image

def outline(file, f='PNG'):
    """
    Cette fonction détecte les contours d'une image fournie en nuances de gris, et renvoie une image en noir et blanc.
    """
    dim, pixels = image_to_list(file, 10)

    if f == 'JPEG':
        ext = 'jpg'
    elif f == 'PNG':
        ext = 'png'    
    #On crée un nouveau fichier dans lequel on écrit l'en-tête
    new_filename = '.'.join(file.split('.')[:-1]) + ' - outline.' + ext
    values = []
    
    for h in range(dim[1]):
        for w in range(dim[0]):
            if w in [0, dim[0] - 1] or h in [0, dim[1] - 1]:
                new_pixel = 255
            else:
                new_pixel = 255 * (8 * pixels[h * dim[0] * 3 + w * 3] - sum([   #On applique un filtre à chaque pixel
                    pixels[(h-1) * dim[0] * 3 + w * 3],                         #La valeur du nouveau pixel va dépendre de ceux
                    pixels[(h+1) * dim[0] * 3 + w * 3],                         #qui se trouvent autour.
                    pixels[h * dim[0] * 3 + (w - 1) * 3],                       #Les bords de l'image restent donc blancs.
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
    image.save(getcwd() + '\\' + new_filename, f)
    return image

def embossage(file, f='PNG'):
    """
    Cette fonction applique un filtre à l'image fournie, pour donner un impression de relief en nuances de gris sur fond noir (image de sortie en nuances de gris).
    """
    dim, pixels = image_to_list(file, 10)

    #On crée un nouveau fichier dans lequel on écrit l'en-tête
    if f == 'JPEG':
        ext = 'jpg'
    elif f == 'PNG':
        ext = 'png'
    new_filename = '.'.join(file.split('.')[:-1]) + ' - emb.' + ext

    values = []

    for h in range(dim[1]):
        for w in range(dim[0]):
            if w in [0, dim[0] - 1] or h in [0, dim[1] - 1]:
                new_pixel = 0
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
    image.save(getcwd() + '\\' + new_filename, f)
    return image


def steg_encode(file, base=16):
    """
    Cette fonction permet de générer une image aléatoire dans laquelle est dissimulée en stéganographie l'image fournie.
    Il y a trois niveaux de dissimulation disponibles: 1/16 (hexa), 1/64 (base 4), 1/256 (binaire)
    """
    dim, pixels = image_to_list(file, base)

    #On crée un nouveau fichier dans lequel on écrit l'en-tête
    new_filename = '.'.join(file.split('.')[:-1]) + ' - steg{}.png'.format(base)

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

    image = Image.new('RGBA', new_dim)
    image.putdata(values)
    image.save(getcwd() + '\\' + new_filename, 'png', subsampling=0)
    return image


def steg_decode(file, base=16):
    """
    Cette fonction sert à décoder une image stéganographiée. En spécifiant l'encodage utilisé pour créér l'image stéganographiée, on récupère l'image d'origine sans altération.
    """
    dim, pixels = image_to_list(file, base)

    #On crée un nouveau fichier dans lequel on écrit l'en-tête
    new_filename = '.'.join(file.split('.')[:-1]) + ' - decoded.png'
  
    #On prévient l'utilisateur que le traitement de son image a commencé
    print('Traitement de l\'image en cours...')
    values = []
    if base == 16:
        new_dim = (int(dim[0]/2), dim[1])
    elif base == 4:
        new_dim = (int(dim[0]/2), int(dim[1]/2))
    elif base == 2:
        new_dim = (int(dim[0]/4), int(dim[1]/2))
    x = int(log(256) / log(base))
    if int(len(pixels)/(3*x)) != new_dim[0]*new_dim[1]:
        print('Wrong size')
        raise Exception
    
    #Pour chaque valeur de l'image finale, on recupère 8 LSBs consécutifs
    #                                           Least Significant Bit
    new_pixel = tuple()
    for a in range(0, int(dim[1] * dim[0] * 3), x):
        byte = ''
        for bit in range(x):
            byte += pixels[a+bit][x-1]
        new_pixel += tuple([int(byte, base)])
        if len(new_pixel) == 3:
            values.append(new_pixel)
            new_pixel = tuple()
        #On stocke les valeurs décodées dans le nouveau fichier


    image = Image.new('RGBA', new_dim)
    image.putdata(values)
    image.save(getcwd() + '\\' + new_filename, 'png')
    return image
    

def negative(file, f='PNG'):
    """
    Cette fonction renvoie un négatif de l'image fournie, en faisant 255 - x pour chaque couleur de chaque pixel, où x est l'intensité d'une couleur.
    """
    dim, pixels = image_to_list(file, 10)
    
    if f == 'JPEG':
        ext = 'jpg'
    elif f == 'PNG':
        ext = 'png'
    new_filename = file.split('.')[0] + ' - negative.' + ext

    values = []
    new_pixel = tuple()
    for a in pixels:
        new_pixel += tuple([255 - a])
        if len(new_pixel) == 3:
            values.append(new_pixel)
            new_pixel = tuple()

    image = Image.new('RGBA', dim)
    image.putdata(values)
    image.save(getcwd() + '\\' + new_filename, f)
    return image


def check_settings(*ignore):
    """
    Cette fonction est exécutée avant de lancer une opération, afin de s'assurer que les paramètres choisis par l'utilisateur sont valides
    """
    file = filename.get()
    if file == '':
        if not err_message.winfo_ismapped():
            err_message.config(text='Merci d\'entrer un nom valide')
            err_message.pack()
    elif operation.get() == 'Choisir une opération à réaliser':
            if not no_op.winfo_ismapped():
                no_op.pack()
    else:
        op = Thread(target=start_op)
        op.start()

def start_op():
    err_message.pack_forget()
    no_op.pack_forget()
    file = filename.get().strip('\r\x08')
    accept.config(state=DISABLED)
    #On prévient l'utilisateur que le traitement de son image a commencé
    message.config(text='Traitement de l\'image en cours...')
    message.pack()
    try:
        if operation.get() == 'Conversion en niveaux de gris':
            im = gray_levels(file, f.get())
        elif operation.get() == 'Détection des contours':
            im = outline(file, f.get())
        elif operation.get() == 'Négatif':
            im = negative(file, f.get())
        elif operation.get() == 'Embossage':
            im = embossage(file, f.get())
        elif operation.get() == 'Stéganographie (encodage)':
            im = steg_encode(file, base.get())
        elif operation.get() == 'Stéganographie (décodage)':
            im = steg_decode(file, base.get())
        message.config(text='Fini')
        filename_field.delete(0, 'end')
        filename_field.insert(0, '')
        accept.config(state=NORMAL)
        im.show()
    except FileNotFoundError:
        err_message.pack()
        message.pack_forget()
        accept.config(state=NORMAL)
    except InvalidEncoding:
        err_message.config(text='Encodage invalide.')
        err_message.pack()
        message.pack_forget()
        accept.config(state=NORMAL)
        
    
#Fenêtre principale de l'interface
master = Tk()
master.title('BERBAECA Image Edition Software')

main = Frame(master)
main.pack(padx=10, pady=2)

message = Label(main)

err_message = Label(main, text='Merci d\'entrer un nom valide')
no_op = Label(main, text='Merci de choisir une opération')
title = Label(main, text='Nom du fichier:').pack(anchor=N)

filename = StringVar()
filename_field = Entry(main, textvariable=filename, width=50)
filename_field.bind('<Return>', check_settings)
filename_field.pack(side=TOP, anchor=N)

Label(main, text='Format de sortie:').pack(side=TOP, anchor=W)

f = StringVar()
f.set('PNG')

f_jpeg = Radiobutton(main, text='JPEG', variable=f, value='JPEG')
f_jpeg.pack(side=TOP, anchor=W)
f_png = Radiobutton(main, text='PNG', variable=f, value='PNG')
f_png.pack(side=TOP, anchor=W)

operation = StringVar()
operation.set('Choisir une opération à réaliser')
OptionMenu(main, operation,
           'Conversion en niveaux de gris',
           'Détection des contours',
           'Négatif',
           'Embossage',
           'Stéganographie (encodage)',
           'Stéganographie (décodage)').pack()


accept = Button(main, text='Valider', command=check_settings)

base = IntVar()
base.set(2)
encoding_select = [] #Liste qui contient les différents boutons d'encodage
encoding_select.append(Label(main, text='Merci de choisir un base numérique pour l\'encodage:'))
encoding_select.append(Radiobutton(main, text='Binaire', variable=base, value=2))
encoding_select.append(Radiobutton(main, text='Base 4', variable=base, value=4))
encoding_select.append(Radiobutton(main, text='Hexadécimal', variable=base, value=16))

def if_steg():
    """
    Fonction qui permet d'afficher ou d'effacer les options de stéganographie, selon l'opération choisie.
    Cette fonction doit être lancée dans un thread à part.
    """   
    accept.pack(anchor=S)
    selected = False
    while not master.stop:
        if operation.get().startswith('Stéganographie') and not selected:
            f_jpeg.config(state=DISABLED)
            f_png.select()
            selected = True
            accept.pack_forget()
            
            for i in encoding_select:
                i.pack(side=TOP, anchor=W)
            
            accept.pack(anchor=S)
            #accept = Button(master, text='Valider', command=check_settings).pack(anchor=S)
        elif not operation.get().startswith('Stéganographie') and selected:
            selected = False
            for i in encoding_select:
                f_jpeg.config(state=NORMAL)
                i.pack_forget()

setattr(master, 'stop', False)
steg = Thread(target=if_steg, daemon=True)
steg.start()

mainloop()

setattr(master, 'stop', True) #Ceci donne au thread steg l'information que le programme a été arrêté
sys.exit(1)
