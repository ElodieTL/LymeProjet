from fonctions import *


""" Fonction permettant de fusionner des rasters pour un même déterminant. """
# dataDir: String représentant le répertoire où seront enregistrées les données.
# detPaths: liste contenant le code numérique du déterminant en premier, puis une liste des rasters à fusionner.
# rasterFinal: String représentant le chemin vers le fichier raster fusionné.
# noDet: nombre représentant le numéro du déterminant.
def fusionIntra(dataDir, detPaths, noDet):
    detStr = getDet(detPaths[0])

    # Répertoire où les données seront enregistrées selon le déterminant courant.
    detDir = os.path.join(dataDir, detStr)

    rasters = detPaths[1]
    nbRasters = len(rasters)

    if nbRasters > 1:
        rasterIntermediaire = os.path.join(detDir, "intermediaire.tif")
        rasterFinal = os.path.join(detDir, "final.tif")

        if not os.path.exists(rasterFinal):
            print("Fusion intra-déterminant du déterminant " + detStr + ". Il y a " + str(nbRasters) + " rasters à fusionner.")

            for raster in range(nbRasters - 1):
                if (raster + 2) == nbRasters:  # S'il y a seulement deux rasters à fusionner ou s'il ne reste qu'à fusionner deux rasters.
                    if nbRasters == 2:
                        rasterIntermediaire = rasters[0]

                    print("          Fusion finale. Création du raster " + os.path.basename(rasterFinal) + "...")
                    rasterClassification(rasterIntermediaire, rasters[raster + 1], rasterFinal, noDet)

                    if nbRasters != 2:
                        os.remove(rasterIntermediaire)

                elif raster == 0 and nbRasters != 2:  # Si on est au premier raster et qu'il y en a plus que deux à fusionner.
                    rasterClassification(rasters[raster], rasters[raster + 1], rasterIntermediaire, noDet)
                    print("          Fusion #1...")

                else:  # Si on traite un raster autre que le premier.
                    rasterClassification(rasterIntermediaire, rasters[raster + 1], rasterIntermediaire, noDet)
                    print("          Fusion #" + str(raster + 1) + "...")

        print("Fin de la fusion intra-déterminant pour le déterminant " + detStr + ".")

        return rasterFinal

    else:
        return rasters[0]


""" Fonction permettant de fusionner des rasters provenant de déterminants différents. """
# dataDir: String représentant le chemin vers le répertoire contenant les données.
# listPathIntra: liste contenant le numéro de déterminant, la priorité et le raster à fusionner.
def fusionInter(dataDir, listPathIntra):
    listIntraAsc = sorted(listPathIntra, key=itemgetter(1))
    listIntraDesc = sorted(listPathIntra, key=itemgetter(1), reverse=True)
    nbRasters = len(listIntraDesc)
    rasters = [listIntraDesc[raster][2] for raster in range(nbRasters)]

    rasterIntermediaire = os.path.join(dataDir, "intermediaire.tif")

    fichier = "classification"
    for det in range(nbRasters):
        fichier = fichier + "_" + (getDet(listIntraAsc[det][0]))

    fichier = fichier + ".tif"
    rasterFinal = os.path.join(dataDir, fichier)

    if nbRasters > 1:
        if not os.path.exists(rasterFinal):
            ("Fusion des " + str(nbRasters) + "rasters.")

            for raster in range(nbRasters - 1):
                if (raster + 2) == nbRasters:  # S'il y a seulement deux rasters à fusionner ou s'il ne reste qu'à fusionner le raster final.
                    if nbRasters == 2:
                        rasterIntermediaire = rasters[0]

                    print("          Fusion finale. Création du raster " + os.path.basename(rasterFinal) + "...")
                    rasterClassificationTotale(rasterIntermediaire, rasters[raster + 1], rasterFinal, listIntraDesc[raster + 1][0])

                    if nbRasters != 2:
                        os.remove(rasterIntermediaire)

                elif raster == 0 and nbRasters != 2:  # Si on est au premier raster et qu'il y en a plus que deux à fusionner.
                    rasterClassificationTotale(rasters[raster], rasters[raster + 1], rasterIntermediaire, listIntraDesc[raster + 1][0])
                    print("          Fusion #1...")

                else:  # Si on traite un raster autre que le premier.
                    rasterClassificationTotale(rasterIntermediaire, rasters[raster + 1], rasterIntermediaire, listIntraDesc[raster + 1][0])
                    print("          Fusion #" + str(raster + 1) + "...")

        return rasterFinal

    else:
        print("Aucune fusion inter-déterminants à effectuer.")

        shutil.copyfile(listIntraDesc[0][2], rasterFinal)

        return rasterFinal


""" Fonction permettant de transformer un raster en NG en un raster RGB. """
# dataDir: String représentant le chemin vers le répertoire contenant les données.
# inRasterPath: String représentant le chemin vers le raster devant être coloré.
def colorer(inRasterPath):
    print("Coloration du raster classifié...")

    outPath = inRasterPath.replace(".", "_RGB.")

    if not os.path.exists(outPath):
        listCouleurs = pd.read_excel("Couleurs.xlsx")

        raster = gdal.Open(inRasterPath, gdal.GA_ReadOnly)

        rasterB1 = raster.GetRasterBand(1).ReadAsArray()
        rasterB2 = raster.GetRasterBand(1).ReadAsArray()
        rasterB3 = raster.GetRasterBand(1).ReadAsArray()

        for i in range(raster.RasterYSize):
            for j in range(raster.RasterXSize):
                ng = rasterB1[i, j]

                # Si le NG n'est pas nul.
                if ng != 0:
                    couleur = listCouleurs.loc[listCouleurs["NG"] == ng]

                    rasterB1[i, j] = couleur["R"]
                    rasterB2[i, j] = couleur["G"]
                    rasterB3[i, j] = couleur["B"]

        rasterCouleur = gdal.GetDriverByName("GTiff").Create(outPath, raster.RasterXSize, raster.RasterYSize, 3)
        rasterCouleur.GetRasterBand(1).WriteArray(rasterB1)
        rasterCouleur.GetRasterBand(2).WriteArray(rasterB2)
        rasterCouleur.GetRasterBand(3).WriteArray(rasterB3)

        rasterCouleur.SetProjection(raster.GetProjection())
        rasterCouleur.SetGeoTransform(raster.GetGeoTransform())
        rasterCouleur.FlushCache()
