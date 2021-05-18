
#uncompress the vcf to allow it to be sorted
bgzip -d -c $1 > temp_vcf

#temp_vcf=${1%.*}

cat temp_vcf | vcf-sort -c > sorted_${1%.*}
rm temp_vcf

bgzip sorted_${1%.*}

vcf=sorted_${1%.*}.gz

tabix $vcf

sansa annotate -m -n -b 50 -r 0.8 -s all -d nstd166.GRCh38.variant_call.vcf.gz $vcf

bcftools query -H -f "%ANNOID\t%ID\t%SVTYPE\t%AN\t%AF\t%AC\t%AFR_AN\t%AFR_AF\t%AFR_AC\t%AMR_AN\t%AMR_AF\t%AMR_AC\t%EAS_AN\t%EAS_AF\t%EAS_AC\t%EUR_AN\t%EUR_AF\t%EUR_AC\t%OTH_AN\t%OTH_AF\t%OTH_AC\n" anno.bcf | sed -e 's/^# //' > anno.tsv

join anno.tsv <(zcat query.tsv.gz | sort -k 1b,1) > results.tsv
