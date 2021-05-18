#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement

hints:
  - class: DockerRequirement
    dockerPull: cgap/cgap:v22

baseCommand: [vep-annot.sh]

inputs:
  - id: input
    type: File
    inputBinding:
      position: 1
    secondaryFiles:
      - .tbi
    doc: expect the path to the vcf gz file

  - id: reference
    type: File
    inputBinding:
      position: 2
    secondaryFiles:
      - ^.dict
      - .fai
    doc: expect the path to the fa reference file

  - id: regions
    type: File
    inputBinding:
      position: 3
    doc: expect the path to the file defining regions

  - id: vep
    type: File
    inputBinding:
      position: 4
    secondaryFiles:
      - ^^^.plugins.tar.gz
    doc: expect the path to the vep tar gz

  - id: clinvar
    type: File
    inputBinding:
      position: 5
    secondaryFiles:
      - .tbi
    doc: expect the path to the vcf gz file with Clinvar annotations

  - id: dbnsfp
    type: File
    inputBinding:
      position: 6
    secondaryFiles:
      - .tbi
      - ^.readme.txt
    doc: expect the path to the vcf gz file with dbNSFP annotations

  - id: maxent
    type: File
    inputBinding:
      position: 7
    doc: expect the path to the fordownload tar gz

  - id: spliceai_snv
    type: File
    inputBinding:
      position: 8
    secondaryFiles:
      - .tbi
    doc: expect the path to the vcf gz file with SpliceAI for SNVs

  - id: spliceai_indel
    type: File
    inputBinding:
      position: 9
    secondaryFiles:
      - .tbi
    doc: expect the path to the vcf gz file with SpliceAI for indels

  - id: gnomad
    type: File
    inputBinding:
      position: 10
    secondaryFiles:
      - .tbi
    doc: expect the path to the vcf gz file with gnomAD v3.1 genome annotations

  - id: gnomad2
    type: File
    inputBinding:
      position: 11
    secondaryFiles:
      - .tbi
    doc: expect the path to the vcf gz file with gnomAD v2.1 exome annotations

  - id: CADD_snv
    type: File
    inputBinding:
      position: 12
    secondaryFiles:
      - .tbi
    doc: expect the path to the tsv gz file with CADD Phred annotations for SNVs

  - id: CADD_indel
    type: File
    inputBinding:
      position: 13
    secondaryFiles:
      - .tbi
    doc: expect the path to the tsv gz file with CADD Phred annotations for indels

  - id: phylop100bw
    type: File
    inputBinding:
      position: 14
    doc: expect the path to the bw file with phyloP 100-way vertebrate conservation scores

  - id: phylop30bw
    type: File
    inputBinding:
      position: 15
    doc: expect the path to the bw file with phyloP 30-way mammalian conservation scores

  - id: phastc100bw
    type: File
    inputBinding:
      position: 16
    doc: expect the path to the bw file with PhastCons 100-way vertebrate conservation scores

  - id: nthreads
    type: int
    inputBinding:
      position: 17
    doc: number of threads used to run parallel

  - id: version
    type: string
    inputBinding:
      position: 18
    doc: vep datasource version

  - id: assembly
    type: string
    inputBinding:
      position: 19
    doc: genome assembly version

outputs:
  - id: output
    type: File
    outputBinding:
      glob: combined.vep.vcf.gz
    secondaryFiles:
      - .tbi

doc: |
  run vep
