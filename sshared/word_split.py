from asyncio import Semaphore, gather
from base64 import b64encode
from datetime import datetime, timezone
from hashlib import sha1
from hmac import new as hmac_new
from itertools import chain
from random import randint
from re import findall
from typing import Any
from urllib.parse import quote

from httpx import AsyncClient
from msgspec.json import decode as json_decode

_CHUNK_SEPARATOR: set[str] = {"，", "。", "？", "！", "\n"}


class WordSplitter:
    def __init__(
        self,
        *,
        access_key_id: str,
        access_key_secret: str,
        max_concurrency: int = 5,
        max_chars_per_chunk: int = 1024,
    ) -> None:
        self._access_key_id = access_key_id
        self._access_key_secret = access_key_secret
        self._client = AsyncClient()
        self._semaphore = Semaphore(max_concurrency)
        self._max_chars_per_chunk = max_chars_per_chunk

    def _clean_input_text(self, text: str) -> str:
        # 只保留中文字符与标点符号
        return "".join(findall(r"[\u4e00-\u9fff\u3000-\u303f\n]", text))

    def _split_into_chunks(self, text: str) -> list[str]:
        micro_chunks: list[str] = []
        now_chars: list[str] = []

        # 按照中文标点进行分割，避免影响分词效果
        for char in text:
            if char in _CHUNK_SEPARATOR:
                # 避免空字符串作为 chunk
                if any(now_chars):
                    micro_chunks.append("".join(now_chars))
                now_chars.clear()
            else:
                now_chars.append(char)
        if any(now_chars):
            micro_chunks.append("".join(now_chars))
        now_chars.clear()

        chunks: list[str] = []
        now_chunks: list[str] = []
        now_chunks_chars: int = 0

        # 将 micro chunks 组合为多个不超过最大字符数限制的 chunks
        for micro_chunk in micro_chunks:
            # 如果再添加一个 micro chunk 就要超出字符限制
            # 就将现在的 micro chunks 合并成一个 chunk
            # 每个 micro chunks 间以空格分隔
            if (
                now_chunks_chars + len(micro_chunk) + len(now_chunks) - 1
                > self._max_chars_per_chunk
            ):
                chunks.append(" ".join(now_chunks))

                now_chunks = [micro_chunk]
                now_chunks_chars = len(micro_chunks)
            else:
                now_chunks.append(micro_chunk)
                now_chunks_chars += len(micro_chunk)
        chunks.append(" ".join(now_chunks))
        now_chunks.clear()

        return chunks

    def _get_data(self, text: str) -> dict[str, Any]:
        return {
            "Action": "GetWsChGeneral",
            "Version": "2020-06-29",
            "Format": "JSON",
            "AccessKeyId": self._access_key_id,
            "SignatureNonce": randint(10000, 99999),  # noqa: S311
            "SignatureMethod": "HMAC-SHA1",
            "SignatureVersion": "1.0",
            "Timestamp": datetime.now(timezone.utc).strftime(r"%Y-%m-%dT%H:%M:%SZ"),
            "ServiceCode": "alinlp",
            "Text": text,
            "TokenizerId": "GENERAL_CHN",
        }

    def _get_string_to_sign(self, body: dict[str, Any]) -> str:
        # 将 body 中的每个键值对按照键排序，然后构建 query string
        query_string = "&".join(f"{k}={v}" for k, v in sorted(body.items()))
        # 对 Query String 进行 URL Encode
        # 然后在前面添加 HTTP 请求方法，获得 string to sign
        string_to_sign = "POST&%2F&" + quote(query_string)

        # 修复错误的 Text 字段
        wrong_text = quote(body["Text"])
        right_text = wrong_text.replace("%", "%25")
        string_to_sign = string_to_sign.replace(wrong_text, right_text)
        # 修复错误的 Timestamp 字段
        wrong_timestamp = quote(":" + body["Timestamp"].split(":", maxsplit=1)[1])
        right_timestamp = wrong_timestamp.replace("%", "%25")
        string_to_sign = string_to_sign.replace(wrong_timestamp, right_timestamp)

        return string_to_sign  # noqa: RET504

    def _get_signature(self, string_to_sign: str) -> str:
        key = (self._access_key_secret + "&").encode("utf-8")
        message = string_to_sign.encode("utf-8")

        hmac_sha1_result = hmac_new(key, message, digestmod=sha1).digest()

        return b64encode(hmac_sha1_result).decode("utf-8")

    def _clean_splitted_words(self, words: tuple[str, ...]) -> tuple[str, ...]:
        # 去除所有单字
        return tuple(x for x in words if len(x) > 1)

    async def _get_chunk_result(self, chunk: str) -> tuple[str, ...]:
        data = self._get_data(chunk)
        string_to_sign = self._get_string_to_sign(data)
        signature = self._get_signature(string_to_sign)
        data["Signature"] = signature

        async with self._semaphore:
            response = await self._client.post(
                "https://alinlp.cn-hangzhou.aliyuncs.com", data=data
            )
        if not response.is_success:
            raise Exception(f"分词接口返回失败 - {response.json()['Message']}")

        data = json_decode(response.json()["Data"])
        if not data["success"]:
            raise Exception("分词接口返回失败")

        words = tuple(x["word"] for x in data["result"])
        return self._clean_splitted_words(words)

    async def split(self, text: str) -> tuple[str, ...]:
        text = self._clean_input_text(text)
        chunks = self._split_into_chunks(text)

        tasks = [self._get_chunk_result(chunk) for chunk in chunks]
        task_results = await gather(*tasks)

        return tuple(chain.from_iterable(task_results))
