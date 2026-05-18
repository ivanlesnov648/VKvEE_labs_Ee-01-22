import math
from components.base import Component


class VoltageSource(Component):
    def __init__(self, branch_id, node_begin, node_end, E=0.0, amplitude=None, frequency=None):
        super().__init__(branch_id, node_begin, node_end)
        self.E = E
        self.amplitude = amplitude
        self.frequency = frequency
        self.time = 0.0

    def get_R(self, h):
        return 1e-9

    def get_E(self, h):
        if self.amplitude is not None and self.frequency is not None:
            return self.amplitude * math.sin(2 * math.pi * self.frequency * self.time)
        return self.E

    def update_time(self, t):
        self.time = t

    def update_state(self, voltage, current, h):
        self.current = current
        self.fi_begin = voltage[0]
        self.fi_end = voltage[1]