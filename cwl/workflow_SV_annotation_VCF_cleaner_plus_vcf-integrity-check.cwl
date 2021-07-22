cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}

inputs:
  - id: input_vcf
    type: File
    doc: expect the path to the sample vcf gz file

  - id: output_vcf
    type: string
    default: "output.vcf"
    doc: base name of output vcf gz file

outputs:
  higlass_SV_vcf:
    type: File
    outputSource: SV_annotation_VCF_cleaner/output

  vcf-check:
    type: File
    outputSource: integrity-check/output

steps:
  SV_annotation_VCF_cleaner:
    run: SV_annotation_VCF_cleaner.cwl
    in:
      input:
        source: input_vcf
      output:
        source: output_vcf
    out: [output]

  integrity-check:
    run: vcf-integrity-check.cwl
    in:
      input:
        source: SV_annotation_VCF_cleaner/output
    out: [output]

doc: |
  run SV_annotation_VCF_cleaner.py to create a cleaned VCF for visualization |
  run an integrity check on the output vcf gz
