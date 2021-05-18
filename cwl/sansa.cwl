#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement

hints:
  - class: DockerRequirement
    dockerPull: cgap/cnv:v1

baseCommand: [sansa.sh]

inputs:
  - id: input
    type: File
    inputBinding:
      position: 1
    doc: expect the path to the sample vcf gz file

  - id: gnomAD_SV
    type: File
    inputBinding:
      position: 2
    doc: expect the path to the <NAME HERE> file

outputs:
  - id: output
    type: File
    outputBinding:
      glob: $(sansa.txt)

doc: |
  run sansa.sh to add gnomAD-SV information to variants
