import json
import numpy as np
from components import Resistor, Inductor, Capacitor
import matplotlib.pyplot as plt

class TransientSimulator: #класс симуляция перех процессов
    def __init__(self, config_path: str):#принимает путь к JSON-файлу
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self.dt = self.config['dt']
        self.duration = self.config['duration']
        self.voltage = self.config.get('voltage', 10.0)
        self.source_node = self.config.get('source_node', 1)
        self.circuit_type = self.config.get('circuit_type', 'unknown')
        self.components = [] #create список для элементов цепи
        self._create_components() #вызов метода заполнения списка

    def _create_components(self):
        comp_map = { # "переводчик" - если R - значит создается обьект класса резистор
            "R": Resistor,
            "L": Inductor,
            "C": Capacitor
        }
        for comp_data in self.config['components']: #взяли элемент из списка, посмотрели к какому типу относится
            #cоздали обьект нужного класс и добавили в списочек components []
            cls = comp_map[comp_data['type']]
            self.components.append(cls(
                node_begin=comp_data['node1'],
                node_end=comp_data['node2'],
                value=comp_data['value']
            ))

    def _get_max_node(self): #поиск самого большого номера узла
        max_node = 0
        for comp in self.components:
            max_node = max(max_node, comp.node_begin, comp.node_end) #поиск наибольшего среди нач конечного и нулевого как заданного в начале 0
        return max_node

    def run(self, plot: bool = True): #запуск симуляции с рисованием графиков в случае true
        # но у меня стоит False чтобы компьютер не взорвался
        num_steps = int(self.duration / self.dt) #cколько шагов по времени (общее время на время симуляции делить)
        times = np.arange(0, self.duration, self.dt)
        currents = []

        max_node = self._get_max_node() #запуск возвращение самого большого узла
        source_idx = self.source_node - 1 if self.source_node > 0 else -1
        #тернарный оператор, чтобы не писать долгий цикл for:if else
        #Если self.source_node больше 0 (обычно это узел 1), то:
#source_idx = self.source_node - 1  превращаем номер узла в индекс массива 0, 1, 2..
#Если source_node равен 0 или меньше — source_idx = -1 значит источника нет.

        for step in range(num_steps): #Повтори всё, что будет дальше ровно столько раз сколько мы посчитали шагов по времени
            # Строим матрицу Y и вектор J
            Y = np.zeros((max_node, max_node)) #матрица нульчиков
            J = np.zeros(max_node)

            for comp in self.components: #для каждого элемента схемы
                g = comp.get_conductance(self.dt) #проводимость в текущий момент времени
                j_hist = comp.get_history_current(self.dt) #ток на текущем шаге
                n1 = comp.node_begin - 1 # номер узла -> индекс массива
                n2 = comp.node_end - 1

                if n1 >= 0:
                    Y[n1, n1] += g
                    J[n1] -= j_hist
                if n2 >= 0:
                    Y[n2, n2] += g
                    J[n2] += j_hist
                if n1 >= 0 and n2 >= 0: #
                    Y[n1, n2] -= g
                    Y[n2, n1] -= g

            # метод Доммеля
            if source_idx >= 0: # наличие источника в схеме
                Y[source_idx, :] = 0 #обнулить всю строку матрицы
                Y[source_idx, source_idx] = 1 #напряжение в узле равно какому то значению на пересеч строки и столбцы
                J[source_idx] = self.voltage

            # Решаем систему уравнений
            try:
                v = np.linalg.solve(Y, J)
            except np.linalg.LinAlgError: #если при решении матрицы выходит бред, то заполнить нулями
                v = np.zeros(max_node)

            # Вычисляем ток
            current = 0.0
            if self.components:
                comp = self.components[0] #взяли первый эл-т, если rl -> взяли r
                v_b = self.voltage if comp.node_begin == self.source_node else (v[comp.node_begin-1] if comp.node_begin > 0 else 0.0)
                #если нач узел эл-та совпадает с узлом ист, тогда напр-е - напр-е источ
                v_e = v[comp.node_end-1] if comp.node_end > 0 else 0.0
                # потенциал на конце эл-та если заземлен то U = 0
                current = comp.get_conductance(self.dt) * (v_b - v_e) + comp.get_history_current(self.dt) #метод Доммеля расчета тока

            currents.append(current)

            # Обновляем состояние компонентов
            for comp in self.components: #проход по всем элементам и обновление их состояний
                v_b = self.voltage if comp.node_begin == self.source_node else (v[comp.node_begin-1] if comp.node_begin > 0 else 0.0)
                v_e = v[comp.node_end-1] if comp.node_end > 0 else 0.0
                curr = comp.get_conductance(self.dt) * (v_b - v_e) + comp.get_history_current(self.dt)
                comp.update_state(v_b, v_e, curr)

        print(f"✓ Симуляция '{self.circuit_type}' завершена")

        if plot:
            plt.figure(figsize=(10, 5))
            plt.plot(times[:len(currents)], currents, label='Ток, А')
            plt.xlabel('Время, с')
            plt.ylabel('Ток, А')
            plt.title(f'Переходный процесс — {self.circuit_type}')
            plt.grid(True)
            plt.legend()
            plt.show()

        return currents[-1] if currents else 0.0