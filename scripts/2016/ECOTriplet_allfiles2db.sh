#!/bin/bash

# Purpose:
#       Script to run ACROBAT_gps_read.py

data_dir="/Volumes/WDC_internal/Users/bell/ecoraid/2016/AlongTrack/AQ1601/ACROBAT/RAW/Triplet/*.dat"
prog_dir="/Volumes/WDC_internal/Users/bell/Programs/Python/EcoFOCI_AcrobatProcessing/"


for files in $data_dir
do
    names=(${files//\// })
    outfile=${names[${#names[@]} - 1]}
    #echo "processing file: $files"
    python ${prog_dir}ACROBAT_raw2db.py ${files} ECOTriplet -ini EcoFOCI_config/AQ1601.yaml
done
