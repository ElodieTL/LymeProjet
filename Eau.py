from generic import *

def Eau(pixelSize, ROICRSStr, ROICRS, ROIData):
    # Répertoire où les données seront enregistrées
    eauDir = r"Z:\GALAL35\Projet_lyme\Donnees\Eau"
    #zonesHumidesDir = r"Z:\MALAM357\GMT-3051 Projet en génie géomatique II\Donnees\Eau"

    # Liste de liens menant aux données.
    urlListEau = [
        "http://ftp.geogratis.gc.ca/pub/nrcan_rncan/vector/canvec/shp/Hydro/canvec_250K_QC_Hydro_shp.zip"]

    # Créer le répertoire s'il n'existe pas.
    createDir(eauDir)

    # # Créer une liste vide qui contiendra les rasters créés
    rasters = []

    for url in urlListEau:
        # Spécifier les liens vers les fichiers de sortie.
        outPath = os.path.join(eauDir, os.path.basename(url))

        # Si le fichier vectoriel d'origine n'existe pas.
        if not os.path.exists(outPath):
            downloadData(url, outPath, eauDir, True)

        # Obtenir la liste de tous les fichiers shapefile du déterminant Eau
        fileNames = listChemin(eauDir,("aterbody_2.shp")) #"watercourse_1.shp"

        for file in fileNames:
            outPath, outPathReproject, outPathClip, outPathRaster = createPaths(eauDir, file, pixelSize, True)

            # Extraire le code EPSG de la donnée téléchargée.
            data = gpd.read_file(outPath)
            dataCRS, dataCRSStr = extractEPSGVector(data)

            # Si la projection n'est pas la même que celle de la région d'intérêt et qu'un shp reprojeté n'existe pas.
            if dataCRS != ROICRS and not os.path.exists(outPathReproject):
                reprojectShp(data, outPathReproject, ROICRSStr)

            # Si un .shp découpé n'existe pas.
            if not os.path.exists(outPathClip):
                clipShp(outPathReproject, outPathClip, ROIData)

            # Si le .shp n'est pas rasterisé.
            if not os.path.exists(outPathRaster):
                rasteriseShp(outPathClip, outPathRaster, pixelSize, ROICRS)

            # Ajouter la donnée à la liste.
            rasters.append(outPathRaster)

        return rasters