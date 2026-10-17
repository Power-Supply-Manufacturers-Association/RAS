# RAS Schema Reference

Complete field-by-field documentation for the Resistor-family Agnostic Structure (fixed resistors, varistors, thermistors **and** potentiometers).

---

## Top-Level: RAS.json

The root document wraps exactly one component with its design context. The field name (`resistor`, `varistor`, `thermistor` or `potentiometer`) is the device-type discriminator — there is no `deviceType` property on the component itself.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `inputs` | [inputs](#inputs-inputsjson) | Yes | Design requirements and operating points for this component |
| `resistor` | [resistor](#resistorjson) | Exactly one of the four | Fixed resistor component data |
| `varistor` | [varistor](#varistorjson) | Exactly one of the four | Varistor / MOV component data |
| `thermistor` | [thermistor](#thermistorjson) | Exactly one of the four | Thermistor (NTC / PTC) component data |
| `potentiometer` | [potentiometer](#potentiometerjson) | Exactly one of the four | Potentiometer / rheostat / trimmer component data |
| `outputs` | array of [outputs](#outputs-outputsjson) | Yes | Computed results per operating point; `outputs[i]` aligns positionally with `inputs.operatingPoints[i]` |

A top-level `oneOf` enforces that exactly one of `resistor` / `varistor` / `thermistor` / `potentiometer` is present. The root object is closed (`additionalProperties: false`).

**Schema ID**: `https://psma.com/ras/RAS.json`

---

## inputs (inputs.json)

Mirrors the MAS / CAS inputs structure. Both fields required; closed object.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `operatingPoints` | array (min 1 item) | Yes | Each item is a PEAS [`twoTerminalOperatingPoint`](https://psma.com/peas/inputs/twoTerminalOperatingPoint.json): `{name?, conditions, excitation}` with `conditions` and `excitation` required (single voltage + current waveform, since resistors are two-terminal). |
| `designRequirements` | [designRequirements](#designrequirements-inputsdesignrequirementsjson) | Yes | Requirements the component must satisfy |

### designRequirements (inputs/designRequirements.json)

An `allOf` extension of the PEAS `designRequirementsBase` mixin, closed with top-level `unevaluatedProperties: false`. A **`deviceType` discriminator** (required, `"resistor"`, `"varistor"`, `"thermistor"` or `"potentiometer"`) drives a per-type `oneOf` — mirrors the SAS pattern.

Fields common to all device types:

| Field | Type | Required | Unit | Description |
|-------|------|----------|------|-------------|
| `deviceType` | string (enum) | Yes | — | `resistor`, `varistor`, `thermistor` or `potentiometer`; aligns with the RAS top-level field name |
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
| `allowedTechnologies` | array (enum items) | — | Subset of the resistor [technology enum](#technology-enum-values) (same 12 values). Absent = all allowed. |

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

**Thermistor branch** (`deviceType: "thermistor"`) — **required: `resistanceAt25C`**:

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `resistanceAt25C` | [dimensionWithTolerance](#dimensionwithtolerance) | Ohm | Required zero-power resistance R25 at 25 °C (required) |
| `bConstant` | [dimensionWithTolerance](#dimensionwithtolerance) | K | Required B (beta) constant (NTC parts) |
| `minimumSteadyStateCurrent` | number ≥ 0 | A | Required minimum continuous (steady-state) current capability (inrush limiters) |
| `minimumEnergy` | number ≥ 0 | J | Required minimum single-event energy absorption capability, i.e. the capacitive load to charge (inrush limiters) |
| `switchTemperature` | [dimensionWithTolerance](#dimensionwithtolerance) | °C | Required PTC switch / reference temperature |
| `role` | string (enum) | — | `inrushLimiting`, `temperatureSensing`, `temperatureCompensation`, `overtemperatureProtection` |
| `allowedTechnologies` | array (enum items) | — | Subset of `ntc`, `ptc` — items `$ref` the part-side anchor `thermistor.json#/$defs/technology`, so the two enums cannot drift |

**Potentiometer branch** (`deviceType: "potentiometer"`) — **required: `totalResistance`**:

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `totalResistance` | [dimensionWithTolerance](#dimensionwithtolerance) | Ohm | Required end-to-end track resistance (required). Named to match the part side, so a `resistance` requirement cannot be mistaken for a potentiometer one |
| `powerRating` | number ≥ 0 | W | Required continuous power dissipation rating of the whole track |
| `wiperPosition` | [dimensionWithTolerance](#dimensionwithtolerance) | fraction | Where the design expects the wiper to sit, `0..1` of electrical travel from the low end. **The design-time free variable** — give it as a range when the design needs adjustment headroom |
| `taperLaw` | string (enum) | — | Required taper law; `$ref`s `potentiometer.json#/$defs/taperLaw` (`linear`, `logarithmic`, `sShaped`, `custom`) so the requirement and part vocabularies cannot drift |
| `minimumTurns` | number > 0 | — | Required minimum actuator turns end-to-end, where setting resolution matters |
| `gangs` | integer ≥ 1 | — | Required number of independent sections on one actuator (`1` single, `2` dual) |
| `maximumTemperatureCoefficient` | number ≥ 0 | ppm/K | Maximum acceptable track temperature coefficient |
| `maximumWiperResistance` | number ≥ 0 | Ohm | Maximum acceptable wiper contact resistance |
| `role` | string (enum) | — | `trimming`, `voltageDivider`, `rheostat`, `feedbackAdjust`, `referenceAdjust`, `userControl`, `positionSensing` |
| `allowedTechnologies` | array (enum items) | — | Subset of the [potentiometer technology enum](#potentiometer-technology-enum-values) — items `$ref` the part-side anchor `potentiometer.json#/$defs/technology`, so the two cannot drift |

---

## resistor.json

Describes a fixed resistor. Closed object with three optional properties, constrained by an `anyOf`: either `manufacturerInfo` is present (a sourced part) **or** the object is completely empty (`{}` — a pre-sourcing seed whose requirements live in the enclosing document's `inputs.designRequirements`). A document carrying only `substitutesInfo` satisfies neither branch and is rejected.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `manufacturerInfo` | [manufacturerInfo](#manufacturerinfo) | Yes (unless empty seed) | Container for manufacturer-specific information |
| `distributorsInfo` | array of PEAS `distributorInfo` | No | Where to buy this component (packaging, MOQ, VPE, stock, cost `{value, currency}`) — commercial data lives here; there is **no** `business` section in `datasheetInfo` |
| `substitutesInfo` | array of PEAS `substituteInfo` | No | Replacement parts: manufacturer-named successors and second sources (`{partNumber, manufacturer, type, notes, source}`). `type: "successor"` means THIS part is superseded by the named one — one hop, as the manufacturer states it, never inferred from `status: obsolete`. The named part need not be in any catalogue; resolving it is the referential pass's job. The evidence goes in `datasheetInfo.provenance[]` with `fields: ["substitutesInfo"]` (PEAS-RFC 0002). Present on all four RAS part files (`resistor`, `varistor`, `thermistor`, `potentiometer`). |

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
| `cermet` | Cermet -- ceramic-metal thick film fired onto a ceramic substrate. Stable, high-voltage-capable, and the standard element of resistor networks and trimmers. Added 2026-09. |
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

Thermal characteristics, shared by resistor, varistor, thermistor and potentiometer (`utils.json#/$defs/thermal`) — an `allOf` extension of PEAS `datasheetInfoThermal`. All fields optional.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `operatingTemperature` | [dimensionWithTolerance](#dimensionwithtolerance) | No | Operating temperature range in Celsius. Uses `minimum` and `maximum` fields (e.g., `{"minimum": -55, "maximum": 155}`). |
| `thermalResistance` | number ≥ 0 | No | Thermal resistance from body to ambient, in K/W. |

---

## mechanical

Mechanical dimensions and package information, shared by resistor, varistor and thermistor (`utils.json#/$defs/mechanical`) — an `allOf` extension of PEAS `datasheetInfoMechanical`. The object is **flat** (no nested `dimensions`/`shape` sub-objects) and all fields are optional. **Potentiometers do not use this `$def`**: they need shaft, mounting and actuation mechanics, and this one is sealed, so `potentiometer.json` composes the PEAS base directly — see [potentiometer mechanical](#potentiometer-mechanical).

- **`pinout`** / **`landPattern`** — optional, both the **shared PEAS types** (`https://psma.com/peas/utils.json#/$defs/pinout` and `#/$defs/landPattern`, hoisted 2026-08): per-terminal `(pin, name, function)` map using the family-wide `pinFunction` vocabulary, and the manufacturer-recommended PCB land pattern (pad centres/sizes/drills). No module defines its own variant of these types — additions to the vocabulary go to PEAS.

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
| `surgeWaveform` | string enum ([PEAS `surgeWaveform`](https://psma.com/peas/utils.json#/$defs/surgeWaveform)) | No | — | Impulse the `peakSurgeCurrent` rating is stated at: one of `8/20`, `10/1000`, `10/350`, `2/10`, `5/320`, `10/700`, `10/560`, `9/720`, `10/160`, `TLP 100 ns` (each label's wave and standard are listed in PEAS `docs/architecture.md`). Free strings such as `8x20` are rejected. Absent = not stated (no default). |
| `energyAbsorption` | number ≥ 0 | No | J | Maximum single-pulse energy absorption (10/1000 µs waveform). A power-/disc-MOV rating; **multilayer chip varistors** (e.g. TDK AVR) are specified by `peakSurgeCurrent` + `clampingVoltage` instead and typically publish no Joule rating — for those parts this field is absent. |
| `capacitance` | number ≥ 0 | No | F | Typical capacitance at 1 kHz |
| `leakageCurrent` | number ≥ 0 | No | A | DC leakage current at the maximum continuous voltage |
| `nonlinearityCoefficient` | number > 0 | No | — | Non-linearity exponent α (V = k * I^(1/α)) in the conduction region |

---

## thermistor.json

Describes a thermistor (NTC or PTC) — a temperature-dependent resistor for inrush current limiting, temperature sensing/compensation and overtemperature protection. **Scope**: ceramic NTC and PTC *thermistors* only; resettable polymer PTC fuses (PPTC / "polyfuse") are protection parts and out of RAS scope. Same outer shape as `resistor.json` / `varistor.json`: closed object with `manufacturerInfo` (same required `name` + `datasheetInfo`) and `distributorsInfo`, plus the same `anyOf` allowing an **empty pre-sourcing seed** (`{}`).

### thermistor datasheetInfo

**Required: `part`, `electrical`.**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `part` | object | Yes | Part identification — same base as the resistor `part`, with the thermistor technology enum |
| `electrical` | object | Yes | Thermistor electrical characteristics |
| `thermal` | [thermal](#thermal) | No | Shared thermal section |
| `mechanical` | [mechanical](#mechanical) | No | Shared flat mechanical section |
| `provenance` | array | No | Data-provenance trail |

### thermistor part

**Required: `partNumber`, `technology`.** Same fields as the resistor part (`series`, `case`, `description`, `matchcodeDescription`), with the thermistor technology enum (a named `$def`, `thermistor.json#/$defs/technology`, so requirement-side `allowedTechnologies` can `$ref` it):

| Value | Description |
|-------|-------------|
| `ntc` | Negative temperature coefficient — temperature sensing/compensation, inrush current limiting |
| `ptc` | Positive temperature coefficient ceramic thermistor — overtemperature sensing, self-regulating heating (NOT a resettable polymer PTC fuse) |

### thermistor electrical

**Required: `resistanceAt25C`.** Optional fields are plain numbers (not nullable) — omit what the datasheet does not state. The field surface matches the live distributor parametric columns (R @ 25 °C, B value, steady-state current max, energy) plus the physics constants every NTC/PTC datasheet publishes.

| Field | Type | Required | Unit | Description |
|-------|------|----------|------|-------------|
| `resistanceAt25C` | [dimensionWithTolerance](#dimensionwithtolerance) | Yes | Ohm | Zero-power resistance R25 at 25 °C |
| `resistanceTolerance` | number ≥ 0 | No | fraction | Tolerance on `resistanceAt25C` (`0.05` = ±5%) |
| `bConstant` | number > 0 | No | K | NTC B (beta) constant between the two `bConstantTemperatures`; PTC parts publish no B constant |
| `bConstantTemperatures` | number[2] | No | °C | The two reference temperatures qualifying `bConstant`, ascending (B25/85 → `[25, 85]`) |
| `maximumSteadyStateCurrent` | number ≥ 0 | No | A | Maximum continuous current — the headline rating of NTC inrush limiters |
| `maximumEnergy` | number ≥ 0 | No | J | Maximum single-event energy absorption (capacitive load rating) |
| `dissipationConstant` | number > 0 | No | W/K | Dissipation constant δth (power to raise the body 1 K above ambient in still air) |
| `thermalTimeConstant` | number > 0 | No | s | Thermal (cooling) time constant τc — 63.2% of the temperature step after power removal |
| `switchTemperature` | number | No | °C | PTC switch / reference temperature T_ref where resistance begins its steep rise (PTC only) |

---

## potentiometer.json

Describes a **potentiometer** — an adjustable three-terminal resistive divider (also covering rheostats and trimmers). Same outer shape as the other three members: a closed object with `manufacturerInfo` (required `name` + `datasheetInfo`) and `distributorsInfo`, plus the same `anyOf` allowing an **empty pre-sourcing seed** (`{}`).

### Why it is a separate member and not a `resistor`

A potentiometer **satisfies every field the fixed-resistor `electrical` block requires** — `resistance`, `tolerance`, `powerRating`. Filing one as a `resistor` therefore does **not** fail; it validates *silently* and quietly becomes wrong: nothing in the record would then say the part is adjustable, has a third terminal, has a taper, or has a wiper with its own current limit and contact resistance. `thermistor` is the precedent for splitting a member out of `resistor`, and a thermistor differs from a fixed resistor *less* than a potentiometer does.

The separation is enforced by naming, not by convention: the headline value is **`totalResistance`**, and `resistance` **does not exist** in `potentiometer.electrical`. A fixed-resistor electrical block therefore fails twice over — `resistance` is an unknown property, and `totalResistance` is missing.

### The model: two resistances summing to a constant

A potentiometer is one resistive track of constant end-to-end resistance, split by the wiper into two sections:

```
R_cw + R_ccw = totalResistance      at every wiper position
R_cw         = taper(wiperPosition) * totalResistance
```

`wiperPosition` (dimensionless, `0..1`) is the **design-time free variable** — a choice the design makes, not a fact read off a datasheet. It therefore lives on the *requirement* side (`designRequirements.wiperPosition`) and in `modelParams`, never in the part's `electrical` block.

### Units

All SI, with **one documented exception**: `actuation.mechanicalTravel` and `actuation.electricalTravel` are **in degrees** for a rotary part (they are in **metres** for a linear/slide part, where the pinned `type` const tells you which). Everything else is Ohm, W, V, A, metre, Celsius, or a dimensionless fraction, as elsewhere in RAS.

### potentiometer datasheetInfo

**Required: `part`, `electrical`.**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `part` | object | Yes | Part identification — PEAS part base plus the potentiometer technology enum |
| `electrical` | object | Yes | Track, taper and wiper characteristics |
| `thermal` | [thermal](#thermal) | No | Shared RAS thermal section |
| `mechanical` | object | No | Potentiometer-specific mechanical section (shaft, mounting, actuation) |
| `modelParams` | object | No | SPICE model parameters |
| `factors` | object | No | Power derating curve |
| `provenance` | array | No | Data-provenance trail |

### potentiometer part

**Required: `partNumber` (from the PEAS base), `technology`.** Composed as `allOf [ PEAS datasheetInfoPartBase, extension ]` sealed with top-level `unevaluatedProperties: false`, so `partNumber` / `series` / `case` / `description` are inherited rather than re-declared.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `technology` | string (enum) | Yes | Resistive-element material — see below |
| `adjustmentAccess` | string (enum) | No | `userAdjustable` (a control turned in service) or `trimmer` (set once at manufacture/calibration) |
| `matchcodeDescription` | string | No | Human-readable description of the part |

#### potentiometer technology enum values

A named `$def` (`potentiometer.json#/$defs/technology`) so requirement-side `allowedTechnologies` `$ref`s it and the two cannot drift.

| Value | Description |
|-------|-------------|
| `cermet` | Ceramic-metal thick film — the standard trimmer material |
| `carbonComposition` | Moulded carbon element — the commodity rotary material |
| `carbonFilm` | Printed carbon film |
| `conductivePlastic` | Polymer track — long life, low noise |
| `wirewound` | Resistance wire on a former — high power, stepwise (finite `resolution`) |
| `thickFilm` | Printed film on a substrate |
| `thinFilm` | Sputtered film on a substrate |

### potentiometer electrical

**Required: `totalResistance`.** Optional fields are plain numbers (not nullable) — omit what the datasheet does not state, matching the rest of RAS.

| Field | Type | Required | Unit | Description |
|-------|------|----------|------|-------------|
| `totalResistance` | [dimensionWithTolerance](#dimensionwithtolerance) | Yes | Ohm | End-to-end track resistance. The two wiper-split sections sum to this at every position |
| `resistanceTolerance` | number ≥ 0 | No | fraction | Tolerance on `totalResistance` (`0.2` = ±20%) |
| `powerRating` | number ≥ 0 | No | W | Power the whole track may dissipate at `powerRatingTemperature` |
| `powerRatingTemperature` | number | No | °C | Reference temperature for `powerRating` |
| `temperatureCoefficient` | number | No | ppm/K | Temperature coefficient of the track |
| `maximumWorkingVoltage` | number ≥ 0 | No | V | Maximum continuous voltage across the full track |
| `insulationResistance` | number ≥ 0 | No | Ohm | Element to case/shaft |
| `taper` | [taper](#potentiometer-taper) | No | — | The resistance-division law. **Absent means not yet sourced — it is not an assertion of linearity** |
| `wiper` | object | No | — | The moving contact — see below |
| `endResistance` | number ≥ 0 | No | Ohm | Residual resistance wiper-to-end at full travel; never zero on a real part |
| `independentLinearity` | number ≥ 0 | No | fraction | Maximum departure from the ideal taper (`0.005` = ±0.5%) |
| `resolution` | number > 0 | No | fraction | Smallest resistance step. Wirewound tracks only; continuous tracks omit it |
| `gangs` | integer ≥ 1 | No | — | Independent resistive sections on one actuator. `1` = single, `2` = dual |
| `gangTracking` | number ≥ 0 | No | fraction | Worst-case mismatch between gangs (`0.03` ≈ 0.26 dB). Only meaningful when `gangs > 1` |

#### wiper

The terminal a fixed resistor does not have. Closed object.

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `resistance` | number ≥ 0 | Ohm | Wiper contact resistance |
| `maximumCurrent` | number ≥ 0 | A | Maximum continuous wiper-terminal current — the rheostat-connection limit, usually far below the track's own capability |
| `contactResistanceVariation` | number ≥ 0 | fraction | CRV as a fraction of `totalResistance` — the noise spec of a moving contact |

### potentiometer taper

A **closed `oneOf` discriminated by a pinned `law` const**: every branch fixes its own `law` value, so a document lands in exactly one branch and cannot be silently misclassified. The `law` values are drawn from the named `$def` `potentiometer.json#/$defs/taperLaw`, which the requirement side also `$ref`s.

| `law` | Additional fields | Description |
|-------|-------------------|-------------|
| `linear` | — | `R_cw = position * totalResistance` |
| `logarithmic` | `sense` (**required**), `exponent` | Audio/volume taper. `sense` is `log` (standard audio "A": slow then steep) or `antiLog` (reverse-audio "C": steep then slow). **Required** because both curves are called "log" on datasheets and getting it wrong inverts the control. `exponent` is the optional fitted `n` in `R_cw/totalResistance = position^n` |
| `sShaped` | `centreResistanceFraction` | S-law / W-taper: two mirrored log segments meeting at the centre — balance and pan controls |
| `custom` | `curve` (**required**) | Any other law, as measured data: `x` = wiper position (`0..1`), `y` = `R_cw/totalResistance` (`0..1`). `custom` without the curve says nothing, so the curve is required |

### potentiometer mechanical

Extends the PEAS `datasheetInfoMechanical` base by `allOf`, sealed with top-level `unevaluatedProperties: false`, so it carries the base's `length` / `width` / `height` / `diameter` / `weight` / `shapeType` / `assemblyType` plus the fields below. It composes the PEAS base directly rather than the shared RAS `mechanical` because that `$def` is *sealed* and a sealed subschema cannot be extended; `case`, `pinout` and `landPattern` are re-referenced here (they are `$ref`s to the single PEAS definition, not copies of it).

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `case` | string | — | Package code (`"3296W"`, `"16 mm"`, `"Citec 23"`) |
| `pinout` | PEAS `pinout` | — | Per-terminal function map. Genuinely needed here: the three terminals are not interchangeable (CW end / wiper / CCW end), and a dual-gang part has six |
| `landPattern` | PEAS `landPattern` | — | Recommended PCB land pattern |
| `mounting` | string (enum) | — | `panel`, `board`, `bushing`, `chassis`, `surfaceMount` |
| `adjustmentSide` | string (enum) | — | `top`, `side`, `bottom`, `front`, `rear` — the face the adjuster is reached from |
| `terminalOrientation` | string (enum) | — | `vertical` (axis normal to the board) or `rightAngle` (axis in the board plane) |
| `shaft` | object | — | Shaft geometry — see below |
| `actuation` | [actuation](#potentiometer-actuation) | — | How the wiper moves, and over how much travel |
| `rotationalLife` | integer ≥ 0 | cycles | Rated mechanical life in full actuation cycles |

#### shaft

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `diameter` | [dimensionWithTolerance](#dimensionwithtolerance) | m | Shaft diameter (`6.35e-3` for a quarter-inch shaft) |
| `length` | [dimensionWithTolerance](#dimensionwithtolerance) | m | Shaft length beyond the bushing |
| `style` | string (enum) | — | `round`, `flatted`, `knurled`, `splined`, `slotted`, `screwdriverSlot`, `hex` |
| `material` | string | — | Shaft material as named on the datasheet |

### potentiometer actuation

A second **closed `oneOf` with a pinned `type` const**, because the quantities are not interchangeable: a rotary part has travel in **degrees** and a `turns` count; a linear (slide) part has travel in **metres** and no turns at all. Pinning the const is what stops a slide potentiometer acquiring a turns count.

| `type` | Fields | Description |
|--------|--------|-------------|
| `rotary` | `turns`, `mechanicalTravel` (**degrees**), `electricalTravel` (**degrees**), `detents`, `endStop` | Shaft- or screw-driven. `turns` is dimensionless: `1` for an ordinary control, `0.75` for a 270° trimmer, `25` for a multiturn trimmer (= `mechanicalTravel / 360`). `endStop` is `hardStop`, `continuous` or `clutched` |
| `linear` | `mechanicalTravel` (**metres**), `electricalTravel` (**metres**), `detents` | Slide / fader / linear-motion position sensor |

`electricalTravel` ≤ `mechanicalTravel` in both branches; the difference is the dead band at the ends.

### potentiometer modelParams

A potentiometer is emitted as two resistors sharing a wiper node. Closed object.

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `rTotal` | number > 0 | Ohm | End-to-end track resistance |
| `wiperPosition` | number 0..1 | fraction | **The design-time free variable** — the split point, measured from the low/CCW end |
| `rWiper` | number ≥ 0 | Ohm | Series wiper contact resistance |
| `taperExponent` | number > 0 | — | Exponent `n` in `R_cw/rTotal = wiperPosition^n`; `n = 1` is linear |

### potentiometer factors

| Field | Type | Description |
|-------|------|-------------|
| `powerDerating` | [deratingCurve](#deratingcurve) | Power derating curve for the whole track |

### Worked examples

- [`examples/05_potentiometer_3296w_trimmer.json`](../examples/05_potentiometer_3296w_trimmer.json) — a 10 kΩ 25-turn cermet trimmer: linear taper, rotary actuation with `turns`, clutched end stop, three-pin pinout, `modelParams` with the wiper at mid-travel.
- [`examples/06_potentiometer_te_citec_dual.json`](../examples/06_potentiometer_te_citec_dual.json) — a real TE Citec **dual-gang** carbon panel potentiometer, showing the shape of the catalogue data as actually sourced: `gangs: 2`, panel mounting, side adjustment, right-angle terminals, 6.35 × 50 mm shaft, and **`taper` and `turns` deliberately absent** because TE's parametric data does not carry them. The schema models them because a potentiometer *has* them; a record omits them until they are sourced.

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

Every `datasheetInfo` (resistor, varistor, thermistor and potentiometer) carries an optional `provenance` array recording where its data
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
