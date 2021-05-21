cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}

inputs:
  - id: input_vcf
    type: File
    doc: expect the path to the vcf file

  - id: VEP
    type: boolean
    doc: use VEP annotations to whitelist exonic and functional relevant variants |
         removed by default intron_variant, intergenic_variant, downstream_gene_variant, |
         upstream_gene_variant, regulatory_region_variant

  - id: VEPsep
    type: string
    default: null
    doc: VEP separator to use for subfields

  - id: VEPtag
    type: string
    default: null
    doc: VEP tag to use

  - id: VEPrescue
    type: string[]
    default: ["splice_region_variant"]
    doc: terms to overrule removed flags and/or to rescue and whitelist variants

  - id: aftag
    type: string
    default: "AF"
    doc: TAG to be used to filter by population allele frequency

  - id: afthr
    type: float
    default: 0.01
    doc: threshold to filter by population allele frequency

  - id: SV_types
    type: string[]
    default: ["DEL", "DUP", "INV"]
    doc: list of SVTYPE classes to retain in the final VCF

  - id: outputfile-whiteList_SV
    type: string
    default: "output-whiteList_SV.vcf"
    doc: name of the output file

  - id: outputfile-blackList_SV
    type: string
    default: "output-blackList_SV.vcf"
    doc: name of the output file

  - id: outputfile-SV_type_selector
    type: string
    default: "output-SV_type_selector.vcf"
    doc: name of the output file

outputs:
  vcf:
    type: File
    outputSource: SV_type_selector/output

  vcf-check:
    type: File
    outputSource: integrity-check/output

steps:

  granite-whiteList_SV:
    run: granite-whiteList_SV.cwl
    in:
      input:
        source: input_vcf
      outputfile:
        source: outputfile-whiteList_SV
      VEP:
        source: VEP
      VEPrescue:
        source: VEPrescue
      VEPsep:
        source: VEPsep
      VEPtag:
        source: VEPtag
    out: [output]

  granite-blackList_SV:
    run: granite-blackList_SV.cwl
    in:
      input:
        source: granite-whiteList_SV/output
      outputfile:
        source: outputfile-blackList_SV
      aftag:
        source: aftag
      afthr:
        source: afthr
    out: [output]

  SV_type_selector:
    run: SV_type_selector.cwl
    in:
      input:
        source: granite-blackList_SV/output
      SV_types:
        source: SV_types
      outputfile:
        source: outputfile-SV_type_selector
    out: [output]

  integrity-check:
    run: vcf-integrity-check.cwl
    in:
      input:
        source: SV_type_selector/output
    out: [output]

doc: |
  run granite whiteList SV |
  run granite blackList SV |
  run SV_type_selector |
  run an integrity check on the output vcf
