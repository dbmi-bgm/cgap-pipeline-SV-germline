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
  SV_confidence:
    type: File
    outputSource: manta_confidence_filters/output

steps:
  manta_confidence_filters:
    run: manta_confidence_filters.cwl
    in:
      input:
        source: input_vcf
      outputfile:
        source: output_vcf
    out: 
        [output]

doc: |
  run SV_manta_filters.py to calculate confidence classes of CNV variants from Manta
