#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement

hints:
  - class: DockerRequirement
    dockerPull: cgap/cnv:v1

baseCommand: [python3, /usr/local/bin/reformat_SV_vcf.py]

inputs:
  - id: input
    type: File
    inputBinding:
      position: 1
      prefix: -i
    doc: expect the path to the sample vcf gz file

  - id: contigs
    type: File
    inputBinding:
      position: 2
      prefix: -c
    doc: expect the path to the hg38-vcf-header-contig-fields file

  - id: output
    default: 'reformat.vcf'
    type: string
    inputBinding:
      position: 2
      prefix: -o
    doc: base name of output vcf gz file

outputs:
  - id: output
    type: File
    outputBinding:
      glob: $(inputs.output + ".gz")

doc: |
  run reformat_SV_vcf.py to create a new VCF with contig header fields and a FORMAT field for SP
