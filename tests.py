import os
import re
import osr
import urllib
import geopandas as gpd
import rasterio as rio
from rasterio.merge import merge
from rasterio.plot import show
from rasterio.warp import calculate_default_transform, reproject, Resampling
import gdal
import matplotlib.pyplot as plt

# Fonction permettant d'extraire le code EPSG (la projection) de données vectorielles.
# data: objet geopandas représentant la donnée vectorielle.
# dataCRS: entier représentant le code EPSG de la projection utilisée.
# dataCRSStr: String représentant le code EPSG de la projection utilisée (EPSG:#).
def extractEPSGVector(data):
    # Extraire le code EPSG (la projection) de la zone d'intérêt.
    dataCRS = re.search('epsg:(.*)', data.crs["init"])

    # Si une projection existe, extraire le code et un String pour d'autres fonctions.
    if dataCRS:
        dataCRS = dataCRS.group(1)
        dataCRSStr = "EPSG:" + dataCRS

        return dataCRS, dataCRSStr

    return None, None

# Fonction permettant d'extraire le code EPSG (la projection) de données de type raster.
# inPath: String représentant le chemin vers le fichier raster entrant.
# rasterCRS: entier représentant le code EPSG de la projection utilisée.
# rasterCRSStr: String représentant le code EPSG de la projection utilisée (EPSG:#).
def extractEPSGRaster(inPath):
    raster = gdal.Open(inPath)
    rasterCRS = osr.SpatialReference(wkt = raster.GetProjection()).GetAttrValue('AUTHORITY', 1)
    rasterCRSStr = "EPSG:" + rasterCRS

    return rasterCRS, rasterCRSStr

# Fonction permettant de créer une liste de fichiers de type raster.
# inDir: String représentant le répertoire où sont stockées les fichiers.
# extension: String représentant un pattern que doit respecter le nom du fichier.
# rasterFiles: List contenant les fichiers de type raster.
def listRasterFiles(inDir, extension):
    rasterFiles = []
    for root, dirs, files in os.walk(inDir):
        for file in files:
            if file.endswith(extension):
                rasterFiles.append(os.path.join(root, file))

    return rasterFiles

# Fonction permettant de télécharger des données provenant d'un serveur ou d'un site web.
# url: String représentant l'adresse URL complète de la donnée à télécharger.
# outPath: String représentant le chemin vers le fichier sortant.
def downloadData(url, outPath):
    fileName = os.path.basename(url)
    print("Downloading " + fileName + "...")

    urllib.request.urlretrieve(url, outPath)

# Fonction permettant de reprojeter un fichier de type raster.
# inPath: String représentant le chemin vers le fichier raster entrant.
# outPath: String représentant le chemin vers le fichier raster sortant.
# dstCrs: String représentant le code EPSG de la projection voulue (EPSG:#)
def reprojectRaster(inPath, outPath, dstCRS):
    dst_crs = dstCRS
    fileName = os.path.basename(inPath)
    print("Reprojecting raster " + fileName + "...")

    with rio.open(inPath) as src:
        transform, width, height = calculate_default_transform(src.crs, dst_crs, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({'crs': dst_crs, 'transform': transform, 'width': width, 'height': height})

        with rio.open(outPath, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(source = rio.band(src, i), destination = rio.band(dst, i), src_transform = src.transform, src_crs = src.crs, dst_transform = transform, dst_crs = dst_crs, resampling = Resampling.nearest)

# Fonction permettant d'ouvrir un raster et de l'ajouter à une liste de rasters ouverts.
# inpath: String représentant le chemin vers le fichier raster entrant.
# rasters: List de rasters ouverts.
def addRastertoRasters(inPath, rasters):
    raster = rio.open(inPath)
    rasters.append(raster)

def main():
    # Importer et lire les données du shapelefile représentant la zone d'intérêt.
    ROIPath = "Z:/MALAM357/GMT-3051 Projet en génie géomatique II/Données/ROI/ROI_Projet_Genie_Maladies_Vectorielles_v2.shp"
    ROIData = gpd.read_file(ROIPath)

    # Extraire le code EPSG (la projection) de la zone d'intérêt.
    ROICRS, ROICRSStr = extractEPSGVector(ROIData)

    # Télécharger les données de forêt de NRCan
    rasters = [] # Créer une liste vide qui contiendra les rasters téléchargés.

    # Répertoire où les données seront enregistrées.
    foretsDir = r"Z:\MALAM357\GMT-3051 Projet en génie géomatique II\Données\Forêt"

    # Liste de liens menant aux données.
    urlList = [
        "http://ftp.geogratis.gc.ca/pub/nrcan_rncan/Forests_Foret/canada-forests-attributes_attributs-forests-canada/2011-attributes_attributs-2011/NFI_MODIS250m_2011_kNN_SpeciesGroups_Broadleaf_Spp_v1.tif",
        "http://ftp.geogratis.gc.ca/pub/nrcan_rncan/Forests_Foret/canada-forests-attributes_attributs-forests-canada/2011-attributes_attributs-2011/NFI_MODIS250m_2011_kNN_SpeciesGroups_Needleleaf_Spp_v1.tif",
        "http://ftp.geogratis.gc.ca/pub/nrcan_rncan/Forests_Foret/canada-forests-attributes_attributs-forests-canada/2011-attributes_attributs-2011/NFI_MODIS250m_2011_kNN_SpeciesGroups_Unknown_Spp_v1.tif"]

    # Créer un répertoire s'il n'existe pas.
    if not os.path.exists(foretsDir):
        os.makedirs(foretsDir)

    # Pour chaque lien de la liste
    for url in urlList:
        outPath = os.path.join(foretsDir, os.path.basename(url))

        if not os.path.exists(outPath):
            downloadData(url, outPath)

            rasterCRS, rasterCRSStr = extractEPSGRaster(outPath)

            if rasterCRS != ROICRS:
                reprojectRaster(outPath, outPath.replace(".", "_reproject."), ROICRSStr)
                addRastertoRasters(outPath.replace(".", "_reproject."), rasters)

            else:
                addRastertoRasters(outPath, rasters)

        else:
            rasterCRS, rasterCRSStr = extractEPSGRaster(outPath)

            if rasterCRS != ROICRS:
                reprojectRaster(outPath, outPath.replace(".", "_reproject."), ROICRSStr)
                addRastertoRasters(outPath.replace(".", "_reproject."), rasters)

            else:
                addRastertoRasters(outPath, rasters)

if __name__ == "__main__":
    main()
