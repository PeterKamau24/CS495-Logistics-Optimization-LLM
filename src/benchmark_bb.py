"""
Benchmark Branch and Bound implementations: Python vs C++ vs Assembly.

Runs every implementation N times per instance and keeps the best of N
(min) as the representative time, matching the brute force benchmark
methodology so the two JSONs are directly comparable.
"""

import json
import os
import subprocess
import sys
import time
from typing import Dict, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from knapsack_branch_bound import knapsack_branch_bound, read_knapsack_instance


CPP_EXE = './src/knapsack_branch_bound_cpp.exe'
ASM_EXE = './src/knapsack_branch_bound_asm.exe'


def benchmark_python(instance_file: str, n_runs: int = 5) -> Dict:
    n_items, capacity, weights, values = read_knapsack_instance(instance_file)
    times = []
    max_value = 0
    for _ in range(n_runs):
        t0 = time.perf_counter()
        max_value, _ = knapsack_branch_bound(weights, values, capacity)
        times.append(time.perf_counter() - t0)
    return {
        'n_items': n_items,
        'optimal_value': max_value,
        'time_seconds': min(times),
        'avg_time': sum(times) / len(times),
    }


def _parse_cpp_time(stdout: str, instance_name: str) -> float:
    """Extract 'Computation time: X seconds' for the block matching this instance."""
    in_block = False
    for line in stdout.split('\n'):
        if 'Solving instance:' in line and instance_name in line:
            in_block = True
        elif in_block and 'Computation time:' in line:
            return float(line.split('Computation time:')[1].strip().split()[0])
    return 0.0


def benchmark_cpp(instance_file: str, n_runs: int = 5) -> Dict:
    """C++ runs all instances per invocation; we just read the right block N times."""
    times = []
    for _ in range(n_runs):
        result = subprocess.run([CPP_EXE], capture_output=True, text=True, timeout=300)
        t = _parse_cpp_time(result.stdout, instance_file)
        if t > 0:
            times.append(t)
    return {'time_seconds': min(times) if times else 0.0,
            'avg_time': sum(times) / len(times) if times else 0.0}


def benchmark_asm(instance_file: str, n_runs: int = 5) -> Dict:
    """ASM wrapper prints a final '<value> <time>' line when invoked with a single instance."""
    times = []
    for _ in range(n_runs):
        result = subprocess.run([ASM_EXE, instance_file],
                                capture_output=True, text=True, timeout=300)
        last = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else ''
        parts = last.split()
        if len(parts) >= 2:
            try:
                times.append(float(parts[1]))
            except ValueError:
                pass
    return {'time_seconds': min(times) if times else 0.0,
            'avg_time': sum(times) / len(times) if times else 0.0}


def run_single(instance_file: str) -> Dict:
    print(f"\nBenchmarking: {os.path.basename(instance_file)}")
    print("-" * 70)

    py = benchmark_python(instance_file)
    print(f"  Python : best {py['time_seconds']:.6f}s  avg {py['avg_time']:.6f}s  opt {py['optimal_value']}")

    cpp = benchmark_cpp(instance_file)
    print(f"  C++    : best {cpp['time_seconds']:.6f}s  avg {cpp['avg_time']:.6f}s")

    asm = benchmark_asm(instance_file)
    print(f"  ASM    : best {asm['time_seconds']:.6f}s  avg {asm['avg_time']:.6f}s")

    py_t, cpp_t, asm_t = py['time_seconds'], cpp['time_seconds'], asm['time_seconds']
    return {
        'instance': os.path.basename(instance_file),
        'n_items': py['n_items'],
        'optimal_value': py['optimal_value'],
        'python_time': py_t,
        'cpp_time': cpp_t,
        'asm_time': asm_t,
        'cpp_speedup': py_t / cpp_t if cpp_t > 0 else 0.0,
        'asm_speedup': py_t / asm_t if asm_t > 0 else 0.0,
        'asm_vs_cpp':  cpp_t / asm_t if asm_t > 0 else 0.0,
    }


def main():
    if not os.path.exists(CPP_EXE):
        print(f"Missing {CPP_EXE} — build with:\n  g++ -std=c++17 -O3 -static -o {CPP_EXE} src/knapsack_branch_bound.cpp")
        sys.exit(1)
    if not os.path.exists(ASM_EXE):
        print(f"Missing {ASM_EXE} — build with:\n"
              f"  nasm -f win64 src/knapsack_branch_bound.asm -o src/knapsack_branch_bound_asm.obj\n"
              f"  gcc -O3 src/knapsack_bb_asm_wrapper.c src/knapsack_branch_bound_asm.obj -o {ASM_EXE}")
        sys.exit(1)

    instances = [
        'notebooks/plan_md_instance.txt',
        'notebooks/instance_n10.txt',
        'notebooks/instance_n15.txt',
        'notebooks/instance_n20.txt',
        'notebooks/instance_n22.txt',
        'notebooks/instance_n25.txt',
    ]

    print("=" * 70)
    print("KNAPSACK BRANCH & BOUND 3-WAY BENCHMARK: Python vs C++ vs Assembly")
    print("=" * 70)

    results: List[Dict] = []
    for f in instances:
        if os.path.exists(f):
            results.append(run_single(f))
        else:
            print(f"\nFile not found: {f}")

    print("\n" + "=" * 95)
    print("SUMMARY")
    print("=" * 95)
    print(f"{'Instance':<25} {'n':<4} {'Python(s)':<12} {'C++(s)':<12} {'ASM(s)':<12} {'C++/Py':<8} {'ASM/Py':<8}")
    print("-" * 95)
    for r in results:
        print(f"{r['instance']:<25} {r['n_items']:<4} "
              f"{r['python_time']:<12.6f} {r['cpp_time']:<12.6f} {r['asm_time']:<12.6f} "
              f"{r['cpp_speedup']:<8.1f}x {r['asm_speedup']:<8.1f}x")
    print("=" * 95)

    out = 'benchmark_results_bb.json'
    with open(out, 'w') as fp:
        json.dump(results, fp, indent=2)
    print(f"\nResults saved to: {out}\n")


if __name__ == '__main__':
    main()
