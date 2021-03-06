#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement

hints:
  - class: DockerRequirement
    dockerPull: ACCOUNT/cnv_germline:VERSION

baseCommand: [norm.sh]

inputs:
  - id: seq
    type: File
    inputBinding:
      prefix: -s
    doc: expect the path to tar.gz archive of seq files from map step

  - id: chrlist
    type: File
    inputBinding:
      prefix: -c
    doc: expect the path to newline-separated list of chromosomes to analyze

  - id: fasta
    type: File
    inputBinding:
      prefix: -a
    secondaryFiles:
      - .fai
    doc: expect the path to hg38 fasta file and index

  - id: mappability
    type: File
    inputBinding:
      prefix: -m
    doc: expect the path to the tar.gz archive of mappability files

  - id: binsize
    type: int
    inputBinding:
      prefix: -b
    doc: expect integer for bin size

  - id: perc
    type: float
    inputBinding:
      prefix: -p
    doc: expect float for subsample percentage

  - id: rlength
    type: int
    inputBinding:
      prefix: -l
    doc: expect integer for read length (must be smaller than fragment size)

  - id: fsizefile
    type: File
    inputBinding:
      prefix: -f
    doc: expect the path to the .txt output of picard CollectInsertSizeMetrics

  - id: threads
    type: int
    inputBinding:
      prefix: -t
    doc: expect integer for thread count

  - id: outdir
    type: string
    inputBinding:
      prefix: -o
    doc: expect string for name of output directory

outputs:
  - id: output
    type: File
    outputBinding:
      glob: $(inputs.outdir)_BinFilesBICseq2.tar.gz

doc: |
  run BIC-seq2 norm through norm.sh on the seq files generated by map.sh
