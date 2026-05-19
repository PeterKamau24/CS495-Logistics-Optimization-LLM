"""
Visualization script for Python vs C++ knapsack benchmark results.
"""

import json
import matplotlib.pyplot as plt
import numpy as np


def load_results(filepath: str = 'benchmark_results.json'):
    """Load benchmark results from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def create_benchmark_plots(results):
    """Create comprehensive benchmark visualization."""
    # Extract data
    instances = [r['instance'].replace('_instance.txt', '').replace('instance_', '') for r in results]
    n_items = [r['n_items'] for r in results]
    python_times = [r['python_time'] for r in results]
    cpp_times = [r['cpp_time'] for r in results]
    speedups = [r['speedup'] for r in results]

    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Knapsack Brute Force: Python vs C++ Performance Comparison',
                 fontsize=16, fontweight='bold')

    # Plot 1: Execution Time Comparison (Linear Scale)
    ax1 = axes[0, 0]
    x = np.arange(len(instances))
    width = 0.35

    bars1 = ax1.bar(x - width/2, python_times, width, label='Python', color='#3776ab', alpha=0.8)
    bars2 = ax1.bar(x + width/2, cpp_times, width, label='C++', color='#00599c', alpha=0.8)

    ax1.set_xlabel('Instance (n items)', fontweight='bold')
    ax1.set_ylabel('Time (seconds)', fontweight='bold')
    ax1.set_title('Execution Time Comparison (Linear Scale)')
    ax1.set_xticks(x)
    ax1.set_xticklabels([f'n={n}' for n in n_items])
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)

    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0.01:
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.3f}s',
                        ha='center', va='bottom', fontsize=8)

    # Plot 2: Execution Time Comparison (Log Scale)
    ax2 = axes[0, 1]
    ax2.plot(n_items, python_times, 'o-', label='Python',
             color='#3776ab', linewidth=2, markersize=8)
    ax2.plot(n_items, cpp_times, 's-', label='C++',
             color='#00599c', linewidth=2, markersize=8)

    ax2.set_xlabel('Number of Items (n)', fontweight='bold')
    ax2.set_ylabel('Time (seconds, log scale)', fontweight='bold')
    ax2.set_title('Execution Time Growth (Log Scale)')
    ax2.set_yscale('log')
    ax2.legend()
    ax2.grid(True, alpha=0.3, which='both')

    # Plot 3: Speedup Factor
    ax3 = axes[1, 0]
    bars3 = ax3.bar(x, speedups, color='#2ecc71', alpha=0.8, edgecolor='black')

    ax3.set_xlabel('Instance (n items)', fontweight='bold')
    ax3.set_ylabel('Speedup Factor (×)', fontweight='bold')
    ax3.set_title('C++ Speedup over Python')
    ax3.set_xticks(x)
    ax3.set_xticklabels([f'n={n}' for n in n_items])
    ax3.axhline(y=np.mean(speedups), color='red', linestyle='--',
                label=f'Average: {np.mean(speedups):.2f}x', linewidth=2)
    ax3.legend()
    ax3.grid(axis='y', alpha=0.3)

    # Add value labels
    for bar in bars3:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}x',
                ha='center', va='bottom', fontsize=9, fontweight='bold')

    # Plot 4: Performance Summary Table
    ax4 = axes[1, 1]
    ax4.axis('tight')
    ax4.axis('off')

    # Create table data
    table_data = [
        ['n', 'Python (s)', 'C++ (s)', 'Speedup']
    ]
    for r in results:
        table_data.append([
            str(r['n_items']),
            f"{r['python_time']:.4f}",
            f"{r['cpp_time']:.4f}",
            f"{r['speedup']:.2f}x"
        ])

    # Add summary row
    table_data.append([
        'Avg',
        f"{np.mean(python_times):.4f}",
        f"{np.mean(cpp_times):.4f}",
        f"{np.mean(speedups):.2f}x"
    ])

    table = ax4.table(cellText=table_data, cellLoc='center', loc='center',
                     colWidths=[0.15, 0.25, 0.25, 0.25])

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)

    # Style header row
    for i in range(4):
        table[(0, i)].set_facecolor('#34495e')
        table[(0, i)].set_text_props(weight='bold', color='white')

    # Style summary row
    last_row = len(table_data) - 1
    for i in range(4):
        table[(last_row, i)].set_facecolor('#ecf0f1')
        table[(last_row, i)].set_text_props(weight='bold')

    ax4.set_title('Performance Summary', fontweight='bold', pad=20)

    plt.tight_layout()
    return fig


def create_scaling_analysis(results):
    """Create theoretical vs actual scaling analysis."""
    n_items = np.array([r['n_items'] for r in results])
    python_times = np.array([r['python_time'] for r in results])
    cpp_times = np.array([r['cpp_time'] for r in results])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle('Exponential Scaling Analysis: O(2^n) Complexity',
                 fontsize=14, fontweight='bold')

    # Fit exponential curve: T = a * 2^n
    # Taking log: log(T) = log(a) + n*log(2)
    # So we fit log(T) vs n linearly

    # Python fit
    log_python_times = np.log(python_times)
    python_coef = np.polyfit(n_items, log_python_times, 1)
    python_a = np.exp(python_coef[1])
    python_fit = python_a * (2 ** n_items)

    # C++ fit
    log_cpp_times = np.log(cpp_times)
    cpp_coef = np.polyfit(n_items, log_cpp_times, 1)
    cpp_a = np.exp(cpp_coef[1])
    cpp_fit = cpp_a * (2 ** n_items)

    # Plot 1: Actual vs Fitted
    ax1.plot(n_items, python_times, 'o', label='Python (actual)',
             color='#3776ab', markersize=10)
    ax1.plot(n_items, python_fit, '--', label=f'Python fit: {python_a:.2e}·2^n',
             color='#3776ab', linewidth=2)
    ax1.plot(n_items, cpp_times, 's', label='C++ (actual)',
             color='#00599c', markersize=10)
    ax1.plot(n_items, cpp_fit, '--', label=f'C++ fit: {cpp_a:.2e}·2^n',
             color='#00599c', linewidth=2)

    ax1.set_xlabel('Number of Items (n)', fontweight='bold')
    ax1.set_ylabel('Time (seconds, log scale)', fontweight='bold')
    ax1.set_title('Exponential Curve Fitting')
    ax1.set_yscale('log')
    ax1.legend()
    ax1.grid(True, alpha=0.3, which='both')

    # Plot 2: Growth rate comparison
    # Calculate doubling time (time for n+1 vs n)
    python_growth = [python_times[i+1]/python_times[i] for i in range(len(python_times)-1)]
    cpp_growth = [cpp_times[i+1]/cpp_times[i] for i in range(len(cpp_times)-1)]
    n_items_growth = n_items[1:]

    ax2.plot(n_items_growth, python_growth, 'o-', label='Python',
             color='#3776ab', linewidth=2, markersize=8)
    ax2.plot(n_items_growth, cpp_growth, 's-', label='C++',
             color='#00599c', linewidth=2, markersize=8)
    ax2.axhline(y=2, color='red', linestyle='--',
                label='Theoretical (2×)', linewidth=2)

    ax2.set_xlabel('Number of Items (n)', fontweight='bold')
    ax2.set_ylabel('Growth Factor (T[n+1] / T[n])', fontweight='bold')
    ax2.set_title('Time Growth Rate Between Instances')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(bottom=0)

    plt.tight_layout()
    return fig


if __name__ == "__main__":
    # Load results
    results = load_results('benchmark_results.json')

    # Create main benchmark plots
    fig1 = create_benchmark_plots(results)
    fig1.savefig('benchmark_comparison.png', dpi=300, bbox_inches='tight')
    print("Saved: benchmark_comparison.png")

    # Create scaling analysis
    fig2 = create_scaling_analysis(results)
    fig2.savefig('scaling_analysis.png', dpi=300, bbox_inches='tight')
    print("Saved: scaling_analysis.png")

    plt.show()
