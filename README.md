![cgap_logo](https://github.com/dbmi-bgm/cgap-sv-pipeline/blob/main/docs/images/cgap_logo.png)

# CGAP Structural Variant Pipeline

* This repo contains CGAP SV Pipeline components
  * CWL
  * Public Docker sources - `cgap/cgap-manta:v2` for Manta and `cgap/cnv:v2` for annotation and filtering
  * Private ECR sources created dynamically at deployment with `post_patch_to_portal.py`
  * Example Tibanna input jsons for individual steps
  * CGAP Portal Workflows and Metaworkflow

For more detailed documentation : https://cgap-sv-pipeline.readthedocs.io/en/latest/

### Updating portal objects
The following command patches/posts all portal objects including softwares, file formats and workflows
```
python post_patch_to_portal.py [--ff-env=<env_name>] [--del-prev-version]
                               [--skip-software]
                               [--skip-file-format] [--skip-file-reference]
                               [--skip-workflow] [--skip-metaworkflow]
                               [--skip-cwl] [--skip-ecr] [--cwl-bucket=<cwl_s3_bucket>]
                               [--account=<account_num>] [--region=<region>]
                               [--ugrp-unrelated] [--ignore-key-conflict]

# env_name : fourfront-cgapwolf (default), fourfront-cgap
# cwl_s3_bucket : '' (default); provide s3 cwl bucket name, required for cwl and workflow steps
# account_num : '' (default); provide aws account number, required for cwl, workflow, and ecr steps
# region : '' (default); provide aws account region, required for cwl, workflow, and ecr steps
```

### Version updates

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
