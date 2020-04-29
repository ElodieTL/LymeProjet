import os
import re
import osr
import urllib
import geopandas as gpd
import rasterio as rio
import json
import pycrs
import shutil
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
import earthpy.spatial as es
import earthpy.plot as ep
from operator import itemgetter
import time
import warnings

warnings.filterwarnings('ignore', 'GeoSeries.notna', UserWarning)


""" Fonction permettant d'extraire le code EPSG (la projection) d'une donnée vectorielle. """
# inVectorData: Objet de type geopandas représentant la donnée vectorielle.
# vectorDataCRS: String représentant le code EPSG de la projection utilisée (#).
# vectorDataCRSStr: String représentant le code EPSG de la projection utilisée (EPSG:#).
def extractEPSGVector(inVectorData):
    # Extraire le code EPSG (la projection) du fichier vectoriel.
    srs = inVectorData.crs

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
# inRasterPath: String représentant le chemin vers le fichier raster entrant.
# rasterCRS: String représentant le code EPSG de la projection utilisée (#).
# rasterCRSStr: String représentant le code EPSG de la projection utilisée (EPSG:#).
def extractEPSGRaster(inRasterPath):
    # Ouvrir le raster pour recherche.
    raster = gdal.Open(inRasterPath, gdal.GA_ReadOnly)

    # Extraire le code EPSG (la projection) du raster.
    rasterCRS = osr.SpatialReference(wkt=raster.GetProjection()).GetAttrValue("AUTHORITY", 1)
    rasterCRSStr = "EPSG:" + rasterCRS

    # Si une projection existe, extraire le code numérique et un String pour d'autres fonctions.
    if rasterCRS is not None:
        return rasterCRS, rasterCRSStr

    # Si aucune projection n'est détectée, retourner None.
    else:
        return None, None


""" Fonction permettant de créer une liste des chemins menant aux données. """
# inDir: String représentant le chemin vers le répertoire contenant les fichiers du déterminants.
# criteres: tuple des critères de sélection des fichiers désirés se terminant par... (".shp", ".pdf").
# conditions: tuple des critères négatifs de sélection des fichiers désirés ne se terminant pas par... (facultatif).
# listFichiers: Liste comportant les chemins des fichiers désirés.
def listFiles(inDir, criteres, conditions=None):
    listFichiers = []

    for root, dirs, files in os.walk(inDir):
        for file in files:
            if conditions is None:
                if file.endswith(criteres):
                    listFichiers.append(os.path.join(root, file))
            else:
                if file.endswith(criteres) and not file.endswith(conditions):
                    listFichiers.append(os.path.join(root, file))

    return listFichiers


""" Fonction permettant de créer un nouveau répertoire pour le téléchargement de données. """
# inDir: String représentant le chemin du répertoire devant être créé, s'il n'existe pas.
def createDir(inDir):
    if not os.path.exists(inDir):
        print("          Création du répertoire " + inDir + "...")

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
    print("          Téléchargement du fichier " + fileName + "...")

    urllib.request.urlretrieve(url, outPath)

    if compress:
        print("          Extraction du fichier " + fileName + "...")

        Archive(outPath).extractall(pathDir)


""" Fonction permettant de reprojeter un fichier de type raster. """
# inRasterPath: String représentant le chemin vers le fichier raster entrant.
# outRasterPath: String représentant le chemin vers le fichier raster sortant.
# dstCrs: String représentant le code EPSG de la projection voulue (EPSG:#).
def reprojectRaster(inRasterPath, outRasterPath, dstCRS):
    fileName = os.path.basename(inRasterPath)
    print("          Reprojection du raster " + fileName + "...")

    # Extraire les métadonnées.
    with rio.open(inRasterPath) as src:
        transform, width, height = calculate_default_transform(src.crs, dstCRS, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({"crs": dstCRS, "transform": transform, "width": width, "height": height})

        # Effectuer la reprojection et exporter le raster résultant.
        with rio.open(outRasterPath, "w", **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(source=rio.band(src, i), destination=rio.band(dst, i), src_transform=src.transform, src_crs=src.crs, dst_transform=transform, dst_crs=dstCRS, resampling=Resampling.nearest)


""" Fonction permettant de reprojeter un fichier de formes. """
# inVectorData: Objet de type geopandas représentant le fichier vectoriel entrant.
# outVectorPath: String représentant le chemin vers le fichier vectoriel sortant.
# dstCrs: String représentant le code EPSG de la projection voulue (EPSG:#).
def reprojectVector(inVectorData, outVectorPath, dstCRS):
    fileName = os.path.basename(outVectorPath)
    print("          Reprojection du fichier " + fileName.replace("_reproject", "") + "...")

    vectorDataReproject = inVectorData.to_crs(dstCRS)
    vectorDataReproject.to_file(outVectorPath)


""" Fonction permettant de transformer une géométrie d'une geodataframe en format JSON. """
# gdf: Objet de type geopandas contenant un champ 'geometry'.
def geoToJson(gdf):
    return[json.loads(gdf.to_json())["features"][0]["geometry"]]


""" Fonction permettant de découper un raster selon une région d'intérêt. """
# inRasterPath: String représentant le chemin vers le fichier raster entrant.
# outRasterPath: String représentant le chemin vers le fichier raster sortant.
# clipPoly: Objet de type JSON représentant le polygone servant au découpage.
# dstCRS: int représentant le code EPSG de la projection voulue (#).
def clipRaster(inRasterPath, outRasterPath, clipPoly, dstCRS):
    fileName = os.path.basename(inRasterPath)
    print("          Découpage du raster " + fileName + "...")

    # Ouvrir le raster.
    raster = rio.open(inRasterPath)

    # Découper le raster.
    outRaster, outTransform = mask(dataset=raster, shapes=clipPoly, crop=True)

    # Mettre à jour les métadonnées.
    outMeta = raster.meta.copy()
    outMeta.update({"driver": "GTiff", "height": outRaster.shape[1], "width": outRaster.shape[2], "transform": outTransform, "crs": pycrs.parse.from_epsg_code(dstCRS).to_proj4()})

    # Exporter le raster résultant.
    with rio.open(outRasterPath, "w", **outMeta) as dest:
        dest.write(outRaster)


""" Fonction permettant de découper un fichier vectoriel selon une région d'intérêt. """
# inVectorPath: String représentant le chemin vers le fichier vectoriel entrant.
# outVectorPath: String représentant le chemin vers le fichier vectoriel sortant.
# clipPoly: Objet de type geopandas servant au découpage.
# clip: Boolean indiquant si un fichier découpé a été produit.
def clipVector(inVectorPath, outVectorPath, clipPoly):
    fileName = os.path.basename(inVectorPath)
    print("          Découpage du fichier vectoriel " + fileName + "...")

    # Ouvrir le fichier vectoriel.
    dataVector = gpd.read_file(inVectorPath)

    if not dataVector.empty:
        if dataVector["geometry"][0].geom_type == "Polygon" or dataVector["geometry"][0].geom_type == "MultiPolygon":
            # Appliquer un buffer nul (pour gérer les géométries invalides, au besoin).
            dataVector["geometry"] = dataVector.geometry.buffer(0)

        # Déterminer si la couche comporte que des éléments de type point
        #filterPoint = False
        #dataVector["geometry"] = dataVector.apply(next(filter(lambda row: row.geometry.geom_type == "Point", filterPoint)))

        # Découper le fichier vectoriel
        dataVectorClip = gpd.clip(dataVector, clipPoly)

        if not dataVectorClip.empty:
            # Exporter le raster résultant.
            dataVectorClip.to_file(outVectorPath)
            clip = True

            return clip

        else:
            print("               Aucune donnée restante après découpage. Supression des fichiers liés.")
            clip = False

            # Supprimer les fichiers afin de ne pas refaire les traitements dans le futur.
            for file in glob.glob(inVectorPath.replace("_reproject.shp", "*")):
                os.remove(file)

            return clip


""" Fonction permettant de codifier le déterminant courant en String. """
# noDet: nombre représentant le code du déterminant.
# strDet: String représentant le déterminant sous format texte.
def getDet(noDet):
    if noDet == 0:
        strDet = "Foret"

    elif noDet == 1:
        strDet = "Zones humides"

    elif noDet == 2:
        strDet = "Eau"

    elif noDet == 3:
        strDet = "Parcs"

    elif noDet == 4:
        strDet = "Zones agricoles"

    elif noDet == 5:
        strDet = "Voies de communication"

    elif noDet == 6:
        strDet = "Zones anthropisees"

    elif noDet == 7:
        strDet = "Couverture du sol"

    return strDet


""" Fonction permettant de rééchantillonner un raster. """
# inRasterPath: String représentant le chemin vers le fichier raster entrant.
# inRefRasterPath: String représentant le chemin vers le fichier raster  de référence.
# outRasterPath: String représentant le chemin vers le fichier raster sortant.
def resampleRaster(inRasterPath, inRefRasterPath, outRasterPath):
    fileName = os.path.basename(inRasterPath)
    print("          Rééchantillonnage du raster " + fileName + "...")

    src = gdal.Open(inRasterPath, gdal.GA_ReadOnly)
    srcProj = src.GetProjection()

    ref = gdal.Open(inRefRasterPath, gdal.GA_ReadOnly)
    refProj = ref.GetProjection()
    refTrans = ref.GetGeoTransform()

    out = gdal.GetDriverByName("GTiff").Create(outRasterPath, ref.RasterXSize, ref.RasterYSize, 1, gdal.GDT_Byte)
    out.SetGeoTransform(refTrans)
    out.SetProjection(refProj)

    gdal.ReprojectImage(src, out, srcProj, refProj, gdal.GRA_NearestNeighbour)

    del out


""" Fonction permettant de rastériser un fichier vectoriel. """
# inVectorPath: String représentant le chemin vers le fichier vectoriel entrant.
# inRasterPath: String représentant le chemin vers le fichier raster servant de référence.
# outRasterPath: String représentant le chemin vers le fichier raster sortant.
# champs: String représentant le champs où sélectionner les données pertinentes.
# valeur: String représentant la valeur des données pertinentes qui doivent être rasterisées.
# noDet: nombre correspondant au numéro du déterminant.
def rasteriseVector(inVectorPath, inRasterPath, outRasterPath, champs, valeur, noDet):
    fileName = os.path.basename(inVectorPath)
    print("          Rasterisation du fichier " + fileName + "...")

    rasterRef = gdal.Open(inRasterPath, gdal.GA_ReadOnly)

    vectorData = ogr.Open(inVectorPath)
    vectorLayer = vectorData.GetLayer()

    out = gdal.GetDriverByName("GTiff").Create(outRasterPath, rasterRef.RasterXSize, rasterRef.RasterYSize, 1, gdal.GDT_Byte)
    out.SetProjection(rasterRef.GetProjectionRef())
    out.SetGeoTransform(rasterRef.GetGeoTransform())

    if type(valeur) == str:
        SQL = champs + "='" + valeur + "'"
        vectorLayer.SetAttributeFilter(SQL)

    band = out.GetRasterBand(1)
    band.Fill(-9999)
    band.SetNoDataValue(-9999)
    band.FlushCache()

    gdal.RasterizeLayer(out, [1], vectorLayer, None, None, [5 * noDet])


""" Fonction permettant de fusionner deux rasters en priorisant le premier. (Intra) """
# inRaster1Path: String représentant le chemin vers le premier raster. Le raster intermédiaire doit toujours être le inRaster1Path.
# inRaster2Path: String représentant le chemin vers le deuxième raster.
# outRasterPath: String représentant le chemin vers le raster en sortie.
# noDet: nombre représentant le numéro du déterminant.
def rasterClassification(inRaster1Path, inRaster2Path, outRasterPath, noDet):
    raster1 = gdal.Open(inRaster1Path, gdal.GA_ReadOnly)
    raster2 = gdal.Open(inRaster2Path, gdal.GA_ReadOnly)

    raster1B1 = raster1.GetRasterBand(1).ReadAsArray()
    raster2B1 = raster2.GetRasterBand(1).ReadAsArray()

    for i in range(raster1.RasterYSize):
        for j in range(raster1.RasterXSize):
            if raster1B1[i, j] != 5 * noDet:
                raster1B1[i, j] = raster2B1[i, j]

    del raster1

    rasterClass = gdal.GetDriverByName("GTiff").Create(outRasterPath, raster2.RasterXSize, raster2.RasterYSize, 1)
    rasterClass.GetRasterBand(1).WriteArray(raster1B1)

    rasterClass.SetProjection(raster2.GetProjection())
    rasterClass.SetGeoTransform(raster2.GetGeoTransform())
    rasterClass.FlushCache()


""" Fonction permettant de fusionner deux rasters en priorisant le premier. (Inter) """
# inRaster1Path: String représentant le chemin vers le premier raster. Le raster intermédiaire doit toujours être le inRaster1Path.
# inRaster2Path: String représentant le chemin vers le deuxième raster.
# outRasterPath: String représentant le chemin vers le raster en sortie.
# noDet2: nombre représentant le numéro du déterminant représentant le deuxière raster.
def rasterClassificationTotale(inRaster1Path, inRaster2Path, outPath, noDet2):
    raster1 = gdal.Open(inRaster1Path, gdal.GA_ReadOnly)
    raster2 = gdal.Open(inRaster2Path, gdal.GA_ReadOnly)

    raster1B1 = raster1.GetRasterBand(1).ReadAsArray()
    raster2B1 = raster2.GetRasterBand(1).ReadAsArray()

    for i in range(raster1.RasterYSize):
        for j in range(raster1.RasterXSize):
            if noDet2 == 0:
                if raster2B1[i, j] in range(1, 4):
                    raster1B1[i, j] = raster2B1[i, j]

            else:
                if raster2B1[i, j] == 5 * noDet2:
                    raster1B1[i, j] = raster2B1[i, j]

    del raster1

    rasterClass = gdal.GetDriverByName("GTiff").Create(outPath, raster2.RasterXSize, raster2.RasterYSize, 1)
    rasterClass.GetRasterBand(1).WriteArray(raster1B1)

    rasterClass.SetProjection(raster2.GetProjection())
    rasterClass.SetGeoTransform(raster2.GetGeoTransform())
    rasterClass.FlushCache()


""" Fonction permettant de faire la fusion intra déterminant de Forêt (RN Canada). """
# inPathFeuillus: String représentant le chemin vers le fichier raster des feuillus.
# inPathConifères: String représentant le chemin vers le fichier raster des conifères.
# inPathInconnu: String représentant le chemin vers le fichier raster de la végétation iconnue.
def foret(inPathFeuillus, inPathConiferes, inPathInconnu, dir):
    # Création de Strings représentant les chemins vers de nouveaux fichiers créés.
    pathAll = os.path.join(dir, "NFI_MODIS250m_2011_kNN_SpeciesGroups_All_Spp_v1_resample_30.tif")
    pathClass = os.path.join(dir, "NFI_MODIS250m_2011_kNN_SpeciesGroups_Class_Spp_v1_resample_30.tif")

    # Si la fusion des trois rasters n'a pas déjà été faite.
    if not os.path.exists(pathAll):
        fileName = os.path.basename(pathAll)
        print("          Création du raster fusionné " + fileName + "...")

        # Création d'une liste des fichiers raster pertinents.
        list = [inPathFeuillus, inPathConiferes, inPathInconnu]

        # Fusionner les rasters contenus dans la liste.
        es.stack(list, pathAll)  # 2 = Feuillus, 1 = Conifères, 0 = Inconnu.

    # Si la classification n'a pas été faite.
    if not os.path.exists(pathClass):
        fileName = os.path.basename(pathClass)
        print("          Classification du raster " + fileName + "...")

        # Ouverture des données.
        rasterAll = gdal.Open(pathAll, gdal.GA_ReadOnly)
        rasterAllBand0 = rasterAll.GetRasterBand(1).ReadAsArray()
        rasterAllBand1 = rasterAll.GetRasterBand(2).ReadAsArray()
        rasterAllBand2 = rasterAll.GetRasterBand(3).ReadAsArray()

        for i in range(rasterAll.RasterYSize):
            for j in range(rasterAll.RasterXSize):
                if rasterAllBand0[i, j] == 0 and rasterAllBand1[i, j] == 0 and rasterAllBand2[i, j] == 0:  # Aucune forêt
                    rasterAllBand0[i, j] = 0

                elif rasterAllBand0[i, j] > 50:  # Feuillus
                    rasterAllBand0[i, j] = 1

                elif rasterAllBand1[i, j] > 50:  # Conifères
                    rasterAllBand0[i, j] = 2

                elif rasterAllBand2[i, j] > 50:  # Inconnu
                    rasterAllBand0[i, j] = 0

                else:  # Mixte
                    rasterAllBand0[i, j] = 3

        rasterClass = gdal.GetDriverByName("GTiff").Create(pathClass, rasterAll.RasterXSize, rasterAll.RasterYSize, 1)
        rasterClass.GetRasterBand(1).WriteArray(rasterAllBand0)

        rasterClass.SetProjection(rasterAll.GetProjection())
        rasterClass.SetGeoTransform(rasterAll.GetGeoTransform())
        rasterClass.FlushCache()

    return pathClass
