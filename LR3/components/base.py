from abc import ABC, abstractmethod

'branch id - номер ветви, node end - начальный конечный узел'
class Component(ABC):
    def __init__(self, branch_id, node_begin, node_end):
        self.branch_id = branch_id
        self.node_begin = node_begin
        self.node_end = node_end
        self.fi_begin = 0.0 #потенциал
        self.fi_end = 0.0
        self.current = 0.0

    def get_R(self, h):
        pass


    def get_E(self, h):
        pass

    def update_state(self, voltage, current, h):   #метод обновления состояния эл-та
        self.current = current
        self.fi_begin = voltage[0] #берем первый элементы массива и записываем как начальный потенциал узла
        self.fi_end = voltage[1] #второй эл-т массива - потенциал конечный узла

    def set_fi_begin(self, value):
        self.fi_begin = value

    def set_fi_end(self, value):
        self.fi_end = value

    def set_current(self, value):
        self.current = value

    def get_node_begin(self):  #метод для получения начального узла(геттер) возвращает номер начального узла
        return self.node_begin

    def get_node_end(self):
        return self.node_end