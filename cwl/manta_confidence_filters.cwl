#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement

hints:
  - class: DockerRequirement
    dockerPull: granite:0.2.0

baseCommand: [python3, /usr/local/bin/SV_manta_filters.py]

inputs:
  - id: input
    type: File
    inputBinding:
      prefix: -i
    doc: expect the path to the sample vcf gz file

  - id: outputfile
    type: string
    inputBinding:
      prefix: -o
    doc: base name of output vcf gz file

outputs:
  - id: output
    type: File
    outputBinding:
      glob: $(inputs.output + ".gz")
    secondaryFiles:
      - .tbi

doc: |
  run SV_manta_filters.py to calculate a confidence class of variants
