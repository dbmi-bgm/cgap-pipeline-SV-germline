#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement

hints:
  - class: DockerRequirement
    dockerPull: cgap/cnv:v2

baseCommand: [qc_variant_line_count.sh]

inputs:
  - id: input
    type: File
    inputBinding:
      position: 1
    doc: expect the path to the vcf gz file

outputs:
  - id: output
    type: File
    outputBinding:
      glob: "qc_variant_line_count.json"

doc: |
  count the number of variant lines in vcf |
  return a json file
