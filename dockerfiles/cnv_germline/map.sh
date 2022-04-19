#!/usr/bin/env bash

# Get the uniquely mapped reads from bam file in parallel runs
# file/sample name is defined by $PREFIX when looping over $CHRLIST, which is newline-separated list of chromosomes passed to samtools, e.g., 'chr1'

# Usage:
#   map.sh -b BAM -p PREFIX -c CHRLIST -m MAPQ -l LENGTH -t THREADS

printHelpAndExit() {
    echo "Usage: ${0##*/} -b bam -p prefix -c chrlist -o outdir"
    echo "-b bam : input bam file"
    echo "-p prefix : sample file name"
    echo "-c chrlist : newline-separated list of chromosomes, e.g., 'chr1'"
    echo "-m mapq : mapq score to filter reads by (default 30)"
    echo "-l length : minimum length for reads (default 145)"
    echo "-t threads : number of threads for parallelization (default 1)"
    exit $1
}

while getopts ":b:p:c:m:l:t:s:" opt
do
    case "$opt" in
        b ) bam="$OPTARG" ;;
        p ) prefix="$OPTARG" ;;
        c ) chrlist="$OPTARG" ;;
        m ) mapq="$OPTARG" ;;
        l ) length="$OPTARG" ;;
        t ) threads="$OPTARG" ;;
        ? ) printHelpAndExit ;; # Print helpFunction in case parameter is non-existent
    esac
done

# Print helpFunction in case parameters are empty
if [ -z "$bam" ] || [ -z "$prefix" ] || [ -z "$chrlist" ] || [ -z "$mapq" ] || [ -z "$length" ] || [ -z "$threads" ]
then
    echo "Some or all of the parameters are empty";
    printHelpAndExit
fi

cat $chrlist | xargs -P $threads -i bash -c "samtools view -b -h $bam {} | samtools view -q $mapq | awk ' length(\$10) >= $length ' | awk '{print \$4}' > ${prefix}_{}.seq" || exit 1

tar -czvf ${prefix}_SeqFilesBICseq2.tar.gz ${prefix}_*.seq || exit 1

# Want to also run picard to estimate fragment size (used as a parameter in norm.sh)
samtools view -h $bam chr22 | picard CollectInsertSizeMetrics I=/dev/stdin O=insert_size_metrics.txt H=insert_size_histogram.pdf || exit 1
