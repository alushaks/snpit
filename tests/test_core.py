import vcf
from pathlib import Path
from collections import Counter, defaultdict
from snpit.genotype import Genotype
from snpit.lineage import Lineage
from snpit.core import load_lineages_from_csv, SnpIt


def get_record(record_type):
    v = vcf.Reader(open("test_cases/test.vcf"))
    records = [record for record in v]

    if record_type == "ref":
        idx = 1
    elif record_type == "alt":
        idx = 0
    elif record_type == "null":
        idx = 3
    elif record_type == "het":
        idx = 2
    else:
        return None
    return records[idx]


def create_test_snpit():
    positions = [2, 5, 8, 11, 14, 16, 20]
    names = [
        [("L1", "A")],
        [("L2", "C")],
        [("L1", "A"), ("L4", "C")],
        [("L2", "T"), ("L3", "G")],
        [("L3", "A")],
        [("L4", "G")],
        [("L1", "C"), ("L3", "T"), ("L4", "G")],
    ]
    lineages = {
        "L1": Lineage(name="L1", species="S1", lineage="Lin1", sublineage="SL1"),
        "L2": Lineage(name="L2", species="S2", lineage="Lin2", sublineage="SL2"),
        "L3": Lineage(name="L3", species="S3", lineage="Lin3", sublineage="SL3"),
        "L4": Lineage(name="L4", species="S4", lineage="Lin4", sublineage="SL4"),
    }
    position_map = dict()

    for i in range(len(positions)):
        position_map[positions[i]] = {}
        for name, variant in names[i]:
            if variant not in position_map[positions[i]]:
                position_map[positions[i]][variant] = [name]
            else:
                position_map[positions[i]][variant].append(name)

    snpit = SnpIt(threshold=10)
    snpit.lineages = lineages
    snpit.lineage_positions = position_map
    return snpit


def test_getSampleGenotypedVariant_refCallReturnsNone():
    record = get_record("ref")
    genotype = Genotype("0")

    actual = SnpIt.get_variant_for_genotype_in_vcf_record(genotype, record)
    expected = None

    assert actual == expected


def test_getSampleGenotypedVariant_altCallReturnsVariant():
    record = get_record("alt")
    genotype = Genotype("1")

    actual = SnpIt.get_variant_for_genotype_in_vcf_record(genotype, record)
    expected = "A"

    assert actual == expected


def test_getSampleGenotypedVariant_nullCallReturnsHyphen():
    record = get_record("null")
    genotype = Genotype(".")

    actual = SnpIt.get_variant_for_genotype_in_vcf_record(genotype, record)
    expected = "-"

    assert actual == expected


def test_getSampleGenotypedVariant_hetCallReturnsNone():
    record = get_record("het")
    genotype = Genotype("0", "1")

    actual = SnpIt.get_variant_for_genotype_in_vcf_record(genotype, record)
    expected = None

    assert actual == expected


def test_loadLineagesFromCsv_emptyFileReturnsEmptyDict():
    filepath = Path("test_cases/empty.csv")

    actual = load_lineages_from_csv(filepath)
    expected = dict()

    assert actual == expected


def test_loadLineagesFromCsv_fileWithTwoEntriesReturnsDictWithTwoLineages():
    filepath = Path("test_cases/test_library.csv")

    actual = load_lineages_from_csv(filepath)

    assert len(actual) == 731
    assert actual[115_499] == {
        Lineage(
            name="indo-oceanic",
            species="M. tuberculosis",
            lineage="Lineage 1",
            sublineage="Sublineage 7",
        ): "G"
    }
    assert actual[1_288_698] == {
        Lineage(
            name="beijing",
            species="M. tuberculosis",
            lineage="Lineage 2",
            sublineage="",
        ): "A"
    }


def test_classifyVcf_exampleVcfReturnsCorrectClassification():
    snpit = SnpIt(10, True)

    actual = snpit.classify_vcf("../example/example.vcf")
    expected = {
        "example": (
            97.368_421_052_631_58,
            Lineage(lineage="Lineage 2", species="M. tuberculosis", name="beijing"),
        )
    }

    assert actual == expected


def test_countLineageClassificationsForSamplesInVcf_ignoreFilterIgnoreStatus():
    snpit = create_test_snpit()
    snpit.ignore_filter = True
    snpit.ignore_status = True
    vcf_path = Path("test_cases/multisample_test.vcf")

    actual = snpit.count_lineage_classifications_for_samples_in_vcf(vcf_path)
    expected = defaultdict()
    expected["Sample1"] = Counter(["L4", "L3", "L3"])
    expected["Sample2"] = Counter(["L1", "L1", "L1", "L2", "L3", "L3"])

    assert actual == expected

def test_countLineageClassificationsForSamplesInVcf_notIgnoreFilterIgnoreStatus():
    snpit = create_test_snpit()
    snpit.ignore_filter = False
    snpit.ignore_status = True
    vcf_path = Path("test_cases/multisample_test.vcf")

    actual = snpit.count_lineage_classifications_for_samples_in_vcf(vcf_path)
    expected = defaultdict()
    expected["Sample1"] = Counter(["L3", "L3"])
    expected["Sample2"] = Counter(["L1", "L2", "L3"])

    assert actual == expected

def test_countLineageClassificationsForSamplesInVcf_ignoreFilterNotIgnoreStatus():
    snpit = create_test_snpit()
    snpit.ignore_filter = True
    snpit.ignore_status = False
    vcf_path = Path("test_cases/multisample_test.vcf")

    actual = snpit.count_lineage_classifications_for_samples_in_vcf(vcf_path)
    expected = defaultdict()
    expected["Sample1"] = Counter(["L4", "L3", "L3"])
    expected["Sample2"] = Counter(["L1", "L2", "L3", "L3"])

    assert actual == expected

def test_countLineageClassificationsForSamplesInVcf_notIgnoreFilterNotIgnoreStatus():
    snpit = create_test_snpit()
    snpit.ignore_filter = False
    snpit.ignore_status = False
    vcf_path = Path("test_cases/multisample_test.vcf")

    actual = snpit.count_lineage_classifications_for_samples_in_vcf(vcf_path)
    expected = defaultdict()
    expected["Sample1"] = Counter(["L3", "L3"])
    expected["Sample2"] = Counter(["L2", "L3"])

    assert actual == expected