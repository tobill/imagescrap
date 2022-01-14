import os

import imagecopy as ic
import argparse

FILEEXT = [".jpg", ".jpeg", ".mp4", ".mov"]
FOTO_COPY_PICKLE = "./foto.pickle"
FOTO_RENAME_PICKLE = "./foto_rename.pickle"
MIMETYPE_EXT =  {
    'image/jpeg': '.jpg',
    'video/mp4': '.mp4',
}

def get_cmd_parser():
    action_choices = [
        'copy',
        'rename-ext',
    ]
    parser = argparse.ArgumentParser(description="Imagescrap")
    parser.add_argument('--action', '-a', default='list', choices=action_choices)
    parser.add_argument('--srcpath', '-s')
    parser.add_argument('--destpath', '-d')
    return parser

def copy_action(args):
    fotos = ic.load_foto_pickle(FOTO_COPY_PICKLE)
    i = 0
    for f in ic.find_files(args.srcpath, FILEEXT):
        if not f in fotos:
            i = i +1
            ic.copy_foto(f, args.destpath)
            fotos.append(f)
            if i % 10 == 0:
                print("save pickel {0}".format(FOTO_COPY_PICKLE))
                ic.save_foto_pickle(fotos, FOTO_COPY_PICKLE)
        if i > 1000:
            break
    print("save pickel {0}".format(FOTO_COPY_PICKLE))
    ic.save_foto_pickle(fotos, FOTO_COPY_PICKLE)


def rename_ext_action(args):
    fotos = ic.load_foto_pickle(FOTO_RENAME_PICKLE)
    i = 0
    for f in ic.find_files(args.srcpath, FILEEXT):
        if not f in fotos:
            i = i + 1
            exifdata = ic.get_exif_data(f)
            filebase, file_ext = os.path.splitext(f)
            if MIMETYPE_EXT[exifdata['File:MIMEType']] != file_ext:
                fnew = "{0}{1}".format(filebase, MIMETYPE_EXT[exifdata['File:MIMEType']])
                ic.rename_extension(f, fnew)
            if i % 100 == 0:
                print("save pickel {0}".format(FOTO_COPY_PICKLE))
                ic.save_foto_pickle(fotos, FOTO_COPY_PICKLE)
        if i > 10000:
            break
    print("save pickel {0}".format(FOTO_COPY_PICKLE))
    ic.save_foto_pickle(fotos, FOTO_COPY_PICKLE)

if __name__ == '__main__':
    args = get_cmd_parser().parse_args()
    if args.action == 'copy':
        copy_action(args)
    if args.action == 'rename-ext':
        rename_ext_action(args)