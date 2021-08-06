# CGAP Structural Variant Pipeline

* This repo contains CGAP SV Pipeline components
  * CWL
  * Docker sources - `cgap/cgap-manta:v1` for Manta and `cgap/cnv:v1` for annotation and filtering
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
                               [--ugrp-unrelated] [--ignore-key-conflict]
# env_name : fourfront-cgapwolf (default), fourfront-cgap
```

### Version updates

#### v1

* Created entirely new pipeline - CGAP Structural Variant (SV) Pipeline
  * Step 1. Manta-based SV calling to generate a vcf file containing SVs in proband or trio
  * Step 2. VEP annotation for genes/transcripts and sansa annotation for gnomAD SV population allele frequencies
  * Step 3. Annotation filter to remove non-coding SVs, SVs with high allele frequency in gnomAD SV, and select for only deletions (SVTYPE=DEL) and duplications (SVTYPE=DUP)
  * Step 4. 20 Unrelated filtering to remove common and artefactual SVs compared to 20 unrelated samples that were also run through Manta
  * Step 5. Length-based filtering to remove very long variants that are likely false positives and create issues when ingested into CGAP Portal due to the size of the associated gene list
  * Step 6. Annotation cleaning to produce a vcf file that loads quickly in the Higlass genome browser
