import csv
import random
import time
from paho.mqtt import client as mqtt_client


BROKER = "broker.emqx.io"
PORT = 1883
TOPIC = "lab7/sine_signal"
CSV_FILE = "signal.csv"

CLIENT_ID = f"publisher-{random.randint(0, 10000)}"


def connect_mqtt():
    def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            print("Издатель подключился к MQTT брокеру")
        else:
            print(f"Ошибка подключения, код: {reason_code}")

    client = mqtt_client.Client(
        mqtt_client.CallbackAPIVersion.VERSION2,
        client_id=CLIENT_ID
    )
    client.on_connect = on_connect
    client.connect(BROKER, PORT)
    return client


def publish_signal(client):
    with open(CSV_FILE, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            message = f"{row['time']},{row['value']}"
            result = client.publish(TOPIC, message, qos=1)
            result.wait_for_publish()

            print(f"Отправлено: {message}")
            time.sleep(0.05)


def main():
    client = connect_mqtt()
    client.loop_start()

    time.sleep(1)
    publish_signal(client)

    client.loop_stop()
    client.disconnect()
    print("Публикация завершена")


if __name__ == "__main__":
    main()