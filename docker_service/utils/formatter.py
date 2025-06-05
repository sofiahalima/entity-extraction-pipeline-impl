import json
import pandas as pd


def flatten_ner_results(input_json_path: str, output_json_path: str, output_csv_path: str):
    with open(input_json_path, 'r') as f:
        data = json.load(f)

    rows = []
    for item in data:
        doc_id = item["id"]
        for ent in item["entities"]:
            rows.append({
                "doc_id": doc_id,
                "start": ent["start"],
                "end": ent["end"],
                "text": ent["text"],
                "label": ent["label"],
                "score": round(ent["score"], 4)
            })

    df = pd.DataFrame(rows)
    df.to_json(output_json_path, orient='records', indent=2)
    df.to_csv(output_csv_path, index=False)
    print(f"[INFO] Saved JSON to {output_json_path}")
    print(f"[INFO] Saved CSV to {output_csv_path}")
