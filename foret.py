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
import pycrs
from rasterio.merge import merge
from rasterio.mask import mask
from rasterio.plot import show
from rasterio.warp import calculate_default_transform, reproject, Resampling
import gdal
import earthpy.spatial as es

# Data dir
data_dir = "Z:\ELTAL8\ProjetLYME\ROI_Projet_Genie_Maladies_Vectorielles_v2\Données\Forêt"

# Filepath
fpfeuillu = os.path.join(data_dir, "NFI_MODIS250m_2011_kNN_SpeciesGroups_Broadleaf_Spp_v1_clip.tif")
fpconifere = os.path.join(data_dir, "NFI_MODIS250m_2011_kNN_SpeciesGroups_Needleleaf_Spp_v1_clip.tif")
fpunknow = os.path.join(data_dir, "NFI_MODIS250m_2011_kNN_SpeciesGroups_Unknown_Spp_v1_clip.tif")

# Liste de raster
file_list = [fpfeuillu, fpconifere, fpunknow]

# Fusionner les rasters
es.stack(file_list, "Z:\ELTAL8\ProjetLYME\ROI_Projet_Genie_Maladies_Vectorielles_v2\Données/foret.tif")

# Lire les différentes bandes
RasterForet = rio.open("Z:\ELTAL8\ProjetLYME\ROI_Projet_Genie_Maladies_Vectorielles_v2\Données/foret.tif")

feuillu = RasterForet.read(1)
conifere = RasterForet.read(2)
inconnu = RasterForet.read(3)

# Convertir en float
feuillu = feuillu.astype(float)
inconnu = inconnu.astype(float)
conifere = conifere.astype(float)

checkForet = np.greater(conifere, 50)
pasforet = np.where ( checkForet, inconnu , -999 )
'''
np.seterr(divide='ignore', invalid='ignore')

ndvi = np.empty(RasterForet.shape, dtype=rio.float32)

check = np.logical_or ( feuillu > 0, conifere > 0 )

ndvi = np.where ( check,  feuillu / conifere, -999 ) '''

show(pasforet)
