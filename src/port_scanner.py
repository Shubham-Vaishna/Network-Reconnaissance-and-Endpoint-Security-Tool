#!/usr/bin/env python3
"""
port_scanner.py
Concurrent TCP port scanner + simple subdomain enumerator (lab-only).
Usage examples:
  python src/port_scanner.py --target 10.0.2.15 --ports 1-1024 --threads 200
  python src/port_scanner.py --target example.local --subdomains wordlist.txt
"""
import argparse
import socket
import threading
import time
from queue import Queue

def scan_port(target_ip, port, timeout=1.0):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        result = s.connect_ex((target_ip, port))
        s.close()
        return result == 0
    except Exception:
        return False

def worker(port_queue, target_ip, open_ports, timeout):
    while True:
        port = port_queue.get()
        if port is None:
            port_queue.task_done()
            break
        if scan_port(target_ip, port, timeout):
            open_ports.append(port)
        port_queue.task_done()

def run_port_scan(target, ports, threads=100, timeout=0.5):
    # resolve target to IP
    try:
        target_ip = socket.gethostbyname(target)
    except Exception as e:
        print(f"[!] Could not resolve target {target}: {e}")
        return []
    print(f"Scanning {target} ({target_ip}) ports: {min(ports)}-{max(ports)} with {threads} threads")

    port_queue = Queue()
    open_ports = []
    for _ in range(threads):
        t = threading.Thread(target=worker, args=(port_queue, target_ip, open_ports, timeout))
        t.daemon = True
        t.start()

    for p in ports:
        port_queue.put(p)

    # stop workers
    for _ in range(threads):
        port_queue.put(None)

    start = time.time()
    port_queue.join()
    elapsed = time.time() - start
    open_ports.sort()
    print(f"Scan finished in {elapsed:.2f}s — Open ports: {open_ports}")
    return open_ports

# Simple subdomain enumerator via DNS resolution
def check_subdomains(domain, subdomains_list, timeout=1.0):
    found = []
    for sub in subdomains_list:
        hostname = f"{sub.strip()}.{domain}"
        try:
            ip = socket.gethostbyname_ex(hostname)
            found.append((hostname, ip[2]))
            print(f"[+] Found {hostname} -> {ip[2]}")
        except socket.gaierror:
            # not found
            pass
        except Exception as e:
            print(f"[!] Error checking {hostname}: {e}")
    return found

def parse_ports_arg(port_arg):
    # supports "1-1024" or "80,443,8080"
    ports = set()
    parts = port_arg.split(",")
    for part in parts:
        part = part.strip()
        if "-" in part:
            a,b = part.split("-")
            ports.update(range(int(a), int(b)+1))
        else:
            ports.add(int(part))
    return sorted(ports)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Concurrent Port Scanner & Subdomain Enumerator (lab only)")
    parser.add_argument("--target", required=True, help="Target IP or domain")
    parser.add_argument("--ports", default="1-1024", help="Ports to scan, e.g. 1-1024 or 22,80,443")
    parser.add_argument("--threads", type=int, default=150, help="Worker threads")
    parser.add_argument("--timeout", type=float, default=0.5, help="Socket timeout (seconds)")
    parser.add_argument("--subdomains", help="Optional: wordlist file for subdomain enumeration (one per line)")
    args = parser.parse_args()

    ports = parse_ports_arg(args.ports)

    # Run port scan
    open_ports = run_port_scan(args.target, ports, threads=args.threads, timeout=args.timeout)

    # Optional subdomain enumeration
    if args.subdomains:
        print("\n[>] Running subdomain checks (DNS resolution)...")
        try:
            with open(args.subdomains, "r") as f:
                subs = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print("[!] Subdomain wordlist not found.")
            subs = []
        found = check_subdomains(args.target, subs, timeout=args.timeout)
        if not found:
            print("[*] No subdomains discovered (or DNS blocked).")
