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
        return Subvolume.from_path(os.path.join(self.path, snapshot))

    def delete(self):
        subprocess.check_call(["btrfs", "subvolume", "delete", self.path])

    def send(self, parent=None, out=None):
        cmd = ["btrfs", "send"]
        if parent is not None:
            cmd.extend(["-p", parent.path])
        if out is not None:
            if not os.path.isabs(out):
                out = os.path.join(self.path, out)
            cmd.extend(["-f", out])
        cmd.append(self.path)
        subprocess.check_call(cmd)
        return out

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
        uuid = re.search("UUID:\s+([^\n]+)", out).group(1)
        parent = re.search("Parent UUID:\s+([^\n]+)", out).group(1)
        if parent == "-":
            parent = None
        created = time.strptime(
            re.search("Creation time:\s+([^\n]+)", out).group(1),
            "%Y-%m-%d %H:%M:%S %z")
        return cls(path, name, uuid, parent, created)


def find_parent(subvolume, directory):
    candidates = subvolume.children_in(directory)
    if len(candidates) > 1:
        raise RuntimeError("multiple snapshots in {}".format(directory))
    if len(candidates) == 0:
        return None
    return candidates[0]

def subvolume(s):
    try:
        return Subvolume.from_path(s)
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
