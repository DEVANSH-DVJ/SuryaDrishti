#!/bin/bash

## Set working directory
cd $(dirname "$0")/../data
echo $(pwd)

## List files template
# find $SRC -type f -path '*\.zip' >"$SRC"_list.txt

SRC="XSM_Data"
find $SRC -type f -path '*\.zip' | sort >"$SRC"_list.txt

SRC="XSM_Extracted_LightCurve"
find $SRC -type f -path '*\.lc' | sort >"$SRC"_list.txt

SRC="XSM_Extracted_PHA"
find $SRC -type f -path '*\.pha' | sort >"$SRC"_list.txt

SRC="XSM_Generated_LightCurve"
find $SRC -type f -path '*\.lc' | sort >"$SRC"_list.txt

SRC="XSM_Generated_PHA"
find $SRC -type f -path '*\.pha' | sort >"$SRC"_list.txt

SRC="XSM_Processed_Summary"
find $SRC -type f -path '*\.csv' | sort >"$SRC"_list.txt

SRC="XSM_Processed_Plots"
find $SRC -type f -path '*\.jpg' | sort >"$SRC"_list.txt
