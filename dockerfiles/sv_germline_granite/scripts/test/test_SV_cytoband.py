#################################################################
#   Libraries
#################################################################
import sys, os
import pytest
from subprocess import Popen

from SV_cytoband import (
                            main as main_SV_cytoband
                           )

#################################################################
# Description of variants in cytoband_in.vcf.gz
#################################################################

# below I describe the variants in cytoband_in.vcf.gz
# this is test data - only relevant columns have been modified
# should work with DEL/DUP, but will need modification for other variant types

#1st variant - chr1, POS=1 END=2300000 (both ends of p36.33)
#2nd variant - chr1, POS=2300000 END=2300001 (should be p36.33 and p36.32)
#3rd variant - chr1, POS=46300050 END=125100050 (should be p33 and q12)
#4th variant - chrX, POS=1 END=156040895 (should be p22.33 and q28)

#################################################################
#   Tests
#################################################################

def test_full_process():
    # Variables and Run
    args = {'inputvcf': 'test/files/cytoband_in.vcf.gz','outputfile':'output.vcf','cytoband':'test/files/cytoBand.txt'}
    # Test
    main_SV_cytoband(args)
    a = os.popen('bgzip -c -d output.vcf.gz')
    b = os.popen('bgzip -c -d test/files/cytoband_out.vcf.gz')

    assert [row for row in a.read()] == [row for row in b.read()]
    # Clean
    os.remove('output.vcf.gz')
    os.remove('output.vcf.gz.tbi')

#################################################################
#   Errors
#################################################################

def test_nonstandard_chromosome():
    # Variables
    args = {'inputvcf': 'test/files/cytoband_test_fail.vcf.gz','outputfile':'output.vcf','cytoband':'test/files/cytoBand.txt'}
    # Run and Tests
    with pytest.raises(Exception, match="Unexpected chromosome found. Quitting. Chromosome in SV file: chrY_KI270740v1_random"):
        main_SV_cytoband(args)

def test_end_not_found():
    #Variables
    args = {'inputvcf': 'test/files/cytoband_test_fail2.vcf.gz','outputfile':'output.vcf','cytoband':'test/files/cytoBand.txt'}
    # Run and Tests
    with pytest.raises(Exception, match="Unexpected variant format found - END not in 0th position of INFO. Quitting"):
        main_SV_cytoband(args)

def test_multiple_start_cytobands():
    #Variables
    args = {'inputvcf': 'test/files/cytoband_test_fail3.vcf.gz','outputfile':'output.vcf','cytoband':'test/files/cytoBand_fail.txt'}
    # Run and Tests
    with pytest.raises(Exception, match="Multiple hits for start position. Quitting. Variant: chr1"+"\t"+"55000"):
        main_SV_cytoband(args)

def test_multiple_end_cytobands():
    #Variables
    args = {'inputvcf': 'test/files/cytoband_test_fail4.vcf.gz','outputfile':'output.vcf','cytoband':'test/files/cytoBand_fail.txt'}
    # Run and Tests
    with pytest.raises(Exception, match="Multiple hits for end position. Quitting. Variant: chr1"+"\t"+"4400"):
        main_SV_cytoband(args)
