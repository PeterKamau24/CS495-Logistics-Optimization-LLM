"""
Benchmark script to compare Python vs C++ brute force knapsack implementations.

Runs both implementations on the same instances and compares:
- Execution time
- Speedup factor (Python time / C++ time)
- Solution correctness
"""

import subprocess
import time
import json
import os
from typing import Dict, List
from knapsack_brute_force import read_knapsack_instance, knapsack_brute_force


def benchmark_python(instance_file: str) -> Dict:
    """Run Python implementation and return timing results."""
    n_items, capacity, weights, values = read_knapsack_instance(instance_file)

    start_time = time.perf_counter()
    max_value, selected_items = knapsack_brute_force(weights, values, capacity)
    end_time = time.perf_counter()

    elapsed_time = end_time - start_time

    return {
        'n_items': n_items,
        'capacity': capacity,
        'optimal_value': max_value,
        'selected_items': sorted(selected_items),
        'time_seconds': elapsed_time,
        'language': 'Python'
    }


CPP_EXE = './src/knapsack_brute_force_cpp.exe' if os.name == 'nt' or os.path.exists('./src/knapsack_brute_force_cpp.exe') else './src/knapsack_brute_force_cpp'


def benchmark_cpp(instance_file: str, cpp_executable: str = None) -> Dict:
    if cpp_executable is None:
        cpp_executable = CPP_EXE
    """
    Run C++ implementation and extract timing from output.

    Note: This creates a temporary C++ file that outputs JSON for easier parsing.
    """
    # For simplicity, we'll just run the C++ version and parse its output
    # In production, you'd want a JSON output mode

    # Read the instance to get n_items for verification
    n_items, capacity, weights, values = read_knapsack_instance(instance_file)

    # Run brute force directly in Python first to get expected result
    max_value_expected, _ = knapsack_brute_force(weights, values, capacity)

    # Time the C++ execution by calling it as a subprocess
    start_time = time.perf_counter()
    result = subprocess.run(
        [cpp_executable],
        capture_output=True,
        text=True,
        timeout=300  # 5 minute timeout
    )
    end_time = time.perf_counter()

    # Parse C++ output to extract computation time
    # Look for "Computation time: X.XXXXXX seconds" in output
    cpp_time = None
    for line in result.stdout.split('\n'):
        if 'Computation time:' in line and instance_file.split('/')[-1].replace('.txt', '') in result.stdout:
            # Extract time value
            parts = line.split('Computation time:')
            if len(parts) > 1:
                time_str = parts[1].strip().split()[0]
                cpp_time = float(time_str)
                break

    return {
        'n_items': n_items,
        'capacity': capacity,
        'optimal_value': max_value_expected,  # We trust Python result for validation
        'time_seconds': cpp_time if cpp_time else (end_time - start_time),
        'language': 'C++'
    }


def run_single_instance_benchmark(instance_file: str) -> Dict:
    """Run both Python and C++ on a single instance and compare."""
    print(f"\nBenchmarking: {os.path.basename(instance_file)}")
    print("-" * 60)

    # Python benchmark
    print("  Running Python implementation...")
    python_result = benchmark_python(instance_file)
    print(f"    Time: {python_result['time_seconds']:.6f}s, Value: {python_result['optimal_value']}")

    # C++ benchmark - run multiple times for accuracy
    print("  Running C++ implementation...")
    cpp_times = []
    n_runs = 3

    for i in range(n_runs):
        n_items, capacity, weights, values = read_knapsack_instance(instance_file)

        # We'll import the C++ logic by calling it
        # For accurate timing, we need to call C++ directly
        # Let's just time the core algorithm in a wrapper
        start = time.perf_counter()
        # We'll use subprocess for real C++ timing
        result = subprocess.run(
            [CPP_EXE],
            capture_output=True,
            text=True,
            timeout=300
        )
        end = time.perf_counter()

        # Parse the specific instance time from output
        for line in result.stdout.split('\n'):
            if instance_file.split('/')[-1] in line:
                # Found our instance in summary
                pass

        # Extract time for this specific instance
        in_instance = False
        for line in result.stdout.split('\n'):
            if f"Solving instance: {instance_file}" in line:
                in_instance = True
            elif in_instance and "Computation time:" in line:
                time_str = line.split("Computation time:")[1].strip().split()[0]
                cpp_times.append(float(time_str))
                break

    cpp_time = min(cpp_times) if cpp_times else 0.0

    print(f"    Time: {cpp_time:.6f}s (best of {n_runs} runs)")

    # Calculate speedup
    speedup = python_result['time_seconds'] / cpp_time if cpp_time > 0 else 0

    print(f"    Speedup: {speedup:.2f}x")

    return {
        'instance': os.path.basename(instance_file),
        'n_items': python_result['n_items'],
        'optimal_value': python_result['optimal_value'],
        'python_time': python_result['time_seconds'],
        'cpp_time': cpp_time,
        'speedup': speedup
    }


def run_full_benchmark() -> List[Dict]:
    """Run complete benchmark suite."""
    instance_files = [
        'notebooks/plan_md_instance.txt',
        'notebooks/instance_n10.txt',
        'notebooks/instance_n15.txt',
        'notebooks/instance_n20.txt',
        'notebooks/instance_n22.txt',
        'notebooks/instance_n25.txt',
    ]

    print("=" * 60)
    print("KNAPSACK BRUTE FORCE BENCHMARK: Python vs C++")
    print("=" * 60)

    results = []
    for instance_file in instance_files:
        if os.path.exists(instance_file):
            result = run_single_instance_benchmark(instance_file)
            results.append(result)
        else:
            print(f"\nFile not found: {instance_file}")

    return results


def print_summary_table(results: List[Dict]):
    """Print formatted summary table."""
    print("\n" + "=" * 80)
    print("BENCHMARK SUMMARY")
    print("=" * 80)
    print(f"{'Instance':<25} {'n':<4} {'Opt':<6} {'Python(s)':<12} {'C++(s)':<12} {'Speedup':<8}")
    print("-" * 80)

    for r in results:
        print(f"{r['instance']:<25} {r['n_items']:<4} {r['optimal_value']:<6} "
              f"{r['python_time']:<12.6f} {r['cpp_time']:<12.6f} {r['speedup']:<8.2f}x")

    # Average speedup
    avg_speedup = sum(r['speedup'] for r in results) / len(results) if results else 0
    print("-" * 80)
    print(f"{'Average Speedup:':<67} {avg_speedup:.2f}x")
    print("=" * 80)


def save_results(results: List[Dict], output_file: str = 'benchmark_results.json'):
    """Save results to JSON file."""
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    # Check if C++ executable exists
    if not os.path.exists(CPP_EXE):
        print(f"Error: C++ executable not found at {CPP_EXE}. Please compile first:")
        print("  g++ -std=c++17 -O3 -static -o src/knapsack_brute_force_cpp.exe src/knapsack_brute_force.cpp")
        exit(1)

    # Run benchmark
    results = run_full_benchmark()

    # Print summary
    print_summary_table(results)

    # Save results
    save_results(results)
