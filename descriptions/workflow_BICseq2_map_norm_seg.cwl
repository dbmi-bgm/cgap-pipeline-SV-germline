cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}

inputs:
  - id: bam
    type: File
    secondaryFiles:
       - .bai
    doc: expect the path to the input bam

  - id: prefisso
    type: string
    default: "map"
    doc: expect string for pre-fix on sample file name

  - id: chrlist
    type: File
    doc: expect the path to newline-separated list of chromosomes to analyze

  - id: mapq
    type: int
    default: 60
    doc: expect minimum acceptable MAPQ integer for read filtering

  - id: length
    type: int
    default: 145
    doc: expect minimum acceptable read length integer for read filtering

  - id: fasta
    type: File
    secondaryFiles:
      - .fai
    doc: expect the path to hg38 fasta file and index

  - id: mappability
    type: File
    doc: expect the path to the tar.gz archive of mappability files

  - id: binsize
    type: int
    default: 100
    doc: expect integer for bin size

  - id: perc
    type: float
    default: 0.0002
    doc: expect float for subsample percentage

  - id: rlength
    type: int
    default: 150
    doc: expect integer for read length (must be smaller than fragment size)

  - id: outdir
    type: string
    default: "norm"
    doc: expect string for name of output directory (norm)

  - id: lambda
    type: int
    default: 3
    doc: expect int for lambda, the smoothing parameter

  - id: outseg
    type: string
    default: "seg"
    doc: expect string for name of output directory (seg)

  - id: threads
    type: int
    default: 2
    doc: expect integer for thread count

outputs:
  BICseq2_out:
    type: File
    outputSource: BICseq2_seg/output

steps:
  BICseq2_map:
    run: BICseq2_map.cwl
    in:
      bam:
        source: bam
      prefisso:
        source: prefisso
      chrlist:
        source: chrlist
      mapq:
        source: mapq
      length:
        source: length
      threads:
        source: threads
    out: [output, fsizefile]

  BICseq2_norm:
    run: BICseq2_norm.cwl
    in:
      seq:
        source: BICseq2_map/output
      chrlist:
        source: chrlist
      fasta:
        source: fasta
      mappability:
        source: mappability
      binsize:
        source: binsize
      perc:
        source: perc
      rlength:
        source: rlength
      fsizefile:
        source: BICseq2_map/fsizefile
      threads:
        source: threads
      outdir:
        source: outdir
    out: [output]

  BICseq2_seg:
    run: BICseq2_seg.cwl
    in:
      input:
        source: BICseq2_norm/output
      chrlist:
        source: chrlist
      lambda:
        source: lambda
      outseg:
        source: outseg
    out: [output]

doc: |
  run map.sh on a bam file to filter reads and generate seq files and fragment size files for BIC-seq2 norm |
  run BIC-seq2 norm through norm.sh on the seq files generated by map.sh |
  run BIC-seq2 seg through seg.sh on the bin files generated by norm.sh