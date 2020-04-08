liste = [1, 5, 10]
len = len(liste)

for i in range (0,len-1):
    if (i+2) == len:
        if len ==2:
            intermediaire = liste[0]
        print("dernier:" , intermediaire+ liste[i+1])
    elif i ==0 and len != 2:
        intermediaire = liste[i]+ liste[i+1]
        print("premier:" , intermediaire)

    else:
        intermediaire = intermediaire + liste[i+1]
        print(intermediaire)

print(os.path.basename("Z:\GMT3051\Donnees\Eau\canvec_250K_QC_Hydro/hydro_obstacle_2.tif"))