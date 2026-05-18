from .base import Component

class Inductor(Component):
    def get_conductance(self, dt: float) -> float:
        return dt / (2.0 * self.value)

    def get_history_current(self, dt: float) -> float:
        g = self.get_conductance(dt)
        return self.current_prev + g * self.voltage_prev