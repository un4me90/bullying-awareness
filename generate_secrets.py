import os, json, toml

raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "")
if raw:
    creds = json.loads(raw)
    os.makedirs(".streamlit", exist_ok=True)
    with open(".streamlit/secrets.toml", "w") as f:
        toml.dump({"gcp_service_account": creds}, f)
    print("✅ .streamlit/secrets.toml generated")
