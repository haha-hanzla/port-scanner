#!/usr/bin/env python3
"""
Simple TCP Port Scanner

A beginner-friendly port scanner that checks which TCP ports are open
on a target host using the "connect scan" technique.

How it works (the idea):
    1. We try to open a TCP connection to each port on the target.
    2. If the connection succeeds, the port is OPEN (a service is listening).
    3. If it fails or times out, the port is CLOSED or FILTERED.

DISCLAIMER:
    Use this tool only on systems you own or have written permission to test.
    Scanning other people's systems without permission may be illegal.
"""

import argparse
import socket
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

MIN_PORT = 1
MAX_PORT = 65535


def parse_ports(port_text):
    """
    Convert a string like "22,80,100-110" into a sorted list of port numbers.

    Supported formats:
        single port : "80"
        list        : "22,80,443"
        range       : "1-1024"
        mixed       : "22,80,8000-8100"
    """
    ports = set()  # a set avoids duplicates (e.g. "80,80")

    for part in port_text.split(","):
        part = part.strip()
        if not part:
            continue

        try:
            if "-" in part:
                start_text, end_text = part.split("-", 1)
                start, end = int(start_text), int(end_text)
                if start > end:
                    raise ValueError(f"Invalid range '{part}': start is bigger than end")
                ports.update(range(start, end + 1))
            else:
                ports.add(int(part))
        except ValueError as error:
            raise ValueError(f"Invalid port value '{part}': {error}")

    # Make sure every port is inside the valid range
    for port in ports:
        if port < MIN_PORT or port > MAX_PORT:
            raise ValueError(f"Port {port} is out of range ({MIN_PORT}-{MAX_PORT})")

    if not ports:
        raise ValueError("No ports were given")

    return sorted(ports)


def resolve_target(target):
    """Turn a hostname (like 'example.com') into an IP address."""
    try:
        return socket.gethostbyname(target)
    except socket.gaierror:
        raise ValueError(f"Could not resolve host '{target}'")


def get_service_name(port):
    """Return the common service name for a port (e.g. 80 -> 'http')."""
    try:
        return socket.getservbyport(port, "tcp")
    except OSError:
        return "unknown"


def scan_port(ip, port, timeout):
    """
    Try to connect to one port.
    Returns the port number if it is open, otherwise None.
    """
    # AF_INET = IPv4, SOCK_STREAM = TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        # connect_ex returns 0 on success instead of raising an error
        result = sock.connect_ex((ip, port))
        if result == 0:
            return port
    return None


def run_scan(ip, ports, timeout, threads):
    """Scan all ports using several threads at once so it runs faster."""
    open_ports = []

    with ThreadPoolExecutor(max_workers=threads) as executor:
        # Start a scan for each port, then collect results in order
        futures = [executor.submit(scan_port, ip, port, timeout) for port in ports]
        for future in futures:
            port = future.result()
            if port is not None:
                open_ports.append(port)
                print(f"[+] Port {port:<5} OPEN   ({get_service_name(port)})")

    return open_ports


def save_report(filename, target, ip, ports_scanned, open_ports, started, finished):
    """Write the scan results to a text file."""
    with open(filename, "w", encoding="utf-8") as report:
        report.write("PORT SCAN REPORT\n")
        report.write("\n")
        report.write(f"Target        : {target} ({ip})\n")
        report.write(f"Started       : {started:%Y-%m-%d %H:%M:%S}\n")
        report.write(f"Finished      : {finished:%Y-%m-%d %H:%M:%S}\n")
        report.write(f"Ports scanned : {ports_scanned}\n")
        report.write(f"Open ports    : {len(open_ports)}\n\n")
        for port in open_ports:
            report.write(f"{port}/tcp  open  {get_service_name(port)}\n")


def build_parser():
    """Define the command-line options."""
    parser = argparse.ArgumentParser(
        description="Simple TCP port scanner (for educational use only)."
    )
    parser.add_argument("target", help="IP address or hostname to scan")
    parser.add_argument(
        "-p", "--ports", default="1-1024",
        help="ports to scan, e.g. '80', '22,80,443' or '1-1024' (default: 1-1024)",
    )
    parser.add_argument(
        "-t", "--timeout", type=float, default=0.5,
        help="seconds to wait for each port (default: 0.5)",
    )
    parser.add_argument(
        "--threads", type=int, default=100,
        help="number of parallel threads (default: 100)",
    )
    parser.add_argument(
        "-o", "--output", help="save the results to this text file",
    )
    return parser


def main():
    args = build_parser().parse_args()

    # Validate user input before doing any scanning
    try:
        ports = parse_ports(args.ports)
        ip = resolve_target(args.target)
    except ValueError as error:
        print(f"[!] Error: {error}")
        sys.exit(1)

    if args.timeout <= 0 or args.threads <= 0:
        print("[!] Error: timeout and threads must be greater than 0")
        sys.exit(1)

    print()
    print(f"Scanning target : {args.target} ({ip})")
    print(f"Ports           : {len(ports)} port(s)")
    print(f"Started at      : {datetime.now():%Y-%m-%d %H:%M:%S}")
    print()

    started = datetime.now()
    try:
        open_ports = run_scan(ip, ports, args.timeout, args.threads)
    except KeyboardInterrupt:
        print("\n[!] Scan stopped by user.")
        sys.exit(0)
    finished = datetime.now()

    print()
    print(f"Scan finished in {(finished - started).total_seconds():.2f} seconds")
    print(f"Open ports found: {len(open_ports)}")

    if args.output:
        save_report(args.output, args.target, ip, len(ports), open_ports, started, finished)
        print(f"Report saved to : {args.output}")


if __name__ == "__main__":
    main()
