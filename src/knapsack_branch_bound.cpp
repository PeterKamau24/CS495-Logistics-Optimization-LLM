/**
 * Branch and Bound Solver for 0-1 Knapsack Problem
 *
 * Replaces the O(2^n) brute force enumeration with a DFS Branch and Bound
 * search guided by a linear (LP) relaxation upper bound.
 *
 * Pipeline:
 *     1. Items are pre-sorted by value/weight ratio descending.
 *     2. DFS tries "include" before "exclude" so a strong incumbent appears early.
 *     3. Bound = current_value + fractional knapsack over remaining items.
 *        If bound <= best_value, the subtree is pruned.
 *     4. Infeasible (weight > capacity) branches are pruned immediately.
 *
 * Worst case is still O(2^n), but the bound typically collapses the search
 * by orders of magnitude on non-pathological instances.
 */

#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <sstream>
#include <chrono>
#include <iomanip>
#include <algorithm>
#include <numeric>

using namespace std;

struct KnapsackInstance {
    int n_items;
    int capacity;
    vector<int> weights;
    vector<int> values;
};

struct Solution {
    int max_value;
    int total_weight;
    vector<int> selected_items;
    double time_seconds;
};

KnapsackInstance read_knapsack_instance(const string& filepath) {
    KnapsackInstance instance;
    ifstream file(filepath);

    if (!file.is_open()) {
        cerr << "Error: Could not open file " << filepath << endl;
        exit(1);
    }

    string line;
    vector<string> lines;
    while (getline(file, line)) {
        line.erase(0, line.find_first_not_of(" \t\r\n"));
        line.erase(line.find_last_not_of(" \t\r\n") + 1);
        if (!line.empty()) lines.push_back(line);
    }
    file.close();

    if (lines.size() < 3) {
        cerr << "Error: Invalid file format" << endl;
        exit(1);
    }

    istringstream iss0(lines[0]);
    iss0 >> instance.n_items >> instance.capacity;

    istringstream iss1(lines[1]);
    int weight;
    while (iss1 >> weight) instance.weights.push_back(weight);

    istringstream iss2(lines[2]);
    int value;
    while (iss2 >> value) instance.values.push_back(value);

    if ((int)instance.weights.size() != instance.n_items ||
        (int)instance.values.size()  != instance.n_items) {
        cerr << "Error: weight/value count mismatch with n_items" << endl;
        exit(1);
    }

    return instance;
}

namespace {
    // Search state, scoped to a single solve.
    int N;
    int CAP;
    const int* W;     // sorted weights
    const int* V;     // sorted values
    int best_value;
    vector<char> cur_mask;
    vector<char> best_mask;

    double upper_bound(int level, int cur_weight, int cur_value) {
        double bound = cur_value;
        int remaining = CAP - cur_weight;
        for (int i = level; i < N; ++i) {
            if (W[i] <= remaining) {
                bound += V[i];
                remaining -= W[i];
            } else {
                bound += (double)V[i] * remaining / W[i];
                break;
            }
        }
        return bound;
    }

    void branch(int level, int cur_weight, int cur_value) {
        if (cur_value > best_value) {
            best_value = cur_value;
            best_mask = cur_mask;
        }
        if (level == N) return;
        if (upper_bound(level, cur_weight, cur_value) <= best_value) return;

        if (cur_weight + W[level] <= CAP) {
            cur_mask[level] = 1;
            branch(level + 1, cur_weight + W[level], cur_value + V[level]);
            cur_mask[level] = 0;
        }
        branch(level + 1, cur_weight, cur_value);
    }
}

Solution knapsack_branch_bound(const vector<int>& weights,
                               const vector<int>& values,
                               int capacity) {
    int n = (int)weights.size();
    Solution sol{0, 0, {}, 0.0};

    if (n == 0 || capacity <= 0) return sol;

    // Sort indices by value/weight ratio descending.
    vector<int> order(n);
    iota(order.begin(), order.end(), 0);
    sort(order.begin(), order.end(), [&](int a, int b) {
        return (double)values[a] / weights[a] > (double)values[b] / weights[b];
    });

    vector<int> sw(n), sv(n);
    for (int i = 0; i < n; ++i) {
        sw[i] = weights[order[i]];
        sv[i] = values[order[i]];
    }

    N = n;
    CAP = capacity;
    W = sw.data();
    V = sv.data();
    best_value = 0;
    cur_mask.assign(n, 0);
    best_mask.assign(n, 0);

    branch(0, 0, 0);

    sol.max_value = best_value;
    for (int i = 0; i < n; ++i) {
        if (best_mask[i]) {
            sol.selected_items.push_back(order[i]);
            sol.total_weight += weights[order[i]];
        }
    }
    sort(sol.selected_items.begin(), sol.selected_items.end());
    return sol;
}

Solution solve_instance(const string& filepath, bool verbose = true) {
    KnapsackInstance instance = read_knapsack_instance(filepath);

    if (verbose) {
        cout << "\n" << string(60, '=') << endl;
        cout << "Solving instance: " << filepath << endl;
        cout << string(60, '=') << endl;
        cout << "Number of items: " << instance.n_items << endl;
        cout << "Capacity: " << instance.capacity << endl;
    }

    auto start_time = chrono::high_resolution_clock::now();
    Solution solution = knapsack_branch_bound(instance.weights, instance.values, instance.capacity);
    auto end_time = chrono::high_resolution_clock::now();

    chrono::duration<double> elapsed = end_time - start_time;
    solution.time_seconds = elapsed.count();

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
            if (i + 1 < solution.selected_items.size()) cout << ", ";
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

int main() {
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
    cout << "0-1 KNAPSACK PROBLEM - BRANCH AND BOUND SOLVER (C++)" << endl;
    cout << string(60, '=') << endl;

    for (const string& f : instance_files) {
        ifstream test_file(f);
        if (test_file.good()) {
            test_file.close();
            try {
                Solution r = solve_instance(f, true);
                results.push_back(r);
                successful_files.push_back(f);
            } catch (const exception& e) {
                cerr << "Error solving " << f << ": " << e.what() << "\n" << endl;
            }
        } else {
            cout << "File not found: " << f << "\n" << endl;
        }
    }

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
            string filename = successful_files[i];
            size_t last_slash = filename.find_last_of("/\\");
            if (last_slash != string::npos) filename = filename.substr(last_slash + 1);

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
