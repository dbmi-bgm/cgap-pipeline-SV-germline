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

  - id: cytoband
    type: File
    doc: expect the path to the cytoband reference file

outputs:
  cytoband_SV_vcf:
    type: File
    outputSource: SV_cytoband/output

  vcf-check:
    type: File
    outputSource: integrity-check/output

steps:
  SV_cytoband:
    run: SV_cytoband.cwl
    in:
      input:
        source: input_vcf
      outputfile:
        source: output_vcf
      cytoband:
        source: cytoband
    out: [output]

  integrity-check:
    run: vcf-integrity-check.cwl
    in:
      input:
        source: SV_cytoband/output
    out: [output]

doc: |
  run SV_cytoband.py to add cytoband annotations for each SV breakpoint |
  run an integrity check on the output vcf gz
