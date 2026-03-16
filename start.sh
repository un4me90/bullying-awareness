#!/bin/bash
# GCP_SERVICE_ACCOUNT_JSON 환경변수가 있으면 .streamlit/secrets.toml 생성
if [ -n "$GCP_SERVICE_ACCOUNT_JSON" ]; then
    mkdir -p .streamlit
    python3 - <<'PYEOF'
import os, json, toml
creds = json.loads(os.environ["GCP_SERVICE_ACCOUNT_JSON"])
with open(".streamlit/secrets.toml", "w") as f:
    toml.dump({"gcp_service_account": creds}, f)
PYEOF
    echo "✅ .streamlit/secrets.toml 생성 완료"
fi

exec streamlit run dashboard.py \
    --server.port "${PORT:-8501}" \
    --server.address "0.0.0.0" \
    --server.headless true
