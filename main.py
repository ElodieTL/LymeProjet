from generic import *
from ZoneHumide import *
from detForet import *
from park import *

def main():
    # Dimension d'un pixel pour un raster.
    pixelSize = 30

    # Importer et lire les données du shapelefile représentant la zone d'intérêt.
    # ROIPath = "X:\ELTAL8\ProjetLYME\ROI_Projet_Genie_Maladies_Vectorielles_v2/ROI_Projet_Genie_Maladies_Vectorielles_v2.shp"
    ROIPath = "Z:\GALAL35\Projet_lyme\LymeProjet\ROI\ROI_Projet_Genie_Maladies_Vectorielles_v2.shp"
    #ROIPath = "Z:\MALAM357\GMT-3051 Projet en génie géomatique II\LymeProjet\ROI\ROI_Projet_Genie_Maladies_Vectorielles_v2.shp"
    ROIData = gpd.read_file(ROIPath)

    # Transformer en format json
    ROIDataJson = geoToJson(ROIData)

    # Extraire le code EPSG (la projection) de la zone d'intérêt.
    ROICRS, ROICRSStr = extractEPSGVector(ROIData)

    # Télécharger les données de forêt de NRCan
    rasters = [] # Créer une liste vide qui contiendra les rasters téléchargés.

    # Répertoires où les données seront enregistrées.
    # eauDir = r"X:\ELTAL8\ProjetLYME\ROI_Projet_Genie_Maladies_Vectorielles_v2\Données\Eau"
    eauDir = r"Z:\GALAL35\Projet_lyme\Donnees\Eau"
    #eauDir = r"Z:\MALAM357\GMT-3051 Projet en génie géomatique II\Donnees\Eau"

    # Liste de liens menant aux données.
    urlListEau = [
        "http://ftp.geogratis.gc.ca/pub/nrcan_rncan/vector/canvec/shp/Hydro/canvec_250K_QC_Hydro_shp.zip"]

    # Créer des répertoires s'ils n'existent pas.
    createDir(eauDir)

    """ Traitement des données pour le déterminant Foret"""
    #Foret_raster = Foret(pixelSize, ROICRSStr, ROICRS, ROIData, ROIDataJson)
    #rasters.append(Foret_raster)

    """ Traitement des données pour le déterminant Zone humide"""
    #ZH_raster = ZoneHumide(pixelSize, ROICRSStr, ROICRS, ROIData)
    #rasters.append(ZH_raster)

    """ Traitement des données pour le déterminant Parc"""
    Parc_raster = Parc(pixelSize, ROICRSStr, ROICRS, ROIData)
    rasters.append(Parc_raster)

    """
    for url in urlListEau:
        # Spécifier les liens vers les fichiers de sortie.
        outPath = os.path.join(eauDir, os.path.basename(url))

        # Si le fichier vectoriel d'origine n'existe pas.
        if not os.path.exists(outPath):
            downloadData(url, outPath, eauDir, True)

        # Obtenir la liste de tous les fichiers shapefile des milieux humides
        fileNames = [file for file in os.listdir(eauDir) if file.endswith(".shp") and not file.endswith("reproject.shp") and not file.endswith("clip.shp") and not file.endswith("resample" + str(pixelSize) + ".shp")]

        for file in fileNames:
            outPath, outPathReproject, outPathClip, outPathResample = createPaths(eauDir, file, pixelSize, True)

            # Extraire le code EPSG de la donnée téléchargée.
            data = gpd.read_file(outPath)
            dataCRS, dataCRSStr = extractEPSGVector(data)

            # Si la projection n'est pas la même que celle de la région d'intérêt et qu'un shp reprojeté n'existe pas.
            if dataCRS != ROICRS and not os.path.exists(outPathReproject):
                reprojectShp(data, outPathReproject, ROICRSStr)

            # Si un .shp découpé n'existe pas.
            if not os.path.exists(outPathClip):
                clipShp(outPathReproject, outPathClip, ROIData)
    """
if __name__ == "__main__":
    main()