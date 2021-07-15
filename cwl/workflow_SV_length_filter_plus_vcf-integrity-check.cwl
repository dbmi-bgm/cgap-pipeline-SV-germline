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

  - id: max_length
    type: int
    doc: expect int for maximum length (in bp) for an SV to pass filter

outputs:
  output_vcf:
    type: File
    outputSource: SV_length_filter/output

  vcf-check:
    type: File
    outputSource: integrity-check/output

steps:
  SV_length_filter:
    run: SV_length_filter.cwl
    in:
      input:
        source: input_vcf
      output:
        source: output_vcf
      max_length:
        source: max_length
    out: [output]

  integrity-check:
    run: vcf-integrity-check.cwl
    in:
      input:
        source: SV_length_filter/output
    out: [output]

doc: |
  run SV_length_filter.py to create a filtered VCF file |
  run an integrity check on the output vcf gz
