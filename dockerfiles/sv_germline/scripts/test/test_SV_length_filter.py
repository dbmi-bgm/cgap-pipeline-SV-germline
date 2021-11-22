
#################################################################
#   Libraries
#################################################################
import sys, os
import pytest

from SV_length_filter import (
                            main as main_SV_length_filter
                           )


#################################################################
#   Tests
#################################################################

def test_full_process():
    # Variables and Run
    args = {'inputVCF': 'test/files/GAPFIAFHF16S_chr1.vcf.gz', 'lengthBP': '10000000','outputfile':'output.vcf'}
    # Test
    main_SV_length_filter(args)
    a = os.popen('bgzip -c -d output.vcf.gz')
    b = os.popen('bgzip -c -d test/files/GAPFI1HUPKOC_chr1.vcf.gz')

    assert [row for row in a.read()] == [row for row in b.read()]

    # Clean
    os.remove('output.vcf.gz')

def test_full_process_wrong_size():
    # Variables and Run
    args = {'inputVCF': 'test/files/GAPFIAFHF16S_chr1.vcf.gz', 'lengthBP': '1000','outputfile':'output.vcf'}
    # Test
    main_SV_length_filter(args)
    a = os.popen('bgzip -c -d output.vcf.gz')
    b = os.popen('bgzip -c -d test/files/GAPFI1HUPKOC_chr1.vcf.gz')

    assert [row for row in a.read()] != [row for row in b.read()]

    # Clean
    os.remove('output.vcf.gz')
