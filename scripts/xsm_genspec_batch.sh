#!/bin/bash

## Set working directory
cd $(dirname "$0")/../data
echo $(pwd)

DST="XSM_Generated_PHA"
SRC="XSM_Data"

xsmgenspec_cmd=$xsmdas/bin/xsmgenspec
tbin_size=10

mkdir -p $DST
for filename in $SRC/*.zip; do
    rm -rf temp.zip temp
    echo $filename

    cp $filename temp.zip
    unzip -qo temp.zip -d temp

    l1_file=$(find temp/ -name "*.fits")
    hk_file=$(find temp/ -name "*.hk")
    sa_file=$(find temp/ -name "*.sa")
    gti_file=$(find temp/ -name "*.gti")
    if [ ! -f "$l1_file" ] || [ ! -f "$hk_file" ] || [ ! -f "$sa_file" ] || [ ! -f "$gti_file" ]; then
        echo "Required files not found"
        rm -rf temp.zip temp
        continue
    fi

    spec_file=$DST/$(basename $filename .zip).pha
    $xsmgenspec_cmd l1file=$l1_file specfile=$spec_file hkfile=$hk_file safile=$sa_file gtifile=$gti_file spectype=time-resolved tstart=0 tstop=0 tbinsize=$tbin_size areascal=yes genarf=no

    rm -rf temp.zip temp
done
