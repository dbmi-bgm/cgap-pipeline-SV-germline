#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement

hints:
  - class: DockerRequirement
    dockerPull: ACCOUNT/sv_germline:VERSION

baseCommand: [python3, /usr/local/bin/SV_annotation_VCF_cleaner.py]

inputs:
  - id: input
    type: File
    inputBinding:
      prefix: -i
    doc: expect the path to the vcf file

  - id: output
    type: string
    inputBinding:
      prefix: -o
    doc: name of the output file

outputs:
  - id: output
    type: File
    outputBinding:
      glob: $(inputs.output + ".gz")
    secondaryFiles:
      - .tbi

doc: |
  run SV_annotation_VCF_cleaner.py to clean unnecessary data from the VCF for visualization
