#début du programe
#on importe les modules qui nous seront utiles
from time import sleep
from math import sqrt
from os import system
from turtle import *
from random import randrange

#Cette fonction rentre dans une liste les dimensions de l'image
#et les pixels séparés en lignes
def ppmToList(file):
    #Initialisation de la variable:
    pixels = [[],[]]
    #Création de la variable image, qui permet de lire le code du fichier .ppm
    image = open(file, "r")
    #readline() lit les lignes à la suite, une à chaque itération
    image.readline()
    temp = ""
    l = ""
    h = ""
    #On ignore les commentaires éventuels, et on stocke les dimensions dans  l et h
    space = False
    while temp != "\n":
        temp = image.readline(1)
        if temp == "#":
            image.readline()
        elif temp == " ":
            space = True
        elif space == False:
            l += temp
        else:
            h += temp
    #On insère les dimensions dans la liste pixels
    pixels[0].append(int(l))
    pixels[0].append(int(h))
    image.readline()
    #Création d'une liste intermédiaire pour contenir les valeurs temporairement
    sub = []
    #Cette boucle sépare les pixels en listes individuelles, contenues dans une une liste par ligne, selon les dimensions du fichier
    for ligne in range(pixels[0][1]):
        for pixel in range(pixels[0][0]):
            r = bin(int(image.readline()))[2:]
            r = '0' * (8-len(r)) + r
            g = bin(int(image.readline()))[2:]
            g = '0' * (8-len(g)) + g
            b = bin(int(image.readline()))[2:]
            b = '0' * (8-len(b)) + b
            sub.append([r, g, b])
        pixels[1].append(sub)
        sub = []
    #Le fichier est fermé pour éviter la perte de données
    image.close()

    #La liste finale, de la forme [[x,y],[[[pix_aR,pix_aV,pix_aB],[pix_bR,pix_bV,pix_bB]],[[pix_cR,pix_cV,pix_cB],[pix_dR,pix_dV,pix_dB]],...]]
    #                                     ^-------------------ligne 1-------------------^ ^-------------------ligne 2-------------------^
    #est renvoyée comme résultat de la fonction
    return pixels


#Cette fonction définit l'en-tete du nouveau fichier.
def header(file, dim):
    #Ouvrir en "w+" permet d'effacer le contenu du fichier
    image = open(file, "w+")
    #"\n" donne l'indication de sauter une ligne
    image.write("P3\n# CREATOR: ETWYNIEL FILTER v2.0\n")
    #On utilise la liste dim qui contient la résolution de l'image à transformer, pour écrire l'en-tete
    image.write(str(dim[0])+" "+str(dim[1])+"\n")
    image.write("255\n")
    #En mode écriture, close() est indispensable pour que le contenu des instructions write() soit écrit dans le fichier
    image.close()


#Cette fonction convertit les pixels de l'image en nuances de gris.
def grayLevels(file):
    #On appelle la fonction ppmToList, et on stocke son résultat dans dat
    dat = ppmToList(file)
    #On sépare la dimension de l'image et son corps dans deux listes différentes
    dim = dat[0]
    pix = dat[1]
    #On appelle la fonction header pour créér l'en-tete du fichier
    header(file, dim)
    #On ouvre le fichier en "a", ce qui permet d'ajouter du texte à la suite de ce qui est écrit
    image = open(file, "a")
    print("Traitement de l'image en cours...")
    #On fait la moyenne de l'intensité des couleurs de chaque pixel, et on donne cette valeur aux trois octets du pixel
    for ligne in pix:
        for pixel in ligne:
             image.write((str(int((pixel[0]+pixel[1]+pixel[2])/3))+"\n")*3)    #a nouveau fermer le contenu des instructions, comme dans toutes les autres petites parties du programme
    image.close()
    
def BLandWH(file):
    #On appelle la fonction ppmToList, et on stocke son résultat dans dat
    dat = ppmToList(file)
    #On sépare la dimension de l'image et son corps dans deux listes différentes
    dim = dat[0]
    pix = dat[1]
    #On appelle la fonction header pour créér l'en-tete du fichier
    header(file, dim)
    #On ouvre le fichier en "a", ce qui permet d'ajouter du texte à la suite de ce qui est écrit
    image = open(file, "a")
    print("Traitement de l'image en cours...")
    for ligne in range(0,dim[1]):
        for col in range(0,dim[0]):
            #On ignore les lignes et les colonnes sur lesquelles on ne peut pas appliquer le filtre
            if col == 0 or col == dim[0]-1 or ligne == 0 or ligne == dim[1]-1:
                for a in range(3):
                    image.write("255\n")
                    image.flush()
            else:
                #On applique le filtre de détection des contours à l'image
                p = 8 * int(pix[ligne][col][0], 2) -\
                    int(pix[ligne-1][col-1][0], 2) -\
                    int(pix[ligne-1][col+1][0], 2) -\
                    int(pix[ligne+1][col-1][0], 2) -\
                    int(pix[ligne-1][col][0], 2) -\
                    int(pix[ligne][col-1][0], 2) -\
                    int(pix[ligne][col+1][0], 2) -\
                    int(pix[ligne+1][col][0], 2) -\
                    int(pix[ligne+1][col+1][0], 2)
                if p>255: p=255
                elif p<0: p=0
                for a in range(3):
                    image.write(str(255-p)+"\n")
                    image.flush()
    image.close()

def steg_encode(file):
    #On appelle la fonction ppmToList, et on stocke son résultat dans dat
    dat = ppmToList(file)
    #On sépare la dimension de l'image et son corps dans deux listes différentes
    dim = dat[0]
    pix = dat[1]
    new_filename = file.split('.')[0] + ' - steg.ppm'
    header(new_filename, [dim[0] * 2, dim[1]])

    image = open(new_filename, 'a')
    print('Traitement de l\'image en cours...')

    for ligne in pix:
        for pixel in ligne:
            for color in pixel:
                for a in range(2):
                    byte = ''
                    for b in range(4):
                        byte += str(randrange(2))
                    image.write(str(int(byte + color[4*a] +
                                        color[4*a+1] +
                                        color[4*a+2] +
                                        color[4*a+3],
                                        2)))
                    image.write('\n')
    image.close()
    
def steg_decode(file):
    #On ouvre l'image encodée en mode lecture
    image = open(file, 'r')
    #On ignore la première ligne ('P3'), les commentaires et la valeur maximale
    image.readline()
    a = image.readline()
    while a[0] == '#':
        a = image.readline()
    dim = a.split(' ')
    image.readline()

    #On crée un nouveau fichier pour l'image décodée
    new_filename = file.split('.')[0] + ' - decoded.ppm'
    #On y écrit l'en-tête
    header(new_filename, [int(dim[0]) / 2, int(dim[1])])
    new_image = open(new_filename, 'a')
    print('traitement en cours')
    

    #Pour chaque valeur de l'image finale, on recupère 8 LSBs consécutifs
    #                                           Least Significant Bit
    for a in range(int((int(dim[1])* int(dim[0])) * 3/2)):
        byte = ''
        for bit in range(2):
            line = image.readline()
            bits = bin(int(line))[2:]
            bits = '0' * (8-len(bits)) + bits
            byte += bits[-4:]
        #On stocke les valeurs décodées dans le nouveau fichier
        new_image.write(str(int(byte, 2)) + '\n')

    #On ferme le fichier encodé et le fichier décodé
    image.close()
    new_image.close()


#Cette commande est cosmétique, et sert à changer la couleur de la console
system("color 70")
#Boucle principale, où on demande à l'utilisateur de choisir une opération
try:
    while 1:
        #début de l interface avec l utilisateur
        print("Veuillez entrer le nom du fichier .ppm à convertir. Il doit etre sous la forme: P3\nCommentaire\nLongueur Hauteur\n255\nR\nV\nB\nR...")
        file = input("Nom du fichier : ")
        if not file.endswith('.ppm'):
            file += ".ppm"
        system("cls")
        print("Opération à effectuer:\n1) Conversion en nuances de gris\
\n2) Détection des contours\n3) Stéganographie\
\n4) Décodage d'une stéganographie")
        choice = input("Opération : ")

        if choice == "1":
            grayLevels(file)
            break
        elif choice == "2":
            BLandWH(file)
            break
        elif choice == "3":
            steg_encode(file)
            break
        elif choice == "4":
            steg_decode(file)
            break
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
sleep(5)
