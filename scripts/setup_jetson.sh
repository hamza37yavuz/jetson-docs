#!/usr/bin/env bash
set -euo pipefail

echo "== Jetson Setup =="

echo "Updating packages"
sudo apt-get update -y

echo "Installing python3-pip"
sudo apt-get install -y python3-pip

echo "Installing jtop"
sudo pip3 install -U jetson-stats

echo "== Verification Complete =="
echo "Please reboot the system and then run 'jtop' for monitoring"