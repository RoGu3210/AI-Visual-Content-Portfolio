#!/usr/bin/env python3
"""
generate_infographic.py
=======================

A small, self-contained client for generating images with **Nano Banana 2**
on **Kie.ai** (https://kie.ai). It does exactly one job: take a finished prompt,
create one task per requested variation, poll until each is done, and download
the resulting images to disk.

It deliberately does NOT do any web search, scraping, or content summarizing.
Inside Claude Code, Claude performs the research + prompt-crafting (see the
`/infographic-generator` skill) and then calls this script with a ready prompt.

Workflow (per the official docs at https://docs.kie.ai):
    1. POST https://api.kie.ai/api/v1/jobs/createTask   -> returns a taskId
    2. GET  https://api.kie.ai/api/v1/jobs/recordInfo    -> poll until state=success
    3. The image URL lives in data.resultJson["resultUrls"][0]; download it
       immediately (Kie.ai result URLs expire ~24h after generation).

The Kie.ai API returns ONE image per request, so N "variations" are simply N
independent requests, which this script runs in parallel.

Usage:
    py generate_infographic.py --prompt-file prompt.txt --name kie_infographic
    py generate_infographic.py --prompt "a hand-drawn infographic about cats" --variations 3

Auth:
    Reads KIE_API_KEY from the environment or from a local .env file.
    Get a key at https://kie.ai/api-key. The key is never printed.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #
API_BASE = "https://api.kie.ai/api/v1"
CREATE_TASK_URL = f"{API_BASE}/jobs/createTask"
RECORD_INFO_URL = f"{API_BASE}/jobs/recordInfo"
MODEL = "nano-banana-2"

# Allowed values, mirrored from docs.kie.ai/market/google/nanobanana2 so we can
# fail fast with a friendly message instead of a 422 from the API.
ALLOWED_ASPECT_RATIOS = {
    "1:1", "1:4", "1:8", "2:3", "3:2", "3:4", "4:1", "4:3",
    "4:5", "5:4", "8:1", "9:16", "16:9", "21:9", "auto",
}
ALLOWED_RESOLUTIONS = {"1K", "2K", "4K"}
ALLOWED_OUTPUT_FORMATS = {"png", "jpg"}

# Terminal task states reported by recordInfo.
STATE_SUCCESS = "success"
STATE_FAIL = "fail"

# HTTP statuses worth retrying (rate limit + transient server errors).
RETRYABLE_STATUSES = {429, 500, 502, 503, 504}


# --------------------------------------------------------------------------- #
# Environment / API key
# --------------------------------------------------------------------------- #
def load_env(env_path: Path | None = None) -> None:
    """Populate os.environ from a local .env file without overwriting existing
    variables. Minimal parser (KEY=VALUE, ignores blank lines and # comments)
    so we don't need a python-dotenv dependency."""
    if env_path is None:
        env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.is_file():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def get_api_key() -> str:
    key = os.environ.get("KIE_API_KEY", "").strip()
    if not key:
        sys.exit(
            "ERROR: KIE_API_KEY is not set.\n"
            "  - Add it to a .env file next to this script:  KIE_API_KEY=your_key_here\n"
            "  - Or set it for the session:  $env:KIE_API_KEY = 'your_key_here'\n"
            "  Get a key at https://kie.ai/api-key"
        )
    return key


def auth_headers(api_key: str) -> dict:
    return {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}


# --------------------------------------------------------------------------- #
# API calls
# --------------------------------------------------------------------------- #
def create_task(
    prompt: str,
    aspect_ratio: str,
    resolution: str,
    output_format: str,
    api_key: str,
) -> str:
    """Create one generation task and return its taskId."""
    payload = {
        "model": MODEL,
        "input": {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
            "output_format": output_format,
        },
    }
    resp = _request_with_retry(
        "POST", CREATE_TASK_URL, headers=auth_headers(api_key), json=payload
    )
    body = resp.json()
    if body.get("code") != 200:
        raise RuntimeError(
            f"createTask failed (code={body.get('code')}): {body.get('msg', 'unknown error')}"
        )
    task_id = (body.get("data") or {}).get("taskId")
    if not task_id:
        raise RuntimeError(f"createTask returned no taskId: {body}")
    return task_id


def poll_task(task_id: str, api_key: str, timeout: int, interval: float) -> dict:
    """Poll recordInfo until the task reaches a terminal state. Returns the
    `data` dict on success; raises on failure or timeout."""
    deadline = time.monotonic() + timeout
    while True:
        resp = _request_with_retry(
            "GET",
            RECORD_INFO_URL,
            headers=auth_headers(api_key),
            params={"taskId": task_id},
        )
        body = resp.json()
        if body.get("code") != 200:
            raise RuntimeError(
                f"recordInfo failed (code={body.get('code')}): {body.get('msg', 'unknown error')}"
            )
        data = body.get("data") or {}
        state = data.get("state")
        if state == STATE_SUCCESS:
            return data
        if state == STATE_FAIL:
            raise RuntimeError(
                f"Generation failed for task {task_id} "
                f"(failCode={data.get('failCode')}): {data.get('failMsg', 'no message')}"
            )
        if time.monotonic() >= deadline:
            raise TimeoutError(
                f"Task {task_id} did not finish within {timeout}s "
                f"(last state: {state!r}). Try a larger --timeout."
            )
        time.sleep(interval)


def extract_url(data: dict) -> str:
    """Pull the first generated image URL out of recordInfo's `data`."""
    result_json = data.get("resultJson")
    if isinstance(result_json, str):
        result_json = json.loads(result_json)
    if not isinstance(result_json, dict):
        raise RuntimeError(f"Unexpected resultJson shape: {data.get('resultJson')!r}")
    urls = result_json.get("resultUrls") or []
    if not urls:
        raise RuntimeError(f"No resultUrls in response: {result_json}")
    return urls[0]


def download_image(url: str, dest: Path) -> int:
    """Stream an image URL to disk. Returns bytes written."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        with dest.open("wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    written += len(chunk)
    if written == 0:
        raise RuntimeError(f"Downloaded 0 bytes from {url}")
    return written


def _request_with_retry(method: str, url: str, *, max_retries: int = 4, **kwargs):
    """HTTP wrapper with backoff on rate limits / transient 5xx. Surfaces clean
    messages for the common auth/credit errors."""
    timeout = kwargs.pop("timeout", 60)
    last_exc: Exception | None = None
    for attempt in range(max_retries):
        try:
            resp = requests.request(method, url, timeout=timeout, **kwargs)
        except requests.RequestException as exc:
            last_exc = exc
            time.sleep(2 ** attempt)
            continue
        if resp.status_code == 401:
            sys.exit("ERROR: 401 Unauthorized — your KIE_API_KEY is missing or invalid.")
        if resp.status_code == 402:
            sys.exit("ERROR: 402 Payment Required — insufficient Kie.ai credits. Top up at https://kie.ai.")
        if resp.status_code in RETRYABLE_STATUSES and attempt < max_retries - 1:
            # Honor Retry-After if present, else exponential backoff.
            wait = float(resp.headers.get("Retry-After", 2 ** (attempt + 1)))
            time.sleep(wait)
            continue
        try:
            resp.raise_for_status()
        except requests.HTTPError as exc:
            raise RuntimeError(f"HTTP {resp.status_code} from {url}: {resp.text[:300]}") from exc
        return resp
    raise RuntimeError(f"Request to {url} failed after {max_retries} attempts: {last_exc}")


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #
def _one_variation(
    index: int,
    prompt: str,
    args: argparse.Namespace,
    api_key: str,
    ext: str,
) -> dict:
    """Run a single variation end to end. Returns a result record (never raises;
    failures are captured so other variations can still succeed)."""
    label = f"v{index}"
    dest = Path(args.out) / f"{args.name}_{label}.{ext}"
    record: dict = {"label": label, "path": str(dest), "ok": False}
    try:
        task_id = create_task(
            prompt, args.aspect_ratio, args.resolution, args.output_format, api_key
        )
        record["taskId"] = task_id
        data = poll_task(task_id, api_key, args.timeout, args.poll_interval)
        url = extract_url(data)
        size = download_image(url, dest)
        record.update(
            ok=True,
            bytes=size,
            credits=data.get("creditsConsumed"),
            cost_time_ms=data.get("costTime"),
        )
    except SystemExit:
        raise  # let 401/402 hard-exit propagate
    except Exception as exc:  # noqa: BLE001 - we want to report, not crash
        record["error"] = str(exc)
    return record


def generate(prompt: str, args: argparse.Namespace, api_key: str) -> list[dict]:
    ext = "png" if args.output_format == "png" else "jpg"
    print(
        f"Generating {args.variations} variation(s) with {MODEL} "
        f"[{args.aspect_ratio}, {args.resolution}, {args.output_format}] -> {args.out}/\n"
    )
    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=min(args.variations, 8)) as pool:
        futures = {
            pool.submit(_one_variation, i, prompt, args, api_key, ext): i
            for i in range(1, args.variations + 1)
        }
        for fut in as_completed(futures):
            results.append(fut.result())
    results.sort(key=lambda r: r["label"])
    return results


def print_summary(results: list[dict], elapsed: float) -> None:
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    ok = [r for r in results if r["ok"]]
    for r in results:
        if r["ok"]:
            kb = r["bytes"] / 1024
            credits = r.get("credits")
            credits_str = f", {credits} credits" if credits is not None else ""
            print(f"  [OK]   {r['path']}  ({kb:,.0f} KB{credits_str})")
        else:
            print(f"  [FAIL] {r['label']}: {r.get('error', 'unknown error')}")
    total_credits = sum(r.get("credits") or 0 for r in ok)
    print("-" * 60)
    print(
        f"  {len(ok)}/{len(results)} succeeded in {elapsed:.1f}s"
        + (f"  |  {total_credits} credits used" if total_credits else "")
    )
    print("=" * 60)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Generate infographic images with Kie.ai Nano Banana 2.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--prompt", help="The full image prompt as a string.")
    src.add_argument(
        "--prompt-file",
        help="Path to a UTF-8 text file containing the prompt "
        "(preferred for long prompts to avoid shell-escaping).",
    )
    p.add_argument("--name", default="infographic", help="Base filename for outputs.")
    p.add_argument("--variations", type=int, default=2, help="How many images to generate (parallel requests).")
    p.add_argument("--aspect-ratio", default="3:4", choices=sorted(ALLOWED_ASPECT_RATIOS), metavar="RATIO",
                   help="Image aspect ratio. Portrait infographics: 3:4 / 2:3 / 9:16.")
    p.add_argument("--resolution", default="2K", choices=sorted(ALLOWED_RESOLUTIONS),
                   help="1K (~$0.04), 2K (~$0.06), 4K (~$0.09) per image.")
    p.add_argument("--output-format", default="png", choices=sorted(ALLOWED_OUTPUT_FORMATS),
                   help="Image file format.")
    p.add_argument("--out", default="generated", help="Output directory.")
    p.add_argument("--timeout", type=int, default=300, help="Max seconds to wait per variation.")
    p.add_argument("--poll-interval", type=float, default=3.0, help="Seconds between status polls.")
    args = p.parse_args(argv)

    if args.variations < 1:
        p.error("--variations must be >= 1")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.prompt_file:
        prompt_path = Path(args.prompt_file)
        if not prompt_path.is_file():
            sys.exit(f"ERROR: prompt file not found: {prompt_path}")
        prompt = prompt_path.read_text(encoding="utf-8").strip()
    else:
        prompt = args.prompt.strip()
    if not prompt:
        sys.exit("ERROR: the prompt is empty.")

    load_env()
    api_key = get_api_key()

    start = time.monotonic()
    results = generate(prompt, args, api_key)
    print_summary(results, time.monotonic() - start)

    return 0 if any(r["ok"] for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
