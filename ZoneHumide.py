from generic import *


def zonesHumides(dir, det, sources, pixelSize, ROICRSStr, ROICRS, ROIPathRaster, ROIData):
    # Répertoire où les données seront enregistrées.
    detDir = dir + r"\\" + det

    sourcesList = pd.read_excel("ListeSources.xlsx")
    det = sourcesList.loc[sourcesList["Determinant"] == det]
    detSources = det.loc[det["Sources"].isin(sources)]

    # Initialisation d'une liste de liens menant aux données.
    urlList = []

    # Ajout des liens à la liste.
    for row in detSources.itertuples():
        urlList.append(row.Liens)

    # Créer le répertoire où sera contenu les données, s'il n'existe pas.
    createDir(detDir)

    # Pour chaque lien de la liste fournie.
    for url in urlList:
        # Spécifier le lien vers le fichier en sortie.
        outPath = os.path.join(detDir, os.path.basename(url))

        # Vérifier si la donnée téléchargée est compressée.
        if outPath[-3:] in ["rar", "zip"]:
            compress = True

        else:
            compress = False

        # Si la donnée d'origine n'a pas été téléchargée ou n'existe pas.
        if not os.path.exists(outPath):
            downloadData(url, outPath, detDir, compress)

        # Obtenir la liste de tous les fichiers vectoriels.
        fileNames = listFiles(detDir, ".shp", ("reproject.shp", "clip.shp", "resample" + pixelSize + ".shp"))

        # Pour chaque lien de la liste.
        for file in fileNames:
            # Créer les liens vers les fichiers de sortie.
            outPath, outPathReproject, outPathClip, outPathRaster = createPaths(detDir, file, pixelSize, True)

            # Extraire le code EPSG de la donnée téléchargée.
            data = gpd.read_file(outPath)
            dataCRS, dataCRSStr = extractEPSGVector(data)

            # Si la projection n'est pas la même que celle de la région d'intérêt et qu'un fichier vectoriel reprojeté n'existe pas.
            if dataCRS is not None:
                if dataCRS != ROICRS and not os.path.exists(outPathReproject):
                    reprojectVector(data, outPathReproject, ROICRSStr)

                # Si un .shp découpé n'existe pas.
                clip = False
                if not os.path.exists(outPathClip):
                    clip = clipVector(outPathReproject, outPathClip, ROIData)

                # Si le fichier vectoriel n'est pas rasterisé.
                if not os.path.exists(outPathRaster) and (clip or os.path.exists(outPathClip)):
                    rasteriseVector(outPathClip, ROIPathRaster, outPathRaster)

            else:
                print("No projection detected for raster " + outPath + ". Impossible to proceed.")
