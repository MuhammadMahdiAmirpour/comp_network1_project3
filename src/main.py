from server import Server
from client import Client

# Default configuration
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 65432

def run_server(host=DEFAULT_HOST, port=DEFAULT_PORT):
    server = Server(host, port)
    try:
        print(f"Starting server on {host}:{port}")
        server.start()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.stop()

def run_client(host=DEFAULT_HOST, port=DEFAULT_PORT):
    client = Client(host, port)
    try:
        print(f"Connecting to server at {host}:{port}")
        client.connect()
    except KeyboardInterrupt:
        print("\nClient disconnected.")
    finally:
        client.disconnect()

def main():
    while True:
        mode = input("Enter 'server' or 'client' (or 'quit' to exit): ").lower()
        if mode == 'quit':
            break
        elif mode == 'server':
            run_server()
        elif mode == 'client':
            run_client()
        else:
            print("Invalid input. Please enter 'server', 'client', or 'quit'.")

if __name__ == "__main__":
    main()

