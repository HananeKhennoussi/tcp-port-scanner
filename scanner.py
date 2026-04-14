import socket
import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed


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


def parse_port_range(port_range):
    """
    Parse a port range written as 'start-end' and return two integers.
    Example: '20-80' -> (20, 80)
    """
    try:
        start_port, end_port = map(int, port_range.split("-"))
        return start_port, end_port
    except ValueError:
        return None, None


def save_to_json(data, filename):
    """
    Save scan results to a JSON file.
    """
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        print(f"\nResults saved to {filename}")
    except Exception as e:
        print(f"[ERROR] Could not save file: {e}")


def scan_single_port(host, port):
    """
    Scan a single port and return a result dictionary if the port is open.
    Otherwise, return None.
    """
    if scan_port(host, port):
        service = get_service_name(port)
        banner = grab_banner(host, port)

        return {
            "port": port,
            "service": service,
            "banner": banner
        }

    return None


def main():
    """
    Main function:
    - parse command-line arguments
    - validate port values
    - scan ports using multithreading
    - display open ports, services, and banners if available
    - optionally save results to JSON
    """
    parser = argparse.ArgumentParser(
        description="TCP port scanner with service detection, banner grabbing, and multithreading"
    )

    parser.add_argument(
        "host",
        help="Target IP address or domain name"
    )

    parser.add_argument(
        "-p",
        "--ports",
        required=True,
        help="Port range to scan (example: 20-100)"
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Output file in JSON format"
    )

    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=50,
        help="Number of threads to use (default: 50)"
    )

    args = parser.parse_args()

    host = args.host
    start_port, end_port = parse_port_range(args.ports)

    if start_port is None or end_port is None:
        print("[ERROR] Invalid port range format. Use: start-end")
        return

    if not is_valid_port(start_port) or not is_valid_port(end_port):
        print("[ERROR] Ports must be between 1 and 65535.")
        return

    if start_port > end_port:
        print("[ERROR] Start port must be less than or equal to end port.")
        return

    if args.threads < 1:
        print("[ERROR] Number of threads must be at least 1.")
        return

    print(f"\nScanning {host} with {args.threads} threads...\n")

    results = []

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = [
            executor.submit(scan_single_port, host, port)
            for port in range(start_port, end_port + 1)
        ]

        for future in as_completed(futures):
            result = future.result()

            if result:
                results.append(result)

    # Sort results by port number for clean output
    results.sort(key=lambda item: item["port"])

    for result in results:
        print(f"[OPEN] Port {result['port']} ({result['service']})")

        if result["banner"]:
            print(f"       Banner: {result['banner']}")

    if not results:
        print("No open ports found.")
    else:
        print(f"\nTotal open ports: {len(results)}")

    if args.output:
        save_to_json(results, args.output)


if __name__ == "__main__":
    main()