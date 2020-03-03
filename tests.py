from generic import *

def main():
    # Dimension d'un pixel pour un raster.
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
