import os
import matplotlib.pyplot as plt
from parser import CircuitParser
from solver import CircuitSolver


def run_simulation(config_file, t_end=0.05): #расчет схемы по времени
    parser = CircuitParser(config_file)
    h, nodes, components = parser.parse()

    solver = CircuitSolver(nodes, components, h) #решает схему с конкретным шагом

    steps = int(t_end / h) #количество шагов моделирования
    time = [] #в него записывается время после каждого шага
    currents = [[] for _ in components] #для каждого компонента свой список например если rlc то [] [] []
    voltages = [[] for _ in range(nodes - 1)]#список напряжений для каждого компонента, -1 потому что нулевой потенциал не считаем

    for _ in range(steps):
        U, I = solver.step()
        time.append(solver.time) #в список добавляется время текущее, ниже соответственно токи и напряжения

        for i in range(len(components)):
            currents[i].append(I[i, 0])

        for i in range(nodes - 1):
            voltages[i].append(U[i, 0])

    return time, currents, voltages, components


def plot_results(time, currents, voltages, components, file_name="scheme", save_path=None):
    fig, axes = plt.subplots(2, 1, figsize=(12, 8)) #создается фигура с двумя графиками, 2 1 - 2 сроки один столбец, то есть нижний и верхний график

    ax1 = axes[0] #верхний график и ниже нижний график
    ax2 = axes[1]

    comp_names = [comp.__class__.__name__ for comp in components] #cоздает список имен классов компонентов
    file_lower = file_name.lower() #имя файла переводится в нижний регистр
    # ВЕРХНИЙ ГРАФИК — ТОКИ
    if "resistors_series" in file_lower or "resistors_parallel" in file_lower: #если имя файлика содержит строку одну из этих, то значит схемка с резисторами
        for i, comp in enumerate(components):
            if comp.__class__.__name__ == "Resistor":
                ax1.plot(time, currents[i], linewidth=2, label=f"I через Resistor #{i}")

    elif "rl" in file_lower and "rlc" not in file_lower:
        for i, comp in enumerate(components):
            if comp.__class__.__name__ == "Inductor":
                ax1.plot(time, currents[i], linewidth=2, label="I через Inductor")
            elif comp.__class__.__name__ == "Resistor":
                ax1.plot(time, currents[i], linewidth=2, linestyle="--", label="I через Resistor")

    elif "rc" in file_lower:
        for i, comp in enumerate(components):
            if comp.__class__.__name__ == "Capacitor":
                ax1.plot(time, currents[i], linewidth=2, label="I через Capacitor")
            elif comp.__class__.__name__ == "Resistor":
                ax1.plot(time, currents[i], linewidth=2, linestyle="--", label="I через Resistor")

    elif "rlc" in file_lower:
        for i, comp in enumerate(components):
            if comp.__class__.__name__ in ["Resistor", "Inductor", "Capacitor"]:
                ax1.plot(time, currents[i], linewidth=1.8, label=f"I через {comp.__class__.__name__}")



    ax1.set_title(f"Моделирование: {file_name}")
    ax1.set_ylabel("Ток, А")
    ax1.grid() #сеточка
    ax1.legend()

    # НИЖНИЙ ГРАФИК — НАПРЯЖЕНИЯ
    if len(voltages) == 0:
        ax2.text(0.5, 0.5, "Нет узловых напряжений для отображения",
                 ha='center', va='center', transform=ax2.transAxes)
    else:
        if "resistors_series" in file_lower or "resistors_parallel" in file_lower:
            for i in range(len(voltages)):
                ax2.plot(time, voltages[i], linewidth=2, label=f"U узел {i + 1}")

        elif "rl" in file_lower and "rlc" not in file_lower:
            # обычно интересен последний узел
            u = voltages[-1]
            ax2.plot(time, u, linewidth=2, label=f"U узел {len(voltages)}")
            ax2.set_ylim(min(u) - 0.1, max(u) + 0.1)

        elif "rc" in file_lower:
            # для RC показываем напряжение на последнем узле (на конденсаторе)
            u = voltages[-1]
            ax2.plot(time, u, linewidth=2, label=f"U узел {len(voltages)} (на конденсаторе)")
            ax2.set_ylim(min(u) - 0.1, max(u) + 0.1)

        elif "rlc" in file_lower:
            # для RLC тоже удобнее смотреть последний узел
            u = voltages[-1]
            ax2.plot(time, u, linewidth=2, label=f"U узел {len(voltages)}")
            ax2.set_ylim(min(u) - 0.1, max(u) + 0.1)


    ax2.set_xlabel("Время, с")
    ax2.set_ylabel("Напряжение, В")
    ax2.grid()
    ax2.legend()

    plt.tight_layout()


    plt.show()


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__)) #определяется папка в которой лежит текущий файл


    selected_json = "rlc.json"
    # selected_json = "resistors_series.json"
    # selected_json = "resistors_parallel.json"
    # selected_json = "rl.json"
    # selected_json = "rc.json"
    # selected_json = "rlc.json"

    file_path = os.path.join(base_dir, selected_json) #формируется путь к выбранному json файлу

    # ВРЕМЯ МОДЕЛИРОВАНИЯ
    if selected_json == "resistors_series.json":
        t_end = 0.02
    elif selected_json == "resistors_parallel.json":
        t_end = 0.02
    elif selected_json == "rl.json":
        t_end = 0.02
    elif selected_json == "rc.json":
        t_end = 2
    elif selected_json == "rlc.json":
        t_end = 0.1
    else:
        t_end = 0.05

    t, I, U, comps = run_simulation(file_path, t_end=t_end) #функции моделирования

    print("Последние значения напряжений:")
    for i in range(len(U)):
        print(f"U узел {i + 1} = {U[i][-1]:.6f} В")

    save_name = os.path.join(base_dir, f"{os.path.splitext(selected_json)[0]}_plot.png") #создается имя картинки

    plot_results( #функция построения графиков
        t,
        I,
        U,
        comps,
        file_name=selected_json,
        save_path=save_name
    )

