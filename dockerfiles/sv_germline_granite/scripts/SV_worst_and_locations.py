#!/usr/bin/env python3

"""
Update SV VEP annotations and filter SVs for CGAP.

Specifically, this script:
    - Adds a "most severe" annotation per transcript to indicate if the
      transcript has the most severe consequence for its gene across
      all the transcripts on the SV

    - Adds two "variant location" annotations per transcript to
      indicate the location of the variant breakpoints relative to the
      transcript

    - Filters transcripts by biotype and removes variants from the VCF
      if all transcripts have been filtered out.

NOTE: Script only intended to work/tested on deletions/duplications as
of November 2021.

NOTE: If additional transcript biotypes are added to include, update
the variant locations algorithm in Transcript.get_variant_locations()
to handle such biotypes properly.
"""

import argparse
import subprocess

from granite.lib import vcf_parser as granite_parser

EPILOG = __doc__

# VEP constants
VEP_TAG = "CSQ"
VEP_TRANSCRIPT_SPLIT = "|"
VEP_TRANSCRIPT_JOIN = ","
VEP_CONSEQUENCE = "Consequence"
VEP_CONSEQUENCE_JOIN = "&"
VEP_GENE = "Gene"
VEP_EXON = "EXON"
VEP_INTRON = "INTRON"
VEP_EXON_TOTAL_SPLIT = "/"
VEP_EXON_AFFECTED_SPLIT = "-"
VEP_CDNA_POSITION = "cDNA_position"
VEP_CDNA_POSITION_SPLIT = "-"
VEP_CDNA_NONCODING_END = "?"
VEP_CANONICAL = "CANONICAL"
VEP_CANONICAL_TRUE = "YES"
VEP_BIOTYPE = "BIOTYPE"
VEP_BIOTYPE_PROTEIN_CODING = "protein_coding"
VEP_BIOTYPE_MIRNA = "miRNA"
VEP_BIOTYPE_POLYMORPHIC_PSEUDOGENE = "polymorphic_pseudogene"
VEP_CONSEQUENCE_ABLATION = "transcript_ablation"
VEP_CONSEQUENCE_STOP_GAINED = "stop_gained"
VEP_CONSEQUENCE_FRAMESHIFT = "frameshift_variant"
VEP_CONSEQUENCE_STOP_LOST = "stop_lost"
VEP_CONSEQUENCE_START_LOST = "start_lost"
VEP_CONSEQUENCE_AMPLIFICATION = "transcript_amplification"
VEP_CONSEQUENCE_INFRAME_INSERTION = "inframe_insertion"
VEP_CONSEQUENCE_INFRAME_DELETION = "inframe_deletion"
VEP_CONSEQUENCE_PROTEIN_ALTERING = "protein_altering_variant"
VEP_CONSEQUENCE_CODING_VARIANT = "coding_sequence_variant"
VEP_CONSEQUENCE_MATURE_MIRNA = "mature_miRNA_variant"
VEP_CONSEQUENCE_5_UTR = "5_prime_UTR_variant"
VEP_CONSEQUENCE_3_UTR = "3_prime_UTR_variant"
VEP_CONSEQUENCE_INTRON_VARIANT = "intron_variant"
VEP_CONSEQUENCE_UPSTREAM = "upstream_gene_variant"
VEP_CONSEQUENCE_DOWNSTREAM = "downstream_gene_variant"
CONSEQUENCE_ORDER = {
    VEP_CONSEQUENCE_ABLATION: 1,
    "splice_acceptor_variant": 2,
    "splice_donor_variant": 3,
    VEP_CONSEQUENCE_STOP_GAINED: 4,
    VEP_CONSEQUENCE_FRAMESHIFT: 5,
    VEP_CONSEQUENCE_STOP_LOST: 6,
    VEP_CONSEQUENCE_START_LOST: 7,
    VEP_CONSEQUENCE_AMPLIFICATION: 8,
    VEP_CONSEQUENCE_INFRAME_INSERTION: 9,
    VEP_CONSEQUENCE_INFRAME_DELETION: 10,
    "missense_variant": 11,
    VEP_CONSEQUENCE_PROTEIN_ALTERING: 12,
    "splice_region_variant": 13,
    "incomplete_terminal_codon_variant": 14,
    "start_retained_variant": 15,
    "stop_retained_variant": 16,
    "synonymous_variant": 17,
    VEP_CONSEQUENCE_CODING_VARIANT: 18,
    VEP_CONSEQUENCE_MATURE_MIRNA: 19,
    VEP_CONSEQUENCE_5_UTR: 20,
    VEP_CONSEQUENCE_3_UTR: 21,
    "non_coding_transcript_exon_variant": 22,
    VEP_CONSEQUENCE_INTRON_VARIANT: 23,
    "NMD_transcript_variant": 24,
    "non_coding_transcript_variant": 25,
    VEP_CONSEQUENCE_UPSTREAM: 26,
    VEP_CONSEQUENCE_DOWNSTREAM: 27,
    "TFBS_ablation": 28,
    "TFBS_amplification": 29,
    "TF_binding_site_variant": 30,
    "regulatory_region_ablation": 31,
    "regulatory_region_amplification": 32,
    "feature_elongation": 33,
    "regulatory_region_variant": 34,
    "feature_truncation": 35,
    "intergenic_variant": 36,
}

# CGAP New VEP annotations and constants. For locations, attempt to make human readable
# with underscores similar to VEP consequence names.
CGAP_MOST_SEVERE = "Most_severe"
CGAP_MOST_SEVERE_TRUE = "1"
CGAP_VARIANT_5_LOCATION = "Variant_5_prime_location"
CGAP_VARIANT_3_LOCATION = "Variant_3_prime_location"
CGAP_LOCATION_INDETERMINATE = "Indeterminate"
CGAP_LOCATION_UPSTREAM = "Upstream"
CGAP_LOCATION_DOWNSTREAM = "Downstream"
CGAP_LOCATION_INTRONIC = "Intronic"
CGAP_LOCATION_EXONIC = "Exonic"
CGAP_LOCATION_UTR_5 = "5_prime_UTR"
CGAP_LOCATION_UTR_3 = "3_prime_UTR"
CGAP_LOCATION_UPSTREAM_UTR_5 = "Upstream_or_5_prime_UTR"
CGAP_LOCATION_UTR_3_DOWNSTREAM = "3_prime_UTR_or_Downstream"
CGAP_LOCATION_WITHIN_MIRNA = "Within_miRNA"
CGAP_NEW_FIELDS = [CGAP_MOST_SEVERE, CGAP_VARIANT_5_LOCATION, CGAP_VARIANT_3_LOCATION]

# CGAP permitted transcript biotypes
# NOTE: Any transcripts with a biotype not in this list will be removed from the variant
CGAP_BIOTYPES = [
    VEP_BIOTYPE_PROTEIN_CODING,
    VEP_BIOTYPE_MIRNA,
    VEP_BIOTYPE_POLYMORPHIC_PSEUDOGENE,
]

# VCF constants
VEP_HEADER = "ID=" + VEP_TAG
VEP_HEADER_SPLIT_START = "Format: "
VEP_HEADER_SPLIT_END = '">'
VEP_HEADER_FIELDS_SPLIT = "|"


class CGAPTranscriptAnnotationError(Exception):
    """Exception class for this script."""

    pass


class Transcript:
    """Captures transcript features and calculates new properties.

    For a given input transcript string, uses information from the VCF
    parser to capture all incoming transcript annotations. Select
    annotations are set as properties on the class to make more
    accessible.

    Additionally, the worst consequence for the transcript as well as
    the locations of the variant breakpoints relative to the transcript
    are calculated here.

    :param transcript_annotation: A single VEP-formatted transcript
    :type transcript_annotation: str
    :param vcf_parser: A handle for the VCF parser
    :type vcf_parser: class:`VCFParser`
    :var vcf_parser: A handle for the VCF parser
    :vartype vcf_parser: class:`VCFParser`
    :var annotations: Names of transcript annotations matched with
        values for the transcript
    :vartype annotations: dict
    :var gene: Transcript's gene
    :vartype gene: str
    :var consequence: Transcript's consequence(s)
    :vartype consequence: str
    :var exon: Transcript's exon(s)
    :vartype exon: str
    :var intron: Transcript's intron(s)
    :vartype intron: str
    :var canonical: Transcript's canonical status
    :vartype canonical: str
    :var biotype: Transcript's biotype
    :vartype biotype: str
    :var worst_consequence: The highest-ranked consequence of all
        consequences on the transcript
    :vartype worst_consequence: str
    :var variant_locations: The 5' and 3' locations of the variant
        breakpoints relative to the transcript
    :vartype variant_locations: tuple(str, str)
    """

    def __init__(self, transcript_annotation, vcf_parser):
        self.vcf_parser = vcf_parser
        self.gene = None
        self.consequence = None
        self.exon = None
        self.intron = None
        self.cdna_position = None
        self.canonical = None
        self.biotype = None
        self.annotations = self.get_annotations(transcript_annotation)
        if self.biotype in CGAP_BIOTYPES:
            self.worst_consequence = self.get_worst_consequence()
            self.variant_locations = self.get_variant_locations()

    def get_annotations(self, transcript_annotation):
        """Match annotation names from VCF with transcript's values.

        Additionally, set some specific annotations as instance
        attributes for ease of access elsewhere.

        :param transcript_annotation: Raw VEP transcript annotation
        :type transcript_annotation: str
        :raises CGAPTranscriptAnnotationException: Unable to identify required info for
            the transcript
        :return: Key, value pairs of annotation names with
            corresponding transcript fields
        :rtype: dict
        """
        annotations = {}
        transcript_annotations = transcript_annotation.split(VEP_TRANSCRIPT_SPLIT)
        for idx, annotation_field in enumerate(self.vcf_parser.vep_annotations):
            annotations[annotation_field] = transcript_annotations[idx]
        self.gene = annotations.get(VEP_GENE)
        self.consequence = annotations.get(VEP_CONSEQUENCE)
        self.exon = annotations.get(VEP_EXON)
        self.intron = annotations.get(VEP_INTRON)
        self.cdna_position = annotations.get(VEP_CDNA_POSITION)
        self.canonical = annotations.get(VEP_CANONICAL)
        self.biotype = annotations.get(VEP_BIOTYPE)
        if not self.gene or not self.consequence or not self.biotype:
            raise CGAPTranscriptAnnotationError(
                "Could not find an expected, required field on the following"
                " transcript: %s." % transcript_annotation
            )
        return annotations

    def get_worst_consequence(self):
        """Determine worst consequence of transcript's consequences.

        :return: Single worst transcript consequence
        :rtype: str
        """
        worst_consequence = None
        worst_consequence_index = max(CONSEQUENCE_ORDER.values()) + 1
        consequences = self.consequence.split(VEP_CONSEQUENCE_JOIN)
        for consequence in consequences:
            if not consequence:
                continue
            consequence_index = CONSEQUENCE_ORDER[consequence]
            if consequence_index < worst_consequence_index:
                worst_consequence = consequence
                worst_consequence_index = consequence_index
        return worst_consequence

    def split_exons_or_introns(self, exon_or_intron):
        """Parse exon/intron string.

        :return: The total number of exons/introns, the exon(s)/
            intron(s) impacted by the SV
        :rtype: tuple(str, list)
        """
        if not exon_or_intron:
            total = affected = None
        else:
            exon_or_intron = exon_or_intron.split(VEP_EXON_TOTAL_SPLIT)
            total = exon_or_intron[-1]
            affected = exon_or_intron[0].split(VEP_EXON_AFFECTED_SPLIT)
        return total, affected

    def split_cdna_position(self, cdna_position):
        """Parse cDNA position string.

        :return: Start cDNA position, end cDNA position (may be same).
        :rtype: (str, str)
        """
        cdna_position = cdna_position.split(VEP_CDNA_POSITION_SPLIT)
        start_cdna = cdna_position[0]
        end_cdna = cdna_position[-1]
        return start_cdna, end_cdna

    def get_variant_locations(self):
        """Determine SV breakpoint locations relative to transcript.

        A mix of consequence and exon/intron information is utilized,
        but not all transcripts will have determinable results.

        The locations are also added to self.annotations if appropriate.

        If/when biotypes included are updated, this method must also be
        updated appropriately.

        NOTE: Best to test any changes on a number of SV VCFs as quite
        difficult to capture all combinations in tests (and then update
        tests for combinations not handled correctly).

        :return: Variant location at 5' of transcript, variant location
            at 3' of transcript
        :rtype: tuple(str, str)
        """
        consequences = self.consequence
        exons = self.exon
        _, exons_affected = self.split_exons_or_introns(exons)
        introns = self.intron
        _, introns_affected = self.split_exons_or_introns(introns)
        cdna_position = self.cdna_position
        whole_transcript_consequences = [
            VEP_CONSEQUENCE_ABLATION,
            VEP_CONSEQUENCE_AMPLIFICATION,
            VEP_CONSEQUENCE_UPSTREAM,
            VEP_CONSEQUENCE_DOWNSTREAM,
        ]
        coding_region_consequences = [
            #  NOTE: Not all exons coming in on a transcript are coding; this
            #  can only be determined by the presence of a corresponding consequence,
            #  which this list is meant to capture.
            VEP_CONSEQUENCE_CODING_VARIANT,
            VEP_CONSEQUENCE_PROTEIN_ALTERING,
            VEP_CONSEQUENCE_FRAMESHIFT,
            VEP_CONSEQUENCE_INFRAME_INSERTION,
            VEP_CONSEQUENCE_INFRAME_DELETION,
            VEP_CONSEQUENCE_START_LOST,
            VEP_CONSEQUENCE_STOP_LOST,
            VEP_CONSEQUENCE_STOP_GAINED,
        ]
        five_prime_location = three_prime_location = CGAP_LOCATION_INDETERMINATE
        if any(
            consequence in consequences for consequence in whole_transcript_consequences
        ):
            #  No other information required than the consequence here because the
            #  entire transcript is involved.
            if (
                VEP_CONSEQUENCE_ABLATION in consequences
                or VEP_CONSEQUENCE_AMPLIFICATION in consequences
            ):
                five_prime_location = CGAP_LOCATION_UPSTREAM
                three_prime_location = CGAP_LOCATION_DOWNSTREAM
            elif VEP_CONSEQUENCE_UPSTREAM in consequences:
                five_prime_location = three_prime_location = CGAP_LOCATION_UPSTREAM
            else:
                five_prime_location = three_prime_location = CGAP_LOCATION_DOWNSTREAM
        elif (VEP_CONSEQUENCE_MATURE_MIRNA in consequences) and cdna_position:
            #  Handle miRNAs that haven't been entirely affected
            cdna_start, cdna_end = self.split_cdna_position(cdna_position)
            if cdna_start == VEP_CDNA_NONCODING_END:
                five_prime_location = CGAP_LOCATION_UPSTREAM
            else:
                five_prime_location = CGAP_LOCATION_WITHIN_MIRNA
            if cdna_end == VEP_CDNA_NONCODING_END:
                three_prime_location = CGAP_LOCATION_DOWNSTREAM
            else:
                three_prime_location = CGAP_LOCATION_WITHIN_MIRNA
        else:
            #  Only a portion of the transcript has been impacted by the SV, so utilize
            #  the available info to narrow down relative location.
            #  NOTE: As above, not all exons are coding.

            #  5' location determination
            if VEP_CONSEQUENCE_5_UTR in consequences:
                five_prime_location = CGAP_LOCATION_UPSTREAM_UTR_5
            elif (introns and not exons) and (
                VEP_CONSEQUENCE_INTRON_VARIANT in consequences
            ):
                five_prime_location = CGAP_LOCATION_INTRONIC
            elif exons and not introns:
                if any(
                    consequence in consequences
                    for consequence in coding_region_consequences
                ):
                    five_prime_location = CGAP_LOCATION_EXONIC
                elif VEP_CONSEQUENCE_3_UTR in consequences:
                    five_prime_location = CGAP_LOCATION_UTR_3
            elif exons and introns:
                if (int(introns_affected[0]) < int(exons_affected[0])) and (
                    VEP_CONSEQUENCE_INTRON_VARIANT in consequences
                ):
                    five_prime_location = CGAP_LOCATION_INTRONIC
                elif int(exons_affected[0]) <= int(introns_affected[0]):
                    if any(
                        consequence in consequences
                        for consequence in coding_region_consequences
                    ):
                        five_prime_location = CGAP_LOCATION_EXONIC
                    elif VEP_CONSEQUENCE_3_UTR in consequences:
                        five_prime_location = CGAP_LOCATION_UTR_3

            #  3' location determination (~same as 5' but switched accordingly)
            if VEP_CONSEQUENCE_3_UTR in consequences:
                three_prime_location = CGAP_LOCATION_UTR_3_DOWNSTREAM
            elif (introns and not exons) and (
                VEP_CONSEQUENCE_INTRON_VARIANT in consequences
            ):
                three_prime_location = CGAP_LOCATION_INTRONIC
            elif exons and not introns:
                if any(
                    consequence in consequences
                    for consequence in coding_region_consequences
                ):
                    three_prime_location = CGAP_LOCATION_EXONIC
                elif VEP_CONSEQUENCE_5_UTR in consequences:
                    three_prime_location = CGAP_LOCATION_UTR_5
            elif exons and introns:
                if (int(introns_affected[-1]) >= int(exons_affected[-1])) and (
                    VEP_CONSEQUENCE_INTRON_VARIANT in consequences
                ):
                    three_prime_location = CGAP_LOCATION_INTRONIC
                elif int(exons_affected[-1]) > int(introns_affected[-1]):
                    if any(
                        consequence in consequences
                        for consequence in coding_region_consequences
                    ):
                        three_prime_location = CGAP_LOCATION_EXONIC
                    elif VEP_CONSEQUENCE_5_UTR in consequences:
                        three_prime_location = CGAP_LOCATION_UTR_5
        if CGAP_VARIANT_5_LOCATION in self.annotations:
            self.annotations[CGAP_VARIANT_5_LOCATION] = five_prime_location
        if CGAP_VARIANT_3_LOCATION in self.annotations:
            self.annotations[CGAP_VARIANT_3_LOCATION] = three_prime_location
        return five_prime_location, three_prime_location

    def write_annotation(self):
        """Convert transcript annotations to VEP-formatted string.

        NOTE: The annotation order should remain identical to that
        which came into the class due to the ordered dict.

        :return: VEP-formatted transcript
        :rtype: str
        """
        return VEP_TRANSCRIPT_SPLIT.join(self.annotations.values())


class VariantAnnotator:
    """Filters and updates variant's transcripts with new annotations.

    The worst consequence annotations per gene are calculated here
    since information across all transcripts is required.

    :param: variant: A single variant from the VCF
    :type variant: class:`granite.lib.vcf_parser.Vcf.Variant`
    :param: vcf_parser: Parser for the variant's source VCF
    :type vcf_parser: class:`VCFParser`
    :var transcripts: The variant's validated transcripts
    :vartype transcripts: list(str)
    :var gene_worst_consequence: Worst consequences for each gene that
        appears in the variant's transcripts
    :vartype gene_worst_consequence: dict
    """

    def __init__(self, variant, vcf_parser):
        self.variant = variant
        self.vcf_parser = vcf_parser
        self.transcripts = self.get_transcripts()
        self.gene_worst_consequence = {}

    def get_transcripts(self):
        """Collect and validate the variant's transcripts.

        :return: All validated transcripts
        :rtype: list(:class:`Transcript`)
        """
        result = []
        vep_transcripts = self.variant.get_tag_value(VEP_TAG).split(VEP_TRANSCRIPT_JOIN)
        for vep_transcript in vep_transcripts:
            vep_transcript += VEP_TRANSCRIPT_SPLIT * len(CGAP_NEW_FIELDS)
            transcript = Transcript(vep_transcript, self.vcf_parser)
            valid_transcript = self.validate_transcript(transcript)
            if valid_transcript:
                result.append(transcript)
        return result

    def validate_transcript(self, transcript):
        """Run all checks to validate transcript for inclusion.

        This serves as the only transcript filtering step, and while
        quite simple at the moment may become more complicated.

        :return: True if validated, False if not
        :rtype: bool
        """
        result = True
        if transcript.biotype not in CGAP_BIOTYPES:
            result = False
        return result

    def add_cgap_transcript_annotations(self):
        """Add transcript annotations that require more information
        than a single transcript contains.

        Loop once through the transcripts, updating instance attributes
        on the fly since there may be many transcripts here.

        NOTE: Annotations that can be calculated based solely on the
        transcript itself come in via :class:`Transcript`.
        """
        for transcript in self.transcripts:
            self.update_gene_worst_consequence(transcript)
        self.add_worst_consequence_annotations()
        self.update_variant_vep_annotation()

    def update_gene_worst_consequence(self, transcript):
        """Compare transcript's worst consequence to current worst
        consequence for its gene, updating if required.

        Choose the canonical transcript if it contains the worst
        consequence; otherwise, the first transcript seen corresponding
        to the worst consequence is chosen.

        :param transcript: A transcript
        :type transcript: class:`Transcript`
        """
        if transcript.gene not in self.gene_worst_consequence:
            self.gene_worst_consequence[transcript.gene] = transcript
        else:
            gene_worst_consequence = self.gene_worst_consequence[
                transcript.gene
            ].worst_consequence
            gene_consequence_order = CONSEQUENCE_ORDER[gene_worst_consequence]
            transcript_consequence_order = CONSEQUENCE_ORDER[
                transcript.worst_consequence
            ]
            if transcript_consequence_order < gene_consequence_order:
                self.gene_worst_consequence[transcript.gene] = transcript
            elif (
                transcript_consequence_order == gene_consequence_order
                and transcript.canonical == VEP_CANONICAL_TRUE
            ):
                self.gene_worst_consequence[transcript.gene] = transcript

    def add_worst_consequence_annotations(self):
        """Add the most severe annotation to transcripts.

        Needs to be run once all worst consequences have already been
        calculated.
        """
        for transcript in self.gene_worst_consequence.values():
            transcript.annotations[CGAP_MOST_SEVERE] = CGAP_MOST_SEVERE_TRUE

    def update_variant_vep_annotation(self):
        """Replace VEP transcript annotations with updated versions.

        NOTE: CGAP transcript annotations are added on to the existing
        VEP annotations here under the original VEP tag in the
        variant's INFO field.
        """
        vep_transcript_annotation = []
        for transcript in self.transcripts:
            vep_transcript_annotation.append(transcript.write_annotation())
        vep_annotation = self.create_tag_definition(VEP_TAG, vep_transcript_annotation)
        self.variant.remove_tag_info(VEP_TAG)
        if self.variant.INFO:
            self.variant.add_tag_info(vep_annotation)
        else:
            # Small bug in granite vcf_parser: always adds INFO separator (";") to start
            # of INFO field even if unnecessary because empty.
            self.variant.INFO = vep_annotation

    def create_tag_definition(self, tag_name, tag_value, separator=","):
        """Create VCF tag in expected format.

        :return: VCF tag for INFO field
        :rtype: str
        """
        return tag_name + "=" + separator.join(tag_value)


class VCFParser(granite_parser.Vcf):
    """
    Wrapper class for granite's VCF class with additional properties
    and methods useful for adding custom transcript annotations.

    NOTE: Current construction facilitates adding new headers or
    annotations, but deleting annotations will likely require
    refactoring here and in above classes.

    :param vcf_file_in: Existing VCF file path
    :type vcf_file_in: str
    :param vcf_file_out: Output VCF file path
    :type vcf_file_out: str
    :var variants_to_write: Variants to include in output VCF
    :vartype variants_to_write: list(str)
    :var variants: Variants from the existing VCF
    :vartype variants: class:`granite.lib.vcf_parser.Vcf.Variant`
    :var vep_annotations: Existing VCF's VEP transcript annotations
        plus CGAP's custom transcript annotations
    :vartype vep_annotations: list(str)
    """

    def __init__(self, vcf_file_in, vcf_file_out):
        super().__init__(vcf_file_in)
        self.output_vcf = vcf_file_out
        self.variants_to_write = []
        self.variants = self.parse_variants()
        self.vep_annotations = self.get_vep_annotations()

    def get_vep_annotations(self):
        """Collect existing VCF's VEP annotations and add CGAP's.

        :return: All transcript annotations for output VCF
        :rtype: list(str)
        """
        annotations = []
        for line in self.header.definitions.split("\n")[::-1]:  # VEP header ~last
            if VEP_HEADER in line:
                descriptions = line.split(VEP_HEADER_SPLIT_START)[1]
                annotations = descriptions.split(VEP_HEADER_SPLIT_END)[0]
                annotations = annotations.split(VEP_HEADER_FIELDS_SPLIT)
                break
        for field in CGAP_NEW_FIELDS:
            if field not in annotations:
                annotations.append(field)
        return annotations

    def add_cgap_annotations(self):
        """Update variants with new annotations, filter variants, and
        update VEP header.

        The filtering step here is to check if the variant has
        transcripts after the transcripts have been filtered elsewhere.

        If filtering passes, variant (as string to write to VCF) is
        added to self.variants_to_write.
        """
        for variant in self.variants:
            variant_annotator = VariantAnnotator(variant, self)
            if variant_annotator.transcripts:
                variant_annotator.add_cgap_transcript_annotations()
                self.variants_to_write.append(variant_annotator.variant.to_string())
        self.update_vep_header()

    def update_vep_header(self):
        """Update VEP header to include new calculated annotations.

        Only the VEP transcript fields are touched; other parts of
        header should remain identical to as they came in.
        """
        header_definitions = self.header.definitions.split("\n")[::-1]  # VEP ~last
        for idx, line in enumerate(header_definitions):
            if VEP_HEADER in line:
                header_split = line.split(VEP_HEADER_SPLIT_START)
                new_line = (
                    header_split[0]
                    + VEP_HEADER_SPLIT_START
                    + VEP_HEADER_FIELDS_SPLIT.join(self.vep_annotations)
                    + VEP_HEADER_SPLIT_END
                )
                header_definitions[idx] = new_line
                break
        self.header.definitions = "".join(
            [line + "\n" for line in header_definitions[::-1] if line]  # Re-reverse
        )

    def write_output_file(self):
        """Write the output VCF."""
        with open(self.output_vcf, "w+") as file_handle:
            self.write_header(file_handle)
            for variant in self.variants_to_write:
                file_handle.write(variant)


def run(input_vcf, output_vcf):
    """Add CGAP transcript annotations and write the updated VCF.

    :param input_vcf: Existing VCF file path
    :type input_vcf: str
    :param output_vcf: Output VCF file path
    :type output_vcf: str
    """
    vcf_parser = VCFParser(input_vcf, output_vcf)
    vcf_parser.add_cgap_annotations()
    vcf_parser.write_output_file()


def main():
    """Add CGAP transcript annotations when run as script.

    Additionally, compress the output file and create a corresponding
    index file.
    """
    parser = argparse.ArgumentParser(
        description="Add CGAP transcript annotations",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-i",
        "--input-vcf",
        help="VEP-annotated VCF path",
        required=True,
    )
    parser.add_argument(
        "-o", "--output-vcf", help="Output VCF file path", required=True
    )
    args = parser.parse_args()

    run(args.input_vcf, args.output_vcf)

    subprocess.run(["bgzip", args.output_vcf])
    subprocess.run(["tabix", args.output_vcf + ".gz"])


if __name__ == "__main__":
    main()
