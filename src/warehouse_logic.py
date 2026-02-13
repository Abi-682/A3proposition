"""Warehouse propositional enumerator for 3x3 grid.
Provides functions to enumerate all models consistent with axioms+percepts
and to compute provable facts (safe/damaged/forklift) across all models.
"""
from itertools import product

coords = [(x, y) for y in (1, 2, 3) for x in (1, 2, 3)]


def neighbors(cell):
    x, y = cell
    neigh = []
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if 1 <= nx <= 3 and 1 <= ny <= 3:
            neigh.append((nx, ny))
    return neigh


def derive_creaks(Dset):
    """Return set of cells where creaking (C) is true given damaged set Dset."""
    Cset = set()
    for cell in coords:
        for n in neighbors(cell):
            if n in Dset:
                Cset.add(cell)
                break
    return Cset


def derive_noises(Fset):
    """Return set of cells where noise (N) is true given forklift set Fset."""
    Nset = set()
    for cell in coords:
        for n in neighbors(cell):
            if n in Fset:
                Nset.add(cell)
                break
    return Nset


def is_safe(cell, Dset, Fset):
    return (cell not in Dset) and (cell not in Fset)


def enumerate_models(percepts=None):
    """Enumerate all models (choices of exactly-one D and exactly-one F)
    that satisfy initial axioms and the given percepts.

    percepts: dict mapping tuples like ('C', (x,y)) to bool, or ('N', (x,y)) to bool.
    Returns list of models; model is dict with keys 'D', 'F', 'C', 'N'.
    """
    if percepts is None:
        percepts = {}

    models = []

    for Dcell in coords:  # exactly one damaged floor
        Dset = {Dcell}
        for Fcell in coords:  # exactly one forklift
            Fset = {Fcell}

            # Initial knowledge: start square (1,1) is safe => not D and not F
            if (1, 1) in Dset or (1, 1) in Fset:
                continue

            Cset = derive_creaks(Dset)
            Nset = derive_noises(Fset)

            # Check percept consistency
            violated = False
            for (sym, cell), val in percepts.items():
                if sym == 'C':
                    if ((cell in Cset) != val):
                        violated = True
                        break
                elif sym == 'N':
                    if ((cell in Nset) != val):
                        violated = True
                        break
                else:
                    raise ValueError('Unknown percept symbol')
            if violated:
                continue

            model = {'D': set(Dset), 'F': set(Fset), 'C': set(Cset), 'N': set(Nset)}
            models.append(model)

    return models


def provable_facts(models):
    """Given a list of models, compute provable facts across all models.
    Returns dicts: provable_safe, provable_damaged, provable_forklift.
    Each is a set of cells that are True in all models for that predicate.
    """
    if not models:
        return set(), set(), set()

    prov_safe = set(coords)
    prov_damaged = set(coords)
    prov_forklift = set(coords)

    for cell in coords:
        for m in models:
            if not is_safe(cell, m['D'], m['F']):
                prov_safe.discard(cell)
            if cell not in m['D']:
                prov_damaged.discard(cell)
            if cell not in m['F']:
                prov_forklift.discard(cell)

    return prov_safe, prov_damaged, prov_forklift


def summarize(models):
    """Return summary strings and sets of possible locations for D and F."""
    prov_safe, prov_damaged, prov_forklift = provable_facts(models)

    # Possible sets (appear in at least one model)
    poss_D = set()
    poss_F = set()
    for m in models:
        poss_D.update(m['D'])
        poss_F.update(m['F'])

    summary = {
        'num_models': len(models),
        'provably_safe': prov_safe,
        'provably_damaged': prov_damaged,
        'provably_forklift': prov_forklift,
        'possible_D': poss_D,
        'possible_F': poss_F,
    }
    return summary
