import datetime, time
import os
import os.path
import pickle
import re
import shutil
import hashlib

import exiftool
from pathlib import Path
from shutil import copyfile

MIMETYPE_EXT =  {
    'image/jpeg': '.jpg',
    'video/mp4': '.mp4',
}

FILECHARPATTERN = re.compile('^[\w\-]+$')

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


def rename_file(fold, fnew):
    fnew = increment_file_dest(fnew)
    print("rename {0} to {1}".format(fold, fnew))
    shutil.move(fold, fnew)


def correct_name(fpath):
    exifdata = get_exif_data(fpath)
    filebase, file_ext = os.path.splitext(fpath)
    if MIMETYPE_EXT[exifdata['File:MIMEType']] != file_ext:
        fnew = "{0}{1}".format(filebase, MIMETYPE_EXT[exifdata['File:MIMEType']])
        rename_file(fpath, fnew)
        print('correct extension from {0} to {1}'.format(fpath, fnew))
        fpath = fnew
    filename = os.path.basename(fpath)
    dpath = os.path.dirname(fpath)
    filebase, file_ext = os.path.splitext(filename)
    new_filebase = re.sub('[^\w\s-]', '_', filebase).strip()
    if filebase == new_filebase:
        return
    new_filebase = re.sub('[-\s]+', '_', new_filebase).strip('_')
    fnew = "{0}{1}".format(os.path.join(dpath, new_filebase), file_ext)
    rename_file(fpath, fnew)
    print('correct extension from {0} to {1}'.format(fpath, fnew))


def get_hash_of_file(f):
    sha_hash = hashlib.sha256()
    with open(f, 'rb') as fob:
        content = fob.read()
        sha_hash.update(content)
    return sha_hash.hexdigest()