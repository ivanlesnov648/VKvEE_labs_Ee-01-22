import time
import threading
from simulator import TransientSimulator

def run_single_simulation(config_path: str, name: str):
    print(f"Запуск симуляции: {name}")
    sim = TransientSimulator(config_path)
    result = sim.run(plot=False)  # чтобы не рисовал графики, но можно их рисовать
    #построение графиков тоже идет параллельно или последовательно - вопрос
    print(f"✓ {name} завершена (финальный ток ≈ {result:.4f} А)")
    return result

def main():
    configs = [
        ("configs/series_resistors.json", "Последовательное соединение резисторов"),
        ("configs/parallel_resistors.json", "Параллельное соединение резисторов"),
        ("configs/rl_circuit.json", "RL-цепь"),
        ("configs/rc_circuit.json", "RC-цепь"),
        ("configs/rlc_circuit.json", "RLC-цепь")
    ]

    #  Последовательное выполнение
    print("=== ПОСЛЕДОВАТЕЛЬНОЕ ВЫПОЛНЕНИЕ ===") #запуск 5 симуляций посл-то и расчет сколько ушло времени на это
    start = time.time()
    for config_path, name in configs: #прошелся по каждому configs "сверху вниз"
        run_single_simulation(config_path, name)
    seq_time = time.time() - start
    print(f"Время последовательного выполнения: {seq_time:.2f} секунд\n")

    #  многопоточность
    print("=== (THREADING) ===")
    threads = [] #cписок для потоков
    start = time.time()

    for config_path, name in configs:
        #создали новый поток; в потоке запускаем функцию симуляции; передаем этой функции 2 аргумента: путь и название схемы
        t = threading.Thread(target=run_single_simulation, args=(config_path, name))
        threads.append(t) #добавили поток в список потоков
        t.start() #запуск потока

    for t in threads: #пройтись по потокам
        t.join() #ждать пока поток не закончит работу

    par_time = time.time() - start
    print(f"Время параллельного выполнения: {par_time:.2f} секунд")

    print(f"\nУскорение: {par_time / seq_time:.2f}x")

if __name__ == "__main__":
    main()