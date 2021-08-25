cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}

inputs:
  - id: input_vcf
    type: File
    doc: expect the path to the vcf gz file

outputs:
  variant_lines:
    type: File
    outputSource: count_variant_lines/output

steps:
  count_variant_lines:
    run: qc_variant_lines_vcf.cwl
    in:
      input:
        source: input_vcf
    out: [output]

doc: |
  count the number of variant lines in vcf |
  return a json file
