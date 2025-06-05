import logging
from gliner import GLiNER
import os
import sys
import json

os.environ["HF_HOME"] = "/root/.cache/huggingface"

def debug_env():
    print("🚀 HF_HOME:", os.environ.get("HF_HOME"))
    print("🚀 TRANSFORMERS_CACHE:", os.environ.get("TRANSFORMERS_CACHE"))
    print("🚀 CWD:", os.getcwd())
    print("🚀 Files in /root/.cache/huggingface:")
    os.system("ls -lh /root/.cache/huggingface/hub")


def load_gliner_model() -> GLiNER:
    print("[DEBUG] Current working directory:", os.getcwd())
    print("[DEBUG] Loading GLiNER model...")
    print(f"HF_HOME: {os.environ.get('HF_HOME')}")
    print(f"TRANSFORMERS_CACHE: {os.environ.get('TRANSFORMERS_CACHE')}")
    return GLiNER.from_pretrained("urchade/gliner_multi-v2.1")


def extract_entities(model: GLiNER, text: str, labels: list[str] | None = None, threshold: float = 0.5):
    if labels is None:
        labels = ["Person", "Company", "Location"]
    return model.predict_entities(text, labels, threshold=threshold)

if __name__ == "__main__":
    debug_env()

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    with open(input_path, "r") as f:
        text = f.read()

    model = load_gliner_model()
    results = extract_entities(model, text)

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"✅ Entity extraction complete: {output_path}")
