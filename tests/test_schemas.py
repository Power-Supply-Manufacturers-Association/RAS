"""Validation tests for the RAS schemas.

Run with:   pytest tests/
or:         python3 -m pytest tests/test_schemas.py -v

Covers:
  * every RAS schema parses and passes Draft 2020-12 meta-validation
  * cross-document $refs resolve (RAS + PEAS schemas registered)
  * the canonical examples (resistor, shunt, varistor, thermistor, potentiometer) validate
  * negative cases:
      - top-level oneOf (must have exactly one of
        resistor/varistor/thermistor/potentiometer)
      - a fixed resistor must NOT validate as a potentiometer
      - manufacturerInfo / electrical required
      - per-type required electrical fields
      - additionalProperties: false enforced
      - dimensionWithTolerance shape
      - designRequirements deviceType discriminator
"""

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

REPO = Path(__file__).resolve().parents[1]
SCHEMA_DIR = REPO / "schemas"
EXAMPLES_DIR = REPO / "examples"
PEAS_SCHEMA_DIR = REPO.parent / "PEAS" / "schemas"

RAS_SCHEMA_FILES = [
    "RAS.json",
    "inputs.json",
    "outputs.json",
    "utils.json",
    "resistor.json",
    "varistor.json",
    "thermistor.json",
    "potentiometer.json",
    "inputs/designRequirements.json",
]


def _load(path: Path):
    return json.loads(path.read_text())


@pytest.fixture(scope="session")
def schemas():
    out = {}
    for rel in RAS_SCHEMA_FILES:
        s = _load(SCHEMA_DIR / rel)
        out[s["$id"]] = s
    for path in PEAS_SCHEMA_DIR.rglob("*.json"):
        s = _load(path)
        out[s["$id"]] = s
    return out


@pytest.fixture(scope="session")
def registry(schemas):
    resources = [
        (sid, Resource(contents=s, specification=DRAFT202012))
        for sid, s in schemas.items()
    ]
    return Registry().with_resources(resources)


@pytest.fixture(scope="session")
def ras_validator(schemas, registry):
    return Draft202012Validator(
        schemas["https://psma.com/ras/RAS.json"],
        registry=registry,
    )


@pytest.fixture
def resistor_doc():
    return _load(EXAMPLES_DIR / "01_resistor_crcw0603.json")


@pytest.fixture
def shunt_doc():
    return _load(EXAMPLES_DIR / "02_shunt_resistor_wsk2512.json")


@pytest.fixture
def varistor_doc():
    return _load(EXAMPLES_DIR / "03_varistor_b72214.json")


@pytest.fixture
def thermistor_doc():
    return _load(EXAMPLES_DIR / "04_thermistor_sl22.json")


@pytest.fixture
def potentiometer_doc():
    return _load(EXAMPLES_DIR / "05_potentiometer_3296w_trimmer.json")


@pytest.fixture
def potentiometer_dual_doc():
    return _load(EXAMPLES_DIR / "06_potentiometer_te_citec_dual.json")


@pytest.fixture
def ccr_doc():
    return _load(EXAMPLES_DIR / "07_resistor_te_ccr2_10k.json")


def assert_valid(validator, doc):
    errs = sorted(validator.iter_errors(doc), key=lambda e: list(e.path))
    assert not errs, "expected valid, got errors:\n" + "\n".join(
        f"  - {e.message} @ {list(e.absolute_path)}" for e in errs
    )


def assert_invalid(validator, doc):
    errs = list(validator.iter_errors(doc))
    assert errs, "expected invalid, got no errors"


# ---------------------------------------------------------------------------
# Schema-level tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("rel", RAS_SCHEMA_FILES)
def test_schema_parses(rel):
    _load(SCHEMA_DIR / rel)


@pytest.mark.parametrize("rel", RAS_SCHEMA_FILES)
def test_schema_meta_valid(rel):
    Draft202012Validator.check_schema(_load(SCHEMA_DIR / rel))


# ---------------------------------------------------------------------------
# Positive examples
# ---------------------------------------------------------------------------

def test_resistor_example_validates(ras_validator, resistor_doc):
    assert_valid(ras_validator, resistor_doc)


def test_shunt_example_validates(ras_validator, shunt_doc):
    assert_valid(ras_validator, shunt_doc)


def test_varistor_example_validates(ras_validator, varistor_doc):
    assert_valid(ras_validator, varistor_doc)


def test_thermistor_example_validates(ras_validator, thermistor_doc):
    assert_valid(ras_validator, thermistor_doc)


def test_thermistor_empty_seed_validates(ras_validator, thermistor_doc):
    thermistor_doc["thermistor"] = {}
    assert_valid(ras_validator, thermistor_doc)


def test_potentiometer_example_validates(ras_validator, potentiometer_doc):
    assert_valid(ras_validator, potentiometer_doc)


def test_potentiometer_dual_gang_example_validates(ras_validator, potentiometer_dual_doc):
    assert_valid(ras_validator, potentiometer_dual_doc)


def test_potentiometer_empty_seed_validates(ras_validator, potentiometer_doc):
    potentiometer_doc["potentiometer"] = {}
    assert_valid(ras_validator, potentiometer_doc)


# ---------------------------------------------------------------------------
# Top-level oneOf
# ---------------------------------------------------------------------------

def test_missing_device_field_invalid(ras_validator, resistor_doc):
    del resistor_doc["resistor"]
    assert_invalid(ras_validator, resistor_doc)


def test_two_device_fields_invalid(ras_validator, resistor_doc, varistor_doc):
    resistor_doc["varistor"] = varistor_doc["varistor"]
    assert_invalid(ras_validator, resistor_doc)


def test_unknown_device_field_rejected(ras_validator, resistor_doc):
    # `potentiometer` became a real RAS member in 2026-09; `rheostat` is not one.
    resistor_doc["rheostat"] = resistor_doc.pop("resistor")
    assert_invalid(ras_validator, resistor_doc)


# ---------------------------------------------------------------------------
# Structural requirements
# ---------------------------------------------------------------------------

def test_inputs_required(ras_validator, resistor_doc):
    del resistor_doc["inputs"]
    assert_invalid(ras_validator, resistor_doc)


def test_outputs_must_be_array(ras_validator, resistor_doc):
    resistor_doc["outputs"] = {}
    assert_invalid(ras_validator, resistor_doc)


def test_operating_points_min_one(ras_validator, resistor_doc):
    resistor_doc["inputs"]["operatingPoints"] = []
    assert_invalid(ras_validator, resistor_doc)


# ---------------------------------------------------------------------------
# Per-type schema rules
# ---------------------------------------------------------------------------

def test_manufacturer_info_required(ras_validator, resistor_doc):
    del resistor_doc["resistor"]["manufacturerInfo"]
    assert_invalid(ras_validator, resistor_doc)


def test_datasheet_info_required(ras_validator, resistor_doc):
    del resistor_doc["resistor"]["manufacturerInfo"]["datasheetInfo"]
    assert_invalid(ras_validator, resistor_doc)


def test_resistor_required_electrical_fields(ras_validator, resistor_doc):
    for field in ("resistance", "tolerance", "powerRating"):
        bad = copy.deepcopy(resistor_doc)
        del bad["resistor"]["manufacturerInfo"]["datasheetInfo"]["electrical"][field]
        assert_invalid(ras_validator, bad)


def test_varistor_required_electrical_fields(ras_validator, varistor_doc):
    # energyAbsorption is deliberately NOT here: multilayer/ESD chip varistors
    # publish no Joule rating (see its description in varistor.json).
    for field in ("varistorVoltage", "clampingVoltage", "peakSurgeCurrent"):
        bad = copy.deepcopy(varistor_doc)
        del bad["varistor"]["manufacturerInfo"]["datasheetInfo"]["electrical"][field]
        assert_invalid(ras_validator, bad)


def test_varistor_energy_absorption_optional(ras_validator, varistor_doc):
    ok = copy.deepcopy(varistor_doc)
    del ok["varistor"]["manufacturerInfo"]["datasheetInfo"]["electrical"]["energyAbsorption"]
    assert_valid(ras_validator, ok)


def test_part_no_device_type_property(ras_validator, resistor_doc):
    resistor_doc["resistor"]["manufacturerInfo"]["datasheetInfo"]["part"]["deviceType"] = "resistor"
    assert_invalid(ras_validator, resistor_doc)


def test_resistor_unknown_technology_rejected(ras_validator, resistor_doc):
    resistor_doc["resistor"]["manufacturerInfo"]["datasheetInfo"]["part"]["technology"] = "magicFilm"
    assert_invalid(ras_validator, resistor_doc)


def test_varistor_unknown_technology_rejected(ras_validator, varistor_doc):
    varistor_doc["varistor"]["manufacturerInfo"]["datasheetInfo"]["part"]["technology"] = "thinFilm"
    assert_invalid(ras_validator, varistor_doc)


def test_thermistor_required_electrical_fields(ras_validator, thermistor_doc):
    for field in ("resistanceAt25C",):
        bad = copy.deepcopy(thermistor_doc)
        del bad["thermistor"]["manufacturerInfo"]["datasheetInfo"]["electrical"][field]
        assert_invalid(ras_validator, bad)


def test_thermistor_unknown_technology_rejected(ras_validator, thermistor_doc):
    thermistor_doc["thermistor"]["manufacturerInfo"]["datasheetInfo"]["part"]["technology"] = "metalOxide"
    assert_invalid(ras_validator, thermistor_doc)


def test_thermistor_b_constant_temperatures_pair_enforced(ras_validator, thermistor_doc):
    electrical = thermistor_doc["thermistor"]["manufacturerInfo"]["datasheetInfo"]["electrical"]
    electrical["bConstantTemperatures"] = [25]
    assert_invalid(ras_validator, thermistor_doc)


def test_dimension_with_tolerance_requires_one_field(ras_validator, resistor_doc):
    resistor_doc["resistor"]["manufacturerInfo"]["datasheetInfo"]["electrical"]["resistance"] = {}
    assert_invalid(ras_validator, resistor_doc)


def test_extra_property_rejected(ras_validator, resistor_doc):
    resistor_doc["resistor"]["manufacturerInfo"]["datasheetInfo"]["electrical"]["bogus"] = 1
    assert_invalid(ras_validator, resistor_doc)


def test_derating_curve_amplitude_in_range(ras_validator, resistor_doc):
    resistor_doc["resistor"]["manufacturerInfo"]["datasheetInfo"]["factors"]["powerDerating"]["amplitude"] = [1.5, 0.5]
    resistor_doc["resistor"]["manufacturerInfo"]["datasheetInfo"]["factors"]["powerDerating"]["temperature"] = [25, 100]
    assert_invalid(ras_validator, resistor_doc)


# ---------------------------------------------------------------------------
# designRequirements discriminator
# ---------------------------------------------------------------------------

def test_design_requirements_device_type_required(ras_validator, resistor_doc):
    del resistor_doc["inputs"]["designRequirements"]["deviceType"]
    assert_invalid(ras_validator, resistor_doc)


def test_design_requirements_resistor_requires_resistance(ras_validator, resistor_doc):
    del resistor_doc["inputs"]["designRequirements"]["resistance"]
    assert_invalid(ras_validator, resistor_doc)


def test_design_requirements_varistor_requires_voltage(ras_validator, varistor_doc):
    del varistor_doc["inputs"]["designRequirements"]["ratedContinuousVoltage"]
    assert_invalid(ras_validator, varistor_doc)


def test_design_requirements_thermistor_requires_resistance(ras_validator, thermistor_doc):
    del thermistor_doc["inputs"]["designRequirements"]["resistanceAt25C"]
    assert_invalid(ras_validator, thermistor_doc)


def test_design_requirements_thermistor_unknown_technology_rejected(ras_validator, thermistor_doc):
    thermistor_doc["inputs"]["designRequirements"]["allowedTechnologies"] = ["metalOxide"]
    assert_invalid(ras_validator, thermistor_doc)


def test_design_requirements_unknown_device_type_rejected(ras_validator, resistor_doc):
    resistor_doc["inputs"]["designRequirements"]["deviceType"] = "rheostat"
    assert_invalid(ras_validator, resistor_doc)


# ---------------------------------------------------------------------------
# Potentiometer: the separation from a fixed resistor is the whole point
# ---------------------------------------------------------------------------

def test_fixed_resistor_does_not_validate_as_potentiometer(ras_validator, resistor_doc):
    """The reason potentiometer is its own member.

    A fixed resistor satisfies resistor.electrical's required set
    (resistance, tolerance, powerRating). Re-labelling one as a potentiometer
    must FAIL LOUDLY, not validate silently: potentiometer.electrical has no
    `resistance` property and requires `totalResistance`.
    """
    resistor_doc["potentiometer"] = resistor_doc.pop("resistor")
    resistor_doc["inputs"]["designRequirements"]["deviceType"] = "potentiometer"
    assert_invalid(ras_validator, resistor_doc)


def test_potentiometer_electrical_rejects_plain_resistance(ras_validator, potentiometer_doc):
    electrical = potentiometer_doc["potentiometer"]["manufacturerInfo"]["datasheetInfo"]["electrical"]
    electrical["resistance"] = electrical.pop("totalResistance")
    assert_invalid(ras_validator, potentiometer_doc)


def test_potentiometer_requires_total_resistance(ras_validator, potentiometer_doc):
    del potentiometer_doc["potentiometer"]["manufacturerInfo"]["datasheetInfo"]["electrical"]["totalResistance"]
    assert_invalid(ras_validator, potentiometer_doc)


def test_potentiometer_unknown_technology_rejected(ras_validator, potentiometer_doc):
    potentiometer_doc["potentiometer"]["manufacturerInfo"]["datasheetInfo"]["part"]["technology"] = "metalOxide"
    assert_invalid(ras_validator, potentiometer_doc)


def test_potentiometer_taper_and_turns_optional(ras_validator, potentiometer_doc):
    """Absent on all 106 sourced TE parts today -- the schema must not force them."""
    ds = potentiometer_doc["potentiometer"]["manufacturerInfo"]["datasheetInfo"]
    del ds["electrical"]["taper"]
    del ds["mechanical"]["actuation"]["turns"]
    assert_valid(ras_validator, potentiometer_doc)


def test_potentiometer_taper_requires_law(ras_validator, potentiometer_doc):
    potentiometer_doc["potentiometer"]["manufacturerInfo"]["datasheetInfo"]["electrical"]["taper"] = {}
    assert_invalid(ras_validator, potentiometer_doc)


def test_potentiometer_taper_unknown_law_rejected(ras_validator, potentiometer_doc):
    potentiometer_doc["potentiometer"]["manufacturerInfo"]["datasheetInfo"]["electrical"]["taper"] = {"law": "audio"}
    assert_invalid(ras_validator, potentiometer_doc)


def test_potentiometer_logarithmic_taper_requires_sense(ras_validator, potentiometer_doc):
    electrical = potentiometer_doc["potentiometer"]["manufacturerInfo"]["datasheetInfo"]["electrical"]
    electrical["taper"] = {"law": "logarithmic"}
    assert_invalid(ras_validator, potentiometer_doc)
    electrical["taper"] = {"law": "logarithmic", "sense": "log"}
    assert_valid(ras_validator, potentiometer_doc)


def test_potentiometer_custom_taper_requires_curve(ras_validator, potentiometer_doc):
    electrical = potentiometer_doc["potentiometer"]["manufacturerInfo"]["datasheetInfo"]["electrical"]
    electrical["taper"] = {"law": "custom"}
    assert_invalid(ras_validator, potentiometer_doc)


def test_potentiometer_taper_branches_do_not_mix(ras_validator, potentiometer_doc):
    """Pinned consts: a linear taper cannot carry the logarithmic branch's fields."""
    electrical = potentiometer_doc["potentiometer"]["manufacturerInfo"]["datasheetInfo"]["electrical"]
    electrical["taper"] = {"law": "linear", "sense": "log"}
    assert_invalid(ras_validator, potentiometer_doc)


def test_potentiometer_rotary_actuation_rejects_linear_fields(ras_validator, potentiometer_doc):
    mechanical = potentiometer_doc["potentiometer"]["manufacturerInfo"]["datasheetInfo"]["mechanical"]
    mechanical["actuation"] = {"type": "linear", "turns": 25}
    assert_invalid(ras_validator, potentiometer_doc)


def test_potentiometer_actuation_requires_type(ras_validator, potentiometer_doc):
    mechanical = potentiometer_doc["potentiometer"]["manufacturerInfo"]["datasheetInfo"]["mechanical"]
    mechanical["actuation"] = {"turns": 25}
    assert_invalid(ras_validator, potentiometer_doc)


def test_potentiometer_mechanical_extra_property_rejected(ras_validator, potentiometer_doc):
    potentiometer_doc["potentiometer"]["manufacturerInfo"]["datasheetInfo"]["mechanical"]["bogus"] = 1
    assert_invalid(ras_validator, potentiometer_doc)


def test_potentiometer_shaft_extra_property_rejected(ras_validator, potentiometer_doc):
    potentiometer_doc["potentiometer"]["manufacturerInfo"]["datasheetInfo"]["mechanical"]["shaft"]["bogus"] = 1
    assert_invalid(ras_validator, potentiometer_doc)


def test_potentiometer_part_no_device_type_property(ras_validator, potentiometer_doc):
    potentiometer_doc["potentiometer"]["manufacturerInfo"]["datasheetInfo"]["part"]["deviceType"] = "potentiometer"
    assert_invalid(ras_validator, potentiometer_doc)


def test_design_requirements_potentiometer_requires_total_resistance(ras_validator, potentiometer_doc):
    del potentiometer_doc["inputs"]["designRequirements"]["totalResistance"]
    assert_invalid(ras_validator, potentiometer_doc)


def test_design_requirements_potentiometer_rejects_resistor_fields(ras_validator, potentiometer_doc):
    potentiometer_doc["inputs"]["designRequirements"]["resistance"] = {"nominal": 10000}
    assert_invalid(ras_validator, potentiometer_doc)


def test_design_requirements_potentiometer_unknown_technology_rejected(ras_validator, potentiometer_doc):
    potentiometer_doc["inputs"]["designRequirements"]["allowedTechnologies"] = ["metalOxide"]
    assert_invalid(ras_validator, potentiometer_doc)


# ---------------------------------------------------------------------------
# cermet in the fixed-resistor technology enum (separable change)
# ---------------------------------------------------------------------------

def test_resistor_cermet_technology_accepted(ras_validator, resistor_doc):
    resistor_doc["resistor"]["manufacturerInfo"]["datasheetInfo"]["part"]["technology"] = "cermet"
    assert_valid(ras_validator, resistor_doc)


def test_design_requirements_resistor_allows_cermet(ras_validator, resistor_doc):
    resistor_doc["inputs"]["designRequirements"]["allowedTechnologies"] = ["cermet"]
    assert_valid(ras_validator, resistor_doc)


# ---------------------------------------------------------------------------
# ceramicComposition in the fixed-resistor technology enum, and the enum
# hoisted into one named $def that the requirement side $refs
# ---------------------------------------------------------------------------

def test_ccr_example_validates(ras_validator, ccr_doc):
    assert_valid(ras_validator, ccr_doc)


def test_resistor_ceramic_composition_technology_accepted(ras_validator, resistor_doc):
    resistor_doc["resistor"]["manufacturerInfo"]["datasheetInfo"]["part"]["technology"] = "ceramicComposition"
    assert_valid(ras_validator, resistor_doc)


def test_design_requirements_resistor_allows_ceramic_composition(ras_validator, resistor_doc):
    resistor_doc["inputs"]["designRequirements"]["allowedTechnologies"] = ["ceramicComposition"]
    assert_valid(ras_validator, resistor_doc)


def test_resistor_hyphenated_ceramic_composition_rejected(ras_validator, ccr_doc):
    ccr_doc["resistor"]["manufacturerInfo"]["datasheetInfo"]["part"]["technology"] = "ceramic-composition"
    assert_invalid(ras_validator, ccr_doc)


def test_design_requirements_resistor_hyphenated_ceramic_composition_rejected(ras_validator, ccr_doc):
    ccr_doc["inputs"]["designRequirements"]["allowedTechnologies"] = ["ceramic-composition"]
    assert_invalid(ras_validator, ccr_doc)


def test_resistor_technology_is_one_named_def():
    resistor = _load(SCHEMA_DIR / "resistor.json")
    assert "ceramicComposition" in resistor["$defs"]["technology"]["enum"]
    text = json.dumps(resistor)
    assert text.count('"carbonComposition"') == 1, "resistor technology enum must exist exactly once"
    dr = json.dumps(_load(SCHEMA_DIR / "inputs" / "designRequirements.json"))
    assert "https://psma.com/ras/resistor.json#/$defs/technology" in dr
    assert '"bulkMetalFoil"' not in dr, "requirement side must $ref the anchor, not restate the enum"


# ---------------------------------------------------------------------------
# varistor surgeWaveform is the shared PEAS enum (PEAS-RFC 0003)
# ---------------------------------------------------------------------------

def _varistor_electrical(doc):
    return doc["varistor"]["manufacturerInfo"]["datasheetInfo"]["electrical"]


@pytest.mark.parametrize("w", ["8/20", "10/350", "10/1000"])
def test_varistor_surge_waveform_member_accepted(ras_validator, varistor_doc, w):
    _varistor_electrical(varistor_doc)["surgeWaveform"] = w
    assert_valid(ras_validator, varistor_doc)


@pytest.mark.parametrize("w", ["8x20", "8/20us", "8/20 µs", "ISO 7637-2 pulse 5a", ""])
def test_varistor_unknown_surge_waveform_rejected(ras_validator, varistor_doc, w):
    _varistor_electrical(varistor_doc)["surgeWaveform"] = w
    msgs = [e.message for e in ras_validator.iter_errors(varistor_doc)]
    assert any("is not one of" in m for m in msgs), msgs
