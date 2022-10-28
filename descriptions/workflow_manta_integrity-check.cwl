cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}

inputs:
  - id: input_bams
    type:
      -
        type: array
        items: File
    secondaryFiles:
      - .bai
    doc: expect the path to the sample bam files

  - id: ref_fasta
    type: File
    secondaryFiles:
      - .fai
    doc: expect the path to the reference fasta file

  - id: callRegions
    type: File
    secondaryFiles:
      - .tbi
    doc: expect the path to the bed file for callRegions

outputs:
  final_zip:
    type: File
    outputSource: manta/result

  manta_vcf:
    type: File
    outputSource: manta/variants

  vcf-check:
    type: File
    outputSource: integrity-check/output

steps:
  manta:
    run: manta.cwl
    in:
      input_bams:
        source: input_bams
      ref_fasta:
        source: ref_fasta
      callRegions:
        source: callRegions

    out: [result, variants]

  integrity-check:
    run: vcf-integrity-check.cwl
    in:
      input:
        source: manta/variants
    out: [output]

doc: |
  run manta.sh to call variants |
  run an integrity check on the output vcf gz
