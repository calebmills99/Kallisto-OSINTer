"""Tests for the Kilocode client wrapper."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from requests.exceptions import HTTPError, RequestException

from src.llm.kilocode_client import KilocodeClient


class TestKilocodeClient(unittest.TestCase):
    def setUp(self) -> None:
        self.api_key = "test-key"
        self.base_url = "https://kilocode.test/v1"

    @patch("src.llm.kilocode_client.requests.post")
    def test_chat_completion_success(self, post_mock: MagicMock) -> None:
        response_mock = MagicMock()
        response_mock.raise_for_status.return_value = None
        response_mock.json.return_value = {
            "choices": [{"message": {"content": "Hello world"}}]
        }
        post_mock.return_value = response_mock

        client = KilocodeClient(api_key=self.api_key, base_url=self.base_url)
        result = client.chat_completion(
            "prompt", system_prompt="system", model="model", temperature=0.7, max_tokens=128
        )

        self.assertEqual(result, "Hello world")
        post_mock.assert_called_once_with(
            "https://kilocode.test/v1/chat/completions",
            headers={
                "Authorization": "Bearer test-key",
                "Content-Type": "application/json",
            },
            json={
                "model": "model",
                "messages": [
                    {"role": "system", "content": "system"},
                    {"role": "user", "content": "prompt"},
                ],
                "temperature": 0.7,
                "max_tokens": 128,
            },
            timeout=30,
        )

    @patch("src.llm.kilocode_client.requests.post")
    def test_chat_completion_http_error(self, post_mock: MagicMock) -> None:
        response_mock = MagicMock()
        response_mock.raise_for_status.side_effect = HTTPError("boom")
        response_mock.status_code = 500
        response_mock.text = "internal error"
        post_mock.return_value = response_mock

        client = KilocodeClient(api_key=self.api_key, base_url=self.base_url)
        with self.assertRaises(RuntimeError) as ctx:
            client.chat_completion(
                "prompt",
                system_prompt="system",
                model="model",
                temperature=0.7,
                max_tokens=128,
            )
        self.assertIn("Kilocode HTTP", str(ctx.exception))
        self.assertIn("500", str(ctx.exception))
        self.assertIn("internal error", str(ctx.exception))

    @patch("src.llm.kilocode_client.requests.post")
    def test_chat_completion_request_exception(self, post_mock: MagicMock) -> None:
        post_mock.side_effect = RequestException("network down")

        client = KilocodeClient(api_key=self.api_key, base_url=self.base_url)
        with self.assertRaises(RuntimeError) as ctx:
            client.chat_completion(
                "prompt",
                system_prompt="system",
                model="model",
                temperature=0.7,
                max_tokens=128,
            )
        self.assertIn("Kilocode request failed", str(ctx.exception))

    @patch("src.llm.kilocode_client.requests.post")
    def test_chat_completion_invalid_json(self, post_mock: MagicMock) -> None:
        response_mock = MagicMock()
        response_mock.raise_for_status.return_value = None
        response_mock.json.side_effect = ValueError("bad json")
        post_mock.return_value = response_mock

        client = KilocodeClient(api_key=self.api_key, base_url=self.base_url)
        with self.assertRaises(RuntimeError) as ctx:
            client.chat_completion(
                "prompt",
                system_prompt="system",
                model="model",
                temperature=0.7,
                max_tokens=128,
            )
        self.assertEqual(str(ctx.exception), "Kilocode returned a non-JSON response")

    @patch("src.llm.kilocode_client.requests.post")
    def test_extract_message_content_logs_warning_for_list(self, post_mock: MagicMock) -> None:
        response_mock = MagicMock()
        response_mock.raise_for_status.return_value = None
        response_mock.json.return_value = {
            "choices": [
                {"message": {"content": ["part1", "part2"]}},
            ]
        }
        post_mock.return_value = response_mock

        client = KilocodeClient(api_key=self.api_key, base_url=self.base_url)
        with self.assertLogs("src.llm.kilocode_client", level="WARNING") as log_cm:
            result = client.chat_completion(
                "prompt",
                system_prompt="system",
                model="model",
                temperature=0.7,
                max_tokens=128,
            )
        self.assertEqual(result, "part1part2")
        self.assertTrue(any("content is a list" in message for message in log_cm.output))


if __name__ == "__main__":
    unittest.main()
