#!/usr/bin/env bash

# Create normalization configuration file and run BICSeq2 normalization
# Writes to directory $OUTDIR, file/sample name is defined by a $PREFIX derived from the .seq file names provided by the input archive file/directory $SEQ

# Usage:
#   norm.sh -s SEQ -c CHRLIST -a FASTA -m MAPPABILITY -b BINSIZE -p PERC -l RLEN -f FSIZEFILE -o OUTDIR -t THREADS

printHelpAndExit() {
    echo "Usage: ${0##*/} -s seq -c chrlist -f fasta -i faidx -m mappability -n nomchr -b binsize -p perc -l rlen -f fsize -o outdir"
    echo "-s seq : path to seq files. It can be either a folder pointing to the files or a tar.gz archive. The name of seq files must have the following structure '{prefix}_{chromosome}.seq' with all the same 'prefix' name"
    echo "-c chrlist : newline-separated list of chromosomes, e.g., 'chr1'"
    echo "-a fasta : path fasta file"
    echo "-m mappability : path to mappability file. It can be either a folder pointing to the files or a tar.gz archive. The name of mappability files must have the following structure '{chromosome}_{suffix}' with all the same 'suffix' name"
    echo "-b binsize : size of the bins (default=100)"
    echo "-p perc : a subsample percentage (default=0.0002)"
    echo "-l rlen : read length (default=150). NOTE: the read length must be smaller than the fragment size"
    echo "-f fsizefile : path to picard CollectInsertSizeMetrics file" # the mean fragment size is used to have a reasonable window to estimate the GC content
    echo "-o outdir : output directory"
    echo "-t threads : number of threads for parallelization (default 1)"
    exit "$1"
}

while getopts ":s:c:a:m:b:p:l:f:o:t:" opt
do
    case "$opt" in
        s ) seq="$OPTARG" ;;
        c ) chrlist="$OPTARG" ;;
        a ) fasta="$OPTARG" ;;
        m ) mappability="$OPTARG" ;;
        b ) binsize="$OPTARG" ;;
        p ) perc="$OPTARG" ;;
        l ) rlen="$OPTARG" ;;
        f ) fsizefile="$OPTARG" ;;
        o ) outdir="$OPTARG" ;;
        t ) threads="$OPTARG" ;;
        ? ) printHelpAndExit ;; # Print helpFunction in case parameter is non-existent
    esac
done

# Print helpFunction in case parameters are empty
if [ -z "$seq" ] || [ -z "$chrlist" ] || [ -z "$fasta" ] || [ -z "$mappability" ] || [ -z "$binsize" ] || [ -z "$perc" ] || [ -z "$rlen" ] || [ -z "$fsizefile" ] || [ -z "$outdir" ] || [ -z "$threads" ]
then
    echo "Some or all of the parameters are empty";
    printHelpAndExit
fi

# Get fragment size and check that it is reasonable. Fragment size must be larger than read length.
fsize=$(grep -A1 -m1 -P 'MEDIAN_INSERT_SIZE\tMODE_INSERT_SIZE' $fsizefile | tail -n 1 | awk '{print $1}')
if (($fsize > 150)); then echo "Fragment size is greater than 150 bp"; else echo "ERROR: fragment size is less than 150 bp. Exiting..."; exit 1; fi; if (($fsize < 1500)); then echo "Fragment size is less than 1500 bp"; else echo "ERROR: fragment size is greater than 1500 bp. Exiting ..."; exit 1; fi

# make temporary output directories

mkdir -p $outdir || exit 1
mkdir -p $outdir/tmp || exit 1
mkdir -p $outdir/tmp/mappability || exit 1

# decompress seq files from map step into temp directory
tar -xzf $seq -C $outdir/tmp || exit 1
echo "Seq files copied"

# derive the prefix to be used as file name from the .seq files, assuming that the name structure is '{prefix}_{chromosome}.seq'

flist=(`ls $outdir/tmp/*.seq`) || exit 1
nompath=${flist[0]/%\.seq} || exit 1
nomfile=`basename $nompath` || exit 1
prefix=`echo $nomfile | rev | cut -d"_" -f2-  | rev` || exit 1

# symbolic links for reference fasta and index

ln -s $fasta $outdir/tmp/${prefix}_fasta.fa || exit 1
ln -s ${fasta}.fai $outdir/tmp/${prefix}_faidx.fa.fai || exit 1
echo "Fasta files linked"

# add mappability files to the temporary directory

if [[ $mappability == *tar.gz ]]
then
    tar -xzf $mappability -C $outdir/tmp/mappability || exit 1
else
    cp $mappability/* $outdir/tmp/mappability || exit 1
    rm -r $mappability || exit 1
fi
echo "Mappability files copied"

nompath=(`ls $outdir/tmp/mappability/*`) || exit 1
nomfile=`basename $nompath` || exit 1
suffix=`echo $nomfile | cut -d "_" -f2` || exit 1

# split fasta file for chromosomes of interest
echo "Beginning chromosome split from fasta reference genome"
cat $chrlist | xargs -P $threads -i bash -c "samtools faidx $outdir/tmp/${prefix}_fasta.fa {} > $outdir/tmp/${prefix}_fasta_{}.fa" || exit 1
echo "Completed chromsome split from fasta reference genome"

# prepare the configuration file
echo "Preparing the configuration file"
NORM_CONFIG="$outdir/tmp/${prefix}.norm-config.txt" || exit 1

printf "chromName\tfaFile\tMapFile\treadPosFile\tbinFileNorm\n" > $NORM_CONFIG
while read CHR; do
    faFile=$outdir/tmp/${prefix}_fasta_${CHR}.fa || exit 1
    if [ ! -z "$nomchr" ];then
        MapFile=$outdir/tmp/mappability/${nomchr}${CHR}_${suffix} || exit 1
    else
        MapFile=$outdir/tmp/mappability/${CHR}_${suffix} || exit 1
    fi
    readPosFile=$outdir/tmp/${prefix}_${CHR}.seq || exit 1
    binFile=$outdir/${prefix}_${CHR}.bin || exit 1
    printf "$CHR\t$faFile\t$MapFile\t$readPosFile\t$binFile\n" >> $NORM_CONFIG || exit 1
done<$chrlist
echo "Configuration file complete"

echo "Starting BIC-Seq2 Norm"
BICseq2-norm.pl -p $perc -b $binsize -l $rlen -s $fsize --tmp $outdir/tmp $NORM_CONFIG $outdir/${prefix}_bin.prm || exit 1
echo "BIC-Seq2 Norm completed"

# make tar.gz archive of bin files to pass to seg.sh
cd $outdir || exit 1
tar -czvf ${outdir}_BinFilesBICseq2.tar.gz ${prefix}*bin* || exit 1
mv ${outdir}_BinFilesBICseq2.tar.gz ../ || exit 1
