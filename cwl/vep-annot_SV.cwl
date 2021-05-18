#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement

hints:
  - class: DockerRequirement
    dockerPull: cgap/cnv:v1

baseCommand: [vep-annot_SV.sh]

inputs:
  - id: input
    type: File
    inputBinding:
      position: 1
    secondaryFiles:
      - .tbi
    doc: expect the path to the vcf gz file

  - id: reference
    type: File
    inputBinding:
      position: 2
    secondaryFiles:
      - ^.dict
      - .fai
    doc: expect the path to the fa reference file

  - id: vep
    type: File
    inputBinding:
      position: 3
    secondaryFiles:
      - ^^^.plugins.tar.gz
    doc: expect the path to the vep tar gz

  - id: version
    type: string
    inputBinding:
      position: 4
    doc: vep datasource version

  - id: assembly
    type: string
    inputBinding:
      position: 5
    doc: genome assembly version

outputs:
  - id: output
    type: File
    outputBinding:
      glob: sv_annotated_vep.vcf.gz
    secondaryFiles:
      - .tbi

doc: |
  run vep SV
