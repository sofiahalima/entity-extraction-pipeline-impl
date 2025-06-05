FROM python:3.12

WORKDIR /app


# Install GLiNER and logging tools
RUN pip install --no-cache-dir gliner

# Set HuggingFace default cache location explicitly
ENV HF_HOME=/root/.cache/huggingface
ENV TRANSFORMERS_CACHE=/root/.cache/huggingface

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY run_extractor.py /app/run_extractor.py
COPY extractor.py /app/extractor.py

# Entrypoint (expects 2 args: input_path, output_path)
ENTRYPOINT ["python", "/app/run_extractor.py"]