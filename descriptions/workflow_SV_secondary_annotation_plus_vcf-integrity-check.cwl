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

  - id: chainfile
    type: File
    doc: expect the path to the hg38-to-hg19-chain file

outputs:
  cytoband_SV_vcf:
    type: File
    outputSource: SV_cytoband/output

  vcf-check:
    type: File
    outputSource: integrity-check/output

steps:
  SV_liftover_hg19:
    run: SV_liftover_hg19.cwl
    in:
      input:
        source: input_vcf
      chainfile:
        source: chainfile
    out: [output]

  SV_worst_and_locations:
    run: SV_worst_and_locations.cwl
    in:
      input:
        source: SV_liftover_hg19/output
    out: [output]

  SV_cytoband:
    run: SV_cytoband.cwl
    in:
      input:
        source: SV_worst_and_locations/output
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
  run liftover_hg19.py to add hg19_chr with hg19_pos and/or hg19_end data to INFO field for breakpoints that lift over to hg19 |
  run SV_worst_and_locations.py to annotate worst consequence and breakpoint locations |
  run SV_cytoband.py to add cytoband annotations for each SV breakpoint |
  run an integrity check on the output vcf gz
