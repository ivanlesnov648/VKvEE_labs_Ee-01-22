import math
from components.base import Component


class CurrentSource(Component): #класс источника тока  , амплитуда синусоиды переменного источника, частота
    def __init__(self, branch_id, node_begin, node_end, J=0.0, amplitude=None, frequency=None):
        super().__init__(branch_id, node_begin, node_end)
        self.J = J
        self.amplitude = amplitude
        self.frequency = frequency
        self.time = 0.0

    def get_R(self, h):
        return 1e12

    def get_E(self, h):
        return 0.0

    def get_J(self):
        if self.amplitude is not None and self.frequency is not None:
            return self.amplitude * math.sin(2 * math.pi * self.frequency * self.time)
        return self.J

    def update_time(self, t):
        self.time = t

    def update_state(self, voltage, current, h):
        self.current = current
        self.fi_begin = voltage[0]
        self.fi_end = voltage[1]