import os
import random
from unittest.mock import call, Mock, mock_open, patch

import gzip
import pytest

from .. import sv_cgap_annotations as cgap_annotations


# Test constants
GENE = "BRCA"
CONSEQUENCES = cgap_annotations.VEP_CONSEQUENCE_JOIN.join(
    [
        cgap_annotations.VEP_CONSEQUENCE_ABLATION,
        cgap_annotations.VEP_CONSEQUENCE_AMPLIFICATION,
    ]
)
EXONS = "1-2/10"
INTRONS = "1/9"
CANONICAL = cgap_annotations.VEP_CANONICAL_TRUE
BIOTYPE = cgap_annotations.VEP_BIOTYPE_PROTEIN_CODING
WORST_CONSEQUENCE = cgap_annotations.VEP_CONSEQUENCE_ABLATION
VARIANT_LOCATIONS = (
    cgap_annotations.CGAP_LOCATION_UPSTREAM,
    cgap_annotations.CGAP_LOCATION_DOWNSTREAM,
)
SIMPLE_ANNOTATION_ORDER = [  # Annotation order for simple_transcript result
    cgap_annotations.VEP_GENE,
    cgap_annotations.VEP_CONSEQUENCE,
    cgap_annotations.VEP_EXON,
    cgap_annotations.VEP_INTRON,
    cgap_annotations.VEP_CANONICAL,
    cgap_annotations.VEP_BIOTYPE,
]
EXTENDED_ANNOTATION_ORDER = SIMPLE_ANNOTATION_ORDER + cgap_annotations.CGAP_NEW_FIELDS
SIMPLE_VEP_HEADER = (
    "##INFO<ID="
    + cgap_annotations.VEP_TAG
    + ',Description="Something with Format: '
    + cgap_annotations.VEP_TRANSCRIPT_SPLIT.join(SIMPLE_ANNOTATION_ORDER)
    + '">'
)
EXTENDED_VEP_HEADER = (
    "##INFO<ID="
    + cgap_annotations.VEP_TAG
    + ',Description="Something with Format: '
    + cgap_annotations.VEP_TRANSCRIPT_SPLIT.join(EXTENDED_ANNOTATION_ORDER)
    + '">'
)
VCF_COLUMNS = "\t".join(
    ["#CHROM", "POS", "REF", "ALT", "QUAL", "FILTER", "INFO", "FORMAT", "Sample1234"]
)
# Path below assumes tests run from sv/scripts
INPUT_VCF_PATH = "test/files/cgap_annotations_input.vcf.gz"
OUTPUT_VCF_PATH = "cgap_annotations_output.vcf"
EXPECTED_OUTPUT_VCF_PATH = "test/files/cgap_annotations_output.vcf.gz"


# Functions utilized by tests
def simple_transcript(
    gene=GENE,
    consequences=CONSEQUENCES,
    exons=EXONS,
    introns=INTRONS,
    canonical=CANONICAL,
    biotype=BIOTYPE,
    most_severe="",
    variant_5="",
    variant_3="",
    extended=False,
):
    """Generate a simple, VEP-formatted transcript.

    By default, transcript will not contain CGAP annotations. If
    desired, set extended=True and provide the appropriate kwargs.
    """
    transcript = cgap_annotations.VEP_TRANSCRIPT_SPLIT.join(
        [gene, consequences, exons, introns, canonical, biotype]
    )
    if extended:
        new_fields = cgap_annotations.CGAP_NEW_FIELDS
        to_add = ["" for field in new_fields]
        if most_severe:
            term = cgap_annotations.CGAP_MOST_SEVERE
            if term in new_fields:
                idx = new_fields.index(term)
                to_add[idx] = most_severe
        if variant_5:
            term = cgap_annotations.CGAP_VARIANT_5_LOCATION
            if term in new_fields:
                idx = new_fields.index(term)
                to_add[idx] = variant_5
        if variant_3:
            term = cgap_annotations.CGAP_VARIANT_3_LOCATION
            if term in new_fields:
                idx = new_fields.index(term)
                to_add[idx] = variant_3
        if to_add:
            transcript += cgap_annotations.VEP_TRANSCRIPT_SPLIT
            transcript += cgap_annotations.VEP_TRANSCRIPT_SPLIT.join(to_add)
    return transcript


def mock_transcript_vcf_parser(annotation_order=None):
    """Mock out an input VCF file to return VEP annotations used at the
    transcript level.

    Either provide the annotations as kwarg or use default that lacks
    CGAP annotations.

    NOTE: This mock needs to be used a lot because granite's Variant
    class is an inner class on granite's Vcf class, and thus
    inaccessible to be imported.
    """
    vcf_parser = Mock()
    vcf_parser.vep_annotations = SIMPLE_ANNOTATION_ORDER
    if annotation_order:
        vcf_parser.vep_annotations = annotation_order
    return vcf_parser


def choose_consequences(count=2):
    """Pick some consequences at random.

    :return: All consequences chosen, most severe consequence from
        those chosen
    :rtype: tuple(str, str)
    """
    indices_to_choose = []
    while count > 0:
        random_index = random.randint(0, len(cgap_annotations.CONSEQUENCE_ORDER) - 1)
        indices_to_choose.append(random_index)
        count -= 1
    all_consequences = list(cgap_annotations.CONSEQUENCE_ORDER.keys())
    consequences = [all_consequences[idx] for idx in indices_to_choose]
    worst_consequence_index = indices_to_choose.index(min(indices_to_choose))
    worst_consequence = consequences[worst_consequence_index]
    return (
        cgap_annotations.VEP_CONSEQUENCE_JOIN.join(consequences),
        worst_consequence,
    )


def simple_vcf(variants=None):
    """Generate a simple VCF with VEP header, columns, and variants.

    If no variants provided, only one variant from simple_variant()
    will be included.
    """
    headers = [SIMPLE_VEP_HEADER, VCF_COLUMNS]
    if variants is None:
        variants = [simple_variant()]
    return headers + variants


def worst_consequence_transcripts_to_classes(worst_consequences):
    """Transform worst_consequences dict of genes: transcript strings
    to dict of genes: Transcript classes.
    """
    for key, value in worst_consequences.items():
        worst_consequences[key] = cgap_annotations.Transcript(
            value,
            mock_transcript_vcf_parser(annotation_order=EXTENDED_ANNOTATION_ORDER),
        )


def get_vep_header(vcf_parser):
    """Return the VEP header from the VCF parser."""
    header_definitions = vcf_parser.header.definitions.split("\n")
    for line in header_definitions:
        if cgap_annotations.VEP_HEADER in line:
            return line


def update_variant(variant_string):
    """Update variant with all CGAP annotations/filtering."""
    with patch(
        "scripts.sv_cgap_annotations.VCFParser.read_vcf",
        return_value=simple_vcf(variants=[variant_string]),
    ):
        parser = cgap_annotations.VCFParser(None, None)
        variant = list(parser.variants)[0]
        annotator = cgap_annotations.VariantAnnotator(variant, parser)
        annotator.add_cgap_transcript_annotations()
        return annotator.variant.to_string()


def mock_argparse():
    """Mock of argparse to return fixed input/output files."""
    args = Mock(input_vcf=INPUT_VCF_PATH, output_vcf=OUTPUT_VCF_PATH)
    parser = Mock()
    parser.parse_args.return_value = args
    argparse = Mock()
    argparse.ArgumentParser.return_value = parser
    return argparse


class TestTranscript:
    """Test methods of Transcript class"""

    def test_get_annotations(self):
        """Test retrieval of annotations from input VCF."""
        annotation = simple_transcript()
        vcf_parser = mock_transcript_vcf_parser()
        transcript = cgap_annotations.Transcript(annotation, vcf_parser)
        assert transcript.gene == GENE
        assert transcript.consequence == CONSEQUENCES
        assert transcript.exon == EXONS
        assert transcript.intron == INTRONS
        assert transcript.canonical == CANONICAL
        assert transcript.biotype == BIOTYPE

    @pytest.mark.parametrize(
        ("consequences", "worst_consequence"),
        [
            choose_consequences(),
            choose_consequences(count=3),
            choose_consequences(count=4),
            choose_consequences(count=5),
            choose_consequences(count=6),
            choose_consequences(count=7),
            choose_consequences(count=8),
        ],
    )
    def test_transcript_get_worst_consequence(self, consequences, worst_consequence):
        """Test accurate calculation of worst consequence from all
        consequences.

        NOTE: We're choosing consequences at random here and calcuating
        the worst consequence differently in choose_consequences() than
        we do within the class.
        """
        annotation = simple_transcript(consequences=consequences)
        vcf_parser = mock_transcript_vcf_parser()
        transcript = cgap_annotations.Transcript(annotation, vcf_parser)
        assert transcript.worst_consequence == worst_consequence

    @pytest.mark.parametrize(
        "exons,expected",
        [
            (None, (None, None)),
            ("", (None, None)),
            ("1/1", ("1", ["1"])),
            ("1-2/2", ("2", ["1", "2"])),
            ("1-2/10", ("10", ["1", "2"])),
        ],
    )
    def test_split_exons_or_introns(self, exons, expected):
        """Test splitting of exon/intron strings into components."""
        assert (
            cgap_annotations.Transcript.split_exons_or_introns(None, exons) == expected
        )

    @pytest.mark.parametrize(
        "consequences,exons,introns,expected_5_prime,expected_3_prime",
        [
            (
                "",
                "",
                "",
                cgap_annotations.CGAP_LOCATION_INDETERMINATE,
                cgap_annotations.CGAP_LOCATION_INDETERMINATE,
            ),
            (
                cgap_annotations.VEP_CONSEQUENCE_ABLATION,
                "",
                "",
                cgap_annotations.CGAP_LOCATION_UPSTREAM,
                cgap_annotations.CGAP_LOCATION_DOWNSTREAM,
            ),
            (
                cgap_annotations.VEP_CONSEQUENCE_ABLATION,
                "1-2/2",
                "",
                cgap_annotations.CGAP_LOCATION_UPSTREAM,
                cgap_annotations.CGAP_LOCATION_DOWNSTREAM,
            ),
            (
                cgap_annotations.VEP_CONSEQUENCE_ABLATION,
                "",
                "3-4/4",
                cgap_annotations.CGAP_LOCATION_UPSTREAM,
                cgap_annotations.CGAP_LOCATION_DOWNSTREAM,
            ),
            (
                cgap_annotations.VEP_CONSEQUENCE_ABLATION,
                "1-2/2",
                "3-4/4",
                cgap_annotations.CGAP_LOCATION_UPSTREAM,
                cgap_annotations.CGAP_LOCATION_DOWNSTREAM,
            ),
            (
                cgap_annotations.VEP_CONSEQUENCE_AMPLIFICATION,
                "",
                "",
                cgap_annotations.CGAP_LOCATION_UPSTREAM,
                cgap_annotations.CGAP_LOCATION_DOWNSTREAM,
            ),
            (
                cgap_annotations.VEP_CONSEQUENCE_AMPLIFICATION,
                "1-2/2",
                "",
                cgap_annotations.CGAP_LOCATION_UPSTREAM,
                cgap_annotations.CGAP_LOCATION_DOWNSTREAM,
            ),
            (
                cgap_annotations.VEP_CONSEQUENCE_AMPLIFICATION,
                "",
                "3-4/4",
                cgap_annotations.CGAP_LOCATION_UPSTREAM,
                cgap_annotations.CGAP_LOCATION_DOWNSTREAM,
            ),
            (
                cgap_annotations.VEP_CONSEQUENCE_AMPLIFICATION,
                "1-2/2",
                "3-4/4",
                cgap_annotations.CGAP_LOCATION_UPSTREAM,
                cgap_annotations.CGAP_LOCATION_DOWNSTREAM,
            ),
            (
                cgap_annotations.VEP_CONSEQUENCE_DOWNSTREAM,
                "",
                "",
                cgap_annotations.CGAP_LOCATION_DOWNSTREAM,
                cgap_annotations.CGAP_LOCATION_DOWNSTREAM,
            ),
            (
                cgap_annotations.VEP_CONSEQUENCE_DOWNSTREAM,
                "1-2/2",
                "",
                cgap_annotations.CGAP_LOCATION_DOWNSTREAM,
                cgap_annotations.CGAP_LOCATION_DOWNSTREAM,
            ),
            (
                cgap_annotations.VEP_CONSEQUENCE_DOWNSTREAM,
                "",
                "3-4/4",
                cgap_annotations.CGAP_LOCATION_DOWNSTREAM,
                cgap_annotations.CGAP_LOCATION_DOWNSTREAM,
            ),
            (
                cgap_annotations.VEP_CONSEQUENCE_DOWNSTREAM,
                "1-2/2",
                "3-4/4",
                cgap_annotations.CGAP_LOCATION_DOWNSTREAM,
                cgap_annotations.CGAP_LOCATION_DOWNSTREAM,
            ),
            (
                cgap_annotations.VEP_CONSEQUENCE_UPSTREAM,
                "",
                "",
                cgap_annotations.CGAP_LOCATION_UPSTREAM,
                cgap_annotations.CGAP_LOCATION_UPSTREAM,
            ),
            (
                cgap_annotations.VEP_CONSEQUENCE_UPSTREAM,
                "1-2/2",
                "",
                cgap_annotations.CGAP_LOCATION_UPSTREAM,
                cgap_annotations.CGAP_LOCATION_UPSTREAM,
            ),
            (
                cgap_annotations.VEP_CONSEQUENCE_UPSTREAM,
                "",
                "3-4/4",
                cgap_annotations.CGAP_LOCATION_UPSTREAM,
                cgap_annotations.CGAP_LOCATION_UPSTREAM,
            ),
            (
                cgap_annotations.VEP_CONSEQUENCE_UPSTREAM,
                "1-2/2",
                "3-4/4",
                cgap_annotations.CGAP_LOCATION_UPSTREAM,
                cgap_annotations.CGAP_LOCATION_UPSTREAM,
            ),
            (
                cgap_annotations.VEP_CONSEQUENCE_JOIN.join(
                    [
                        cgap_annotations.VEP_CONSEQUENCE_5_UTR,
                        cgap_annotations.VEP_CONSEQUENCE_3_UTR,
                    ]
                ),
                "",
                "",
                cgap_annotations.CGAP_LOCATION_UPSTREAM_UTR_5,
                cgap_annotations.CGAP_LOCATION_UTR_3_DOWNSTREAM,
            ),
            (
                cgap_annotations.VEP_CONSEQUENCE_JOIN.join(
                    [
                        cgap_annotations.VEP_CONSEQUENCE_5_UTR,
                        cgap_annotations.VEP_CONSEQUENCE_3_UTR,
                    ]
                ),
                "1-2/2",
                "",
                cgap_annotations.CGAP_LOCATION_UPSTREAM_UTR_5,
                cgap_annotations.CGAP_LOCATION_UTR_3_DOWNSTREAM,
            ),
            (
                cgap_annotations.VEP_CONSEQUENCE_JOIN.join(
                    [
                        cgap_annotations.VEP_CONSEQUENCE_5_UTR,
                        cgap_annotations.VEP_CONSEQUENCE_3_UTR,
                    ]
                ),
                "",
                "3-4/4",
                cgap_annotations.CGAP_LOCATION_UPSTREAM_UTR_5,
                cgap_annotations.CGAP_LOCATION_UTR_3_DOWNSTREAM,
            ),
            (
                cgap_annotations.VEP_CONSEQUENCE_JOIN.join(
                    [
                        cgap_annotations.VEP_CONSEQUENCE_5_UTR,
                        cgap_annotations.VEP_CONSEQUENCE_3_UTR,
                    ]
                ),
                "1-2/2",
                "3-4/4",
                cgap_annotations.CGAP_LOCATION_UPSTREAM_UTR_5,
                cgap_annotations.CGAP_LOCATION_UTR_3_DOWNSTREAM,
            ),
            (
                cgap_annotations.VEP_CONSEQUENCE_CODING_VARIANT,
                "1-2/2",
                "",
                cgap_annotations.CGAP_LOCATION_EXONIC,
                cgap_annotations.CGAP_LOCATION_EXONIC,
            ),
            (
                cgap_annotations.VEP_CONSEQUENCE_CODING_VARIANT,
                "1/1",
                "",
                cgap_annotations.CGAP_LOCATION_EXONIC,
                cgap_annotations.CGAP_LOCATION_EXONIC,
            ),
            (
                cgap_annotations.VEP_CONSEQUENCE_INTRON_VARIANT,
                "",
                "3-4/4",
                cgap_annotations.CGAP_LOCATION_INTRONIC,
                cgap_annotations.CGAP_LOCATION_INTRONIC,
            ),
            (
                cgap_annotations.VEP_CONSEQUENCE_JOIN.join(
                    [
                        cgap_annotations.VEP_CONSEQUENCE_CODING_VARIANT,
                        cgap_annotations.VEP_CONSEQUENCE_INTRON_VARIANT,
                    ]
                ),
                "1-2/2",
                "1/1",
                cgap_annotations.CGAP_LOCATION_EXONIC,
                cgap_annotations.CGAP_LOCATION_EXONIC,
            ),
            (
                cgap_annotations.VEP_CONSEQUENCE_JOIN.join(
                    [
                        cgap_annotations.VEP_CONSEQUENCE_CODING_VARIANT,
                        cgap_annotations.VEP_CONSEQUENCE_INTRON_VARIANT,
                    ]
                ),
                "2/2",
                "1/1",
                cgap_annotations.CGAP_LOCATION_INTRONIC,
                cgap_annotations.CGAP_LOCATION_EXONIC,
            ),
            (
                cgap_annotations.VEP_CONSEQUENCE_JOIN.join(
                    [
                        cgap_annotations.VEP_CONSEQUENCE_CODING_VARIANT,
                        cgap_annotations.VEP_CONSEQUENCE_INTRON_VARIANT,
                    ]
                ),
                "3/4",
                "3/3",
                cgap_annotations.CGAP_LOCATION_EXONIC,
                cgap_annotations.CGAP_LOCATION_INTRONIC,
            ),
            (
                cgap_annotations.VEP_CONSEQUENCE_JOIN.join(
                    [
                        cgap_annotations.VEP_CONSEQUENCE_CODING_VARIANT,
                        cgap_annotations.VEP_CONSEQUENCE_INTRON_VARIANT,
                    ]
                ),
                "3/5",
                "2-3/4",
                cgap_annotations.CGAP_LOCATION_INTRONIC,
                cgap_annotations.CGAP_LOCATION_INTRONIC,
            ),
            (
                cgap_annotations.VEP_CONSEQUENCE_5_UTR,
                "1-3/5",
                "",
                cgap_annotations.CGAP_LOCATION_UPSTREAM_UTR_5,
                cgap_annotations.CGAP_LOCATION_UTR_5,
            ),
            (
                cgap_annotations.VEP_CONSEQUENCE_3_UTR,
                "3-5/5",
                "",
                cgap_annotations.CGAP_LOCATION_UTR_3,
                cgap_annotations.CGAP_LOCATION_UTR_3_DOWNSTREAM,
            ),
        ],
    )
    def test_get_variant_locations(
        self, consequences, exons, introns, expected_5_prime, expected_3_prime
    ):
        """Test accurate calculation of variant breakpoint locations
        relative to a transcript.

        Also, test that the locations are accurately updated within the
        transcript annotation dict.
        """
        annotation = simple_transcript(
            consequences=consequences, exons=exons, introns=introns, extended=True
        )
        annotation_order = EXTENDED_ANNOTATION_ORDER
        vcf_parser = mock_transcript_vcf_parser(annotation_order=annotation_order)
        transcript = cgap_annotations.Transcript(annotation, vcf_parser)
        expected_result = (expected_5_prime, expected_3_prime)
        assert transcript.get_variant_locations() == expected_result
        assert (
            transcript.annotations.get(cgap_annotations.CGAP_VARIANT_5_LOCATION)
            == expected_5_prime
        )
        assert (
            transcript.annotations.get(cgap_annotations.CGAP_VARIANT_3_LOCATION)
            == expected_3_prime
        )

    def test_write_annotation(self):
        """Test conversion of transcript annotations dict to
        VEP-formatted string.

        In this case, we aren't doing anything to the transcript, so
        we expect to get out exactly what we put in.
        """
        annotation = simple_transcript()
        vcf_parser = mock_transcript_vcf_parser()
        transcript = cgap_annotations.Transcript(annotation, vcf_parser)
        assert transcript.write_annotation() == annotation


def simple_variant(transcripts=None):
    """Create a simple variant string as it'd come in from VCF.

    If no list of transcripts provided, only transcript will come from
    simple_transcript() result.
    """
    if transcripts is None:
        transcripts = [simple_transcript()]
    chromosome = "1"
    position = "1000"
    identifier = "SimpleSV"
    reference = "A"
    alternate = "<DUP>"
    quality = "100"
    filters = "PASS"
    information = (
        cgap_annotations.VEP_TAG
        + "="
        + cgap_annotations.VEP_TRANSCRIPT_JOIN.join(transcripts)
    )
    variant = "\t".join(
        [
            chromosome,
            position,
            identifier,
            reference,
            alternate,
            quality,
            filters,
            information,
        ]
    )
    return variant


class TestVariantAnnotator:
    """Test methods of VariantAnnotator class."""

    @pytest.mark.parametrize(
        "biotype,expected",
        [
            ("", False),
            ("some_biotype", False),
            (cgap_annotations.VEP_BIOTYPE_PROTEIN_CODING, True),
            (cgap_annotations.VEP_BIOTYPE_MIRNA, True),
            (cgap_annotations.VEP_BIOTYPE_POLYMORPHIC_PSEUDOGENE, True),
        ],
    )
    def test_validate_transcript(self, biotype, expected):
        """Test transcript validation on transcript biotype."""
        transcript = cgap_annotations.Transcript(
            simple_transcript(biotype=biotype), mock_transcript_vcf_parser()
        )
        assert (
            cgap_annotations.VariantAnnotator.validate_transcript(None, transcript)
            == expected
        )

    @pytest.mark.parametrize(
        "transcripts,expected_transcripts",
        [
            ([simple_transcript()], [simple_transcript(extended=True)]),
            (
                [simple_transcript(biotype=cgap_annotations.VEP_BIOTYPE_MIRNA)],
                [
                    simple_transcript(
                        biotype=cgap_annotations.VEP_BIOTYPE_MIRNA, extended=True
                    )
                ],
            ),
            (
                [
                    simple_transcript(
                        biotype=cgap_annotations.VEP_BIOTYPE_POLYMORPHIC_PSEUDOGENE
                    )
                ],
                [
                    simple_transcript(
                        biotype=cgap_annotations.VEP_BIOTYPE_POLYMORPHIC_PSEUDOGENE,
                        extended=True,
                    )
                ],
            ),
            (
                [simple_transcript(), simple_transcript(biotype="foo")],
                [simple_transcript(extended=True)],
            ),
            (
                [simple_transcript(gene="BRCA2"), simple_transcript()],
                [
                    simple_transcript(gene="BRCA2", extended=True),
                    simple_transcript(extended=True),
                ],
            ),
        ],
    )
    def test_get_transcripts(self, transcripts, expected_transcripts):
        """Test retrieval and filtering of transcripts from a (mocked)
        VCF.
        """
        variant_string = simple_variant(transcripts=transcripts)
        vcf = simple_vcf([variant_string])
        expected = [
            cgap_annotations.Transcript(
                transcript,
                mock_transcript_vcf_parser(annotation_order=EXTENDED_ANNOTATION_ORDER),
            )
            for transcript in expected_transcripts
        ]
        with patch("scripts.sv_cgap_annotations.VCFParser.read_vcf", return_value=vcf):
            parser = cgap_annotations.VCFParser(None, None)
            variant = list(parser.variants)[0]
            annotator = cgap_annotations.VariantAnnotator(variant, parser)
            variant_transcripts = annotator.transcripts
            assert len(variant_transcripts) == len(expected)
            for idx, transcript in enumerate(variant_transcripts):
                assert transcript.annotations == expected[idx].annotations

    @pytest.mark.parametrize(
        "transcripts,expected",
        [
            (
                [simple_transcript(gene="GeneA")],
                {"GeneA": simple_transcript(gene="GeneA", extended=True)},
            ),
            (
                [simple_transcript(gene="GeneA"), simple_transcript(gene="GeneB")],
                {
                    "GeneA": simple_transcript(gene="GeneA", extended=True),
                    "GeneB": simple_transcript(gene="GeneB", extended=True),
                },
            ),
            (
                [simple_transcript(gene="GeneA"), simple_transcript(gene="GeneA")],
                {"GeneA": simple_transcript(gene="GeneA", extended=True)},
            ),
            (
                [
                    simple_transcript(
                        gene="GeneA",
                        consequences=cgap_annotations.VEP_CONSEQUENCE_ABLATION,
                    ),
                    simple_transcript(
                        gene="GeneA",
                        consequences=cgap_annotations.VEP_CONSEQUENCE_5_UTR,
                    ),
                ],
                {
                    "GeneA": simple_transcript(
                        gene="GeneA",
                        consequences=cgap_annotations.VEP_CONSEQUENCE_ABLATION,
                        extended=True,
                    )
                },
            ),
            (
                [
                    simple_transcript(
                        gene="GeneA",
                        consequences=cgap_annotations.VEP_CONSEQUENCE_5_UTR,
                    ),
                    simple_transcript(
                        gene="GeneA",
                        consequences=cgap_annotations.VEP_CONSEQUENCE_ABLATION,
                    ),
                ],
                {
                    "GeneA": simple_transcript(
                        gene="GeneA",
                        consequences=cgap_annotations.VEP_CONSEQUENCE_ABLATION,
                        extended=True,
                    )
                },
            ),
            (
                [
                    simple_transcript(
                        gene="GeneA",
                        consequences=cgap_annotations.VEP_CONSEQUENCE_ABLATION,
                    ),
                    simple_transcript(
                        gene="GeneA",
                        consequences=cgap_annotations.VEP_CONSEQUENCE_5_UTR,
                        canonical="",
                    ),
                ],
                {
                    "GeneA": simple_transcript(
                        gene="GeneA",
                        consequences=cgap_annotations.VEP_CONSEQUENCE_ABLATION,
                        extended=True,
                    )
                },
            ),
            (
                [
                    simple_transcript(
                        gene="GeneA",
                        consequences=cgap_annotations.VEP_CONSEQUENCE_5_UTR,
                    ),
                    simple_transcript(
                        gene="GeneA",
                        consequences=cgap_annotations.VEP_CONSEQUENCE_5_UTR,
                        canonical="",
                    ),
                ],
                {
                    "GeneA": simple_transcript(
                        gene="GeneA",
                        consequences=cgap_annotations.VEP_CONSEQUENCE_5_UTR,
                        extended=True,
                    )
                },
            ),
            (
                [
                    simple_transcript(
                        gene="GeneA",
                        consequences=cgap_annotations.VEP_CONSEQUENCE_5_UTR,
                        canonical="",
                    ),
                    simple_transcript(
                        gene="GeneA",
                        consequences=cgap_annotations.VEP_CONSEQUENCE_5_UTR,
                    ),
                ],
                {
                    "GeneA": simple_transcript(
                        gene="GeneA",
                        consequences=cgap_annotations.VEP_CONSEQUENCE_5_UTR,
                        extended=True,
                    )
                },
            ),
            (
                [
                    simple_transcript(
                        gene="GeneA",
                        consequences=cgap_annotations.VEP_CONSEQUENCE_5_UTR,
                        canonical="",
                    ),
                    simple_transcript(
                        gene="GeneA",
                        consequences=cgap_annotations.VEP_CONSEQUENCE_5_UTR,
                        biotype="foo",
                    ),
                ],
                {
                    "GeneA": simple_transcript(
                        gene="GeneA",
                        consequences=cgap_annotations.VEP_CONSEQUENCE_5_UTR,
                        canonical="",
                        extended=True,
                    )
                },
            ),
        ],
    )
    def test_update_gene_worst_consequence(self, transcripts, expected):
        """Test for calculation of worst consequence per gene across
        all genes in the variant's transcripts.

        The ordering of the consequences is declared in the
        CONSEQUENCE_ORDER constant of the module. If altered, the
        expected consequences here also need to be updated.

        We also ensure transcripts that should be filtered out don't
        make it into the consequence dict here.
        """
        variant_string = simple_variant(transcripts=transcripts)
        worst_consequence_transcripts_to_classes(expected)
        with patch(
            "scripts.sv_cgap_annotations.VCFParser.read_vcf",
            return_value=simple_vcf(variants=[variant_string]),
        ):
            parser = cgap_annotations.VCFParser(None, None)
            variant = list(parser.variants)[0]
            annotator = cgap_annotations.VariantAnnotator(variant, parser)
            for transcript in annotator.transcripts:
                annotator.update_gene_worst_consequence(transcript)
            assert len(annotator.gene_worst_consequence) == len(expected)
            for key, value in annotator.gene_worst_consequence.items():
                assert key in expected
                assert value.write_annotation() == expected[key].write_annotation()

    @pytest.mark.parametrize(
        "transcripts,expected_most_severe_idx",
        [
            ([simple_transcript()], [0]),
            ([simple_transcript(), simple_transcript(canonical="")], [0]),
            ([simple_transcript(canonical=""), simple_transcript()], [1]),
            (
                [
                    simple_transcript(canonical=""),
                    simple_transcript(canonical="", exons="1/1"),
                ],
                [0],
            ),
            (
                [
                    simple_transcript(
                        consequences=cgap_annotations.VEP_CONSEQUENCE_5_UTR
                    ),
                    simple_transcript(
                        consequences=cgap_annotations.VEP_CONSEQUENCE_ABLATION
                    ),
                ],
                [1],
            ),
            (
                [
                    simple_transcript(
                        consequences=cgap_annotations.VEP_CONSEQUENCE_5_UTR
                    ),
                    simple_transcript(
                        gene="BRCA2",
                        consequences=cgap_annotations.VEP_CONSEQUENCE_ABLATION,
                    ),
                ],
                [0, 1],
            ),
        ],
    )
    def test_add_worst_consequence_annotations(
        self, transcripts, expected_most_severe_idx
    ):
        """Test correct annotation of transcripts that are expected
        to contain the most severe consequence for their gene.

        If choosing between transcripts for same gene with same
        consequences, choose canonical if it exists; otherwise, take
        the first transcript.

        NOTE: Consequence severity calculated via
        VariantAnnotator.update_gene_worst_consequence() here, so
        test is dependent upon that method.
        """
        variant_string = simple_variant(transcripts=transcripts)
        with patch(
            "scripts.sv_cgap_annotations.VCFParser.read_vcf",
            return_value=simple_vcf(variants=[variant_string]),
        ):
            parser = cgap_annotations.VCFParser(None, None)
            variant = list(parser.variants)[0]
            annotator = cgap_annotations.VariantAnnotator(variant, parser)
            for transcript in annotator.transcripts:
                annotator.update_gene_worst_consequence(transcript)
            annotator.add_worst_consequence_annotations()
            for idx, transcript in enumerate(annotator.transcripts):
                most_severe = transcript.annotations[cgap_annotations.CGAP_MOST_SEVERE]
                if idx in expected_most_severe_idx:
                    assert most_severe == cgap_annotations.CGAP_MOST_SEVERE_TRUE
                else:
                    assert most_severe == ""

    @pytest.mark.parametrize(
        "transcripts,expected_transcripts",
        [
            ([simple_transcript()], [simple_transcript(extended=True)]),
            (
                [simple_transcript(), simple_transcript(gene="BRCA2")],
                [
                    simple_transcript(extended=True),
                    simple_transcript(gene="BRCA2", extended=True),
                ],
            ),
        ],
    )
    def test_update_variant_vep_annotation(self, transcripts, expected_transcripts):
        """Test successful replacement of variant VEP annotation in
        INFO field with updated version containing fields for new CGAP
        annotations.
        """
        variant_string = simple_variant(transcripts=transcripts)
        with patch(
            "scripts.sv_cgap_annotations.VCFParser.read_vcf",
            return_value=simple_vcf(variants=[variant_string]),
        ):
            parser = cgap_annotations.VCFParser(None, None)
            expected = cgap_annotations.VEP_TRANSCRIPT_JOIN.join(
                [
                    cgap_annotations.Transcript(x, parser).write_annotation()
                    for x in expected_transcripts
                ]
            )
            variant = list(parser.variants)[0]
            assert variant.get_tag_value(cgap_annotations.VEP_TAG) != expected
            annotator = cgap_annotations.VariantAnnotator(variant, parser)
            annotator.update_variant_vep_annotation()
            variant_transcripts = variant.get_tag_value(cgap_annotations.VEP_TAG)
            assert variant_transcripts == expected

    @pytest.mark.parametrize(
        "tag_name,tag_value,expected",
        [
            ("CSQ", [], "CSQ="),
            ("CSQ", ["foo|bar"], "CSQ=foo|bar"),
            ("CSQ", ["foo|bar", "fu|bur"], "CSQ=foo|bar,fu|bur"),
        ],
    )
    def test_create_tag_definition(self, tag_name, tag_value, expected):
        """Test for creation of VCF INFO tag in correct format."""
        assert (
            cgap_annotations.VariantAnnotator.create_tag_definition(
                None, tag_name, tag_value
            )
            == expected
        )


class TestVCFParser:
    """Test methods of VCFParser class."""

    def test_get_vep_annotations(self):
        """Test collection of VEP annotations from existing (mocked)
        VCF and addition of expected new CGAP annotations.
        """
        with patch(
            "scripts.sv_cgap_annotations.VCFParser.read_vcf",
            return_value=simple_vcf(),
        ):
            parser = cgap_annotations.VCFParser(None, None)
            vep_annotations = parser.get_vep_annotations()
            assert vep_annotations == EXTENDED_ANNOTATION_ORDER

    def test_update_vep_header(self):
        """Test update of VEP header in (mocked) VCF with new CGAP
        annotation fields.
        """
        with patch(
            "scripts.sv_cgap_annotations.VCFParser.read_vcf",
            return_value=simple_vcf(),
        ):
            parser = cgap_annotations.VCFParser(None, None)
            original_header = get_vep_header(parser)
            parser.update_vep_header()
            new_header = get_vep_header(parser)
            assert original_header != new_header
            assert new_header == EXTENDED_VEP_HEADER

    @pytest.mark.parametrize(
        "variants,expected",
        [
            ([simple_variant()], [update_variant(simple_variant())]),
            ([simple_variant(transcripts=[simple_transcript(biotype="foo")])], []),
            (
                [
                    simple_variant(),
                    simple_variant(transcripts=[simple_transcript(biotype="foo")]),
                ],
                [update_variant(simple_variant())],
            ),
        ],
    )
    def test_add_cgap_annotations(self, variants, expected):
        """Test update of variants with new annotations and filtering
        of variants based on presence of transcripts.

        Variants with no transcripts should be filtered out.

        If annotations are added/removed, modify update_variant()
        function to produce correct expected output here.

        NOTE: Header is updated within this function but tested
        separately.
        """
        with patch(
            "scripts.sv_cgap_annotations.VCFParser.read_vcf",
            return_value=simple_vcf(variants=variants),
        ):
            parser = cgap_annotations.VCFParser(None, None)
            assert not parser.variants_to_write
            parser.add_cgap_annotations()
            assert parser.variants_to_write == expected

    @pytest.mark.parametrize(
        "variants",
        [
            [simple_variant()],
            [
                simple_variant(),
                simple_variant(transcripts=simple_transcript(gene="BRCA2")),
            ],
        ],
    )
    @patch("builtins.open", new_callable=mock_open)
    def test_write_output_file(self, mock_file, variants):
        """Test writing of output VCF.

        Variants in output are expected to be identical to those of
        input to prevent dependence on other methods of class passing.
        """
        fake_file_path = "/foo/bar"
        with patch(
            "scripts.sv_cgap_annotations.VCFParser.read_vcf",
            return_value=simple_vcf(variants=variants),
        ):
            parser = cgap_annotations.VCFParser(None, fake_file_path)
            parser.variants_to_write = variants
            parser.write_output_file()
            variants = parser.variants_to_write
            variant_calls = [call(x) for x in variants]
            mock_file.assert_called_once_with(fake_file_path, "w+")
            mock_file_write = mock_file().write
            assert mock_file_write.call_count == 2 + len(variants)
            mock_file_write.assert_has_calls(
                [call(SIMPLE_VEP_HEADER + "\n"), call(VCF_COLUMNS + "\n")]
                + variant_calls
            )


@patch("scripts.sv_cgap_annotations.argparse", new=mock_argparse())
def test_main():
    """Integrated test running main script with actual inputs/outputs.

    Output files are tested for existence/accuracy and then deleted.
    """
    cgap_annotations.main()
    assert os.path.exists(OUTPUT_VCF_PATH + ".gz")
    assert os.path.exists(OUTPUT_VCF_PATH + ".gz.tbi")
    with gzip.open(OUTPUT_VCF_PATH + ".gz") as output:
        with gzip.open(EXPECTED_OUTPUT_VCF_PATH) as expected:
            output_lines = output.readlines()
            expected_lines = expected.readlines()
    assert output_lines == expected_lines
    os.remove(OUTPUT_VCF_PATH + ".gz")
    os.remove(OUTPUT_VCF_PATH + ".gz.tbi")
