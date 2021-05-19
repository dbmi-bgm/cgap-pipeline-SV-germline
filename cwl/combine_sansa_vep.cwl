#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement

hints:
  - class: DockerRequirement
    dockerPull: cgap/cnv:v1

baseCommand: [combine_sansa_and_VEP_vcf.py]

inputs:
  - id: vep_vcf
    type: File
    inputBinding:
      position: 1
      prefix: -v
    doc: expect the path to the vep-annotated vcf gz file

  - id: sansa_txt
    type: File
    inputBinding:
      position: 2
      prefix: -s
    doc: expect the path to the sansa-annotated txt file

  - id: output
    default: 'combined.vcf'
    type: string
    inputBinding:
      position: 3
      prefix: -o
    doc: expect the path to the combined vcf gz file

outputs:
  - id: output
    type: File
    outputBinding:
      glob: 'combined.vcf.gz'

doc: |
  run combine_sansa_and_VEP_vcf.py to combine sansa and vep annotations into single VCF
