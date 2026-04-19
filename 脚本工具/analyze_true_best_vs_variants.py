#!/usr/bin/env python3
import json
from pathlib import Path
from collections import Counter

ROOT = Path('/home/ubuntu/bisai/数据/A榜')
FILES = {
    'true_best': Path('/home/ubuntu/v30_fixed_upload/submit.json'),
    'v29': ROOT / 'submit_v29_postprocessed.json',
    'v30_safe': ROOT / 'submit_v30_safe.json',
    'v30_ultrasafe': ROOT / 'submit_v30_ultrasafe.json',
    'v30_supported_alltypes': ROOT / 'submit_v30_supported_alltypes.json',
}
OUT = Path('/home/ubuntu/bisai/分析报告/true_best_vs_variants.txt')


def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def rel_key(r):
    return (
        r['head'].strip().lower(), r['head_type'],
        r['label'],
        r['tail'].strip().lower(), r['tail_type']
    )


def rel_triplet(r):
    return (r['head_type'], r['label'], r['tail_type'])


def keyed(item):
    return {rel_key(r): r for r in item.get('relations', [])}


data = {k: load(v) for k, v in FILES.items()}
base = data['true_best']

lines = []
for name, items in data.items():
    ent = sum(len(x.get('entities', [])) for x in items)/len(items)
    rel = sum(len(x.get('relations', [])) for x in items)/len(items)
    no_rel = sum(1 for x in items if not x.get('relations'))/len(items)*100
    lines.append(f'{name}: ent_avg={ent:.2f} rel_avg={rel:.2f} no_rel={no_rel:.1f}%')

lines.append('')
for name in ['v29', 'v30_safe', 'v30_ultrasafe', 'v30_supported_alltypes']:
    other = data[name]
    only_base = Counter()
    only_other = Counter()
    item_gain = []
    item_loss = []
    overlap_support = Counter()
    for idx, (ib, io) in enumerate(zip(base, other)):
        kb = keyed(ib)
        ko = keyed(io)
        add = kb.keys() - ko.keys()
        rem = ko.keys() - kb.keys()
        if add:
            item_gain.append((len(add), idx, ib['text'][:120].replace('\n', ' ')))
        if rem:
            item_loss.append((len(rem), idx, ib['text'][:120].replace('\n', ' ')))
        for k in add:
            only_base[rel_triplet(kb[k])] += 1
        for k in rem:
            only_other[rel_triplet(ko[k])] += 1
        # see whether base-only relation is present in other variants
        if name == 'v29':
            ks = keyed(data['v30_safe'][idx])
            ku = keyed(data['v30_ultrasafe'][idx])
            ka = keyed(data['v30_supported_alltypes'][idx])
            for k in add:
                bucket = []
                if k in ks:
                    bucket.append('safe')
                if k in ku:
                    bucket.append('ultra')
                if k in ka:
                    bucket.append('all')
                overlap_support['+'.join(bucket) if bucket else 'none'] += 1
    item_gain.sort(reverse=True)
    item_loss.sort(reverse=True)
    lines.append(f'=== true_best vs {name} ===')
    lines.append('only_true_best_top=' + ', '.join(f'{a}-{b}-{c}:{n}' for (a,b,c), n in only_base.most_common(20)))
    lines.append('only_' + name + '_top=' + ', '.join(f'{a}-{b}-{c}:{n}' for (a,b,c), n in only_other.most_common(20)))
    lines.append('gain_examples=' + ' | '.join(f'idx={idx} add={cnt} {txt}' for cnt, idx, txt in item_gain[:10]))
    lines.append('loss_examples=' + ' | '.join(f'idx={idx} rem={cnt} {txt}' for cnt, idx, txt in item_loss[:10]))
    if name == 'v29':
        lines.append('true_best_over_v29_overlap_with_v30_variants=' + ', '.join(f'{k}:{v}' for k, v in overlap_support.items()))
    lines.append('')

OUT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(OUT)
print(OUT.read_text(encoding='utf-8'))
