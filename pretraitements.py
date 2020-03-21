from generic import *


def pretraitements(dir, det, sources, pixelSize, ROICRSStr, ROICRS, ROIPathRaster, ROIData, ROIDataJson):
    if det == 0:
        det = "Foret"

    elif det == 1:
        det = "Zones humides"

    elif det == 2:
        det = "Eau"

    elif det == 3:
        det = "Parcs"

    # Répertoire où les données seront enregistrées.
    detDir = dir + r"\\" + det

    sourcesList = pd.read_excel("ListeSources.xlsx")
    det = sourcesList.loc[sourcesList["Determinant"] == det]
    detSources = det.loc[det["Sources"].isin(sources)]

    # Initialisation d'une liste de liens menant aux données.
    urlList = []

    # Ajout des liens à la liste.
    for row in detSources.itertuples():
        urlList.append([row.Liens, row.Types])

    # Créer le répertoire où sera contenu les données, s'il n'existe pas.
    createDir(detDir)

    # Pour chaque lien de la liste fournie.
    for url in urlList:
        # Type courant.
        type = url[1]

        # Spécifier le lien vers le fichier en sortie.
        outPath = os.path.join(detDir, os.path.basename(url[0]))

        # Vérifier si la donnée téléchargée est compressée.
        if outPath[-4:] in [".rar", ".zip"]:
            compress = True

        else:
            compress = False

        # Si la donnée d'origine n'a pas été téléchargée ou n'existe pas.
        if not os.path.exists(outPath):
            downloadData(url[0], outPath, detDir, compress)

        # Obtenir la liste de tous les fichiers.
        if type == "Raster":
            fileNames = listFiles(detDir, ".tif", ("reproject.tif", "clip.tif", "resample_" + pixelSize + ".tif"))

        else:
            fileNames = listFiles(detDir, ".shp", ("reproject.shp", "clip.shp", "resample_" + pixelSize + ".shp"))

        # Pour chaque lien de la liste.
        for file in fileNames:
            # Créer les liens vers les fichiers de sortie.
            if type == "Raster":
                outPath, outPathReproject, outPathClip, outPathResample = createPaths(detDir, file, pixelSize, False)

                # Extraire le code EPSG de la donnée téléchargée.
                dataCRS, dataCRSStr = extractEPSGRaster(outPath)

            else:
                outPath, outPathReproject, outPathClip, outPathRaster = createPaths(detDir, file, pixelSize, True)

                # Extraire le code EPSG de la donnée téléchargée.
                data = gpd.read_file(outPath)
                dataCRS, dataCRSStr = extractEPSGVector(data)

            if dataCRS is not None:
                # Si la projection n'est pas la même que celle de la région d'intérêt et qu'un fichier reprojeté n'existe pas.
                if dataCRS != ROICRS:
                    if type == "Raster":
                        if not os.path.exists(outPathReproject):
                            reprojectRaster(outPath, outPathReproject, ROICRSStr)

                        # Si un raster découpé n'existe pas.
                        if not os.path.exists(outPathClip):
                            clipRaster(outPathReproject, outPathClip, ROIDataJson, ROICRS)

                        # Si un raster rééchantillonné n'existe pas.
                        if not os.path.exists(outPathResample):
                            resampleRaster(outPathClip, ROIPathRaster, outPathResample)

                    else:
                        if not os.path.exists(outPathReproject):
                            reprojectVector(data, outPathReproject, ROICRSStr)

                        clip = False
                        if not os.path.exists(outPathClip):
                            clip = clipVector(outPathReproject, outPathClip, ROIData)

                        # Si le fichier vectoriel n'est pas rasterisé.
                        if not os.path.exists(outPathRaster) and (clip or os.path.exists(outPathClip)):
                            rasteriseVector(outPathClip, ROIPathRaster, outPathRaster)

            else:
                print("No projection detected for raster " + outPath + ". Impossible to proceed.")
