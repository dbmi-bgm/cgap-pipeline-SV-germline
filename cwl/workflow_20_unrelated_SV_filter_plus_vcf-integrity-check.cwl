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
    default: "20_filtered.vcf"
    doc: base name of output vcf gz file

  - id: max_unrelated
    type: int
    default: 1
    doc: expect the maximum number of unrelated individuals a variant can match with without being filtered out

  - id: wiggle
    type: int
    default: 50
    doc: expect int for number of bp wiggle on either side of each breakpoint

  - id: recip
    type: float
    default: 0.8
    doc: expect float for proportion of overlap between variants

  - id: dirPath20vcf
    type: File
    doc: expect path to tar directory containing 20 unrelated VCFs

  - id: SV_types
    type: string[]
    doc: list of SVTYPE classes to consider in the 20 unrelated VCFs

outputs:
  output_vcf:
    type: File
    outputSource: 20_unrelated_SV_filter/output

  vcf-check:
    type: File
    outputSource: integrity-check/output

steps:
  20_unrelated_SV_filter:
    run: 20_unrelated_SV_filter.cwl
    in:
      input:
        source: input_vcf
      output:
        source: output_vcf
      max_unrelated:
        source: max_unrelated
      wiggle:
        source: wiggle
      recip:
        source: recip
      dirPath20vcf:
        source: dirPath20vcf
      SV_types:
        source: SV_types
    out: [output]

  integrity-check:
    run: vcf-integrity-check.cwl
    in:
      input:
        source: 20_unrelated_SV_filter/output
    out: [output]

doc: |
  run 20_unrelated_SV_filter.py to create a filtered VCF file |
  run an integrity check on the output vcf gz
