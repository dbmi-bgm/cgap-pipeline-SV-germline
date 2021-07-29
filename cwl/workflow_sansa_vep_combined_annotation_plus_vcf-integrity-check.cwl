cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}

inputs:
  - id: input_vcf
    type: File
    doc: expect the path to the sample vcf gz file

  - id: gnomAD_SV
    type: File
    secondaryFiles:
      - .tbi
    doc: expect the path to the hg38-vcf-header-contig-fields file

  - id: reference
    type: File
    secondaryFiles:
      - ^.dict
      - .fai
    doc: expect the path to the fa reference file

  - id: vep
    type: File
    secondaryFiles:
      - ^^^.plugins.tar.gz
    doc: expect the path to the vep tar gz

  - id: version
    type: string
    default: "101"
    doc: vep datasource version

  - id: assembly
    type: string
    default: "GRCh38"
    doc: genome assembly version

  - id: outputfile
    type: string
    doc: expect the path to the combined vcf gz file

outputs:
  sorted_vcf:
    type: File
    outputSource: sansa/sorted_vcf

  annotated_SV_vcf:
    type: File
    outputSource: combine_sansa_vep/output

  vcf-check:
    type: File
    outputSource: integrity-check/output

steps:
  sansa:
    run: sansa.cwl
    in:
      input:
        source: input_vcf
      gnomAD_SV:
        source: gnomAD_SV
    out: [output, sorted_vcf]

  vep-annot_SV:
    run: vep-annot_SV.cwl
    in:
      input:
        source: sansa/sorted_vcf
      reference:
        source: reference
      vep:
        source: vep
      version:
        source: version
      assembly:
        source: assembly
    out: [output]

  combine_sansa_vep:
    run: combine_sansa_vep.cwl
    in:
      vep_vcf:
        source: vep-annot_SV/output
      sansa_txt:
        source: sansa/output
      outputfile:
        source: outputfile
    out: [output]

  integrity-check:
    run: vcf-integrity-check.cwl
    in:
      input:
        source: combine_sansa_vep/output
    out: [output]

doc: |
  run sansa.sh to add gnomAD-SV information to variants |
  run vep-annot_SV.sh to annotate SVs with Ensembl transcripts |
  run combine_sansa_and_VEP_vcf.py to combine sansa and vep annotations into single VCF |
  run an integrity check on the output vcf gz
