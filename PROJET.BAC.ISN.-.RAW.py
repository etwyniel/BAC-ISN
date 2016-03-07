from random import randrange
from os import system
from time import sleep

def ppm_to_list(file):
    image = open(file, 'rb')
    data = image.read()
    f = data[:2].decode('utf-8')

    i = 3
    while data[i] == 35:
                a = i
                while data[a] != 10:
                        a+=1
                i = a + 1

    dim = data[i:i+15].decode().split('\n')[0].split(' ')
    dim[0] = int(dim[0])
    dim[1] = int(dim[1])

    n = i
    c = 0
    while c < 2:
                if chr(data[n]) == '\n':
                        c += 1
                n += 1

    values = data[n:]

    pixels = [[values[i], values[i+1], values[i+2]] for i in range(dim[0]*dim[1])]
    return dim, pixels

def header(file, dim):
    #Ouvrir en "w+" permet d'effacer le contenu du fichier
    image = open(file, "w+")
    #"\n" donne l'indication de sauter une ligne
    image.write("P6\n# CREATOR: ETWYNIEL FILTER v2.0\n")
    #On utilise la liste dim qui contient la résolution de l'image à transformer, pour écrire l'en-tete
    image.write(str(dim[0])+" "+str(dim[1])+"\n")
    image.write("255\n")
    #En mode écriture, close() est indispensable pour que le contenu des instructions write() soit écrit dans le fichier
    image.close()

def steg_encode(file):
    data = ppm_to_list(file)
    dim = data[0]
    pixels = data[1]

    new_filename = file.split('.')[0] + ' - steg.ppm'
    header(new_filename, [dim[0] * 2, dim[1]])

    image = open(new_filename, 'ab')
    print('Traitement de l\'image en cours...')

    for pixel in pixels:
        for color in pixel:
            color = bin(color)[2:]
            color = '0' * (8-len(color)) + color
            for a in range(2):
                byte = ''
                for b in range(4):
                    byte += str(randrange(2))
                to_write = "%c" % int(byte + color[4*a] +
                                    color[4*a+1] +
                                    color[4*a+2] +
                                    color[4*a+3],
                                    2)
                image.write(to_write.encode('utf-8'))
    image.close()

def steg_decode(file):
    data = ppm_to_list(file)
    dim = data[0]
    pixels = []
    for a in data[1]:
        pixels += a

    #On crée un nouveau fichier pour l'image décodée
    new_filename = file.split('.')[0] + ' - decoded.ppm'
    #On y écrit l'en-tête
    header(new_filename, [int(dim[0]) / 2, int(dim[1])])
    image = open(new_filename, 'ab')
    print('traitement en cours')
    

    #Pour chaque valeur de l'image finale, on recupère 8 LSBs consécutifs
    #                                           Least Significant Bit
    for a in range(int(dim[1] * dim[0] * 3/2)):
        byte = ''
        for bit in range(2):
            bits = bin(pixels[a+bit])[2:]
            bits = '0' * (8-len(bits)) + bits
            byte += bits[-4:]
        #On stocke les valeurs décodées dans le nouveau fichier
        to_write = "%c" % int(byte, 2)
        image.write(to_write.encode('utf-8'))

    #On ferme le fichier encodé et le fichier décodé
    image.close()


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
                      
except FileNotFoundError:
    print("Ce fichier n'existe pas. Veuillez entrer le nom d'un fichier .ppm (sans extension)")
except ValueError:
    print("Erreur. Veuillez vérifier que le format fichier correspond conditions requises")
except:
    print("Le programme a cessé de fonctionner.")            



print("Done")
sleep(5)
