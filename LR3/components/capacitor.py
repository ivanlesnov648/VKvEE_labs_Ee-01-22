from components.base import Component


class Capacitor(Component):
    def __init__(self, branch_id, node_begin, node_end, C, u0=0.0):
        super().__init__(branch_id, node_begin, node_end)
        self.C = C
        self.prev_voltage = u0
        self.current = 0.0

    def get_R(self, h):
        return h / (2 * self.C)

    def get_E(self, h):
        return -(self.prev_voltage + self.get_R(h) * self.current)

    def update_state(self, voltage, current, h): #нужен, чтобы после расчёта очередного шага по времени сохранить новое состояние элемента.
        self.current = current
        self.fi_begin = voltage[0]
        self.fi_end = voltage[1]
        self.prev_voltage = self.fi_begin - self.fi_end