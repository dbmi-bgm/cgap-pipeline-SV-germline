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
  - id: input_vcf
    type: File
    inputBinding:
      prefix: -i
    doc: expect the path to the sample vcf gz file

  - id: output_vcf
    type: string
    default: "output.vcf"
    inputBinding:
      prefix: -o
    doc: base name of output vcf file

outputs:
  - id: confidence_SV_vcf
    type: File
    outputBinding:
      glob: $(inputs.output_vcf + ".gz")
    secondaryFiles:
      - .tbi

doc: |
  run SV_confidence.py to infer confidence classes of germline CNVs from BIC-Seq2