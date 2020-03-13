from generic import *


def eau(pixelSize, ROICRSStr, ROICRS, ROIPathRaster, ROIData):
    # Répertoire où les données seront enregistrées.
    # eauDir = r"Z:\ELTAL8\ProjetLYME\c\Donnees\Eau"
    # eauDir = r"Z:\GALAL35\Projet_lyme\Donnees\Eau"
    eauDir = r"D:\Donnees\Eau"

    # Liste de liens menant aux données.
    urlListEau = [
        "http://ftp.geogratis.gc.ca/pub/nrcan_rncan/vector/canvec/shp/Hydro/canvec_250K_QC_Hydro_shp.zip"]

    # Créer le répertoire où sera contenu les données, s'il n'existe pas.
    createDir(eauDir)

    # Pour chaque lien de la liste fournie.
    for url in urlListEau:
        # Spécifier le lien vers le fichier en sortie.
        outPath = os.path.join(eauDir, os.path.basename(url))

        # Si la donnée d'origine n'a pas été téléchargée ou n'existe pas.
        if not os.path.exists(outPath):
            downloadData(url, outPath, eauDir, True)

        # Obtenir la liste de tous les fichiers vectoriels.
        fileNames = listFiles(eauDir, ".shp", ("reproject.shp", "clip.shp", "resample" + str(pixelSize) + ".shp"))

        for file in fileNames:
            # Créer les liens vers les fichiers de sortie.
            outPath, outPathReproject, outPathClip, outPathRaster = createPaths(eauDir, file, pixelSize, True)

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
                if not os.path.exists(outPathRaster) and clip:
                    rasteriseVector(outPathClip, ROIPathRaster, outPathRaster)

            else:
                print("No projection detected for raster " + outPath + ". Impossible to proceed.")
