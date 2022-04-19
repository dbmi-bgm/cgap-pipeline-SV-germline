#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement

hints:
  - class: DockerRequirement
    dockerPull: ACCOUNT/sv_germline_granite:VERSION

baseCommand: [python3, /usr/local/bin/SV_worst_and_locations.py]

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

outputs:
  - id: output
    type: File
    outputBinding:
      glob: $(inputs.outputfile + ".gz")
    secondaryFiles:
      - .tbi

doc: |
  run SV_worst_and_locations.py to annotate worst consequence and breakpoint locations
