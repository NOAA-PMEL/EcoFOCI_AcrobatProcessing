# EcoFOCI_AcrobatProcessing

For the AQ1601 Cruise, the following instruments where part of the ACROBAT Package:
- WetLabs EcoFluorometer Triplet
- Seabird FastCat
- SUNA
- GPS

## Data Processing Procedures

1. Run the data read routine for each instrument in the package

`ACROBAT_data_read.py Triplet > filename_Triplet.csv` 
`ACROBAT_data_read.py FastCAT > filename_FastCat.csv`
`ACROBAT_data_read.py GPS > filename_GPS.csv`

This will create concatenated data files with 1s resolution.  It is a messy collection of files and each needs to be cleaned at the moment (manually).
Issues to clean:
- many blank lines where no data was recorded but the data capture routine was running. ()
- instances when the instrument was not setup properly and not all data was obtained (often can be seen by errors in headers)

2. run the data combine/merge routines.

`ACROBAT_merge_data.py`

- with clean 1s files, we want to collocate all the datastreams in time.

3. run the data convert routines.
`ACROBAT_convert_data.py`

- converts fastcat conductivity to salinity
- converts ECOTriplet counts to calibrated scientific parameters (edit ECO_Cal.yaml with appropriate constants)

################

Legal Disclaimer

This repository is a scientific product and is not official communication of the National Oceanic and Atmospheric Administration (NOAA), or the United States Department of Commerce (DOC). All NOAA GitHub project code is provided on an 'as is' basis and the user assumes responsibility for its use. Any claims against the DOC or DOC bureaus stemming from the use of this GitHub project will be governed by all applicable Federal law. Any reference to specific commercial products, processes, or services by service mark, trademark, manufacturer, or otherwise, does not constitute or imply their endorsement, recommendation, or favoring by the DOC. The DOC seal and logo, or the seal and logo of a DOC bureau, shall not be used in any manner to imply endorsement of any commercial product or activity by the DOC or the United States Government.