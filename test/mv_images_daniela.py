import os
import shutil
from glob import glob

class dossier():
    def __init__(self, dossier):
        self.dossier = dossier

def mvImg():
    rep = "/home/eloi/Images/*"
    for i, f in enumerate(glob(rep)):
        if i >10 :
            break
        if os.path.isfile(f):
            print ("fichier",)
            info = os.stat(f)
            print(f, info)
        else:
            print ("dossier",  f)
            for file2 in glob(f):
                info2 = os.stat(file2)
                print(2, file2, info2)


mvImg()
#shutil.move("path/to/current/file.foo", "path/to/new/destination/for/file.foo")