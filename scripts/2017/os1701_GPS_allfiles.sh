#!/bin/bash

# Purpose:
#       Script to run ACROBAT_gps_read.py

data_dir="/Volumes/WDC_internal/Users/bell/ecoraid/2017/AlongTrack/os1701/TSG//RAW/GPS/*Ocean_Starr*.dat"
prog_dir="/Volumes/WDC_internal/Users/bell/Programs/Python/EcoFOCI_AcrobatProcessing/"


for files in $data_dir
do
    names=(${files//\// })
    outfile=${names[${#names[@]} - 1]}
    #echo "processing file: $files"
    python ${prog_dir}ACROBAT_raw2csv.py ${files} GPS -timecorr 30 -avestring 60s
done
