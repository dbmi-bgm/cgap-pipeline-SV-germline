
#################################################################
#   Libraries
#################################################################
import sys, os
import pytest

from SV_annotation_VCF_cleaner import (
                            main as main_SV_annotation_VCF_cleaner
                           )


#################################################################
#   Tests
#################################################################

def test_full_process():
    # Variables and Run
    args = {'inputVCF': 'test/files/GAPFI1HUPKOC_chr1.vcf.gz','outputfile':'output.vcf'}
    # Test
    main_SV_annotation_VCF_cleaner(args)
    a = os.popen('bgzip -c -d output.vcf.gz')
    b = os.popen('bgzip -c -d test/files/GAPFIQ1ECJB8_chr1.vcf.gz')

    assert [row for row in a.read()] == [row for row in b.read()]

    # Clean
    os.remove('output.vcf.gz')
