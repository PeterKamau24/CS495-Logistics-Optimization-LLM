"""
Extra visualizations for the B&B presentation:

1. pruning_effectiveness.png — 2^n search space vs actual nodes B&B explored.
2. bb_decision_tree.png      — annotated decision tree for a tiny instance
                                showing INCLUDE/EXCLUDE branches and pruned nodes.
3. project_pipeline.png      — where Branch & Bound sits in the capstone:
                                CSV → PuLP model → CBC (B&B) → assignment.
"""

import os
import sys
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from knapsack_branch_bound import read_knapsack_instance


# ---------------------------------------------------------------------------
# Instrumented B&B: same algorithm as knapsack_branch_bound, but counts nodes.
# Kept here (not in the solver) so the production code stays clean.
# ---------------------------------------------------------------------------
def bb_with_counts(weights, values, capacity):
    n = len(weights)
    order = sorted(range(n), key=lambda i: values[i] / weights[i], reverse=True)
    w = [weights[i] for i in order]
    v = [values[i] for i in order]

    stats = {'explored': 0, 'pruned_bound': 0, 'pruned_infeasible': 0,
             'best': 0}

    sys.setrecursionlimit(max(10000, 4 * n))

    def ub(level, cw, cv):
        b, rem = cv, capacity - cw
        for i in range(level, n):
            if w[i] <= rem:
                b += v[i]
                rem -= w[i]
            else:
                b += v[i] * rem / w[i]
                break
        return b

    def branch(level, cw, cv):
        stats['explored'] += 1
        if cv > stats['best']:
            stats['best'] = cv
        if level == n:
            return
        if ub(level, cw, cv) <= stats['best']:
            stats['pruned_bound'] += 1
            return
        if cw + w[level] <= capacity:
            branch(level + 1, cw + w[level], cv + v[level])
        else:
            stats['pruned_infeasible'] += 1
        branch(level + 1, cw, cv)

    branch(0, 0, 0)
    return stats


# ---------------------------------------------------------------------------
# 1. Pruning effectiveness — 2^n vs nodes actually explored
# ---------------------------------------------------------------------------
def make_pruning_chart():
    instances = [
        ('notebooks/plan_md_instance.txt', 3),
        ('notebooks/instance_n10.txt',    10),
        ('notebooks/instance_n15.txt',    15),
        ('notebooks/instance_n20.txt',    20),
        ('notebooks/instance_n22.txt',    22),
        ('notebooks/instance_n25.txt',    25),
    ]

    ns, brute_force, explored, pruned = [], [], [], []
    for path, _ in instances:
        if not os.path.exists(path):
            continue
        n, cap, w, v = read_knapsack_instance(path)
        stats = bb_with_counts(w, v, cap)
        ns.append(n)
        brute_force.append(2 ** n)
        explored.append(stats['explored'])
        pruned.append(stats['pruned_bound'] + stats['pruned_infeasible'])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    fig.suptitle('B&B Pruning Effectiveness: Search Space vs Nodes Actually Visited',
                 fontsize=14, fontweight='bold')

    x = np.arange(len(ns))
    width = 0.4
    ax1.bar(x - width / 2, brute_force, width, label='Brute force: 2^n',
            color='#ef5350', edgecolor='black', linewidth=0.6)
    ax1.bar(x + width / 2, explored, width, label='B&B nodes explored',
            color='#66bb6a', edgecolor='black', linewidth=0.6)
    ax1.set_yscale('log')
    ax1.set_xticks(x)
    ax1.set_xticklabels([f'n={n}' for n in ns])
    ax1.set_xlabel('Instance size', fontweight='bold')
    ax1.set_ylabel('Nodes (log scale)', fontweight='bold')
    ax1.set_title('Search Space Reduction', fontweight='bold')
    ax1.legend()
    ax1.grid(axis='y', which='both', alpha=0.3)

    for xi, bf, ex in zip(x, brute_force, explored):
        reduction = bf / ex if ex else 0
        ax1.text(xi, max(bf, ex) * 1.3,
                 f'{reduction:,.0f}×',
                 ha='center', fontsize=8, fontweight='bold', color='#1b5e20')

    # Right panel: % of search space that B&B touched
    pct = [ex / bf * 100 for ex, bf in zip(explored, brute_force)]
    bars = ax2.bar(x, pct, color='#1976d2', edgecolor='black', linewidth=0.6)
    ax2.set_yscale('log')
    ax2.set_xticks(x)
    ax2.set_xticklabels([f'n={n}' for n in ns])
    ax2.set_xlabel('Instance size', fontweight='bold')
    ax2.set_ylabel('% of 2^n explored (log scale)', fontweight='bold')
    ax2.set_title('Fraction of Search Tree B&B Touches', fontweight='bold')
    ax2.grid(axis='y', which='both', alpha=0.3)

    for bar, p in zip(bars, pct):
        h = bar.get_height()
        label = f'{p:.4f}%' if p < 0.01 else f'{p:.2f}%'
        ax2.text(bar.get_x() + bar.get_width() / 2, h, label,
                 ha='center', va='bottom', fontsize=8, fontweight='bold')

    plt.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# 2. Annotated decision tree for a tiny didactic instance (n=4)
#    Items sorted by ratio desc:
#       i=0: v=10 w=2  (ratio 5.0)
#       i=1: v=7  w=2  (ratio 3.5)
#       i=2: v=8  w=4  (ratio 2.0)
#       i=3: v=4  w=4  (ratio 1.0)
#    capacity = 6
#    Optimal: include i=0, i=1, i=2 -> weight=8 > 6, so try other combos.
#    Best feasible: i=0 + i=1 + i=3 has weight 8 too. Hmm.
#    Let me pick: capacity=8 to make a clean small example.
# ---------------------------------------------------------------------------
def make_decision_tree():
    # Hand-built example so the diagram has a clear narrative.
    # 4 items, capacity 8, sorted by v/w desc:
    #   A: v=10 w=2 (5.0)
    #   B: v=10 w=3 (3.33)
    #   C: v=12 w=5 (2.4)
    #   D: v=8  w=4 (2.0)
    # Greedy LP at root: take A (cv=10,cw=2), B (cv=20,cw=5), then C frac:
    #   remaining=3, contributes 12*3/5 = 7.2  -> bound = 27.2
    # Optimal integer: A+B+D = v=28, w=9 — wait that's over cap. Let's check.
    # A+B+C = v=32, w=10 (over). A+B+D = w=9 (over). A+C+D = w=11 (over).
    # B+C+D = w=12 (over). A+B = v=20 w=5. A+C = v=22 w=7. A+D = v=18 w=6.
    # B+C = v=22 w=8. B+D = v=18 w=7. C+D = v=20 w=9 over. Singles best=C=12.
    # So optimal = A+C or B+C, both v=22, with weights 7 and 8.
    # Let me use cap=8 so A+B+D=9 over, B+C=22 w=8 fits. Optimal = 22.

    fig, ax = plt.subplots(figsize=(14, 8))

    # Tree nodes: (x, y, label, state)
    # state in {'best', 'explored', 'pruned_bound', 'pruned_infeasible'}
    nodes = [
        # Level 0 (root)
        (7.0, 7.5, 'root\ncv=0 cw=0\nbound=27.2', 'explored'),
        # Level 1: include A (left), exclude A (right)
        (3.5, 6.0, 'A=1\ncv=10 cw=2\nbound=27.2', 'explored'),
        (10.5, 6.0, 'A=0\ncv=0 cw=0\nbound=22', 'explored'),
        # Level 2: under A=1 — include B / exclude B; under A=0 — include B / exclude B
        (1.5, 4.5, 'B=1\ncv=20 cw=5\nbound=27.2', 'explored'),
        (5.5, 4.5, 'B=0\ncv=10 cw=2\nbound=21', 'pruned_bound'),
        (8.5, 4.5, 'B=1\ncv=10 cw=3\nbound=22', 'explored'),
        (12.5, 4.5, 'B=0\ncv=0 cw=0\nbound=15.6', 'pruned_bound'),
        # Level 3: under B=1 (cv=20 cw=5) — C=1 (over cap), C=0
        (0.5, 3.0, 'C=1\ncw=10 > 8\nINFEASIBLE', 'pruned_infeasible'),
        (2.5, 3.0, 'C=0\ncv=20 cw=5\nbound=24', 'explored'),
        # Level 3 under A=0, B=1 (cv=10 cw=3) — C=1, C=0
        (7.5, 3.0, 'C=1\ncv=22 cw=8\n★ BEST', 'best'),
        (9.5, 3.0, 'C=0\ncv=10 cw=3\nbound=14', 'pruned_bound'),
        # Level 4: under A=1, B=1, C=0 — D=1, D=0
        (1.5, 1.5, 'D=1\ncw=9 > 8\nINFEASIBLE', 'pruned_infeasible'),
        (3.5, 1.5, 'D=0\ncv=20\nleaf', 'explored'),
    ]

    # Edges as (parent_idx, child_idx)
    edges = [
        (0, 1, 'INCLUDE A'),
        (0, 2, 'EXCLUDE A'),
        (1, 3, 'INCL B'),
        (1, 4, 'EXCL B'),
        (2, 5, 'INCL B'),
        (2, 6, 'EXCL B'),
        (3, 7, 'INCL C'),
        (3, 8, 'EXCL C'),
        (5, 9, 'INCL C'),
        (5, 10, 'EXCL C'),
        (8, 11, 'INCL D'),
        (8, 12, 'EXCL D'),
    ]

    color = {
        'explored':           '#90caf9',
        'best':               '#66bb6a',
        'pruned_bound':       '#ef5350',
        'pruned_infeasible':  '#ffb74d',
    }

    # Draw edges first (so nodes overlay)
    for parent, child, label in edges:
        px, py, _, _ = nodes[parent]
        cx, cy, _, _ = nodes[child]
        ax.annotate('', xy=(cx, cy + 0.35), xytext=(px, py - 0.35),
                    arrowprops=dict(arrowstyle='->', color='#555', lw=1.2))
        mx, my = (px + cx) / 2, (py + cy) / 2
        ax.text(mx, my, label, fontsize=7, color='#444',
                ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                          edgecolor='none', alpha=0.85))

    # Draw nodes
    for x, y, label, state in nodes:
        box = FancyBboxPatch((x - 0.85, y - 0.4), 1.7, 0.8,
                             boxstyle='round,pad=0.05',
                             facecolor=color[state],
                             edgecolor='black', linewidth=1.0)
        ax.add_patch(box)
        ax.text(x, y, label, ha='center', va='center', fontsize=7.5,
                fontweight='bold' if state == 'best' else 'normal')

    legend_handles = [
        mpatches.Patch(color=color['explored'], label='Explored'),
        mpatches.Patch(color=color['best'],     label='Best feasible found'),
        mpatches.Patch(color=color['pruned_bound'],
                       label='Pruned: bound ≤ incumbent'),
        mpatches.Patch(color=color['pruned_infeasible'],
                       label='Pruned: weight > capacity'),
    ]
    ax.legend(handles=legend_handles, loc='upper right', fontsize=9)

    ax.set_xlim(-0.5, 14)
    ax.set_ylim(0.5, 8.5)
    ax.axis('off')
    ax.set_title('B&B Decision Tree — 4 items, capacity 8\n'
                 'Items sorted by value/weight: A(v10,w2), B(v10,w3), C(v12,w5), D(v8,w4)',
                 fontsize=12, fontweight='bold')

    plt.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# 3. Project pipeline: where B&B fits in the capstone
# ---------------------------------------------------------------------------
def make_pipeline_diagram():
    fig, ax = plt.subplots(figsize=(15, 7))

    # (x, y, w, h, title, subtitle, color)
    boxes = [
        (0.5, 4.0, 2.2, 1.4, 'Driver–Region\nCSV',
         'driver_id, region_id\ncost, eligible',
         '#bbdefb'),
        (3.4, 4.0, 2.2, 1.4, 'Pre-processing',
         'src/data_\npreprocessing.py',
         '#90caf9'),
        (6.3, 4.0, 2.2, 1.4, 'ILP Model\n(PuLP)',
         'binary x[d,r]\nmin Σ cost·x',
         '#64b5f6'),
        (9.2, 4.0, 2.2, 1.4, 'CBC Solver',
         'Branch & Bound\nunder the hood',
         '#ffd54f'),
        (12.1, 4.0, 2.2, 1.4, 'Assignment +\nMetrics',
         'src/evaluation.py',
         '#a5d6a7'),
        # Lower row: Knapsack benchmark track
        (3.4, 1.0, 2.2, 1.4, 'Knapsack\nInstances',
         'n=3 … 25',
         '#bbdefb'),
        (6.3, 1.0, 2.2, 1.4, 'Brute Force\n(baseline)',
         'O(2^n)\nPy / C++ / ASM',
         '#ef9a9a'),
        (9.2, 1.0, 2.2, 1.4, 'Branch &\nBound',
         'LP-bound + DFS\nPy / C++ / ASM',
         '#ffd54f'),
        (12.1, 1.0, 2.2, 1.4, 'Speed +\nVerification',
         'same answer,\n~10^6× faster',
         '#a5d6a7'),
    ]

    for x, y, w, h, title, sub, color in boxes:
        box = FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.08',
                             facecolor=color, edgecolor='black', linewidth=1.2)
        ax.add_patch(box)
        ax.text(x + w / 2, y + h * 0.65, title, ha='center', va='center',
                fontsize=11, fontweight='bold')
        ax.text(x + w / 2, y + h * 0.25, sub, ha='center', va='center',
                fontsize=8, color='#333')

    arrows_top = [(2.7, 4.7, 3.4, 4.7), (5.6, 4.7, 6.3, 4.7),
                  (8.5, 4.7, 9.2, 4.7), (11.4, 4.7, 12.1, 4.7)]
    arrows_bot = [(5.6, 1.7, 6.3, 1.7), (8.5, 1.7, 9.2, 1.7),
                  (11.4, 1.7, 12.1, 1.7)]
    for x1, y1, x2, y2 in arrows_top + arrows_bot:
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color='black', lw=1.8))

    # Vertical link showing CBC == B&B
    ax.annotate('', xy=(10.3, 2.4), xytext=(10.3, 4.0),
                arrowprops=dict(arrowstyle='<->', color='#d84315', lw=2.5,
                                linestyle='--'))
    ax.text(11.3, 3.2, 'same\nalgorithm\nfamily',
            ha='center', va='center', fontsize=9, color='#d84315',
            fontweight='bold')

    ax.text(0.6, 5.8, 'Production track — Logistics ILP',
            fontsize=12, fontweight='bold', color='#0d47a1')
    ax.text(0.6, 2.8, 'Research track — Knapsack benchmarks (this work)',
            fontsize=12, fontweight='bold', color='#0d47a1')

    ax.text(7.5, 0.2,
            'Knapsack is the didactic sibling of the driver–region ILP. '
            'Mastering B&B = understanding what CBC is doing for you.',
            ha='center', fontsize=10, style='italic', color='#444')

    ax.set_xlim(0, 15)
    ax.set_ylim(0, 6.5)
    ax.axis('off')
    ax.set_title('Capstone Architecture — Where Branch & Bound Fits',
                 fontsize=14, fontweight='bold', pad=15)

    plt.tight_layout()
    return fig


if __name__ == '__main__':
    fig1 = make_pruning_chart()
    fig1.savefig('pruning_effectiveness.png', dpi=300, bbox_inches='tight')
    print('Saved: pruning_effectiveness.png')

    fig2 = make_decision_tree()
    fig2.savefig('bb_decision_tree.png', dpi=300, bbox_inches='tight')
    print('Saved: bb_decision_tree.png')

    fig3 = make_pipeline_diagram()
    fig3.savefig('project_pipeline.png', dpi=300, bbox_inches='tight')
    print('Saved: project_pipeline.png')

    plt.show()
