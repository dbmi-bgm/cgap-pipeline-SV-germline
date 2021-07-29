#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement

hints:
  - class: DockerRequirement
    dockerPull: cgap/cnv:v1

baseCommand: [python3, /usr/local/bin/SV_length_filter.py]

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

  - id: max_length
    type: int
    inputBinding:
      prefix: -l
    doc: expect int for maximum length (in bp) for an SV to pass filter

outputs:
  - id: output
    type: File
    outputBinding:
      glob: $(inputs.outputfile + ".gz")
    secondaryFiles:
      - .tbi

doc: |
  run SV_length_filter.py to filter VCF for SVs below a given length
