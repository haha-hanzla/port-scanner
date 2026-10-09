# Simple TCP Port Scanner

A beginner-friendly port scanner written in Python. It checks which TCP ports are open on a target using a **TCP connect scan** and uses multithreading to scan quickly.

> **Disclaimer:** This tool is for **educational purposes only**. Only scan systems you own or have explicit written permission to test. Unauthorized scanning may be illegal.

## Features

- Scan a single port, a list, a range, or a mix (`22,80,8000-8100`)
- Resolves hostnames to IP addresses
- Multithreaded for fast scans
- Shows the common service name for each open port
- Adjustable timeout and thread count
- Optional report saved to a text file
- Input validation and clean error messages
- Uses only the Python standard library (no installs needed)

## How It Works

1. The script creates a TCP socket for each port.
2. It tries to connect to `target:port`.
3. If the connection succeeds, the port is **open**. If it is refused or times out, it is **closed** or **filtered**.
4. A thread pool runs many of these checks at the same time.

## Requirements

- Python 3.7 or newer

## Usage

```bash
python port_scanner.py <target> [-p PORTS] [-t TIMEOUT] [--threads N] [-o FILE]
```

| Option | Description | Default |
|--------|-------------|---------|
| `target` | IP address or hostname | required |
| `-p`, `--ports` | Ports to scan | `1-1024` |
| `-t`, `--timeout` | Seconds to wait per port | `0.5` |
| `--threads` | Parallel threads | `100` |
| `-o`, `--output` | Save results to a file | none |

### Examples

```bash
# Scan the default ports (1-1024) on your own machine
python port_scanner.py 127.0.0.1

# Scan specific ports
python port_scanner.py 127.0.0.1 -p 22,80,443

# Scan a range and save a report
python port_scanner.py scanme.nmap.org -p 1-200 -o report.txt
```

`scanme.nmap.org` is a host the Nmap project provides for people to practice scanning legally.

### Sample Output

```
--------------------------------------------------
Scanning target : 127.0.0.1 (127.0.0.1)
Ports           : 3 port(s)
Started at      : 2026-10-09 18:10:00
--------------------------------------------------
[+] Port 80    OPEN   (http)
--------------------------------------------------
Scan finished in 0.51 seconds
Open ports found: 1
```

## Project Structure

```
port-scanner/
├── port_scanner.py   # main program
├── README.md         # documentation
├── requirements.txt  # dependencies (none needed)
└── .gitignore
```

## What You Will Learn

- How TCP connections and ports work
- Using Python's `socket` module
- Command-line tools with `argparse`
- Speeding up programs with `ThreadPoolExecutor`
- Input validation and error handling

## Ideas to Improve It

- Add banner grabbing to identify service versions
- Add UDP scanning
- Add colored output
- Export results as JSON or CSV

## License

MIT License. Free to use for learning.
