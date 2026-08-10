"""Minimal, auditable model-provider adapters used by the experiments.

The adapters intentionally return raw text plus provider metadata. They never
interpret business fields; parsing and routing remain in ``model_pipeline``.
Credentials are read at call time from environment variables and are never
included in exceptions, result objects, or command-line arguments.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


class ProviderError(RuntimeError):
    """A sanitized model-provider failure safe to record in experiment logs."""


@dataclass(frozen=True)
class ProviderResponse:
    """Raw provider output and reproducibility metadata for one call."""

    content: str
    model: str
    latency_ms: float
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    cached_input_tokens: Optional[int] = None
    provider_request_id: Optional[str] = None


class DeepSeekProvider:
    """Call DeepSeek's OpenAI-compatible chat-completions endpoint."""

    def __init__(
        self,
        api_key_env: str = "DEEPSEEK_API_KEY",
        base_url: str = "https://api.deepseek.com/chat/completions",
        timeout_seconds: float = 120.0,
    ) -> None:
        self._api_key_env = api_key_env
        self._base_url = base_url
        self._timeout_seconds = timeout_seconds

    def generate(
        self,
        *,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 2048,
        thinking_enabled: bool = False,
    ) -> ProviderResponse:
        api_key = os.environ.get(self._api_key_env)
        if not api_key:
            raise ProviderError(
                f"Required environment variable {self._api_key_env} is not configured."
            )

        body = json.dumps(
            {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "response_format": {"type": "json_object"},
                "temperature": temperature,
                "max_tokens": max_tokens,
                "thinking": {"type": "enabled" if thinking_enabled else "disabled"},
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            self._base_url,
            data=body,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        started = time.perf_counter()
        try:
            with urllib.request.urlopen(request, timeout=self._timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
                request_id = response.headers.get("x-request-id")
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            # Never include request headers or the API key in a recorded error.
            raise ProviderError(f"DeepSeek request failed: {type(exc).__name__}") from exc
        latency_ms = (time.perf_counter() - started) * 1000

        try:
            choice = payload["choices"][0]
            content = choice["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            error = payload.get("error", {}) if isinstance(payload, dict) else {}
            error_type = error.get("type", "invalid_response") if isinstance(error, dict) else "invalid_response"
            raise ProviderError(f"DeepSeek returned no model content ({error_type}).") from exc

        usage = payload.get("usage", {})
        return ProviderResponse(
            content=content,
            model=str(payload.get("model") or model),
            latency_ms=latency_ms,
            input_tokens=_optional_int(usage.get("prompt_tokens")),
            output_tokens=_optional_int(usage.get("completion_tokens")),
            cached_input_tokens=_optional_int(usage.get("prompt_cache_hit_tokens")),
            provider_request_id=request_id,
        )


class CodexProvider:
    """Use the authenticated local Codex CLI as the closed-model provider."""

    def __init__(self, executable: str = "codex", timeout_seconds: float = 180.0) -> None:
        self._executable = executable
        self._timeout_seconds = timeout_seconds

    def generate(
        self,
        *,
        model: str,
        system_prompt: str,
        user_prompt: str,
        output_schema: Optional[Path] = None,
        reasoning_effort: str = "low",
    ) -> ProviderResponse:
        combined_prompt = f"{system_prompt.rstrip()}\n\nINPUT\n{user_prompt.rstrip()}\n"
        with tempfile.TemporaryDirectory(prefix="voltstream-codex-") as directory:
            output_path = Path(directory) / "last-message.json"
            command = [
                self._executable,
                "exec",
                "--ephemeral",
                "--ignore-user-config",
                "--ignore-rules",
                "--sandbox",
                "read-only",
                "--skip-git-repo-check",
                "-C",
                directory,
                "-m",
                model,
                "-c",
                f'model_reasoning_effort="{reasoning_effort}"',
                "--json",
                "-o",
                str(output_path),
            ]
            if output_schema is not None:
                command.extend(["--output-schema", str(output_schema.resolve())])
            command.append("-")

            started = time.perf_counter()
            try:
                completed = subprocess.run(
                    command,
                    input=combined_prompt,
                    capture_output=True,
                    text=True,
                    timeout=self._timeout_seconds,
                    check=False,
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise ProviderError(f"Codex invocation failed: {type(exc).__name__}") from exc
            latency_ms = (time.perf_counter() - started) * 1000

            if completed.returncode != 0 or not output_path.exists():
                # stderr may contain local paths or plugin details, so retain only
                # the exit code in the durable experiment error.
                raise ProviderError(f"Codex exited with status {completed.returncode}.")

            usage = _last_codex_usage(completed.stdout)
            return ProviderResponse(
                content=output_path.read_text(encoding="utf-8"),
                model=model,
                latency_ms=latency_ms,
                input_tokens=_optional_int(usage.get("input_tokens")),
                output_tokens=_optional_int(usage.get("output_tokens")),
                cached_input_tokens=_optional_int(usage.get("cached_input_tokens")),
            )


def _last_codex_usage(stdout: str) -> dict[str, Any]:
    """Return usage from the final machine-readable Codex event, if present."""

    usage: dict[str, Any] = {}
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
            usage = event["usage"]
    return usage


def _optional_int(value: Any) -> Optional[int]:
    return value if isinstance(value, int) and not isinstance(value, bool) else None
