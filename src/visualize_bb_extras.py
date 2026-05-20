"""
Extra visualizations for the B&B presentation:

1. bb_decision_tree.png — annotated decision tree for a tiny instance showing
                          INCLUDE/EXCLUDE branches and pruned nodes.
2. project_pipeline.png — where Branch & Bound sits in the capstone:
                          CSV -> PuLP model -> CBC (B&B) -> assignment.

Brute Force and Branch & Bound are presented as independent tracks. This
module does NOT generate any chart that compares B&B against Brute Force.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch


# ---------------------------------------------------------------------------
# 1. Annotated decision tree for a tiny didactic instance (n=4, capacity=8)
#    Items sorted by ratio desc:
#       A: v=10 w=2 (5.0)
#       B: v=10 w=3 (3.33)
#       C: v=12 w=5 (2.4)
#       D: v=8  w=4 (2.0)
#    Optimal = B+C, value 22, weight 8.
# ---------------------------------------------------------------------------
def make_decision_tree():
    fig, ax = plt.subplots(figsize=(14, 8))

    # Tree nodes: (x, y, label, state)
    nodes = [
        (7.0, 7.5, 'root\ncv=0 cw=0\nbound=27.2', 'explored'),
        (3.5, 6.0, 'A=1\ncv=10 cw=2\nbound=27.2', 'explored'),
        (10.5, 6.0, 'A=0\ncv=0 cw=0\nbound=22', 'explored'),
        (1.5, 4.5, 'B=1\ncv=20 cw=5\nbound=27.2', 'explored'),
        (5.5, 4.5, 'B=0\ncv=10 cw=2\nbound=21', 'pruned_bound'),
        (8.5, 4.5, 'B=1\ncv=10 cw=3\nbound=22', 'explored'),
        (12.5, 4.5, 'B=0\ncv=0 cw=0\nbound=15.6', 'pruned_bound'),
        (0.5, 3.0, 'C=1\ncw=10 > 8\nINFEASIBLE', 'pruned_infeasible'),
        (2.5, 3.0, 'C=0\ncv=20 cw=5\nbound=24', 'explored'),
        (7.5, 3.0, 'C=1\ncv=22 cw=8\n* BEST', 'best'),
        (9.5, 3.0, 'C=0\ncv=10 cw=3\nbound=14', 'pruned_bound'),
        (1.5, 1.5, 'D=1\ncw=9 > 8\nINFEASIBLE', 'pruned_infeasible'),
        (3.5, 1.5, 'D=0\ncv=20\nleaf', 'explored'),
    ]

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
                       label='Pruned: bound <= incumbent'),
        mpatches.Patch(color=color['pruned_infeasible'],
                       label='Pruned: weight > capacity'),
    ]
    ax.legend(handles=legend_handles, loc='upper right', fontsize=9)

    ax.set_xlim(-0.5, 14)
    ax.set_ylim(0.5, 8.5)
    ax.axis('off')
    ax.set_title('B&B Decision Tree -- 4 items, capacity 8\n'
                 'Items sorted by value/weight: A(v10,w2), B(v10,w3), C(v12,w5), D(v8,w4)',
                 fontsize=12, fontweight='bold')

    plt.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# 2. Project pipeline: where B&B fits in the capstone.
#    Bottom row shows the two implementation tracks as parallel, independent
#    pipelines (no shared "comparison" endpoint).
# ---------------------------------------------------------------------------
def make_pipeline_diagram():
    fig, ax = plt.subplots(figsize=(15, 8))

    # (x, y, w, h, title, subtitle, color)
    boxes = [
        # Top row: production ILP track
        (0.5, 5.5, 2.2, 1.4, 'Driver-Region\nCSV',
         'driver_id, region_id\ncost, eligible',
         '#bbdefb'),
        (3.4, 5.5, 2.2, 1.4, 'Pre-processing',
         'src/data_\npreprocessing.py',
         '#90caf9'),
        (6.3, 5.5, 2.2, 1.4, 'ILP Model\n(PuLP)',
         'binary x[d,r]\nmin sum cost*x',
         '#64b5f6'),
        (9.2, 5.5, 2.2, 1.4, 'CBC Solver',
         'Branch & Bound\nunder the hood',
         '#ffd54f'),
        (12.1, 5.5, 2.2, 1.4, 'Assignment +\nMetrics',
         'src/evaluation.py',
         '#a5d6a7'),

        # Shared instance source for the research track
        (0.5, 2.5, 2.2, 1.4, 'Knapsack\nInstances',
         'n=3 ... 25',
         '#bbdefb'),

        # Independent Brute Force track (top sub-row)
        (3.4, 3.4, 2.2, 1.0, 'Brute Force',
         'Py / C++ / ASM',
         '#ef9a9a'),
        (6.3, 3.4, 2.2, 1.0, 'Benchmark',
         'O(2^n) timing',
         '#a5d6a7'),

        # Independent Branch & Bound track (bottom sub-row)
        (3.4, 1.5, 2.2, 1.0, 'Branch & Bound',
         'Py / C++ / ASM',
         '#ffd54f'),
        (6.3, 1.5, 2.2, 1.0, 'Benchmark',
         'LP-bound + DFS\ntiming',
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

    # Top row arrows
    arrows_top = [(2.7, 6.2, 3.4, 6.2), (5.6, 6.2, 6.3, 6.2),
                  (8.5, 6.2, 9.2, 6.2), (11.4, 6.2, 12.1, 6.2)]
    for x1, y1, x2, y2 in arrows_top:
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color='black', lw=1.8))

    # Instances -> Brute Force (upper sub-row)
    ax.annotate('', xy=(3.4, 3.9), xytext=(2.7, 3.2),
                arrowprops=dict(arrowstyle='->', color='black', lw=1.6))
    # Brute Force -> Benchmark
    ax.annotate('', xy=(6.3, 3.9), xytext=(5.6, 3.9),
                arrowprops=dict(arrowstyle='->', color='black', lw=1.6))

    # Instances -> B&B (lower sub-row)
    ax.annotate('', xy=(3.4, 2.0), xytext=(2.7, 3.0),
                arrowprops=dict(arrowstyle='->', color='black', lw=1.6))
    # B&B -> Benchmark
    ax.annotate('', xy=(6.3, 2.0), xytext=(5.6, 2.0),
                arrowprops=dict(arrowstyle='->', color='black', lw=1.6))

    # Vertical link showing CBC and B&B share algorithm family
    ax.annotate('', xy=(10.3, 2.5), xytext=(10.3, 5.5),
                arrowprops=dict(arrowstyle='<->', color='#d84315', lw=2.5,
                                linestyle='--'))
    ax.text(11.3, 4.0, 'same\nalgorithm\nfamily',
            ha='center', va='center', fontsize=9, color='#d84315',
            fontweight='bold')

    ax.text(0.6, 7.3, 'Production track -- Logistics ILP',
            fontsize=12, fontweight='bold', color='#0d47a1')
    ax.text(0.6, 4.7, 'Research track -- Knapsack benchmarks (two independent implementations)',
            fontsize=12, fontweight='bold', color='#0d47a1')

    ax.text(7.5, 0.4,
            'Knapsack is the didactic sibling of the driver-region ILP. '
            'Mastering B&B = understanding what CBC is doing for you.',
            ha='center', fontsize=10, style='italic', color='#444')

    ax.set_xlim(0, 15)
    ax.set_ylim(0, 8.0)
    ax.axis('off')
    ax.set_title('Capstone Architecture -- Where Branch & Bound Fits',
                 fontsize=14, fontweight='bold', pad=15)

    plt.tight_layout()
    return fig


if __name__ == '__main__':
    fig1 = make_decision_tree()
    fig1.savefig('results/figures/bb_decision_tree.png', dpi=300, bbox_inches='tight')
    print('Saved: bb_decision_tree.png')

    fig2 = make_pipeline_diagram()
    fig2.savefig('results/figures/project_pipeline.png', dpi=300, bbox_inches='tight')
    print('Saved: project_pipeline.png')

    plt.show()
