from components.base import Component

class Inductor(Component):
    def __init__(self, branch_id, node_begin, node_end, L, i0=0.0):
        super().__init__(branch_id, node_begin, node_end)
        self.L = L
        self.current = i0
        self.prev_voltage = 0.0
        self.R_eq = 1.0

    def get_R(self, h):
        self.R_eq = 2.0 * self.L / h
        return self.R_eq

    def get_E(self, h):
        # solver считает ток ветви так: I = Y * (A^T U + E) Поэтому здесь нужен "добавочный" E_add = R_eq * i_n + u_n
        # i_(n+1) = (u_(n+1) + E_add) / R_eq  = (u_(n+1) + R_eq*i_n + u_n) / R_eq что эквивалентно по Доммелю
        return self.R_eq * self.current + self.prev_voltage

    def update_state(self, voltage, current, h):
        self.current = current
        self.fi_begin = voltage[0]
        self.fi_end = voltage[1]
        self.prev_voltage = self.fi_begin - self.fi_end