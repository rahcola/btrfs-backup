#!/usr/bin/env python3

import argparse
from glob import glob
import os.path
import re
import subprocess
import time

def subvolume(s):
    try:
        out = subprocess.check_output(["btrfs", "subvolume", "show", s],
                                      stderr=subprocess.DEVNULL,
                                      universal_newlines=True)
        volume_name = re.search("Name:\s+([^\n]+)", out).group(1)
        return {"path": os.path.abspath(s), "name": volume_name}
    except subprocess.CalledProcessError:
        msg = "{} is not a subvolume".format(s)
        raise argparse.ArgumentTypeError(msg)

def dir_path(s):
    if os.path.isdir(s):
        return os.path.abspath(s)
    else:
        msg = "{} is not a directory".format(s)
        raise argparse.ArgumentTypeError(msg)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Snapshot and rotate btrfs subvolumes.")
    parser.add_argument("subvolume", type=subvolume,
                        help="path to a subvolume")
    parser.add_argument("destination", type=dir_path,
                        help="destination directory")
    parser.add_argument("-r", "--retain", type=int, metavar="n",
                        help="if given, only n snapshots in " +
                        "the destination directory are retained. rest are " +
                        "deleted, starting from the oldest")
    args = parser.parse_args()

    volume_name = args.subvolume["name"]
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S+0000", time.gmtime())
    snapshot_name = volume_name + "-" + timestamp
    subprocess.check_call(["btrfs", "subvolume", "snapshot", "-r",
                           args.subvolume["path"],
                           os.path.join(args.destination, snapshot_name)])
    if args.retain is not None:
        snapshots = glob(os.path.join(args.destination, volume_name + "-*"))
        for snapshot in sorted(snapshots, reverse=True)[args.retain:]:
            subprocess.check_call(["btrfs", "subvolume", "delete", snapshot])
