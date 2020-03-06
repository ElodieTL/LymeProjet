from generic import *

def Foret(pixelSize, ROICRSStr, ROICRS, ROIData,ROIDataJson):
    # Répertoire où les données seront enregistrées
    foretsDir = r"Z:\GALAL35\Projet_lyme\Donnees\Foret"
    #zonesHumidesDir = r"Z:\MALAM357\GMT-3051 Projet en génie géomatique II\Donnees\Foret"

    # Liste de liens menant aux données.
    urlListF = [
        "http://ftp.geogratis.gc.ca/pub/nrcan_rncan/Forests_Foret/canada-forests-attributes_attributs-forests-canada/2011-attributes_attributs-2011/NFI_MODIS250m_2011_kNN_SpeciesGroups_Broadleaf_Spp_v1.tif",
        "http://ftp.geogratis.gc.ca/pub/nrcan_rncan/Forests_Foret/canada-forests-attributes_attributs-forests-canada/2011-attributes_attributs-2011/NFI_MODIS250m_2011_kNN_SpeciesGroups_Needleleaf_Spp_v1.tif",
        "http://ftp.geogratis.gc.ca/pub/nrcan_rncan/Forests_Foret/canada-forests-attributes_attributs-forests-canada/2011-attributes_attributs-2011/NFI_MODIS250m_2011_kNN_SpeciesGroups_Unknown_Spp_v1.tif"]

    # Créer le répertoire s'il n'existe pas.
    createDir(foretsDir)

    # Créer une liste vide qui contiendra les rasters créés
    rasters = []

    # Pour chaque lien de la liste
    for url in urlListF:
        # Spécifier les liens vers les fichiers de sortie.
        outPath, outPathReproject, outPathClip, outPathResample = createPaths(foretsDir, os.path.basename(url), pixelSize)

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

    return rasters