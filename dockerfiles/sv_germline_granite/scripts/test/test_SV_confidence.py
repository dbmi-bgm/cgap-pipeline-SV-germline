#################################################################
#   Libraries
#################################################################
import sys, os
import pytest
import shutil
from subprocess import Popen
from granite.lib import vcf_parser


filters = __import__("SV_confidence")


def test_manta(tmp_path):
    # Variables and Run
    args = {
        "input": "test/files/confidence_filters_manta_in.vcf",
        "output": f"{tmp_path}/output.vcf",
        "tool": "manta",
    }

    filters.main(args)
    a = os.popen(f"bgzip -c -d {tmp_path}/output.vcf.gz")
    b = os.popen("bgzip -c -d test/files/confidence_filters_manta_out.vcf.gz")

    # Test
    assert [row for row in a.read()] == [row for row in b.read()]


def test_manta_multiple_gentype_ids(tmp_path):
    # Variables and Run
    args = {
        "input": "test/files/confidence_filters_manta_3_genotype_ids_in.vcf",
        "output": f"{tmp_path}/output.vcf",
        "tool": "manta",
    }

    filters.main(args)

    a = os.popen(f"bgzip -c -d {tmp_path}/output.vcf.gz")
    b = os.popen(
        "bgzip -c -d test/files/confidence_filters_manta_3_genotype_ids_out.vcf.gz"
    )

    # Test
    assert [row for row in a.read()] == [row for row in b.read()]


def test_bicseq2(tmp_path):
    # Variables and Run
    args = {
        "input": "test/files/confidence_filters_bicseq2_in.vcf",
        "output": f"{tmp_path}/output.vcf",
        "tool": "bicseq2",
    }

    filters.main(args)

    a = os.popen(f"bgzip -c -d {tmp_path}/output.vcf.gz")
    b = os.popen("bgzip -c -d test/files/confidence_filters_bicseq2_out.vcf.gz")

    # Test
    assert [row for row in a.read()] == [row for row in b.read()]
