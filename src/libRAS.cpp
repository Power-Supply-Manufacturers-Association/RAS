// libRAS — emscripten/embind module exposing the RAS->CIAS converter to JS/WASM.
// JSON-string-in / JSON-string-out, exceptions returned as "Exception: ..." (MKF/WebLibMKF pattern).
#include <emscripten/bind.h>
#include "RasConverter.hpp"
#include "FidelityJson.hpp"
#include <nlohmann/json.hpp>
#include <string>

using json = nlohmann::json;

static std::string ras_to_cias_json(std::string peasStr, std::string fidelityStr) {
    try {
        auto leaf = RAS::ras_to_cias(json::parse(peasStr),
                                     PEAS::fidelity_from_json(json::parse(fidelityStr)));
        return leaf.dump();
    } catch (const std::exception& e) {
        return std::string("Exception: ") + e.what();
    }
}

EMSCRIPTEN_BINDINGS(ras) {
    emscripten::function("ras_to_cias", &ras_to_cias_json);
}
