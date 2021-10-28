#!/usr/bin/env

################################################
#
#      Script to clean SV VCF for
#        better SV visualization
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
            vnt_obj.REF = "."
            vnt_obj.ALT = "<"+vnt_obj.get_tag_value("SVTYPE")+">"
            vnt_obj.remove_tag_info("CSQ")
            vcf.write_variant(fo, vnt_obj)
    subprocess.run(["bgzip", args['outputfile']])
    subprocess.run(["tabix",args['outputfile']+".gz"])

################################################
#   Main
################################################

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Clean SV VCF for easier visualization')

    parser.add_argument('-i','--inputVCF', help='input VCF file', required=True)
    parser.add_argument('-o','--outputfile', help='output VCF file', required=True)
    args = vars(parser.parse_args())

    main(args)
