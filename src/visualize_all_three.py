"""
Comprehensive visualization for Python vs C++ vs Assembly benchmark results.
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle


def load_results(filepath: str = 'benchmark_results_all_three.json'):
    """Load benchmark results from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def create_comprehensive_plots(results):
    """Create comprehensive 3-way benchmark visualization."""
    # Extract data
    instances = [r['instance'].replace('_instance.txt', '').replace('instance_', '') for r in results]
    n_items = np.array([r['n_items'] for r in results])
    python_times = np.array([r['python_time'] for r in results])
    cpp_times = np.array([r['cpp_time'] for r in results])
    asm_times = np.array([r['asm_time'] for r in results])
    cpp_speedups = np.array([r['cpp_speedup'] for r in results])
    asm_speedups = np.array([r['asm_speedup'] for r in results])
    asm_vs_cpp = np.array([r['asm_vs_cpp'] for r in results])

    # Create figure with subplots
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

    fig.suptitle('Knapsack Brute Force: Python vs C++ vs Assembly Performance Analysis',
                 fontsize=18, fontweight='bold', y=0.98)

    # Plot 1: Execution Time Comparison (Linear Scale) - LARGE
    ax1 = fig.add_subplot(gs[0, :2])
    x = np.arange(len(instances))
    width = 0.25

    bars1 = ax1.bar(x - width, python_times, width, label='Python',
                    color='#3776ab', alpha=0.85, edgecolor='black', linewidth=0.5)
    bars2 = ax1.bar(x, cpp_times, width, label='C++',
                    color='#00599c', alpha=0.85, edgecolor='black', linewidth=0.5)
    bars3 = ax1.bar(x + width, asm_times, width, label='Assembly (ARM64)',
                    color='#e74c3c', alpha=0.85, edgecolor='black', linewidth=0.5)

    ax1.set_xlabel('Instance (n items)', fontweight='bold', fontsize=11)
    ax1.set_ylabel('Time (seconds)', fontweight='bold', fontsize=11)
    ax1.set_title('Execution Time Comparison (Linear Scale)', fontweight='bold', fontsize=12)
    ax1.set_xticks(x)
    ax1.set_xticklabels([f'n={n}' for n in n_items])
    ax1.legend(fontsize=10)
    ax1.grid(axis='y', alpha=0.3)

    # Plot 2: Performance Summary Table
    ax2 = fig.add_subplot(gs[0, 2])
    ax2.axis('tight')
    ax2.axis('off')

    table_data = [['n', 'Py(s)', 'C++(s)', 'ASM(s)']]
    for r in results:
        table_data.append([
            str(r['n_items']),
            f"{r['python_time']:.4f}",
            f"{r['cpp_time']:.4f}",
            f"{r['asm_time']:.4f}"
        ])

    # Add summary row
    table_data.append([
        'Avg',
        f"{np.mean(python_times):.3f}",
        f"{np.mean(cpp_times):.3f}",
        f"{np.mean(asm_times):.3f}"
    ])

    table = ax2.table(cellText=table_data, cellLoc='center', loc='center',
                     colWidths=[0.2, 0.27, 0.27, 0.27])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2.2)

    # Style header
    for i in range(4):
        table[(0, i)].set_facecolor('#2c3e50')
        table[(0, i)].set_text_props(weight='bold', color='white')

    # Style summary row
    last_row = len(table_data) - 1
    for i in range(4):
        table[(last_row, i)].set_facecolor('#ecf0f1')
        table[(last_row, i)].set_text_props(weight='bold')

    ax2.set_title('Timing Summary', fontweight='bold', pad=15, fontsize=11)

    # Plot 3: Log Scale Time Comparison
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.plot(n_items, python_times, 'o-', label='Python',
             color='#3776ab', linewidth=2.5, markersize=9, markeredgecolor='black', markeredgewidth=0.5)
    ax3.plot(n_items, cpp_times, 's-', label='C++',
             color='#00599c', linewidth=2.5, markersize=9, markeredgecolor='black', markeredgewidth=0.5)
    ax3.plot(n_items, asm_times, '^-', label='Assembly',
             color='#e74c3c', linewidth=2.5, markersize=9, markeredgecolor='black', markeredgewidth=0.5)

    ax3.set_xlabel('Number of Items (n)', fontweight='bold')
    ax3.set_ylabel('Time (seconds, log scale)', fontweight='bold')
    ax3.set_title('Execution Time Growth', fontweight='bold')
    ax3.set_yscale('log')
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3, which='both')

    # Plot 4: Speedup vs Python
    ax4 = fig.add_subplot(gs[1, 1])
    x_pos = np.arange(len(instances))
    width = 0.35

    bars_cpp = ax4.bar(x_pos - width/2, cpp_speedups, width,
                       label='C++ vs Python', color='#00599c', alpha=0.85,
                       edgecolor='black', linewidth=0.5)
    bars_asm = ax4.bar(x_pos + width/2, asm_speedups, width,
                       label='ASM vs Python', color='#e74c3c', alpha=0.85,
                       edgecolor='black', linewidth=0.5)

    ax4.set_xlabel('Instance (n items)', fontweight='bold')
    ax4.set_ylabel('Speedup Factor (×)', fontweight='bold')
    ax4.set_title('Speedup over Python', fontweight='bold')
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels([f'n={n}' for n in n_items], fontsize=9)
    ax4.axhline(y=np.mean(cpp_speedups), color='#00599c', linestyle='--',
                alpha=0.7, linewidth=1.5, label=f'C++ Avg: {np.mean(cpp_speedups):.1f}x')
    ax4.axhline(y=np.mean(asm_speedups), color='#e74c3c', linestyle='--',
                alpha=0.7, linewidth=1.5, label=f'ASM Avg: {np.mean(asm_speedups):.1f}x')
    ax4.legend(fontsize=8)
    ax4.grid(axis='y', alpha=0.3)

    # Plot 5: Assembly vs C++ Speedup
    ax5 = fig.add_subplot(gs[1, 2])
    bars_asm_cpp = ax5.bar(x_pos, asm_vs_cpp, color='#27ae60', alpha=0.85,
                           edgecolor='black', linewidth=0.5)

    ax5.set_xlabel('Instance (n items)', fontweight='bold')
    ax5.set_ylabel('Speedup Factor (×)', fontweight='bold')
    ax5.set_title('Assembly vs C++ Speedup', fontweight='bold')
    ax5.set_xticks(x_pos)
    ax5.set_xticklabels([f'n={n}' for n in n_items], fontsize=9)
    ax5.axhline(y=np.mean(asm_vs_cpp), color='red', linestyle='--',
                linewidth=2, label=f'Average: {np.mean(asm_vs_cpp):.2f}x')
    ax5.legend(fontsize=9)
    ax5.grid(axis='y', alpha=0.3)

    # Add value labels
    for bar in bars_asm_cpp:
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}x',
                ha='center', va='bottom', fontsize=8, fontweight='bold')

    # Plot 6: Relative Performance Bar Chart
    ax6 = fig.add_subplot(gs[2, :])

    # Normalize times relative to Python (Python = 100%)
    python_normalized = np.ones(len(results)) * 100
    cpp_normalized = (cpp_times / python_times) * 100
    asm_normalized = (asm_times / python_times) * 100

    x_pos = np.arange(len(instances))
    width = 0.25

    bars_py_norm = ax6.bar(x_pos - width, python_normalized, width,
                           label='Python (baseline)', color='#3776ab',
                           alpha=0.85, edgecolor='black', linewidth=0.5)
    bars_cpp_norm = ax6.bar(x_pos, cpp_normalized, width,
                            label='C++', color='#00599c',
                            alpha=0.85, edgecolor='black', linewidth=0.5)
    bars_asm_norm = ax6.bar(x_pos + width, asm_normalized, width,
                            label='Assembly', color='#e74c3c',
                            alpha=0.85, edgecolor='black', linewidth=0.5)

    ax6.set_xlabel('Instance (n items)', fontweight='bold', fontsize=11)
    ax6.set_ylabel('Relative Time (% of Python)', fontweight='bold', fontsize=11)
    ax6.set_title('Relative Performance: Lower is Better (Python = 100% baseline)',
                  fontweight='bold', fontsize=12)
    ax6.set_xticks(x_pos)
    ax6.set_xticklabels([f'n={n}' for n in n_items])
    ax6.legend(fontsize=10)
    ax6.grid(axis='y', alpha=0.3)

    # Add percentage labels on bars
    for i, (bar_cpp, bar_asm) in enumerate(zip(bars_cpp_norm, bars_asm_norm)):
        height_cpp = bar_cpp.get_height()
        height_asm = bar_asm.get_height()

        if height_cpp < 50:  # Only label if visible
            ax6.text(bar_cpp.get_x() + bar_cpp.get_width()/2., height_cpp,
                    f'{height_cpp:.1f}%',
                    ha='center', va='bottom', fontsize=8)

        if height_asm < 50:
            ax6.text(bar_asm.get_x() + bar_asm.get_width()/2., height_asm,
                    f'{height_asm:.1f}%',
                    ha='center', va='bottom', fontsize=8)

    return fig


def create_scaling_comparison(results):
    """Create detailed scaling analysis comparing all three."""
    n_items = np.array([r['n_items'] for r in results])
    python_times = np.array([r['python_time'] for r in results])
    cpp_times = np.array([r['cpp_time'] for r in results])
    asm_times = np.array([r['asm_time'] for r in results])

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle('Exponential Scaling Analysis: O(2^n) Complexity - All Three Languages',
                 fontsize=14, fontweight='bold')

    # Fit exponential curves
    log_python = np.log(python_times)
    log_cpp = np.log(cpp_times)
    log_asm = np.log(asm_times)

    python_coef = np.polyfit(n_items, log_python, 1)
    cpp_coef = np.polyfit(n_items, log_cpp, 1)
    asm_coef = np.polyfit(n_items, log_asm, 1)

    python_a = np.exp(python_coef[1])
    cpp_a = np.exp(cpp_coef[1])
    asm_a = np.exp(asm_coef[1])

    python_fit = python_a * (2 ** n_items)
    cpp_fit = cpp_a * (2 ** n_items)
    asm_fit = asm_a * (2 ** n_items)

    # Plot 1: Exponential Fit
    ax1 = axes[0]
    ax1.plot(n_items, python_times, 'o', label='Python (actual)',
             color='#3776ab', markersize=10)
    ax1.plot(n_items, python_fit, '--', label=f'Fit: {python_a:.2e}·2^n',
             color='#3776ab', linewidth=2, alpha=0.7)
    ax1.plot(n_items, cpp_times, 's', label='C++ (actual)',
             color='#00599c', markersize=10)
    ax1.plot(n_items, cpp_fit, '--', label=f'Fit: {cpp_a:.2e}·2^n',
             color='#00599c', linewidth=2, alpha=0.7)
    ax1.plot(n_items, asm_times, '^', label='ASM (actual)',
             color='#e74c3c', markersize=10)
    ax1.plot(n_items, asm_fit, '--', label=f'Fit: {asm_a:.2e}·2^n',
             color='#e74c3c', linewidth=2, alpha=0.7)

    ax1.set_xlabel('Number of Items (n)', fontweight='bold')
    ax1.set_ylabel('Time (seconds, log scale)', fontweight='bold')
    ax1.set_title('Exponential Curve Fitting')
    ax1.set_yscale('log')
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3, which='both')

    # Plot 2: Growth Rate
    python_growth = [python_times[i+1]/python_times[i] for i in range(len(python_times)-1)]
    cpp_growth = [cpp_times[i+1]/cpp_times[i] for i in range(len(cpp_times)-1)]
    asm_growth = [asm_times[i+1]/asm_times[i] for i in range(len(asm_times)-1)]
    n_items_growth = n_items[1:]

    ax2 = axes[1]
    ax2.plot(n_items_growth, python_growth, 'o-', label='Python',
             color='#3776ab', linewidth=2, markersize=8)
    ax2.plot(n_items_growth, cpp_growth, 's-', label='C++',
             color='#00599c', linewidth=2, markersize=8)
    ax2.plot(n_items_growth, asm_growth, '^-', label='Assembly',
             color='#e74c3c', linewidth=2, markersize=8)
    ax2.axhline(y=2, color='red', linestyle='--',
                label='Theoretical (2×)', linewidth=2)

    ax2.set_xlabel('Number of Items (n)', fontweight='bold')
    ax2.set_ylabel('Growth Factor (T[n+1] / T[n])', fontweight='bold')
    ax2.set_title('Time Growth Rate Between Instances')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(bottom=0, top=max(python_growth[:3]) * 1.1)

    # Plot 3: Performance Gap Evolution
    ax3 = axes[2]
    cpp_gap = python_times / cpp_times
    asm_gap = python_times / asm_times

    ax3.plot(n_items, cpp_gap, 's-', label='Python / C++',
             color='#00599c', linewidth=2.5, markersize=9)
    ax3.plot(n_items, asm_gap, '^-', label='Python / Assembly',
             color='#e74c3c', linewidth=2.5, markersize=9)

    ax3.set_xlabel('Number of Items (n)', fontweight='bold')
    ax3.set_ylabel('Performance Gap (Speedup)', fontweight='bold')
    ax3.set_title('Performance Gap Evolution')
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


if __name__ == "__main__":
    # Load results
    results = load_results('benchmark_results_all_three.json')

    # Create main benchmark plots
    fig1 = create_comprehensive_plots(results)
    fig1.savefig('benchmark_all_three.png', dpi=300, bbox_inches='tight')
    print("Saved: benchmark_all_three.png")

    # Create scaling analysis
    fig2 = create_scaling_comparison(results)
    fig2.savefig('scaling_all_three.png', dpi=300, bbox_inches='tight')
    print("Saved: scaling_all_three.png")

    print("\nVisualization complete!")
    plt.show()
