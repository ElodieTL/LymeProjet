from generic import *

""" Fonction permettant de faire les prétraitements pour chaque déterminant et chaque source de données. """
# dir: String représentant le répertoire où seront enregistrées les données.
# det: entier représentant le déterminant courant.
# sources: Liste contenant les sources de données devant être traitées pour le déterminant courant.
# pixelSize: String représentant la taille d'un pixel (utilisé pour les noms de fichiers).
# ROICRSStr: String représentant le code EPSG de la donnée vectorielle de référence (EPSG:#).
# ROICRS: String représentant le code EPSG de la donnée vectorielle de référence (#).
# ROIPathRaster: String représentant le chemin du fichier raster de référence.
# ROIDataVector: Objet de type geopandas représentant le fichier vectoriel de référence.
# ROIDataJson: Objet de type JSON représentant la géométrie du fichier vectoriel de référence au format JSON.
def pretraitements(dir, det, sources, pixelSize, ROICRSStr, ROICRS, ROIPathRaster, ROIDataVector, ROIDataJson):
    # Codification du déterminant courant en String.
    if det == 0:
        det = "Foret"

    elif det == 1:
        det = "Zones humides"

    elif det == 2:
        det = "Eau"

    elif det == 3:
        det = "Parcs"

    elif det == 4:
        det = "Zones agricoles"

    elif det == 5:
        det = "Voies de communication"

    elif det == 6:
        det = "Zones anthropisées"

    elif det == 7:
        det = "Couverture du sol"

    # Répertoire où les données seront enregistrées selon le déterminant courant.
    detDir = dir + "\\" + det

    # Extraction des liens URL menant aux données et d'autres données du fichier Excel.
    sourcesList = pd.read_excel("ListeSources.xlsx")
    det = sourcesList.loc[sourcesList["Determinant"] == det]
    detSources = det.loc[det["Sources"].isin(sources)]

    # Création d'une liste de liens URL menant aux données et d'autres données.
    urlList = [[row.Liens, row.Types, row.Champs, row.Valeur, row.Nom] for row in detSources.itertuples()]

    # Création du répertoire où sera contenu les données selon le déterminant courant, s'il n'existe pas.
    createDir(detDir)

    # Pour chaque lien de la liste de liens.
    for url in urlList:
        # Type courant (Raster ou Vecteur).
        type = url[1]

        # Champs et valeur où récupérer les données pertinentes, si applicable.
        champs = url[2]
        valeur = url[3]

        # Nom de bases des fichiers de sortie
        nom = url[4]

        # Spécifier le chemin du fichier qui sera téléchargé.
        outPath = os.path.join(detDir, nom)
        extension = os.path.basename(url[0])[-4:]
        outPath = outPath + extension
        #outPath = os.path.join(detDir, os.path.basename(url[0]))

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
            fileNames = listFiles(detDir, ".tif", ("reproject.tif", "clip.tif", "resample_" + pixelSize + ".tif"))

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

            if dataCRS is not None:
                # Si la projection n'est pas la même que celle de la région d'intérêt et qu'un fichier reprojeté n'existe pas.
                if dataCRS != ROICRS:
                    if type == "Raster":
                        if not os.path.exists(outPathReproject):
                            reprojectRaster(outPath, outPathReproject, ROICRSStr)

                        # Si un raster découpé n'existe pas.
                        if not os.path.exists(outPathClip):
                            clipRaster(outPathReproject, outPathClip, ROIDataJson, ROICRS)

                        # Si un raster rééchantillonné n'existe pas.
                        if not os.path.exists(outPathResample):
                            resampleRaster(outPathClip, ROIPathRaster, outPathResample)

                    else:
                        if not os.path.exists(outPathReproject):
                            reprojectVector(data, outPathReproject, ROICRSStr)

                        clip = False
                        if not os.path.exists(outPathClip):
                            clip = clipVector(outPathReproject, outPathClip, ROIDataVector)

                            #if clip == False:
                                #os.remove(outPath, outPathReproject)     à tester, les supprimer pour pas les traiter à chaque fois


                        # Si le fichier vectoriel n'est pas rasterisé.
                        if not os.path.exists(outPathRaster) and (clip or os.path.exists(outPathClip)):
                            rasteriseVector(outPathClip, ROIPathRaster, outPathRaster, champs, valeur)

            else:
                print("No projection detected for raster " + outPath + ". Impossible to proceed.")
