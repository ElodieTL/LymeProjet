from fonctions import *


""" Fonction permettant de faire les prétraitements pour chaque déterminant et chaque source de données. """
# dataDir: String représentant le répertoire où seront enregistrées les données.
# noDet: entier représentant le déterminant courant.
# listSourcesDet: Liste contenant les sources de données devant être traitées pour le déterminant courant.
# pixelSize: String représentant la taille d'un pixel (utilisé pour les noms de fichiers).
# ROICRSStr: String représentant le code EPSG de la donnée vectorielle de référence (EPSG:#).
# ROICRS: String représentant le code EPSG de la donnée vectorielle de référence (#).
# ROIRasterPath: String représentant le chemin du fichier raster de référence.
# ROIVectorData: Objet de type geopandas représentant le fichier vectoriel de référence.
# ROIVectorDataJson: Objet de type JSON représentant la géométrie du fichier vectoriel de référence au format JSON.
# listRasterOutPath: Liste contenant les chemins des rasters produits en sortie.
def pretraitements(dataDir, noDet, listSourcesDet, pixelSize, ROICRSStr, ROICRS, ROIRasterPath, ROIVectorData, ROIVectorDataJson):
    detStr = getDet(noDet)
    print("Début des prétraitements pour le déterminant " + detStr + "...")

    # Répertoire où les données seront enregistrées selon le déterminant courant.
    detDir = os.path.join(dataDir, detStr)

    # Extraction des liens URL menant aux données et d'autres données du fichier Excel.
    listSources = pd.read_excel("ListeSources.xlsx")
    dets = listSources.loc[listSources["Determinants"] == detStr]
    detSources = dets.loc[dets["Sources"].isin(listSourcesDet)]

    # Création d'une liste de liens URL menant aux données et d'autres données.
    urlList = [[row.Liens, row.Types, row.Champs, row.Valeurs, row.Noms] for row in detSources.itertuples()]

    # Création du répertoire où sera contenu les données selon le déterminant courant, s'il n'existe pas.
    createDir(detDir)

    listRasterOutPath = []

    # Pour chaque lien de la liste de liens.
    for url in urlList:
        # Type courant (Raster ou Vecteur).
        type = url[1]

        # Champs et valeur où récupérer les données pertinentes, si applicable.
        champs = url[2]
        valeur = url[3]

        # Nom de bases des fichiers de sortie
        nom = url[4]

        # Spécifier le nom et le chemin du fichier qui sera téléchargé.
        outPath = os.path.join(detDir, nom)
        extension = os.path.basename(url[0])[-4:]
        outPath = outPath + extension

        # Vérifier si la donnée téléchargée est compressée.
        if os.path.basename(url[0])[-4:] in [".zip", ".rar"]:
            compress = True
        else:
            compress = False

        # Si la donnée d'origine n'a pas été téléchargée ou n'existe pas, on la télécharge.
        if not os.path.exists(outPath):
            downloadData(url[0], outPath, detDir, compress)

        # Obtenir la liste de tous les fichiers.
        if type == "Raster":
            fileNames = listFiles(detDir, ".tif", ("reproject.tif", "clip.tif", "resample_" + pixelSize + ".tif", "_intermediaire.tif", "_final.tif"))

        else:
            fileNames = listFiles(detDir, ".shp", ("reproject.shp", "clip.shp", "resample_" + pixelSize + ".shp"))

        # Pour chaque lien de la liste.
        for file in fileNames:
            # Créer les liens vers les fichiers de sortie.
            if type == "Raster":
                outPath, outPathReproject, outPathClip, outPathResample = createPaths(detDir, file, pixelSize, False)

                # Extraire le code EPSG de la donnée téléchargée.
                dataCRS, dataCRSStr = extractEPSGRaster(outPath)

            else:
                outPath, outPathReproject, outPathClip, outPathRaster = createPaths(detDir, file, pixelSize, True)

                # Extraire le code EPSG de la donnée téléchargée.
                data = gpd.read_file(outPath)
                dataCRS, dataCRSStr = extractEPSGVector(data)

            # Si la projection n'est pas la même que celle de la région d'intérêt et qu'un fichier reprojeté n'existe pas.
            if dataCRS != ROICRS:
                if type == "Raster":
                    if not os.path.exists(outPathReproject):
                        reprojectRaster(outPath, outPathReproject, ROICRSStr)

                    # Si un raster découpé n'existe pas.
                    if not os.path.exists(outPathClip):
                        clipRaster(outPathReproject, outPathClip, ROIVectorDataJson, ROICRS)

                    # Si un raster rééchantillonné n'existe pas.
                    if not os.path.exists(outPathResample):
                        resampleRaster(outPathClip, ROIRasterPath, outPathResample)

                    if os.path.exists(outPathResample) and outPathResample not in listRasterOutPath:
                        listRasterOutPath.append(outPathResample)

                else:
                    if not os.path.exists(outPathReproject):
                        reprojectVector(data, outPathReproject, ROICRSStr)

                    clip = False
                    if not os.path.exists(outPathClip):
                        clip = clipVector(outPathReproject, outPathClip, ROIVectorData)

                    # Si le fichier vectoriel n'est pas rasterisé.
                    if not os.path.exists(outPathRaster) and (clip or os.path.exists(outPathClip)):
                        rasteriseVector(outPathClip, ROIRasterPath, outPathRaster, champs, valeur, noDet)

                    if os.path.exists(outPathRaster) and outPathRaster not in listRasterOutPath:
                        listRasterOutPath.append(outPathRaster)

            else:
                print("No projection detected for raster " + outPath + ". Impossible to proceed.")

    print("Fin des prétraitements pour le déterminant " + detStr + ".")

    return listRasterOutPath
