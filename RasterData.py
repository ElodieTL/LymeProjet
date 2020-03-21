from generic import *


def rasterData(dir, det, sources, pixelSize, ROICRSStr, ROICRS, ROIPathRaster, ROIDataJson):
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
        if outPath[-4:] in [".rar", ".zip"]:
            compress = True

        else:
            compress = False

        # Si la donnée d'origine n'a pas été téléchargée ou n'existe pas.
        if not os.path.exists(outPath):
            downloadData(url, outPath, detDir, compress)

        # Obtenir la liste de tous les fichiers matriciels.
        fileNames = listFiles(detDir, ".tif", ("reproject.tif", "clip.tif", "resample" + pixelSize + ".tif"))

        # Pour chaque lien de la liste.
        for file in fileNames:
            # Créer les liens vers les fichiers de sortie.
            outPath, outPathReproject, outPathClip, outPathResample = createPaths(detDir, file, pixelSize, False)

            # Extraire le code EPSG de la donnée téléchargée.
            data = gpd.read_file(outPath)
            dataCRS, dataCRSStr = extractEPSGRaster(data)

            # Si la projection n'est pas la même que celle de la région d'intérêt et qu'un fichier matriciel reprojeté n'existe pas.
            if dataCRS is not None:
                if dataCRS != ROICRS and not os.path.exists(outPathReproject):
                    reprojectRaster(data, outPathReproject, ROICRSStr)

                # Si un raster découpé n'existe pas.
                if not os.path.exists(outPathClip):
                    clipRaster(outPathReproject, outPathClip, ROIDataJson, ROICRS)

                # Si un raster rééchantillonné n'existe pas.
                if not os.path.exists(outPathResample):
                    resampleRaster(outPathClip, ROIPathRaster, outPathResample)

            else:
                print("No projection detected for file " + outPath + ". Impossible to proceed.")