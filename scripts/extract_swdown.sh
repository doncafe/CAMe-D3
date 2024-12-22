#!/bin/bash

# Input WRF file path
WRF_FILE="/LUSTRE/ID/hidromet/WRF/Salidas_WRF_mayo_2022/wrfout_d01_2022-05-01_00.nc"

# Temporary NetCDF file with only SWDOWN and Times
TMP_NC="tmp_swdown.nc"

# Output CSV file
OUTPUT_CSV="swdown_values.csv"

# Extract only SWDOWN and Times variables
ncks -v Times,SWDOWN ${WRF_FILE} ${TMP_NC}

# Use ncdump to convert to text and process with awk to create CSV
echo "Time,SWDOWN" > ${OUTPUT_CSV}

# Extract Times and convert to more readable format
ncdump -v Times ${TMP_NC} | grep -E '[0-9]{4}-[0-9]{2}-[0-9]{2}' | tr -d '"' | tr -d ',' | awk '{print $1}' > times.txt

# Extract SWDOWN values
ncdump -v SWDOWN ${TMP_NC} | grep -E '^[ ]*[0-9]+\.*[0-9]*,' | tr -d ',' > swdown.txt

# Combine times and values into CSV
paste -d',' times.txt swdown.txt >> ${OUTPUT_CSV}

# Clean up temporary files
rm ${TMP_NC} times.txt swdown.txt

echo "Extraction complete. Results saved to ${OUTPUT_CSV}"

# Optional: Show first few lines of the output
echo -e "\nFirst few lines of ${OUTPUT_CSV}:"
head -n 5 ${OUTPUT_CSV}
