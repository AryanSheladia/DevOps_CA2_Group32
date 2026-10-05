#!/usr/bin/env python3
"""Check readiness and run the repository's sample CSV through a live app."""

import argparse
import time
import uuid
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def request(url: str, *, data: bytes | None = None, headers: dict | None = None):
    req = Request(url, data=data, headers=headers or {})
    with urlopen(req, timeout=15) as response:
        return response.status, response.read()


def wait_until_ready(base_url: str) -> None:
    deadline = time.monotonic() + 90
    last_error = "no response"
    while time.monotonic() < deadline:
        try:
            status, body = request(f"{base_url}/ready")
            if status == 200 and b'"status":"ready"' in body.replace(b" ", b""):
                return
            last_error = f"HTTP {status}: {body[:200]!r}"
        except (HTTPError, URLError, TimeoutError) as exc:
            last_error = str(exc)
        time.sleep(3)
    raise RuntimeError(f"Application did not become ready: {last_error}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--csv", required=True, type=Path)
    args = parser.parse_args()

    csv_bytes = args.csv.read_bytes()
    boundary = f"----networkx-{uuid.uuid4().hex}"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{args.csv.name}"\r\n'
        "Content-Type: text/csv\r\n\r\n"
    ).encode() + csv_bytes + f"\r\n--{boundary}--\r\n".encode()

    wait_until_ready(args.base_url.rstrip("/"))
    status, response = request(
        f"{args.base_url.rstrip('/')}/predict",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    if status != 200:
        raise RuntimeError(f"Prediction returned HTTP {status}")
    if b"predicted_column" not in response:
        raise RuntimeError("Prediction response does not contain predicted_column")

    expected_rows = sum(1 for line in csv_bytes.splitlines() if line.strip()) - 1
    predicted_rows = response.count(b"<tr") - 1  # Ignore the HTML table header row.
    if expected_rows < 1 or predicted_rows != expected_rows:
        raise RuntimeError(
            f"Expected predictions for {expected_rows} rows, found {predicted_rows}"
        )
    print(f"Prediction smoke test passed: {predicted_rows} rows predicted.")


if __name__ == "__main__":
    main()
