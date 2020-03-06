from generic import *

def ZoneHumide(pixelSize, ROICRSStr, ROICRS, ROIData):
    # Répertoire où les données seront enregistrées
    zonesHumidesDir = r"Z:\GALAL35\Projet_lyme\Donnees\Zones humides"
    #zonesHumidesDir = r"Z:\MALAM357\GMT-3051 Projet en génie géomatique II\Donnees\Zones humides"

    # Liste de liens menant aux données.
    urlListZH = [
        "https://www.donneesquebec.ca/recherche/fr/dataset/eafec419-d67d-449e-a157-d22230314d36/resource/c95e97fe-77cb-49f2-822d-c45067b6a190/download/mh2019shp.zip"]

    # Créer le répertoire s'il n'existe pas.
    createDir(zonesHumidesDir)

    # # Créer une liste vide qui contiendra les rasters créés
    rasters = []

    for url in urlListZH:
        # Spécifier les liens vers les fichiers de sortie.
        outPath = os.path.join(zonesHumidesDir, os.path.basename(url))

        # Si le fichier vectoriel d'origine n'existe pas.
        if not os.path.exists(outPath):
            downloadData(url, outPath, zonesHumidesDir, True)

        # Obtenir la liste de tous les fichiers shapefile des milieux humides
        fileNames = [file for file in os.listdir(zonesHumidesDir) if file.endswith(".shp") and not file.endswith("reproject.shp") and not file.endswith("clip.shp") and not file.endswith("resample" + str(pixelSize) + ".shp")]

        for file in fileNames:
            # Spécifier les liens vers les fichiers de sortie.
            outPath, outPathReproject, outPathClip, outPathRaster = createPaths(zonesHumidesDir, file, pixelSize, True)

            # Extraire le code EPSG de la donnée téléchargée.
            data = gpd.read_file(outPath)
            dataCRS, dataCRSStr = extractEPSGVector(data)

            # Si la projection n'est pas la même que celle de la région d'intérêt et qu'un shp reprojeté n'existe pas.
            if dataCRS != ROICRS and not os.path.exists(outPathReproject):
                reprojectShp(data, outPathReproject, ROICRSStr)

            # Si un shp découpé n'existe pas.
            if not os.path.exists(outPathClip):
                clipShp(outPathReproject, outPathClip, ROIData)

            # Si le .shp n'est pas rasterisé.
            if not os.path.exists(outPathRaster):
                rasteriseShp(outPathClip, outPathRaster, pixelSize, ROICRS)

            # Ajouter la donnée à la liste.
            rasters.append(outPathResample)

    return rasters