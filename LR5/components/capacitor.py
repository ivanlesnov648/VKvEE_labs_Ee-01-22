from .base import Component

class Capacitor(Component):
    def get_conductance(self, dt: float) -> float:
        return (2.0 * self.value) / dt

    def get_history_current(self, dt: float) -> float:
        g = self.get_conductance(dt)
        return -g * self.voltage_prev - self.current_prev