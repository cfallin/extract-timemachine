#!/bin/bash

INSTALL_PATH=`dirname $0`
EXTRACTPY=$INSTALL_PATH/extract.py
if [ ! -f $EXTRACTPY ]; then
    echo Could not find extract.py "(looking in ${INSTALL_PATH})". Please ensure
    echo the Python script is present.
    exit 1
fi

if [ $# -lt 3 ]; then
    echo "Usage: extract.sh <TimeMachine backup device> <machine name> <dest>"
    echo ""
    echo "For example:"
    echo "   ./extract.sh /dev/sdb mymac /tmp/mymac-restore"
    exit 1
fi

DEV=$1
NAME=$2
DEST=$3

if [ -e $DEST ]; then
    echo Destination $DEST already exists; please remove first.
    exit 1
fi

if [ `whoami` != "root" ]; then
    echo Must run as root.
    exit 1
fi

mount | grep -q $DEV
if [ $? -eq 0 ]; then
    echo Filesystem already mounted; please unmount first.
    exit 1
fi

SRC=/tmp/timemachine-$$
if [ -e $SRC ]; then umount $SRC; rm -r $SRC; fi
mkdir -p $SRC

mount -t hfsplus $DEV $SRC
if [ $? -ne 0 ]; then
    echo Error mounting $DEV.
    exit 1
fi

DUMPDIR=$SRC/Backups.backupdb/$NAME/Latest/
if [ ! -d $DUMPDIR ]; then
    echo No TimeMachine backups found in $DUMPDIR. Exiting.
    exit 1
fi

FIRSTDUMP=`ls $DUMPDIR | head -n 1`
if [ "$FIRSTDUMP" = "" ]; then
    echo No dumps found in $DUMPDIR. Exiting.
    exit 1
fi

SRC=$DUMPDIR/$FIRSTDUMP

echo Extracting from ${SRC}...
    
$EXTRACTPY -s $SRC -d $DEST

umount $SRC
rm -r $SRC
