from generic import *


def parcs(dir, sources, pixelSize, ROICRSStr, ROICRS, ROIPathRaster, ROIData):
    # Répertoire où les données seront enregistrées.
    parcsDir = dir + r"\Parcs"

    # Liste de liens menant aux données.
    urlListParc = [
        "http://www.cec.org/sites/default/files/Atlas/Files/NA_ProtectedAreas_2017/NA_ProtectedAreas_2017_Shapefile.rar"]

    # Créer le répertoire où sera contenu les données, s'il n'existe pas.
    createDir(parcsDir)

    # Pour chaque lien de la liste fournie.
    for url in urlListParc:
        # Spécifier le lien vers le fichier en sortie.
        outPath = os.path.join(parcsDir, os.path.basename(url))

        # Si la donnée d'origine n'a pas été téléchargée ou n'existe pas.
        if not os.path.exists(outPath):
            downloadData(url, outPath, parcsDir, True)

        # Obtenir la liste de tous les fichiers shapefile des milieux humides
        fileNames = listFiles(parcsDir, ".shp", ("reproject.shp", "clip.shp", "resample" + str(pixelSize) + ".shp"))

        # Pour chaque lien de la liste
        for file in fileNames:
            # Spécifier les liens vers les fichiers de sortie.
            outPath, outPathReproject, outPathClip, outPathRaster = createPaths(parcsDir, file, pixelSize, True)

            # Extraire le code EPSG de la donnée téléchargée.
            data = gpd.read_file(outPath)
            dataCRS, dataCRSStr = extractEPSGVector(data)

            # Si la projection n'est pas la même que celle de la région d'intérêt et qu'un shp reprojeté n'existe pas.
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
