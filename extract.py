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
argparser.add_argument('-s', type=str, help='TimeMachine path (full path to root under Backups.backupdb)')
argparser.add_argument('-d', type=str, help='Restore path (must initially not exist)')

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

def handle_path(args, path, src_path, dst_path):
    if os.path.isdir(src_path):
        handle_dir(args, path, src_path, dst_path)
    elif os.path.isfile(src_path):
        handle_file(args, path, src_path, dst_path)

def handle_dir(args, path, src_path, dst_path):
    mkdir_recursive(dst_path)
    for entry in os.listdir(src_path):
        entry_path = src_path + os.path.sep + entry
        handle_path(args, path + os.path.sep + entry, src_path + os.path.sep + entry, dst_path + os.path.sep + entry)

def sanitize_path(s):
    return s.replace("\r", "")

def handle_file(args, path, src_path, dst_path):
    # if file is zero-length, and if its link count points to a hidden 'dir_N'
    # directory at the HFS+ root, it's really a hardlinked directory and we
    # should treat it as such...
    s = os.stat(src_path)
    if s.st_size == 0:
        # four levels up: disk name, backup time, machine name,
        # 'Backups.backupdb' (in deepest-to-shallowest order) --> disk root.
        hidden_path = args.s + "/../../../../.HFS+ Private Directory Data\r" + os.path.sep + ('dir_%d' % s.st_nlink)
        if os.path.isdir(hidden_path):
            print 'Following hidden link for %s: %s' % (path, sanitize_path(hidden_path))
            handle_dir(args, path, hidden_path, dst_path)
            return

    print 'Copying %s: %s -> %s' % (path, sanitize_path(src_path), dst_path)
    shutil.copyfile(src_path, dst_path)

# root call
handle_path(args, '', args.s, args.d)
