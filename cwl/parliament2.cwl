#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

baseCommand: parliament2_tibanna.sh

requirements:
  InlineJavascriptRequirement: {}

hints:
  - dockerPull: aveit/parliament2:v1
    class: DockerRequirement

inputs:
  illumina_bam:
    type: File
    inputBinding:
      position: 1
    secondaryFiles:
      - .bai
  ref_fasta:
    type: File
    inputBinding:
      position: 2
    secondaryFiles:
      - .fai
  filter_short_contigs:
    type: string
    inputBinding:
      position: 3
  run_breakdancer:
    type: string
    inputBinding:
      position: 4
  run_breakseq:
    type: string
    inputBinding:
      position: 5
  run_manta:
    type: string
    inputBinding:
      position: 6
  run_cnvnator:
    type: string
    inputBinding:
      position: 7
  run_lumpy:
    type: string
    inputBinding:
      position: 8
  run_delly_deletion:
    type: string
    inputBinding:
      position: 9
  run_delly_insertion:
    type: string
    inputBinding:
      position: 10
  run_delly_inversion:
    type: string
    inputBinding:
      position: 11
  run_delly_duplication:
    type: string
    inputBinding:
      position: 12
  run_genotype_candidates:
    type: string
    inputBinding:
      position: 13
  sample_name:
    type: string
    inputBinding:
      position: 14

outputs:
  result:
    type: File
    outputBinding:
      glob: result.zip
  variants:
    type: File
    outputBinding:
      glob: variants.vcf.gz
    secondaryFiles:
      - .tbi


      
