<img src="https://github.com/dbmi-bgm/cgap-pipeline/blob/master/docs/images/cgap_logo.png" width="200" align="right">

# CGAP Pipeline for Germline Structural Variants

This repository contains components for the CGAP pipeline for germline structural variants (SVs):

  * CWL workflows
  * CGAP Portal Workflows and MetaWorkflows objects
  * ECR (Docker) source files, which allow for creation of public Docker images (using `docker build`) or private dynamically-generated ECR images (using [*cgap pipeline utils*](https://github.com/dbmi-bgm/cgap-pipeline-utils/) `deploy_pipeline`)

The pipeline starts from analysis ready `bam` files and produces `vcf` files containing calls for SVs as output.
For more details check [*documentation*](https://cgap-pipeline-main.readthedocs.io/en/latest/Pipelines/Downstream/SV_germline/index-SV_germline.html "SV germline").
