#pragma once

// RasConverter — "generate a CIAS element (leaf) from a RAS part".
//
// ras_to_cias(peas, fidelity) returns a small CIAS brick (a "leaf") whose components are
// ideal-atom PEAS parts and whose connections wire them. The leaf is the equivalent circuit of
// ONE resistor:
//   - REQUIREMENTS (ideal): a single ideal resistor, value from inputs.designRequirements.resistance.
//   - DATASHEET   (real)  : a resistor from datasheetInfo.electrical.resistance (or modelParams.r,
//                           only when fidelity.allowStoredModelParams). Series-L / shunt-C parasitic
//                           synthesis (RAS has no parasitic field) is the next step (Phase 4) — it is
//                           tracked, not silently skipped.
//   - MKF_MODEL           : throws (MAS-only origin).
//
// Input `peas` is a PEAS resistor document ({"resistor": {...}, "inputs": {...}}). Output is CIAS
// JSON ({name, ports, components, connections}) — never persisted, so it need not validate against
// CIAS.json; it is consumed by the CIAS converter which emits the SPICE/PSIM/... cards.
//
// Convention: a resistor's two terminals are pins "1" and "2".

#include <nlohmann/json.hpp>
#include <string>
#include "Fidelity.hpp"

namespace RAS {

// peas: a PEAS resistor document. Returns a CIAS leaf brick as JSON.
nlohmann::json ras_to_cias(const nlohmann::json& peas,
                           const PEAS::Fidelity& fidelity,
                           const std::string& name = "resistor");

} // namespace RAS
