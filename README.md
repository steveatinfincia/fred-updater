# fred-updater

Update system for the Freenet reference daemon

#### Requirements

Install the `tuf[tools]` and `cryptography` modules in a virtualenv for management or development. 

The `tuf` module alone is enough for the client updater script.

#### Manager usage

Run the manage.py script with no arguments to see usage info

#### Client updater usage

By default the update script will update fred using the main repository role, no arguments are needed.

There are two additional commands, `testing` and `installer`, though `installer` is unused at the moment.

#### Repository structure

The update repository has a simple directory structure where node files should go. The contents of each 
target directory will be copied into the root of the node installation.

There is a release tree:

    repository/targets
    repository/targets/fred
    repository/targets/fred/bcprov-jdk15on-154.jar
    repository/targets/fred/bin
    repository/targets/fred/freenet-ext.jar
    repository/targets/fred/freenet-stable-latest.jar
    repository/targets/fred/lib
    repository/targets/fred/plugins
    repository/targets/fred/run.sh
    repository/targets/fred/seednodes.fref
    repository/targets/fred/wrapper.jar

A separate testing build tree:

    repository/targets/fred-testing/

And a directory for installers that may be distributed as updates:

    repository/targets/installer/


#### Distribution of client updater

This is an open question, PyInstaller perhaps?
