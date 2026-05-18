from abc import ABC, abstractmethod

class Component(ABC): #родительский класс унаследование крч идет отсюда классов емкости индукт и рез-ра
    def __init__(self, node_begin: int, node_end: int, value: float):
        self.node_begin = node_begin # номер нач узла
        self.node_end = node_end
        self.value = value #характерное значение элемента(Ом,Гн,Ф)
        self.current_prev = 0.0# нач напр-е до симуляции
        self.voltage_prev = 0.0 #аналогично ток

    @abstractmethod #декоратор -
    #Любой класс, который будет наследовать от Component(R C L),
    #должен сам написать свою версию этого метода.
    def get_conductance(self, dt: float) -> float:#метод возвращаюсь проводимость принимая на вход параметр, шаг по времени и возвращает с плав точкой число
        pass

    @abstractmethod
    def get_history_current(self, dt: float) -> float: #возвращает ток с плав точкой
        pass

    def update_state(self, v_begin: float, v_end: float, current: float): #параметры закидываем: ток, потенциал на нач узле и конечном
        self.voltage_prev = v_begin - v_end
        self.current_prev = current