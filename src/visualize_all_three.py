"""
Visualization for Brute Force benchmark results.

Produces a single focused plot comparing the brute-force implementation across
Python, C++, and x86-64 Assembly. Brute Force and Branch & Bound are presented
in separate, independent plots (no cross-algorithm comparison).
"""

import json
import matplotlib.pyplot as plt
import numpy as np


def load_results(filepath: str = 'benchmark_results_all_three.json'):
    with open(filepath, 'r') as f:
        return json.load(f)


def create_bf_plot(results):
    """One clean plot: Brute Force execution time across Python, C++, Assembly."""
    n_items = np.array([r['n_items'] for r in results])
    py_t = np.array([r['python_time'] for r in results])
    cpp_t = np.array([r['cpp_time'] for r in results])
    asm_t = np.array([r['asm_time'] for r in results])

    fig, ax = plt.subplots(figsize=(12, 7))
    fig.suptitle('Brute Force: Python vs C++ vs Assembly',
                 fontsize=16, fontweight='bold')

    x = np.arange(len(n_items))
    width = 0.27

    bars_py = ax.bar(x - width, py_t, width, label='Python',
                     color='#3776ab', edgecolor='black', linewidth=0.6)
    bars_cpp = ax.bar(x, cpp_t, width, label='C++',
                      color='#00599c', edgecolor='black', linewidth=0.6)
    bars_asm = ax.bar(x + width, asm_t, width, label='Assembly (x86-64)',
                      color='#e74c3c', edgecolor='black', linewidth=0.6)

    ax.set_xlabel('Instance size (n items)', fontweight='bold', fontsize=12)
    ax.set_ylabel('Time (seconds, log scale)', fontweight='bold', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels([f'n={n}' for n in n_items], fontsize=11)
    ax.set_yscale('log')
    ax.legend(fontsize=11, loc='upper left')
    ax.grid(axis='y', which='both', alpha=0.3)

    for bars in (bars_py, bars_cpp, bars_asm):
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                if h >= 1:
                    label = f'{h:.1f}s'
                elif h >= 1e-3:
                    label = f'{h*1e3:.1f}ms'
                else:
                    label = f'{h*1e6:.0f}us'
                ax.text(bar.get_x() + bar.get_width() / 2, h, label,
                        ha='center', va='bottom', fontsize=7.5)

    plt.tight_layout()
    return fig


if __name__ == "__main__":
    results = load_results('benchmark_results_all_three.json')

    fig = create_bf_plot(results)
    fig.savefig('results/figures/benchmark_all_three.png',
                dpi=300, bbox_inches='tight')
    print("Saved: benchmark_all_three.png")

    plt.show()
