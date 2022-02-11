cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}

inputs:
  - id: vcfheader
    type: File
    doc: expect path to vcf.gz of SV/CNV vcf header file

  - id: pvalue
    type: float
    default: 0.05
    doc: expect float for BIC-seq2 significance p-value

  - id: fastaref
    type: File
    secondaryFiles:
      - .fai
    doc: expect the path to hg38 fasta file and index

  - id: samplename
    type: string
    doc: expect string for sample name for vcf header

  - id: inputbicseq2
    type: File
    doc: expect the path to BIC-seq2 txt file

  - id: log2_min_dup
    type: float
    default: 0.2
    doc: expect float for positive value (log2.copyRatio) above which a Duplication is called

  - id: log2_min_hom_dup
    type: float
    default: 0.8
    doc: expect float for positive value (log2.copyRatio) above which a homozygous or high copy number Duplication is called

  - id: log2_min_del
    type: float
    default: 0.2
    doc: expect float for negative value (log2.copyRatio) below which a Deletion is called (do not provide negative sign)

  - id: log2_min_hom_del
    type: float
    default: 3.0
    doc: expect float for negative value (log2.copyRatio) below which a homozygous Deletion is called (do not provide negative sign)

  - id: outputfile
    type: string
    default: "BIC-seq2.vcf"
    doc: expect string for name of output vcf file

outputs:
  BICseq2_CNV_vcf:
    type: File
    outputSource: BICseq2_to_vcf/output

  vcf-check:
    type: File
    outputSource: integrity-check-cnv/output

steps:
  BICseq2_to_vcf:
    run: BICseq2_to_vcf.cwl
    in:
      vcfheader:
        source: vcfheader
      pvalue:
        source: pvalue
      fastaref:
        source: fastaref
      samplename:
        source: samplename
      inputbicseq2:
        source: inputbicseq2
      log2_min_dup:
        source: log2_min_dup
      log2_min_hom_dup:
        source: log2_min_hom_dup
      log2_min_del:
        source: log2_min_del
      log2_min_hom_del:
        source: log2_min_hom_del
      outputfile:
        source: outputfile
    out: [output]

  integrity-check-cnv:
    run: vcf-integrity-check-cnv.cwl
    in:
      input:
        source: BICseq2_to_vcf/output
    out: [output]

doc: |
  run bic-seq2_vcf_formatter.py to convert BIC-seq2 output txt to genotyped vcf |
  run an integrity check on the output vcf gz
