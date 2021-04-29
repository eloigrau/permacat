import os


def resizeImgesDossier(dossier):
    print(os.listdir(dossier))
    fichiers = [f for f in os.listdir(dossier) if os.path.isfile(os.path.join(dossier, f)) and (f.endswith(".jpg") or f.endswith(".png"))]
    for f in fichiers:
        cmd = "convert " + dossier+f +" -resize 800 " + dossier+os.path.splitext(f)[0] + "_resized"+os.path.splitext(f)[1]
        print(cmd)
        os.system(cmd)

dossier = "/home/tchenrezi/Téléchargements/img3/"

resizeImgesDossier(dossier)