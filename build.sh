#!/bin/sh

#
# Build script for client updater binaries
#
# Generates 'dist/update-linux-64' on 64-bit Linux, 'dist/update-darwin-64' on macOS, etc
# 

PLATFORM=`python2.7 -c "import platform; print platform.system().lower()"`
ARCH=`python2.7 -c "import sys; arch = lambda(is_64bit): "64" if is_64bit else "32"; print arch(sys.maxsize > 2**32)"`

echo "Building for $PLATFORM-$ARCH"

# clean up previous runs
rm -rf installer_env client_env build dist update-$PLATFORM-$ARCH.spec

# set up build environment
virtualenv -p python2.7 installer_env
source installer_env/bin/activate
pip install pyinstaller
deactivate

# set up client environment and build 
virtualenv -p python2.7 client_env
source client_env/bin/activate
pip install tuf
installer_env/bin/pyinstaller --onefile client/update.py --name "update-$PLATFORM-$ARCH"
