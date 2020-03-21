from generic import *
from tkinter import *
from tkinter import filedialog
from tkinter.tix import *
from ZoneHumide import *
from detForet import *
from park import *
from Eau import *
from RasterData import *
from vecteurData import *

# Fonction permettant d'extraire les informations demandées par l'utilisateur dans l'application.
def getValues():
    # Créer une liste vide des déterminants qui seront traités.
    detsList = []

    # Ajouter l'état des checkBoxes dans la liste de déterminants à traiter.
    detsList.append(varForet.get())
    detsList.append(varZonesHumides.get())
    detsList.append(varEau.get())
    detsList.append(varParcs.get())

    # Créer une liste vide des sources qui seront traitées.
    sourcesListMaster = []

    # Ajouter les sources sélectionnées par l'utilisateur, pour chaque déterminant.
    for i in range(len(detsList)):
        sourcesListDet = []
        if i == 0:
            for id in listForet.curselection():
                sourcesListDet.append(listForet.get(id))

        elif i == 1:
            for id in listZonesHumides.curselection():
                sourcesListDet.append(listZonesHumides.get(id))

        elif i == 2:
            for id in listEau.curselection():
                sourcesListDet.append(listEau.get(id))

        elif i == 3:
            for id in listParcs.curselection():
                sourcesListDet.append(listParcs.get(id))

        sourcesListMaster.append(sourcesListDet)

    # Récupérer le répertoire entré par l'utilisateur.
    dataDir = entryDir.get()

    # Récupérer le fichier vectoriel de référence entré par l'utilisateur.
    vectorBase = entryVec.get()

    # Récupérer le raster de référence entré par l'utilisateur.
    rasterBase = entryRaster.get()

    # Récupérer la dimension d'un pixel.
    pixelSize = entryPixel.get()

    # Fermer la fenêtre.
    mainWindow.destroy()

    # Appeler la fonction principale.
    main(dataDir, vectorBase, rasterBase, detsList, sourcesListMaster, pixelSize)


# Fonction permettant de récupérer le nom du répertoire où seront enregistrées les données.
def getDir():
    mainWindow.directory = filedialog.askdirectory(initialdir="/")
    entryDir.delete(0, END)
    entryDir.insert(0, mainWindow.directory.replace("/", "\\"))


# Fonction permettant de récupérer le nom du raster de référence.
def getFileVector():
    mainWindow.filename = filedialog.askopenfilename(initialdir="/")
    entryVec.delete(0, END)
    entryVec.insert(0, mainWindow.filename.replace("/", "\\"))


# Fonction permettant de récupérer le nom du raster de référence.
def getFileRaster():
    mainWindow.filename = filedialog.askopenfilename(initialdir="/")
    entryRaster.delete(0, END)
    entryRaster.insert(0, mainWindow.filename.replace("/", "\\"))


def main(dataDir, ROIPathVector, ROIPathRaster, detList, sourcesList, pixelSize):
    # Lecture des données du fichier vectoriel représentant la zone d'intérêt.
    ROIDataVector = gpd.read_file(ROIPathVector)

    # Transformer la composante géométrique de la donnée vectorielle en format json.
    ROIDataVectorJson = geoToJson(ROIDataVector)

    # Extraire le code EPSG (la projection) de la zone d'intérêt.
    ROICRS, ROICRSStr = extractEPSGVector(ROIDataVector)

    if ROICRS is not None:
        if detList[0] == 1:
            sources = sourcesList[0]
            """ Traitement des données pour le déterminant Forêt """
            RasterData(dataDir, "Foret", sources, pixelSize, ROICRSStr, ROICRS, ROIPathRaster, ROIDataVectorJson)

        if detList[1] == 1:
            sources = sourcesList[1]
            """ Traitement des données pour le déterminant Zones humides """
            vecteurData(dataDir, "Zones humides", sources, pixelSize, ROICRSStr, ROICRS, ROIPathRaster, ROIDataVector)

        if detList[2] == 1:
            sources = sourcesList[2]
            """ Traitement des données pour le déterminant Eau """
            vecteurData(dataDir, "Eau", sources, pixelSize, ROICRSStr, ROICRS, ROIPathRaster, ROIDataVector)

        if detList[3] == 1:
            sources = sourcesList[3]
            """ Traitement des données pour le déterminant Parcs """
            vecteurData(dataDir, "Parcs", sources, pixelSize, ROICRSStr, ROICRS, ROIPathRaster, ROIDataVector)

    else:
        print("No projection detected for ROI. Impossible to proceed.")


if __name__ == "__main__":
    mainWindow = Tk()
    mainWindow.title("Fusion et classification de déterminants environnementaux")
    mainWindow.geometry("260x500")

    scrollbar = Scrollbar(mainWindow)

    canvas = Canvas(mainWindow, yscrollcommand=scrollbar.set)

    scrollbar.config(command=canvas.yview)
    scrollbar.pack(side=RIGHT, fill=Y)

    frame = Frame(canvas)
    canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)

    canvas.create_window(0, 0, window=frame, anchor=NW)

    labelTitre = Label(frame, text="Maladie de Lyme")
    labelTitre.grid(row=0, columnspan=4)

    labelDet = Label(frame, text="Déterminant")
    labelDet.grid(row=1, column=0)

    labelSources = Label(frame, text="Source(s)")
    labelSources.grid(row=1, column=2, columnspan=2)

    labelForet = Label(frame, text="Forêt")
    labelForet.grid(row=2, column=0)
    varForet = IntVar()
    checkForet = Checkbutton(frame, variable=varForet)
    checkForet.grid(row=2, column=1)
    listForet = Listbox(frame, selectmode=MULTIPLE, exportselection=0)
    listForet.grid(row=2, column=2, columnspan=2)
    listForet.insert(END, "RN Canada")

    labelZonesHumides = Label(frame, text="Zones humides")
    labelZonesHumides.grid(row=3, column=0)
    varZonesHumides = IntVar()
    checkZonesHumides = Checkbutton(frame, variable=varZonesHumides)
    checkZonesHumides.grid(row=3, column=1)
    listZonesHumides = Listbox(frame, selectmode=MULTIPLE, exportselection=0)
    listZonesHumides.grid(row=3, column=2, columnspan=2)
    listZonesHumides.insert(END, "Canards illimités")

    labelEau = Label(frame, text="Eau")
    labelEau.grid(row=4, column=0)
    varEau = IntVar()
    checkEau = Checkbutton(frame, variable=varEau)
    checkEau.grid(row=4, column=1)
    listEau = Listbox(frame, selectmode=MULTIPLE, exportselection=0)
    listEau.grid(row=4, column=2, columnspan=2)
    listEau.insert(END, "CanVec")

    labelParcs = Label(frame, text="Parcs")
    labelParcs.grid(row=5, column=0)
    varParcs = IntVar()
    checkParcs = Checkbutton(frame, variable=varParcs)
    checkParcs.grid(row=5, column=1)
    listParcs = Listbox(frame, selectmode=MULTIPLE, exportselection=0)
    listParcs.grid(row=5, column=2, columnspan=2)
    listParcs.insert(END, "MERN")

    labelDir = Label(frame, text="Data Directory:")
    labelDir.grid(row=6, column=0)
    entryDir = Entry(frame)

    entryDir.grid(row=6, column=1, columnspan=2)
    buttonDir = Button(frame, text="...", command=getDir)
    buttonDir.grid(row=6, column=3)
    entryDir.insert(END, 'Z:\GALAL35\Projet_lyme\Donnees')
    labelVec = Label(frame, text="ROI Vector:")
    labelVec.grid(row=7, column=0)
    entryVec = Entry(frame)
    entryVec.insert(END, 'Z:\GALAL35\Projet_lyme\LymeProjet\ROI\ROI_Projet_Genie_Maladies_Vectorielles_v2.shp')
    entryVec.grid(row=7, column=1, columnspan=2)
    buttonVec = Button(frame, text="...", command=getFileVector)
    buttonVec.grid(row=7, column=3)

    labelRaster = Label(frame, text="ROI Raster:")
    labelRaster.grid(row=8, column=0)
    entryRaster = Entry(frame)
    entryRaster.insert(END, 'Z:\GALAL35\Projet_lyme\Donnees\ROI_Projet_Genie_Maladies_Vectorielles_v2_30.tif')
    entryRaster.grid(row=8, column=1, columnspan=2)
    buttonRaster = Button(frame, text="...", command=getFileRaster)
    buttonRaster.grid(row=8, column=3)

    labelPixel = Label(frame, text="Pixel Size:")
    labelPixel.grid(row=9, column=0)
    entryPixel = Entry(frame)
    entryPixel.insert(END, '30')
    entryPixel.grid(row=9, column=1, columnspan=2)

    buttonOK = Button(frame, text="OK", command=getValues)
    buttonOK.grid(row=10, column=1)
    buttonQuit = Button(frame, text="Quit", command=sys.exit)
    buttonQuit.grid(row=10, column=2)

    mainWindow.update()
    canvas.config(scrollregion=canvas.bbox(ALL))

    mainWindow.mainloop()
