import json
from ЛР3.components.resistor import Resistor
from components.inductor import Inductor
from components.capacitor import Capacitor
from ЛР3.components.voltage_source import VoltageSource
from components.current_source import CurrentSource


class CircuitParser:
    def __init__(self, filename):
        self.filename = filename

    def create_component(self, item):
        t = item["type"].lower()

        if t == "r":
            return Resistor(item["branch"], item["from"], item["to"], item["R"])
        elif t == "l":
            return Inductor(
                item["branch"],
                item["from"],
                item["to"],
                item["L"],
                item.get("i0", 0.0)
            )
        elif t == "c":
            return Capacitor(
                item["branch"],
                item["from"],
                item["to"],
                item["C"],
                item.get("u0", 0.0)
            )
        elif t == "v":
            return VoltageSource(
                item["branch"],
                item["from"],
                item["to"],
                item.get("E", 0.0),
                item.get("amplitude"),
                item.get("frequency")
            )
        elif t == "j":
            return CurrentSource(
                item["branch"],
                item["from"],
                item["to"],
                item.get("J", 0.0),
                item.get("amplitude"),
                item.get("frequency")
            )
        else:
            raise ValueError(f"Неизвестный тип компонента: {t}")

    def parse(self):
        with open(self.filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        h = data["time_step"]
        nodes = data["nodes"]
        components = [self.create_component(item) for item in data["branches"]]

        return h, nodes, components