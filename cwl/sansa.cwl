#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement

hints:
  - class: DockerRequirement
    dockerPull: ACCOUNT/cnv:VERSION

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
    secondaryFiles:
      - .tbi
    doc: expect the path to the gnomADref file

outputs:
  - id: output
    type: File
    outputBinding:
      glob: 'sansa.txt'

  - id: sorted_vcf
    type: File
    outputBinding:
      glob: 'sorted*gz'

doc: |
  run sansa.sh to add gnomAD-SV information to variants
