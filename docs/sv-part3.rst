====================================
Part 3. Structural Variant Filtering
====================================

Initial Annotation Filtering
++++++++++++++++++++++++++++

The multi-step workflow carries out ``granite`` filtering, coding filtering, gnomAD SV allele frequency filtering and SV type selection.

Requirements
------------

A single, annotated SV ``vcf`` file is required as input. The annotations should include annotation of transcripts through ``VEP`` and gnomAD SV allele frequency through ``sansa``.

The filtering step is composed of multiple steps and the output ``vcf`` file is checked for integrity to ensure the format is correct and the file is not truncated.

Genelist
---------

The genelist step uses ``granite geneList`` to clean VEP annotations for transcripts that are not mapping to any gene of interest. This step does not remove any variants, but only modifies the VEP annotation.


Whitelist
---------

The whitelist steps use ``granite whiteList`` to filter-in exonic and functionally relevant variant based on VEP annotations. This step removes a large number of SVs from the initial call set.


Blacklist
---------

The blacklist step uses ``granite blackList`` to filter-out common variants based on gnomAD SV population allele frequency (AF <= 0.01 retained). Variants without gnomAD SV annotations are also retained.


SV Type Selection
-----------------

This step uses ``SV_type_selector.py`` (https://github.com/dbmi-bgm/cgap-annotations) to filter out unwanted SV types.  Currently only DEL and DUP are retained.


Output
------

The output is a filtered ``vcf`` file containing a lot fewer entries compared to the input ``vcf``. The content of the remaining entries are identical to the input (no additional information added or removed). The resulting ``vcf`` file is checked for integrity.

* CWL: workflow_granite-filtering_SV_selector_plus_vcf-integrity-check.cwl

20 Unrelated Filtering
++++++++++++++++++++++

This step usese ``20_unrelated_SV_filter.py`` (https://github.com/dbmi-bgm/cgap-annotations) to assess common and artefactual SVs in 20 unrelated samples and allows us to filter them from our sample ``vcf`` file. The 20 unrelated reference files (SV ``vcf`` files) were generated using Manta for a single diploid individual as described in ``Part 1`` of the CGAP SV Pipeline.

Requirements
------------

A single, annotated SV ``vcf`` file is expected as input alongside a ``tar`` folder of 20 unrelated SV ``vcf`` files. This step cannot currently assess SVs other than DELs and DUPs (which are provided to the SVTYPE argument), although the ``vcf`` files can contain these variants.

Matching and Filtering
----------------------

When comparing variants from the sample SV ``vcf`` file to an unrelated SV ``vcf`` file, the following matching criteria are currently in place:

  1. SVTYPE must match
  2. Breakpoints at 5' end must be +/- 50 bp from each other
  3. Breakpoints at 3' end must be +/- 50 bp from each other
  4. SVs must reciprocally overlap by a minimum of 80%

The matching step is carried out as follows:

  1. The sample SV ``vcf`` file is compared pair-wise to each of 20 unrelated SV ``vcf`` reference files and SVs that match between are written out from the sample SV ``vcf`` file.
  2. This results in 20 "matched" SV ``vcf`` files that each contain the subset of SVs from the sample file that overlapped a single individual from the 20 unrelated references.
  3. The "matched" SV ``vcf`` files are read into a dictionary that counts the number of times each sample SV is found (max of 1 time per 20 files = 20 matches).

The filtering step reads through the sample SV ``vcf`` file a final time and writes a filtered SV ``vcf`` file that only contains SVs that matched a maximum of n individuals.  The default is currently n = 1, such that sample SVs that match 2 or more of the 20 unrelated individuals are filtered out.

Output
------

The output is a filtered ``vcf`` file containing a lot fewer entries compared to the input ``vcf``.  The variants that remain after filtering will receive an additional annotation, ``UNRELATED=n``, where n is the number of matches found within the 20 unrelated SV ``vcf`` files.

* CWL: workflow_20_unrelated_SV_filter_plus_vcf-integrity-check.cwl


Length Filtering
++++++++++++++++

This step uses ``SV_length_filter.py`` (https://github.com/dbmi-bgm/cgap-annotations) to remove the longest SVs from the sample SV ``vcf`` file. The resulting ``vcf`` file is checked for integrity.

Requirements
------------

A single, annotated SV ``vcf`` file is expected as input alongside a maximum length (currently 10,000,000 bp).

Filtering
---------

Based on the maximum length provided, this step filters the longest SVs from the sample SV ``vcf`` file.  This is currently done to remove nearly chromosome-sized SVs that we believe to be artefactual, which result in very long gene lists during ingestion.

Output
------

The output is a filtered ``vcf`` file containing slightly fewer entries.  No additional information is added or removed for remaining variants. The resulting ``vcf`` file is checked for integrity.  This is the **Full Annotated VCF** that is ingested into the CGAP Portal.

* CWL: workflow_20_unrelated_SV_filter_plus_vcf-integrity-check.cwl

VCF Annotation Cleaning
+++++++++++++++++++++++

This step uses ``SV_annotation_VCF_cleaner.py`` (https://github.com/dbmi-bgm/cgap-annotations) to remove ``VEP`` annotations from the **Full Annotated VCF** to create the **Higlass SV VCF**.  These annotations are removed to improve loading speed in the ``Higlass`` genome browser.  The resulting ``vcf`` file is checked for integrity.

Requirements
------------

The final **Full Annotated VCF**.

Cleaning
--------

To improve loading speed in the ``Higlass`` genome browser, ``VEP`` annotations are removed from the **Full Annotated VCF** and the ``REF`` and ``ALT`` fields are simplified using the ``SV_annotation_VCF_cleaner.py`` script.

Output
------

The output is a modified version of the **Full Annotated VCF** that has been cleaned for the ``Higlass`` genome browser.  This is ingested into the CGAP Portal as the **Higlass SV VCF** and is only used for visualization. The resulting ``vcf`` file is checked for integrity.

* CWL: workflow_SV_annotation_VCF_cleaner_plus_vcf-integrity-check.cwl
