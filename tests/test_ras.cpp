// Minimal dependency-free unit tests for ras_to_cias.
#include "RasConverter.hpp"
#include "Fidelity.hpp"
#include <nlohmann/json.hpp>
#include <iostream>
#include <string>

using nlohmann::json;
using PEAS::Fidelity;

#include <catch2/catch_test_macros.hpp>
#define CHECK_MSG(cond, ...) do { INFO(__VA_ARGS__); CHECK(cond); } while (0)

// Pull the resistance value the CIAS converter would later read out of an emitted leaf.
static double leaf_resistance(const json& leaf) {
    const auto& comp = leaf.at("components").at(0);
    return comp.at("data").at("resistor").at("manufacturerInfo").at("datasheetInfo")
               .at("electrical").at("resistance").at("nominal").get<double>();
}

TEST_CASE("RAS ras_to_cias", "[ras]") {
    // --- ideal (REQUIREMENTS): value from designRequirements.resistance ---
    json idealDoc = json::parse(R"({
        "resistor": { "manufacturerInfo": { "name": "stub", "datasheetInfo": {
            "part": { "partNumber": "X", "technology": "thickFilm" },
            "electrical": { "resistance": { "nominal": 999.0 }, "tolerance": 0.01, "powerRating": 0.25 } } } },
        "inputs": { "designRequirements": { "deviceType": "resistor",
            "resistance": { "nominal": 1000.0 }, "powerRating": 0.25 } }
    })");
    json leaf = RAS::ras_to_cias(idealDoc, Fidelity(Fidelity::Origin::REQUIREMENTS));
    CHECK_MSG(leaf.at("name") == "resistor", "ideal: leaf name");
    CHECK_MSG(leaf.at("ports").size() == 2, "ideal: 2 ports");
    CHECK_MSG(leaf.at("components").size() == 1, "ideal: 1 component");
    CHECK_MSG(leaf.at("components").at(0).at("name") == "R", "ideal: component R");
    CHECK_MSG(leaf.at("connections").size() == 2, "ideal: 2 connections");
    CHECK_MSG(leaf_resistance(leaf) == 1000.0, "ideal: value from designRequirements (1000)");

    // --- real (DATASHEET): value from electrical.resistance, not modelParams (stored OFF) ---
    json realDoc = json::parse(R"({
        "resistor": { "manufacturerInfo": { "name": "Vishay", "datasheetInfo": {
            "part": { "partNumber": "CRCW0402470R", "technology": "thickFilm" },
            "electrical": { "resistance": { "nominal": 470.0 }, "tolerance": 0.01, "powerRating": 0.063 },
            "modelParams": { "r": 471.5 } } } }
    })");
    json realLeaf = RAS::ras_to_cias(realDoc, Fidelity(Fidelity::Origin::DATASHEET));
    CHECK_MSG(leaf_resistance(realLeaf) == 470.0, "real: value from electrical.resistance (470)");

    // --- real with allowStoredModelParams: prefer modelParams.r ---
    json storedLeaf = RAS::ras_to_cias(realDoc, Fidelity(Fidelity::Origin::DATASHEET, /*allowStored*/true));
    CHECK_MSG(leaf_resistance(storedLeaf) == 471.5, "real+allowStored: value from modelParams.r (471.5)");

    // --- resolve_dimensional_values: NOMINAL averages min+max when nominal absent ---
    json rangeDoc = json::parse(R"({
        "inputs": { "designRequirements": { "deviceType": "resistor",
            "resistance": { "minimum": 900.0, "maximum": 1100.0 }, "powerRating": 0.25 } }
    })");
    json rangeLeaf = RAS::ras_to_cias(rangeDoc, Fidelity(Fidelity::Origin::REQUIREMENTS));
    CHECK_MSG(leaf_resistance(rangeLeaf) == 1000.0, "resolve: NOMINAL averages (900+1100)/2 = 1000");

    // --- MKF_MODEL must throw for RAS ---
    bool threw = false;
    try { RAS::ras_to_cias(realDoc, Fidelity(Fidelity::Origin::MKF_MODEL)); }
    catch (const std::exception&) { threw = true; }
    CHECK_MSG(threw, "MKF_MODEL origin throws for RAS");

}
