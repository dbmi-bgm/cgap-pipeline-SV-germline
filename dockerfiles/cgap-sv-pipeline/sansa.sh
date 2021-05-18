# inputs
inputVCF=$1
gnomAD=$2

# decompress the vcf and sort it
bgzip -d -c $inputVCF > temp_vcf
cat temp_vcf | vcf-sort -c > sorted_${inputVCF%.*}
rm temp_vcf

# bgzip the sorted VCF and Tabix it
bgzip sorted_${inputVCF%.*}
vcf=sorted_${inputVCF%.*}.gz
tabix $vcf

# run sansa to annotate SVs against the gnomAD_SV database
sansa annotate -m -n -b 50 -r 0.8 -s all -d $gnomAD $vcf
bcftools query -H -f "%ANNOID\t%ID\t%SVTYPE\t%AN\t%AF\t%AC\t%AFR_AN\t%AFR_AF\t%AFR_AC\t%AMR_AN\t%AMR_AF\t%AMR_AC\t%EAS_AN\t%EAS_AF\t%EAS_AC\t%EUR_AN\t%EUR_AF\t%EUR_AC\t%OTH_AN\t%OTH_AF\t%OTH_AC\n" anno.bcf | sed -e 's/^# //' > anno.tsv
join anno.tsv <(zcat query.tsv.gz | sort -k 1b,1) > sansa.txt
