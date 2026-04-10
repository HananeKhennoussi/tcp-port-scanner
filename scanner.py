import socket


def get_service_name(port):
    """
    Return the standard service name associated with a TCP port.
    If the service is unknown, return 'unknown'.
    """
    try:
        return socket.getservbyport(port, "tcp")
    except OSError:
        return "unknown"


def grab_banner(host, port):
    """
    Try to retrieve a banner from an open TCP service.
    Some services send data immediately after connection.
    Return the banner if available, otherwise return None.
    """
    try:
        # Create a new TCP socket for banner grabbing
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Set a slightly longer timeout for receiving data
        s.settimeout(2)

        # Connect to the target host and port
        s.connect((host, port))

        # Try to receive up to 1024 bytes from the service
        banner = s.recv(1024)

        # Close the socket after reading
        s.close()

        # Decode bytes into a readable string
        decoded_banner = banner.decode(errors="ignore").strip()

        if decoded_banner:
            return decoded_banner

        return None

    except Exception:
        return None


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

        # If connection is successful, the port is open
        return result == 0

    except Exception:
        # In case of error, consider the port closed
        return False


def is_valid_port(port):
    """
    Check whether a port number is valid.
    Valid ports are between 1 and 65535.
    """
    return 1 <= port <= 65535


def main():
    """
    Main function:
    - asks user input
    - validates port values
    - scans a range of ports
    - displays open ports, services, and banners if available
    """
    host = input("Enter target IP or domain: ")

    try:
        start_port = int(input("Start port: "))
        end_port = int(input("End port: "))
    except ValueError:
        print("[ERROR] Ports must be integer values.")
        return

    if not is_valid_port(start_port) or not is_valid_port(end_port):
        print("[ERROR] Ports must be between 1 and 65535.")
        return

    if start_port > end_port:
        print("[ERROR] Start port must be less than or equal to end port.")
        return

    print(f"\nScanning {host}...\n")

    open_ports = []

    # Scan each port in the selected range
    for port in range(start_port, end_port + 1):
        if scan_port(host, port):
            service = get_service_name(port)
            banner = grab_banner(host, port)

            open_ports.append((port, service, banner))
            print(f"[OPEN] Port {port} ({service})")

            if banner:
                print(f"       Banner: {banner}")

    # Display summary
    if not open_ports:
        print("No open ports found.")
    else:
        print(f"\nTotal open ports: {len(open_ports)}")


if __name__ == "__main__":
    main()