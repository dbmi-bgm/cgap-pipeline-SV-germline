#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement

hints:
  - class: DockerRequirement
    dockerPull: cgap/cnv:v2

baseCommand: [granite, SVqcVCF]

inputs:
  - id: input_vcf
    type: File
    inputBinding:
      prefix: -i
    doc: expect the path to the vcf gz file

  - id: outputfile
    type: string
    default: "output.json"
    inputBinding:
      prefix: -o
    doc: name of the output file

  - id: samples
    type: string[]
    inputBinding:
      prefix: --samples
    doc: samples to collect metrics for

outputs:
  - id: qc_json
    type: File
    outputBinding:
      glob: $(inputs.outputfile)

doc: |
  run granite SVqcVCF
