#!/usr/bin/env python3
"""
打包提交脚本：将预测结果 JSON 打包为 submit.zip
用法：python make_submit_zip.py <input_json_path>
示例：python make_submit_zip.py /home/ubuntu/bisai/数据/A榜/submit_v6_rag.json
"""
import json
import os
import sys
import zipfile

def make_zip(input_path: str):
    if not os.path.exists(input_path):
        print(f"❌ 文件不存在：{input_path}")
        sys.exit(1)

    # 验证格式
    with open(input_path, encoding='utf-8') as f:
        data = json.load(f)

    print(f"✓ 加载 {len(data)} 条预测结果")

    # 统计
    total_ent = sum(len(item.get('entities', [])) for item in data)
    total_rel = sum(len(item.get('relations', [])) for item in data)
    no_rel    = sum(1 for item in data if len(item.get('relations', [])) == 0)
    print(f"  实体总数: {total_ent} (均值: {total_ent/len(data):.2f}/条)")
    print(f"  关系总数: {total_rel} (均值: {total_rel/len(data):.2f}/条)")
    print(f"  无关系比例: {no_rel}/{len(data)} = {no_rel/len(data)*100:.1f}%")
    print(f"  期望值参考: 实体~5.92/条, 关系~2.80/条, 无关系~32.7%")

    # 打包
    out_dir  = os.path.dirname(input_path)
    zip_name = os.path.basename(input_path).replace('.json', '.zip')
    zip_path = os.path.join(out_dir, zip_name)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(input_path, 'submit.json')

    print(f"\n✅ 打包完成：{zip_path}")
    print(f"   文件大小：{os.path.getsize(zip_path)/1024:.1f} KB")
    print(f"\n请将 {zip_path} 上传到天池平台提交。")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法：python make_submit_zip.py <input_json_path>")
        print("示例：python make_submit_zip.py /home/ubuntu/bisai/数据/A榜/submit_v6_rag.json")
        sys.exit(1)
    make_zip(sys.argv[1])
