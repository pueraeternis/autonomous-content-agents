#!/usr/bin/env python3
"""Manual Twitter/X publishing diagnostic script.

Loads app settings and exercises Tweepy create_tweet in isolation.
Not part of CI — see docs/ENGINEERING.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

import tweepy

from content_agents.core.config import settings

MAX_TWEET_LENGTH = 280

_CREDENTIAL_SPECS: tuple[tuple[str, str], ...] = (
    ("API_KEY", "twitter_api_key"),
    ("API_KEY_SECRET", "twitter_api_secret"),
    ("ACCESS_TOKEN", "twitter_access_token"),
    ("ACCESS_TOKEN_SECRET", "twitter_access_secret"),
)


def _credential_status() -> dict[str, dict[str, object]]:
    status: dict[str, dict[str, object]] = {}
    for env_name, attr_name in _CREDENTIAL_SPECS:
        secret = getattr(settings, attr_name)
        if secret is None:
            status[env_name] = {"present": False, "length": 0}
            continue
        value = secret.get_secret_value()
        status[env_name] = {"present": bool(value), "length": len(value)}
    return status


def _all_credentials_present(status: dict[str, dict[str, object]]) -> bool:
    return all(entry["present"] for entry in status.values())


def _build_client() -> tweepy.Client:
    return tweepy.Client(
        consumer_key=settings.twitter_api_key.get_secret_value(),  # type: ignore[union-attr]
        consumer_secret=settings.twitter_api_secret.get_secret_value(),  # type: ignore[union-attr]
        access_token=settings.twitter_access_token.get_secret_value(),  # type: ignore[union-attr]
        access_token_secret=settings.twitter_access_secret.get_secret_value(),  # type: ignore[union-attr]
    )


def _exception_diagnostics(exc: BaseException) -> dict[str, Any]:
    context: dict[str, Any] = {
        "exception_type": type(exc).__qualname__,
        "message": str(exc),
        "repr": repr(exc),
    }

    response = getattr(exc, "response", None)
    if response is not None:
        context["response_status"] = getattr(response, "status_code", None) or getattr(
            response, "status", None
        )
        response_body = getattr(response, "text", None)
        if not response_body:
            raw_body = getattr(response, "content", None)
            if isinstance(raw_body, bytes):
                response_body = raw_body.decode("utf-8", errors="replace")
            else:
                response_body = raw_body
        if response_body:
            context["response_body"] = response_body

    for attr in ("api_errors", "api_codes", "api_messages"):
        value = getattr(exc, attr, None)
        if value:
            context[attr] = value

    return context


def _validate_text(text: str | None) -> str:
    if text is None or not text.strip():
        print("ERROR: --text is required and must not be empty.", file=sys.stderr)
        sys.exit(1)
    if len(text) > MAX_TWEET_LENGTH:
        print(
            f"ERROR: text length {len(text)} exceeds {MAX_TWEET_LENGTH} characters.",
            file=sys.stderr,
        )
        sys.exit(1)
    return text


def _print_header(*, mode: str, live: bool) -> None:
    creds = _credential_status()
    print("Twitter/X smoke post diagnostic")
    print(f"tweepy version: {tweepy.__version__}")
    print(f"mode: {mode}")
    print(f"live post: {'yes' if live else 'no (dry-run)'}")
    print("credentials:")
    for env_name, entry in creds.items():
        print(f"  {env_name}: present={entry['present']}, length={entry['length']}")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Manual Twitter/X publishing diagnostic (not part of CI)."
    )
    parser.add_argument(
        "--text",
        required=True,
        help="Tweet text to publish (validated even in dry-run).",
    )
    parser.add_argument(
        "--mode",
        choices=("default", "user-auth"),
        default="default",
        help="Tweepy create_tweet mode (default: default).",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Actually publish the tweet. Without this flag, only validates.",
    )
    args = parser.parse_args()

    text = _validate_text(args.text)
    live = args.yes
    _print_header(mode=args.mode, live=live)

    creds = _credential_status()
    if not _all_credentials_present(creds):
        print("FAILURE: one or more credentials are missing.")
        return 1

    client = _build_client()

    if not live:
        print("DRY RUN: credentials present; client created successfully.")
        print(f"DRY RUN: would call create_tweet(text=..., mode={args.mode!r})")
        print(f"DRY RUN: text length={len(text)}")
        print("DRY RUN: pass --yes to publish.")
        return 0

    try:
        if args.mode == "user-auth":
            response = client.create_tweet(text=text, user_auth=True)
        else:
            response = client.create_tweet(text=text)

        tweet_id = response.data["id"] if response.data else None
        print("SUCCESS")
        print(f"tweet_id: {tweet_id}")
        return 0
    except Exception as exc:
        print("FAILURE")
        print(json.dumps(_exception_diagnostics(exc), indent=2, default=str))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
