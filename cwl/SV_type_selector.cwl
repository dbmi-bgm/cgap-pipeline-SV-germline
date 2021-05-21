#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement

hints:
  - class: DockerRequirement
    dockerPull: cgap/cnv:v1

baseCommand: [python3, /usr/local/bin/SV_type_selector.py]

inputs:
  - id: input
    type: File
    inputBinding:
      prefix: -i
    doc: expect the path to the vcf file

  - id: outputfile
    type: string
    default: "output.vcf"
    inputBinding:
      prefix: -o
    doc: name of the output file

  - id: SV_types
    type: string[]
    inputBinding:
      prefix: -s
    doc: list of SVTYPE classes to retain in the final VCF

outputs:
  - id: output
    type: File
    outputBinding:
      glob: $(inputs.outputfile)

doc: |
  run SV_type_selector.py to filter VCF for specific SV classes
