# RAS Schema Reference

Complete field-by-field documentation for the Resistor Agnostic Structure.

---

## Top-Level: RAS.json

The root document wraps a resistor with its design context.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `inputs` | object | Yes | Design requirements and operating points for this resistor |
| `resistor` | [resistor](#resistorjson) | Yes | The resistor component data |
| `outputs` | object or array | Yes | Computed results (power dissipation, temperature rise, etc.) |

**Schema ID**: `https://psma.com/ras/RAS.json`

---

## resistor.json

Describes a complete resistor component. The only top-level property is `manufacturerInfo`, which contains all data extracted from the manufacturer's datasheet.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `manufacturerInfo` | [manufacturerInfo](#manufacturerinfo) | Yes | Container for manufacturer-specific information |

---

## manufacturerInfo

Container that holds the datasheet-extracted data.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `datasheetInfo` | [datasheetInfo](#datasheetinfo) | Yes | Information extracted from the component datasheet |

---

## datasheetInfo

The main data block containing all resistor parameters organized into sections.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `part` | [part](#part) | Yes | Basic part identification |
| `electrical` | [electrical](#electrical) | Yes | Electrical characteristics |
| `thermal` | [thermal](#thermal) | No | Thermal characteristics |
| `mechanical` | [mechanical](#mechanical) | Yes | Mechanical dimensions and shape information |
| `business` | [business](#business) | No | Commercial and business information |
| `modelParams` | [modelParams](#modelparams) | No | SPICE model parameters |
| `factors` | [factors](#factors) | No | Derating factors for temperature |

---

## part

Basic part identification fields.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `partNumber` | string | Yes | Manufacturer part number (e.g., `"CRCW060310K0FKEA"`) |
| `series` | string or null | No | Product series name (e.g., `"CRCW"`, `"WSK2512"`) |
| `technology` | string (enum) | Yes | Resistor technology type |
| `case` | string | Yes | Case or package code (e.g., `"0603"`, `"2512"`) |
| `matchcodeDescription` | string or null | No | Human-readable description of the part |

### technology enum values

| Value | Description |
|-------|-------------|
| `thinFilm` | Thin film -- sputtered metal alloy on ceramic substrate. Low TCR, tight tolerance. |
| `thickFilm` | Thick film -- printed resistive paste on ceramic. General purpose, low cost. |
| `wirewound` | Wirewound -- resistance wire wound on a core. High power, precise, but inductive. |
| `carbonComposition` | Carbon composition -- carbon particles in a binder. High pulse handling. |
| `metalOxide` | Metal oxide -- metal oxide film on ceramic. High voltage, flame-proof. |
| `foil` | Foil -- precision metal foil on ceramic. Ultra-low TCR, highest precision. |
| `shunt` | Shunt -- metal alloy strip for current sensing. Very low resistance (mOhm range). |

---

## electrical

Electrical characteristics of the resistor.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `resistance` | [dimensionWithTolerance](#dimensionwithtolerance) | Yes | Nominal resistance in Ohms. Uses `dimensionWithTolerance` -- typically only `nominal` is specified, since the separate `tolerance` field captures the percentage. |
| `tolerance` | number | Yes | Resistance tolerance as a fraction. `0.01` = 1%, `0.001` = 0.1%. |
| `temperatureCoefficient` | number or null | No | Temperature coefficient of resistance (TCR) in ppm/K. Typical values: thin film 5-50, thick film 100-200, foil <1. |
| `powerRating` | number | Yes | Maximum continuous power dissipation in Watts at the reference temperature. |
| `powerRatingTemperature` | number or null | No | Reference temperature (in Celsius) at which `powerRating` applies. Typically 70 C for SMD resistors. Above this temperature, the power must be derated per the `factors` section. |
| `maxVoltage` | number or null | No | Maximum continuous working voltage in Volts. For high-resistance values, this may limit power before the wattage rating does (P = V^2/R). |
| `maxOverloadVoltage` | number or null | No | Maximum overload voltage in Volts (short-duration stress test per IEC 60115). |
| `insulationResistance` | number or null | No | Insulation resistance in Ohms (typically > 1 GOhm). |
| `noiseIndex` | number or null | No | Current noise index in dB. Lower is better. Relevant for thin film and foil types. |

---

## thermal

Thermal characteristics.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `operatingTemperature` | [dimensionWithTolerance](#dimensionwithtolerance) or null | No | Operating temperature range in Celsius. Uses `minimum` and `maximum` fields (e.g., `{"minimum": -55, "maximum": 155}`). |

---

## mechanical

Mechanical dimensions and package information.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `dimensions` | [dimensions](#dimensions) | No | Physical dimensions of the component |
| `shape` | [shape](#shape) | Yes | Shape and assembly type |

### dimensions

Physical dimensions. All values in meters (SI).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `width` | [dimensionWithTolerance](#dimensionwithtolerance) or null | No | Width in meters |
| `length` | [dimensionWithTolerance](#dimensionwithtolerance) or null | No | Length in meters |
| `height` | [dimensionWithTolerance](#dimensionwithtolerance) or null | No | Height in meters |

### shape

Component shape and assembly information.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `assembly` | string (enum) | Yes | Assembly type: `"SMT"` (surface mount), `"THT"` (through-hole), or `"Chassis"` (chassis-mounted) |
| `shapeType` | string | Yes | Package shape type (e.g., `"SMD Chip"`, `"Axial"`, `"MELF"`) |

---

## business

Commercial and supply chain information.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `packaging` | string or null | No | Packaging format (e.g., `"Tape & Reel"`, `"Cut Tape"`, `"Bulk"`) |
| `vpe` | integer or null | No | Units per package/reel |
| `moq` | integer or null | No | Minimum order quantity |
| `priceCost` | number or null | No | Cost price per unit |

---

## modelParams

SPICE model parameters for circuit simulation. These map directly to the standard SPICE resistor model.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `r` | number or null | No | Resistance in Ohms (same as `electrical.resistance.nominal`) |
| `tcr1` | number or null | No | First-order temperature coefficient in 1/K. This is the `temperatureCoefficient` value converted from ppm/K to 1/K: divide by 1e6. Example: 100 ppm/K = `100e-6`. |
| `tcr2` | number or null | No | Second-order temperature coefficient in 1/K^2. Usually null for standard resistors; relevant for precision types. |

The SPICE temperature model is: `R(T) = R * (1 + tcr1*(T-Tnom) + tcr2*(T-Tnom)^2)`

---

## factors

Derating factors that define how the maximum power rating decreases with temperature.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `powerDeratingTemperature` | number[] | No | Temperature values (in Celsius) defining the derating curve breakpoints. Must be sorted in ascending order. |
| `powerDeratingAmplitude` | number[] | No | Power derating factors (fraction of rated power, 0.0 to 1.0) at the corresponding temperatures. Same length as `powerDeratingTemperature`. |

**Example**: A resistor rated 0.1W at 70 C that derates to zero at 155 C:

```json
{
    "powerDeratingTemperature": [70, 100, 125, 155],
    "powerDeratingAmplitude": [1.0, 0.65, 0.35, 0.0]
}
```

At 100 C, the maximum allowed power is `0.1W * 0.65 = 0.065W`.

---

## Shared Types (utils.json)

### dimensionWithTolerance

A dimension with minimum, nominal, and maximum values. At least one of the three fields must be present.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `minimum` | number | At least one required | The minimum value |
| `nominal` | number | At least one required | The nominal value |
| `maximum` | number | At least one required | The maximum value |

**Usage in RAS**:
- `resistance`: typically only `nominal` (e.g., `{"nominal": 10000}`)
- `operatingTemperature`: uses `minimum` and `maximum` (e.g., `{"minimum": -55, "maximum": 155}`)
- `dimensions`: typically only `nominal` (e.g., `{"nominal": 0.0016}`)

### curve

X-Y curve data points for piecewise-linear characteristics.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `xData` | number[] | No | X-axis values |
| `yData` | number[] | No | Y-axis values |

### numberArray

An array of numeric values. Used by `powerDeratingTemperature`, `powerDeratingAmplitude`, and curve data.

```json
[70, 100, 125, 155]
```
