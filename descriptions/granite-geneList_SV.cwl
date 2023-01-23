#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement

hints:
  - class: DockerRequirement
    dockerPull: ACCOUNT/sv_germline_granite:VERSION

baseCommand: [granite, geneList]

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

  - id: genes
    type: File
    inputBinding:
      prefix: -g
    doc: expect the path to the tsv file with list of genes to apply

  - id: VEPtag
    type: string
    default: null
    inputBinding:
      prefix: --VEPtag
    doc: VEP tag to use

outputs:
  - id: output
    type: File
    outputBinding:
      glob: $(inputs.outputfile)

doc: |
  run granite geneList
