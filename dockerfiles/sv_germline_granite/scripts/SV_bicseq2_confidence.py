#!/usr/bin/env python3

#######################################################
#
#  Script to add confidence filters to SVs from BIC-seq2
#
#######################################################

#######################################################
#   Libraries
#######################################################
import argparse, subprocess
from granite.lib import vcf_parser

#####################################################
#   Constants
#####################################################


HIGH_CONFIDENCE = "HIGH"
LOW_CONFIDENCE = "LOW"

CONFIDENCE_TAG = "CF"
#####################################################
#   Functions
#####################################################


def calculate_confidence_bicseq2(vnt_obj):

    # difference in length between REF and ALT alleles
    svlen = 0
    
    svlen = abs(int(vnt_obj.get_tag_value("SVLEN")))
    logr = float(vnt_obj.get_tag_value("BICseq2_log2_copyRatio")) 
    
    vnt_obj.add_tag_format(CONFIDENCE_TAG)


    # iterate over each sample
    for genotype_id in vnt_obj.IDs_genotypes:
        
        confidence = LOW_CONFIDENCE

        if (svlen > pow(10,6)) and (logr > 0.4 or logr < -0.8):

            confidence = HIGH_CONFIDENCE

        vnt_obj.add_values_genotype(genotype_id, confidence)

    return vnt_obj


def add_confidence_bicseq2(input_file, output_file):

    vcf_obj = vcf_parser.Vcf(input_file)

    # create FORMAT entries for vcf header
    FORMAT_cf = f'##FORMAT=<ID={CONFIDENCE_TAG},Number=.,Type=String,Description="Confidence class length and copy ratio">'
    vcf_obj.header.add_tag_definition(FORMAT_cf, tag_type="FORMAT")

    # write output file with confidence format
    with open(output_file, "w") as output:

        vcf_obj.write_header(output)

        for vnt_obj in vcf_obj.parse_variants():

            calculate_confidence_bicseq2(vnt_obj)

            # write variant
            vcf_obj.write_variant(output, vnt_obj)


def main(args):

    input_file = args["input"]
    output_file = args["output"]

    add_confidence_bicseq2(input_file, output_file)
    
    subprocess.run(["bgzip", output_file])
    subprocess.run(["tabix", f"{output_file}.gz"])


#####################################################
#   MAIN
#####################################################
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="")

    parser.add_argument("-i", "--input", help="input sample vcf", required=True)
    parser.add_argument(
        "-o", "--output", help="output VCF file with confidence filters", required=True
    )
    parser.add_argument(
        "-t", "--tool", help="tool that produced the input VCF", required=True, choices = ['bicseq2', 'manta'])

    args = vars(parser.parse_args())

    main(args)

