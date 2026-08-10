import json
import os
import unittest
from pathlib import Path
from unittest import mock

from voltstream.providers import (
    CodexProvider,
    DeepSeekProvider,
    ProviderError,
    _last_codex_usage,
)


class _FakeHttpResponse:
    def __init__(self, payload):
        self._payload = payload
        self.headers = {"x-request-id": "request-1"}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps(self._payload).encode("utf-8")


class ProviderTests(unittest.TestCase):
    def test_codex_output_schema_avoids_known_unsupported_keywords(self):
        schema_path = Path(__file__).parents[1] / "evaluation" / "model_response.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))

        self.assertNotIn("uniqueItems", schema["properties"]["issue_codes"])

    def test_deepseek_requires_environment_key(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ProviderError):
                DeepSeekProvider().generate(
                    model="test", system_prompt="system", user_prompt="user"
                )

    @mock.patch("urllib.request.urlopen")
    def test_deepseek_returns_content_and_usage_without_key(self, urlopen):
        urlopen.return_value = _FakeHttpResponse(
            {
                "model": "deepseek-test",
                "choices": [{"message": {"content": '{"ok":true}'}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 3},
            }
        )
        with mock.patch.dict(os.environ, {"DEEPSEEK_API_KEY": "local-test-value"}):
            result = DeepSeekProvider().generate(
                model="deepseek-test", system_prompt="system", user_prompt="user"
            )
        self.assertEqual(result.content, '{"ok":true}')
        self.assertEqual(result.input_tokens, 10)
        request = urlopen.call_args.args[0]
        self.assertIn("Authorization", request.headers)
        self.assertNotIn("local-test-value", repr(result))

    def test_codex_usage_parser_uses_final_event(self):
        stdout = "\n".join(
            [
                '{"type":"turn.completed","usage":{"input_tokens":10}}',
                '{"type":"turn.completed","usage":{"input_tokens":20,"output_tokens":4}}',
            ]
        )
        self.assertEqual(_last_codex_usage(stdout)["input_tokens"], 20)

    @mock.patch("subprocess.run")
    def test_codex_passes_prompt_on_stdin_and_reads_output(self, run):
        def complete(command, **kwargs):
            output_path = Path(command[command.index("-o") + 1])
            output_path.write_text('{"ok":true}', encoding="utf-8")
            return mock.Mock(
                returncode=0,
                stdout='{"type":"turn.completed","usage":{"input_tokens":8,"output_tokens":2}}',
            )

        run.side_effect = complete
        result = CodexProvider().generate(
            model="closed-test", system_prompt="system", user_prompt="payload"
        )
        self.assertEqual(result.content, '{"ok":true}')
        self.assertEqual(result.input_tokens, 8)
        self.assertIn("system", run.call_args.kwargs["input"])
        command = run.call_args.args[0]
        self.assertEqual(command[-1], "-")
        self.assertIn('model_reasoning_effort="low"', command)


if __name__ == "__main__":
    unittest.main()
