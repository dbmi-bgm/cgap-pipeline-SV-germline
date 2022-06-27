#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement

hints:
  - class: DockerRequirement
    dockerPull: ACCOUNT/sv_germline_granite:VERSION

baseCommand: [python3, /usr/local/bin/SV_confidence.py]

arguments: ["--tool", "bicseq2"]
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
      glob: $(inputs.outputfile + ".gz")
    secondaryFiles:
      - .tbi

doc: |
  run SV_confidence.py to infer confidence classes of germline CNVs from BIC-Seq2