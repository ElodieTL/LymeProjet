#

import os
import numpy as np
from rasterio.plot import show
import re
import osr
import urllib
import geopandas as gpd
import rasterio as rio
import json
import matplotlib.pyplot as plt
import pycrs
from rasterio.merge import merge
from rasterio.mask import mask
from rasterio.plot import show
from rasterio.warp import calculate_default_transform, reproject, Resampling
import gdal
import earthpy.spatial as es
import earthpy.plot as ep
import cv2

# Data dir
data_dir = "X:\ELTAL8\ProjetLYME\ROI_Projet_Genie_Maladies_Vectorielles_v2\Données\Forêt"

# Filepath
fpfeuillu = os.path.join(data_dir, "NFI_MODIS250m_2011_kNN_SpeciesGroups_Broadleaf_Spp_v1_clip.tif")
fpconifere = os.path.join(data_dir, "NFI_MODIS250m_2011_kNN_SpeciesGroups_Needleleaf_Spp_v1_clip.tif")
fpunknow = os.path.join(data_dir, "NFI_MODIS250m_2011_kNN_SpeciesGroups_Unknown_Spp_v1_clip.tif")

# Liste de raster
file_list = [fpfeuillu, fpconifere, fpunknow]

# Fusionner les rasters
es.stack(file_list, "X:\ELTAL8\ProjetLYME\ROI_Projet_Genie_Maladies_Vectorielles_v2\Données/foret.tif")



img_file = 'X:\ELTAL8\eforet.tif'
img = cv2.imread(img_file, cv2.IMREAD_UNCHANGED)           # rgb
rows, cols = img.shape[:2]

img2 = np.ones((rows, cols,1),np.uint8)*255


for i in range(rows):
    for j in range(cols):
        if (img[i,j,0] == 0 and img[i,j,1] == 0 and img[i,j,2] == 0) :
            img2[i,j] = 0

        if (img[i,j,0] > 50):
                img2[i, j] = 0

        elif (img[i,j,0] > 0):
            if (img[i,j,1] / img[i,j,0] > 0.6 and img[i,j,1] / img[i,j,0] < 1.4):
                img2[i,j] = 75

            elif (img[i,j,0] > img[i,j,1]):
                 img2[i, j] = 125

            elif (img[i,j,0] < img[i,j,1]):
                img2[i, j] = 200



# Window name in which image is displayed
window_name = 'image'

# Using cv2.imshow() method
# Displaying the image
cv2.imshow(window_name, img2)
cv2.waitKey(0)