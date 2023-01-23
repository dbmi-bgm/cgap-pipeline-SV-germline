cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}

inputs:
  - id: input_vcf
    type: File
    doc: expect the path to the vcf gz file

  - id: samples
    type: string[]
    doc: samples to collect metrics for

outputs:
  qc_json:
    type: File
    outputSource: granite-SVqcVCF/qc_json

steps:
  granite-SVqcVCF:
    run: granite-SVqcVCF.cwl
    in:
      input_vcf:
        source: input_vcf
      samples:
        source: samples
    out: [qc_json]


doc: |
  run granite SVqcVCF
