======================
SV VCF quality control
======================

Overview
++++++++

To evaluate the quality of a ``vcf`` file, different metrics are calculated using ``granite SVqcVCF``.

The metrics currently available are:

  - variant types distribution per sample
  - total variant counts per sample


Definitions
+++++++++++

Variant types distribution
--------------------------

Total number of variants classified by type as:

  - **DEL**\ etion  (SVTYPE=DEL)
  - **DUP**\ ertion  (SVTYPE=DUP)
  - Total variants (SVTYPE=DEL + SVTYPE=DUP)

Variants are only counted if the sample has a non-reference genotype (0/1 or 1/1)

These metrics are compared between steps to ensure that variants are not unexpectedly dropped during pipeline steps that do not remove variants.
