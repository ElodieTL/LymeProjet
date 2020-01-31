import os
import re
import osr
import urllib
import geopandas as gpd
#import rasterio
import gdal
#from rasterio.plot import show
import matplotlib.pyplot as plt

ROIPath = "Z:/MALAM357/GMT-3051 Projet en génie géomatique II/Données/ROI/ROI_Projet_Genie_Maladies_Vectorielles_v2.shp"

ROIData = gpd.read_file(ROIPath)
ROICrs = re.search('epsg:(.*)', ROIData.crs["init"])

if ROICrs:
    ROICrs = ROICrs.group(1)

# Télécharger les données de forêt de NRCan RRRRRRRRRRRRRR
rasters = []

outputDir = r"Z:\MALAM357\GMT-3051 Projet en génie géomatique II\Données\Forêt"

urlList = ["http://ftp.geogratis.gc.ca/pub/nrcan_rncan/Forests_Foret/canada-forests-attributes_attributs-forests-canada/2011-attributes_attributs-2011/NFI_MODIS250m_2011_kNN_SpeciesGroups_Broadleaf_Spp_v1.tif",
           "http://ftp.geogratis.gc.ca/pub/nrcan_rncan/Forests_Foret/canada-forests-attributes_attributs-forests-canada/2011-attributes_attributs-2011/NFI_MODIS250m_2011_kNN_SpeciesGroups_Needleleaf_Spp_v1.tif",
           "http://ftp.geogratis.gc.ca/pub/nrcan_rncan/Forests_Foret/canada-forests-attributes_attributs-forests-canada/2011-attributes_attributs-2011/NFI_MODIS250m_2011_kNN_SpeciesGroups_Unknown_Spp_v1.tif"]

if not os.path.exists(outputDir):
    os.makedirs(outputDir)
    
for url in urlList:
    fileName = os.path.basename(url)
    outputPath = os.path.join(outputDir, fileName)
    
    if not os.path.exists(outputPath):
        print("Downloading", fileName)
        r = urllib.request.urlretrieve(url, outputPath)

        raster = gdal.Open(outputPath)
        rasterCrs = osr.SpatialReference(wkt = raster.GetProjection()).GetAttrValue('AUTHORITY', 1)

        if rasterCrs != ROICrs:
            print("Reprojecting image " + fileName + "...")
            gdal.Warp(outputPath.replace(".", "_reproject."), raster, dstSRS = "EPSG:" + ROICrs)

        rasters.append(raster)
        
    else:
        raster = gdal.Open(outputPath)
        rasterCrs = osr.SpatialReference(wkt = raster.GetProjection()).GetAttrValue('AUTHORITY', 1)
        if rasterCrs != ROICrs:
            print("Reprojecting image " + fileName + "...")
            gdal.Warp(outputPath.replace(".", "_reproject."), raster, dstSRS = "EPSG:" + ROICrs)

        rasters.append(raster)
