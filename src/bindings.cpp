// PyRAS — pybind11 module exposing the RAS->CIAS converter.
#include <pybind11/pybind11.h>
#include <pybind11_json/pybind11_json.hpp>
#include "RasConverter.hpp"
#include "FidelityJson.hpp"

namespace py = pybind11;
using json = nlohmann::json;

PYBIND11_MODULE(PyRAS, m) {
    m.doc() = "RAS (resistor) -> CIAS leaf converter";
    m.def("ras_to_cias",
          [](const json& peas, const json& fidelity, const std::string& name) {
              return RAS::ras_to_cias(peas, PEAS::fidelity_from_json(fidelity), name);
          },
          py::arg("peas"), py::arg("fidelity"), py::arg("name") = "resistor",
          "Convert a RAS resistor PEAS document to a CIAS leaf. fidelity = "
          "{origin: REQUIREMENTS|DATASHEET|MKF_MODEL, allowStoredModelParams?: bool, curveFit?: str}.");
}
