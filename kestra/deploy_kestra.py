from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

KESTRA_BASE_URL = os.getenv("KESTRA_BASE_URL", "http://localhost:8080/api/v1")
NAMESPACE = os.getenv("KESTRA_NAMESPACE", "austin_animal_center")

KESTRA_USERNAME = os.getenv("KESTRA_USERNAME")
KESTRA_PASSWORD = os.getenv("KESTRA_PASSWORD")

FLOW_HEADERS = {"Content-Type": "application/x-yaml"}
KV_HEADERS = {"Content-Type": "text/plain"}

REPO_ROOT = Path(__file__).resolve().parent.parent
FLOWS_DIR = REPO_ROOT / "kestra" / "flows"
SCRIPTS_DIR = REPO_ROOT / "scripts"


def get_auth() -> tuple[str, str] | None:
    if KESTRA_USERNAME and KESTRA_PASSWORD:
        return (KESTRA_USERNAME, KESTRA_PASSWORD)
    return None


def raise_for_bad_response(response: requests.Response, context: str) -> None:
    if not response.ok:
        raise RuntimeError(
            f"{context} failed with status {response.status_code}: {response.text}"
        )


def load_gcp_credentials() -> dict[str, Any]:
    creds_path = os.getenv("GCP_CREDS_PATH")
    if not creds_path:
        raise ValueError("GCP_CREDS_PATH is not set in .env")

    creds_file = Path(creds_path)
    if not creds_file.exists():
        raise FileNotFoundError(f"GCP credentials file not found: {creds_file}")

    with creds_file.open("r", encoding="utf-8") as file:
        return json.load(file)


def build_keyvalues() -> dict[str, Any]:
    return {
        "GCP_CREDS": load_gcp_credentials(),
        "GCP_PROJECT_ID": os.getenv("GCP_PROJECT_ID"),
        "GCP_LOCATION": os.getenv("GCP_LOCATION"),
        "GCP_BUCKET_NAME": os.getenv("GCP_BUCKET_NAME"),
        "GCP_DATASET": os.getenv("GCP_DATASET"),
    }


def create_or_update_flow(flow_path: Path) -> None:
    flow_data = flow_path.read_text(encoding="utf-8")

    url = f"{KESTRA_BASE_URL}/flows"
    response = requests.post(
        url,
        data=flow_data,
        headers=FLOW_HEADERS,
        auth=get_auth(),
        timeout=60,
    )

    print(f"Deploying flow: {flow_path.name}")
    raise_for_bad_response(response, f"Flow deploy for {flow_path.name}")
    print(f"OK flow deployed: {flow_path.name}")


def deploy_all_flows() -> None:
    if not FLOWS_DIR.exists():
        print(f"Flows directory does not exist: {FLOWS_DIR}")
        return

    flow_files = sorted(FLOWS_DIR.glob("*.yml"))
    if not flow_files:
        print(f"No flow files found in: {FLOWS_DIR}")
        return

    for flow_path in flow_files:
        create_or_update_flow(flow_path)


def upload_keyvalue(key: str, value: Any) -> None:
    url = f"{KESTRA_BASE_URL}/main/namespaces/{NAMESPACE}/kv/{key}"
    response = requests.put(
        url,
        data=json.dumps(value),
        headers=KV_HEADERS,
        auth=get_auth(),
        timeout=60,
    )

    print(f"Uploading KV: {key}")
    raise_for_bad_response(response, f"KV upload for {key}")
    print(f"OK KV uploaded: {key}")


def upload_all_keyvalues() -> None:
    keyvalues = build_keyvalues()

    missing_keys = [k for k, v in keyvalues.items() if v is None]
    if missing_keys:
        raise ValueError(f"Missing required environment variables for keys: {missing_keys}")

    for key, value in keyvalues.items():
        upload_keyvalue(key, value)


def upload_namespace_file(local_path: Path, namespace_file_path: str) -> None:
    url = f"{KESTRA_BASE_URL}/main/namespaces/{NAMESPACE}/files"
    params = {"path": namespace_file_path}

    with local_path.open("rb") as f:
        response = requests.post(
            url,
            params=params,
            files={"fileContent": (local_path.name, f)},
            auth=get_auth(),
            timeout=60,
        )

    print(f"Uploading namespace file: {namespace_file_path}")
    raise_for_bad_response(response, f"Namespace file upload for {namespace_file_path}")
    print(f"OK namespace file uploaded: {namespace_file_path}")


def deploy_scripts_directory() -> None:
    if not SCRIPTS_DIR.exists():
        print(f"Scripts directory does not exist: {SCRIPTS_DIR}")
        return

    script_files = sorted(SCRIPTS_DIR.rglob("*.py"))
    if not script_files:
        print(f"No Python scripts found in: {SCRIPTS_DIR}")
        return

    for script_path in script_files:
        relative_path = script_path.relative_to(REPO_ROOT).as_posix()
        upload_namespace_file(script_path, relative_path)


def main() -> None:
    print(f"Kestra base URL: {KESTRA_BASE_URL}")
    print(f"Kestra namespace: {NAMESPACE}")

    deploy_all_flows()
    upload_all_keyvalues()
    deploy_scripts_directory()

    print("Kestra deployment completed successfully.")


if __name__ == "__main__":
    main()