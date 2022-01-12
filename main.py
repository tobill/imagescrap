import datetime, time
import os
import os.path
import pickle
import re

import exiftool
from pathlib import Path
from shutil import copyfile
import argparse

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
    with exiftool.ExifTool() as et:
        exifdata = et.get_metadata(file_path)
        return exifdata

def get_folder_name(dt, dest):
    if not dt:
        path = os.path.join(dest, "no_exif_data")
    else:
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


def determine_date_by_filename(file_path):
    pattern = re.compile(r"IMG-(\d{8})-(WA\d+).jpg")
    m = pattern.search(file_path)
    if m is not None:
        return datetime.datetime.strptime(m.group(1), "%Y%m%d")
    return None

def copy_foto(file_path, dest):
    exif_data = get_exif_data(file_path)
    print(exif_data)
    if "EXIF:DateTimeOriginal" in exif_data:
        dt = exif_data["EXIF:DateTimeOriginal"]
        dt = datetime.datetime.strptime(dt, "%Y:%m:%d %H:%M:%S")
    elif "QuickTime:MediaCreateDate" in exif_data:
        dt = exif_data["QuickTime:MediaCreateDate"]
        dt = datetime.datetime.strptime(dt, "%Y:%m:%d %H:%M:%S")
    else:
        dt = determine_date_by_filename(file_path)
    folder_name = get_folder_name(dt, dest)
    file_name = os.path.basename(file_path)
    file_dest = os.path.join(folder_name, file_name)
    file_dest = increment_file_dest(file_dest)
    print("copy {0} to {1}".format(file_name, file_dest))
    copyfile(file_path, file_dest)


def find_files(path, filter=[]):
    for (dirpath, dirnames, filenames) in os.walk(path):
        print("in directory: {0}".format(dirpath))
        for filename in filenames:
            if os.path.splitext(filename)[1] in filter:
                yield os.path.join(dirpath, filename)

def get_cmd_parser():
    action_choices = [
        'list',
    ]
    parser = argparse.ArgumentParser(description="Imagescrap")
    parser.add_argument('--srcpath', '-s')
    parser.add_argument('--destpath', '-d')
    return parser

if __name__ == '__main__':
    fotos = load_foto_pickle(FOTOPICKLE)
    args = get_cmd_parser().parse_args()
    i = 0
    for f in find_files(args.srcpath, FILEEXT):
        if not f in fotos:
            i = i +1 if copy_foto(f, args.destpath) else i
            fotos.append(f)
            if i % 10 == 0:
                print("save pickel {0}".format(FOTOPICKLE))
                save_foto_pickle(fotos, FOTOPICKLE)
        if i > 1000:
            break
        #copyfile(f)
    print("save pickel {0}".format(FOTOPICKLE))
    save_foto_pickle(fotos, FOTOPICKLE)
