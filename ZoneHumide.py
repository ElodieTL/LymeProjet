from generic import *


def zonesHumides(dir, sources, pixelSize, ROICRSStr, ROICRS, ROIPathRaster, ROIData):
    # Répertoire où les données seront enregistrées.
    zonesHumidesDir = dir + r"\Zones humides"

    # Liste de liens menant aux données.
    urlListZH = [
        "https://www.donneesquebec.ca/recherche/fr/dataset/eafec419-d67d-449e-a157-d22230314d36/resource/c95e97fe-77cb-49f2-822d-c45067b6a190/download/mh2019shp.zip"]

    # Créer le répertoire où sera contenu les données, s'il n'existe pas.
    createDir(zonesHumidesDir)

    # Pour chaque lien de la liste fournie.
    for url in urlListZH:
        # Spécifier le lien vers le fichier en sortie.
        outPath = os.path.join(zonesHumidesDir, os.path.basename(url))

        # Si la donnée d'origine n'a pas été téléchargée ou n'existe pas.
        if not os.path.exists(outPath):
            downloadData(url, outPath, zonesHumidesDir, True)

        # Obtenir la liste de tous les fichiers vectoriels.
        fileNames = listFiles(zonesHumidesDir, ".shp", ("reproject.shp", "clip.shp", "resample" + str(pixelSize) + ".shp"))

        for file in fileNames:
            # Créer les liens vers les fichiers de sortie.
            outPath, outPathReproject, outPathClip, outPathRaster = createPaths(zonesHumidesDir, file, pixelSize, True)

            # Extraire le code EPSG de la donnée téléchargée.
            data = gpd.read_file(outPath)
            dataCRS, dataCRSStr = extractEPSGVector(data)

            # Si la projection n'est pas la même que celle de la région d'intérêt et qu'un raster reprojeté n'existe pas.
            if dataCRS is not None:
                if dataCRS != ROICRS and not os.path.exists(outPathReproject):
                    reprojectVector(data, outPathReproject, ROICRSStr)

                # Si un .shp découpé n'existe pas.
                clip = False
                if not os.path.exists(outPathClip):
                    clip = clipVector(outPathReproject, outPathClip, ROIData)

                # Si le fichier vectoriel n'est pas rasterisé.
                if (not os.path.exists(outPathRaster) and clip) or os.path.exists(outPathClip):
                    rasteriseVector(outPathClip, ROIPathRaster, outPathRaster)

            else:
                print("No projection detected for raster " + outPath + ". Impossible to proceed.")
