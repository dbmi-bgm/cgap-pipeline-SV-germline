#!/usr/bin/env python3

################################################
#
#  Script to hard filter SVs based on length
#     BNDs not supported in MANTA format
#
################################################

################################################
#   Libraries
################################################
from granite.lib import vcf_parser
import sys, argparse, subprocess

################################################
#   Functions
################################################

def main(args):
    vcf = vcf_parser.Vcf(args['inputVCF'])
    with open(args['outputfile'], 'w') as fo:
        vcf.write_header(fo)
        for vnt_obj in vcf.parse_variants():
            if abs(int(vnt_obj.get_tag_value("SVLEN"))) <= int(args['lengthBP']):
                vcf.write_variant(fo, vnt_obj)
    subprocess.run(["bgzip", args['outputfile']])
    subprocess.run(["tabix",args['outputfile']+".gz"])

################################################
#   Main
################################################

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Filter SV VCF for SVs by length')

    parser.add_argument('-i','--inputVCF', help='input VCF file', required=True)
    parser.add_argument('-o','--outputfile', help='output VCF file', required=True)
    parser.add_argument('-l','--lengthBP', help='int for maximum length (in bp) for an SV to pass filter', required=True)
    args = vars(parser.parse_args())

    main(args)
