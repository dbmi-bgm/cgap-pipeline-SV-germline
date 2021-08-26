#!/bin/bash

# variables from command line
input_vcf=$1 #'sorted_manta.vcf.gz'
reference=$2 #'GAPFIXRDPDK5.fa'

# data sources
vep_tar_gz=$3 #'GAPFIPK4VGWV.vep.tar.gz'
version=$4 #'101'
assembly=$5 #'GRCh38'

# self variables
directory=VCFS/

tar -xzf $vep_tar_gz
tar -xzf ${vep_tar_gz%%.*}.plugins.tar.gz
tar -xzf $fordownload_tar_gz

# setting up output directory
mkdir -p $directory

# command line VEP

options="--fasta $reference --assembly $assembly --use_given_ref --offline --overlaps --canonical --format vcf --max_sv_size 250000000 --cache_version $version --dir_cache . --force_overwrite --vcf"

command="vep -i $input_vcf -o ${directory}test.vep.vcf $options"

echo "Running VEP"
$command || exit 1

cp ${directory}test.vep.vcf sv_annotated_vep.vcf || exit 1

bgzip sv_annotated_vep.vcf || exit 1
tabix -p vcf sv_annotated_vep.vcf.gz || exit 1
