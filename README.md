# Network Reconnaissance & Endpoint Security Tool

This repo contains two lab-only tools:
- **Port Scanner & Subdomain Enumerator** (concurrent TCP connect scans + DNS-based subdomain checks)
- **Keylogger (ethical PoC)** for endpoint-capture research in isolated labs

> **IMPORTANT:** All tools are for research and training in controlled environments only. Do NOT run against third-party systems without explicit authorization.

## Quick start

1. Clone the repo:
```bash
git clone https://github.com/Shubham-Vaishna/Network-Reconnaissance-and-Endpoint-Security-Tool.git
cd Network-Reconnaissance-and-Endpoint-Security-Tool
python -m venv venv
source venv/bin/activate    # on Windows: venv\Scripts\activate
pip install -r requirements.txt
# Scan ports 1-1024 on a lab VM (example IP)
python src/port_scanner.py --target 10.0.2.15 --ports 1-1024 --threads 200
# Or domain + subdomain wordlist
python src/port_scanner.py --target lab.example.org --subdomains wordlists/subs.txt
python src/keylogger_poc.py
# Stop via hotkey Ctrl+Shift+Q
