#!/usr/bin/env python3

################################################
#
#  Script to parse SV annoation from Sansa and
#   incorporate them into a VEP-annotated VCF
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

def sv_dict(args):
    reader = csv.reader(open(args['inputSANSA']), delimiter=" ")

    # given any sansa output, get the name and row index for all population frequency values and the index for query.id (which links to ID for the VEP VCF)
    header = next(reader)
    index = -1
    sansa_index_dict = {}
    sansa_fields = []
    for element in header:
        index += 1
        if "]" in element:
            if element.split("]")[1] != "ANNOID" and element.split("]")[1] != "ID":
                if element.split("]")[1] != "SVTYPE":
                    sansa_index_dict[(element.split("]")[1])]=index
                    sansa_fields.append(element.split("]")[1])
                else:
                    SVTYPE_index = index
                    sansa_index_dict[(element.split("]")[1])]=index
                    sansa_fields.append(element.split("]")[1])
        if element == "query.id":
            queryID_index = index
        if element == "query.svtype":
            querySVtype_index = index

    # we have a dictionary of all the correctly indexed (given row below) and named allele frequency fields from any sansa file
    # we have an ordered list of these fields from sansa
    # we have an index for query.id in each row
    # we have an index for the gnomAD SVTYPE and for the sample SVTYPE
    # we need an index for AF in the sansa_fields list
    AF_index = sansa_fields.index('AF')

    # now want to create a dictionary with query.id as key and an ordered list of sansa_fields as the value, checking for the rarest occurance of an SV based on AF and also for agreement between SV type

    sv_dictionary = {}

    # create functions for individual loops that can all be tested separately

    for row in reader:
        row_annotations = []
        #assign all gnomAD SV values from sansa
        for field in sansa_fields:
            row_annotations.append(row[sansa_index_dict[field]])
        SV_ID = row[queryID_index]
        if SV_ID not in sv_dictionary:#.keys():
            sv_dictionary[SV_ID] = row_annotations
        else:
            # if SV_ID is already in the dictionary, we are now interested in whether dict_gnomAD_SV_TYPE matches sample_SV_TYPE and row_gnomAD_SV_TYPE matches sample_SV_TYPE
            # when nothing matches or both new and old entries match, given that we're running Sansa with "all", we want to return the most rare of the "all" given global allele freq

            # define variables
            dict_gnomAD_SV_TYPE = sv_dictionary[SV_ID][0]
            row_gnomAD_SV_TYPE = row[SVTYPE_index]
            sample_SV_TYPE = row[querySVtype_index]
            row_AF = float(row_annotations[AF_index])
            dict_AF = float(sv_dictionary[SV_ID][AF_index])

            # generate the dictionary
            if dict_gnomAD_SV_TYPE != sample_SV_TYPE: #if current entry SV_TYPE doesn't match query SV_TYPE
                if row_gnomAD_SV_TYPE != sample_SV_TYPE: #if the new line's SV_TYPE doesn't match query SV_TYPE
                    if sample_SV_TYPE == "DEL" or sample_SV_TYPE == "DUP":
                        if dict_gnomAD_SV_TYPE == "CNV":
                            if row_gnomAD_SV_TYPE == "CNV":
                                if row_AF < dict_AF: #if new is more rare, replace the existing entry
                                    sv_dictionary[SV_ID] = row_annotations
                        else:
                            if row_gnomAD_SV_TYPE == "CNV":
                                sv_dictionary[SV_ID] = row_annotations
                            else:
                                if row_AF < dict_AF: #if new is more rare, replace the existing entry
                                    sv_dictionary[SV_ID] = row_annotations
                    else:
                        if row_AF < dict_AF: #if new is more rare, replace the existing entry
                            sv_dictionary[SV_ID] = row_annotations
                else: #if new line's SV_TYPE does match, replace the mismatched current entry regardless of rarity
                    sv_dictionary[SV_ID] = row_annotations
            else: #if current entry SV_TYPE matches query SV_TYPE
                if row_gnomAD_SV_TYPE == sample_SV_TYPE: #if current line also matches
                    if row_AF < dict_AF: #if new is more rare, replace the existing entry
                        sv_dictionary[SV_ID] = row_annotations
    return sv_dictionary, sansa_fields

def main(args, sv_dictionary, sansa_fields):
    # now we read the VCF from VEP and update it.
    vcf = vcf_parser.Vcf(args['inputVEPvcf'])

    # create new header lines and a list to loop to write them - these will need to be manually updated if new fields are brought in or existing fields are dropped.
    # global
    AN_INFO = '##INFO=<ID=AN,Number=1,Type=Integer,Description="Total number of alleles genotyped (for biallelic sites) or individuals with copy-state estimates (for multiallelic sites) from gnomAD v2.1 SV liftover https://www.ncbi.nlm.nih.gov/sites/dbvarapp/studies/nstd166/">'
    AC_INFO = '##INFO=<ID=AC,Number=1,Type=Integer,Description="Number of non-reference alleles observed (for biallelic sites) or individuals at each copy state (for multiallelic sites) from gnomAD v2.1 SV liftover https://www.ncbi.nlm.nih.gov/sites/dbvarapp/studies/nstd166/">'
    AF_INFO = '##INFO=<ID=AF,Number=1,Type=Float,Description="Allele frequency (for biallelic sites) or copy-state frequency (for multiallelic sites) from gnomAD v2.1 SV liftover https://www.ncbi.nlm.nih.gov/sites/dbvarapp/studies/nstd166/">'
    # AFR
    AFR_AN_INFO = '##INFO=<ID=AFR_AN,Number=1,Type=Integer,Description="Total number of AFR alleles genotyped (for biallelic sites) or AFR individuals with copy-state estimates (for multiallelic sites) from gnomAD v2.1 SV liftover https://www.ncbi.nlm.nih.gov/sites/dbvarapp/studies/nstd166/">'
    AFR_AC_INFO = '##INFO=<ID=AFR_AC,Number=1,Type=Integer,Description="Number of non-reference AFR alleles observed (for biallelic sites) or AFR individuals at each copy state (for multiallelic sites) from gnomAD v2.1 SV liftover https://www.ncbi.nlm.nih.gov/sites/dbvarapp/studies/nstd166/">'
    AFR_AF_INFO = '##INFO=<ID=AFR_AF,Number=1,Type=Float,Description="AFR allele frequency (for biallelic sites) or AFR copy-state frequency (for multiallelic sites) from gnomAD v2.1 SV liftover https://www.ncbi.nlm.nih.gov/sites/dbvarapp/studies/nstd166/">'
    # AMR
    AMR_AN_INFO = '##INFO=<ID=AMR_AN,Number=1,Type=Integer,Description="Total number of AMR alleles genotyped (for biallelic sites) or AMR individuals with copy-state estimates (for multiallelic sites) from gnomAD v2.1 SV liftover https://www.ncbi.nlm.nih.gov/sites/dbvarapp/studies/nstd166/">'
    AMR_AC_INFO = '##INFO=<ID=AMR_AC,Number=1,Type=Integer,Description="Number of non-reference AMR alleles observed (for biallelic sites) or AMR individuals at each copy state (for multiallelic sites) from gnomAD v2.1 SV liftover https://www.ncbi.nlm.nih.gov/sites/dbvarapp/studies/nstd166/">'
    AMR_AF_INFO = '##INFO=<ID=AMR_AF,Number=1,Type=Float,Description="AMR allele frequency (for biallelic sites) or AMR copy-state frequency (for multiallelic sites) from gnomAD v2.1 SV liftover https://www.ncbi.nlm.nih.gov/sites/dbvarapp/studies/nstd166/">'
    # EAS
    EAS_AN_INFO = '##INFO=<ID=EAS_AN,Number=1,Type=Integer,Description="Total number of EAS alleles genotyped (for biallelic sites) or EAS individuals with copy-state estimates (for multiallelic sites) from gnomAD v2.1 SV liftover https://www.ncbi.nlm.nih.gov/sites/dbvarapp/studies/nstd166/">'
    EAS_AC_INFO = '##INFO=<ID=EAS_AC,Number=1,Type=Integer,Description="Number of non-reference EAS alleles observed (for biallelic sites) or EAS individuals at each copy state (for multiallelic sites) from gnomAD v2.1 SV liftover https://www.ncbi.nlm.nih.gov/sites/dbvarapp/studies/nstd166/">'
    EAS_AF_INFO = '##INFO=<ID=EAS_AF,Number=1,Type=Float,Description="EAS allele frequency (for biallelic sites) or EAS copy-state frequency (for multiallelic sites) from gnomAD v2.1 SV liftover https://www.ncbi.nlm.nih.gov/sites/dbvarapp/studies/nstd166/">'
    # EUR
    EUR_AN_INFO = '##INFO=<ID=EUR_AN,Number=1,Type=Integer,Description="Total number of EUR alleles genotyped (for biallelic sites) or EUR individuals with copy-state estimates (for multiallelic sites) from gnomAD v2.1 SV liftover https://www.ncbi.nlm.nih.gov/sites/dbvarapp/studies/nstd166/">'
    EUR_AC_INFO = '##INFO=<ID=EUR_AC,Number=1,Type=Integer,Description="Number of non-reference EUR alleles observed (for biallelic sites) or EUR individuals at each copy state (for multiallelic sites) from gnomAD v2.1 SV liftover https://www.ncbi.nlm.nih.gov/sites/dbvarapp/studies/nstd166/">'
    EUR_AF_INFO = '##INFO=<ID=EUR_AF,Number=1,Type=Float,Description="EUR allele frequency (for biallelic sites) or EUR copy-state frequency (for multiallelic sites) from gnomAD v2.1 SV liftover https://www.ncbi.nlm.nih.gov/sites/dbvarapp/studies/nstd166/">'
    # OTH
    OTH_AN_INFO = '##INFO=<ID=OTH_AN,Number=1,Type=Integer,Description="Total number of OTH alleles genotyped (for biallelic sites) or OTH individuals with copy-state estimates (for multiallelic sites) from gnomAD v2.1 SV liftover https://www.ncbi.nlm.nih.gov/sites/dbvarapp/studies/nstd166/">'
    OTH_AC_INFO = '##INFO=<ID=OTH_AC,Number=1,Type=Integer,Description="Number of non-reference OTH alleles observed (for biallelic sites) or OTH individuals at each copy state (for multiallelic sites) from gnomAD v2.1 SV liftover https://www.ncbi.nlm.nih.gov/sites/dbvarapp/studies/nstd166/">'
    OTH_AF_INFO = '##INFO=<ID=OTH_AF,Number=1,Type=Float,Description="OTH allele frequency (for biallelic sites) or OTH copy-state frequency (for multiallelic sites) from gnomAD v2.1 SV liftover https://www.ncbi.nlm.nih.gov/sites/dbvarapp/studies/nstd166/">'

    INFO_list = [OTH_AN_INFO,OTH_AC_INFO,OTH_AF_INFO,EUR_AN_INFO,EUR_AC_INFO,EUR_AF_INFO,EAS_AN_INFO,EAS_AC_INFO,EAS_AF_INFO,AMR_AN_INFO,AMR_AC_INFO,AMR_AF_INFO,AFR_AN_INFO,AFR_AC_INFO,AFR_AF_INFO,AN_INFO,AC_INFO,AF_INFO]

    # add the header lines to the header field
    for tag_def in INFO_list:
        vcf.header.add_tag_definition(tag_def)

    # add the format line for SP
    #SP = '##FORMAT=<ID=SP,Number=.,Type=String,Description="Names of SV callers that identified this variant">'
    #vcf.header.add_tag_definition(SP)

    # write the updated header and annotations
    with open(args['outputfile'], 'w') as fo:
        vcf.write_header(fo)
        #create a list for writing out (e.g., AC field will write as 'AC=')
        out_fields = []
        for field in sansa_fields[1:]:#skip 0th entry - SV_TYPE
            out_fields.append(field+"=")
        # loop the variants and check if ID (which matches query.id) is in our dictionary of sansa results. add the sansa results to the vnt_obj INFO if yes and write the vnt_obj either way
        for vnt_obj in vcf.parse_variants():
            if vnt_obj.ID in sv_dictionary.keys():
                out_values=sv_dictionary[vnt_obj.ID][1:]#skip 0th entry - SV_TYPE
                index = 0
                for field in out_fields:
                    output = field+out_values[index]
                    vnt_obj.add_tag_info(output)
                    index +=1
            vcf.write_variant(fo, vnt_obj)
    subprocess.run(["bgzip", args['outputfile']])
    subprocess.run(["tabix",args['outputfile']+".gz"])

################################################
#   Main
################################################

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Parse sansa output and add annotations to VEP-annotated VCF')

    parser.add_argument('-v','--inputVEPvcf', help='input VEP-annotated VCF file', required=True)
    parser.add_argument('-s','--inputSANSA', help='input Sansa-annotated space delimited file', required=True)
    parser.add_argument('-o','--outputfile', help='output VCF file with VEP and Sansa annotations', required=True)

    args = vars(parser.parse_args())

    sv_dictionary, sansa_fields = sv_dict(args)
    main(args, sv_dictionary, sansa_fields)
