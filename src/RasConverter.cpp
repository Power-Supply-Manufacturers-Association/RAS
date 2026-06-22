#include "RasConverter.hpp"
#include "RAS.hpp"        // quicktype-generated typed structs (build/RAS.hpp)
#include "Dimension.hpp"  // PEAS::resolve_dimensional_values

#include <optional>
#include <stdexcept>

namespace RAS {

using nlohmann::json;

namespace {

// The chosen resistance value, per the fidelity origin.
double resolve_resistance(const json& peas, const PEAS::Fidelity& fidelity) {
    using Origin = PEAS::Fidelity::Origin;
    PEAS::reject_mkf_model(fidelity, "RAS");

    if (fidelity.origin == Origin::REQUIREMENTS) {
        if (!peas.contains("inputs") || !peas.at("inputs").contains("designRequirements"))
            throw std::runtime_error("RAS ideal: inputs.designRequirements missing");
        auto dr = peas.at("inputs").at("designRequirements").get<DesignRequirements>();
        if (!dr.get_resistance())
            throw std::runtime_error("RAS ideal: designRequirements.resistance missing");
        return PEAS::resolve_dimensional_values(*dr.get_resistance());
    }

    // DATASHEET (real): physical electrical.resistance by default; stored modelParams.r only when
    // explicitly allowed.
    if (!peas.contains("resistor"))
        throw std::runtime_error("RAS real: 'resistor' component missing from PEAS document");
    auto resistor = peas.at("resistor").get<Resistor>();
    const auto& datasheet = resistor.get_manufacturer_info().get_datasheet_info();

    if (fidelity.allowStoredModelParams) {
        if (auto mp = datasheet.get_model_params()) {
            if (mp->get_r()) return *mp->get_r();
        }
    }
    return PEAS::resolve_dimensional_values(datasheet.get_electrical().get_resistance());
}

// A minimal ideal-resistor PEAS document carrying just the value — the leaf atom the CIAS
// converter reads (resistor...electrical.resistance.nominal) to emit an R card. Built with
// explicit assignment to avoid nlohmann brace-init ambiguity.
json make_resistor_atom(double r) {
    json electrical;
    electrical["resistance"]["nominal"] = r;
    electrical["tolerance"] = 0.0;
    electrical["powerRating"] = 0.0;

    json datasheet;
    datasheet["part"]["partNumber"] = "ideal";
    datasheet["part"]["technology"] = "thickFilm";
    datasheet["electrical"] = electrical;

    json atom;
    atom["resistor"]["manufacturerInfo"]["name"] = "ideal";
    atom["resistor"]["manufacturerInfo"]["datasheetInfo"] = datasheet;
    return atom;
}

// One CIAS net that lands on a component pin and exposes a brick port of the same name.
json pin_port_net(const std::string& net, const std::string& comp,
                  const std::string& pin, const std::string& port) {
    json endpoints = json::array();
    endpoints.push_back(json{{"component", comp}, {"pin", pin}});
    endpoints.push_back(json{{"port", port}});
    return json{{"name", net}, {"endpoints", endpoints}};
}

} // namespace

json ras_to_cias(const json& peas, const PEAS::Fidelity& fidelity, const std::string& name) {
    const double r = resolve_resistance(peas, fidelity);

    // Leaf: 2 ports ("1","2"), one ideal-resistor atom, two nets each exposing a port.
    // NOTE: real (DATASHEET) parasitic series-L / shunt-C synthesis is Phase 4 — to be added as
    // extra atoms + connections here; currently a real resistor's leaf is a single R (the dominant
    // term), tracked in PLAN.md, not a silent omission.
    json ports = json::array();
    ports.push_back(json{{"name", "1"}});
    ports.push_back(json{{"name", "2"}});

    json components = json::array();
    components.push_back(json{{"name", "R"}, {"data", make_resistor_atom(r)}});

    json connections = json::array();
    connections.push_back(pin_port_net("1", "R", "1", "1"));
    connections.push_back(pin_port_net("2", "R", "2", "2"));

    json leaf;
    leaf["name"] = name;
    leaf["ports"] = ports;
    leaf["components"] = components;
    leaf["connections"] = connections;
    return leaf;
}

} // namespace RAS
