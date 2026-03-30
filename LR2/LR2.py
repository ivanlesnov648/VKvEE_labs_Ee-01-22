import json
import random
import logging
import os


class Equipment:
    def __init__(self, name, voltage, connected_with, switched_by):
        self.__name = name
        self.__voltage = voltage
        self.__connected_with = connected_with
        self.__switched_by = switched_by

    def get_name(self):
        return self.__name

    def get_voltage(self):
        return self.__voltage

    def get_connected_with(self):
        return self.__connected_with

    def get_switched_by(self):
        return self.__switched_by


class Line(Equipment):
    pass


class Transformer(Equipment):
    pass


class Bus(Equipment):
    pass


class Breaker(Equipment):
    def __init__(self, name, voltage, connected_with, switched_by):
        super().__init__(name, voltage, connected_with, switched_by)
        self.__state = "ON"

    def get_state(self):
        return self.__state

    def set_state(self, state):
        self.__state = state

    def open(self):
        self.__state = "OFF"


class Fault:
    def __init__(self, fault_type, current, damaged_element, self_cleared):
        self.__fault_type = fault_type
        self.__current = current
        self.__damaged_element = damaged_element
        self.__self_cleared = self_cleared

    def get_fault_type(self):
        return self.__fault_type

    def get_current(self):
        return self.__current

    def get_damaged_element(self):
        return self.__damaged_element

    def is_self_cleared(self):
        return self.__self_cleared


class Protection:
    def __init__(self, name, protected_equipment, setting, p_type, failure_probability):
        self.__name = name
        self.__protected_equipment = protected_equipment
        self.__setting = setting
        self.__p_type = p_type
        self.__failure_probability = failure_probability

    def get_name(self):
        return self.__name

    def get_protected_equipment(self):
        return self.__protected_equipment

    def get_type(self):
        return self.__p_type

    def works_for_fault(self, fault):
        return fault.get_current() >= self.__setting

    def failed(self):
        return random.random() < self.__failure_probability


def setup_logger():
    logger = logging.getLogger("lab2")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    file_handler = logging.FileHandler("lab2_variant6_student.log", encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def load_json(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def create_objects(data):
    equipment = {}
    breakers = {}
    protections = []

    for item in data["substation"]["line"]:
        equipment[item["name"]] = Line(
            item["name"], item["voltage"], item["connected_with"], item["switched_by"]
        )

    for item in data["substation"]["transformer"]:
        equipment[item["name"]] = Transformer(
            item["name"], item["voltage"], item["connected_with"], item["switched_by"]
        )

    for item in data["substation"]["bus"]:
        equipment[item["name"]] = Bus(
            item["name"], item["voltage"], item["connected_with"], item["switched_by"]
        )

    for item in data["substation"]["breaker"]:
        breakers[item["name"]] = Breaker(
            item["name"], item["voltage"], item["connected_with"], item["switched_by"]
        )

    for group in data["protection"]:
        for item in data["protection"][group]:
            protections.append(
                Protection(
                    item["name"],
                    item["name_protected_equipment"],
                    item["setting"],
                    item["type"],
                    item["failure_probability"]
                )
            )

    return equipment, breakers, protections


def generate_fault(damaged_equipment):
    voltage = damaged_equipment.get_voltage()

    if isinstance(damaged_equipment, Transformer):
        fault_types = ["three_phase", "two_phase", "single_phase", "turn_fault"]
    else:
        fault_types = ["three_phase", "two_phase", "single_phase"]

    fault_type = random.choice(fault_types)

    if "500" in voltage:
        if fault_type == "three_phase":
            current = random.randint(3000, 5000)
        elif fault_type == "two_phase":
            current = random.randint(2200, 4000)
        elif fault_type == "single_phase":
            current = random.randint(1500, 3000)
        else:
            current = random.randint(1000, 2000)
    else:
        if fault_type == "three_phase":
            current = random.randint(1500, 2800)
        elif fault_type == "two_phase":
            current = random.randint(1000, 2200)
        elif fault_type == "single_phase":
            current = random.randint(700, 1600)
        else:
            current = random.randint(600, 1200)

    self_cleared = False
    if isinstance(damaged_equipment, Line) and random.random() < 0.25:
        self_cleared = True

    return Fault(fault_type, current, damaged_equipment, self_cleared)


def reset_breakers(breakers):
    for breaker in breakers.values():
        breaker.set_state("ON")


def main():
    logger = setup_logger()


    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    file_path = os.path.join(downloads_path, "lab2_variant6_student.json")


    data = load_json(file_path)
    equipment, breakers, protections = create_objects(data)

    equipment_list = list(equipment.values())

    i = 1
    while i <= 10:
        reset_breakers(breakers)

        damaged_equipment = random.choice(equipment_list)
        fault = generate_fault(damaged_equipment)

        damaged_name = fault.get_damaged_element().get_name()

        print("Итерация", i)
        print("Поврежденный элемент:", damaged_name)
        print("Тип КЗ:", fault.get_fault_type())
        print("Ток КЗ:", fault.get_current(), "А")

        if fault.is_self_cleared():
            print("Результат: КЗ самоустранилось")
            print("Отключенные выключатели: нет")
            print("-" * 50)

            logger.info(
                "Поврежденный элемент: %s; Тип КЗ: %s; Ток КЗ: %s А; Результат: КЗ самоустранилось; Отключенные выключатели: нет",
                damaged_name,
                fault.get_fault_type(),
                fault.get_current()
            )

            i += 1
            continue

        local_protections = []
        for p in protections:
            if p.get_protected_equipment() == damaged_name:
                local_protections.append(p)

        mains = []
        reserves = []

        for p in local_protections:
            if p.get_type() == "main":
                mains.append(p)
            else:
                reserves.append(p)

        worked = False
        worked_name = None
        tripped = []

        for group in [mains, reserves]:
            for p in group:
                if p.works_for_fault(fault):
                    if p.failed():
                        logger.info(
                            "Поврежденный элемент: %s; Тип КЗ: %s; Ток КЗ: %s А; Защита %s отказала",
                            damaged_name,
                            fault.get_fault_type(),
                            fault.get_current(),
                            p.get_name()
                        )
                    else:
                        for br_name in fault.get_damaged_element().get_switched_by():
                            if br_name in breakers:
                                breakers[br_name].open()
                                tripped.append(br_name)

                        worked = True
                        worked_name = p.get_name()

                        logger.info(
                            "Поврежденный элемент: %s; Тип КЗ: %s; Ток КЗ: %s А; Сработала защита %s; Отключенные выключатели: %s",
                            damaged_name,
                            fault.get_fault_type(),
                            fault.get_current(),
                            worked_name,
                            ", ".join(tripped)
                        )
                        break
            if worked:
                break

        if worked:
            print("Результат: Защита сработала")
            print("Сработавшая защита:", worked_name)
            print("Отключенные выключатели:", ", ".join(tripped))
        else:
            print("Результат: Защита не сработала")
            print("Сработавшая защита: нет")
            print("Отключенные выключатели: нет")

            logger.info(
                "Поврежденный элемент: %s; Тип КЗ: %s; Ток КЗ: %s А; Ни одна защита не отключила повреждение",
                damaged_name,
                fault.get_fault_type(),
                fault.get_current()
            )

        print("-" * 50)
        i += 1


if __name__ == "__main__":
    main()
    
