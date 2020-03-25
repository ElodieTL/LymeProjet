from tkinter import filedialog
from tkinter.tix import *
from pretraitements import *


""" Fonction permettant d'extraire les informations demandées par l'utilisateur dans l'application (après avoir cliqué OK). """
def getValues():
    # Créer une liste vide des déterminants qui seront traités.
    detsList = []

    # Ajouter l'état des checkBoxes (1 ou 0) dans la liste de déterminants à traiter.
    detsList.append(varForet.get())
    detsList.append(varZonesHumides.get())
    detsList.append(varEau.get())
    detsList.append(varParcs.get())
    detsList.append(varZonesAgricoles.get())

    # Créer une liste vide des sources qui seront traitées.
    sourcesListMaster = []

    # Ajouter les sources sélectionnées par l'utilisateur, pour chaque déterminant.
    for det in range(len(detsList)):
        sourcesListDet = []
        if det == 0:
            for source in listForet.curselection():
                sourcesListDet.append(listForet.get(source))

        elif det == 1:
            for source in listZonesHumides.curselection():
                sourcesListDet.append(listZonesHumides.get(source))

        elif det == 2:
            for source in listEau.curselection():
                sourcesListDet.append(listEau.get(source))

        elif det == 3:
            for source in listParcs.curselection():
                sourcesListDet.append(listParcs.get(source))

        elif det == 4:
            for source in listZonesAgricoles.curselection():
                sourcesListDet.append(listZonesAgricoles.get(source))

        sourcesListMaster.append(sourcesListDet)

    # Récupérer le répertoire choisi par l'utilisateur.
    dataDir = entryDir.get()

    # Récupérer le fichier vectoriel de référence choisi par l'utilisateur.
    vectorBase = entryVec.get()

    # Récupérer le raster de référence choisi par l'utilisateur.
    rasterBase = entryRaster.get()

    # Récupérer la dimension d'un pixel.
    pixelSize = entryPixel.get()

    # Fermer l'interface graphique.
    mainWindow.destroy()

    # Appeler la fonction principale.
    main(dataDir, vectorBase, rasterBase, detsList, sourcesListMaster, pixelSize)


""" Fonction permettant de récupérer le chemin du répertoire où seront enregistrées les données. """
def getDir():
    mainWindow.directory = filedialog.askdirectory(initialdir="/")
    entryDir.delete(0, END)
    entryDir.insert(0, mainWindow.directory.replace("/", "\\"))


""" Fonction permettant de récupérer le chemin du fichier vectoriel de référence. """
def getFileVector():
    mainWindow.filename = filedialog.askopenfilename(initialdir="/")
    entryVec.delete(0, END)
    entryVec.insert(0, mainWindow.filename.replace("/", "\\"))


""" Fonction permettant de récupérer le chemin du raster de référence. """
def getFileRaster():
    mainWindow.filename = filedialog.askopenfilename(initialdir="/")
    entryRaster.delete(0, END)
    entryRaster.insert(0, mainWindow.filename.replace("/", "\\"))


""" Fonction permettant de lancer les traitements. """
# dataDir: String représentant le répertoire où seront enregistrées les données.
# ROIPathVector: String représentant le chemin du fichier vectoriel de référence.
# ROIPathRaster: String représentant le chemin du fichier raster de référence.
# detList: Liste contenant les déterminants devant être traités.
# sourcesList: Liste contenant les sources de données devant être traitées.
# pixelSize: String représentant la taille d'un pixel (utilisé pour les noms de fichiers).
def main(dataDir, ROIPathVector, ROIPathRaster, detList, sourcesList, pixelSize):
    # Lecture des données du fichier vectoriel de référence.
    ROIDataVector = gpd.read_file(ROIPathVector)

    # Transformer la composante géométrique de la donnée vectorielle de référence en format json.
    ROIDataVectorJson = geoToJson(ROIDataVector)

    # Extraire le code EPSG (la projection) de la donnée vectorielle de référence sous deux formats.
    ROICRS, ROICRSStr = extractEPSGVector(ROIDataVector)

    # Si le code EPSG de la donnée vectielle de référence est connu, on poursuit. Sinon, on ne peut poursuivre.
    if ROICRS is not None:
        # Pour chaque déterminant de la liste de déterminants devant être traités.
        for det in range(len(detList)):
            # Si le déterminant courant doit être traité.
            if detList[det] == 1:
                # On récupère la liste de sources correspondantes.
                sources = sourcesList[det]

                # On lance les prétraitements pour le déterminant et les sources courants.
                pretraitements(dataDir, det, sources, pixelSize, ROICRSStr, ROICRS, ROIPathRaster, ROIDataVector, ROIDataVectorJson)

    else:
        print("No projection detected for ROI. Impossible to proceed.")


if __name__ == "__main__":
    # Initialisation de la fenêtre principale incluant le titre et la taille.
    mainWindow = Tk()
    mainWindow.title("Fusion et classification de déterminants environnementaux")
    mainWindow.geometry("260x500")

    # Initialisation d'une barre de défilement.
    scrollbar = Scrollbar(mainWindow)

    # Initialisation d'un canevas lié à la barre de défilement.
    canvas = Canvas(mainWindow, yscrollcommand=scrollbar.set)

    # Configuration de la barre de défilement.
    scrollbar.config(command=canvas.yview)
    scrollbar.pack(side=RIGHT, fill=Y)

    # Initialisation d'un cadre contenu à l'intérieur du canevas.
    frame = Frame(canvas)
    canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)

    # Ajout du canevas à la fenètre principale.
    canvas.create_window(0, 0, window=frame, anchor=NW)

    # Ajout d'un sous-titre à la fenêtre.
    labelTitre = Label(frame, text="Maladie de Lyme")
    labelTitre.grid(row=0, columnspan=4)

    # Ajout d'une légende pour les déterminants.
    labelDet = Label(frame, text="Déterminant")
    labelDet.grid(row=1, column=0)

    # Ajout d'une légende pour les sources.
    labelSources = Label(frame, text="Source(s)")
    labelSources.grid(row=1, column=2, columnspan=2)

    # Ajout d'une légende, d'une case à cocher et d'une liste de sources pour le déterminant Forêt.
    labelForet = Label(frame, text="Forêt")
    labelForet.grid(row=2, column=0)
    varForet = IntVar()
    checkForet = Checkbutton(frame, variable=varForet)
    checkForet.grid(row=2, column=1)
    listForet = Listbox(frame, selectmode=MULTIPLE, exportselection=0)
    listForet.grid(row=2, column=2, columnspan=2)
    listForet.insert(END, "RN Canada")

    # Ajout d'une légende, d'une case à cocher et d'une liste de sources pour le déterminant Zones humides.
    labelZonesHumides = Label(frame, text="Zones humides")
    labelZonesHumides.grid(row=3, column=0)
    varZonesHumides = IntVar()
    checkZonesHumides = Checkbutton(frame, variable=varZonesHumides)
    checkZonesHumides.grid(row=3, column=1)
    listZonesHumides = Listbox(frame, selectmode=MULTIPLE, exportselection=0)
    listZonesHumides.grid(row=3, column=2, columnspan=2)
    listZonesHumides.insert(END, "Canards illimités")

    # Ajout d'une légende, d'une case à cocher et d'une liste de sources pour le déterminant Forêt.
    labelEau = Label(frame, text="Eau")
    labelEau.grid(row=4, column=0)
    varEau = IntVar()
    checkEau = Checkbutton(frame, variable=varEau)
    checkEau.grid(row=4, column=1)
    listEau = Listbox(frame, selectmode=MULTIPLE, exportselection=0)
    listEau.grid(row=4, column=2, columnspan=2)
    listEau.insert(END, "CanVec")

    # Ajout d'une légende, d'une case à cocher et d'une liste de sources pour le déterminant Eau.
    labelParcs = Label(frame, text="Parcs")
    labelParcs.grid(row=5, column=0)
    varParcs = IntVar()
    checkParcs = Checkbutton(frame, variable=varParcs)
    checkParcs.grid(row=5, column=1)
    listParcs = Listbox(frame, selectmode=MULTIPLE, exportselection=0)
    listParcs.grid(row=5, column=2, columnspan=2)
    listParcs.insert(END, "MERN")

    # Ajout d'une légende, d'une case à cocher et d'une liste de sources pour le déterminant Zones agricoles.
    labelZonesAgricoles = Label(frame, text="Zones agricoles")
    labelZonesAgricoles.grid(row=6, column=0)
    varZonesAgricoles = IntVar()
    checkZonesAgricoles = Checkbutton(frame, variable=varZonesAgricoles)
    checkZonesAgricoles.grid(row=6, column=1)
    listZonesAgricoles = Listbox(frame, selectmode=MULTIPLE, exportselection=0)
    listZonesAgricoles.grid(row=6, column=2, columnspan=2)
    listZonesAgricoles.insert(END, "CPTAQ")

    # Ajout d'une entrée et d'un bouton pour entrer le chemin vers le répertoire où seront enregistré les données.
    labelDir = Label(frame, text="Data Directory:")
    labelDir.grid(row=7, column=0)
    entryDir = Entry(frame)
    entryDir.grid(row=7, column=1, columnspan=2)
    buttonDir = Button(frame, text="...", command=getDir)
    buttonDir.grid(row=7, column=3)
    #entryDir.insert(END, "D:\Donnees")
    entryDir.insert(END, "Z:\GMT3051\Donnees")

    # Ajout d'une entrée et d'un bouton pour entrer le chemin vers le fichier vectoriel de référence.
    labelVec = Label(frame, text="ROI Vector:")
    labelVec.grid(row=8, column=0)
    entryVec = Entry(frame)
    entryVec.grid(row=8, column=1, columnspan=2)
    buttonVec = Button(frame, text="...", command=getFileVector)
    buttonVec.grid(row=8, column=3)
    #entryVec.insert(END, "Z:\MALAM357\GMT-3051 Projet en génie géomatique II\LymeProjet\ROI\ROI_Projet_Genie_Maladies_Vectorielles_v2.shp")
    entryVec.insert(END, "Z:\GMT3051\ROI\ROI_Projet_Genie_Maladies_Vectorielles_v2.shp")

    # Ajout d'une entrée et d'un bouton pour entrer le chemin vers le fichier raster de référence.
    labelRaster = Label(frame, text="ROI Raster:")
    labelRaster.grid(row=9, column=0)
    entryRaster = Entry(frame)
    entryRaster.grid(row=9, column=1, columnspan=2)
    buttonRaster = Button(frame, text="...", command=getFileRaster)
    buttonRaster.grid(row=9, column=3)
    #entryRaster.insert(END, "Z:\MALAM357\GMT-3051 Projet en génie géomatique II\LymeProjet\ROI\ROI_Projet_Genie_Maladies_Vectorielles_v2_30.tif")
    entryRaster.insert(END, "Z:\GMT3051\ROI\ROI_Projet_Genie_Maladies_Vectorielles_v2_30.tif")

    # Ajout d'une entrée et d'un bouton pour entrer une taille de pixel.
    labelPixel = Label(frame, text="Pixel Size:")
    labelPixel.grid(row=10, column=0)
    entryPixel = Entry(frame)
    entryPixel.grid(row=10, column=1, columnspan=2)
    entryPixel.insert(END, "30")

    # Ajout de deux boutons pour poursuivre et pour quitter.
    buttonOK = Button(frame, text="OK", command=getValues)
    buttonOK.grid(row=11, column=1)
    buttonQuit = Button(frame, text="Quit", command=sys.exit)
    buttonQuit.grid(row=11, column=2)

    mainWindow.update()
    canvas.config(scrollregion=canvas.bbox(ALL))

    mainWindow.mainloop()
