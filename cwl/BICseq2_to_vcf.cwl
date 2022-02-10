#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement

hints:
  - class: DockerRequirement
    dockerPull: ACCOUNT/cnv_germline:VERSION

baseCommand: [python3, /usr/local/bin/bic-seq2_vcf_formatter.py]

inputs:
  - id: vcfheader
    type: File
    inputBinding:
      prefix: -v
    doc: expect path to vcf.gz of SV/CNV vcf header file

  - id: pvalue
    type: float
    inputBinding:
      prefix: -p
    doc: expect float for BIC-seq2 significance p-value

  - id: fastaref
    type: File
    inputBinding:
      prefix: -f
    secondaryFiles:
      - .fai
    doc: expect the path to hg38 fasta file and index

  - id: samplename
    type: string
    inputBinding:
      prefix: -s
    doc: expect string for sample name for vcf header

  - id: inputbicseq2
    type: File
    inputBinding:
      prefix: -i
    doc: expect the path to BIC-seq2 txt file

  - id: log2_min_dup
    type: float
    inputBinding:
      prefix: -d
    doc: expect float for positive value (log2.copyRatio) above which a Duplication is called

  - id: log2_min_hom_dup
    type: float
    inputBinding:
      prefix: -u
    doc: expect float for positive value (log2.copyRatio) above which a homozygous or high copy number Duplication is called

  - id: log2_min_del
    type: float
    inputBinding:
      prefix: -e
    doc: expect float for negative value (log2.copyRatio) below which a Deletion is called (do not provide negative sign)

  - id: log2_min_hom_del
    type: float
    inputBinding:
      prefix: -l
    doc: expect float for negative value (log2.copyRatio) below which a homozygous Deletion is called (do not provide negative sign)

  - id: outputfile
    type: string
    inputBinding:
      prefix: -o
    doc: expect string for name of output vcf file

outputs:
  - id: output
    type: File
    outputBinding:
      glob: $(inputs.outputfile + ".gz")

doc: |
  run bic-seq2_vcf_formatter.py to convert BIC-seq2 output txt to genotyped vcf
