cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}

inputs:
  - id: input_vcf
    type: File
    doc: expect the path to the sample vcf gz file

  - id: contig_file
    type: File
    doc: expect the path to the hg38-vcf-header-contig-fields file

outputs:
  vcf:
    type: File
    outputSource: reformat_SV_vcf/output

  vcf-check:
    type: File
    outputSource: integrity-check/output

steps:
  reformat_SV_vcf:
    run: reformat_SV_vcf.cwl
    in:
      input:
        source: input_vcf
      contigs:
        source: contig_file
    out: [output]

  integrity-check:
    run: vcf-integrity-check.cwl
    in:
      input:
        source: reformat_SV_vcf/output
    out: [output]

doc: |
  run reformat_SV_vcf.py to create a new VCF with contig header fields and a FORMAT field for SP |
  run an integrity check on the output vcf gz
