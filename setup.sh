#!/bin/bash

echo "[+] Installing LulzSec DDOS Tool..."

# Check Python version
python3 --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "[-] Python3 is not installed. Installing..."
    sudo apt-get update && sudo apt-get install python3 python3-pip -y
fi

# Install dependencies
echo "[+] Installing Python dependencies..."
pip3 install -r requirements.txt

# Install scapy for raw packet manipulation
echo "[+] Installing Scapy (requires root)..."
sudo pip3 install scapy

# Make script executable
chmod +x dark_ddos.py

echo ""
echo "[+] Installation complete!"
echo "[+] Run: python3 dark_ddos.py"
echo ""
echo "[!] WARNING: This tool is for educational purposes only."
echo "[!] Use only on systems you own or have permission to test."
