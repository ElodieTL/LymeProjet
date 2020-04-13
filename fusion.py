from generic import *

""" Fonction permettant de fusionner des déterminants"""
# dir: String représentant le répertoire où seront enregistrées les données.
# detPaths: liste contenant le code numérique du déterminant en premier, puis une liste des rasters à fusionner.
# rasterFinal: String représentant le chemin vers le fichier raster fusionné.
def fusionIntra(dir, detPaths):
    det = getDet(detPaths[0])

    # Répertoire où les données seront enregistrées selon le déterminant courant.
    detDir = os.path.join(dir, det)

    rasters = detPaths[1]
    nbRasters = len(rasters)

    if nbRasters > 1:
        rasterIntermediaire = os.path.join(detDir, "intermediaire.tif")
        rasterFinal = os.path.join(detDir, "final.tif")

        if not os.path.exists(rasterFinal):
            print("Fusion intra du déterminant " + det + ". Il y a " + str(nbRasters) + " rasters à fusionner.")

            for raster in range(nbRasters - 1):
                if (raster + 2) == nbRasters:  # S'il y a seulement deux rasters à fusionner ou s'il ne reste qu'à fusionner le raster final.
                    if nbRasters == 2:
                        rasterIntermediaire = rasters[0]

                    print("Fusion finale. Création du raster " + os.path.basename(rasterFinal) + "...")
                    rasterClassification(rasterIntermediaire, rasters[raster + 1], rasterFinal)

                    if nbRasters != 2:
                        os.remove(rasterIntermediaire)

                elif raster == 0 and nbRasters != 2:  # Si on est au premier raster et qu'il y en a plus que deux à fusionner.
                    rasterClassification(rasters[raster], rasters[raster + 1], rasterIntermediaire)
                    print("Fusion #1...")

                else:  # Si on traite un raster autre que le premier.
                    rasterClassification(rasterIntermediaire, rasters[raster + 1], rasterIntermediaire)
                    print("Fusion #" + str(raster + 1) + "...")

        return rasterFinal

    else:
        return rasters[0]


def fusionInter(dataDir, listIntra):
    listIntra = sorted(listIntra, key=itemgetter(1), reverse=True)
    nbRasters = len(listIntra)
    rasters = [listIntra[raster][2] for raster in range(nbRasters)]

    if nbRasters > 1:
        rasterIntermediaire = os.path.join(dataDir, "intermediaire.tif")
        rasterFinal = os.path.join(dataDir, "classification.tif")

        if not os.path.exists(rasterFinal):
            ("Fusion des " + str(nbRasters) + ".")

            for raster in range(nbRasters - 1):
                if (raster + 2) == nbRasters:  # S'il y a seulement deux rasters à fusionner ou s'il ne reste qu'à fusionner le raster final.
                    if nbRasters == 2:
                        rasterIntermediaire = rasters[0]

                    print("Fusion finale. Création du raster " + os.path.basename(rasterFinal) + "...")
                    rasterClassification(rasters[raster + 1], rasterIntermediaire, rasterFinal)

                    if nbRasters != 2:
                        os.remove(rasterIntermediaire)

                elif raster == 0 and nbRasters != 2:  # Si on est au premier raster et qu'il y en a plus que deux à fusionner.
                    rasterClassification(rasters[raster + 1], rasters[raster], rasterIntermediaire)
                    print("Fusion #1...")

                else:  # Si on traite un raster autre que le premier.
                    rasterClassification(rasters[raster + 1], rasterIntermediaire, rasterIntermediaire)
                    print("Fusion #" + str(raster + 1) + "...")

    else:
        listIntra[0][2]
