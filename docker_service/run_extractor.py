import json
import sys
import pandas as pd
from datetime import datetime
from extractor import load_gliner_model, extract_entities

import os
import logging

logger = logging.getLogger(__name__)

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
input_csv = sys.argv[1]
output_json = sys.argv[2]

df = pd.read_csv(input_csv)

model = load_gliner_model()

results = []
for _, row in df.iterrows():
    entities = extract_entities(model, row["body_en"])
    results.append({"id": row["uuid"], "entities": entities})

# Write result
with open(output_json, 'w') as f:
    json.dump(results, f, indent=2)

logger.info(f"[INFO] Extraction complete: {output_json}")


