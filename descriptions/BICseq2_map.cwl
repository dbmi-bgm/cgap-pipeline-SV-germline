#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement

hints:
  - class: DockerRequirement
    dockerPull: ACCOUNT/cnv_germline:VERSION

baseCommand: [map.sh]

inputs:
  - id: bam
    type: File
    inputBinding:
      prefix: -b
    secondaryFiles:
      - .bai
    doc: expect the path to the input bam

  - id: prefisso
    type: string
    inputBinding:
      prefix: -p
    doc: expect string for pre-fix on sample file name

  - id: chrlist
    type: File
    inputBinding:
      prefix: -c
    doc: expect the path to newline-separated list of chromosomes to analyze

  - id: mapq
    type: int
    inputBinding:
      prefix: -m
    doc: expect minimum acceptable MAPQ integer for read filtering

  - id: length
    type: int
    inputBinding:
      prefix: -l
    doc: expect minimum acceptable read length integer for read filtering

  - id: threads
    type: int
    inputBinding:
      prefix: -t
    doc: expect integer for thread count

outputs:
  - id: output
    type: File
    outputBinding:
      glob: $(inputs.prefisso)_SeqFilesBICseq2.tar.gz

  - id: fsizefile
    type: File
    outputBinding:
      glob: insert_size_metrics.txt

doc: |
  run map.sh on a bam file to filter reads and generate seq files and fragment size files for BIC-seq2 norm
