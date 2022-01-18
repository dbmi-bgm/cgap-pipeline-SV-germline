
#################################################################
#   Libraries
#################################################################
import sys, os
import pytest
import shutil
from subprocess import Popen

overlap = __import__('20_unrelated_SV_filter')

#################################################################
#   Tests
#################################################################


def test_recip():
    assert overlap.recip_overlap([0,100],[0,100]) == 1.0
    assert overlap.recip_overlap([0,80],[0,100]) == 0.8
    assert overlap.recip_overlap([0,20],[20,100]) == 0
    assert overlap.recip_overlap([0,100],[1000,1100]) == 0

#################################################################
#            Description of files in same_file.tar
# We only need 2 fabricated "unrelated" files for testing
# GAPFI1PXGJFI_chr1.vcf.gz (input) has been copied 2x to make:
# GAPFI1PXGJFI_chr1_unrelated_1.vcf.gz and _unrelated_2.vcf.gz
#
# These were placed in same_file.tar
# This test results in complete removal of all variants
#################################################################


def test_same_file():
    #first test should remove all variants
    shutil.copyfile('test/files/same_file.tar', 'same_file.tar')
    args = {'inputSampleVCF': 'test/files/GAPFI1PXGJFI_chr1.vcf.gz', 'max_unrelated': '1', 'outputfile':'output.vcf', 'wiggle': '50', 'recip': '0.8', 'dirPath20vcf': 'same_file.tar', 'SVtypes': '[DEL, DUP]'}
    overlap.match(args)
    overlap.filter(args)
    a = os.popen('bgzip -c -d output.vcf.gz')
    b = os.popen('bgzip -c -d test/files/GAPFIAFHF16S_header_only.vcf.gz')
    assert [row for row in a.read()] == [row for row in b.read()]

    os.remove('output.vcf.gz')
    os.remove('output.vcf.gz.tbi')
    os.remove('matched_GAPFI1PXGJFI_chr1_unrelated_1.vcf')
    os.remove('matched_GAPFI1PXGJFI_chr1_unrelated_2.vcf')
    os.remove('same_file.tar')
    shutil.rmtree('unrelated')

    #second test should remove no varaints (change max_related to 2 - which is 3 or more). unrelated added to header, and variants get UNRELATED=2 in INFO
    shutil.copyfile('test/files/same_file.tar', 'same_file.tar')
    args = {'inputSampleVCF': 'test/files/GAPFI1PXGJFI_chr1.vcf.gz', 'max_unrelated': '2', 'outputfile':'output.vcf', 'wiggle': '50', 'recip': '0.8', 'dirPath20vcf': 'same_file.tar', 'SVtypes': '[DEL, DUP]'}
    overlap.match(args)
    overlap.filter(args)
    a = os.popen('bgzip -c -d output.vcf.gz')
    b = os.popen('bgzip -c -d test/files/GAPFI1PXGJFI_chr1_20_2_expected.vcf.gz')
    assert [row for row in a.read()] == [row for row in b.read()]

    os.remove('output.vcf.gz')
    os.remove('output.vcf.gz.tbi')
    os.remove('matched_GAPFI1PXGJFI_chr1_unrelated_1.vcf')
    os.remove('matched_GAPFI1PXGJFI_chr1_unrelated_2.vcf')
    os.remove('same_file.tar')
    shutil.rmtree('unrelated')

#################################################################
#            Description of files in test_files.tar
# We only need 2 fabricated "unrelated" files for testing
# GAPFI1PXGJFI_chr1.vcf.gz (input) has been copied 2x to make:
# GAPFI1PXGJFI_chr1_unrelated_1.vcf.gz and _unrelated_2.vcf.gz
# These files were then modified as follows:
#
# chr1	1227292 SVTYPE changed to DUP for both variants
# should not be filtered out anymore
#
# chr1	1656917 start position changed to 16569177 in _1
# should not be filtered with wiggle of 50 and 80% recip
# should be filtered with wiggle of 1000000 and 80% recip
#
# chr1	4125488 SVTYPE changed to DEL for both variants
# should not be filtered out anymore
#
# chr1	16037389 16060489 changed to 16050000-16080000 in _2
# should not be filtered out with wiggle of 50 and 80% recip
# should not be filtered out with wiggle of 1000000 and 80% recip
# should be filtered out with wiggle of 1000000 and 25% recip
#
# These were placed in same_file.tar
# This test results in complete removal of all variants
#################################################################


def test_files():
    #first test returns 4 variants with UNRELATED=1 or 0 (0 if SVTYPE changed above)
    shutil.copyfile('test/files/test_files.tar', 'test_files.tar')
    args = {'inputSampleVCF': 'test/files/GAPFI1PXGJFI_chr1.vcf.gz', 'max_unrelated': '1', 'outputfile':'output.vcf', 'wiggle': '50', 'recip': '0.8', 'dirPath20vcf': 'test_files.tar', 'SVtypes': '[DEL, DUP]'}
    overlap.match(args)
    overlap.filter(args)
    a = os.popen('bgzip -c -d output.vcf.gz')
    b = os.popen('bgzip -c -d test/files/GAPFI1PXGJFI_chr1_w50_r80.vcf.gz')
    assert [row for row in a.read()] == [row for row in b.read()]

    os.remove('output.vcf.gz')
    os.remove('output.vcf.gz.tbi')
    os.remove('matched_GAPFI1PXGJFI_chr1_unrelated_1.vcf')
    os.remove('matched_GAPFI1PXGJFI_chr1_unrelated_2.vcf')
    os.remove('test_files.tar')
    shutil.rmtree('unrelated')

    #second test returns 3 variants with UNRELATED=1 or 0 (0 if SVTYPE changed above)
    shutil.copyfile('test/files/test_files.tar', 'test_files.tar')
    args = {'inputSampleVCF': 'test/files/GAPFI1PXGJFI_chr1.vcf.gz', 'max_unrelated': '1', 'outputfile':'output.vcf', 'wiggle': '1000000', 'recip': '0.8', 'dirPath20vcf': 'test_files.tar', 'SVtypes': '[DEL, DUP]'}
    overlap.match(args)
    overlap.filter(args)
    a = os.popen('bgzip -c -d output.vcf.gz')
    b = os.popen('bgzip -c -d test/files/GAPFI1PXGJFI_chr1_w1000000_r80.vcf.gz')
    assert [row for row in a.read()] == [row for row in b.read()]

    os.remove('output.vcf.gz')
    os.remove('output.vcf.gz.tbi')
    os.remove('matched_GAPFI1PXGJFI_chr1_unrelated_1.vcf')
    os.remove('matched_GAPFI1PXGJFI_chr1_unrelated_2.vcf')
    os.remove('test_files.tar')
    shutil.rmtree('unrelated')

    #third test returns 2 variants with UNRELATED=0
    shutil.copyfile('test/files/test_files.tar', 'test_files.tar')
    args = {'inputSampleVCF': 'test/files/GAPFI1PXGJFI_chr1.vcf.gz', 'max_unrelated': '1', 'outputfile':'output.vcf', 'wiggle': '1000000', 'recip': '0.25', 'dirPath20vcf': 'test_files.tar', 'SVtypes': '[DEL, DUP]'}
    overlap.match(args)
    overlap.filter(args)
    a = os.popen('bgzip -c -d output.vcf.gz')
    b = os.popen('bgzip -c -d test/files/GAPFI1PXGJFI_chr1_w1000000_r25.vcf.gz')
    assert [row for row in a.read()] == [row for row in b.read()]

    os.remove('output.vcf.gz')
    os.remove('output.vcf.gz.tbi')
    os.remove('matched_GAPFI1PXGJFI_chr1_unrelated_1.vcf')
    os.remove('matched_GAPFI1PXGJFI_chr1_unrelated_2.vcf')
    os.remove('test_files.tar')
    shutil.rmtree('unrelated')
