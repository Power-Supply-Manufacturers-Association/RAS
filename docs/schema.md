# RAS Schema Reference

Complete field-by-field documentation for the Resistor-family Agnostic Structure (fixed resistors **and** varistors).

---

## Top-Level: RAS.json

The root document wraps exactly one component with its design context. The field name (`resistor` or `varistor`) is the device-type discriminator — there is no `deviceType` property on the component itself.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `inputs` | [inputs](#inputs-inputsjson) | Yes | Design requirements and operating points for this component |
| `resistor` | [resistor](#resistorjson) | Exactly one of the two | Fixed resistor component data |
| `varistor` | [varistor](#varistorjson) | Exactly one of the two | Varistor / MOV component data |
| `outputs` | array of [outputs](#outputs-outputsjson) | Yes | Computed results per operating point; `outputs[i]` aligns positionally with `inputs.operatingPoints[i]` |

A top-level `oneOf` enforces that exactly one of `resistor` / `varistor` is present. The root object is closed (`additionalProperties: false`).

**Schema ID**: `https://psma.com/ras/RAS.json`

---

## inputs (inputs.json)

Mirrors the MAS / CAS inputs structure. Both fields required; closed object.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `operatingPoints` | array (min 1 item) | Yes | Each item is a PEAS [`twoTerminalOperatingPoint`](https://psma.com/peas/inputs/twoTerminalOperatingPoint.json): `{name?, conditions, excitation}` with `conditions` and `excitation` required (single voltage + current waveform, since resistors are two-terminal). |
| `designRequirements` | [designRequirements](#designrequirements-inputsdesignrequirementsjson) | Yes | Requirements the component must satisfy |

### designRequirements (inputs/designRequirements.json)

An `allOf` extension of the PEAS `designRequirementsBase` mixin, closed with top-level `unevaluatedProperties: false`. A **`deviceType` discriminator** (required, `"resistor"` or `"varistor"`) drives a per-type `oneOf` — mirrors the SAS pattern.

Fields common to both device types:

| Field | Type | Required | Unit | Description |
|-------|------|----------|------|-------------|
| `deviceType` | string (enum) | Yes | — | `resistor` or `varistor`; aligns with the RAS top-level field name |
| `maximumWorkingVoltage` | number ≥ 0 | No | V | Maximum DC working voltage allowed across the component |
| `maximumOverloadVoltage` | number ≥ 0 | No | V | Maximum short-pulse / overload voltage |
| `application` | string (enum) | No | — | PEAS `resistorApplication`: `power`, `precision`, `currentSense`, `pulseHandling`, `general` |
| `subApplication` | string (enum) | No | — | PEAS `resistorSubApplication` (e.g. `snubber`, `gateDrive`, `bleed`, `preCharge`, `inrush`, `divider`, `feedback`, `termination`, `pullUpDown`, `fusible`, `shunt`, `audio`, `instrumentation`, `highVoltage`) |

Inherited from PEAS `designRequirementsBase` (all optional): `name`, `market`, `topology`, `operatingTemperature` (dimensionWithTolerance, °C), `terminalType`, `maximumWeight` (kg), `maximumDimensions`.

**Resistor branch** (`deviceType: "resistor"`) — **required: `resistance`**:

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `resistance` | [dimensionWithTolerance](#dimensionwithtolerance) | Ohm | Required values for the resistance (required) |
| `powerRating` | number ≥ 0 | W | Required continuous power dissipation rating |
| `maximumTcr` | number ≥ 0 | ppm/K | Maximum temperature coefficient of resistance |
| `maximumDriftLongTerm` | number ≥ 0 | % | Maximum allowed long-term resistance drift over the operating life |
| `maximumNoise` | number | dB | Maximum allowed current-noise index |
| `minimumPulseEnergy` | number ≥ 0 | J | Minimum pulse-energy withstand requirement |
| `maximumEsl` | number ≥ 0 | H | Maximum equivalent series inductance |
| `role` | string (enum) | — | `currentSense`, `gate`, `snubber`, `damping`, `bleed`, `preCharge`, `inrush`, `divider`, `feedback`, `termination`, `pullUp`, `pullDown`, `fusible` |
| `allowedTechnologies` | array (enum items) | — | Subset of the resistor [technology enum](#technology-enum-values) (same 11 values). Absent = all allowed. |

**Varistor branch** (`deviceType: "varistor"`) — **required: `ratedContinuousVoltage`**, plus **at least one of `minimumEnergyAbsorption` / `minimumPeakSurgeCurrent`** (`anyOf`; Joule-rated disc varistors vs. multilayer/ESD varistors that publish no Joule rating):

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `ratedContinuousVoltage` | number ≥ 0 | V | Required minimum continuous working voltage rating V_M (required) |
| `voltageType` | string (enum) | — | Whether the continuous rating is `ac` (RMS) or `dc` |
| `maximumClampingVoltage` | number ≥ 0 | V | Maximum allowed clamping voltage at the rated surge current |
| `minimumPeakSurgeCurrent` | number ≥ 0 | A | Required minimum peak surge current for the rated waveform |
| `minimumEnergyAbsorption` | number ≥ 0 | J | Required minimum single-pulse energy absorption capability |
| `maximumCapacitance` | number ≥ 0 | F | Maximum allowed capacitance (lower = better for high-frequency lines) |
| `role` | string (enum) | — | `surgeProtection`, `esdProtection`, `snubber`, `voltageClamp` |
| `allowedTechnologies` | array (enum items) | — | Subset of `metalOxide`, `siliconCarbide`, `multiLayer`, `polymer` |

---

## resistor.json

Describes a fixed resistor. Closed object with two optional properties, constrained by an `anyOf`: either `manufacturerInfo` is present (a sourced part) **or** the object is completely empty (`{}` — a pre-sourcing seed whose requirements live in the enclosing document's `inputs.designRequirements`).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `manufacturerInfo` | [manufacturerInfo](#manufacturerinfo) | Yes (unless empty seed) | Container for manufacturer-specific information |
| `distributorsInfo` | array of PEAS `distributorInfo` | No | Where to buy this component (packaging, MOQ, VPE, stock, cost `{value, currency}`) — commercial data lives here; there is **no** `business` section in `datasheetInfo` |

---

## manufacturerInfo

**Required: `name`, `datasheetInfo`.** The other fields `$ref` the shared PEAS `manufacturerInfo` field definitions.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Manufacturer name |
| `datasheetInfo` | [datasheetInfo](#datasheetinfo) | Yes | Information extracted from the component datasheet |
| `reference` | string | No | Manufacturer part number |
| `status` | string (enum) | No | `production`, `prototype`, `nrnd`, `obsolete`, `preview` |
| `description` | string | No | Description of the part per its manufacturer |
| `orderCode` | string | No | Manufacturer order code |
| `datasheetUrl` | string (uri) | No | URL to manufacturer datasheet |
| `family` | string | No | Manufacturer product family / product-line name |
| `spiceModel` | object | No | SPICE simulation model |

---

## datasheetInfo

The main data block containing all resistor parameters organized into sections. **Required: `part`, `electrical`.**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `part` | [part](#part) | Yes | Basic part identification |
| `electrical` | [electrical](#electrical) | Yes | Electrical characteristics |
| `thermal` | [thermal](#thermal) | No | Thermal characteristics (shared, `utils.json#/$defs/thermal`) |
| `mechanical` | [mechanical](#mechanical) | No | Mechanical dimensions and package information (shared, `utils.json#/$defs/mechanical`) |
| `modelParams` | [modelParams](#modelparams) | No | SPICE model parameters |
| `factors` | [factors](#factors) | No | Derating factors for temperature |
| `provenance` | array | No | Data-provenance trail (see [Provenance](#provenance-data-source-trail)) |

---

## part

Basic part identification — an `allOf` extension of PEAS `datasheetInfoPartBase`. **Required: `partNumber`, `technology`.**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `partNumber` | string | Yes | Manufacturer part number (e.g., `"CRCW060310K0FKEA"`) |
| `series` | string or null | No | Product series name (e.g., `"CRCW"`, `"WSK2512"`) |
| `technology` | string (enum) | Yes | Resistor technology type |
| `case` | string | No | Case or package code (e.g., `"0603"`, `"2512"`) |
| `description` | string | No | Free-text part description as on the datasheet |
| `matchcodeDescription` | string | No | Human-readable description of the part |

### technology enum values

| Value | Description |
|-------|-------------|
| `thinFilm` | Thin film -- sputtered metal alloy on ceramic substrate. Low TCR, tight tolerance. |
| `thickFilm` | Thick film -- printed resistive paste on ceramic. General purpose, low cost. |
| `metalFilm` | Metal film -- vacuum-deposited metal film, typically on axial leaded parts. Low noise, good stability. |
| `metalOxide` | Metal oxide -- metal oxide film on ceramic. High voltage, flame-proof. |
| `wirewound` | Wirewound -- resistance wire wound on a core. High power, precise, but inductive. |
| `carbonComposition` | Carbon composition -- carbon particles in a binder. High pulse handling. |
| `carbonFilm` | Carbon film -- deposited carbon film. Low-cost general purpose leaded parts. |
| `metalFoil` | Metal foil -- precision metal foil on ceramic. Ultra-low TCR, highest precision. |
| `bulkMetalFoil` | Bulk metal foil -- Vishay-style bulk foil element. The ultimate in TCR and long-term stability. |
| `currentSenseShunt` | Current sense shunt -- metal alloy strip/element for current sensing. Very low resistance (mOhm range), often 4-terminal Kelvin. |
| `melf` | MELF -- cylindrical metal-film body in SMD (MELF/MiniMELF) form. Good pulse and precision behavior. |

---

## electrical

Electrical characteristics of the resistor. **Required: `resistance`, `tolerance`, `powerRating`.** The optional fields are plain numbers (not nullable) — omit them when the datasheet does not state them.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `resistance` | [dimensionWithTolerance](#dimensionwithtolerance) | Yes | Nominal resistance in Ohms. Typically only `nominal` is specified, since the separate `tolerance` field captures the percentage. |
| `tolerance` | number ≥ 0 | Yes | Resistance tolerance as a fraction. `0.01` = 1%, `0.001` = 0.1%. |
| `temperatureCoefficient` | number | No | Temperature coefficient of resistance (TCR) in ppm/K. Typical values: thin film 5-50, thick film 100-200, foil <1. |
| `powerRating` | number ≥ 0 | Yes | Maximum continuous power dissipation in Watts at the reference temperature. |
| `powerRatingTemperature` | number | No | Reference temperature (in Celsius) at which `powerRating` applies. Typically 70 C for SMD resistors. Above this temperature, the power must be derated per the `factors` section. |
| `maxVoltage` | number ≥ 0 | No | Maximum continuous working voltage in Volts. For high-resistance values, this may limit power before the wattage rating does (P = V^2/R). |
| `maxOverloadVoltage` | number ≥ 0 | No | Maximum overload voltage in Volts (short-duration stress test per IEC 60115). |
| `insulationResistance` | number ≥ 0 | No | Insulation resistance in Ohms (typically > 1 GOhm). |
| `noiseIndex` | number | No | Current noise index in dB. Lower is better. Relevant for thin film and foil types. |

---

## thermal

Thermal characteristics, shared by resistor and varistor (`utils.json#/$defs/thermal`) — an `allOf` extension of PEAS `datasheetInfoThermal`. All fields optional.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `operatingTemperature` | [dimensionWithTolerance](#dimensionwithtolerance) | No | Operating temperature range in Celsius. Uses `minimum` and `maximum` fields (e.g., `{"minimum": -55, "maximum": 155}`). |
| `thermalResistance` | number ≥ 0 | No | Thermal resistance from body to ambient, in K/W. |

---

## mechanical

Mechanical dimensions and package information, shared by resistor and varistor (`utils.json#/$defs/mechanical`) — an `allOf` extension of PEAS `datasheetInfoMechanical`. The object is **flat** (no nested `dimensions`/`shape` sub-objects) and all fields are optional.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `length` | [dimensionWithTolerance](#dimensionwithtolerance) | No | Body length in meters |
| `width` | [dimensionWithTolerance](#dimensionwithtolerance) | No | Body width in meters |
| `height` | [dimensionWithTolerance](#dimensionwithtolerance) | No | Body height in meters |
| `diameter` | [dimensionWithTolerance](#dimensionwithtolerance) | No | Body diameter in meters (cylindrical parts, e.g. MELF, disc varistors) |
| `weight` | number | No | Component weight in kg |
| `shapeType` | string | No | Package / body shape (e.g., `"SMD chip"`, `"Axial"`, `"Disc"`) |
| `assemblyType` | string (enum) | No | PCB mounting / assembly type — the PEAS `connectionType` enum (lowercase): `pin`, `screw`, `smt`, `flyingLead`, `tht`, `pcbPad`, `chassis` |
| `case` | string | No | Package code (e.g. `"0603"`, `"2512"`, `"S14"`, axial) |

---

## modelParams

SPICE model parameters for circuit simulation. These map directly to the standard SPICE resistor model. All fields are optional plain numbers — **not nullable**; omit what is unknown.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `r` | number > 0 | No | Resistance in Ohms (same as `electrical.resistance.nominal`) |
| `tcr1` | number | No | First-order temperature coefficient in 1/K. This is the `temperatureCoefficient` value converted from ppm/K to 1/K: divide by 1e6. Example: 100 ppm/K = `100e-6`. |
| `tcr2` | number | No | Second-order temperature coefficient in 1/K^2. Usually omitted for standard resistors; relevant for precision types. |

The SPICE temperature model is: `R(T) = R * (1 + tcr1*(T-Tnom) + tcr2*(T-Tnom)^2)`

---

## factors

Derating factors that define how the maximum power rating decreases with temperature. A single optional property:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `powerDerating` | [deratingCurve](#deratingcurve) | No | Power derating curve vs. temperature |

### deratingCurve

Defined in `utils.json#/$defs/deratingCurve`. Paired, index-aligned arrays: `amplitude[i]` is the rated fraction at `temperature[i]`. **Both arrays required, min 2 points each.**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `temperature` | number[] (min 2) | Yes | Temperature breakpoints in Celsius |
| `amplitude` | number[] (min 2, each 0.0–1.0) | Yes | Derating fraction of rated power at each temperature breakpoint |

**Example**: A resistor rated 0.1W at 70 C that derates to zero at 155 C:

```json
{
    "powerDerating": {
        "temperature": [70, 100, 125, 155],
        "amplitude": [1.0, 0.65, 0.35, 0.0]
    }
}
```

At 100 C, the maximum allowed power is `0.1W * 0.65 = 0.065W`.

---

## varistor.json

Describes a varistor / MOV (Metal Oxide Varistor). Same outer shape as `resistor.json`: closed object with `manufacturerInfo` (same required `name` + `datasheetInfo`) and `distributorsInfo`, plus the same `anyOf` allowing an **empty pre-sourcing seed** (`{}`).

### varistor datasheetInfo

**Required: `part`, `electrical`.**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `part` | object | Yes | Part identification — same base as the resistor `part`, with the varistor technology enum |
| `electrical` | object | Yes | Varistor electrical characteristics |
| `thermal` | [thermal](#thermal) | No | Shared thermal section |
| `mechanical` | [mechanical](#mechanical) | No | Shared flat mechanical section |
| `viCurve` | [curve](#curve) | No | Voltage vs. current characteristic in the conduction region |
| `provenance` | array | No | Data-provenance trail |

### varistor part

**Required: `partNumber`, `technology`.** Same fields as the resistor part (`series`, `case`, `description`, `matchcodeDescription`), with the varistor technology enum:

| Value | Description |
|-------|-------------|
| `metalOxide` | ZnO disc MOV — AC-line and DC-bus surge protection |
| `siliconCarbide` | SiC varistor (legacy / high-energy) |
| `multiLayer` | Multilayer chip varistor (MLV) — board-level ESD/transient protection |
| `polymer` | Polymer ESD suppressor |

### varistor electrical

**Required: `varistorVoltage`, `clampingVoltage`, `peakSurgeCurrent`.** Optional fields are plain numbers (not nullable).

| Field | Type | Required | Unit | Description |
|-------|------|----------|------|-------------|
| `varistorVoltage` | [dimensionWithTolerance](#dimensionwithtolerance) | Yes | V | Varistor voltage V_1mA at the 1 mA reference current |
| `clampingVoltage` | number ≥ 0 | Yes | V | Clamping voltage V_C at the rated peak surge current I_PP |
| `peakSurgeCurrent` | number ≥ 0 | Yes | A | Peak surge current I_PP for the rated waveform (e.g. 8/20 µs) |
| `maxContinuousAcVoltage` | number ≥ 0 | No | V RMS | Maximum continuous AC working voltage |
| `maxContinuousDcVoltage` | number ≥ 0 | No | V | Maximum continuous DC working voltage |
| `clampingCurrent` | number ≥ 0 | No | A | Test current at which the clamping voltage is specified |
| `surgeWaveform` | string | No | — | Waveform of the rated surge in 'rise/decay' microseconds (e.g. `"8/20"`) |
| `energyAbsorption` | number ≥ 0 | No | J | Maximum single-pulse energy absorption (10/1000 µs waveform). A power-/disc-MOV rating; **multilayer chip varistors** (e.g. TDK AVR) are specified by `peakSurgeCurrent` + `clampingVoltage` instead and typically publish no Joule rating — for those parts this field is absent. |
| `capacitance` | number ≥ 0 | No | F | Typical capacitance at 1 kHz |
| `leakageCurrent` | number ≥ 0 | No | A | DC leakage current at the maximum continuous voltage |
| `nonlinearityCoefficient` | number > 0 | No | — | Non-linearity exponent α (V = k * I^(1/α)) in the conduction region |

---

## outputs (outputs.json)

Computed results for **one operating point**; the top-level RAS document holds an **array** of these, aligned positionally with `inputs.operatingPoints`. Each of the 7 named blocks is independently optional; every block is an `allOf` over the PEAS `outputBase` provenance shell — `origin` (`manufacturer`/`measurement`/`simulation`) and `methodUsed` are **required** in every block — and is sealed with `unevaluatedProperties: false`.

| Block | Required field(s) inside | Description |
|-------|--------------------------|-------------|
| `powerDissipation` | `totalDissipation` (W) | Steady-state Joule heating; optional `rmsCurrent`, `rmsVoltage`, `deratingMargin` |
| `temperature` | `hotSpotTemperature` (°C) | Self-heating; optional `ambientTemperature`, `temperatureRise` (K), `thermalResistance` (K/W) |
| `effectiveResistance` | `effectiveResistance` (dimensionWithTolerance, Ohm) | R at operating temperature (R_nom * (1 + TCR * dT)); optional `ratedResistance`, `tcrApplied`, `conditions` |
| `pulseStress` | `passes` (boolean) | Pulse-handling check; optional `appliedPulseEnergy` (J), `appliedPulsePower` (W), `ratedPulseEnergy` (J), `margin` |
| `lifetime` | `predictedHours` (dimensionWithTolerance, h) | Predicted load life; optional `predictedYears`, `endOfLifeMode` (`openCircuit`/`shortCircuit`/`resistanceDrift`/`thermalRunaway`/`soldersFatigue`), `conditions` |
| `noise` | — | `currentNoiseIndex` (dB), `noiseVoltageRms` (V), `bandwidth` (Hz), `conditions` |
| `drift` | — | `predictedDriftPercent` (% of nominal), `horizonHours` (h) |

---

## Shared Types

`RAS/schemas/utils.json` holds the RAS-shared sub-schemas [`thermal`](#thermal), [`mechanical`](#mechanical), and [`deratingCurve`](#deratingcurve). The generic primitives below live in `PEAS/schemas/utils.json` and are referenced by absolute `$id`.

### dimensionWithTolerance

A dimension with minimum, nominal, and maximum values. At least one of `minimum`/`nominal`/`maximum` must be present. Closed object; also supports optional `excludeMinimum`, `excludeMaximum`, and `unit`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `minimum` | number | At least one of min/nom/max | The minimum value |
| `nominal` | number | At least one of min/nom/max | The nominal value |
| `maximum` | number | At least one of min/nom/max | The maximum value |

**Usage in RAS**:
- `resistance`: typically only `nominal` (e.g., `{"nominal": 10000}`)
- `varistorVoltage`: often all three (e.g., `{"minimum": 387, "nominal": 430, "maximum": 473}`)
- `operatingTemperature`: uses `minimum` and `maximum` (e.g., `{"minimum": -55, "maximum": 155}`)
- mechanical dimensions: typically only `nominal` (e.g., `{"nominal": 0.0016}`)

### curve

X-Y curve data points for piecewise-linear characteristics (used by the varistor `viCurve`). Optional `xLabel`, `yLabel`, `conditions`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `xData` | number[] | No | X-axis values |
| `yData` | number[] | No | Y-axis values |

### numberArray

An array of numeric values.

```json
[70, 100, 125, 155]
```

## Provenance (data-source trail)

Every `datasheetInfo` (resistor and varistor) carries an optional `provenance` array recording where its data
came from. Optional and closed, so records without it remain valid. Each entry:

| field | meaning |
|---|---|
| `source` | `manufacturerDatasheet` · `manufacturerParametric` · `manufacturerDatabase` · `distributor` · `librarianEnrichment` · `scrape` · `manual` (required) |
| `sourceName` | human-readable source, e.g. `"TI parametric API"`, `"WE - Passive Components.mdb"`, `"DigiKey"` |
| `sourceUrl` | URL the value came from (optional) |
| `retrievedDate` | `YYYY-MM-DD` (optional) |
| `fields` | which `datasheetInfo` fields this source supplied — for mixed-source records (optional) |

It is a **list**: a record may combine sources (e.g. specs from the datasheet, a rated
voltage from a distributor, a missing field back-filled by librarian enrichment). The
canonical definition lives in `PEAS/schemas/utils.json#/$defs/provenance`.
