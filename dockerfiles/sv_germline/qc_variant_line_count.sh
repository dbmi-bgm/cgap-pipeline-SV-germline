#!/bin/bash

# Command line variables
vcf_file=$1

# Counting variants
qc_variant_line_count=$(gunzip -c $vcf_file | grep -c -v "^#")

# Printing result as tsv
echo -e "{\"total variant lines in vcf\":\"${qc_variant_line_count}\"}" > qc_variant_line_count.json
