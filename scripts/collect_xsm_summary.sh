#!/bin/bash

## Set working directory
cd $(dirname "$0")/../data
echo $(pwd)

cat XSM_Processed_Summary/*.csv | sort -r | uniq > all.csv
