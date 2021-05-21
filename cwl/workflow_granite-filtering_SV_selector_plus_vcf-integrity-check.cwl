cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}

inputs:
  - id: input_vcf
    type: File
    doc: expect the path to the vcf file

  - id: genes
    type: File
    doc: expect the path to the tsv file with list of genes to apply

  - id: VEPsep
    type: string
    default: null
    doc: VEP separator to use for subfields

  - id: VEPtag
    type: string
    default: null
    doc: VEP tag to use

  - id: outputfile-genes
    type: string
    default: "output-genes.vcf"
    doc: name of the output file

  - id: outputfile-CLI
    type: string
    default: "output-CLI.vcf"
    doc: name of the output file

  - id: outputfile-VEP-SpAI
    type: string
    default: "output-VEP-SpAI.vcf"
    doc: name of the output file

  - id: outputfile-VEP-SpAI_clean
    type: string
    default: "output-VEP-SpAI_clean.vcf"
    doc: name of the output file

  - id: outputfile-BL
    type: string
    default: "output-BL.vcf"
    doc: name of the output file

  - id: CLINVARonly
    type: string[]
    default: ["Pathogenic", "risk_factor"]
    doc: only terms and keywords to be saved for CLINVAR

  - id: SpliceAI
    type: float
    default: 0.2
    doc: threshold to whitelist variants by SpliceAI value

  - id: VEPrescue
    type: string[]
    default: ["splice_region_variant"]
    doc: terms to overrule removed flags and/or to rescue and whitelist variants

  - id: VEPremove
    type: string[]
    default: null
    doc: additional terms to be removed

  - id: BEDfile
    type: File
    default: null
    doc: expect the path to bed file with positions to whitelist

  - id: bigfile
    type: File
    default: null
    doc: expect the path to big file with positions set for blacklist

  - id: aftag
    type: string
    default: "gnomADg_AF"
    doc: TAG to be used to filter by population allele frequency

  - id: afthr
    type: float
    default: 0.01
    doc: threshold to filter by population allele frequency

  - id: float_null
    type: float
    default: null
    doc: null float argument

  - id: boolean_true
    type: boolean
    default: true
    doc: true boolean argument

  - id: boolean_null
    type: boolean
    default: null
    doc: null boolean argument

  - id: str_array_null
    type: string[]
    default: null
    doc: null string array argument

  - id: file_null
    type: File
    default: null
    doc: null file argument

  - id: string_null
    type: string
    default: null
    doc: null string argument

outputs:
  merged_vcf:
    type: File
    outputSource: merge-sort-vcf/output

  merged_vcf-check:
    type: File
    outputSource: integrity-check/output

steps:
  granite-geneList:
    run: granite-geneList.cwl
    in:
      input:
        source: input_vcf
      outputfile:
        source: outputfile-genes
      genes:
        source: genes
      VEPtag:
        source: VEPtag
    out: [output]

  granite-whiteList-CLI:
    run: granite-whiteList.cwl
    in:
      input:
        source: granite-geneList/output
      outputfile:
        source: outputfile-CLI
      CLINVAR:
        source: boolean_true
      CLINVARonly:
        source: CLINVARonly
      SpliceAI:
        source: float_null
      VEP:
        source: boolean_null
      VEPrescue:
        source: str_array_null
      VEPremove:
        source: str_array_null
      BEDfile:
        source: BEDfile
      VEPsep:
        source: string_null
      VEPtag:
        source: string_null
    out: [output]

  granite-whiteList-VEP-SpAI:
    run: granite-whiteList.cwl
    in:
      input:
        source: granite-geneList/output
      outputfile:
        source: outputfile-VEP-SpAI
      CLINVAR:
        source: boolean_null
      CLINVARonly:
        source: str_array_null
      SpliceAI:
        source: SpliceAI
      VEP:
        source: boolean_true
      VEPrescue:
        source: VEPrescue
      VEPremove:
        source: VEPremove
      BEDfile:
        source: file_null
      VEPsep:
        source: VEPsep
      VEPtag:
        source: VEPtag
    out: [output]

  granite-cleanVCF:
    run: granite-cleanVCF.cwl
    in:
      input_vcf:
        source: granite-whiteList-VEP-SpAI/output
      outputfile:
        source: outputfile-VEP-SpAI_clean
      SpliceAI:
        source: SpliceAI
      VEP:
        source: boolean_true
      VEPrescue:
        source: VEPrescue
      VEPremove:
        source: VEPremove
      VEPsep:
        source: VEPsep
      VEPtag:
        source: VEPtag
      filter_VEP:
        source: boolean_true
    out: [output]

  granite-blackList:
    run: granite-blackList.cwl
    in:
      input:
        source: granite-cleanVCF/output
      outputfile:
        source: outputfile-BL
      bigfile:
        source: bigfile
      aftag:
        source: aftag
      afthr:
        source: afthr
    out: [output]

  merge-sort-vcf:
    run: merge-sort-vcf.cwl
    in:
      input_vcf_1:
        source: granite-whiteList-CLI/output
      input_vcf_2:
        source: granite-blackList/output
    out: [output]

  integrity-check:
    run: vcf-integrity-check.cwl
    in:
      input:
        source: merge-sort-vcf/output
    out: [output]

doc: |
  run granite geneList |
  run granite whiteList CLINVAR |
  run granite whiteList VEP-SpAI with cleanVCF, run blackList |
  run merge-sort-vcf.sh to merge and sort the two vcf files |
  run an integrity check on the output vcf
