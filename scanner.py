import socket
import argparse
import json


def get_service_name(port):
    try:
        return socket.getservbyport(port, "tcp")
    except OSError:
        return "unknown"


def grab_banner(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((host, port))

        banner = s.recv(1024)
        s.close()

        decoded = banner.decode(errors="ignore").strip()

        if decoded:
            return decoded

        return None

    except Exception:
        return None


def scan_port(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)

        result = s.connect_ex((host, port))
        s.close()

        return result == 0

    except Exception:
        return False


def is_valid_port(port):
    return 1 <= port <= 65535


def parse_port_range(port_range):
    try:
        start, end = map(int, port_range.split("-"))
        return start, end
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


def main():
    parser = argparse.ArgumentParser(
        description="TCP port scanner with service detection and banner grabbing"
    )

    parser.add_argument("host", help="Target IP or domain")

    parser.add_argument(
        "-p", "--ports",
        required=True,
        help="Port range (example: 20-100)"
    )

    parser.add_argument(
        "-o", "--output",
        help="Output file (JSON format)"
    )

    args = parser.parse_args()

    host = args.host
    start_port, end_port = parse_port_range(args.ports)

    if start_port is None:
        print("[ERROR] Invalid port range format. Use: start-end")
        return

    if not is_valid_port(start_port) or not is_valid_port(end_port):
        print("[ERROR] Ports must be between 1 and 65535.")
        return

    if start_port > end_port:
        print("[ERROR] Start port must be <= end port.")
        return

    print(f"\nScanning {host}...\n")

    results = []

    for port in range(start_port, end_port + 1):
        if scan_port(host, port):
            service = get_service_name(port)
            banner = grab_banner(host, port)

            result = {
                "port": port,
                "service": service,
                "banner": banner
            }

            results.append(result)

            print(f"[OPEN] Port {port} ({service})")

            if banner:
                print(f"       Banner: {banner}")

    if not results:
        print("No open ports found.")
    else:
        print(f"\nTotal open ports: {len(results)}")

    # Save to JSON if requested
    if args.output:
        save_to_json(results, args.output)


if __name__ == "__main__":
    main()