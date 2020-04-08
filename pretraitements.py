from generic import *

""" Fonction permettant de faire les prétraitements pour chaque déterminant et chaque source de données. """
# dir: String représentant le répertoire où seront enregistrées les données.
# no_det: entier représentant le déterminant courant.
# sources: Liste contenant les sources de données devant être traitées pour le déterminant courant.
# pixelSize: String représentant la taille d'un pixel (utilisé pour les noms de fichiers).
# ROICRSStr: String représentant le code EPSG de la donnée vectorielle de référence (EPSG:#).
# ROICRS: String représentant le code EPSG de la donnée vectorielle de référence (#).
# ROIPathRaster: String représentant le chemin du fichier raster de référence.
# ROIDataVector: Objet de type geopandas représentant le fichier vectoriel de référence.
# ROIDataJson: Objet de type JSON représentant la géométrie du fichier vectoriel de référence au format JSON.
# listePath: Liste contenant le chemin de sortie le raster finale du déterminant
def pretraitements(dir, no_det, sources, pixelSize, ROICRSStr, ROICRS, ROIPathRaster, ROIDataVector, ROIDataJson):
    # Codification du déterminant courant en String.
    checkF = False
    if no_det == 0:
        det = "Foret"
        checkF = True
    elif no_det == 1:
        det = "Zones humides"

    elif no_det == 2:
        det = "Eau"

    elif no_det == 3:
        det = "Parcs"

    elif no_det == 4:
        det = "Zones agricoles"

    elif no_det == 5:
        det = "Voies de communication"

    elif no_det == 6:
        det = "Zones anthropisees"

    elif no_det == 7:
        det = "Couverture du sol"

    # Répertoire où les données seront enregistrées selon le déterminant courant.
    detDir = dir + "\\" + det

    # Extraction des liens URL menant aux données et d'autres données du fichier Excel.
    sourcesList = pd.read_excel("ListeSources.xlsx")
    determ = sourcesList.loc[sourcesList["Determinant"] == det]
    detSources = determ.loc[determ["Sources"].isin(sources)]

    # Création d'une liste de liens URL menant aux données et d'autres données.
    urlList = [[row.Liens, row.Types, row.Champs, row.Valeur, row.Nom] for row in detSources.itertuples()]

    # Création du répertoire où sera contenu les données selon le déterminant courant, s'il n'existe pas.
    createDir(detDir)

    listeForet = []
    listePath = []
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
            fileNames = listFiles(detDir, ".tif", ("reproject.tif", "clip.tif", "resample_" + pixelSize + ".tif", "_intermediaire.tif","_final.tif"))

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
                        clipRaster(outPathReproject, outPathClip, ROIDataJson, ROICRS)

                    # Si un raster rééchantillonné n'existe pas.
                    if not os.path.exists(outPathResample):
                        resampleRaster(outPathClip, ROIPathRaster, outPathResample)

                    if "Foret" in outPathResample:
                        listeForet.append(outPathResample)
                    else:
                        listePath.append(outPathResample)
                        print("CALISSS WHY ")
                else:
                    if not os.path.exists(outPathReproject):
                        reprojectVector(data, outPathReproject, ROICRSStr)

                    clip = False
                    if not os.path.exists(outPathClip):
                        clip = clipVector(outPathReproject, outPathClip, ROIDataVector)

                    # Si le fichier vectoriel n'est pas rasterisé.
                    if not os.path.exists(outPathRaster) and (clip or os.path.exists(outPathClip)):
                        rasteriseVector(outPathClip, ROIPathRaster, outPathRaster, champs, valeur)
                    listePath.append( outPathRaster )

            else:
                print("No projection detected for raster " + outPath + ". Impossible to proceed.")
        # Ici c'est quoi?
        if checkF:
            outPathForet = foret(listeForet[0], listeForet[1], listeForet[2], dir)
            listePath.append(outPathForet)
            checkF = False

    # Si la listePath possède plus d'un raster, il faut les fusionner ensemble
    nb_raster = len(listePath)
    raster_intermediaire = os.path.join(detDir, det + "_intermediaire.tif")
    raster_final = os.path.join(detDir, det + "_final.tif")

    if nb_raster > 1:  # si plus de 1 raster
        print("Fusion intra du déterminant:", det)
        for i in range(0,(nb_raster - 1)):
            if (i+2) == nb_raster: # si seulement 2 rasters à fusionner ou générer le raster final (combinaison de tous)
                if nb_raster == 2:
                    raster_intermediaire = listePath[0]
                print("Fusion final. Création du raster:", os.path.basename(raster_final))
                rasterClassification(raster_intermediaire, listePath[i+1], raster_final)

            elif i == 0 and nb_raster != 2: # début de la fusion, raster 0 avec raster 1
                rasterClassification(listePath[i], listePath[i + 1], raster_intermediaire)

            else: # fusion des rasters précédents avec prochain raster de la liste
                rasterClassification(raster_intermediaire,listePath[i + 1],raster_intermediaire )

        return [raster_final]

    else:
        return listePath