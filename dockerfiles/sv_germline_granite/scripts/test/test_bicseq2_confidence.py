#################################################################
#   Libraries
#################################################################
import sys, os
import pytest
import shutil
from subprocess import Popen
from granite.lib import vcf_parser


filters = __import__('SV_bicseq2_confidence')

def test_filters(tmp_path):
    # Variables and Run
    args = {'input': 'test/files/confidence_filters_bicseq2_in.vcf','output': f'{tmp_path}/output.vcf'}

    filters.main(args)

    a = os.popen(f'bgzip -c -d {tmp_path}/output.vcf.gz')
    b = os.popen('bgzip -c -d test/files/confidence_filters_bicseq2_out.vcf.gz')

    # Test
    assert [row for row in a.read()] == [row for row in b.read()]
