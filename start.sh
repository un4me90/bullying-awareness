#!/bin/bash
python3 generate_secrets.py
exec streamlit run dashboard.py \
    --server.port "${PORT:-8501}" \
    --server.address "0.0.0.0" \
    --server.headless true
