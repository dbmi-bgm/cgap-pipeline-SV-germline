#!/usr/bin/env python3

################################################
#
#       Script to filter SV VCF by SVTYPE
#
################################################

################################################
#   Libraries
################################################
from granite.lib import vcf_parser
import sys, argparse, subprocess, csv

################################################
#   Functions
################################################

def main(args):
    vcf = vcf_parser.Vcf(args['inputVCF'])
    with open(args['outputfile'], 'w') as fo:
        vcf.write_header(fo)
        for vnt_obj in vcf.parse_variants():
            if vnt_obj.get_tag_value("SVTYPE") in args['SVtypes']:
                vcf.write_variant(fo, vnt_obj)
    subprocess.run(["bgzip", args['outputfile']])
    subprocess.run(["tabix",args['outputfile']+".gz"])

################################################
#   Main
################################################

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Filter SV VCF for SVs by type')

    parser.add_argument('-i','--inputVCF', help='input VCF file', required=True)
    parser.add_argument('-o','--outputfile', help='output VCF file', required=True)
    parser.add_argument('-s','--SVtypes', nargs='*', help='list of DEL, DUP, INS, INV, BND to keep', choices=['DEL', 'DUP', 'INS', 'INV', 'BND'], required=True)
    args = vars(parser.parse_args())

    main(args)
