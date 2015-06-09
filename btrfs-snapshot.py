#!/usr/bin/env python3

import argparse
import glob
import os.path
import re
import subprocess
import time

class Subvolume(object):
    def __init__(self, path, name, uuid, parent, created):
        self.path = path
        self.name = name
        self.uuid = uuid
        self.parent = parent
        self.created = created

    def snapshot(self, destination, name):
        if os.path.isabs(destination):
            snapshot = os.path.join(destination, name)
        else:
            snapshot = os.path.join(self.path, destination, name)
        subprocess.check_call(["btrfs", "subvolume", "snapshot", "-r",
                               self.path, snapshot])

    def delete(self):
        subprocess.check_call(["btrfs", "subvolume", "delete", self.path])

    def children_in(self, path):
        if not os.path.isabs(path):
            path = os.path.join(self.path, path)
        children = []
        for p in glob.glob(os.path.join(path, "*")):
            try:
                child = Subvolume.from_path(p)
                if child.parent == self.uuid:
                    children.append(child)
            except subprocess.CalledProcessError:
                pass
        return children

    @classmethod
    def from_path(cls, path):
        out = subprocess.check_output(["btrfs", "subvolume", "show", path],
                                      stderr=subprocess.DEVNULL,
                                      universal_newlines=True)
        name = re.search("Name:\s+([^\n]+)", out).group(1)
        uuid = re.search("uuid:\s+([^\n]+)", out).group(1)
        parent = re.search("Parent uuid:\s+([^\n]+)", out).group(1)
        if parent == "-":
            parent = None
        created = time.strptime(
            re.search("Creation time:\s+([^\n]+)", out).group(1),
            "%Y-%m-%d %H:%M:%S")
        return cls(path, name, uuid, parent, created)


def subvolume(s):
    try:
        return Subvolume.from_path(s)
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
