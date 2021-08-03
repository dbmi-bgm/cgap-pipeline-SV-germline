#!/usr/bin/env cwl-runner

cwlVersion: v1.0
baseCommand: manta.sh
requirements:
  InlineJavascriptRequirement: {}
inputs:
  input_bams:
    type:
      type: array
      items: File
      inputBinding:
        prefix: -b
        separate: false
    secondaryFiles:
      - .bai
    inputBinding:
      position: 1
  ref_fasta:
    type: File
    inputBinding:
      prefix: -f
      separate: false
      position: 2
    secondaryFiles:
      - .fai
outputs:
  result:
    type: File
    outputBinding:
      glob: result.zip
  variants:
    type: File
    outputBinding:
      glob: variants.vcf.gz
      
hints:
  - dockerPull: cgap/cgap-manta:v1
    class: DockerRequirement
class: CommandLineTool
