#!/usr/bin/env python3
import json
import zipfile
from collections import Counter
from copy import deepcopy
from pathlib import Path

BASE = Path('/home/ubuntu/bisai/数据/A榜')
V17 = BASE / 'submit_v17_whitelist.json'
V21 = BASE / 'submit_v21_elite.json'
SUPPORT_FILES = {
    'v7': BASE / 'submit_v7_cicl_v2.json',
    'v9': BASE / 'submit_v9_clean.json',
    'v10': BASE / 'submit_v10_gemini.json',
}

CONFIGS = {
    'v30_ultrasafe': {
        'triplets': {
            ('ABS', 'AFF', 'TRT'),
            ('QTL', 'LOI', 'CHR'),
            ('CROP', 'CON', 'VAR'),
            ('GENE', 'LOI', 'TRT'),
            ('VAR', 'USE', 'BM'),
        },
        'require_support_from_any': {'v7', 'v9', 'v10'},
    },
    'v30_safe': {
        'triplets': {
            ('ABS', 'AFF', 'TRT'),
            ('QTL', 'LOI', 'CHR'),
            ('CROP', 'CON', 'VAR'),
            ('GENE', 'LOI', 'TRT'),
            ('VAR', 'USE', 'BM'),
            ('ABS', 'AFF', 'GENE'),
            ('CROP', 'USE', 'BM'),
            ('BM', 'AFF', 'TRT'),
            ('QTL', 'AFF', 'TRT'),
        },
        'require_support_from_any': {'v7', 'v9', 'v10'},
    },
    'v30_supported_alltypes': {
        'triplets': None,
        'require_support_from_any': {'v7', 'v9', 'v10'},
    },
}


def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def rel_key(r):
    return (
        r['head'].strip().lower(), r['head_type'],
        r['label'],
        r['tail'].strip().lower(), r['tail_type']
    )


def triplet(r):
    return (r['head_type'], r['label'], r['tail_type'])


def summarize(data):
    n = len(data)
    ent = sum(len(x.get('entities', [])) for x in data)
    rel = sum(len(x.get('relations', [])) for x in data)
    no_rel = sum(1 for x in data if not x.get('relations'))
    return n, ent / n, rel / n, no_rel / n * 100


def main():
    v17 = load(V17)
    v21 = load(V21)
    supports = {name: load(path) for name, path in SUPPORT_FILES.items()}
    n = len(v17)
    assert len(v21) == n
    for name, data in supports.items():
        assert len(data) == n, name

    lines = []
    base_stats = summarize(v17)
    lines.append('=== Baseline ===')
    lines.append(f'v17_whitelist\titems={base_stats[0]}\tent_avg={base_stats[1]:.2f}\trel_avg={base_stats[2]:.2f}\tno_rel={base_stats[3]:.1f}%')

    for out_name, cfg in CONFIGS.items():
        result = deepcopy(v17)
        added_total = 0
        added_triplets = Counter()
        support_hist = Counter()

        for i in range(n):
            base_keys = {rel_key(r) for r in result[i].get('relations', [])}
            v21_map = {rel_key(r): r for r in v21[i].get('relations', [])}
            support_keys = {
                sname: {rel_key(r) for r in sdata[i].get('relations', [])}
                for sname, sdata in supports.items()
            }

            for key, rel in v21_map.items():
                if key in base_keys:
                    continue
                tri = triplet(rel)
                if cfg['triplets'] is not None and tri not in cfg['triplets']:
                    continue
                supporters = {sname for sname, skeys in support_keys.items() if key in skeys}
                if not supporters.intersection(cfg['require_support_from_any']):
                    continue
                result[i]['relations'].append(rel)
                base_keys.add(key)
                added_total += 1
                added_triplets[tri] += 1
                support_hist['+'.join(sorted(supporters))] += 1

        json_path = BASE / f'submit_{out_name}.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        zip_path = BASE / f'submit_{out_name}.zip'
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(json_path, arcname='submit.json')

        st = summarize(result)
        lines.append('\n=== ' + out_name + ' ===')
        lines.append(f'added_total={added_total}\tent_avg={st[1]:.2f}\trel_avg={st[2]:.2f}\tno_rel={st[3]:.1f}%')
        lines.append('support_hist=' + ', '.join(f'{k or "none"}:{v}' for k, v in sorted(support_hist.items(), key=lambda x: (-x[1], x[0]))))
        lines.append('top_triplets=' + ', '.join(f'{a}-{b}-{c}:{v}' for (a,b,c), v in added_triplets.most_common(15)))
        lines.append(f'json={json_path}')
        lines.append(f'zip={zip_path}')

    report = Path('/home/ubuntu/bisai/分析报告/v30_candidate_report.txt')
    report.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(report)
    print(report.read_text(encoding='utf-8'))

if __name__ == '__main__':
    main()
