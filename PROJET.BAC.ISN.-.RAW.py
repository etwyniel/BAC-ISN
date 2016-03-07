from random import randrange
from os import system
from time import sleep

def ppm_to_list(file):
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
    dim = data[i:data.index(b'\n', i)].decode().split(' ')
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
    values = ['0' * (4-len(hex(d))) + hex(d)[2:] for d in data[n:]]

    #On revoie les dimensions et les pixels dans un tuple
    return dim, values

def header(file, dim):
    #Ouvrir en "wb+" permet d'effacer le contenu du fichier avant d'y accéder en mode binaire
    image = open(file, "wb+")
    image.write(b"P6\n# CREATOR: ETWYNIEL FILTER v2.0\n")
    #On utilise la liste dim qui contient la résolution de l'image à transformer, pour écrire l'en-tete
    #On encode ces données pour qu'elles puissent être stockées dans le fichier binaire
    image.write((str(dim[0])+" "+str(dim[1])+"\n").encode())
    image.write(b"255\n")
    #En mode écriture, close() est indispensable pour que le contenu des instructions write() soit écrit dans le fichier
    image.close()

def steg_encode(file):
    #On récupère les dimensions de l'image ainsi que les valeurs de ses pixels
    data = ppm_to_list(file)
    dim = data[0]
    pixels = data[1]

    #On crée un nouveau fichier dans lequel on écrit l'en-tête
    new_filename = file.split('.')[0] + ' - steg.ppm'
    header(new_filename, [dim[0] * 2, dim[1]])
    #On rouvre le fichier en mode 'ab' pour pouvoir ajouter de données à la suite de l'en-tête
    image = open(new_filename, 'ab')

    #On prévient l'utilisateur que le traitement de son image a commencé
    print('Traitement de l\'image en cours...')
    
    #On sépare chaque octet en deux digits hexadécimaux (4 bits chacuns) que l'on ajoute à la suite de deux digits hexadecimaux aléatoires
    for color in pixels:
        for a in range(2):
            byte = hex(randrange(16))[2:] +  color[a]
            #On convertit ce nouvel octet en entier, pour ensuite le convertir en octet binaire, qui peut être écrit dans le fichier.
            image.write(bytes([int(byte, 16)]))
    #Une fois la stéganographie terminée, on referme le fichier pour appliquer les changements
    image.close()

def steg_decode(file):
    #On récupère les dimensions de l'image ainsi que les valeurs de ses pixels
    data = ppm_to_list(file)
    dim = data[0]
    pixels = data[1]

    #On crée un nouveau fichier dans lequel on écrit l'en-tête
    new_filename = file.split('.')[0] + ' - decoded.ppm'
    header(new_filename, [dim[0] * 2, dim[1]])
    #On rouvre le fichier en mode 'ab' pour pouvoir ajouter de données à la suite de l'en-tête
    image = open(new_filename, 'ab')

    #On prévient l'utilisateur que le traitement de son image a commencé
    print('Traitement de l\'image en cours...')
    
    #Pour chaque valeur de l'image finale, on recupère 8 LSBs consécutifs
    #                                           Least Significant Bit
    for a in range(0, int(dim[1] * dim[0] * 3), 2):
        byte = ''
        for bit in range(2):
            byte += pixels[a+bit][1]
        #On stocke les valeurs décodées dans le nouveau fichier
        image.write(bytes([int(byte, 16)]))

    #On ferme le fichier encodé et le fichier décodé
    image.close()

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
        print("Opération à effectuer:\n1) Conversion en nuances de gris\
\n2) Détection des contours\n3) Stéganographie\
\n4) Décodage d'une stéganographie")
        choice = input("Opération : ")

        if choice == "1":
            grayLevels(file)
            break
        elif choice == "2":
            #BLandWH(file)
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
