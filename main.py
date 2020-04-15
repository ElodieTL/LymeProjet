from tkinter import filedialog
from tkinter.tix import *
from pretraitements import *
from fusion import *


""" Fonction permettant d'extraire les informations demandées par l'utilisateur dans l'application (après avoir cliqué OK). """
def getValues():
    # Créer une liste vide des déterminants qui devront être traités.
    listDets = []

    # Ajouter l'état des checkBoxes (1 ou 0) dans la liste de déterminants à traiter.
    listDets.append(varForet.get())
    listDets.append(varZonesHumides.get())
    listDets.append(varEau.get())
    listDets.append(varParcs.get())
    listDets.append(varZonesAgricoles.get())
    listDets.append(varVoiesCommunication.get())
    listDets.append(varZonesAnthropisées.get())
    listDets.append(varCouvertureSol.get())

    # Créer une liste vide de la priorité des déterminants qui devront être traités.
    listPriorites = []

    # Ajouter la priorité spécifiée pour chacun des déterminants à la liste.
    listPriorites.append(prioriteForet.get())
    listPriorites.append(prioriteZonesHumides.get())
    listPriorites.append(prioriteEau.get())
    listPriorites.append(prioriteParcs.get())
    listPriorites.append(prioriteZonesAgricoles.get())
    listPriorites.append(prioriteVoiesCommunication.get())
    listPriorites.append(prioriteZonesAnthropisées.get())
    listPriorites.append(prioriteCouvertureSol.get())

    # Créer une liste vide des sources qui seront traitées.
    listSourcesAll = []

    # Ajouter les sources sélectionnées par l'utilisateur, pour chaque déterminant.
    for noDet in range(len(listDets)):
        listSourcesDet = []

        if noDet == 0:
            for source in listForet.curselection():
                listSourcesDet.append(listForet.get(source))

        elif noDet == 1:
            for source in listZonesHumides.curselection():
                listSourcesDet.append(listZonesHumides.get(source))

        elif noDet == 2:
            for source in listEau.curselection():
                listSourcesDet.append(listEau.get(source))

        elif noDet == 3:
            for source in listParcs.curselection():
                listSourcesDet.append(listParcs.get(source))

        elif noDet == 4:
            for source in listZonesAgricoles.curselection():
                listSourcesDet.append(listZonesAgricoles.get(source))

        elif noDet == 5:
            for source in listVoiesCommunication.curselection():
                listSourcesDet.append(listVoiesCommunication.get(source))

        elif noDet == 6:
            for source in listZonesAnthropisées.curselection():
                listSourcesDet.append(listZonesAnthropisées.get(source))

        elif noDet == 7:
            for source in listCouvertureSol.curselection():
                listSourcesDet.append(listCouvertureSol.get(source))

        listSourcesAll.append(listSourcesDet)

    # Récupérer le répertoire choisi par l'utilisateur.
    dataDir = entryDir.get()

    # Récupérer le fichier vectoriel de référence choisi par l'utilisateur.
    baseVector = entryVec.get()

    # Récupérer le raster de référence choisi par l'utilisateur.
    baseRaster = entryRaster.get()

    # Récupérer la dimension d'un pixel.
    pixelSize = entryPixel.get()

    # Fermer l'interface graphique.
    mainWindow.destroy()

    # Appeler la fonction principale.
    main(dataDir, baseVector, baseRaster, listDets, listPriorites, listSourcesAll, pixelSize)


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
# ROIVectorPath: String représentant le chemin du fichier vectoriel de référence.
# ROIRasterPath: String représentant le chemin du fichier raster de référence.
# listDets: Liste contenant les déterminants devant être traités.
# listPriorites: Liste contenant l'ordre de priorité des déterminants.
# listSources: Liste contenant les sources de données devant être traitées.
# pixelSize: String représentant la taille d'un pixel (utilisé pour les noms de fichiers).
def main(dataDir, ROIVectorPath, ROIRasterPath, listDets, listPriorites, listSources, pixelSize):
    start = time.time()

    # Lecture des données du fichier vectoriel de référence.
    ROIVectorData = gpd.read_file(ROIVectorPath)

    # Transformer la composante géométrique de la donnée vectorielle de référence en format json.
    ROIVectorDataJson = geoToJson(ROIVectorData)

    # Extraire le code EPSG (la projection) de la donnée vectorielle de référence sous deux formats.
    ROICRS, ROICRSStr = extractEPSGVector(ROIVectorData)

    # Si le code EPSG de la donnée vectielle de référence est connu, on poursuit. Sinon, on ne peut poursuivre.
    if ROICRS is not None:
        listPathIntra = []  # Liste de listes de tous les rasters devant être utilisés pour les fusions intra-déterminant.

        # Pour chaque déterminant de la liste de déterminants devant être traités.
        for noDet in range(len(listDets)):
            # Si le déterminant courant doit être traité (1).
            if listDets[noDet] == 1:
                # On récupère la liste de sources correspondantes.
                listSourcesDet = listSources[noDet]

                # On lance les prétraitements pour le déterminant et les sources courants. On obtient une liste des rasters pertinents.
                listTemp = pretraitements(dataDir, noDet, listSourcesDet, pixelSize, ROICRSStr, ROICRS, ROIRasterPath, ROIVectorData, ROIVectorDataJson)

                # On ajoute le numéro du déterminant et la liste de rasters à fusionner.
                listPathIntra.append([noDet, listTemp])

    else:
        print("No projection detected for ROI. Impossible to proceed.")

    # Fusion intra déterminant.
    listPathInter = []  # Liste de listes de tous les rasters devant être utilisés pour les fusions inter-déterminants.
    for list in range(len(listPathIntra)):
        noDet = listPathIntra[list][0]
        if noDet == 0:
            raster = foret(listPathIntra[list][1][0], listPathIntra[list][1][1], listPathIntra[list][1][2], os.path.dirname(listPathIntra[list][1][1]))
            listPathInter.append([noDet, int(listPriorites[noDet]), raster])

        else:
            if len(listPathIntra[list][1]) > 1:
                raster = fusionIntra(dataDir, listPathIntra[list], noDet)
                listPathInter.append([noDet, int(listPriorites[noDet]), raster])

            else:
                listPathInter.append([noDet, int(listPriorites[noDet]), listPathIntra[list][1][0]])

    fusionInter(dataDir, listPathInter)

    colorer(raster)

    end = time.time()

    print("Secondes écoulées: " + str(end - start) + ".")

        
if __name__ == "__main__":
    # Initialisation de la fenêtre principale incluant le titre et la taille.
    mainWindow = Tk()
    mainWindow.title("Fusion et classification de déterminants environnementaux")
    mainWindow.geometry("370x500")

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
    labelTitre.grid(row=0, columnspan=5)

    # Ajout d'une légende pour les déterminants.
    labelDet = Label(frame, text="Déterminant")
    labelDet.grid(row=1, column=0)

    # Ajout d'une légende pour les sources.
    labelSources = Label(frame, text="Source(s)")
    labelSources.grid(row=1, column=2, columnspan=2)

    # Ajout d'une légende pour les priorités.
    labelPriorite = Label(frame, text="Priorité(s)")
    labelPriorite.grid(row=1, column=4)

    listHeight = 3

    # Ajout d'une légende, d'une case à cocher et d'une liste de sources pour le déterminant Forêt.
    labelForet = Label(frame, text="Forêt")
    labelForet.grid(row=2, column=0)
    varForet = IntVar()
    checkForet = Checkbutton(frame, variable=varForet)
    checkForet.grid(row=2, column=1)
    listForet = Listbox(frame, selectmode=MULTIPLE, height=listHeight, exportselection=0)
    listForet.grid(row=2, column=2, columnspan=2)
    listForet.insert(END, "RN Canada")
    content = StringVar()
    prioriteForet = Entry(frame, textvariable=content)
    prioriteForet.config(width=2)
    prioriteForet.grid(row=2, column=4)

    # Ajout d'une légende, d'une case à cocher et d'une liste de sources pour le déterminant Zones humides.
    labelZonesHumides = Label(frame, text="Zones humides")
    labelZonesHumides.grid(row=3, column=0)
    varZonesHumides = IntVar()
    checkZonesHumides = Checkbutton(frame, variable=varZonesHumides)
    checkZonesHumides.grid(row=3, column=1)
    listZonesHumides = Listbox(frame, selectmode=MULTIPLE,height=listHeight, exportselection=0)
    listZonesHumides.grid(row=3, column=2, columnspan=2)
    listZonesHumides.insert(END, "Canards illimités")
    content = StringVar()
    prioriteZonesHumides = Entry(frame, textvariable=content)
    prioriteZonesHumides.config(width=2)
    prioriteZonesHumides.grid(row=3, column=4)

    # Ajout d'une légende, d'une case à cocher et d'une liste de sources pour le déterminant Eau.
    labelEau = Label(frame, text="Eau")
    labelEau.grid(row=4, column=0)
    varEau = IntVar()
    checkEau = Checkbutton(frame, variable=varEau)
    checkEau.grid(row=4, column=1)
    listEau = Listbox(frame, selectmode=MULTIPLE,height=listHeight, exportselection=0)
    listEau.grid(row=4, column=2, columnspan=2)
    listEau.insert(END, "CanVec")
    content = StringVar()
    prioriteEau = Entry(frame, textvariable=content)
    prioriteEau.config(width=2)
    prioriteEau.grid(row=4, column=4)

    # Ajout d'une légende, d'une case à cocher et d'une liste de sources pour le déterminant Parcs.
    labelParcs = Label(frame, text="Parcs")
    labelParcs.grid(row=5, column=0)
    varParcs = IntVar()
    checkParcs = Checkbutton(frame, variable=varParcs)
    checkParcs.grid(row=5, column=1)
    listParcs = Listbox(frame, selectmode=MULTIPLE,height=listHeight, exportselection=0)
    listParcs.grid(row=5, column=2, columnspan=2)
    listParcs.insert(END, "MERN")
    content = StringVar()
    prioriteParcs = Entry(frame, textvariable=content)
    prioriteParcs.config(width=2)
    prioriteParcs.grid(row=5, column=4)

    # Ajout d'une légende, d'une case à cocher et d'une liste de sources pour le déterminant Zones agricoles.
    labelZonesAgricoles = Label(frame, text="Zones agricoles")
    labelZonesAgricoles.grid(row=6, column=0)
    varZonesAgricoles = IntVar()
    checkZonesAgricoles = Checkbutton(frame, variable=varZonesAgricoles)
    checkZonesAgricoles.grid(row=6, column=1)
    listZonesAgricoles = Listbox(frame, selectmode=MULTIPLE, height=listHeight, exportselection=0)
    listZonesAgricoles.grid(row=6, column=2, columnspan=2)
    listZonesAgricoles.insert(END, "CPTAQ")
    content = StringVar()
    prioriteZonesAgricoles = Entry(frame, textvariable=content)
    prioriteZonesAgricoles.config(width=2)
    prioriteZonesAgricoles.grid(row=6, column=4)

    # Ajout d'une légende, d'une case à cocher et d'une liste de sources pour le déterminant Voies de communication.
    labelVoiesCommunication = Label(frame, text="Voies de communication")
    labelVoiesCommunication.grid(row=7, column=0)
    varVoiesCommunication = IntVar()
    checkVoiesCommunication = Checkbutton(frame, variable=varVoiesCommunication)
    checkVoiesCommunication.grid(row=7, column=1)
    listVoiesCommunication = Listbox(frame, selectmode=MULTIPLE, height=listHeight, exportselection=0)
    listVoiesCommunication.grid(row=7, column=2, columnspan=2)
    listVoiesCommunication.insert(END, "CanVec")
    content = StringVar()
    prioriteVoiesCommunication = Entry(frame, textvariable=content)
    prioriteVoiesCommunication.config(width=2)
    prioriteVoiesCommunication.grid(row=7, column=4)

    # Ajout d'une légende, d'une case à cocher et d'une liste de sources pour le déterminant Zones Anthropisées.
    labelZonesAnthropisées = Label(frame, text="Zones Anthropisées")
    labelZonesAnthropisées.grid(row=8, column=0)
    varZonesAnthropisées = IntVar()
    checkZonesAnthropisées = Checkbutton(frame, variable=varZonesAnthropisées)
    checkZonesAnthropisées.grid(row=8, column=1)
    listZonesAnthropisées = Listbox(frame, selectmode=MULTIPLE, height=listHeight, exportselection=0)
    listZonesAnthropisées.grid(row=8, column=2, columnspan=2)
    listZonesAnthropisées.insert(END, "CanVec")
    content = StringVar()
    prioriteZonesAnthropisées = Entry(frame, textvariable=content)
    prioriteZonesAnthropisées.config(width=2)
    prioriteZonesAnthropisées.grid(row=8, column=4)

    # Ajout d'une légende, d'une case à cocher et d'une liste de sources pour le déterminant Couverture du Sol.
    labelCouvertureSol = Label(frame, text="Couverture du Sol")
    labelCouvertureSol.grid(row=9, column=0)
    varCouvertureSol = IntVar()
    checkCouvertureSol = Checkbutton(frame, variable=varCouvertureSol)
    checkCouvertureSol.grid(row=9, column=1)
    listCouvertureSol = Listbox(frame, selectmode=MULTIPLE, height=listHeight, exportselection=0)
    listCouvertureSol.grid(row=9, column=2, columnspan=2)
    #listCouvertureSol.insert(END, "CanVec")
    content = StringVar()
    prioriteCouvertureSol = Entry(frame, textvariable=content)
    prioriteCouvertureSol.config(width=2)
    prioriteCouvertureSol.grid(row=9, column=4)

    # Ajout d'une entrée et d'un bouton pour entrer le chemin vers le répertoire où seront enregistré les données.
    labelDir = Label(frame, text="Data Directory:")
    labelDir.grid(row=10, column=0)
    entryDir = Entry(frame)
    entryDir.grid(row=10, column=1, columnspan=3)
    buttonDir = Button(frame, text="...", command=getDir)
    buttonDir.grid(row=10, column=4)
    entryDir.insert(END, "Z:\GMT3051\Donnees")

    # Ajout d'une entrée et d'un bouton pour entrer le chemin vers le fichier vectoriel de référence.
    labelVec = Label(frame, text="ROI Vector:")
    labelVec.grid(row=11, column=0)
    entryVec = Entry(frame)
    entryVec.grid(row=11, column=1, columnspan=3)
    buttonVec = Button(frame, text="...", command=getFileVector)
    buttonVec.grid(row=11, column=4)
    entryVec.insert(END, "Z:\GMT3051\ROI\ROI_Projet_Genie_Maladies_Vectorielles_v2.shp")

    # Ajout d'une entrée et d'un bouton pour entrer le chemin vers le fichier raster de référence.
    labelRaster = Label(frame, text="ROI Raster:")
    labelRaster.grid(row=12, column=0)
    entryRaster = Entry(frame)
    entryRaster.grid(row=12, column=1, columnspan=3)
    buttonRaster = Button(frame, text="...", command=getFileRaster)
    buttonRaster.grid(row=12, column=4)
    entryRaster.insert(END, "Z:\GMT3051\ROI\ROI_Projet_Genie_Maladies_Vectorielles_v2_30.tif")

    # Ajout d'une entrée et d'un bouton pour entrer une taille de pixel.
    labelPixel = Label(frame, text="Pixel Size:")
    labelPixel.grid(row=13, column=0)
    entryPixel = Entry(frame)
    entryPixel.grid(row=13, column=1, columnspan=3)
    entryPixel.insert(END, "30")

    # Ajout de deux boutons pour poursuivre et pour quitter.
    buttonOK = Button(frame, text="OK", command=getValues)
    buttonOK.grid(row=14, column=1)
    buttonQuit = Button(frame, text="Quit", command=sys.exit)
    buttonQuit.grid(row=14, column=2)

    mainWindow.update()
    canvas.config(scrollregion=canvas.bbox(ALL))

    mainWindow.mainloop()
