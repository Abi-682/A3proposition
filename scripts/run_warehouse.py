"""Runner script for the 3x3 hazardous warehouse logic.
Generates summaries and saves simple grid diagrams (PNG if matplotlib available).
"""
import os
import sys

# Add workspace root to path so we can import src module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.warehouse_logic import enumerate_models, summarize, coords

OUT_DIR = 'scripts/output'
os.makedirs(OUT_DIR, exist_ok=True)


def coords_to_label(cell):
    return f"({cell[0]},{cell[1]})"


def ascii_grid_label(prov_safe, possible_D, possible_F):
    # Return a simple multiline string representing the grid (j=3 down to 1)
    rows = []
    for y in (3, 2, 1):
        cells = []
        for x in (1, 2, 3):
            c = (x, y)
            if c in prov_safe:
                cells.append('SAFE')
            elif c in possible_D and c in possible_F:
                cells.append('P:D+F')
            elif c in possible_D:
                cells.append('P:D')
            elif c in possible_F:
                cells.append('P:F')
            else:
                cells.append('???')
        rows.append(' | '.join(f"{cell:5}" for cell in cells))
    return '\n'.join(rows)


def try_draw_png(filename, prov_safe, possible_D, possible_F):
    try:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(3, 3))
        ax.set_xlim(0, 3)
        ax.set_ylim(0, 3)
        ax.set_xticks([])
        ax.set_yticks([])
        for x in (0, 1, 2, 3):
            ax.plot([x, x], [0, 3], color='k', lw=1)
        for y in (0, 1, 2, 3):
            ax.plot([0, 3], [y, y], color='k', lw=1)

        for (cx, cy) in coords:
            rx = cx - 1
            ry = cy - 1
            cell = (cx, cy)
            if cell in prov_safe:
                color = '#c6f6d5'
                label = 'SAFE'
            elif cell in possible_D and cell in possible_F:
                color = '#f9d6d6'
                label = 'P:D+F'
            elif cell in possible_D:
                color = '#fff3b0'
                label = 'P:D'
            elif cell in possible_F:
                color = '#bcdff9'
                label = 'P:F'
            else:
                color = '#e6e6e6'
                label = '???'
            rect = plt.Rectangle((rx, ry), 1, 1, facecolor=color, edgecolor='k')
            ax.add_patch(rect)
            ax.text(rx + 0.5, ry + 0.5, label, ha='center', va='center', fontsize=8)

        ax.invert_yaxis()
        plt.tight_layout()
        fig.savefig(filename, dpi=150)
        plt.close(fig)
        return True
    except Exception:
        return False


def run():
    # Scenario 1: robot at (1,1) perceives no creaking and no noise
    percepts1 = {('C', (1, 1)): False, ('N', (1, 1)): False}
    models1 = enumerate_models(percepts1)
    summary1 = summarize(models1)

    # Print summary 1
    print('--- Scenario 1: at (1,1), ¬C, ¬N ---')
    print('Models consistent:', summary1['num_models'])
    print('Provably safe:', sorted(summary1['provably_safe']))
    print('Possible damaged-floor locations:', sorted(summary1['possible_D']))
    print('Possible forklift locations:', sorted(summary1['possible_F']))
    print('\nGrid (ASCII):')
    ascii1 = ascii_grid_label(summary1['provably_safe'], summary1['possible_D'], summary1['possible_F'])
    print(ascii1)

    png1 = os.path.join(OUT_DIR, 'scenario1.png')
    ok1 = try_draw_png(png1, summary1['provably_safe'], summary1['possible_D'], summary1['possible_F'])
    if ok1:
        print('Saved diagram to', png1)
    else:
        print('matplotlib not available, skipped PNG for scenario1')

    # Scenario 2: robot moves to (2,1) and perceives creaking and no noise
    percepts2 = {('C', (1, 1)): False, ('N', (1, 1)): False, ('C', (2, 1)): True, ('N', (2, 1)): False}
    models2 = enumerate_models(percepts2)
    summary2 = summarize(models2)

    print('\n--- Scenario 2: moved to (2,1), C, ¬N ---')
    print('Models consistent:', summary2['num_models'])
    print('Provably safe:', sorted(summary2['provably_safe']))
    print('Possible damaged-floor locations:', sorted(summary2['possible_D']))
    print('Possible forklift locations:', sorted(summary2['possible_F']))
    print('\nGrid (ASCII):')
    ascii2 = ascii_grid_label(summary2['provably_safe'], summary2['possible_D'], summary2['possible_F'])
    print(ascii2)

    png2 = os.path.join(OUT_DIR, 'scenario2.png')
    ok2 = try_draw_png(png2, summary2['provably_safe'], summary2['possible_D'], summary2['possible_F'])
    if ok2:
        print('Saved diagram to', png2)
    else:
        print('matplotlib not available, skipped PNG for scenario2')


if __name__ == '__main__':
    run()
