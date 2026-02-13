import json
from pathlib import Path

def load_jsonl(filepath):
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    json_obj = json.loads(line)
                    data.append(json_obj)
                except json.JSONDecodeError as e:
                    print(f"error parseing lin : {e}")
    return data
    

KNOWLEDGE_FILE_PATH = "C:/Users/Gopinath/Desktop/productrag/knowledge-base"

data = []
for file in Path(KNOWLEDGE_FILE_PATH).iterdir():
    data.extend(load_jsonl(KNOWLEDGE_FILE_PATH+"/"+file.name))



