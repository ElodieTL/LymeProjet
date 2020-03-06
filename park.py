from generic import *

def Parc(pixelSize, ROICRSStr, ROICRS, ROIData):
    # Répertoire où les données seront enregistrées
    parcDir = r"Z:\GALAL35\Projet_lyme\Donnees/Parc"

    # Liste de liens menant aux données.
    urlListParc = ["http://www.cec.org/sites/default/files/Atlas/Files/NA_ProtectedAreas_2017/NA_ProtectedAreas_2017_Shapefile.rar"]

    # Créer le répertoire s'il n'existe pas.
    if not os.path.exists(parcDir):
        os.makedirs(parcDir)

    for url in urlListParc:
        # Spécifier les liens vers les fichiers de sortie.
        outPath = os.path.join(urlListParc, os.path.basename(url))

        # Si le fichier vectoriel d'origine n'existe pas.
        if not os.path.exists(outPath):
            downloadData(url, outPath, urlListParc, True)

        # Obtenir la liste de tous les fichiers shapefile des milieux humides
        fileNames = [file for file in os.listdir(parcDir) if file.endswith('.shp') and not file.endswith('reproject.shp') and not file.endswith('clip.shp') and not file.endswith('resample' + str(pixelSize) + '.shp')]

        # Pour chaque lien de la liste
        for file in fileNames:
            # Spécifier les liens vers les fichiers de sortie.
            outPath = os.path.join(parcDir, file)
            outPathReproject = outPath.replace(".", "_reproject.")
            outPathClip = outPath.replace(".", "_clip.")
            outPathResample = outPath.replace(".", "_resample_" + str(pixelSize) + ".")

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
