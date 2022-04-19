#################################################################
#   Libraries
#################################################################
import sys, os, argparse
import pytest
from subprocess import Popen


from SV_type_selector import (
                            main as main_SV_type_selector
                           )


#################################################################
#   Tests
#################################################################

def test_just_DEL():
    '''Filter for only deletions - match outfile from test/files'''
    # Variables and Run
    args = {'inputVCF': 'test/files/SV_type_selector_input.vcf.gz','outputfile':'output.vcf','SVtypes':'DEL'}
    # Test
    main_SV_type_selector(args)
    a = os.popen('bgzip -c -d output.vcf.gz')
    b = os.popen('bgzip -c -d test/files/SV_type_selector_input_just_DEL.vcf.gz')

    assert [row for row in a.read()] == [row for row in b.read()]
    # Clean
    os.remove('output.vcf.gz')
    os.remove('output.vcf.gz.tbi')

def test_DUP_INV():
    '''Filter for duplications and inversions - match outfile from test/files'''
    # Variables and Run
    args = {'inputVCF': 'test/files/SV_type_selector_input.vcf.gz','outputfile':'output.vcf','SVtypes':['DUP','INV']}
    # Test
    main_SV_type_selector(args)
    a = os.popen('bgzip -c -d output.vcf.gz')
    b = os.popen('bgzip -c -d test/files/SV_type_selector_input_DUP_INV.vcf.gz')

    assert [row for row in a.read()] == [row for row in b.read()]
    # Clean
    os.remove('output.vcf.gz')
    os.remove('output.vcf.gz.tbi')

def test_all_SVs():
    '''Filter for duplications, inversions, insertions, translocations and deletions - match input VCF since that is all SVTYPEs'''
    # Variables and Run
    args = {'inputVCF': 'test/files/SV_type_selector_input.vcf.gz','outputfile':'output.vcf','SVtypes':['DUP','INV','INS','BND','DEL']}
    # Test
    main_SV_type_selector(args)
    a = os.popen('bgzip -c -d output.vcf.gz')
    b = os.popen('bgzip -c -d test/files/SV_type_selector_input.vcf.gz')

    assert [row for row in a.read()] == [row for row in b.read()]
    # Clean
    os.remove('output.vcf.gz')
    os.remove('output.vcf.gz.tbi')

#################################################################
#   Errors
#################################################################

def test_nonstandard_SVTYPE(capsys):
    '''Simple test to show that unexpected SVTYPEs trigger a system exit'''
    parser=argparse.ArgumentParser()
    parser.add_argument('-s','--SVtypes', nargs='*', help='list of DEL, DUP, INS, INV, BND to keep', choices=['DEL', 'DUP', 'INS', 'INV', 'BND'], required=True)
    args = ["--SVtypes", ["DEL","BND","WRONG"]]
    with pytest.raises(SystemExit):
        parser.parse_args(args)
    stderr = capsys.readouterr().err
    assert 'invalid choice' in stderr
