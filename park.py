from generic import *

def Parc(pixelSize, ROICRSStr, ROICRS, ROIData):
    # Répertoire où les données seront enregistrées
    parcDir = r"Z:\ELTAL8\ProjetLYME\c\Donnees\Parc"
    #parcDir = r"Z:\GALAL35\Projet_lyme\Donnees/Parc"
    #parcDir = r"Z:\MALAM357\GMT-3051 Projet en génie géomatique II\Donnees/Parc"

    # Liste de liens menant aux données.
    urlListParc = ["http://www.cec.org/sites/default/files/Atlas/Files/NA_ProtectedAreas_2017/NA_ProtectedAreas_2017_Shapefile.rar"]

    # Créer le répertoire s'il n'existe pas.
    createDir(parcDir)

    # Créer une liste vide qui contiendra les rasters créés
    rasters = []

    for url in urlListParc:
        # Spécifier les liens vers les fichiers de sortie.
        outPath = os.path.join(parcDir, os.path.basename(url))

        # Si le fichier vectoriel d'origine n'existe pas.
        if not os.path.exists(outPath):
            downloadData(url, outPath, parcDir, True)

        # Obtenir la liste de tous les fichiers shapefile des milieux humides
        fileNames = listChemin(parcDir, (".shp"), ("reproject.shp","clip.shp","resample" + str(pixelSize) + ".shp"))
        # fileNames = [file for file in os.listdir(parcDir) if file.endswith('.shp') and not file.endswith('reproject.shp') and not file.endswith('clip.shp') and not file.endswith('resample' + str(pixelSize) + '.shp')]

        # Pour chaque lien de la liste
        for file in fileNames:
            # Spécifier les liens vers les fichiers de sortie.
            outPath, outPathReproject, outPathClip, outPathRaster = createPaths(parcDir, file, pixelSize, True)

            # Extraire le code EPSG de la donnée téléchargée.
            data = gpd.read_file(outPath)
            dataCRS, dataCRSStr = extractEPSGVector(data)

            # Si la projection n'est pas la même que celle de la région d'intérêt et qu'un shp reprojeté n'existe pas.
            if dataCRS != ROICRS and not os.path.exists(outPathReproject):
                reprojectShp(data, outPathReproject, ROICRSStr)

            # Si un shp découpé n'existe pas.
            if not os.path.exists(outPathClip):
                clipShp(outPathReproject, outPathClip, ROIData)

            # Si le shp n'est pas rasterisé
            if not os.path.exists(outPathResample):
                rasterizingShp(outPathClip, outPathResample, pixelSize, ROICRS)

            # Ajouter la donnée à la liste.
            rasters.append(outPathResample)

    return rasters