"""hf_retry.py
Utility helper for uploading files to Hugging Face with automatic
retry/back-off when the Hub returns HTTP 429 (rate-limit).
"""
from __future__ import annotations

import time
from typing import Any

from huggingface_hub import upload_file
from huggingface_hub.utils import HfHubHTTPError


def upload_file_with_retry(
    *,
    path_or_fileobj: Any,
    path_in_repo: str,
    repo_id: str,
    token: str,
    repo_type: str = "dataset",
    commit_message: str = "",
    max_attempts: int = 6,
    initial_delay: int = 5,
) -> bool:
    """Upload a single file to a HF repo, retrying on HTTP 429.

    The delay doubles after each 429 (bounded to 60 s) or honours the
    *Retry-After* response header when provided.
    """
    delay = initial_delay
    for attempt in range(1, max_attempts + 1):
        try:
            upload_file(
                path_or_fileobj=path_or_fileobj,
                path_in_repo=path_in_repo,
                repo_id=repo_id,
                repo_type=repo_type,
                token=token,
                commit_message=commit_message,
            )
            return True
        except HfHubHTTPError as err:
            status = getattr(err.response, "status_code", None)
            if status == 429 and attempt < max_attempts:
                retry_after_hdr = err.response.headers.get("Retry-After", "")
                wait_seconds = int(retry_after_hdr) if retry_after_hdr.isdigit() else delay
                print(
                    f"HF upload rate-limited (429) for {path_in_repo}. "
                    f"Retry {attempt}/{max_attempts} in {wait_seconds}s…"
                )
                time.sleep(wait_seconds)
                delay = min(delay * 2, 60)
                continue
            raise  # propagate other errors or final 429
        except Exception:
            raise
    return False 