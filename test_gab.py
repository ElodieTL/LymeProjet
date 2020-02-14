# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 09:55:21 2020

@author: Administrateur
"""

import rasterio
from rasterio.merge import merge
#from rasterio.plot import show
from rasterio.warp import calculate_default_transform, reproject, Resampling
import glob
import os
import os.path 
import rasterio as rio
import geopandas as gpd
import earthpy as et
import earthpy.spatial as es
import earthpy.plot as ep
#import numpy
#import matplotlib.pyplot as plt


""" Fonction """
# Fontion pour récupérer image dans un dossier composé de dossiers
def list_chemin_image(path, critere): 
    fichier=[] 
    #fichier.extend(glob.glob(os.path.join(path,critere)))
    for i in path: 
        if os.path.isdir(i): fichier.extend(glob.glob(os.path.join(i,critere))) 
    return fichier

# Fonction pour reprojeter les images
def reprojection_image(inpath, outpath, new_crs):
    dst_crs = new_crs # CRS for web meractor 

    with rio.open(inpath) as src:
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height
        })

        with rio.open(outpath, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rio.band(src, i),
                    destination=rio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest)



# Selection de tous les fichiers .tif de tous les dossiers
dossier_chemin = glob.glob("Z:\GALAL35\Projet_lyme\LymeProjet\image\*")
images = list_chemin_image(dossier_chemin,"L*B3.tif" )

# Reprojection des images
images_proj = [] #Contient le nom des chemins pour les images
for i in images:
    nom, extension = i.split(".TIF")
    new_crs = 'EPSG:6622' # Projection conique conforme de Lambert du Québec à 2 parallèles d’appui (46 et 60)
    output_image = nom + 'reproj' + extension
    reprojection_image(i,output_image , new_crs)
    images_proj.append(output_image)

# Merger des images Landsat
repertoire = r"Z:\GALAL35\Projet_lyme\LymeProjet\image\Mosaic"
if not os.path.exists(repertoire):
 os.makedirs(repertoire)

out_fp = r"Z:\GALAL35\Projet_lyme\LymeProjet\image\Mosaic\Mosaic_B3.tif" #raster de sortie #location du raster de sortie

src_files_to_mosaic = []
for fp in images_proj:
    src = rasterio.open(fp)
    src_files_to_mosaic.append(src)
    
mosaic, out_trans = merge(src_files_to_mosaic)

out_meta = src.meta.copy()
out_meta.update({"driver": "GTiff",
                 "height": mosaic.shape[1],
                 "width": mosaic.shape[2],
                 "transform": out_trans,
                 "crs": "+init=epsg:6622 "
                })

with rasterio.open(out_fp, "w", **out_meta) as dest:
    dest.write(mosaic)      # Création du nouveau raster


polygoneDecoupe = gpd.read_file(r"Z:\GALAL35\Projet_lyme\LymeProjet\ROI_Projet_Genie_Maladies_Vectorielles_v2\ROI_Projet_Genie_Maladies_Vectorielles_v2.shp")
#new_crs = 'EPSG:6622' # Projection conique conforme de Lambert du Québec à 2 parallèles d’appui (46 et 60)
polygoneDecoupe_Reproj = polygoneDecoupe.to_crs({'init': 'epsg:6622'})


with rio.open(out_fp) as src:
    single_cropped_image, single_cropped_meta  = es.crop_image(src, polygoneDecoupe_Reproj)


with rasterio.open(out_fp, "w", **single_cropped_meta) as dest:
    dest.write(single_cropped_image)      # Création du nouveau raster