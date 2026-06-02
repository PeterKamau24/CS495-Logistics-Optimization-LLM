// Minimal 0-1 knapsack brute force for the notebook benchmark.
// Reads the 3-line format (n capacity / weights / values) and prints
// "<best_value> <elapsed_seconds>" to stdout.

#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <vector>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: knapsack_brute <instance_file>\n";
        return 1;
    }

    std::ifstream f(argv[1]);
    if (!f) {
        std::cerr << "cannot open " << argv[1] << "\n";
        return 1;
    }

    int n, capacity;
    f >> n >> capacity;

    std::vector<int> w(n), v(n);
    for (int i = 0; i < n; ++i) f >> w[i];
    for (int i = 0; i < n; ++i) f >> v[i];

    auto t0 = std::chrono::steady_clock::now();

    int best = 0;
    const std::uint64_t total = 1ULL << n;
    for (std::uint64_t mask = 0; mask < total; ++mask) {
        int weight = 0, value = 0;
        for (int i = 0; i < n; ++i) {
            if (mask & (1ULL << i)) {
                weight += w[i];
                if (weight > capacity) break;
                value += v[i];
            }
        }
        if (weight <= capacity && value > best) best = value;
    }

    auto t1 = std::chrono::steady_clock::now();
    double elapsed = std::chrono::duration<double>(t1 - t0).count();

    std::cout << best << " " << elapsed << "\n";
    return 0;
}
