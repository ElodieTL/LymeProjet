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

    imgAll = cv2.imread(re.sub(r"\\", r"\\\\", pathAll), -1)
    rows, cols = imgAll.shape[:2]

    imgClass = np.ones((rows, cols, 3), np.uint8) * 255

    for i in range(rows):
        for j in range(cols):
            if imgAll[i, j, 0] == 0 and imgAll[i, j, 1] == 0 and imgAll[i, j, 2] == 0:  # Aucune forêt.
                imgClass[i, j, 0] = 0
                imgClass[i, j, 1] = 0  # Noir
                imgClass[i, j, 2] = 0

            elif imgAll[i, j, 0] > 50:  # Inconnu
                imgClass[i, j, 0] = 0
                imgClass[i, j, 1] = 0  # Vert pâle
                imgClass[i, j, 2] = 0

            elif imgAll[i, j, 1] > 50:  # Conifères
                imgClass[i, j, 0] = 0
                imgClass[i, j, 1] = 75  # Vert foncé
                imgClass[i, j, 2] = 0

            elif imgAll[i, j, 2] > 50:  # Feuillus
                imgClass[i, j, 0] = 0
                imgClass[i, j, 1] = 255  # Noir
                imgClass[i, j, 2] = 0

            else:  # Forêt mixte
                imgClass[i, j, 0] = 0
                imgClass[i, j, 1] = 255  # Jaune
                imgClass[i, j, 2] = 255

    cv2.imwrite(pathClass, imgClass)
