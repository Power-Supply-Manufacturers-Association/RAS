"""Validation tests for the RAS schemas.

Run with:   pytest tests/
or:         python3 -m pytest tests/test_schemas.py -v

Covers:
  * every RAS schema parses and passes Draft 2020-12 meta-validation
  * cross-document $refs resolve (RAS + PEAS schemas registered)
  * the canonical examples (resistor, shunt, varistor) validate
  * negative cases:
      - top-level oneOf (must have exactly one of resistor/varistor)
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
        schemas["http://openconverters.com/schemas/RAS/RAS.json"],
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
    resistor_doc["thermistor"] = resistor_doc.pop("resistor")
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
    for field in ("varistorVoltage", "clampingVoltage", "peakSurgeCurrent", "energyAbsorption"):
        bad = copy.deepcopy(varistor_doc)
        del bad["varistor"]["manufacturerInfo"]["datasheetInfo"]["electrical"][field]
        assert_invalid(ras_validator, bad)


def test_part_no_device_type_property(ras_validator, resistor_doc):
    resistor_doc["resistor"]["manufacturerInfo"]["datasheetInfo"]["part"]["deviceType"] = "resistor"
    assert_invalid(ras_validator, resistor_doc)


def test_resistor_unknown_technology_rejected(ras_validator, resistor_doc):
    resistor_doc["resistor"]["manufacturerInfo"]["datasheetInfo"]["part"]["technology"] = "magicFilm"
    assert_invalid(ras_validator, resistor_doc)


def test_varistor_unknown_technology_rejected(ras_validator, varistor_doc):
    varistor_doc["varistor"]["manufacturerInfo"]["datasheetInfo"]["part"]["technology"] = "thinFilm"
    assert_invalid(ras_validator, varistor_doc)


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


def test_design_requirements_unknown_device_type_rejected(ras_validator, resistor_doc):
    resistor_doc["inputs"]["designRequirements"]["deviceType"] = "thermistor"
    assert_invalid(ras_validator, resistor_doc)
