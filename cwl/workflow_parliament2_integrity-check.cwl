cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}

inputs:
  - id: input_bam
    type: File
    secondaryFiles:
      - .bai
    doc: expect the path to the sample bam file
  
  - id: input_fasta
    type: File
    secondaryFiles:
      - .fai
    doc: expect the path to the reference fasta file
  
  - id: filter_short_contigs
    type: string
    default: "False"

  - id: run_breakdancer
    type: string
    default: "True"

  - id: run_breakseq
    type: string
    default: "True"

  - id: run_manta
    type: string
    default: "True"

  - id: run_cnvnator
    type: string
    default: "True"

  - id: run_lumpy
    type: string
    default: "True"

  - id: run_delly_deletion
    type: string
    default: "True"

  - id: run_delly_insertion
    type: string
    default: "True"

  - id: run_delly_inversion
    type: string
    default: "True"
  
  - id: run_delly_duplication
    type: string
    default: "True"

  - id: run_genotype_candidates
    type: string
    default: "True"

  - id: sample_name
    type: string
    default: "mySample"

outputs:
  final_zip:
    type: File
    outputSource: parliament2/result

  final_vcf:
    type: File
    outputSource: parliament2/variants
    secondaryFiles:
      - .tbi

  vcf-check:
    type: File
    outputSource: integrity-check/output

steps:
  parliament2:
    run: parliament2.cwl
    in:
      illumina_bam:
        source: input_bam
      ref_fasta:
        source: input_fasta
      filter_short_contigs:
        source: filter_short_contigs
      run_breakdancer:
        source: run_breakdancer
      run_breakseq:
        source: run_breakseq
      run_manta:
        source: run_manta
      run_cnvnator:
        source: run_cnvnator
      run_lumpy:
        source: run_lumpy
      run_delly_deletion:
        source: run_delly_deletion
      run_delly_insertion:
        source: run_delly_insertion
      run_delly_inversion:
        source: run_delly_inversion
      run_delly_duplication:
        source: run_delly_duplication
      run_genotype_candidates:
        source: run_genotype_candidates
      sample_name:
        source: sample_name

    out: [result, variants]

  integrity-check:
    run: vcf-integrity-check-parliament2.cwl
    in:
      input:
        source: parliament2/variants
    out: [output]

doc: |
  run parliament2_tibanna.sh call variants |
  run an integrity check on the output vcf gz
