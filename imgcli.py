import json
import os
import dbm
import pathlib

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
        'remove-duplicate',
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
    dbreversname = args.dbfile + '_r'
    dbname =  args.dbfile
    i = 0
    with dbm.open(dbname, 'c') as db:
        with dbm.open(dbreversname, 'c') as dbr:
            for f in ic.find_files(args.srcpath, FILEEXT):
                if not f in dbr:
                    i = i + 1
                    hash = ic.get_hash_of_file(f)
                    dbr[f] = hash
                    print('Hash: {0}'.format(hash))
                    if hash in db:
                        v = json.loads(db[hash])
                        if f not in v:
                            v.append(f)
                        db[hash] = json.dumps(v)
                        print('already there, updateing: {0}'.format(v))
                    else:
                        print('new file adding to db {0}'.format(f))
                        db[hash] = json.dumps([f])
                if i > 100000:
                    break

def delete_duplicate_action(args):
    if not args.dbfile:
        print("dbm file missing")
        return
    i = 0
    dbname =  args.dbfile
    with dbm.open(dbname, 'c') as db:
        for k in db.keys():
            file_list = json.loads(db[k])
            smallest = (0, 1000)
            for i in range(len(file_list)):
                if len(file_list[i]) < smallest[1]:
                    smallest = (i, len(file_list[i]))
            filename = file_list[smallest[0]]
            del(file_list[smallest[0]])
            for f in file_list:
                print("deleting file: {0}".format(f))
                p = pathlib.Path(f)
                p.unlink(missing_ok=True)
            db[k] = json.dumps([filename])

if __name__ == '__main__':
    args = get_cmd_parser().parse_args()
    if args.action == 'copy':
        copy_action(args)
    if args.action == 'rename-ext':
        rename_ext_action(args)

    if args.action == 'compute-hash':
        compute_hash_action(args)
    if args.action == 'remove-duplicate':
        delete_duplicate_action(args)