import json

path = '/home/ubuntu/election2026/data/candidates.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Update meta information
data['meta']['lastUpdated'] = "2026-06-02"
if "MBC 여론M (최종 추정치)" not in data['meta']['sources']:
    data['meta']['sources'].insert(1, "MBC 여론M (최종 추정치)")

with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
