#!/usr/bin/env python3

################################################
#
#  Script to assess common and artefactual
#       SVs in 20 unrelated samples
#      Does not work with MANTA BND
################################################

################################################
#   Libraries
################################################
from granite.lib import vcf_parser
import argparse, subprocess, os
import tarfile

################################################
#   Functions
################################################

def recip_overlap(v1_coor, v2_coor):
    overlap = max(0, min(v1_coor[1], v2_coor[1]) - max(v1_coor[0], v2_coor[0]))
    return min(overlap/(v1_coor[1]-v1_coor[0]), overlap/(v2_coor[1]-v2_coor[0]))

def match(args):
    #untar the archive
    tarfile.open(args['dirPath20vcf']).extractall()

    #inputs
    sample = vcf_parser.Vcf(args['inputSampleVCF'])
    wiggle = int(args['wiggle'])#50
    recip = float(args['recip'])#0.8
    unrelated_dir = 'unrelated' #args['dirPath20vcf']

    for filename in os.listdir(unrelated_dir):
        if filename.endswith(".vcf.gz"):
            unrelatedVCF = vcf_parser.Vcf(unrelated_dir+"/"+filename)
            vcf1_dict = {}
            # add unrelated SVs to a dictionary
            for vnt_obj in unrelatedVCF.parse_variants():
                if vnt_obj.get_tag_value("SVTYPE") in args['SVtypes']:
                    if vnt_obj.CHROM not in vcf1_dict:
                        vcf1_dict[vnt_obj.CHROM]=[[vnt_obj.get_tag_value("SVTYPE"),int(vnt_obj.POS),int(vnt_obj.get_tag_value("END"))]]
                    else:
                        #if [vnt_obj.ALT,int(vnt_obj.POS),int(vnt_obj.get_tag_value("END"))] not in vcf1_dict[vnt_obj.CHROM]:
                        #    vcf1_dict[vnt_obj.CHROM].append([vnt_obj.ALT,int(vnt_obj.POS),int(vnt_obj.get_tag_value("END"))])
                        vcf1_dict[vnt_obj.CHROM].append([vnt_obj.get_tag_value("SVTYPE"),int(vnt_obj.POS),int(vnt_obj.get_tag_value("END"))])
            # write out variants that match between sample and individual from 20 unrelated
            matchedFile = "matched_"+filename.split(".")[0]+"."+filename.split(".")[1]
            with open(matchedFile, 'w') as fo:
                sample.write_header(fo)
                for vnt_obj in sample.parse_variants():
                    SV_TYPE = vnt_obj.get_tag_value("SVTYPE")
                    vnt_range = [int(vnt_obj.POS),int(vnt_obj.get_tag_value("END"))]
                    try:
                        for dict_vnt in vcf1_dict[vnt_obj.CHROM]:
                            if SV_TYPE == dict_vnt[0]:
                                if vnt_range[0] in range(dict_vnt[1]-wiggle,dict_vnt[1]+wiggle):
                                    if vnt_range[1] in range(dict_vnt[2]-wiggle,dict_vnt[2]+wiggle):
                                        dict_vnt_range = [dict_vnt[1],dict_vnt[2]]
                                        if recip_overlap(vnt_range,dict_vnt_range) > recip:
                                            sample.write_variant(fo, vnt_obj)
                                            break
                    except:
                        pass
            #subprocess.run(["bgzip", matchedFile])
            #subprocess.run(["tabix",args['outputfile']+".gz"])

def filter(args):
    counting_dict = {}
    for filename in os.listdir("."):
        if filename.startswith("matched"):
            unrelatedVCF = vcf_parser.Vcf(filename)
            for vnt_obj in unrelatedVCF.parse_variants():
                SV_TYPE = vnt_obj.get_tag_value("SVTYPE")
                query = vnt_obj.CHROM+"_"+vnt_obj.ID+"_"+SV_TYPE+"_"+str(vnt_obj.POS)+"_"+str(vnt_obj.get_tag_value("END"))
                if query not in counting_dict:
                    counting_dict[query]=1
                else:
                    counting_dict[query]+=1

    # load sample, add new header line
    sample = vcf_parser.Vcf(args['inputSampleVCF'])
    twenty_unrelated = '##INFO=<ID=UNRELATED,Number=1,Type=Integer,Description="Number of 20 unrelated individuals that share this variant with target sample">'
    sample.header.add_tag_definition(twenty_unrelated)

    # conditionally filter and add 20 unrelated info before writing variants out
    with open(args['outputfile'], 'w') as fo:
        sample.write_header(fo)
        max_of_20 = int(args["max_unrelated"])
        for vnt_obj in sample.parse_variants():
            SV_TYPE = vnt_obj.get_tag_value("SVTYPE")
            query = vnt_obj.CHROM+"_"+vnt_obj.ID+"_"+SV_TYPE+"_"+str(vnt_obj.POS)+"_"+str(vnt_obj.get_tag_value("END"))
            if query in counting_dict:
                if counting_dict[query] <= max_of_20:
                    twenty_entry = 'UNRELATED='+str(counting_dict[query])
                    vnt_obj.add_tag_info(twenty_entry)
                    sample.write_variant(fo, vnt_obj)
            else:
                twenty_entry = 'UNRELATED=0'
                vnt_obj.add_tag_info(twenty_entry)
                sample.write_variant(fo, vnt_obj)

    subprocess.run(["bgzip", args['outputfile']])
    subprocess.run(["tabix",args['outputfile']+".gz"])

################################################
#   Main
################################################

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Count matches between sample VCF and 20 unrelated VCFs. generate output file with common and artefactual variants filtered out of the original sample file')

    parser.add_argument('-i','--inputSampleVCF', help='input sample VCF file', required=True)
    parser.add_argument('-o','--outputfile', help='output file name for filtered VCF', required=True)
    parser.add_argument('-u','--max_unrelated', help='number of unrelated individuals that can share variant with sample without being filtered out', required=True)
    parser.add_argument('-w','--wiggle', help='int for number of bp wiggle on either side of each breakpoint', required=True)
    parser.add_argument('-r','--recip', help='float for proportion of overlap between variants', required=True)
    parser.add_argument('-d','--dirPath20vcf', help='path to tar file of 20 unrelated VCFs', required=True)
    parser.add_argument('-s','--SVtypes', nargs='*', help='list of variant types to consider from 20 unrelated VCFs (DEL, DUP, INS, INV). BND not supported', choices=['DEL', 'DUP', 'INS', 'INV'], required=True)

    args = vars(parser.parse_args())

    match(args)
    filter(args)
