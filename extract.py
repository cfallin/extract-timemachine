#!/usr/bin/env python
#
# This is a small utility to extract an Apple TimeMachine backup from its HFS+
# volume as seen by Linux's HFS+ driver.
#
# I found details of the TimeMachine / HFS+ driver interactions (w.r.t.
# hard-linked diretories) at http://carsonbaker.org/time-machine-on-linux .
#
# Released to public domain by Chris Fallin <cfallin@c1f.net>.

import os
import os.path
import shutil 
import argparse

argparser = argparse.ArgumentParser('extract.py')
argparser.add_argument('-s', type=str, required=True, help='TimeMachine path (full path to root under Backups.backupdb)')
argparser.add_argument('-d', type=str, required=True, help='Restore path (must initially not exist)')
argparser.add_argument('-v', type=bool, default=False, help='Verbose (print directories as we enter them)')

args = argparser.parse_args()

def mkdir_recursive(path):
    if os.path.isfile(path):
        raise BaseException('recursive mkdir: destination path is file')
    elif os.path.isdir(path):
        return
    else:
        parent = os.path.dirname(path)
        if parent != path: mkdir_recursive(parent)
        os.mkdir(path)

def handle_path(args, path, src_path, dst_path, visited_parents):
    if os.path.isdir(src_path):
        handle_dir(args, path, src_path, dst_path, visited_parents)
    elif os.path.isfile(src_path):
        handle_file(args, path, src_path, dst_path, visited_parents)

def handle_dir(args, path, src_path, dst_path, visited_parents):
    mkdir_recursive(dst_path)

    # progress updates on each new directory
    if args.v:
        print path

    # add our inode to visited path (ancestor set); skip if we are in a
    # directory-hardlink loop.
    inode = os.stat(src_path).st_ino
    if inode in visited_parents: return
    visited_parents.add(inode)

    for entry in os.listdir(src_path):
        entry_path = src_path + os.path.sep + entry
        handle_path(args, path + os.path.sep + entry, src_path + os.path.sep + entry, dst_path + os.path.sep + entry, visited_parents)

    visited_parents.remove(inode)

def sanitize_path(s):
    return s.replace("\r", "")

def handle_file(args, path, src_path, dst_path, visited_parents):
    # if file is zero-length, and if its link count points to a hidden 'dir_N'
    # directory at the HFS+ root, it's really a hardlinked directory and we
    # should treat it as such...
    s = os.stat(src_path)
    if s.st_size == 0:
        # four levels up: disk name, backup time, machine name,
        # 'Backups.backupdb' (in deepest-to-shallowest order) --> disk root.
        hidden_path = args.s + "/../../../../.HFS+ Private Directory Data\r" + os.path.sep + ('dir_%d' % s.st_nlink)
        if os.path.isdir(hidden_path):
            handle_dir(args, path, hidden_path, dst_path, visited_parents)
            return

    # Heuristic: skip the file copy if dest already exists and is
    # the same size. We don't expect to sync divergent trees, only
    # possibly resume an interrupted restore, so this should be
    # sufficient.
    try:
        dest_s = os.stat(dst_path)
        if dest_s.st_size == s.st_size: return
    except:
        pass
    shutil.copyfile(src_path, dst_path)

# root call
handle_path(args, '', args.s, args.d, set())
