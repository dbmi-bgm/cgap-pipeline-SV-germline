#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement

hints:
  - class: DockerRequirement
    dockerPull: cgap/cnv:v1

baseCommand: [python3, /usr/local/bin/20_unrelated_SV_filter.py]

inputs:
  - id: input
    type: File
    inputBinding:
      position: 1
      prefix: -i
    doc: expect the path to the sample vcf gz file

  - id: output
    type: string
    inputBinding:
      position: 2
      prefix: -o
    doc: base name of output vcf gz file

  - id: max_unrelated
    type: int
    inputBinding:
      position: 3
      prefix: -u
    doc: expect the maximum number of unrelated individuals a variant can match with without being filtered out

  - id: wiggle
    type: int
    inputBinding:
      position: 4
      prefix: -w
    doc: expect int for number of bp wiggle on either side of each breakpoint

  - id: recip
    type: float
    inputBinding:
      position: 5
      prefix: -r
    doc: expect float for proportion of overlap between variants

  - id: dirPath20vcf
    type: File
    inputBinding:
      position: 6
      prefix: -d
    doc: expect path zip directory containing 20 unrelated VCFs

outputs:
  - id: output
    type: File
    outputBinding:
      glob: $(inputs.output + ".gz")

doc: |
  run 20_unrelated_SV_filter.py to create a filtered VCF file
