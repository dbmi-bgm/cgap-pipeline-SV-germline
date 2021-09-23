#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement

hints:
  - class: DockerRequirement
    dockerPull: ACCOUNT/cnv:VERSION

baseCommand: [python3, /usr/local/bin/SV_cytoband.py]

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

  - id: cytoband
    type: File
    inputBinding:
      prefix: -c
    doc: expect the path to the cytoband reference file

outputs:
  - id: output
    type: File
    outputBinding:
      glob: $(inputs.outputfile + ".gz")
    secondaryFiles:
      - .tbi

doc: |
  run SV_cytoband.py to add cytoband annotations for each SV breakpoint
