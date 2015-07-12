#!/usr/bin/env python3

import argparse
import btrfs
import subprocess
import time


def subvolume(s):
    try:
        return btrfs.Subvolume.from_path(s)
    except subprocess.CalledProcessError:
        msg = "{} is not a subvolume".format(s)
        raise argparse.ArgumentTypeError(msg)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Snapshot and rotate btrfs subvolumes.")
    parser.add_argument("subvolume", type=subvolume,
                        help="path to a subvolume")
    parser.add_argument("destination", type=str,
                        help="destination directory")
    parser.add_argument("-r", "--retain", type=int, metavar="n",
                        help="if given, only n snapshots in " +
                        "the destination directory are retained. rest are " +
                        "deleted, starting from the oldest")
    args = parser.parse_args()
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S+0000", time.gmtime())
    name = args.subvolume.name + "-" + timestamp
    args.subvolume.snapshot(args.destination, name)
    if args.retain is not None:
        snapshots = sorted(args.subvolume.children_in(args.destination),
                           key=lambda s: s.created,
                           reverse=True)
        for snapshot in snapshots[args.retain:]:
            snapshot.delete()
