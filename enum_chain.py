import argparse
import subprocess
import os
import sys
import time

# --- Configuration and Utility Functions ---

# List of required tools and the suggested order of execution
TOOL_CHAIN = ['subfinder', 'dnsx', 'naabu', 'httpx', 'katana']

# ANSI Colors for nicer output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    WHITE = '\033[97m'  # Added missing color
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_info(msg):
    print(f"{Colors.BLUE}[*] {msg}{Colors.ENDC}")

def print_success(msg):
    print(f"{Colors.GREEN}[✓] {msg}{Colors.ENDC}")

def print_warn(msg):
    print(f"{Colors.YELLOW}[!] {msg}{Colors.ENDC}")

def print_err(msg):
    print(f"{Colors.RED}[✗] {msg}{Colors.ENDC}")

def print_step(step_num, total, tool_name, description):
    print(f"\n{Colors.HEADER}{Colors.BOLD}--- Step {step_num}/{total}: {tool_name.upper()} ---{Colors.ENDC}")
    print(f"{Colors.HEADER}    Description: {description}{Colors.ENDC}")

def check_tools_installed(tools):
    """Checks if all required tools are available in the system's PATH."""
    missing_tools = []
    print(f"{Colors.BOLD}\n--- System Check: Verifying Installed Tools ---{Colors.ENDC}")
    for tool in tools:
        try:
            # Use 'which' command or equivalent to check existence
            subprocess.run(['which', tool], check=True, capture_output=True, text=True)
            print(f"    {Colors.GREEN}✓{Colors.ENDC} {tool:<10} {Colors.GREEN}INSTALLED{Colors.ENDC}")
        except subprocess.CalledProcessError:
            print(f"    {Colors.RED}✗{Colors.ENDC} {tool:<10} {Colors.RED}MISSING{Colors.ENDC}")
            missing_tools.append(tool)
        except FileNotFoundError:
            print(f"    {Colors.RED}✗{Colors.ENDC} {tool:<10} {Colors.RED}ERROR (cmd not found){Colors.ENDC}")
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"\n{Colors.RED}{Colors.BOLD}[FATAL] The following tools are missing: {', '.join(missing_tools)}{Colors.ENDC}")
        print(f"{Colors.YELLOW}Please install them to run this script.{Colors.ENDC}")
        sys.exit(1)
    else:
        print(f"{Colors.GREEN}    >> All systems go. Starting reconnaissance.{Colors.ENDC}")

def run_command(command, input_data=None, output_file=None, environment=None, dry_run=False):
    """Executes a single command and optionally pipes data, saves output, or performs a dry run."""
    
    cmd_str = ' '.join(command)
    print(f"{Colors.CYAN}    ➜ Executing: {cmd_str}{Colors.ENDC}")

    if dry_run:
        if environment:
            proxy_msg = f" (Proxy: {environment.get('HTTP_PROXY')})"
        else:
            proxy_msg = ""
        print(f"{Colors.YELLOW}    [DRY-RUN] Command skipped.{proxy_msg}{Colors.ENDC}")
        if output_file:
            print(f"{Colors.YELLOW}    [DRY-RUN] Output path: {output_file}{Colors.ENDC}")
        return subprocess.CompletedProcess(command, 0, stdout="Simulated output\n", stderr="")

    try:
        result = subprocess.run(
            command,
            input=input_data,
            capture_output=True,
            text=True,
            check=True,
            env=environment,
            encoding='utf-8'
        )

        if output_file:
            with open(output_file, 'w') as f:
                f.write(result.stdout)
            print(f"{Colors.GREEN}    ✓ Output saved to: {Colors.UNDERLINE}{output_file}{Colors.ENDC}")
        
        return result

    except subprocess.CalledProcessError as e:
        print(f"\n{Colors.RED}    [ERROR] Tool '{command[0]}' failed with exit code {e.returncode}.{Colors.ENDC}")
        if e.stderr:
            print(f"{Colors.RED}    Stderr: {e.stderr.strip()}{Colors.ENDC}")
        return subprocess.CompletedProcess(command, 1, stdout="", stderr=e.stderr)
    except Exception as e:
        print(f"\n{Colors.RED}{Colors.BOLD}[CRITICAL ERROR] {e}{Colors.ENDC}")
        sys.exit(1)


# --- Main Logic ---

def main():
    parser = argparse.ArgumentParser(
        description=f"{Colors.BOLD}Automated Reconnaissance Tool Chain{Colors.ENDC}",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('-d', '--domain', type=str, help='Single target domain (e.g., example.com).')
    input_group.add_argument('-l', '--list', type=str, help='File containing a list of domains (one per line).')

    # Output and Proxy options
    parser.add_argument('-o', '--output-dir', type=str, default='recon_results', help='Directory to store all output files (default: recon_results).')
    parser.add_argument('-p', '--proxy', type=str, help='BurpSuite Proxy Address (e.g., 127.0.0.1:8080).')
    parser.add_argument('--dry-run', action='store_true', help='Show planned commands without executing them.')
    
    args = parser.parse_args()

    # --- Setup ---
    check_tools_installed(TOOL_CHAIN)
    
    if args.domain:
        targets = [args.domain]
    else:
        try:
            with open(args.list, 'r') as f:
                targets = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print_err(f"Input list file '{args.list}' not found.")
            sys.exit(1)

    if not targets:
        print_err("No valid targets found in the input.")
        sys.exit(1)

    base_target = targets[0]
    output_base_dir = args.output_dir
    
    os.makedirs(output_base_dir, exist_ok=True)
    print_info(f"Output directory: {output_base_dir}")

    # Prepare environment for proxy integration
    current_env = os.environ.copy()
    proxy_url = ""
    if args.proxy:
        proxy_url = f"http://{args.proxy}"
        current_env['HTTP_PROXY'] = proxy_url
        current_env['HTTPS_PROXY'] = proxy_url
        print_info(f"Proxy enabled: {Colors.BOLD}{proxy_url}{Colors.ENDC} (BurpSuite Integration)")
    else:
        print_info("No proxy specified. Direct connection mode.")

    
    # Process each target
    for target in targets:
        print(f"\n{Colors.BOLD}{Colors.BLUE}" + "="*60 + f"{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.BLUE} STARTING RECON FOR TARGET: {Colors.WHITE}{target}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.BLUE}" + "="*60 + f"{Colors.ENDC}")
        
        current_input = None 
        
        # 1. subfinder
        subfinder_output_file = os.path.join(output_base_dir, f"{target}_subfinder.txt")
        print_step(1, 6, "Subfinder", "Enumerating subdomains")
        subfinder_cmd = ['subfinder', '-d', target, '-silent']
        
        subfinder_result = run_command(subfinder_cmd, dry_run=args.dry_run)
        current_input = subfinder_result.stdout
        
        if current_input and not args.dry_run:
            with open(subfinder_output_file, 'w') as f:
                f.write(current_input)
            print(f"{Colors.GREEN}    ✓ Output saved to: {subfinder_output_file}{Colors.ENDC}")
        
        if not current_input and not args.dry_run:
            print_warn("Subfinder returned no results. Stopping chain for this target.")
            continue


        # 2. dnsx
        dnsx_output_file = os.path.join(output_base_dir, f"{target}_dnsx.txt")
        print_step(2, 6, "DNSx", "Resolving active subdomains")
        dnsx_cmd = ['dnsx', '-silent'] 
        
        dnsx_result = run_command(dnsx_cmd, input_data=current_input, output_file=dnsx_output_file, dry_run=args.dry_run)
        current_input = dnsx_result.stdout

        if not current_input and not args.dry_run:
            print_warn("DNSx resolved no hosts. Stopping chain for this target.")
            continue


        # 3. naabu
        naabu_output_file = os.path.join(output_base_dir, f"{target}_naabu.txt")
        print_step(3, 6, "Naabu", "Port scanning (Top web ports)")
        naabu_cmd = ['naabu', '-p', '80,443,8080,8443', '-nmap-cli', '-silent']
        
        naabu_result = run_command(naabu_cmd, input_data=current_input, output_file=naabu_output_file, dry_run=args.dry_run)
        current_input = naabu_result.stdout

        if not current_input and not args.dry_run:
            print_warn("Naabu found no open web ports. Stopping chain for this target.")
            continue


        # 4. httpx
        httpx_details_file = os.path.join(output_base_dir, f"{target}_httpx_details.txt")
        urls_for_burp_file = os.path.join(output_base_dir, f"{target}_urls_for_burp.txt")
        
        print_step(4, 6, "HTTPX", "Probing for live HTTP services")
        httpx_cmd = ['httpx', '-sc', '-cl', '-title', '-probe', '-silent', '-o', httpx_details_file]
        
        if args.proxy:
            httpx_cmd.extend(['-http-proxy', proxy_url])
        
        httpx_result = run_command(httpx_cmd, input_data=current_input, dry_run=args.dry_run, environment=current_env)
        
        clean_urls = []
        if not args.dry_run:
             try:
                 with open(httpx_details_file, 'r') as f:
                     raw_lines = f.readlines()
                     for line in raw_lines:
                         parts = line.strip().split()
                         if parts:
                             clean_urls.append(parts[0])
                 
                 with open(urls_for_burp_file, 'w') as f:
                     f.write('\n'.join(clean_urls))
                 
                 current_input = '\n'.join(clean_urls)
                 
                 print(f"{Colors.GREEN}    ✓ Rich details: {httpx_details_file}{Colors.ENDC}")
                 print(f"{Colors.GREEN}    ✓ Clean URLs: {urls_for_burp_file} (Ready for Burp){Colors.ENDC}")

             except FileNotFoundError:
                 print_warn("httpx did not produce an output file. Likely no live services found.")
                 current_input = None
        
        if not current_input and not args.dry_run:
            print_warn("httpx found no live HTTP(S) services. Stopping chain for this target.")
            continue


        # 5. katana
        katana_output_file = os.path.join(output_base_dir, f"{target}_katana_crawled_paths.txt")
        print_step(5, 6, "Katana", "Crawling for endpoints")
        
        katana_cmd = ['katana', '-jc', '-aff', '-kf', 'all', '-silent']
        
        if args.proxy:
            katana_cmd.extend(['-proxy', proxy_url])
        
        katana_result = run_command(katana_cmd, input_data=current_input, output_file=katana_output_file, dry_run=args.dry_run, environment=current_env)
        
        if not args.dry_run:
            print(f"{Colors.GREEN}    ✓ Crawled paths saved.{Colors.ENDC}")


        # 6. Seeding Burp
        if args.proxy and not args.dry_run:
            print_step(6, 6, "Burp Suite Integration", "Seeding Site Map")
            print(f"    Sending discovered URLs to {Colors.BOLD}{args.proxy}{Colors.ENDC}...")
            
            seed_cmd = ['httpx', '-silent', '-http-proxy', proxy_url, '-l', urls_for_burp_file]
            run_command(seed_cmd, dry_run=args.dry_run, environment=current_env)
            print_success("Burp Suite Site Map populated successfully.")


        # Final Summary
        print(f"\n{Colors.BOLD}{Colors.GREEN}" + "="*60 + f"{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.GREEN} RECONNAISSANCE COMPLETE: {Colors.WHITE}{target}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.GREEN}" + "="*60 + f"{Colors.ENDC}")
        print(f"    {Colors.CYAN}Results Directory:{Colors.ENDC} {os.path.abspath(output_base_dir)}")
        if args.proxy:
             print(f"    {Colors.CYAN}Proxy Status:{Colors.ENDC}      Traffic sent to {args.proxy}")
             print(f"    {Colors.CYAN}Next Step:{Colors.ENDC}         Check Burp Suite 'Target' tab.")
        else:
             print(f"    {Colors.CYAN}Manual Import:{Colors.ENDC}     Import '{os.path.basename(urls_for_burp_file)}' into Burp.")
        print("\n")

if __name__ == '__main__':
    main()
