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
  vcf_sv_confidence:
    type: File
    outputSource: manta_add_confidence/output

steps:
  manta_add_confidence:
    run: manta_add_confidence.cwl
    in:
      input:
        source: input_vcf
      outputfile:
        source: output_vcf
    out: 
        [output]

doc: |
  run SV_manta_confidence.py to calculate confidence classes of CNV variants from Manta
