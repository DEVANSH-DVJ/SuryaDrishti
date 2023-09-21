#!/bin/bash

## Set working directory
cd $(dirname "$0")/../data
echo $(pwd)

DST="XSM_Extracted_LightCurve"
SRC="XSM_Data"

mkdir -p $DST
for filename in $SRC/*.zip; do
    rm -rf temp.zip temp
    echo $filename

    cp $filename temp.zip
    unzip -qo temp.zip -d temp

    lcname=$(find temp/ -name "*.lc")
    if [ -f "$lcname" ]; then
        cp $lcname $DST
        echo "Copied $lcname"
    else
        echo "No light curve found"
    fi

    echo
    rm -rf temp.zip temp
done
