import numpy as np
from ЛР3.components.voltage_source import VoltageSource
from components.current_source import CurrentSource


class CircuitSolver: #число узлов в схеме, список элементиков и шаг по времени
    #в хранится матрица из 1 -1  и 0, в строке начального узла +1 в строке кон узла -1, в остальных 0
    def __init__(self, nodes, components, h):
        self.nodes = nodes
        self.components = sorted(components, key=lambda x: x.branch_id) #список компонентов сортируется по branch id, чтобы ветви всегда шли в одном порядке
        self.h = h
        self.time = 0.0

    def build_A(self): #построение матрицы соединений А q - число узлов в схеме p - число элементов схемы(число ветвей)
        q = self.nodes
        p = len(self.components)
        A = np.zeros((q - 1, p)) #Создается нулевая матрица размера р q-1, - потому что берется один узел за нулевой

        for j, comp in enumerate(self.components): #перебираем все компоненты по ветвям
            nb = comp.node_begin #нач узел и ниже конечный узел
            ne = comp.node_end

            if nb != 0:
                A[nb - 1, j] = 1 # начальному узлу ставится 1 если он не нулевой, такая же логика с конечным узлом но только -1
            if ne != 0:
                A[ne - 1, j] = -1

        return A

    def build_Y_E_J(self): #построение матрицы и векторы ветвей
        p = len(self.components)
        Y = np.zeros((p, p)) #матрица проводимостей квадратная
        E = np.zeros((p, 1))
        J = np.zeros((p, 1))

        for i, comp in enumerate(self.components):
            if isinstance(comp, (VoltageSource, CurrentSource)): #если элемент - источник E/J, то ему нужно обновить время текущее
                comp.update_time(self.time)

            R = comp.get_R(self.h) #берем эквивалентное сопротивление ветви
            Y[i, i] = 1.0 / R
            E[i, 0] = comp.get_E(self.h)

            if isinstance(comp, CurrentSource):
                J[i, 0] = comp.get_J()

        return Y, E, J

    def step(self): #
        A = self.build_A()
        Y, E, J = self.build_Y_E_J()

        left = A @ Y @ A.T #формируется левая часть уравнения @ - поэлементное умножение
        right = -A @ (J + Y @ E) #правая часть уравнения

        U = np.linalg.solve(left, right) #решается система линейных уравнений

        branch_voltages = A.T @ U + E #вычисл напряжения по ветвям
        I = Y @ branch_voltages + J #токи во всех ветвях

        for i, comp in enumerate(self.components): #теперь перебираются все элементы и им даются новые значения
            nb = comp.node_begin
            ne = comp.node_end

            vb = U[nb - 1, 0] if nb != 0 else 0.0 #потенциал начального узла
            ve = U[ne - 1, 0] if ne != 0 else 0.0

            comp.update_state((vb, ve), I[i, 0], self.h) #каждому компоненту передается новое состояние

        self.time += self.h #увеличиваем текущее время на один шаг
        return U, I