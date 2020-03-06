from generic import *
import numpy as np
import earthpy.spatial as es
import earthpy.plot as ep
import cv2

# Répertoire contenant les données de forêt.
# dir = "X:\ELTAL8\ProjetLYME\ROI_Projet_Genie_Maladies_Vectorielles_v2\Données\Forêt"
dir = r"Z:\MALAM357\GMT-3051 Projet en génie géomatique II\Donnees\Foret"

# Filepath
pathFeuillus = os.path.join(dir, "NFI_MODIS250m_2011_kNN_SpeciesGroups_Broadleaf_Spp_v1_clip.tif")
pathConiferes = os.path.join(dir, "NFI_MODIS250m_2011_kNN_SpeciesGroups_Needleleaf_Spp_v1_clip.tif")
pathUnknown = os.path.join(dir, "NFI_MODIS250m_2011_kNN_SpeciesGroups_Unknown_Spp_v1_clip.tif")
pathAll = os.path.join(dir, "NFI_MODIS250m_2011_kNN_SpeciesGroups_Unknown_Spp_v1_clip.tif")

# Liste des fichiers raster pertinents.
liste = [pathFeuillus, pathConiferes, pathUnknown]

# Fusionner les rasters contenus dans la liste.
es.stack(liste, pathAll)

# bande 0 = inconnu bande 1 = feuillu bande 2 = conifère

img = cv2.imread(pathAll, cv2.IMREAD_UNCHANGED)           # rgb
rows, cols = img.shape[:2]

img2 = np.ones((rows, cols,1), np.uint8) * 255

for i in range(rows):
    for j in range(cols):
        if (img[i,j,0] == 0 and img[i,j,1] == 0 and img[i,j,2] == 0) :
            img2[i,j] = 0

        if (img[i,j,0] > 50):
            img2[i,j] = 0

        elif (img[i,j,2] > 0 and img[i,j,1] / img[i,j,2] > 0.7 and img[i,j,1] / img[i,j,2] < 1.3):
            img2[i,j] = 75

        elif (img[i,j,2] < img[i,j,1]):
            img2[i,j] = 200

        elif (img[i,j,2] > img[i,j,1]):
            img2[i,j] = 125

# Feuillu = 200 conifère = 125 pas foret = 0 mixte = 75

cv2.imshow('image', img2)
cv2.waitKey()