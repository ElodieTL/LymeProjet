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

# Fonction permettant d'extraire le code EPSG (la projection) d'une donnée vectorielle.
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
# extension: String ou tuple représentant le(s) extension(s) à rechercher.
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
# dstCrs: String représentant le code EPSG de la projection voulue (EPSG:#).
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
# inPath: String représentant le chemin vers le fichier raster entrant.
# rasters: List de rasters ouverts.
def addRastertoRasters(inPath, rasters):
    raster = rio.open(inPath)
    rasters.append(raster)

# Fonction permettant de transformer une géométrie d'une geodataframe en format json.
# gdf: objet de type geodataframe contenant un champ 'geometry'.
def geoToJson(gdf):
    return[json.loads(gdf.to_json())['features'][0]['geometry']]

# Fonction permettant de découper un raster selon une région d'intérêt.
# inRaster: String représentant le chemin vers le fichier raster entrant.
# clipPoly: objet de type json représentant le polygone servant au découpage.
def clipRaster(inPath, outPath, clipPoly, epsgPoly):
    fileName = os.path.basename(inPath)
    print("Clipping raster " + fileName + "...")

    raster = rio.open(inPath)
    outRaster, outTransform = mask(dataset = raster, shapes = clipPoly, crop = True)
    outMeta = raster.meta.copy()

    outMeta.update({"driver": "GTiff", "height": outRaster.shape[1], "width": outRaster.shape[2], "transform": outTransform, "crs": pycrs.parse.from_epsg_code(epsgPoly).to_proj4()})

    with rio.open(outPath, "w", **outMeta) as dest:
        dest.write(outRaster)

# Fonction permettant d'extraire la hauteur et la largeur d'un pixel pour un raster.
# inPath: String représentant le chemin vers le fichier raster entrant.
# width: largeur d'un pixel.
# height: hauteur d'un pixel.
def getPixelSize(inPath):
    raster = rio.open(inPath)
    width = raster.transform[0]
    height = -(raster.transform[4])

    return width, height

#
def resampleRaster(inPath, outPath, width, pixelSize):
    fileName = os.path.basename(inPath)
    print("Resampling raster " + fileName + "...")

    factor = width / pixelSize

    raster = rio.open(inPath)
    meta = raster.meta.copy()

    data = raster.read(out_shape = (raster.count, int(raster.width * factor), int(raster.height * factor)), resampling = Resampling.bilinear)
    transform = raster.transform * raster.transform.scale((raster.width / data.shape[-2]), (raster.height / data.shape[-1]))
    meta.update({"driver": "GTiff", "height": int(raster.height * factor), "width": int(raster.width * factor), "transform": transform})

    with rio.open(outPath, 'w', **meta) as dst:
        dst.write(data)

def main():
    # Dimension d'un pixel.
    pixelSize = 30

    # Importer et lire les données du shapelefile représentant la zone d'intérêt.
    ROIPath = "Z:/MALAM357/GMT-3051 Projet en génie géomatique II/LymeProjet/ROI/ROI_Projet_Genie_Maladies_Vectorielles_v2.shp"
    ROIData = gpd.read_file(ROIPath)

    # Transformer en format json
    ROIDataJson = geoToJson(ROIData)

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
        # Spécifier les liens vers les fichiers de sortie.
        outPath = os.path.join(foretsDir, os.path.basename(url))
        outPathReproject = outPath.replace(".", "_reproject.")
        outPathClip = outPath.replace(".", "_clip.")
        outPathResample = outPath.replace(".", "_resample_" + str(pixelSize) + ".")

        # Si le fichier raster d'origine n'existe pas.
        if not os.path.exists(outPath):
            downloadData(url, outPath)

        # Extraire le code EPSG de la donnée téléchargée.
        rasterCRS, rasterCRSStr = extractEPSGRaster(outPath)

        # Si la projection n'est pas la même que celle de la région d'intérêt et qu'un raster reprojeté n'existe pas.
        if rasterCRS != ROICRS and not os.path.exists(outPathReproject):
            reprojectRaster(outPath, outPathReproject, ROICRSStr)

        # Si un raster découpé n'existe pas.
        if not os.path.exists(outPathClip):
            clipRaster(outPathReproject, outPathClip, ROIDataJson, ROICRS)

        # Si un raster rééchantillonné n'existe pas.
        if not os.path.exists(outPathResample):
            # Extraire les dimensions d'un pixel.
            width, height = getPixelSize(outPathClip)

            # Si le pixel est carré.
            if width == height:
                resampleRaster(outPathClip, outPathResample, width, pixelSize)

        # Ajouter la donnée à la liste.
        rasters.append(outPathResample)

if __name__ == "__main__":
    main()
