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


checkForet = np.greater(inconnu, 50)
pasforet = np.where ( checkForet, inconnu , 0 )


np.seterr(divide='ignore', invalid='ignore')

check = np.logical_and ( conifere/feuillu > 0.8, conifere/feuillu < 1.2)

mixte = np.where ( check, pasforet , 50 )

coniferew = np.where ( conifere > feuillu, mixte , 100 )

check3 = np.logical_and ( conifere < feuillu , coniferew != 50, coniferew != 0)

feuilluw = np.where ( check3, coniferew , 200 )

ep.plot_bands(coniferew)
plt.show()