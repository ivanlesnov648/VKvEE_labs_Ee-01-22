import random
import matplotlib.pyplot as plt
from paho.mqtt import client as mqtt_client


BROKER = "broker.emqx.io"
PORT = 1883
TOPIC = "lab7/sine_signal"

CLIENT_ID = f"subscriber-{random.randint(0, 10000)}"

time_values = []
signal_values = []


def connect_mqtt():
    def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            print("Подписчик подключился к MQTT брокеру")
            client.subscribe(TOPIC, qos=1)
            print(f"Подписка на топик: {TOPIC}")
        else:
            print(f"Ошибка подключения, код: {reason_code}")

    client = mqtt_client.Client(
        mqtt_client.CallbackAPIVersion.VERSION2,
        client_id=CLIENT_ID
    )
    client.on_connect = on_connect
    client.connect(BROKER, PORT)
    return client


def on_message(client, userdata, message):
    text = message.payload.decode()
    t, y = text.split(",")

    time_values.append(float(t))
    signal_values.append(float(y))

    print(f"Получено: t={t}, y={y}")


def main():
    client = connect_mqtt()
    client.on_message = on_message
    client.loop_start()

    plt.ion()
    fig, ax = plt.subplots()

    try:
        while True:
            ax.clear()
            ax.plot(time_values, signal_values, color="blue")
            ax.set_title("Синусоида, полученная через MQTT")
            ax.set_xlabel("Время, с")
            ax.set_ylabel("Значение сигнала")
            ax.grid(True)
            plt.pause(0.2)

    except KeyboardInterrupt:
        print("Подписчик остановлен")

    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()