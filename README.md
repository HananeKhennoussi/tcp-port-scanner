# TCP Port Scanner

A Python-based TCP port scanner that detects open ports, identifies associated services, and performs basic banner grabbing.

## Features

- TCP port scanning using Python sockets
- Detection of open ports
- Service identification (e.g. HTTP, HTTPS, SSH)
- Banner grabbing when available
- Command-line interface with argparse
- Multithreaded scanning for faster execution
- Optional JSON export of results

## Usage

python3 scanner.py <host> -p <start-end>

## Example

python3 scanner.py google.com -p 443-443

## With JSON export

python3 scanner.py google.com -p 20-100 -o results.json

## With custom number of threads

python3 scanner.py scanme.nmap.org -p 20-200 -t 100

## Example Output

Scanning google.com with 50 threads...

[OPEN] Port 443 (https)

Total open ports: 1

## Requirements

- Python 3
- No external dependencies required

## Project Structure

tcp-port-scanner/
├── scanner.py
├── requirements.txt
├── README.md
└── examples/
    └── sample_output.txt

## Notes

- This tool is intended for educational purposes only.
- Always make sure you have permission before scanning a target.

## Author

Hanane Khennoussi
