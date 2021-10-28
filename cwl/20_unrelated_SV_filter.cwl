#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement

hints:
  - class: DockerRequirement
    dockerPull: ACCOUNT/sv_germline:VERSION

baseCommand: [python3, /usr/local/bin/20_unrelated_SV_filter.py]

inputs:
  - id: input
    type: File
    inputBinding:
      prefix: -i
    doc: expect the path to the sample vcf gz file

  - id: output
    type: string
    inputBinding:
      prefix: -o
    doc: base name of output vcf gz file

  - id: max_unrelated
    type: int
    inputBinding:
      prefix: -u
    doc: expect the maximum number of unrelated individuals a variant can match with without being filtered out

  - id: wiggle
    type: int
    inputBinding:
      prefix: -w
    doc: expect int for number of bp wiggle on either side of each breakpoint

  - id: recip
    type: float
    inputBinding:
      prefix: -r
    doc: expect float for proportion of overlap between variants

  - id: dirPath20vcf
    type: File
    inputBinding:
      prefix: -d
    doc: expect path to tar directory containing 20 unrelated VCFs

  - id: SV_types
    type: string[]
    inputBinding:
      prefix: -s
    doc: list of SVTYPE classes to consider in 20 VCFs

outputs:
  - id: output
    type: File
    outputBinding:
      glob: $(inputs.output + ".gz")
    secondaryFiles:
      - .tbi

doc: |
  run 20_unrelated_SV_filter.py to create a filtered VCF file
