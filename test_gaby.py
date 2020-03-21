from generic import *

rasterRef = gdal.Open("Z:\GALAL35\Projet_lyme\Donnees\ROI_Projet_Genie_Maladies_Vectorielles_v2_30.tif", gdal.GA_ReadOnly)

vectorData = ogr.Open(r"C:\Users\Administrateur\Downloads\zonage\zonage/zonage_p.shp")
vectorLayer = vectorData.GetLayer()

out = gdal.GetDriverByName("GTiff").Create(r"C:\Users\Administrateur\Downloads\zonage/petite_selection_3.tif", rasterRef.RasterXSize, rasterRef.RasterYSize, 1, gdal.GDT_Byte,
                                           options=["COMPRESS=DEFLATE"])
out.SetProjection(rasterRef.GetProjectionRef())
out.SetGeoTransform(rasterRef.GetGeoTransform())

#OPTIONS = ['ATTRIBUTE=DEFINITION']
#band = out.GetRasterBand(1)
#band.SetNoDataValue(0)
champs = "DEFINITION"
valeur = "Zone agricole"
string = champs + "='" + valeur + "'"
vectorLayer.SetAttributeFilter(string)
gdal.RasterizeLayer(out, [1], vectorLayer, burn_values=[1])
