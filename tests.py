from generic import *

def main():
    # Dimension d'un pixel pour un raster.
    pixelSize = 30

    # Importer et lire les données du shapelefile représentant la zone d'intérêt.
<<<<<<< HEAD
    ROIPath = "X:\ELTAL8\ProjetLYME\ROI_Projet_Genie_Maladies_Vectorielles_v2/ROI_Projet_Genie_Maladies_Vectorielles_v2.shp"
=======
    ROIPath = "Z:\GALAL35\Projet_lyme\LymeProjet\ROI\ROI_Projet_Genie_Maladies_Vectorielles_v2.shp"
>>>>>>> f57af0c1d14442edaec12f4e1175c72ead330339
    ROIData = gpd.read_file(ROIPath)

    # Transformer en format json
    ROIDataJson = geoToJson(ROIData)

    # Extraire le code EPSG (la projection) de la zone d'intérêt.
    ROICRS, ROICRSStr = extractEPSGVector(ROIData)

    # Télécharger les données de forêt de NRCan
    rasters = [] # Créer une liste vide qui contiendra les rasters téléchargés.

    # Répertoire où les données seront enregistrées.
<<<<<<< HEAD
    foretsDir = r"X:\ELTAL8\ProjetLYME\ROI_Projet_Genie_Maladies_Vectorielles_v2\Données\Forêt"
    zonesHumidesDir = r"X:\ELTAL8\ProjetLYME\ROI_Projet_Genie_Maladies_Vectorielles_v2\Données\Zones humides"
    eauDir = r"X:\ELTAL8\ProjetLYME\ROI_Projet_Genie_Maladies_Vectorielles_v2\Données\Eau"
=======

    foretsDir = r"Z:\GALAL35\Projet_lyme\Données\Forêt"
    zonesHumidesDir = r"Z:\GALAL35\Projet_lyme\Données\Zone Humide"
>>>>>>> f57af0c1d14442edaec12f4e1175c72ead330339

    # Liste de liens menant aux données.
    urlListF = [
        "http://ftp.geogratis.gc.ca/pub/nrcan_rncan/Forests_Foret/canada-forests-attributes_attributs-forests-canada/2011-attributes_attributs-2011/NFI_MODIS250m_2011_kNN_SpeciesGroups_Broadleaf_Spp_v1.tif",
        "http://ftp.geogratis.gc.ca/pub/nrcan_rncan/Forests_Foret/canada-forests-attributes_attributs-forests-canada/2011-attributes_attributs-2011/NFI_MODIS250m_2011_kNN_SpeciesGroups_Needleleaf_Spp_v1.tif",
        "http://ftp.geogratis.gc.ca/pub/nrcan_rncan/Forests_Foret/canada-forests-attributes_attributs-forests-canada/2011-attributes_attributs-2011/NFI_MODIS250m_2011_kNN_SpeciesGroups_Unknown_Spp_v1.tif"]

    urlListZH = [
        "https://www.donneesquebec.ca/recherche/fr/dataset/eafec419-d67d-449e-a157-d22230314d36/resource/c95e97fe-77cb-49f2-822d-c45067b6a190/download/mh2019shp.zip"]

    urlListEau = [
        "http://ftp.geogratis.gc.ca/pub/nrcan_rncan/vector/canvec/shp/Hydro/canvec_250K_QC_Hydro_shp.zip"]

    # Créer un répertoire s'il n'existe pas.
    if not os.path.exists(foretsDir):
        os.makedirs(foretsDir)

    if not os.path.exists(zonesHumidesDir):
        os.makedirs(zonesHumidesDir)

    if not os.path.exists(eauDir):
        os.makedirs(eauDir)

    # Pour chaque lien de la liste
    for url in urlListF:
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

    for url in urlListZH:
        # Spécifier les liens vers les fichiers de sortie.
        outPath = os.path.join(zonesHumidesDir, os.path.basename(url))

        # Si le fichier vectoriel d'origine n'existe pas.
        if not os.path.exists(outPath):
            downloadData(url, outPath, zonesHumidesDir, True)

        # Obtenir la liste de tous les fichiers shapefile des milieux humides
        fileNames = [file for file in os.listdir(zonesHumidesDir) if file.endswith('.shp') and not file.endswith('reproject.shp') and not file.endswith('clip.shp') and not file.endswith('resample' + str(pixelSize) + '.shp')]

        for file in fileNames:
            outPath = os.path.join(zonesHumidesDir, file)
            outPathReproject = outPath.replace(".", "_reproject.")
            outPathClip = outPath.replace(".", "_clip.")
            outPathResample = outPath.replace(".shp", "_resample_" + str(pixelSize) + ".tiff")

            # Extraire le code EPSG de la donnée téléchargée.
            data = gpd.read_file(outPath)
            dataCRS, dataCRSStr = extractEPSGVector(data)

            # Si la projection n'est pas la même que celle de la région d'intérêt et qu'un shp reprojeté n'existe pas.
            if dataCRS != ROICRS and not os.path.exists(outPathReproject):
                reprojectShp(data, outPathReproject, ROICRSStr)

            # Si un shp découpé n'existe pas.
            if not os.path.exists(outPathClip):
                clipShp(outPathReproject, outPathClip, ROIData)

            # Si le shp n'est pas rasterisé
            if not os.path.exists(outPathResample):
                rasterizingShp(outPathClip,outPathResample,pixelSize, ROICRS)

            """ 
            # Si un raster rééchantillonné n'existe pas.
            if not os.path.exists(outPathResample):
                # Extraire les dimensions d'un pixel.
                width, height = getPixelSize(outPathClip)

                # Si le pixel est carré.
                if width == height:
                    resampleRaster(outPathClip, outPathResample, width, pixelSize)

            # Ajouter la donnée à la liste.
            rasters.append(outPathResample)"""

        for url in urlListEau:
            # Spécifier les liens vers les fichiers de sortie.
            outPath = os.path.join(eauDir, os.path.basename(url))

            # Si le fichier vectoriel d'origine n'existe pas.
            if not os.path.exists(outPath):
                downloadData(url, outPath, eauDir, True)

            # Obtenir la liste de tous les fichiers shapefile des milieux humides
            fileNames = [file for file in os.listdir(eauDir) if file.endswith('.shp') and not file.endswith('reproject.shp') and not file.endswith('clip.shp') and not file.endswith('resample' + str(pixelSize) + '.shp')]

            for file in fileNames:
                outPath = os.path.join(eauDir, file)
                outPathReproject = outPath.replace(".", "_reproject.")
                outPathClip = outPath.replace(".", "_clip.")
                outPathResample = outPath.replace(".", "_resample_" + str(pixelSize) + ".")

                # Extraire le code EPSG de la donnée téléchargée.
                data = gpd.read_file(outPath)
                dataCRS, dataCRSStr = extractEPSGVector(data)

                # Si la projection n'est pas la même que celle de la région d'intérêt et qu'un shp reprojeté n'existe pas.
                if dataCRS != ROICRS and not os.path.exists(outPathReproject):
                    reprojectShp(data, outPathReproject, ROICRSStr)

                # Si un shp découpé n'existe pas.
                if not os.path.exists(outPathClip):
                    clipShp(outPathReproject, outPathClip, ROIData)

if __name__ == "__main__":
    main()