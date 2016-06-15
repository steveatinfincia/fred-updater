#!/usr/bin/env python

import sys
import os
import errno
import shutil
import platform
from distutils.dir_util import copy_tree

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

mkdir_p("updater/metadata/current")
mkdir_p("updater/metadata/previous")
if not os.path.exists("updater/metadata/current/root.json"):
    print "Error: no root.json file loaded"
    sys.exit(1)

PLATFORM = platform.system()
if PLATFORM == "Windows":
    RUN_CMD ="run.cmd"
else:
    RUN_CMD = "./run.sh"

import tuf.client.updater

# holds updater state and root public key, as well as being the temporary directory for newly fetched updates
tuf.conf.repository_directory = 'updater'

repository_mirrors = {'mirror1': {'url_prefix': 'http://localhost:8000',
                                  'metadata_path': 'metadata',
                                  'targets_path': 'targets',
                                  'confined_target_dirs': ['']}}

updater = tuf.client.updater.Updater('fred', repository_mirrors)


def initialize():
    print "Checking for updates"
    updater.refresh()

def start():
    print "Starting fred"
    os.system(RUN_CMD + " start")

def stop():
    print "Stopping fred"
    os.system(RUN_CMD + " stop")

def fetch(component):
    directory = 'updater-tmp' + "/"
    try:
        os.mkdir(directory)
    except:
        pass # likely the directory already exists
    targets = updater.targets_of_role('targets/' + component)
    updated_targets = updater.updated_targets(targets, directory)

    for target in updated_targets:
        updater.download_target(target, directory)

    updater.remove_obsolete_targets(directory)

def deploy(component):
    src = "updater-tmp" + "/" + component + "/"
    dst = "."
    copy_tree(src, dst)

if __name__ == "__main__":
    initialize()

    components = []

    if "testing" in sys.argv:
        components.append("fred-testing")
    else:
        components.append("fred")

    # unused at the moment but will pull installers as well during the update sequence
    if "installer" in sys.argv:
        components.append("installer")

    for component in components:
        print "Updating " + component
        fetch(component)

    # only stop fred once we're sure we have a full set of files to deploy all at once, minimizes downtime too
    stop()
    for component in components:
        print "Deploying " + component
        deploy(component)
    start()
