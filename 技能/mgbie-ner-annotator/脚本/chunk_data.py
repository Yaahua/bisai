import json
import os
import argparse

def chunk_json_data(input_file, output_dir, chunk_size=10):
    """
    将大型 JSON 数据集按指定大小（默认 10 条）拆分为多个小块。
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total_samples = len(data)
    num_chunks = (total_samples + chunk_size - 1) // chunk_size

    print(f"Total samples: {total_samples}")
    print(f"Chunk size: {chunk_size}")
    print(f"Number of chunks: {num_chunks}")

    for i in range(num_chunks):
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, total_samples)
        chunk_data = data[start_idx:end_idx]

        chunk_filename = os.path.join(output_dir, f"chunk_{i+1:03d}.json")
        with open(chunk_filename, 'w', encoding='utf-8') as f:
            json.dump(chunk_data, f, ensure_ascii=False, indent=2)
        
        print(f"Created {chunk_filename} with {len(chunk_data)} samples.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chunk JSON dataset for MGBIE NER Annotator.")
    parser.add_argument("input_file", help="Path to the input JSON file.")
    parser.add_argument("output_dir", help="Directory to save the chunked JSON files.")
    parser.add_argument("--chunk_size", type=int, default=10, help="Number of samples per chunk (default: 10).")
    
    args = parser.parse_args()
    chunk_json_data(args.input_file, args.output_dir, args.chunk_size)
