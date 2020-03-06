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

    """ Traitement des données pour le déterminant Foret"""
    Foret_raster = Foret(pixelSize, ROICRSStr, ROICRS, ROIData, ROIDataJson)
    rasters.append(Foret_raster)

    """ Traitement des données pour le déterminant Zone humide"""
    ZH_raster = ZoneHumide(pixelSize, ROICRSStr, ROICRS, ROIData)
    rasters.append(ZH_raster)

    """ Traitement des données pour le déterminant Parc"""
    Parc_raster = Parc(pixelSize, ROICRSStr, ROICRS, ROIData)
    rasters.append(Parc_raster)

    """ Traitement des données pour le déterminant Eau"""
    Eau_raster = Parc(pixelSize, ROICRSStr, ROICRS, ROIData)
    rasters.append(Eau_raster )

if __name__ == "__main__":
    main()