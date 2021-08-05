=====================================
Part 1. Manta-Based SV Identification
=====================================

Manta
+++++

Input files
-----------

Input files are sequence alignment files in ``bam`` format, generated in ``Part 1`` of the `CGAP WGS Pipeline <https://cgap-pipeline.readthedocs.io/en/latest/wgs.html>`_.

Running Manta
-------------

This step carries out SV identification using ``Manta`` through the script ``manta.sh`` (https://github.com/dbmi-bgm/cgap-sv-pipeline).

``manta.sh`` carries out joint diploid sample analysis when more than one sample is provided and single diploid sample analysis when run with only the proband.

``manta.sh`` identifies Deletions (SVTYPE=DEL), Duplications (SVTYPE=DUP), Insertions (SVTYPE=INS), and Inversion/Translocations (SVTYPE=BND).

The script ``getContigs.py`` (https://github.com/dnanexus/parliament2/) is used to limit the ``Manta`` run to chr1-chr22, chrX and chrY.

The script ``convertInversion.py`` (https://github.com/Illumina/manta/) is also called within ``manta.sh`` to separate (SVTYPE=INV) from other translocations (SVTYPE=BND).  The output file is a ``vcf`` file which is checked for integrity.

* CWL: workflow_manta_integrity-check.cwl
