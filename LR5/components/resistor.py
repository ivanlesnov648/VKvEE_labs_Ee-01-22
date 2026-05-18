from .base import Component

class Resistor(Component):
    def get_conductance(self, dt: float) -> float:
        return 1.0 / self.value

    def get_history_current(self, dt: float) -> float:
        return 0.0