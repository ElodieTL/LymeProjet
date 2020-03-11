from generic import *
import numpy as np
import earthpy.spatial as es
import earthpy.plot as ep
import cv2

# Répertoire contenant les données de forêt.
# dir = "X:\ELTAL8\ProjetLYME\ROI_Projet_Genie_Maladies_Vectorielles_v2\Données\Forêt"
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
    es.stack(liste, pathAll)  # Bande 1 = Feuillus, Bande 2 = Conifères, Bande 3 = Inconnu.

if not os.path.exists(pathClass):
    print("Classifying raster...")

    imgAll = cv2.imread(re.sub(r"\\", r"\\\\", pathAll), -1)
    rows, cols = imgAll.shape[:2]

    imgClass = np.ones((rows, cols, 3), np.uint8) * 255

    for i in range(rows):
        for j in range(cols):
            if imgAll[i, j, 0] == 0 and imgAll[i, j, 1] == 0 and imgAll[i, j, 2] == 0:  # Aucune forêt ou Inconnu.
                imgClass[i, j, 0] = 0
                imgClass[i, j, 1] = 0  # Noir
                imgClass[i, j, 2] = 0

            if imgAll[i, j, 0] > 50:
                imgClass[i, j, 0] = 0
                imgClass[i, j, 1] = 0  # Noir
                imgClass[i, j, 2] = 0

            elif imgAll[i, j, 2] > 0 and ((0.7 <= imgAll[i, j, 1] / imgAll[i, j, 2] <= 1.3) or (0.7 <= imgAll[i, j, 0] / imgAll[i, j, 2] <= 1.3)):  # Forêt mixte.
                imgClass[i, j, 0] = 0
                imgClass[i, j, 1] = 255  # Jaune
                imgClass[i, j, 2] = 255

            elif imgAll[i, j, 2] < imgAll[i, j, 1]:  # Feuillus.
                imgClass[i, j, 0] = 0
                imgClass[i, j, 1] = 255  # Vert pâle
                imgClass[i, j, 2] = 0

            elif imgAll[i, j, 2] > imgAll[i, j, 1]:  # Conifères.
                imgClass[i, j, 0] = 0
                imgClass[i, j, 1] = 75  # Vert foncé
                imgClass[i, j, 2] = 0

    cv2.imwrite(pathClass, imgClass)
