import os
import re
import osr
import urllib
import geopandas as gpd
import rasterio as rio
import json
import pycrs
import math
import numpy as np
from rasterio.merge import merge
from rasterio.mask import mask
from rasterio.plot import show
from rasterio.warp import calculate_default_transform, reproject, Resampling
import matplotlib.pyplot as plt
import gdal
import matplotlib.pyplot as plt
import zipfile
from zipfile import ZipFile
import io
from io import StringIO
import requests
import earthpy as et
from osgeo import ogr
from pyunpack import Archive
import glob
import sys
import pandas as pd


""" Fonction permettant d'extraire le code EPSG (la projection) d'une donnée vectorielle. """
# vectorData: Objet de type geopandas représentant la donnée vectorielle.
# vectorDataCRS: String représentant le code EPSG de la projection utilisée (#).
# vectorDataCRSStr: String représentant le code EPSG de la projection utilisée (EPSG:#).
def extractEPSGVector(vectorData):
    # Extraire le code EPSG (la projection) du fichier vectoriel.
    srs = vectorData.crs
    vectorDataCRS = re.search("epsg:(.*)", str(srs))

    # Si une projection existe, extraire le code numérique et un String pour d'autres fonctions.
    if vectorDataCRS is not None:
        vectorDataCRS = vectorDataCRS.group(1)
        vectorDataCRSStr = "EPSG:" + vectorDataCRS

        return vectorDataCRS, vectorDataCRSStr

    # Si aucune projection n'est détectée, retourner None.
    else:
        return None, None


""" Fonction permettant d'extraire le code EPSG (la projection) de données de type raster. """
# inPath: String représentant le chemin vers le fichier raster entrant.
# rasterCRS: String représentant le code EPSG de la projection utilisée (#).
# rasterCRSStr: String représentant le code EPSG de la projection utilisée (EPSG:#).
def extractEPSGRaster(inPath):
    # Ouvrir le raster pour recherche.
    raster = gdal.Open(inPath, gdal.GA_ReadOnly)

    # Extraire le code EPSG (la projection) du raster.
    rasterCRS = osr.SpatialReference(wkt=raster.GetProjection()).GetAttrValue("AUTHORITY", 1)
    rasterCRSStr = "EPSG:" + rasterCRS

    # Si une projection existe, extraire le code numérique et un String pour d'autres fonctions.
    if rasterCRS is not None:
        return rasterCRS, rasterCRSStr

    # Si aucune projection n'est détectée, retourner None.
    else:
        return None, None


""" Fonction permettant de créer une liste des chemins menant au données. """
# inDir: String représentant le chemin vers le répertoire contenant les fichiers du déterminants.
# criteres: tuple des critèred de sélection des fichiers désirés se terminant par... (".shp", ".pdf").
# conditions: tuple des critères négatifs de sélection des fichiers désirés ne se terminant pas par... (facultatif).
# fichiers: Liste comportant les chemins des fichiers désirés.
def listFiles(inDir, criteres, conditions=None):
    fichiers = []

    for root, dirs, files in os.walk(inDir):
        for file in files:
            if conditions is None:
                if file.endswith(criteres):
                    fichiers.append(os.path.join(root, file))
            else:
                if file.endswith(criteres) and not file.endswith(conditions):
                    fichiers.append(os.path.join(root, file))

    return fichiers


""" Fonction permettant de créer un nouveau répertoire pour le téléchargement de données. """
# inDir: String représentant le chemin du répertoire devant être créé, s'il n'existe pas.
def createDir(inDir):
    if not os.path.exists(inDir):
        print("Creating directory " + inDir + "...")

        os.makedirs(inDir)


""" Fonction permettant de créer les noms de fichiers nécessaires aux différents processus. """
# inDir: String représentant le chemin du répertoire contenant les fichiers créés.
# baseName: String représentant le nom du fichier.
# pixelSize: String représentant la taille d'un pixel d'un raster.
# rasterise: Boolean représentant si un fichier sera rasterisé au cours d'un traitement subséquent (facultatif).
# outPath: String représentant le chemin de la donnée téléchargée.
# outPathReproject: String représentant le chemin de la donnée reprojetée.
# outPathClip: String représentant le chemin de la donnée découpée.
# outPathRaster: String représentant le chemin de la donnée rasterisée.
# outPathResample: String représentant le chemin de la donnée rééchantillonnée.
def createPaths(inDir, baseName, pixelSize, rasterise=False):
    outPath = os.path.join(inDir, baseName)
    outPathReproject = outPath.replace(".", "_reproject.")
    outPathClip = outPath.replace(".", "_clip.")

    if rasterise:
        outPathRaster = outPath.replace(".shp", ".tiff")

        return outPath, outPathReproject, outPathClip, outPathRaster

    else:
        outPathResample = outPath.replace(".", "_resample_" + pixelSize + ".")

        return outPath, outPathReproject, outPathClip, outPathResample


""" Fonction permettant de télécharger des données (compressées ou non) provenant d'un serveur web ou d'un site web. """
# url: String représentant l'adresse URL complète de la donnée à télécharger.
# outPath: String représentant le chemin du fichier sortant.
# pathDir: String représentant le chemin des fichiers décompressés (facultatif).
# zip: Boolean représentant si les données à télécharger sont contenues dans un fichier compressé (facultatif).
def downloadData(url, outPath, pathDir="", compress=False):
    fileName = os.path.basename(url)
    print("Downloading " + fileName + "...")

    urllib.request.urlretrieve(url, outPath)

    if compress:
        print("Unzipping " + fileName + "...")
        Archive(outPath).extractall(pathDir)


""" Fonction permettant de reprojeter un fichier de type raster. """
# inPath: String représentant le chemin vers le fichier raster entrant.
# outPath: String représentant le chemin vers le fichier raster sortant.
# dstCrs: String représentant le code EPSG de la projection voulue (EPSG:#).
def reprojectRaster(inPath, outPath, dstCRS):
    fileName = os.path.basename(inPath)
    print("Reprojecting raster " + fileName + "...")

    # Extraire les métadonnées.
    with rio.open(inPath) as src:
        transform, width, height = calculate_default_transform(src.crs, dstCRS, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({"crs": dstCRS, "transform": transform, "width": width, "height": height})

        # Effectuer la reprojection et exporter le raster résultant.
        with rio.open(outPath, "w", **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(source=rio.band(src, i), destination=rio.band(dst, i), src_transform=src.transform, src_crs=src.crs, dst_transform=transform, dst_crs=dstCRS, resampling=Resampling.nearest)


""" Fonction permettant de reprojeter un fichier de formes. """
# vectorData: Objet de type geopandas représentant le fichier vectoriel entrant.
# outPath: String représentant le chemin vers le fichier vectoriel sortant.
# dstCrs: String représentant le code EPSG de la projection voulue (EPSG:#).
def reprojectVector(vectorData, outPath, dstCRS):
    fileName = os.path.basename(outPath)
    print("Reprojecting " + fileName.replace("_reproject", "") + "...")

    vectorDataReproject = vectorData.to_crs(dstCRS)
    vectorDataReproject.to_file(outPath)


""" Fonction permettant de transformer une géométrie d'une geodataframe en format JSON. """
# gdf: Objet de type geopandas contenant un champ 'geometry'.
def geoToJson(gdf):
    return[json.loads(gdf.to_json())["features"][0]["geometry"]]


""" Fonction permettant de découper un raster selon une région d'intérêt. """
# inPath: String représentant le chemin vers le fichier raster entrant.
# outPath: String représentant le chemin vers le fichier raster sortant.
# clipPoly: Objet de type JSON représentant le polygone servant au découpage.
# epsgVector: int représentant le code EPSG de la projection voulue (#).
def clipRaster(inPath, outPath, clipPoly, epsgVector):
    fileName = os.path.basename(inPath)
    print("Clipping raster " + fileName + "...")

    # Ouvrir le raster.
    raster = rio.open(inPath)

    # Découper le raster.
    outRaster, outTransform = mask(dataset=raster, shapes=clipPoly, crop=True)

    # Mettre à jour les métadonnées.
    outMeta = raster.meta.copy()
    outMeta.update({"driver": "GTiff", "height": outRaster.shape[1], "width": outRaster.shape[2], "transform": outTransform, "crs": pycrs.parse.from_epsg_code(epsgVector).to_proj4()})

    # Exporter le raster résultant.
    with rio.open(outPath, "w", **outMeta) as dest:
        dest.write(outRaster)


""" Fonction permettant de découper un fichier vectoriel selon une région d'intérêt. """
# inPath: String représentant le chemin vers le fichier vectoriel entrant.
# outPath: String représentant le chemin vers le fichier vectoriel sortant.
# clipPoly: Objet de type geopandas servant au découpage.
# clip: Boolean indiquant si un fichier découpé a été produit.
def clipVector(inPath, outPath, clipPoly):
    fileName = os.path.basename(inPath)
    print("Clipping vector file " + fileName + "...")

    # Ouvrir le fichier vectoriel.
    dataVector = gpd.read_file(inPath)

    if not dataVector.empty:
        # Appliquer un buffer nul (pour gérer les géométries invalides, au besoin).
        dataVector["geometry"] = dataVector.geometry.buffer(0)

        # Découper le fichier vectoriel
        dataVectorClip = gpd.clip(dataVector, clipPoly)

        if not dataVectorClip.empty:
            # Exporter le raster résultant.
            dataVectorClip.to_file(outPath)
            clip = True

            return clip

        else:
            print("No data after clipping.")
            clip = False

            return clip


""" Fonction permettant d'extraire la hauteur et la largeur d'un pixel pour un raster. """
# inPath: String représentant le chemin vers le fichier raster entrant.
# width: nombre représentant la largeur d'un pixel.
# height: nombre représentant la hauteur d'un pixel.
def getPixelSize(inPath):
    # Ouvrir le raster
    raster = rio.open(inPath)

    # Extraire la largeur et la hauteur d'un pixel.
    width = raster.transform[0]
    height = -(raster.transform[4])

    return width, height


""" Fonction permettant de rééchantillonner un raster. """
# inPath: String représentant le chemin vers le fichier raster entrant.
# inPathRef: String représentant le chemin vers le fichier raster  de référence.
# outPath: String représentant le chemin vers le fichier raster sortant.
def resampleRaster(inPath, inPathRef, outPath):
    fileName = os.path.basename(inPath)
    print("Resampling raster " + fileName + "...")

    src = gdal.Open(inPath, gdal.GA_ReadOnly)
    srcProj = src.GetProjection()

    ref = gdal.Open(inPathRef, gdal.GA_ReadOnly)
    refProj = ref.GetProjection()
    refTrans = ref.GetGeoTransform()
    pixelWidth = ref.RasterXSize
    pixelHeight = ref.RasterYSize

    out = gdal.GetDriverByName("GTiff").Create(outPath, pixelWidth, pixelHeight, 1, gdal.GDT_Float32)
    out.SetGeoTransform(refTrans)
    out.SetProjection(refProj)

    gdal.ReprojectImage(src, out, srcProj, refProj, gdal.GRA_NearestNeighbour)

    del out


""" Fonction permettant de rasteriser un fichier vectoriel. """
# inPathVector: String représentant le chemin vers le fichier vectoriel entrant.
# inPathRaster: String représentant le chemin vers le fichier raster servant de référence.
# outPath: String représentant le chemin vers le fichier raster sortant.
# champs: String représentant le champs où sélectionner les données pertinentes.
# valeur: String représentant la valeur des données pertinentes qui doivent être rasterisées.
def rasteriseVector(inPathVector, inPathRaster, outPath, champs, valeur):
    fileName = os.path.basename(inPathVector)
    print("Rasterising " + fileName + "...")

    rasterRef = gdal.Open(inPathRaster, gdal.GA_ReadOnly)

    vectorData = ogr.Open(inPathVector)
    vectorLayer = vectorData.GetLayer()

    out = gdal.GetDriverByName("GTiff").Create(outPath, rasterRef.RasterXSize, rasterRef.RasterYSize, 1, gdal.GDT_Byte, options=["COMPRESS=DEFLATE"])
    out.SetProjection(rasterRef.GetProjectionRef())
    out.SetGeoTransform(rasterRef.GetGeoTransform())

   # if not math.isnan(valeur):
    if not valeur == None:
        SQL = champs + "='" + valeur + "'"
        vectorLayer.SetAttributeFilter(SQL)

    else:
        band = out.GetRasterBand(1)
        band.SetNoDataValue(-9999)

    gdal.RasterizeLayer(out, [1], vectorLayer, burn_values=[1])

    del out

def convertToRGB(pathImage):
    fileName = os.path.basename(pathImage)
    image = gdal.Open(pathImage, gdal.GA_ReadOnly)
    imageBande1 = image.GetRasterBand(1).ReadAsArray()
    pathImage2 = pathImage[:-5] + "_RGB.tiff"

    image_RGB = gdal.GetDriverByName("GTiff").Create(pathImage2,
                                                       image.RasterXSize, image.RasterYSize, 3)
    image_RGB.GetRasterBand(1).WriteArray(imageBande1)
    image_RGB.GetRasterBand(2).WriteArray(imageBande1)
    image_RGB.GetRasterBand(3).WriteArray(imageBande1)

    rasterImage1B1 = image_RGB.GetRasterBand(1).ReadAsArray()
    rasterImage1B2 = image_RGB.GetRasterBand(2).ReadAsArray()
    rasterImage1B3 = image_RGB.GetRasterBand(3).ReadAsArray()

    for i in range(image.RasterYSize):
        for j in range(image.RasterXSize):
            if imageBande1[i, j] == 0:
                rasterImage1B1[i, j] = 255
                rasterImage1B2[i, j] = 255
                rasterImage1B3[i, j] = 255

            elif imageBande1[i, j] == 1:
                rasterImage1B1[i, j] = 0
                rasterImage1B2[i, j] = 0
                rasterImage1B3[i, j] = 0

    image_RGB.GetRasterBand(1).WriteArray(rasterImage1B1)
    image_RGB.GetRasterBand(2).WriteArray(rasterImage1B2)
    image_RGB.GetRasterBand(3).WriteArray(rasterImage1B3)

    image_RGB.SetProjection(image.GetProjection())
    image_RGB.SetGeoTransform(image.GetGeoTransform())
    image_RGB.FlushCache()

    del image_RGB

def rasterClassification(inPathImage1, inPathImage2, outPath):
    if not os.path.exists(outPath):
        fileName = os.path.basename(outPath)

        rasterImage1 = gdal.Open(inPathImage1, gdal.GA_ReadOnly)
        rasterImage2 = gdal.Open(inPathImage2, gdal.GA_ReadOnly)

        rasterImage1B1 = rasterImage1.GetRasterBand(1).ReadAsArray()
        rasterImage1B2 = rasterImage1.GetRasterBand(2).ReadAsArray()
        rasterImage1B3 = rasterImage1.GetRasterBand(3).ReadAsArray()

        rasterImage2B1 = rasterImage1.GetRasterBand(1).ReadAsArray()
        rasterImage2B2 = rasterImage1.GetRasterBand(2).ReadAsArray()
        rasterImage2B3 = rasterImage1.GetRasterBand(3).ReadAsArray()

        for i in range(rasterImage1.RasterYSize):
            for j in range(rasterImage1.RasterXSize):
                if rasterImage1B1[i, j] != 255 and rasterImage1B2[i, j] != 255 and rasterImage1B3[i, j] != 255:
                    rasterImage1B1[i, j] = 0
                    rasterImage1B2[i, j] = 255
                    rasterImage1B3[i, j] = 0

                else:
                    rasterImage1B1[i, j] = rasterImage2B1[i, j]
                    rasterImage1B2[i, j] = rasterImage2B2[i, j]
                    rasterImage1B3[i, j] = rasterImage2B3[i, j]

        rasterClass = gdal.GetDriverByName("GTiff").Create(outPath,
                                                           rasterImage1.RasterXSize, rasterImage1.RasterYSize, 3)
        rasterClass.GetRasterBand(1).WriteArray(rasterImage1B1)
        rasterClass.GetRasterBand(2).WriteArray(rasterImage1B2)
        rasterClass.GetRasterBand(3).WriteArray(rasterImage1B3)

        rasterClass.SetProjection(rasterImage1.GetProjection())
        rasterClass.SetGeoTransform(rasterImage1.GetGeoTransform())
        rasterClass.FlushCache()