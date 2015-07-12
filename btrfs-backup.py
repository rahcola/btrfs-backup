#!/usr/bin/env python3

import argparse
import btrfs
import subprocess
import time


def find_parent(subvolume, directory):
    candidates = subvolume.children_in(directory)
    if len(candidates) > 1:
        raise RuntimeError("multiple snapshots in {}".format(directory))
    if len(candidates) == 0:
        return None
    return candidates[0]

def subvolume(s):
    try:
        return btrfs.Subvolume.from_path(s)
    except subprocess.CalledProcessError:
        msg = "{} is not a subvolume".format(s)
        raise argparse.ArgumentTypeError(msg)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Backup btrfs subvolumes.")
    parser.add_argument("subvolume", type=subvolume,
                        help="path to a subvolume")
    parser.add_argument("cachedir", type=str,
                        help="cache directory")
    args = parser.parse_args()
    subvolume = args.subvolume
    cachedir = args.cachedir
    parent = find_parent(subvolume, cachedir)
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S+0000", time.gmtime())
    name = subvolume.name + "-" + timestamp
    snapshot = subvolume.snapshot(cachedir, name)
    snapshot.send(parent=parent)
    parent.delete()
