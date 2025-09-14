#!/bin/bash

# --- Copyright Notice ---
: <<'END_COPYRIGHT'
Copyright (c) 2025, Samee Ullah. All rights reserved.
This script is the intellectual property of Samee Ullah.
END_COPYRIGHT
# -------------------------

# Adjust these variables to match your setup
INPUT_FASTA="designs_input/input.fasta"
OUTPUT_DIR="designs_output"
METRICS_FILE="designs_input/metrics.csv"
TARGET_LENGTH=118 # IMPORTANT: Change this to your target's length

# --- Script Start ---
echo "Processing results..."

# Create the CSV file and write the header
echo "design_name,iptm,pae_interaction,esm_pll" > $METRICS_FILE

# Read the FASTA file line by line
while read -r line; do
  if [[ $line == \>* ]]; then
    # Extract the design name from the header line
    DESIGN_NAME=$(echo "$line" | sed 's/>//' | tr -d '[:space:]')
    read -r sequence_line

    # Extract the binder sequence (everything before the colon)
    BINDER_SEQUENCE=$(echo "$sequence_line" | cut -d':' -f1)

    echo "--- Processing: $DESIGN_NAME ---"

    # 1. Run compute_af2_metrics.py and capture the output
    AF2_METRICS=$(python compute_af2_metrics.py "$OUTPUT_DIR" "$DESIGN_NAME" --target_length "$TARGET_LENGTH")
    IPTM=$(echo "$AF2_METRICS" | grep "IPTM:" | awk '{print $2}')
    PAE=$(echo "$AF2_METRICS" | grep "PAE interaction:" | awk '{print $3}')

    # 2. Run compute_pll.py and capture the output
    PLL=$(python compute_pll.py "$BINDER_SEQUENCE")

    # 3. Write the results to the CSV file
    echo "$DESIGN_NAME,$IPTM,$PAE,$PLL" >> $METRICS_FILE

    echo "Done. IPTM: $IPTM, PAE: $PAE, PLL: $PLL"
  fi
done < "$INPUT_FASTA"

echo "--- All designs processed. Results saved to $METRICS_FILE ---"
