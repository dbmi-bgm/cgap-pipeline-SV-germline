#################################################################
#   Libraries
#################################################################
import sys, os, argparse
import pytest
import json
from subprocess import Popen


from combine_sansa_and_VEP_vcf import (
                            sv_dict as sv_dict
                           )

from combine_sansa_and_VEP_vcf import (
                            main as main
                           )
#################################################################
# Description of variants in sansa_testing_file.txt (Space DELIM)
#################################################################

# below I describe the variants in sansa_testing_file.txt
# this is test data - only relevant columns have been modified
# the current goal of combine_sansa_and_VEP_vcf:
#   1. select the most appropriate (and rare) match
#   2. add these to the VEP annotated VCF
# the test_dictionary_construction function below focuses on #1
# when we have multiple matches for a given SV:
#   1. if they all have matching types, select the rarest AF
#   2. if none of them have matching types, select the rarest
#   3. if some have matching types, select the rarest match
#   4. since DELs and DUPs are classes of CNVs:
#          best if DEL can match DEL or DUP can match DUP
#          second best of DEL (or DUP) can match CNV
#          all others considered a mismatch

# 1st hit (DUP00128SUR) is mismatch type with 1 hit
# only option, so place it in dictionary (AF = 0.00012345)

# 2-3 (DEL00640SUR) is matched type, rare first hit
# first hit goes in dictionary (AF = 0.00012345)

# 4-5 (DEL00754SUR) is matched type, rare second hit
# second hit goes in dictionary (AF = 0.00012345)

# 6-8 (DEL00873SUR) has 3 matches, rare middle
# middle hit goes in dictionary (AF = 0.00012345)

# 9-10 (DEL001089SUR) two CNVs to a DEL, rare 1st
# first hit goes in dictionary (AF = 0.00012345)

# 11-12 (DEL001247SUR) two CNVs to a DUP, rare 2nd
# second hit goes in dictionary (AF = 0.00012345)

# 13-14 (DEL001423SUR) CNV and DUP mismatch with INS, rare 2nd
# second hit goes in dictionary (AF = 0.00012345)

# 15-16 (DEL001452SUR) INVs mismatched to DEL, rare 2nd
# second hit goes in dictionary (AF = 0.00012345)

# 17-18 (DUP001889SUR) rare INS or common CNV to DUP
# common CNV (AF = 1) matches better, goes in dict

# 19-20 (DEL002121SUR) rare INV or common CNV to DEL
# common CNV (AF = 1) matches better, goes in dict

# 21-22 (DEL002292SUR) common DEL or rare CNV to DEL
# DEL DEL match is better (AF = 1), goes in dict

# 23-24 (DUP002726SUR) common DUP or rare CNV to DUP
# DUP DUP match is better (AF = 1), goes in dict

# the second function tests the second functionality

#################################################################
#   Tests
#################################################################

def test_dictionary_construction():
    '''Test dictionary construction, which includes type matching and rare AF selection when possible'''
    # Variables and Run
    args = {'inputVEPvcf': 'test/files/SV_type_selector_input.vcf.gz', 'inputSANSA':'test/files/sansa_testing_file.txt','outputfile':'output.vcf'}
    # Test
    dict, list = sv_dict(args)
    expected_dict = json.load(open('test/files/sv_dictionary_file.json',))
    assert dict == expected_dict

def test_full_process():
    # Variables and Run
    args = {'inputVEPvcf': 'test/files/full_combine_test_file.vcf.gz', 'inputSANSA': 'test/files/chr19_sansa.txt','outputfile':'output.vcf'}
    # Test
    sv_dictionary, sansa_fields = sv_dict(args)
    main(args, sv_dictionary, sansa_fields)
    a = os.popen('bgzip -c -d output.vcf.gz')
    b = os.popen('bgzip -c -d test/files/full_combined_test_reference_file.vcf.gz')

    assert [row for row in a.read()] == [row for row in b.read()]

    # Clean
    os.remove('output.vcf.gz')
    os.remove('output.vcf.gz.tbi')
