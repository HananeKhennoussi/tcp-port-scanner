import socket


def scan_port(host, port):
    """
    Attempt to connect to a given port on a host.
    Returns True if the port is open, otherwise False.
    """
    try:
        # Create a TCP socket (IPv4)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Set a timeout to avoid long waiting
        s.settimeout(1)

        # Try to connect to the host on the given port
        result = s.connect_ex((host, port))

        # Close the socket after the attempt
        s.close()

        # If connection is successful, port is open
        return result == 0

    except Exception:
        # In case of error, consider the port closed
        return False


def main():
    """
    Main function: asks user input and scans a range of ports.
    Displays only open ports.
    """
    host = input("Enter target IP or domain: ")
    start_port = int(input("Start port: "))
    end_port = int(input("End port: "))

    print(f"\nScanning {host}...\n")

    open_ports = []

    # Iterate through the given port range
    for port in range(start_port, end_port + 1):
        if scan_port(host, port):
            open_ports.append(port)
            print(f"[OPEN] Port {port}")

    # Display summary
    if not open_ports:
        print("No open ports found.")
    else:
        print(f"\nTotal open ports: {len(open_ports)}")


if __name__ == "__main__":
    main()