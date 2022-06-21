#!/usr/bin/env python3

#####################################################
#
#  Script to add confidence classes of SVs from Manta
#
#####################################################

#####################################################
#   Libraries
#####################################################
import argparse, subprocess
from logging import raiseExceptions
from granite.lib import vcf_parser

#####################################################
#   Constants
#####################################################

TRANSLOCATION_SVTYPE_MANTA = "BND"
INSERTION_SVTYPE_MANTA = "INS"

HIGH_CONFIDENCE = "HIGH"
MEDIUM_CONFIDENCE = "MEDIUM"
LOW_CONFIDENCE = "LOW"
NA = "NA"

BICSEQ2 = "bicseq2"
MANTA = "manta"

CONFIDENCE_TAG = "CF"
#####################################################
#   Functions
#####################################################


def calculate_confidence_manta(vnt_obj):

    svtype = vnt_obj.get_tag_value("SVTYPE")

    # difference in length between REF and ALT alleles
    svlen = 0
    # the length condition is not applicable to translocations and insertions
    if svtype not in [TRANSLOCATION_SVTYPE_MANTA, INSERTION_SVTYPE_MANTA]:
        svlen = abs(int(vnt_obj.get_tag_value("SVLEN")))
    vnt_obj.add_tag_format(CONFIDENCE_TAG)

    # iterate over each sample
    for genotype_id in vnt_obj.IDs_genotypes:

        confidence = LOW_CONFIDENCE
        # find ref and alt spanning reads
        try:
            spanning_read = vnt_obj.get_genotype_value(genotype_id, "PR")
            PR_ref, PR_alt = [int(x) for x in spanning_read.split(",")]
            if PR_ref != 0 or PR_alt != 0:
                prop_spanning_reads = PR_alt / (PR_alt + PR_ref)
            else:
                prop_spanning_reads = 0

        # if unavailable assign 0
        except ValueError:
            PR_alt = 0
            PR_ref = 0
            prop_spanning_reads = 0

        # find ref and alt split reads
        try:
            split_read = vnt_obj.get_genotype_value(genotype_id, "SR")
            SR_ref, SR_alt = [int(x) for x in split_read.split(",")]
            if SR_ref != 0 or SR_alt != 0:
                prop_split_reads = SR_alt / (SR_ref + SR_alt)
            else:
                prop_split_reads = 0

        # if unavailable assign 0
        except ValueError:
            SR_alt = 0
            SR_ref = 0
            prop_split_reads = 0

        # we do not assign confidence to insertions at this moment
        if svtype == INSERTION_SVTYPE_MANTA:
            confidence = NA

        elif (
            (svlen > 250 or svtype == TRANSLOCATION_SVTYPE_MANTA)
            and (
                SR_alt >= 5
                and PR_alt >= 5
                and prop_spanning_reads >= 0.3
                and prop_split_reads >= 0.3
            )
        ) or (
            svlen <= 250
            and svtype != TRANSLOCATION_SVTYPE_MANTA
            and SR_alt > 5
            and prop_split_reads > 0.3
        ):

            confidence = HIGH_CONFIDENCE

        elif (
            (svlen > 250 or svtype == TRANSLOCATION_SVTYPE_MANTA)
            and (
                SR_alt >= 3
                and PR_alt >= 3
                and prop_spanning_reads >= 0.3
                and prop_split_reads >= 0.3
            )
        ) or (
            svlen <= 250
            and svtype != TRANSLOCATION_SVTYPE_MANTA
            and SR_alt > 3
            and prop_split_reads > 0.3
        ):

            confidence = MEDIUM_CONFIDENCE

        else:

            confidence = LOW_CONFIDENCE

        vnt_obj.add_values_genotype(genotype_id, confidence)

    return vnt_obj


def add_confidence_manta(input_file, output_file):
    vcf_obj = vcf_parser.Vcf(input_file)

    # create FORMAT entries for vcf header
    FORMAT_cf = f'##FORMAT=<ID={CONFIDENCE_TAG},Number=.,Type=String,Description="Confidence class based on split and spanning reads (HIGH, MEDIUM, LOW)">'
    vcf_obj.header.add_tag_definition(FORMAT_cf, tag_type="FORMAT")

    genotypes_ids = vcf_obj.header.IDs_genotypes

    # write output file with confidence format
    with open(output_file, "w") as output:

        vcf_obj.write_header(output)

        for vnt_obj in vcf_obj.parse_variants():

            calculate_confidence_manta(vnt_obj)

            # write variant
            vcf_obj.write_variant(output, vnt_obj)


def calculate_confidence_bicseq2(vnt_obj):

    # difference in length between REF and ALT alleles
    svlen = 0

    svlen = abs(int(vnt_obj.get_tag_value("SVLEN")))
    logr = float(vnt_obj.get_tag_value("BICseq2_log2_copyRatio"))

    vnt_obj.add_tag_format(CONFIDENCE_TAG)

    # iterate over each sample
    for genotype_id in vnt_obj.IDs_genotypes:

        confidence = LOW_CONFIDENCE

        if (svlen > pow(10, 6)) and (logr > 0.4 or logr < -0.8):

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

    tool = args["tool"]

    if tool == MANTA:
        add_confidence_manta(input_file, output_file)
    elif tool == BICSEQ2:
        add_confidence_bicseq2(input_file, output_file)

    subprocess.run(["bgzip", args["output"]])
    subprocess.run(["tabix", args["output"] + ".gz"])


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
        "-t",
        "--tool",
        help="tool that produced the input VCF",
        required=True,
        choices=[BICSEQ2, MANTA],
    )

    args = vars(parser.parse_args())

    main(args)
