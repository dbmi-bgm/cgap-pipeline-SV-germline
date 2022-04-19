#!/usr/bin/env python3

################################################
#
#  Script to add cytoband annotations to SVs
#
################################################

################################################
#   Libraries
################################################
import sys, argparse, csv, tabix, subprocess
from granite.lib import vcf_parser

################################################
#   Functions
################################################

def main(args):
    #open cytoband reference file
    reader = csv.reader(open(args['cytoband']), delimiter="\t")

    cyto_dict = {}
    for row in reader:
        if row[3] != '': #drop entries without cytobands
            #create cyto_dict
            if row[0] not in cyto_dict:
                cyto_dict[row[0]] = [[int(row[1])+1,int(row[2]),row[3]]] #correct for 0 vs 1 based
            else:
                cyto_dict[row[0]].append([int(row[1])+1,int(row[2]),row[3]]) #correct for 0 vs 1 based

    #open sample VCF
    vcf = vcf_parser.Vcf(args['inputvcf'])

    #create INFO entries for vcf header
    Cyto1_INFO = '##INFO=<ID=Cyto1,Number=1,Type=String,Description="Cytoband for SV start (POS) from hg38 cytoBand.txt.gz from UCSC">'
    Cyto2_INFO = '##INFO=<ID=Cyto2,Number=1,Type=String,Description="Cytoband for SV end (INFO END) from hg38 cytoBand.txt.gz from UCSC">'
    INFO_list = [Cyto2_INFO,Cyto1_INFO]

    # add the header lines to the header field
    for tag_def in INFO_list:
        vcf.header.add_tag_definition(tag_def)

    # write output file with cytoband info
    with open(args['outputfile'], 'w') as fo:
        vcf.write_header(fo)
        for vnt_obj in vcf.parse_variants():
            #get start and end coordinates for the SV
            start = vnt_obj.POS
            if vnt_obj.INFO.split(";")[0].split("=")[0] == "END":
                end = int(vnt_obj.INFO.split(";")[0].split("=")[1])
            else:
                raise Exception('Unexpected variant format found - END not in 0th position of INFO. Quitting')

            start_cyto=''
            end_cyto=''

            #search against the cyto_dict
            if vnt_obj.CHROM in cyto_dict:
                for cytoband in cyto_dict[vnt_obj.CHROM]:
                    if start >= cytoband[0] and start <= cytoband[1]:
                        if start_cyto == '':
                            start_cyto=cytoband[2]
                            vnt_obj.add_tag_info("Cyto1="+start_cyto)
                        else:
                            raise Exception('Multiple hits for start position. Quitting. Variant: '+vnt_obj.CHROM+"\t"+str(vnt_obj.POS))
                    if end >= cytoband[0] and end <= cytoband[1]:
                        if end_cyto == '':
                            end_cyto=cytoband[2]
                            vnt_obj.add_tag_info("Cyto2="+end_cyto)
                        else:
                            raise Exception('Multiple hits for end position. Quitting. Variant: '+vnt_obj.CHROM+"\t"+str(vnt_obj.POS))
            else:
                raise Exception('Unexpected chromosome found. Quitting. Chromosome in SV file: '+vnt_obj.CHROM)

            #write variant
            vcf.write_variant(fo, vnt_obj)

    subprocess.run(["bgzip", args['outputfile']])
    subprocess.run(["tabix",args['outputfile']+".gz"])

################################################
#   MAIN
################################################
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='')

    parser.add_argument('-i', '--inputvcf',  help='input sample vcf', required=True)
    parser.add_argument('-c','--cytoband', help='input tab delimited cytoband file', required=True)
    parser.add_argument('-o','--outputfile', help='output VCF file with cytoband annotations', required=True)

    args = vars(parser.parse_args())

    main(args)
