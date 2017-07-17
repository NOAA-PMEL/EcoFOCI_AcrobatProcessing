#!/bin/bash

# Purpose:
#       Script to run ACROBAT_gps_read.py

data_dir="/Volumes/WDC_internal/Users/bell/ecoraid/2017/AlongTrack/DY1704/ACROBAT/RAW/Optode/*DY1704*.dat"
prog_dir="/Volumes/WDC_internal/Users/bell/Programs/Python/EcoFOCI_AcrobatProcessing/"


for files in $data_dir
do
    names=(${files//\// })
    outfile=${names[${#names[@]} - 1]}
    #echo "processing file: $files"
    python ${prog_dir}ACROBAT_data_read.py ${files} optode 
done
