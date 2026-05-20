"""
Visualization for Branch and Bound benchmark results (Python vs C++ vs Assembly).

Also overlays the brute force times from benchmark_results_all_three.json (if
present) to show the algorithmic win from B&B vs the exhaustive baseline.
"""

import json
import os
import matplotlib.pyplot as plt
import numpy as np


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


def create_bb_plots(bb_results, bf_results=None):
    n_items = np.array([r['n_items'] for r in bb_results])
    py_t = np.array([r['python_time'] for r in bb_results])
    cpp_t = np.array([r['cpp_time'] for r in bb_results])
    asm_t = np.array([r['asm_time'] for r in bb_results])
    cpp_sp = np.array([r['cpp_speedup'] for r in bb_results])
    asm_sp = np.array([r['asm_speedup'] for r in bb_results])
    asm_vs_cpp = np.array([r['asm_vs_cpp'] for r in bb_results])

    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.3)
    fig.suptitle('0-1 Knapsack Branch & Bound: Python vs C++ vs Assembly',
                 fontsize=18, fontweight='bold', y=0.98)

    # 1. Linear time bars
    ax1 = fig.add_subplot(gs[0, :2])
    x = np.arange(len(n_items))
    w = 0.25
    ax1.bar(x - w, py_t * 1e6, w, label='Python', color='#3776ab', edgecolor='black', linewidth=0.5)
    ax1.bar(x, cpp_t * 1e6, w, label='C++', color='#00599c', edgecolor='black', linewidth=0.5)
    ax1.bar(x + w, asm_t * 1e6, w, label='Assembly', color='#e74c3c', edgecolor='black', linewidth=0.5)
    ax1.set_xlabel('Instance (n items)', fontweight='bold')
    ax1.set_ylabel('Time (microseconds)', fontweight='bold')
    ax1.set_title('B&B Execution Time per Instance', fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels([f'n={n}' for n in n_items])
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)

    # 2. Summary table
    ax2 = fig.add_subplot(gs[0, 2])
    ax2.axis('off')
    rows = [['n', 'Py (μs)', 'C++ (μs)', 'ASM (μs)']]
    for r in bb_results:
        rows.append([
            str(r['n_items']),
            f"{r['python_time']*1e6:.1f}",
            f"{r['cpp_time']*1e6:.1f}",
            f"{r['asm_time']*1e6:.1f}",
        ])
    rows.append(['Avg',
                 f"{py_t.mean()*1e6:.1f}",
                 f"{cpp_t.mean()*1e6:.1f}",
                 f"{asm_t.mean()*1e6:.1f}"])
    table = ax2.table(cellText=rows, cellLoc='center', loc='center',
                      colWidths=[0.18, 0.27, 0.27, 0.27])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2.0)
    for i in range(4):
        table[(0, i)].set_facecolor('#2c3e50')
        table[(0, i)].set_text_props(weight='bold', color='white')
    for i in range(4):
        table[(len(rows) - 1, i)].set_facecolor('#ecf0f1')
        table[(len(rows) - 1, i)].set_text_props(weight='bold')
    ax2.set_title('Timing Summary (μs)', fontweight='bold', pad=15)

    # 3. Log-scale growth
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.plot(n_items, py_t, 'o-', label='Python', color='#3776ab', linewidth=2.5, markersize=9)
    ax3.plot(n_items, cpp_t, 's-', label='C++', color='#00599c', linewidth=2.5, markersize=9)
    # Clip ASM to a small positive floor for log scale display
    asm_plot = np.where(asm_t <= 0, 1e-9, asm_t)
    ax3.plot(n_items, asm_plot, '^-', label='Assembly', color='#e74c3c', linewidth=2.5, markersize=9)
    ax3.set_xlabel('n items', fontweight='bold')
    ax3.set_ylabel('Time (s, log scale)', fontweight='bold')
    ax3.set_title('B&B Time Growth', fontweight='bold')
    ax3.set_yscale('log')
    ax3.legend()
    ax3.grid(True, alpha=0.3, which='both')

    # 4. Speedup vs Python
    ax4 = fig.add_subplot(gs[1, 1])
    xp = np.arange(len(n_items))
    ax4.bar(xp - 0.2, cpp_sp, 0.4, label='C++ vs Py', color='#00599c', edgecolor='black', linewidth=0.5)
    ax4.bar(xp + 0.2, asm_sp, 0.4, label='ASM vs Py', color='#e74c3c', edgecolor='black', linewidth=0.5)
    ax4.axhline(cpp_sp.mean(), color='#00599c', linestyle='--', alpha=0.7,
                label=f'C++ avg: {cpp_sp.mean():.1f}x')
    ax4.axhline(asm_sp.mean(), color='#e74c3c', linestyle='--', alpha=0.7,
                label=f'ASM avg: {asm_sp.mean():.1f}x')
    ax4.set_xlabel('n items', fontweight='bold')
    ax4.set_ylabel('Speedup (×)', fontweight='bold')
    ax4.set_title('Speedup over Python B&B', fontweight='bold')
    ax4.set_xticks(xp)
    ax4.set_xticklabels([f'n={n}' for n in n_items], fontsize=9)
    ax4.legend(fontsize=8)
    ax4.grid(axis='y', alpha=0.3)

    # 5. ASM vs C++
    ax5 = fig.add_subplot(gs[1, 2])
    bars = ax5.bar(xp, asm_vs_cpp, color='#27ae60', edgecolor='black', linewidth=0.5)
    ax5.axhline(asm_vs_cpp.mean(), color='red', linestyle='--', linewidth=2,
                label=f'Avg: {asm_vs_cpp.mean():.2f}x')
    for bar in bars:
        h = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width() / 2, h, f'{h:.2f}x',
                 ha='center', va='bottom', fontsize=8, fontweight='bold')
    ax5.set_xlabel('n items', fontweight='bold')
    ax5.set_ylabel('Speedup (×)', fontweight='bold')
    ax5.set_title('Assembly vs C++', fontweight='bold')
    ax5.set_xticks(xp)
    ax5.set_xticklabels([f'n={n}' for n in n_items], fontsize=9)
    ax5.legend()
    ax5.grid(axis='y', alpha=0.3)

    # 6. B&B vs Brute Force (algorithmic win)
    ax6 = fig.add_subplot(gs[2, :])
    if bf_results is not None:
        bf_by_n = {r['n_items']: r for r in bf_results}
        common = [n for n in n_items if n in bf_by_n]
        if common:
            xn = np.array(common)
            bf_py = np.array([bf_by_n[n]['python_time'] for n in common])
            bf_cpp = np.array([bf_by_n[n]['cpp_time'] for n in common])
            bb_py = np.array([py_t[list(n_items).index(n)] for n in common])
            bb_cpp = np.array([cpp_t[list(n_items).index(n)] for n in common])
            ax6.plot(xn, bf_py, 'o-', label='Brute Force (Python)',
                     color='#3776ab', linewidth=2, markersize=9, alpha=0.85)
            ax6.plot(xn, bf_cpp, 's-', label='Brute Force (C++)',
                     color='#00599c', linewidth=2, markersize=9, alpha=0.85)
            ax6.plot(xn, bb_py, 'o--', label='B&B (Python)',
                     color='#e74c3c', linewidth=2, markersize=9)
            ax6.plot(xn, bb_cpp, 's--', label='B&B (C++)',
                     color='#27ae60', linewidth=2, markersize=9)
            ax6.set_yscale('log')
            ax6.set_xlabel('n items', fontweight='bold')
            ax6.set_ylabel('Time (s, log scale)', fontweight='bold')
            ax6.set_title('Algorithmic Win: Brute Force vs Branch & Bound (log scale)',
                          fontweight='bold')
            ax6.legend()
            ax6.grid(True, alpha=0.3, which='both')
    else:
        ax6.axis('off')
        ax6.text(0.5, 0.5, 'benchmark_results_all_three.json not found —\n'
                            'brute force comparison overlay skipped.',
                 ha='center', va='center', fontsize=12, color='gray')

    return fig


def create_speedup_focus(bb_results, bf_results=None):
    """Single chart focused on the B&B-vs-brute-force speedup at each n."""
    n_items = [r['n_items'] for r in bb_results]
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.suptitle('Branch & Bound Algorithmic Speedup over Brute Force',
                 fontsize=14, fontweight='bold')

    if bf_results is None:
        ax.text(0.5, 0.5, 'No brute force results available.', ha='center')
        return fig

    bf_by_n = {r['n_items']: r for r in bf_results}
    rows = []
    for r in bb_results:
        n = r['n_items']
        if n in bf_by_n:
            rows.append((
                n,
                bf_by_n[n]['python_time'] / r['python_time'] if r['python_time'] > 0 else 0,
                bf_by_n[n]['cpp_time'] / r['cpp_time'] if r['cpp_time'] > 0 else 0,
                bf_by_n[n]['asm_time'] / r['asm_time'] if r['asm_time'] > 0 else 0,
            ))

    if not rows:
        ax.text(0.5, 0.5, 'No overlapping instances.', ha='center')
        return fig

    rows.sort()
    ns = [r[0] for r in rows]
    py_sp = [r[1] for r in rows]
    cpp_sp = [r[2] for r in rows]
    asm_sp = [r[3] for r in rows]

    x = np.arange(len(ns))
    w = 0.25
    ax.bar(x - w, py_sp, w, label='Python B&B / Python BF', color='#3776ab', edgecolor='black')
    ax.bar(x,     cpp_sp, w, label='C++ B&B / C++ BF',       color='#00599c', edgecolor='black')
    ax.bar(x + w, asm_sp, w, label='ASM B&B / ASM BF',       color='#e74c3c', edgecolor='black')
    ax.set_yscale('log')
    ax.set_xticks(x)
    ax.set_xticklabels([f'n={n}' for n in ns])
    ax.set_ylabel('B&B Speedup (×) — log scale', fontweight='bold')
    ax.set_xlabel('Instance', fontweight='bold')
    ax.legend()
    ax.grid(axis='y', alpha=0.3, which='both')

    for i, vals in enumerate(zip(py_sp, cpp_sp, asm_sp)):
        for j, val in enumerate(vals):
            ax.text(i + (j - 1) * w, val, f'{val:,.0f}×',
                    ha='center', va='bottom', fontsize=7, rotation=0)

    plt.tight_layout()
    return fig


if __name__ == '__main__':
    bb = load_json('benchmark_results_bb.json')
    bf = load_json('benchmark_results_all_three.json') if os.path.exists(
        'benchmark_results_all_three.json') else None

    fig1 = create_bb_plots(bb, bf)
    fig1.savefig('results/figures/benchmark_bb_comparison.png', dpi=300, bbox_inches='tight')
    print('Saved: benchmark_bb_comparison.png')

    fig2 = create_speedup_focus(bb, bf)
    fig2.savefig('results/figures/bb_vs_brute_force_speedup.png', dpi=300, bbox_inches='tight')
    print('Saved: bb_vs_brute_force_speedup.png')

    plt.show()
