#!/bin/bash

# Check if a filename was provided as an argument
if [ $# -ne 1 ]; then
    echo "Usage: $0 <input_csv_file>"
    echo "Example: $0 input.csv"
    exit 1
fi

# Store the input filename
INPUT_FILE="$1"

# Check if the input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: File '$INPUT_FILE' not found"
    exit 1
fi

# Generate output filename based on input filename
OUTPUT_FILE="2019_${INPUT_FILE}"

# Process the CSV file using awk to exclude specified columns
awk -F',' 'BEGIN {
    # Print the header with only desired columns
    OFS=","
}
NR==1 {
    for(i=1; i<=NF; i++) {
        if($i != "lat_min" && $i != "lat_max" && $i != "lon_min" && $i != "lon_max") {
            header[i] = i
            printf "%s%s", $i, (i==NF ? "\n" : OFS)
        }
    }
}
NR>1 {
    first = 1
    for(i=1; i<=NF; i++) {
        if(i in header) {
            if(!first) {
                printf OFS
            }
            printf "%s", $i
            first = 0
        }
    }
    printf "\n"
}' "$INPUT_FILE" > "$OUTPUT_FILE"

echo "Processing complete. Output saved to: $OUTPUT_FILE"
