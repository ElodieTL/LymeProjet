from generic import *
from tkinter import *
from ZoneHumide import *
from detForet import *
from park import *
from Eau import *


def getValues():
    # Créer une liste vide des déterminants qui seront traités.
    det = []

    # Récupérer le répertoire entré par l'utilisateur.
    dir = entryDir.get()

    # Récupérer la dimension d'un pixel.
    pixelSize = entryPixel.get()

    # Ajouter l'état des checkBoxes dans la liste.
    det.append(varForet.get())
    det.append(varZonesHumides.get())
    det.append(varEau.get())
    det.append(varParcs.get())

    # Fermer la fenêtre.
    mainWindow.destroy()

    main(dir, det, pixelSize)


def quit():
    sys.exit()


def main(dir, det, pixelSize):
    # Importer et lire les données du shapelefile et du raster représentant la zone d'intérêt.
    # ROIPathVector = "X:\ELTAL8\ProjetLYME\ROI_Projet_Genie_Maladies_Vectorielles_v2/ROI_Projet_Genie_Maladies_Vectorielles_v2.shp"
    # ROIPathVector = "Z:\GALAL35\Projet_lyme\LymeProjet\ROI\ROI_Projet_Genie_Maladies_Vectorielles_v2.shp"
    ROIPathVector = "Z:\MALAM357\GMT-3051 Projet en génie géomatique II\LymeProjet\ROI\ROI_Projet_Genie_Maladies_Vectorielles_v2.shp"

    ROIPathRaster = "Z:\MALAM357\GMT-3051 Projet en génie géomatique II\LymeProjet\ROI\ROI_Projet_Genie_Maladies_Vectorielles_v2_" + str(pixelSize) + ".tif"

    ROIDataVector = gpd.read_file(ROIPathVector)

    # Transformer la composante géométrique de la donnée vectorielle en format json.
    ROIDataVectorJson = geoToJson(ROIDataVector)

    # Extraire le code EPSG (la projection) de la zone d'intérêt.
    ROICRS, ROICRSStr = extractEPSGVector(ROIDataVector)

    if ROICRS is not None:
        if det[0] == 1:
            """ Traitement des données pour le déterminant Forêt """
            foret(dir, pixelSize, ROICRSStr, ROICRS, ROIPathRaster, ROIDataVectorJson)

        if det[1] == 1:
            """ Traitement des données pour le déterminant Zones humides """
            zonesHumides(dir, pixelSize, ROICRSStr, ROICRS, ROIPathRaster, ROIDataVector)

        if det[2] == 1:
            """ Traitement des données pour le déterminant Eau """
            eau(dir, pixelSize, ROICRSStr, ROICRS, ROIPathRaster, ROIDataVector)

        if det[3] == 1:
            """ Traitement des données pour le déterminant Parcs """
            parcs(dir, pixelSize, ROICRSStr, ROICRS, ROIPathRaster, ROIDataVector)

    else:
        print("No projection detected for ROI. Impossible to proceed.")


if __name__ == "__main__":
    mainWindow = Tk()
    mainWindow.title("Fusion et classification de déterminants environnementaux")

    labelTitre = Label(mainWindow, text="Maladie de Lyme")
    labelTitre.grid(columnspan=2)

    labelForet = Label(mainWindow, text="Forêt")
    labelForet.grid(row=1)
    varForet = IntVar()
    checkForet = Checkbutton(mainWindow, variable=varForet)
    checkForet.grid(row=1, column=1)

    labelZonesHumides = Label(mainWindow, text="Zones humides")
    labelZonesHumides.grid(row=2)
    varZonesHumides = IntVar()
    checkZonesHumides = Checkbutton(mainWindow, variable=varZonesHumides)
    checkZonesHumides.grid(row=2, column=1)

    labelEau = Label(mainWindow, text="Eau")
    labelEau.grid(row=3)
    varEau = IntVar()
    checkEau = Checkbutton(mainWindow, variable=varEau)
    checkEau.grid(row=3, column=1)

    labelParcs = Label(mainWindow, text="Parcs")
    labelParcs.grid(row=4)
    varParcs = IntVar()
    checkParcs = Checkbutton(mainWindow, variable=varParcs)
    checkParcs.grid(row=4, column=1)

    labelDir = Label(mainWindow, text="Directory:")
    labelDir.grid(row=5)
    entryDir = Entry(mainWindow)
    entryDir.grid(row=5, column=1)

    labelPixel = Label(mainWindow, text="Pixel Size:")
    labelPixel.grid(row=6)
    entryPixel = Entry(mainWindow)
    entryPixel.grid(row=6, column=1)

    buttonOK = Button(mainWindow, text="OK", command=getValues)
    buttonOK.grid(row=7)
    buttonQuit = Button(mainWindow, text="Quit", command=quit)
    buttonQuit.grid(row=7, column=1)

    mainWindow.mainloop()
