import os, json, toml, base64

raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "")
if raw:
    try:
        creds = json.loads(raw)
    except json.JSONDecodeError:
        creds = json.loads(base64.b64decode(raw).decode())
    os.makedirs(".streamlit", exist_ok=True)
    with open(".streamlit/secrets.toml", "w") as f:
        toml.dump({"gcp_service_account": creds}, f)
    print("✅ .streamlit/secrets.toml generated")
