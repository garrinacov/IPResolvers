import socket
import threading
import queue
import time
import random
import argparse
from typing import List, Tuple

# Queue to store the list of IPs
ip_queue = queue.Queue()
# List to store results (thread-safe)
results = []
results_lock = threading.Lock()

def load_file(file_path: str) -> List[str]:
    """Read the contents of a file and return a list of lines."""
    try:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        return []

def resolve_ip_to_dns(ip: str, resolvers: List[str]) -> Tuple[str, str]:
    """Convert an IP to a hostname using a specific resolver."""
    try:
        hostname = socket.gethostbyaddr(ip)[0]
        return (ip, hostname)
    except socket.herror as e:
        return (ip, f"Error: Hostname not found ({e})")
    except socket.gaierror as e:
        return (ip, f"Error: Resolution failed ({e})")
    except Exception as e:
        return (ip, f"Unknown error: {e}")

def worker(resolvers: List[str]):
    """Worker thread to resolve IPs from the queue."""
    while True:
        try:
            ip = ip_queue.get(timeout=5)
        except queue.Empty:
            break
        
        result = resolve_ip_to_dns(ip, resolvers)
        
        with results_lock:
            results.append(result)
        
        ip_queue.task_done()

def resolve_ip_list(ip_file: str, resolver_file: str, num_threads: int = 10) -> List[Tuple[str, str]]:
    """Resolve a list of IPs using resolvers from a file."""
    results.clear()
    
    ip_list = load_file(ip_file)
    resolvers = load_file(resolver_file)
    
    if not ip_list:
        print(f"No IPs to resolve in '{ip_file}'.")
        return []
    if not resolvers:
        print(f"No valid resolvers in '{resolver_file}'.")
        return []
    
    print(f"Processing {len(ip_list)} IPs using {len(resolvers)} resolvers...")
    
    for ip in ip_list:
        ip_queue.put(ip)
    
    threads = []
    for _ in range(min(num_threads, len(ip_list))):
        t = threading.Thread(target=worker, args=(resolvers,))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    
    ip_queue.join()
    
    return sorted(results, key=lambda x: x[0])

def print_help():
    """Display usage instructions for the script."""
    help_text = """
    IP to DNS Resolution Script with Threading
    ------------------------------------------

    Description:
    This script performs reverse DNS lookups on a list of IPs using DNS resolvers
    from a separate file, with multi-threading support.

    Usage:
    python script.py [OPTIONS]

    Options:
    -h, --help          Display this help guide
    -i, --ip-file       File containing the list of IPs to resolve (default: ip_list.txt)
    -r, --resolver-file File containing the list of DNS resolvers (default: resolvers.txt)
    -t, --threads       Number of threads to use (default: 10)

    Examples:
    1. Run with defaults:
       python script.py
    2. Specify IP and resolver files:
       python script.py -i my_ips.txt -r my_resolvers.txt
    3. Specify number of threads:
       python script.py -i ip_list.txt -r resolvers.txt -t 5
    4. Show help:
       python script.py --help

    File Format:
    - ip_list.txt: One IP per line, e.g.:
       8.8.8.8
       1.1.1.1
    - resolvers.txt: One resolver IP per line, e.g.:
       8.8.8.8
       1.1.1.1

    Notes:
    - Ensure both files are in the same directory as the script or provide full paths.
    - For custom resolvers, install 'dnspython' and modify the script as needed.
    """
    print(help_text)

# Main execution with argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resolve IPs to DNS with threading", add_help=False)
    parser.add_argument('-h', '--help', action='store_true', help="Show usage guide")
    parser.add_argument('-i', '--ip-file', default='ip_list.txt', help="File with IP list")
    parser.add_argument('-r', '--resolver-file', default='resolvers.txt', help="File with resolver list")
    parser.add_argument('-t', '--threads', type=int, default=10, help="Number of threads")
    
    args = parser.parse_args()
    
    if args.help:
        print_help()
    else:
        print("Starting IP to DNS resolution...")
        start_time = time.time()
        
        resolved_results = resolve_ip_list(args.ip_file, args.resolver_file, args.threads)
        
        if resolved_results:
            print("\nResolution Results:")
            print("-" * 50)
            for ip, hostname in resolved_results:
                print(f"IP: {ip:<15} | Hostname: {hostname}")
        
        print(f"\nExecution time: {time.time() - start_time:.2f} seconds")
