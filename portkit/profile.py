"""Compare CSV frame time traces against a user-chosen frame budget."""
import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path


def percentile(values, percentage):
    if not values:
        raise ValueError('No values')
    sorted_values = sorted(values)
    return sorted_values[max(0, math.ceil(len(sorted_values) * percentage / 100) - 1)]


def _stats(values, budget):
    return {'samples': len(values), 'median_ms': round(statistics.median(values), 3),
            'p95_ms': round(percentile(values, 95), 3),
            'max_ms': round(max(values), 3),
            'over_budget_count': sum(v > budget for v in values)}


def analyze_frames(csv_file: Path, budget_ms=1000 / 30) -> dict:
    if budget_ms <= 0 or not math.isfinite(budget_ms):
        raise ValueError('Frame budget must be positive and finite')
    grouped = defaultdict(lambda: {'work_ms': [], 'total_ms': []})
    with Path(csv_file).open(newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        if not {'work_ms', 'total_ms'}.issubset(reader.fieldnames or []):
            raise ValueError('CSV must contain work_ms and total_ms columns')
        for n, row in enumerate(reader, start=2):
            try:
                work, total = float(row['work_ms']), float(row['total_ms'])
            except (TypeError, ValueError):
                raise ValueError(f'Invalid frame time on row {n}') from None
            if not all(math.isfinite(x) and x >= 0 for x in (work, total)) or work > total:
                raise ValueError(f'Invalid frame timings on row {n}')
            group = (row.get('scene') or 'unknown').strip() or 'unknown'
            grouped[group]['work_ms'].append(work)
            grouped[group]['total_ms'].append(total)
    if not grouped:
        raise ValueError('No samples found')
    return {'budget_ms': round(budget_ms, 3),
            'scenes': {scene: {key: _stats(values, budget_ms) for key, values in metrics.items()}
                       for scene, metrics in sorted(grouped.items())},
            'note': 'Measured total frame time is not the same as work time. Hardware validation is required.'}
