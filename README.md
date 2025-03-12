 IP to DNS Resolution Script with Threading

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
