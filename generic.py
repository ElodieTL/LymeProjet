import os
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
import matplotlib.pyplot as plt
import gdal
import matplotlib.pyplot as plt
import zipfile
from zipfile import ZipFile
import io
from io import StringIO
import requests

# Fonction permettant d'extraire le code EPSG (la projection) d'une donnée vectorielle.
# data: objet geopandas représentant la donnée vectorielle.
# dataCRS: entier représentant le code EPSG de la projection utilisée (#).
# dataCRSStr: String représentant le code EPSG de la projection utilisée (EPSG:#).
def extractEPSGVector(data):
    # Extraire le code EPSG (la projection) de la zone d'intérêt.
    dataCRS = re.search('epsg:(.*)', data.crs["init"])

    # Si une projection existe, extraire le code numérique et un String pour d'autres fonctions.
    if dataCRS is not None:
        dataCRS = dataCRS.group(1)
        dataCRSStr = "EPSG:" + dataCRS

        return dataCRS, dataCRSStr

    # Si une projection n'est pas détectée, retourner None.
    else:
        return None, None

# Fonction permettant d'extraire le code EPSG (la projection) de données de type raster.
# inPath: String représentant le chemin vers le fichier raster entrant.
# rasterCRS: entier représentant le code EPSG de la projection utilisée (#).
# rasterCRSStr: String représentant le code EPSG de la projection utilisée (EPSG:#).
def extractEPSGRaster(inPath):
    # Ouvrir le raster.
    raster = gdal.Open(inPath)

    # Extraire le code EPSG.
    rasterCRS = osr.SpatialReference(wkt = raster.GetProjection()).GetAttrValue('AUTHORITY', 1)
    rasterCRSStr = "EPSG:" + rasterCRS

    return rasterCRS, rasterCRSStr

# Fonction permettant de créer une liste de fichiers de type raster.
# inDir: String représentant le répertoire où sont stockées les fichiers.
# rasterFiles: List contenant les fichiers de type raster.
def listRasterFiles(inDir):
    # Créer un liste vide.
    rasterFiles = []

    # Parcourir le répertoire afin de lister les fichiers de type raster.
    for root, dirs, files in os.walk(inDir):
        for file in files:
            if file.endswith((".tif", ".TIF", ".TIFF", ".tiff")):
                rasterFiles.append(os.path.join(root, file))

    return rasterFiles

# Fonction permettant de télécharger des données (au format .zip ou non) provenant d'un serveur ou d'un site web.
# url: String représentant l'adresse URL complète de la donnée à télécharger (.ZIP).
# outPath: String représentant le chemin du fichier sortant.
# pathDir: String représentant le chemin des fichiers dé-zippés
# zip: Boolean représentant si les données à télécharger sont contenues dans un fichier .zip.
def downloadData(url, outPath, pathDir = "", zip = false):
    fileName = os.path.basename(url)

    print("Downloading " + fileName + "...")
    urllib.request.urlretrieve(url, outPath)

    if zip:
        with ZipFile(outPath, 'r') as zipObj:
            print("Unzipping " + fileName + "...")
            zipObj.extractall(pathDir)

# Fonction permettant de reprojeter un fichier de type raster.
# inPath: String représentant le chemin vers le fichier raster entrant.
# outPath: String représentant le chemin vers le fichier raster sortant.
# dstCrs: String représentant le code EPSG de la projection voulue (EPSG:#).
def reprojectRaster(inPath, outPath, dstCRS):
    fileName = os.path.basename(inPath)
    print("Reprojecting raster " + fileName + "...")

    dst_crs = dstCRS

    # Extraire les métadonnées.
    with rio.open(inPath) as src:
        transform, width, height = calculate_default_transform(src.crs, dst_crs, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({'crs': dst_crs, 'transform': transform, 'width': width, 'height': height})

        # Effectuer la reprojection et exporter le raster résultant.
        with rio.open(outPath, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(source = rio.band(src, i), destination = rio.band(dst, i), src_transform = src.transform, src_crs = src.crs, dst_transform = transform, dst_crs = dst_crs, resampling = Resampling.nearest)

# Fonction permettant de reprojeter un fichier de formes.
# data: Fichier shp entrant.
# outPath: String représentant le chemin vers le fichier shp sortant.
# dstCrs: String représentant le code EPSG de la projection voulue (EPSG:#).
def reprojectShp(data, outPath, dstCRS):
    fileName = os.path.basename(outPath)
    print("Reprojecting: " + fileName + "...")

    data_reproject = data.to_crs(dstCRS)
    data_reproject.to_file(outPath)

# Fonction permettant d'ouvrir un raster et de l'ajouter à une liste de rasters ouverts.
# inPath: String représentant le chemin vers le fichier raster entrant.
# rasters: List de rasters ouverts.
def addRastertoRasters(inPath, rasters):
    # Ouvrir le raster.
    raster = rio.open(inPath)

    # Ajouter à la liste.
    rasters.append(raster)

    return rasters

# Fonction permettant de transformer une géométrie d'une geodataframe en format json.
# gdf: objet de type geodataframe contenant un champ 'geometry'.
def geoToJson(gdf):
    return[json.loads(gdf.to_json())['features'][0]['geometry']]

# Fonction permettant de découper un raster selon une région d'intérêt.
# inPath: String représentant le chemin vers le fichier raster entrant.
# outPath: String représentant le chemin vers le fichier raster sortant.
# clipPoly: objet de type json représentant le polygone servant au découpage.
# epsgROI: int représentant le code EPSG de la projection voulue (#).
def clipRaster(inPath, outPath, clipPoly, epsgROI):
    fileName = os.path.basename(inPath)
    print("Clipping raster " + fileName + "...")

    # Ouvrir le raster.
    raster = rio.open(inPath)

    # Découper le raster
    outRaster, outTransform = mask(dataset = raster, shapes = clipPoly, crop = True)

    # Mettre à jour les métadonnées.
    outMeta = raster.meta.copy()
    outMeta.update({"driver": "GTiff", "height": outRaster.shape[1], "width": outRaster.shape[2], "transform": outTransform, "crs": pycrs.parse.from_epsg_code(epsgROI).to_proj4()})

    # Exporter le raster résultant.
    with rio.open(outPath, "w", **outMeta) as dest:
        dest.write(outRaster)

# Fonction permettant d'extraire la hauteur et la largeur d'un pixel pour un raster.
# inPath: String représentant le chemin vers le fichier raster entrant.
# width: largeur d'un pixel.
# height: hauteur d'un pixel.
def getPixelSize(inPath):
    # Ouvir le raster
    raster = rio.open(inPath)

    # Extraire la largeur et la hauteur d'un pixel.
    width = raster.transform[0]
    height = -(raster.transform[4])

    return width, height

# Fonction permettant de rééchantillonner un raster.
# inPath: String représentant le chemin vers le fichier raster entrant.
# outPath: String représentant le chemin vers le fichier raster sortant.
# inPixelSize: largeur/hauteur d'un pixel déterminée à l'aide de la fonction getPixelSize().
# outPixelSize: largeur/hauteur d'un pixel voulue.
def resampleRaster(inPath, outPath, inPixelSize, outPixelSize):
    fileName = os.path.basename(inPath)
    print("Resampling raster " + fileName + "...")

    # Calcul du facteur d'agrandissement/de réduction.
    factor = inPixelSize / outPixelSize

    # Ouvrir le raster.
    raster = rio.open(inPath)

    # Rééchantillonner le raster.
    data = raster.read(out_shape = (raster.count, int(raster.width * factor), int(raster.height * factor)), resampling = Resampling.bilinear)
    transform = raster.transform * raster.transform.scale((raster.width / data.shape[-2]), (raster.height / data.shape[-1]))

    # Mettre à jour les métadonnées.
    meta = raster.meta.copy()
    meta.update({"driver": "GTiff", "height": int(raster.height * factor), "width": int(raster.width * factor), "transform": transform})

    # Exporter le raster résultant.
    with rio.open(outPath, 'w', **meta) as dst:
        dst.write(data)