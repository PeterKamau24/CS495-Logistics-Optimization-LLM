/**
 * Brute Force Solver for 0-1 Knapsack Problem
 *
 * This module implements a complete enumeration approach to solve the 0-1 knapsack problem.
 * Time complexity: O(2^n) where n is the number of items.
 * Space complexity: O(n) for storing the solution.
 *
 * The brute force approach evaluates all possible subsets of items (2^n combinations)
 * and selects the one with maximum value that doesn't exceed the capacity constraint.
 */

#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <sstream>
#include <chrono>
#include <iomanip>
#include <algorithm>

using namespace std;

/**
 * Structure to hold knapsack instance data
 */
struct KnapsackInstance {
    int n_items;
    int capacity;
    vector<int> weights;
    vector<int> values;
};

/**
 * Structure to hold solution results
 */
struct Solution {
    int max_value;
    int total_weight;
    vector<int> selected_items;
    double time_seconds;
};

/**
 * Read a knapsack instance from a text file.
 *
 * Expected format:
 *     Line 1: n_items capacity
 *     Line 2: weight_1 weight_2 ... weight_n
 *     Line 3: value_1 value_2 ... value_n
 *
 * @param filepath Path to the instance file
 * @return KnapsackInstance containing the problem data
 */
KnapsackInstance read_knapsack_instance(const string& filepath) {
    KnapsackInstance instance;
    ifstream file(filepath);

    if (!file.is_open()) {
        cerr << "Error: Could not open file " << filepath << endl;
        exit(1);
    }

    string line;
    vector<string> lines;

    // Read all non-empty lines
    while (getline(file, line)) {
        // Trim whitespace
        line.erase(0, line.find_first_not_of(" \t\r\n"));
        line.erase(line.find_last_not_of(" \t\r\n") + 1);

        if (!line.empty()) {
            lines.push_back(line);
        }
    }
    file.close();

    if (lines.size() < 3) {
        cerr << "Error: Invalid file format" << endl;
        exit(1);
    }

    // Parse first line: n_items and capacity
    istringstream iss0(lines[0]);
    iss0 >> instance.n_items >> instance.capacity;

    // Parse weights (line 2)
    istringstream iss1(lines[1]);
    int weight;
    while (iss1 >> weight) {
        instance.weights.push_back(weight);
    }

    // Parse values (line 3)
    istringstream iss2(lines[2]);
    int value;
    while (iss2 >> value) {
        instance.values.push_back(value);
    }

    // Validation
    if (instance.weights.size() != instance.n_items) {
        cerr << "Error: Expected " << instance.n_items << " weights, got "
             << instance.weights.size() << endl;
        exit(1);
    }

    if (instance.values.size() != instance.n_items) {
        cerr << "Error: Expected " << instance.n_items << " values, got "
             << instance.values.size() << endl;
        exit(1);
    }

    return instance;
}

/**
 * Solve 0-1 knapsack problem using complete enumeration (brute force).
 *
 * Evaluates all 2^n possible subsets of items and returns the optimal solution.
 *
 * Algorithm:
 *     For each subset S ⊆ {0, 1, ..., n-1}:
 *         if sum(weights[i] for i in S) ≤ capacity:
 *             compute total_value = sum(values[i] for i in S)
 *             track maximum value and corresponding subset
 *
 * @param weights List of item weights
 * @param values List of item values
 * @param capacity Knapsack capacity constraint
 * @return Solution containing max_value and selected_items
 */
Solution knapsack_brute_force(const vector<int>& weights,
                              const vector<int>& values,
                              int capacity) {
    int n = weights.size();
    int max_value = 0;
    vector<int> best_selection;

    // Enumerate all 2^n subsets using binary representation
    // Each integer from 0 to 2^n - 1 represents a unique subset
    // Bit i indicates whether item i is included (1) or not (0)
    long long total_subsets = 1LL << n;  // 2^n iterations

    for (long long subset_mask = 0; subset_mask < total_subsets; ++subset_mask) {
        int total_weight = 0;
        int total_value = 0;
        vector<int> current_selection;

        // Decode the binary representation
        for (int item_idx = 0; item_idx < n; ++item_idx) {
            // Check if bit item_idx is set in subset_mask
            if (subset_mask & (1LL << item_idx)) {
                total_weight += weights[item_idx];
                total_value += values[item_idx];
                current_selection.push_back(item_idx);
            }
        }

        // Check feasibility constraint and optimality
        if (total_weight <= capacity && total_value > max_value) {
            max_value = total_value;
            best_selection = current_selection;
        }
    }

    Solution solution;
    solution.max_value = max_value;
    solution.selected_items = best_selection;
    solution.total_weight = 0;
    for (int idx : best_selection) {
        solution.total_weight += weights[idx];
    }

    return solution;
}

/**
 * Solve a knapsack instance from file and return detailed results.
 *
 * @param filepath Path to instance file
 * @param verbose Whether to print solution details
 * @return Solution containing results and timing information
 */
Solution solve_instance(const string& filepath, bool verbose = true) {
    // Read instance
    KnapsackInstance instance = read_knapsack_instance(filepath);

    if (verbose) {
        cout << "\n" << string(60, '=') << endl;
        cout << "Solving instance: " << filepath << endl;
        cout << string(60, '=') << endl;
        cout << "Number of items: " << instance.n_items << endl;
        cout << "Capacity: " << instance.capacity << endl;
        cout << "Total combinations to evaluate: " << (1LL << instance.n_items) << endl;
    }

    // Solve with timing
    auto start_time = chrono::high_resolution_clock::now();
    Solution solution = knapsack_brute_force(instance.weights, instance.values, instance.capacity);
    auto end_time = chrono::high_resolution_clock::now();

    chrono::duration<double> elapsed = end_time - start_time;
    solution.time_seconds = elapsed.count();

    // Sort selected items for display
    sort(solution.selected_items.begin(), solution.selected_items.end());

    if (verbose) {
        cout << "\n" << string(60, '-') << endl;
        cout << "SOLUTION" << endl;
        cout << string(60, '-') << endl;
        cout << "Optimal value: " << solution.max_value << endl;
        cout << "Total weight: " << solution.total_weight << "/" << instance.capacity << endl;
        cout << "Items selected: " << solution.selected_items.size() << "/" << instance.n_items << endl;

        cout << "Selected item indices: [";
        for (size_t i = 0; i < solution.selected_items.size(); ++i) {
            cout << solution.selected_items[i];
            if (i < solution.selected_items.size() - 1) cout << ", ";
        }
        cout << "]" << endl;

        cout << "\nItem details:" << endl;
        cout << "  " << left << setw(6) << "Item"
             << setw(8) << "Weight" << setw(8) << "Value" << endl;
        cout << "  " << string(6, '-') << " " << string(8, '-')
             << " " << string(8, '-') << endl;

        for (int idx : solution.selected_items) {
            cout << "  " << left << setw(6) << idx
                 << setw(8) << instance.weights[idx]
                 << setw(8) << instance.values[idx] << endl;
        }

        cout << "\n" << string(60, '-') << endl;
        cout << "Computation time: " << fixed << setprecision(6)
             << solution.time_seconds << " seconds" << endl;
        cout << string(60, '=') << "\n" << endl;
    }

    return solution;
}

/**
 * Main entry point - solve all knapsack instances in notebooks/ directory.
 */
int main() {
    // List of instance files
    vector<string> instance_files = {
        "notebooks/plan_md_instance.txt",
        "notebooks/instance_n10.txt",
        "notebooks/instance_n15.txt",
        "notebooks/instance_n20.txt",
        "notebooks/instance_n22.txt",
        "notebooks/instance_n25.txt"
    };

    vector<Solution> results;
    vector<string> successful_files;

    cout << "\n" << string(60, '=') << endl;
    cout << "0-1 KNAPSACK PROBLEM - BRUTE FORCE SOLVER (C++)" << endl;
    cout << string(60, '=') << endl;

    for (const string& instance_file : instance_files) {
        ifstream test_file(instance_file);
        if (test_file.good()) {
            test_file.close();
            try {
                Solution result = solve_instance(instance_file, true);
                results.push_back(result);
                successful_files.push_back(instance_file);
            } catch (const exception& e) {
                cerr << "Error solving " << instance_file << ": " << e.what() << "\n" << endl;
            }
        } else {
            cout << "File not found: " << instance_file << "\n" << endl;
        }
    }

    // Summary table
    if (!results.empty()) {
        cout << "\n" << string(60, '=') << endl;
        cout << "SUMMARY" << endl;
        cout << string(60, '=') << endl;
        cout << left << setw(25) << "Instance"
             << setw(4) << "n"
             << setw(8) << "Opt Val"
             << setw(12) << "Time (s)" << endl;
        cout << string(60, '-') << endl;

        for (size_t i = 0; i < results.size(); ++i) {
            // Extract filename from path
            string filename = successful_files[i];
            size_t last_slash = filename.find_last_of("/\\");
            if (last_slash != string::npos) {
                filename = filename.substr(last_slash + 1);
            }

            // Get n_items from file
            KnapsackInstance inst = read_knapsack_instance(successful_files[i]);

            cout << left << setw(25) << filename
                 << setw(4) << inst.n_items
                 << setw(8) << results[i].max_value
                 << setw(12) << fixed << setprecision(6) << results[i].time_seconds << endl;
        }
        cout << string(60, '=') << "\n" << endl;
    }

    return 0;
}
