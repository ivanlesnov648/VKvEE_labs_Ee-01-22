import csv
import math
import numpy as np


CSV_FILE = "signal.csv"

POINTS_COUNT = 200
FREQUENCY = 1.0
AMPLITUDE = 1.0
PHASE = 0.0


def main():
    time_values = np.linspace(0, 2, POINTS_COUNT)

    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["time", "value"])

        for t in time_values:
            y = AMPLITUDE * math.sin(2 * math.pi * FREQUENCY * t + PHASE)
            writer.writerow([round(t, 5), round(y, 5)])

    print("Файл signal.csv с синусоидой создан")


if __name__ == "__main__":
    main()