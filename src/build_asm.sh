#!/bin/bash
# Build script for Assembly knapsack solver

echo "Building ARM64 Assembly Knapsack Solver..."

# Detect architecture
ARCH=$(uname -m)
echo "Detected architecture: $ARCH"

if [ "$ARCH" = "arm64" ] || [ "$ARCH" = "aarch64" ]; then
    # ARM64 (Apple Silicon)
    echo "Step 1: Assembling knapsack_brute_force_arm64.s..."
    as -o src/knapsack_brute_force.o src/knapsack_brute_force_arm64.s
else
    # x86-64 (Intel)
    echo "Step 1: Assembling knapsack_brute_force.asm..."
    nasm -f macho64 src/knapsack_brute_force.asm -o src/knapsack_brute_force.o
fi

if [ $? -ne 0 ]; then
    echo "Error: Assembly failed"
    exit 1
fi

# Compile C wrapper
echo "Step 2: Compiling C wrapper..."
gcc -c -O3 src/knapsack_asm_wrapper.c -o src/knapsack_asm_wrapper.o

if [ $? -ne 0 ]; then
    echo "Error: C compilation failed"
    exit 1
fi

# Link object files
echo "Step 3: Linking..."
gcc -O3 src/knapsack_asm_wrapper.o src/knapsack_brute_force.o -o src/knapsack_brute_force_asm

if [ $? -ne 0 ]; then
    echo "Error: Linking failed"
    exit 1
fi

echo "Build successful! Executable: src/knapsack_brute_force_asm"
