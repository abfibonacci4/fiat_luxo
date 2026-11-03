
import socket

ROBOT_IP = "172.16.8.2"

LISTEN_PORT = 5890
STATUS_PORT = 5891


def test_connection(port: int) -> None:
    print(f"\nConnecting to {ROBOT_IP}:{port}")

    try:
        with socket.create_connection(
            (ROBOT_IP, port), timeout=5
        ) as connection:
            print("Connected successfully!")

            connection.settimeout(3)

            try:
                data = connection.recv(4096)

                if data:
                    print("Received:", repr(data[:300]))
                else:
                    print("Connection closed by robot.")

            except socket.timeout:
                print("Connected, but no data received yet.")

    except OSError as error:
        print(f"Connection failed: {error}")


if __name__ == "__main__":
    test_connection(LISTEN_PORT)
    test_connection(STATUS_PORT)
