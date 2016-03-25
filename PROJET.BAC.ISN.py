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
from Threading import Thread
#Pour effectuer simultanément des parties différentes du programme.
from math import log
#Pour éxécuter les calculs de changement de base. 
from PIL import Image
#Pour stocker les pixels d'une image dans une bibliothèque.
import sys


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

def gray_levels(file, f='PNG'):
    dim, pixels = image_to_list(file, 10)
    values = []
    if f == 'JPEG':
        ext = 'jpg'
    elif f == 'PNG':
        ext = 'png'
    new_filename = file.split('.')[0] + ' - gray.' + ext

    for x in range(0, len(pixels), 3):
        new_color = int(sum(pixels[x:x+3]) / 3)
        new_pixel = new_color, new_color, new_color
        values += [new_pixel]
            
    image = Image.new('RGB', dim)
    image.putdata(values)
    image.save('D:/' + new_filename, f)
    return image

def outline(file, f='PNG'):
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
    image.save(getcwd() + '\\' + new_filename, f)
    return image

def embossage(file, f='PNG'):
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
    dim, pixels = image_to_list(file, base)

    #On crée un nouveau fichier dans lequel on écrit l'en-tête
    new_filename = '.'.join(file.split('.')[:-1]) + ' - decoded.png'
  
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

    image = Image.new('RGBA', new_dim)
    image.putdata(values)
    image.save(getcwd() + '\\' + new_filename, 'png')
    return image
    

def negative(file, f='PNG'):
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
        filename.set('')
    except FileNotFoundError:
        no_file.pack()
        message.pack_forget()
    accept.config(state=NORMAL)
    im.show()
        
    

master = Tk()
message = Label(master)
no_file = Label(master, text='Merci d\'entrer un nom valide')
no_op = Label(master, text='Merci de choisir une opération')
master.title('BERBAECA')
title = Label(master, text='Nom du fichier:').pack(anchor=N)
filename = StringVar()
filename_field = Entry(master, textvariable=filename, width=50).pack(side=TOP, anchor=N)

Label(master, text='Format de sortie:').pack(side=TOP, anchor=W)
f = StringVar()
f.set('PNG')
f_jpeg = Radiobutton(master, text='JPEG', variable=f, value='JPEG')
f_jpeg.pack(side=TOP, anchor=W)
f_png = Radiobutton(master, text='PNG', variable=f, value='PNG')
f_png.pack(side=TOP, anchor=W)
operation = StringVar()
operation.set('Choisir une opération à réaliser')
OptionMenu(master, operation,
           'Conversion en niveaux de gris',
           'Détection des contours',
           'Négatif',
           'Embossage',
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
    while not master.stop:
        print(getattr(master, 'stop'))
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
    print('Out!')

setattr(master, 'stop', False)
steg = Thread(target=if_steg, daemon=True)
steg.start()


mainloop()
setattr(master, 'stop', True)
print(getattr(master, 'stop'))
print(steg.isAlive())
sys.exit(1)
