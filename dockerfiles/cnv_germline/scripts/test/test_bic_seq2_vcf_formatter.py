
#################################################################
#   Libraries
#################################################################
import sys, os
import pytest

from bic_seq2_vcf_formatter import (
                            main as main_bic_seq2_vcf_formatter
                           )


#################################################################
#   Tests
#################################################################

def test_full_process():
    # Variables and Run

    args = {'VCFheader':'test/files/header_reference.vcf.gz', 'pvalue': '0.05', 'fastaRef':'test/files/bicseq_conversion_test_genome.fa', 'sampleName':'proband', 'inputBICseq2': 'test/files/bicseq_conversion_test_input.txt', 'log2_min_dup':'0.2', 'log2_min_hom_dup':'0.8', 'log2_min_del':'0.2', 'log2_min_hom_del':'3', 'outputfile':'output_bic.vcf'}

    # Test
    main_bic_seq2_vcf_formatter(args)
    a = os.popen('bgzip -c -d output_bic.vcf.gz')
    b = os.popen('bgzip -c -d test/files/bicseq_conversion_test_out.vcf.gz')

    assert [row for row in a.read()] == [row for row in b.read()]

    # Clean
    os.remove('output_bic.vcf.gz')
    os.remove('output_bic.vcf.gz.tbi')
