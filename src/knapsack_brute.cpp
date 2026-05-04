// =============================================================
// knapsack_brute.cpp
// Brute force 0-1 Knapsack solver in C++
// Tries all 2^n subsets, returns the best one within capacity.
//
// Capstone: LLM-Assisted Generation of Low-Level Discrete
// Optimization Solvers
// =============================================================
//
// Compile: g++ -O2 -std=c++17 knapsack_brute.cpp -o knapsack_brute
// Run:     ./knapsack_brute <input_file>
//
// Input file format:
//   Line 1: n capacity
//   Line 2: n weights separated by spaces
//   Line 3: n values separated by spaces
//
// Output: optimal_value solve_time_seconds
// =============================================================

#include <iostream>
#include <fstream>
#include <vector>
#include <chrono>
#include <cstdint>

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Usage: " << argv[0] << " <input_file>\n";
        return 1;
    }

    // ---- Read instance from file ----
    std::ifstream in(argv[1]);
    if (!in) {
        std::cerr << "Error: cannot open " << argv[1] << "\n";
        return 1;
    }

    int n;
    long long capacity;
    in >> n >> capacity;

    std::vector<long long> weights(n), values(n);
    for (int i = 0; i < n; i++) in >> weights[i];
    for (int i = 0; i < n; i++) in >> values[i];

    if (n > 30) {
        std::cerr << "Warning: brute force is impractical for n > 30 (2^n subsets).\n";
    }

    // ---- Brute force: enumerate all 2^n subsets ----
    auto t_start = std::chrono::high_resolution_clock::now();

    long long best_value = 0;
    uint64_t total_subsets = 1ULL << n;       // 2^n

    for (uint64_t mask = 0; mask < total_subsets; mask++) {
        long long total_w = 0;
        long long total_v = 0;

        // Check each bit: if bit i is set, item i is in this subset
        for (int i = 0; i < n; i++) {
            if (mask & (1ULL << i)) {
                total_w += weights[i];
                total_v += values[i];
            }
        }

        // If feasible and better than current best, update
        if (total_w <= capacity && total_v > best_value) {
            best_value = total_v;
        }
    }

    auto t_end = std::chrono::high_resolution_clock::now();
    double elapsed = std::chrono::duration<double>(t_end - t_start).count();

    // ---- Print result: value, then time ----
    std::cout << best_value << " " << elapsed << "\n";
    return 0;
}
