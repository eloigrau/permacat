import os
import shutil
from glob import glob

def mvImg():
    rep = "/home/eloi/Images/*"
    for file in glob(rep):
        if os.path.isfile(file):
            print ("fichier", file)
            info = os.stat(file)
            print(file, info)
        else:
            print ("dossier",  file)
            for file2 in glob(file):
                info2 = os.stat(file)
                print(2, file2, info2)


mvImg()
#shutil.move("path/to/current/file.foo", "path/to/new/destination/for/file.foo")