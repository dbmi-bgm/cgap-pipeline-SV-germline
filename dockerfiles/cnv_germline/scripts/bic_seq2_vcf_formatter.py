#!/usr/bin/env python3

################################################
#
#  Script to BIC-seq2 output table, genotype
#    variants and produce an SV-style VCF
#
################################################

################################################
#   Libraries
################################################

from granite.lib import vcf_parser, fasta_parser
import sys, argparse, subprocess, csv

################################################
#   Functions
################################################

# we only work with the main chromosomes in BIC-seq2
chrom_set = {'chr1',
             'chr2',
             'chr3',
             'chr4',
             'chr5',
             'chr6',
             'chr7',
             'chr8',
             'chr9',
             'chr10',
             'chr11',
             'chr12',
             'chr13',
             'chr14',
             'chr15',
             'chr16',
             'chr17',
             'chr18',
             'chr19',
             'chr20',
             'chr21',
             'chr22',
             'chrX',
             'chrY'}

def main(args):

    # we need to load the genome (fasta) into memory in order to create the REF field, which requires the DNA base at that POS
    handler = fasta_parser.FastaHandler()
    IT = handler.parse_generator(args['fastaRef'])
    fasta_dict = {}
    for header, seq in IT:
        chrom = header.split()[0]
        if chrom in chrom_set:
            fasta_dict[chrom] = seq

    SAMPLE_NAME = (args['sampleName'])
    vcf = vcf_parser.Vcf(args['VCFheader'])
    vcf.header.columns = vcf.header.columns.strip() + "\t" + str(SAMPLE_NAME) + "\n"

    # add new INFO field definitions for BICseq2
    BICseq2_observed_reads= '##INFO=<ID=BICseq2_observed_reads,Number=1,Type=Integer,Description="Total observed reads within variant calculated with BIC-seq2">'
    BICseq2_expected_reads = '##INFO=<ID=BICseq2_expected_reads,Number=1,Type=Float,Description="Total expected reads within variant calculated with BIC-seq2">'
    BICseq2_log2_copyRatio = '##INFO=<ID=BICseq2_log2_copyRatio,Number=1,Type=Float,Description="log2(Observed Reads/Expected Reads) within variant calculated with BIC-seq2. Positive values indicate an excess of reads, suggesting a possible duplication. Negative values indicate a depletion of reads, suggesting a possible deletion">'
    BICseq2_pvalue = '##INFO=<ID=BICseq2_pvalue,Number=1,Type=Float,Description="p-value significance of the call made by BIC-seq2">'

    INFO_list = [BICseq2_pvalue,BICseq2_log2_copyRatio,BICseq2_expected_reads,BICseq2_observed_reads]

    # add the header lines to the header field
    for tag_def in INFO_list:
        vcf.header.add_tag_definition(tag_def)

    with open(args['outputfile'], 'w') as fo:
        vcf.write_header(fo)

        log2_min_del = -float(args['log2_min_del'])
        log2_min_homo_del = -float(args['log2_min_hom_del'])
        log2_min_dup = float(args['log2_min_dup'])
        log2_min_homo_dup = float(args['log2_min_hom_dup'])

        reader = csv.reader(open(args['inputBICseq2']), delimiter="\t")
        header = next(reader)

        # want to parse BIC-seq2 output, and write significant regions out as their appropriate genotypes
        del_count = 0
        dup_count = 0
        for row in reader:
            if float(row[7]) < float(args['pvalue']):
                CHROM = str(row[0])
                POS = int(row[1]) #input is 0 based, so is fasta parser, add 1 for vcf.
                END = int(row[2])
                OBSERVED = str(row[4])
                EXPECTED = str(row[5])
                RATIO = float(row[6])
                P = str(row[7])

                # we only want those variants that are above or below the thresholds
                if RATIO < log2_min_del or RATIO > log2_min_dup:

                    #below are deletions
                    if RATIO < log2_min_del:
                        del_count += 1
                        SVTYPE = "DEL"
                        ID = "BICseq2_"+SVTYPE+"_"+str(del_count)
                        SVLEN = str((POS + 1) - END) # calculation needs 1 based coordinate
                        if RATIO < log2_min_homo_del:
                            PREDICTED_GENO = "1/1"
                        else:
                             PREDICTED_GENO = "0/1"

                    #above are duplications
                    elif RATIO > log2_min_dup:
                        dup_count += 1
                        SVTYPE = "DUP"
                        ID = "BICseq2_"+SVTYPE+"_"+str(dup_count)
                        SVLEN = str(END - (POS + 1)) # calculation needs 1 based coordinate
                        if RATIO > log2_min_homo_dup:
                            PREDICTED_GENO = "./."
                        else:
                            PREDICTED_GENO = "0/1"

                    # now create the VCF fields for those variants that have qualified.

                    # create REF based on genomic position
                    if CHROM in fasta_dict:
                        REF = fasta_dict[CHROM][POS]
                    else:
                        REF = "N"

                    ALT = "<"+SVTYPE+">"
                    QUAL = "."
                    FILTER = "PASS"
                    INFO = "END="+str(END)+";SVTYPE="+SVTYPE+";SVLEN="+SVLEN+";BICseq2_observed_reads="+OBSERVED+";BICseq2_expected_reads="+EXPECTED+";BICseq2_log2_copyRatio="+str(RATIO)+";BICseq2_pvalue="+P
                    FORMAT = "GT"
                    GENOTYPE = PREDICTED_GENO

                    fo.write("\t".join([CHROM, str(POS + 1), ID, REF, ALT, QUAL, FILTER, INFO, FORMAT, GENOTYPE])+"\n")

    #compress output
    subprocess.run(["bgzip", args['outputfile']])
    subprocess.run(["tabix",args['outputfile']+".gz"])


################################################
#   Main
################################################

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Convert the BIC-seq2 output table to a genotyped VCF for a single sample')

    parser.add_argument('-v','--VCFheader', help='reference file containing a vcf header', required=True)
    parser.add_argument('-p','--pvalue', help='pvalue below which regions are retained', required=True)
    parser.add_argument('-f','--fastaRef', help='refernce fasta for the genome', required=True)
    parser.add_argument('-s','--sampleName', help='sample name for VCF header', required=True)
    parser.add_argument('-i','--inputBICseq2', help='input Sansa-annotated space delimited file', required=True)
    parser.add_argument('-d','--log2_min_dup', help='positive value (log2.copyRatio) above which a Duplication is called', required=True)
    parser.add_argument('-u','--log2_min_hom_dup', help='positive value (log2.copyRatio) above which a homozygous or high copy number Duplication is called', required=True)
    parser.add_argument('-e','--log2_min_del', help='negative value (log2.copyRatio) below which a Deletion is called (do not provide negative sign)', required=True)
    parser.add_argument('-l','--log2_min_hom_del', help='negative value (log2.copyRatio) below which a homozygous Deletion is called (do not provide negative sign)', required=True)
    parser.add_argument('-o','--outputfile', help='output VCF file with DELs and DUPs called and genotyped', required=True)

    args = vars(parser.parse_args())

    main(args)
