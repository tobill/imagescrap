import os
import dbm

import imagecopy as ic
import argparse

FILEEXT = [".jpg", ".jpeg", ".mp4", ".mov"]
FOTO_COPY_PICKLE = "./foto.pickle"
FOTO_RENAME_PICKLE = "./foto_rename.pickle"

def get_cmd_parser():
    action_choices = [
        'copy',
        'rename-ext',
        'compute-hash',
    ]
    parser = argparse.ArgumentParser(description="Imagescrap")
    parser.add_argument('--action', '-a', default='list', choices=action_choices)
    parser.add_argument('--srcpath', '-s')
    parser.add_argument('--destpath', '-d')
    parser.add_argument('--dbfile', '-f')
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
            ic.correct_name(f)
            fotos.append(f)
            if i % 100 == 0:
                print("save pickel {0}".format(FOTO_RENAME_PICKLE))
                ic.save_foto_pickle(fotos, FOTO_RENAME_PICKLE)
        if i > 10000:
            break
    print("save pickel {0}".format(FOTO_RENAME_PICKLE))
    ic.save_foto_pickle(fotos, FOTO_RENAME_PICKLE)


def compute_hash_action(args):
    if not args.dbfile:
        print("dbm file missing")
        return


if __name__ == '__main__':
    args = get_cmd_parser().parse_args()
    if args.action == 'copy':
        copy_action(args)
    if args.action == 'rename-ext':
        rename_ext_action(args)

    if args.action == 'compute-hash':
        compute_hash_action(args)