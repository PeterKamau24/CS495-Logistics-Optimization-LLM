"""
Visualization for Branch and Bound benchmark results.

Produces a single focused plot comparing the B&B implementation across
Python, C++, and x86-64 Assembly. No brute force overlay — Brute Force
and Branch & Bound are presented in separate, independent plots.
"""

import json
import matplotlib.pyplot as plt
import numpy as np


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


def create_bb_plot(bb_results):
    """One clean plot: B&B execution time across Python, C++, Assembly."""
    n_items = np.array([r['n_items'] for r in bb_results])
    py_t = np.array([r['python_time'] for r in bb_results]) * 1e6   # microseconds
    cpp_t = np.array([r['cpp_time'] for r in bb_results]) * 1e6
    asm_t = np.array([r['asm_time'] for r in bb_results]) * 1e6

    fig, ax = plt.subplots(figsize=(12, 7))
    fig.suptitle('Branch & Bound: Python vs C++ vs Assembly',
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
    ax.set_ylabel('Time (microseconds, log scale)', fontweight='bold', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels([f'n={n}' for n in n_items], fontsize=11)
    ax.set_yscale('log')
    ax.legend(fontsize=11, loc='upper left')
    ax.grid(axis='y', which='both', alpha=0.3)

    for bars in (bars_py, bars_cpp, bars_asm):
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                label = f'{h:.1f}' if h >= 1 else f'{h:.2f}'
                ax.text(bar.get_x() + bar.get_width() / 2, h, label,
                        ha='center', va='bottom', fontsize=7.5)

    plt.tight_layout()
    return fig


if __name__ == '__main__':
    bb = load_json('benchmark_results_bb.json')

    fig = create_bb_plot(bb)
    fig.savefig('results/figures/benchmark_bb_comparison.png',
                dpi=300, bbox_inches='tight')
    print('Saved: benchmark_bb_comparison.png')

    plt.show()
