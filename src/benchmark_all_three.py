"""
Comprehensive benchmark script comparing Python, C++, and Assembly implementations
of the brute force knapsack solver.
"""

import subprocess
import time
import json
import os
from typing import Dict, List
from knapsack_brute_force import read_knapsack_instance, knapsack_brute_force


def benchmark_python(instance_file: str, n_runs: int = 3) -> Dict:
    """Run Python implementation multiple times and return best time."""
    n_items, capacity, weights, values = read_knapsack_instance(instance_file)

    times = []
    for _ in range(n_runs):
        start_time = time.perf_counter()
        max_value, selected_items = knapsack_brute_force(weights, values, capacity)
        end_time = time.perf_counter()
        times.append(end_time - start_time)

    return {
        'n_items': n_items,
        'capacity': capacity,
        'optimal_value': max_value,
        'time_seconds': min(times),  # Best of n runs
        'avg_time': sum(times) / len(times),
        'language': 'Python'
    }


def parse_cpp_time(output: str, instance_name: str) -> float:
    """Parse C++ output to extract computation time for specific instance."""
    in_instance = False
    for line in output.split('\n'):
        if f"Solving instance: {instance_name}" in line or instance_name.split('/')[-1] in line:
            in_instance = True
        elif in_instance and "Computation time:" in line:
            time_str = line.split("Computation time:")[1].strip().split()[0]
            return float(time_str)
    return 0.0


def benchmark_cpp(instance_file: str, n_runs: int = 3) -> Dict:
    """Run C++ implementation and extract timing."""
    n_items, capacity, weights, values = read_knapsack_instance(instance_file)
    max_value, _ = knapsack_brute_force(weights, values, capacity)

    times = []
    for _ in range(n_runs):
        result = subprocess.run(
            ['./src/knapsack_brute_force_cpp'],
            capture_output=True,
            text=True,
            timeout=300
        )
        cpp_time = parse_cpp_time(result.stdout, instance_file)
        if cpp_time > 0:
            times.append(cpp_time)

    return {
        'n_items': n_items,
        'capacity': capacity,
        'optimal_value': max_value,
        'time_seconds': min(times) if times else 0.0,
        'avg_time': sum(times) / len(times) if times else 0.0,
        'language': 'C++'
    }


def parse_asm_time(output: str, instance_name: str) -> float:
    """Parse Assembly output to extract computation time for specific instance."""
    in_instance = False
    for line in output.split('\n'):
        if f"Solving instance: {instance_name}" in line or instance_name.split('/')[-1] in line:
            in_instance = True
        elif in_instance and "Computation time:" in line:
            time_str = line.split("Computation time:")[1].strip().split()[0]
            return float(time_str)
    return 0.0


def benchmark_assembly(instance_file: str, n_runs: int = 3) -> Dict:
    """Run Assembly implementation and extract timing."""
    n_items, capacity, weights, values = read_knapsack_instance(instance_file)
    max_value, _ = knapsack_brute_force(weights, values, capacity)

    times = []
    for _ in range(n_runs):
        result = subprocess.run(
            ['./src/knapsack_brute_force_asm'],
            capture_output=True,
            text=True,
            timeout=300
        )
        asm_time = parse_asm_time(result.stdout, instance_file)
        if asm_time > 0:
            times.append(asm_time)

    return {
        'n_items': n_items,
        'capacity': capacity,
        'optimal_value': max_value,
        'time_seconds': min(times) if times else 0.0,
        'avg_time': sum(times) / len(times) if times else 0.0,
        'language': 'Assembly'
    }


def run_single_instance_benchmark(instance_file: str) -> Dict:
    """Run all three implementations on a single instance."""
    print(f"\nBenchmarking: {os.path.basename(instance_file)}")
    print("-" * 70)

    # Python benchmark
    print("  Running Python implementation (3 runs)...")
    python_result = benchmark_python(instance_file, n_runs=3)
    print(f"    Best: {python_result['time_seconds']:.6f}s, "
          f"Avg: {python_result['avg_time']:.6f}s, "
          f"Value: {python_result['optimal_value']}")

    # C++ benchmark
    print("  Running C++ implementation (3 runs)...")
    cpp_result = benchmark_cpp(instance_file, n_runs=3)
    print(f"    Best: {cpp_result['time_seconds']:.6f}s, "
          f"Avg: {cpp_result['avg_time']:.6f}s")

    # Assembly benchmark
    print("  Running Assembly implementation (3 runs)...")
    asm_result = benchmark_assembly(instance_file, n_runs=3)
    print(f"    Best: {asm_result['time_seconds']:.6f}s, "
          f"Avg: {asm_result['avg_time']:.6f}s")

    # Calculate speedups
    python_time = python_result['time_seconds']
    cpp_time = cpp_result['time_seconds']
    asm_time = asm_result['time_seconds']

    cpp_speedup = python_time / cpp_time if cpp_time > 0 else 0
    asm_speedup = python_time / asm_time if asm_time > 0 else 0
    asm_vs_cpp = cpp_time / asm_time if asm_time > 0 else 0

    print(f"  Speedups:")
    print(f"    C++ vs Python: {cpp_speedup:.2f}x")
    print(f"    ASM vs Python: {asm_speedup:.2f}x")
    print(f"    ASM vs C++:    {asm_vs_cpp:.2f}x")

    return {
        'instance': os.path.basename(instance_file),
        'n_items': python_result['n_items'],
        'optimal_value': python_result['optimal_value'],
        'python_time': python_time,
        'cpp_time': cpp_time,
        'asm_time': asm_time,
        'cpp_speedup': cpp_speedup,
        'asm_speedup': asm_speedup,
        'asm_vs_cpp': asm_vs_cpp
    }


def run_full_benchmark() -> List[Dict]:
    """Run complete 3-way benchmark suite."""
    instance_files = [
        'notebooks/plan_md_instance.txt',
        'notebooks/instance_n10.txt',
        'notebooks/instance_n15.txt',
        'notebooks/instance_n20.txt',
        'notebooks/instance_n22.txt',
        'notebooks/instance_n25.txt',
    ]

    print("=" * 70)
    print("KNAPSACK BRUTE FORCE 3-WAY BENCHMARK: Python vs C++ vs Assembly")
    print("=" * 70)

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
    import numpy as np

    print("\n" + "=" * 95)
    print("BENCHMARK SUMMARY - ALL THREE IMPLEMENTATIONS")
    print("=" * 95)
    print(f"{'Instance':<25} {'n':<4} {'Python(s)':<12} {'C++(s)':<12} {'ASM(s)':<12} {'C++/Py':<8} {'ASM/Py':<8}")
    print("-" * 95)

    for r in results:
        print(f"{r['instance']:<25} {r['n_items']:<4} "
              f"{r['python_time']:<12.6f} {r['cpp_time']:<12.6f} {r['asm_time']:<12.6f} "
              f"{r['cpp_speedup']:<8.2f}x {r['asm_speedup']:<8.2f}x")

    # Summary statistics
    avg_cpp_speedup = np.mean([r['cpp_speedup'] for r in results])
    avg_asm_speedup = np.mean([r['asm_speedup'] for r in results])
    avg_asm_vs_cpp = np.mean([r['asm_vs_cpp'] for r in results])

    print("-" * 95)
    print(f"{'Average Speedups:':<53} {avg_cpp_speedup:<8.2f}x {avg_asm_speedup:<8.2f}x")
    print("=" * 95)

    print(f"\nAssembly vs C++ Average Speedup: {avg_asm_vs_cpp:.2f}x")
    print("=" * 95)


def save_results(results: List[Dict], output_file: str = 'benchmark_results_all_three.json'):
    """Save results to JSON file."""
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    # Check executables exist
    if not os.path.exists('./src/knapsack_brute_force_cpp'):
        print("Error: C++ executable not found. Please compile first:")
        print("  g++ -std=c++17 -O3 -o src/knapsack_brute_force_cpp src/knapsack_brute_force.cpp")
        exit(1)

    if not os.path.exists('./src/knapsack_brute_force_asm'):
        print("Error: Assembly executable not found. Please build first:")
        print("  ./src/build_asm.sh")
        exit(1)

    # Run benchmark
    results = run_full_benchmark()

    # Print summary
    print_summary_table(results)

    # Save results
    save_results(results)
