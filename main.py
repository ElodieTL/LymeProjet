from generic import *
from ZoneHumide import *
from detForet import *
from park import *
from Eau import *


def main():
    # Dimension d'un pixel pour un raster.
    pixelSize = 30

    # Liste des traitements à exécuter.
    listeTraitements = [3]

    # Importer et lire les données du shapelefile et du raster représentant la zone d'intérêt.
    # ROIPathVector = "X:\ELTAL8\ProjetLYME\ROI_Projet_Genie_Maladies_Vectorielles_v2/ROI_Projet_Genie_Maladies_Vectorielles_v2.shp"
    # ROIPathVector = "Z:\GALAL35\Projet_lyme\LymeProjet\ROI\ROI_Projet_Genie_Maladies_Vectorielles_v2.shp"
    ROIPathVector = "Z:\MALAM357\GMT-3051 Projet en génie géomatique II\LymeProjet\ROI\ROI_Projet_Genie_Maladies_Vectorielles_v2.shp"

    ROIPathRaster = "Z:\MALAM357\GMT-3051 Projet en génie géomatique II\LymeProjet\ROI\ROI_Projet_Genie_Maladies_Vectorielles_v2_" + str(pixelSize) + ".tif"

    ROIDataVector = gpd.read_file(ROIPathVector)

    # Transformer la composante géométrique de la donnée vectorielle en format json.
    ROIDataVectorJson = geoToJson(ROIDataVector)

    # Extraire le code EPSG (la projection) de la zone d'intérêt.
    ROICRS, ROICRSStr = extractEPSGVector(ROIDataVector)

    if ROICRS is not None:
        if 1 in listeTraitements:
            """ Traitement des données pour le déterminant Forêt """
            foret(pixelSize, ROICRSStr, ROICRS, ROIPathRaster, ROIDataVectorJson)

        if 2 in listeTraitements:
            """ Traitement des données pour le déterminant Zones humides """
            zonesHumides(pixelSize, ROICRSStr, ROICRS, ROIPathRaster, ROIDataVector)

        if 3 in listeTraitements:
            """ Traitement des données pour le déterminant Parcs """
            parcs(pixelSize, ROICRSStr, ROICRS, ROIPathRaster, ROIDataVector)

        if 4 in listeTraitements:
            """ Traitement des données pour le déterminant Eau """
            eau(pixelSize, ROICRSStr, ROICRS, ROIPathRaster, ROIDataVector)
    else:
        print("No projection detected for ROI. Impossible to proceed.")


if __name__ == "__main__":
    main()
