#!/bin/bash
cd "$(dirname "$0")"
echo "=================================================="
echo "      KETTLEBELL WORKOUT CARD GENERATOR"
echo "=================================================="
echo "Cleaning print directory and compiling card JPEGs..."
echo ""

python3 generate_cards.py

echo ""
echo "=================================================="
echo "All cards are ready in the 'print_ready_cards' folder."
read -p "Press [Enter] to exit..."
