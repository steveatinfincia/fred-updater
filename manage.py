#!/usr/bin/env python

import sys
import os.path
import errno
from datetime import date

from distutils.dir_util import copy_tree

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

# https://stackoverflow.com/questions/15741618/add-one-year-in-current-date-python/15743908#15743908
def add_years(d, years):
    """Return a date that's `years` years after the date (or datetime)
    object `d`. Return the same calendar date (month and day) in the
    destination year, if it exists, otherwise use the following day
    (thus changing February 29 to March 1).

    """
    try:
        return d.replace(year = d.year + years)
    except ValueError:
        return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))



from tuf.repository_tool import *

# used for key files at the moment, a password is required by TUF
MASTER_PASSWORD = "fred"

REPO_DIRECTORY = "repository/"

# separate TUF roles for components
delegated_roles = ["fred", "fred-testing", "installer"]


# global repo reference
repository = None


def initialize():
    print "Initializing"
    global repository
    try:
        repository = load_repository(REPO_DIRECTORY)
    except:
        repository = create_new_repository(REPO_DIRECTORY)

    # ensure propery directory structure exists
    for role in delegated_roles:
        mkdir_p(REPO_DIRECTORY + "targets/" + role)

    #
    # load the keys into the repository for use. a simple global password is used at the moment to make them effectively passwordless
    #
    # if we decide to utilize the timestamp key, we may want to separate that part out so it can be used without the others
    #

    root_public_key = import_ed25519_publickey_from_file('keys/root.key.pub')
    root_private_key = import_ed25519_privatekey_from_file('keys/root.key', password=MASTER_PASSWORD)
    targets_public_key = import_ed25519_publickey_from_file('keys/targets.key.pub')
    targets_private_key = import_ed25519_privatekey_from_file('keys/targets.key', password=MASTER_PASSWORD)
    snapshots_public_key = import_ed25519_publickey_from_file('keys/snapshots.key.pub')
    snapshots_private_key = import_ed25519_privatekey_from_file('keys/snapshots.key', password=MASTER_PASSWORD)
    timestamp_public_key = import_ed25519_publickey_from_file('keys/timestamp.key.pub')
    timestap_private_key = import_ed25519_privatekey_from_file('keys/timestamp.key', password=MASTER_PASSWORD)

    # load the keys
    repository.root.add_verification_key(root_public_key)
    repository.root.load_signing_key(root_private_key)
    repository.targets.add_verification_key(targets_public_key)
    repository.targets.load_signing_key(targets_private_key)
    repository.snapshot.add_verification_key(snapshots_public_key)
    repository.snapshot.load_signing_key(snapshots_private_key)
    repository.timestamp.add_verification_key(timestamp_public_key)
    repository.timestamp.load_signing_key(timestap_private_key)

    # ensure we don't try to delegate a role after the repo has already been setup, otherwise we'll get an error
    try:
        for role in delegated_roles:
            repository.targets.delegate(role, [targets_public_key], [])
            repository.targets(role).load_signing_key(targets_private_key)
    except Exception as e:
        print "Warning: " + str(e)
    # set the timestamp signature to expire after 1 year since we're not using online renewal yet
    repository.timestamp.expiration = datetime.datetime.combine(add_years(date.today(), 1), datetime.time.min)
    write_repo()



def write_repo():
    try:
        repository.write()
    except tuf.UnsignedMetadataError, e:
        print e 
    except Exception as e:
        print "Unknown error: ", e


def deploy_staging():
    copy_tree("repository/metadata.staged", "repository/metadata")


def update_target_files():
    for role in delegated_roles:
        list_of_targets = repository.get_filepaths_in_directory(REPO_DIRECTORY + "targets/" + role, recursive_walk=True, followlinks=False)
        print "Updating files in " + role + ": ", list_of_targets
        repository.targets(role).add_targets(list_of_targets)
        repository.targets.add_restricted_paths([REPO_DIRECTORY + "targets/"], role)
    write_repo()


if __name__ == "__main__":
    if "genkeys" in sys.argv:
        if not os.path.exists("keys/root.key"):
            # no keys found so we generate new ones
            generate_and_write_ed25519_keypair('keys/root.key', password=MASTER_PASSWORD)
            generate_and_write_ed25519_keypair('keys/targets.key', password=MASTER_PASSWORD)
            generate_and_write_ed25519_keypair('keys/snapshots.key', password=MASTER_PASSWORD)
            generate_and_write_ed25519_keypair('keys/timestamp.key', password=MASTER_PASSWORD)
        else:
            print "Error: keys already present, delete them from keys/ if you need to regenerate them"
    elif "reset" in sys.argv:
        # for use during testing
        shutil.rmtree("keys", ignore_errors=True)
        shutil.rmtree("repository/metadata", ignore_errors=True)
        shutil.rmtree("repository/metadata.staged", ignore_errors=True)
    elif "update" in sys.argv:
        initialize()
        update_target_files()
        deploy_staging()
        print "Finished"
    else:
        print "Usage: ./manage.py [update] [reset] [genkeys]"
        print ""
        print "       genkeys - Generates a full set of new keypairs under keys/"
        print ""
        print "       update  - scans repository/targets/ to find new and changed files," 
        print "                 signs and deploys updater information"
        print ""
        print "       reset   - removes all keys and repository information, for use during"
        print "                 testing"
