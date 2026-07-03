#!/bin/bash
cd "$(dirname "$0")"
echo "=================================================="
echo "      KETTLEBELL CARD MANAGER GUI LAUNCHER"
echo "=================================================="
echo "Starting local database manager GUI..."
echo "Opening browser to http://localhost:5001"
echo ""

python3 gui.py

echo ""
echo "=================================================="
read -p "Press [Enter] to exit..."
