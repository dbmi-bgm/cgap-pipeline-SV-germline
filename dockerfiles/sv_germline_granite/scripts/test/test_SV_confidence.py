#################################################################
#   Libraries
#################################################################
import sys, os
import pytest
import shutil
from subprocess import Popen
from granite.lib import vcf_parser


confidence = __import__("SV_confidence")


def test_manta(tmp_path):
    """
    This test checks various combinations of possible SV confidence class values (Manta)
    """

    # Variables and Run
    args = {
        "input": "test/files/confidence_classes_manta_in.vcf.gz",
        "output": f"{tmp_path}/output.vcf",
        "tool": "manta",
    }

    confidence.main(args)
    a = os.popen(f"bgzip -c -d {tmp_path}/output.vcf.gz")
    b = os.popen("bgzip -c -d test/files/confidence_classes_manta_out.vcf.gz")

    # Test
    assert [row for row in a.read()] == [row for row in b.read()]


def test_manta_multiple_gentype_ids(tmp_path):
    """
    This test checks if confidence classes would be calculated for more than one sample stored in a VCF file (SVs from Manta)
    """

    # Variables and Run
    args = {
        "input": "test/files/confidence_classes_manta_3_genotype_ids_in.vcf.gz",
        "output": f"{tmp_path}/output.vcf",
        "tool": "manta",
    }

    confidence.main(args)

    a = os.popen(f"bgzip -c -d {tmp_path}/output.vcf.gz")
    b = os.popen(
        "bgzip -c -d test/files/confidence_classes_manta_3_genotype_ids_out.vcf.gz"
    )

    # Test
    assert [row for row in a.read()] == [row for row in b.read()]


def test_bicseq2(tmp_path):
    """
    This test checks various combinations of possible CNV confidence class values (BIC-Seq2)
    """

    # Variables and Run
    args = {
        "input": "test/files/confidence_classes_bicseq2_in.vcf.gz",
        "output": f"{tmp_path}/output.vcf",
        "tool": "bicseq2",
    }

    confidence.main(args)

    a = os.popen(f"bgzip -c -d {tmp_path}/output.vcf.gz")
    b = os.popen("bgzip -c -d test/files/confidence_classes_bicseq2_out.vcf.gz")

    # Test
    assert [row for row in a.read()] == [row for row in b.read()]


def test_bicseq2_multiple_gentype_ids(tmp_path):
    """
    This test checks if confidence classes would be calculated for more than one sample stored in a VCF file (CNVs from BIC-Seq2)
    """

    # Variables and Run
    args = {
        "input": "test/files/confidence_classes_bicseq2_3_genotype_ids_in.vcf.gz",
        "output": f"{tmp_path}/output.vcf",
        "tool": "bicseq2",
    }

    confidence.main(args)

    a = os.popen(f"bgzip -c -d {tmp_path}/output.vcf.gz")
    b = os.popen(
        "bgzip -c -d test/files/confidence_classes_bicseq2_3_genotype_ids_out.vcf.gz"
    )

    # Test
    assert [row for row in a.read()] == [row for row in b.read()]
