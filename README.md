<img src="https://github.com/dbmi-bgm/cgap-pipeline/blob/master/docs/images/cgap_logo.png" width="200" align="right">

# CGAP Pipeline for Germline Structural Variants

This repository contains components for the CGAP pipeline for germline structural variants (SVs):

  * CWL workflows
  * CGAP Portal Workflows and MetaWorkflows objects
  * ECR (Docker) source files, which allow for creation of public Docker images (using `docker build`) or private dynamically-generated ECR images (using [*cgap pipeline utils*](https://github.com/dbmi-bgm/cgap-pipeline-utils/) `deploy_pipeline`)

The pipeline starts from analysis ready `bam` files and produces `vcf` files containing calls for SVs as output.
For more details check [*documentation*](https://cgap-pipeline-main.readthedocs.io/en/latest/Pipelines/Downstream/SV_germline/index-SV_germline.html "SV germline").

### Version Updates

#### v1.0.0
* v3 -> v1.0.0, we are starting a new more comprehensive versioning system
* Added some change in metaworkflows to accomodate the changes in foursight

#### v3
* Changes in repo structure to allow for compatibility with new pipeline organization
* Pipeline renamed from `cnv` to `sv_germline`
* Step 8 (cytoband annotation) renamed to secondary annotation. Additional annotations added on top of the existing cytoband annotation. Worst consequence and breakpoint location(s) relative to transcripts are now reported as well as liftover of each breakpoint (if present in hg19). Filtering of transcript by biotype implemented here as well, with variants being dropped if they no longer have any transcripts after this filter.
* Updated `SV_annotation_VCF_cleaner.py` to remove Cytoband and liftover annotations from the `HiGlass SV VCF` for faster loading.

#### v2
* The pipeline has been converted to work on private ECR images which are created from our public Docker images
* Various updates throughout the CGAP SV Pipeline. The current pipeline is outlined below and updates are indicated. A new version of ``granite`` (v0.1.13) is being used for steps 2-13 of the pipeline.
  * Step 1. Manta-based calling of SVs (**Update**: Manta now uses the `callRegions` flag instead of `regions`. We no longer use get_contigs.py from Parliament2 and have removed the Parliament2 github repo from the `cgap-manta:v2` Dockerfile)
  * Step 2. Granite SVqcVCF is used to count DEL and DUP variants and provide a total number of DEL and DUP variants in each sample (**New Step**)
  * Step 3. VEP/sansa annotation (**Update**: VEP now includes the `canonical` flag to identify the canonical transcript for each gene)
  * Step 4. Granite SVqcVCF is used to count DEL and DUP variants and provide a total number of DEL and DUP variants in each sample (**New Step**)
  * Step 5. Annotation filtering and SV type selection
  * Step 6. 20 Unrelated filtering (**Update**: New 20 unrelated reference file resulting from UGRP samples re-mapped with v24 of the CGAP Pipeline including alt index)
  * Step 7. Granite SVqcVCF is used to count DEL and DUP variants and provide a total number of DEL and DUP variants in each sample (**New Step**)
  * Step 8. Cytoband annotation step adds the cytoband for each breakpoint; Cyto1 and Cyto2 (**New Step**)
  * Step 9. Granite SVqcVCF is used to count DEL and DUP variants and provide a total number of DEL and DUP variants in each sample (**New Step**)
  * Step 10. Length filtering
  * Step 11. Granite SVqcVCF is used to count DEL and DUP variants and provide a total number of DEL and DUP variants in each sample (**New Step**)
  * Step 12. Annotation cleaning to produce a vcf file that loads quickly in the Higlass genome browser
  * Step 13. Granite SVqcVCF is used to count DEL and DUP variants and provide a total number of DEL and DUP variants in each sample (**New Step**)

#### v1
* Created entirely new pipeline - CGAP Structural Variant (SV) Pipeline
  * Step 1. Manta-based SV calling to generate a vcf file containing SVs in proband or trio
  * Step 2. VEP annotation for genes/transcripts and sansa annotation for gnomAD SV population allele frequencies
  * Step 3. Annotation filter to remove non-coding SVs, SVs with high allele frequency in gnomAD SV, and select for only deletions (SVTYPE=DEL) and duplications (SVTYPE=DUP)
  * Step 4. 20 Unrelated filtering to remove common and artefactual SVs compared to 20 unrelated samples that were also run through Manta
  * Step 5. Length-based filtering to remove very long variants that are likely false positives and create issues when ingested into CGAP Portal due to the size of the associated gene list
  * Step 6. Annotation cleaning to produce a vcf file that loads quickly in the Higlass genome browser
