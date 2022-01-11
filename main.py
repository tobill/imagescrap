import datetime, time
import os
import os.path
import pickle
from exif import Image
from pathlib import Path
from shutil import copyfile


SRC_ROOT="/mnt/raspishare/takeout/Takeout/Google Fotos"
DEST_ROOT="/mnt/raspishare/bilder"
FILEEXT = [".jpg", ".jpeg"]
FOTOPICKLE = "./foto.pickle"


def load_foto_pickle(pickle_file):
    if not os.path.exists(pickle_file):
        return []
    else:
        return pickle.load(open(pickle_file, "rb"))

def save_foto_pickle(fotos, pickle_file):
    pickle.dump(fotos, open(pickle_file, "wb"))

def get_exif_data(file_path):
    with open(file_path, 'rb') as image_file:
        exifdata = Image(image_file)
        return exifdata

def get_folder_name(datestring, dest):
    if not datestring:
        path = os.path.join(dest, "no_exif_data")
    else:
        dt = datetime.datetime.strptime(datestring, "%Y:%m:%d %H:%M:%S")
        path = os.path.join(dest, str(dt.year), str(dt.month))
    Path(path).mkdir(parents=True, exist_ok=True)
    return path

def increment_file_dest(file_dest):
    if not os.path.exists(file_dest):
        return file_dest
    i = 0
    filename, file_extension = os.path.splitext(file_dest)
    while True:
        i += 1
        file_dest = "{0}_{1}{2}".format(filename, i, file_extension)
        if not os.path.exists(file_dest):
            return file_dest


def copy_foto(file_path, dest):
    exif_data = get_exif_data(file_path)
    dt = exif_data.get("datetime_original", "") if "datetime_original" in exif_data.list_all() else None
    folder_name = get_folder_name(dt, dest)
    file_name = os.path.basename(file_path)
    file_dest = os.path.join(folder_name, file_name)
    file_dest = increment_file_dest(file_dest)
    copyfile(file_path, file_dest)


def find_files(path, filter=[]):
    for (dirpath, dirnames, filenames) in os.walk(path):
        print("in directory: {0}".format(dirpath))
        for filename in filenames:
            if os.path.splitext(filename)[1] in filter:
                yield os.path.join(dirpath, filename)

if __name__ == '__main__':
    fotos = load_foto_pickle(FOTOPICKLE)
    i = 0
    for f in find_files(SRC_ROOT, FILEEXT):
        if not f in fotos:
            i += 1
            copy_foto(f, DEST_ROOT)
            fotos.append(f)

        if i > 10:
            break
        #copyfile(f)
    save_foto_pickle(fotos, FOTOPICKLE)
