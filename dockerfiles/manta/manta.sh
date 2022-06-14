#!/usr/bin/env bash
# this script is based on components of scripts from the Parliament2 github (https://github.com/dnanexus/parliament2/) including parliament2.sh and runManta

bam_files=()
bai_files=()

while getopts ":f:b:r:" opt; do
  case $opt in
    f) ref_fasta="$OPTARG"
       ref_index="$OPTARG.fai"
    ;;
    b) bam_files+=("$OPTARG")
       bai_files+=("$OPTARG.bai")
    ;;
    r) bed_regions+=("$OPTARG")
       bed_index+=("$OPTARG.tbi")
    ;;
    \?) echo "Invalid option -$OPTARG" >&2
    ;;
  esac
done

prefix="result" #(Optional) If provided, all output files will start with this. If absent, the base of the BAM file name will be used. CWL need to be adjusted

mkdir -p /tmp/output

if [[ ${#bam_files[@]} == 0 ]] || [[ ! -f "${ref_fasta}" ]] || [[ ! -f "${bed_regions}" ]]; then
    echo "ERROR: An invalid (nonexistent) input file has been specified."
    exit 1
fi

for bam_file in "${bam_files[@]}"
do
   if [[ ! -f "${bam_file}" ]]; then
        echo "ERROR: ${bam_file} does not exist."
        exit 1
   fi
done

for bai_file in "${bai_files[@]}"
do
   if [[ ! -f "${bai_file}" ]]; then
        echo "ERROR: ${bai_file} does not exist."
        exit 1
   fi
done

if [[ ! -f "${ref_fasta}" ]]; then
    echo "ERROR: The reference fasta file is missing"
    exit 1
fi

if [[ ! -f "${ref_index}" ]]; then
    echo "ERROR: The reference fasta index file is missing"
    exit 1
fi

if [[ ! -f "${bed_regions}" ]]; then
    echo "ERROR: The bed regions reference file is missing"
    exit 1
fi

if [[ ! -f "${bed_index}" ]]; then
    echo "ERROR: The bed regions index file is missing"
    exit 1
fi


threads="$(nproc)"
threads=$((threads - 1))

wait

mkdir -p /tmp/output/log_files/

echo "Running Manta"

bam_string=

for bam_file in "${bam_files[@]}"
do
   bam_string="$bam_string --bam=$bam_file"
done

mkdir -p /tmp/output/log_files/manta_logs/
python /miniconda/bin/configManta.py --referenceFasta ${ref_fasta} ${bam_string} --runDir manta --callRegions ${bed_regions} || exit 1
python ./manta/runWorkflow.py -m local -j ${threads} 1> /tmp/output/log_files/manta_logs/"${prefix}".manta.stdout.log 2> /tmp/output/log_files/manta_logs/"${prefix}".manta.stderr.log || exit 1 &

wait

mkdir -p /tmp/output/sv_caller_results/

echo "Copying Manta results and converting inversions"
if [[ ! -f manta/results/variants/diploidSV.vcf.gz || ! -f manta/results/stats/alignmentStatsSummary.txt ]]; then
    echo "Manta did not find any variants. Check if it ran correctly. Here are the logs:"
    cat /tmp/output/log_files/manta_logs/"${prefix}".manta.stderr.log
    echo "Exiting"
    exit 1
else
    cp manta/results/variants/diploidSV.vcf.gz /tmp/output/sv_caller_results/"${prefix}".manta.diploidSV.vcf.gz
    mv manta/results/variants/diploidSV.vcf.gz .
    gunzip diploidSV.vcf.gz
    python /miniconda/bin/convertInversion.py /samtools/samtools ${ref_fasta} diploidSV.vcf > diploidSV_inv.vcf || exit 1
    bgzip -c diploidSV_inv.vcf > diploidSV_inv.vcf.gz || exit 1
    cp diploidSV_inv.vcf.gz /tmp/output/sv_caller_results/"${prefix}".manta.diploidSV.convertedInv.vcf.gz
    cp manta/results/stats/alignmentStatsSummary.txt /tmp/output/sv_caller_results/"${prefix}".manta.alignmentStatsSummary.txt
fi

wait



WRITEABLEDIR=`pwd`

cd /tmp/output/log_files/ && find . -type d -empty -delete && find . -maxdepth 1 -mindepth 1 -type d -exec tar czf {}.tar.gz {} --remove-files \;

cd /tmp/output
zip -r result_tmp.zip .
cd $WRITEABLEDIR
cp /tmp/output/result_tmp.zip result.zip
cp /tmp/output/sv_caller_results/"${prefix}".manta.diploidSV.convertedInv.vcf.gz variants.vcf.gz
