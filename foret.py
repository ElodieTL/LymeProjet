from generic import *
import numpy as np
import earthpy.spatial as es
import earthpy.plot as ep
import cv2

# Répertoire contenant les données de forêt.
# dir = "Z:\ELTAL8\ProjetLYME\c\Donnees\Foret"
dir = r"D:\Donnees\Foret"

# Noms des fichiers pertinents.
pathFeuillus = os.path.join(dir, "NFI_MODIS250m_2011_kNN_SpeciesGroups_Broadleaf_Spp_v1_resample_30.tif")
pathConiferes = os.path.join(dir, "NFI_MODIS250m_2011_kNN_SpeciesGroups_Needleleaf_Spp_v1_resample_30.tif")
pathUnknown = os.path.join(dir, "NFI_MODIS250m_2011_kNN_SpeciesGroups_Unknown_Spp_v1_resample_30.tif")

pathAll = os.path.join(dir, "NFI_MODIS250m_2011_kNN_SpeciesGroups_All_Spp_v1_resample_30.tif")

pathClass = os.path.join(dir, "NFI_MODIS250m_2011_kNN_SpeciesGroups_Class_Spp_v1_resample_30.tif")

if not os.path.exists(pathAll):
    print("Stacking rasters...")

    # Création d'une liste des fichiers raster pertinents.
    liste = [pathFeuillus, pathConiferes, pathUnknown]

    # Fusionner les rasters contenus dans la liste.
    es.stack(liste, pathAll)  # 2 = Feuillus, 1 = Conifères, 0 = Inconnu.

if not os.path.exists(pathClass):
    fileName = os.path.basename(pathClass)
    print("Classifying raster " + fileName + "...")

    rasterAll = gdal.Open(pathAll, gdal.GA_ReadOnly)
    rasterAllBand0 = rasterAll.GetRasterBand(1).ReadAsArray()
    rasterAllBand1 = rasterAll.GetRasterBand(2).ReadAsArray()
    rasterAllBand2 = rasterAll.GetRasterBand(3).ReadAsArray()

    for i in range(rasterAll.RasterYSize):
        for j in range(rasterAll.RasterXSize):
            if rasterAllBand0[i, j] == 0 and rasterAllBand1[i, j] == 0 and rasterAllBand2[i, j] == 0:  # Aucune forêt
                rasterAllBand0[i, j] = 0
                rasterAllBand1[i, j] = 0  # Noir
                rasterAllBand2[i, j] = 0

            elif rasterAllBand0[i, j] > 50:  # Feuillus
                rasterAllBand0[i, j] = 0
                rasterAllBand1[i, j] = 255  # Vert
                rasterAllBand2[i, j] = 0

            elif rasterAllBand1[i, j] > 50:  # Conifères
                rasterAllBand0[i, j] = 0
                rasterAllBand1[i, j] = 75  # Vert foncé
                rasterAllBand2[i, j] = 0

            elif rasterAllBand2[i, j] > 50:  # Inconnu
                rasterAllBand0[i, j] = 0
                rasterAllBand1[i, j] = 0  # Noir
                rasterAllBand2[i, j] = 0

            else:  # Mixte
                rasterAllBand0[i, j] = 255
                rasterAllBand1[i, j] = 255  # Jaune
                rasterAllBand2[i, j] = 0

    rasterClass = gdal.GetDriverByName("GTiff").Create(pathClass, rasterAll.RasterXSize, rasterAll.RasterYSize, 3)
    rasterClass.GetRasterBand(1).WriteArray(rasterAllBand0)
    rasterClass.GetRasterBand(2).WriteArray(rasterAllBand1)
    rasterClass.GetRasterBand(3).WriteArray(rasterAllBand2)

    rasterClass.SetProjection(rasterAll.GetProjection())
    rasterClass.SetGeoTransform(rasterAll.GetGeoTransform())
    rasterClass.FlushCache()
