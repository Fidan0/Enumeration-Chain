This Python script automates the reconnaissance phase of web application penetration testing. It chains together powerful ProjectDiscovery tools to discover subdomains, resolve DNS, scan ports, probe for HTTP services, and crawl for endpoints.

It is designed to seamlessly integrate with **Burp Suite**, allowing you to populate your Site Map automatically before beginning manual testing.

## 🚀 Features

- **Automated Tool Chain:** Runs `subfinder` → `dnsx` → `naabu` → `httpx` → `katana` in sequence.
- **Smart Piping:** Passes output from one tool to the next to minimize IO operations.
- **Burp Suite Integration:**
    - Routes traffic through a proxy (e.g., `127.0.0.1:8080`).
    - **Seeding Mode:** Re-fires discovered clean URLs through the proxy to ensure the Site Map is fully populated.
- **Clean Output:** Generates organized text files for every stage of the reconnaissance.
- **Robust Error Handling:** Checks for installed tools and handles execution errors gracefully.

## 📋 Prerequisites

This script uses the standard Python library (Python 3.6+). No `pip` installation is required.

However, you **must** have the following ProjectDiscovery tools installed and available in your system `$PATH`:

1. **Subfinder** (Subdomain discovery)
2. **DNSx** (DNS resolution)
3. **Naabu** (Port scanning)
4. **HTTPx** (Web probing)
5. **Katana** (Crawling)

### Quick Install (using Go)

If you have Go installed, run:

```
go install -v [github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest](https://github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest)
go install -v [github.com/projectdiscovery/dnsx/cmd/dnsx@latest](https://github.com/projectdiscovery/dnsx/cmd/dnsx@latest)
go install -v [github.com/projectdiscovery/naabu/v2/cmd/naabu@latest](https://github.com/projectdiscovery/naabu/v2/cmd/naabu@latest)
go install -v [github.com/projectdiscovery/httpx/cmd/httpx@latest](https://github.com/projectdiscovery/httpx/cmd/httpx@latest)
go install -v [github.com/projectdiscovery/katana/cmd/katana@latest](https://github.com/projectdiscovery/katana/cmd/katana@latest)

```

## 🛠️ Usage

### Basic Usage (Direct Scan)

Scans a domain and saves results to the `recon_results` directory.

```
python3 recon_automation.py -d example.com

```

### Burp Suite Mode (Recommended)

Scans the domain and routes all HTTP probing and crawling traffic through your local Burp proxy.

```
python3 recon_automation.py -d example.com -p 127.0.0.1:8080

```

### Bulk Scan from File

Scans a list of domains provided in a text file.

```
python3 recon_automation.py -l targets.txt -p 127.0.0.1:8080

```

### Command Line Arguments

| Argument | Description |
| --- | --- |
| `-d`, `--domain` | Single target domain (e.g., `tesla.com`). |
| `-l`, `--list` | Input file containing a list of domains (one per line). |
| `-o`, `--output-dir` | Directory to save results (Default: `recon_results`). |
| `-p`, `--proxy` | Proxy address (e.g., `127.0.0.1:8080`). |
| `--dry-run` | Print the commands that would be executed without running them. |

## 📂 Output Structure

The script creates a folder (default: `recon_results/`) containing:

- `domain_subfinder.txt`: List of raw subdomains found.
- `domain_dnsx.txt`: List of active/resolved subdomains.
- `domain_naabu.txt`: List of ports and hosts (e.g., `sub.example.com:443`).
- `domain_httpx_details.txt`: Rich info (Status Codes, Titles, Content-Length).
- `domain_urls_for_burp.txt`: Clean list of live URLs (perfect for Burp import).
- `domain_katana_crawled_paths.txt`: Deep endpoints discovered via crawling.

## ⚠️ Disclaimer

This tool is for **educational purposes and authorized security testing only**. Do not use this tool on targets you do not have explicit permission to audit. The author is not responsible for any misuse.
