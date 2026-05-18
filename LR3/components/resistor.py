from components.base import Component


class Resistor(Component):
    def __init__(self, branch_id, node_begin, node_end, R):
        super().__init__(branch_id, node_begin, node_end)
        self.R = R

    def get_R(self, h):
        return self.R

    def get_E(self, h):
        return 0.0