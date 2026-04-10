import json
import argparse
import sys

def check_format(input_file):
    """
    验证最终输出的 JSON 是否符合比赛提交格式要求。
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {input_file}. Details: {e}")
        sys.exit(1)

    if not isinstance(data, list):
        print(f"Error: Root element must be a list of objects.")
        sys.exit(1)

    required_keys = {'text', 'entities', 'relations'}
    entity_keys = {'start', 'end', 'text', 'label'}
    relation_keys = {'head', 'head_start', 'head_end', 'head_type', 'tail', 'tail_start', 'tail_end', 'tail_type', 'label'}

    valid_entity_labels = {'CROP', 'VAR', 'TRT', 'GST', 'GENE', 'QTL', 'MRK', 'CHR', 'BM', 'CROSS', 'ABS', 'BIS'}
    valid_relation_labels = {'CON', 'USE', 'HAS', 'AFF', 'OCI', 'LOI'}

    errors = []

    for i, sample in enumerate(data):
        if not isinstance(sample, dict):
            errors.append(f"Sample {i}: Must be a dictionary.")
            continue

        missing_keys = required_keys - set(sample.keys())
        if missing_keys:
            errors.append(f"Sample {i}: Missing required keys: {missing_keys}")

        if 'entities' in sample:
            for j, ent in enumerate(sample['entities']):
                missing_ent_keys = entity_keys - set(ent.keys())
                if missing_ent_keys:
                    errors.append(f"Sample {i}, Entity {j}: Missing keys: {missing_ent_keys}")
                if 'label' in ent and ent['label'] not in valid_entity_labels:
                    errors.append(f"Sample {i}, Entity {j}: Invalid label '{ent['label']}'")

        if 'relations' in sample:
            for k, rel in enumerate(sample['relations']):
                missing_rel_keys = relation_keys - set(rel.keys())
                if missing_rel_keys:
                    errors.append(f"Sample {i}, Relation {k}: Missing keys: {missing_rel_keys}")
                if 'label' in rel and rel['label'] not in valid_relation_labels:
                    errors.append(f"Sample {i}, Relation {k}: Invalid label '{rel['label']}'")

    if errors:
        print(f"Format validation failed with {len(errors)} errors:")
        for err in errors[:20]:
            print(f"  - {err}")
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more errors.")
        sys.exit(1)
    else:
        print(f"Format validation passed for {len(data)} samples.")
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate JSON format for MGBIE submission.")
    parser.add_argument("input_file", help="Path to the JSON file to validate.")
    
    args = parser.parse_args()
    check_format(args.input_file)
