#!/bin/bash

## Set working directory
cd $(dirname "$0")/../data
echo $(pwd)

DST="XSM_Extracted_PHA"
SRC="XSM_Data"

mkdir -p $DST
for filename in $SRC/*.zip; do
    rm -rf temp.zip temp
    echo $filename

    cp $filename temp.zip
    unzip -qo temp.zip -d temp

    phaname=$(find temp/ -name "*.pha")
    if [ -f "$phaname" ]; then
        cp $phaname $DST
        echo "Copied $phaname"
    else
        echo "No pha found"
    fi

    echo
    rm -rf temp.zip temp
done

for filename in $DST/*.pha; do
    mv -n $filename ${filename//level2r/level2}
done
