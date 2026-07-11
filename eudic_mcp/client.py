#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eudic 生词本 OpenAPI 客户端。

官方文档：https://my.eudic.net/OpenAPI/doc_api_study
"""

from __future__ import annotations

import json
import os
from typing import Any

import requests

BASE_URL = "https://api.frdic.com/api/open/v1"
DEFAULT_LANGUAGE = "en"


class EudicError(Exception):
    """Eudic API 返回的非 2xx 响应。"""

    def __init__(self, message: str, status_code: int | None = None, response_body: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


def _headers(token: str) -> dict[str, str]:
    return {
        "User-Agent": "eudic-mcp/1.0",
        "Authorization": f"NIS {token}",
        "Content-Type": "application/json",
    }


def _token(token: str | None = None) -> str:
    if token:
        return token.strip()
    t = os.environ.get("EUDIC_API_TOKEN", "").strip()
    if not t:
        raise EudicError(
            "缺少 Eudic API Token。请设置环境变量 EUDIC_API_TOKEN，"
            "或在调用函数时传入 token 参数。"
        )
    return t


def _request(
    method: str,
    path: str,
    *,
    token: str | None = None,
    params: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    url = f"{BASE_URL}{path}"
    headers = _headers(_token(token))
    data = json.dumps(payload, ensure_ascii=False) if payload else None
    resp = requests.request(
        method, url, headers=headers, params=params, data=data, timeout=30
    )
    try:
        resp.raise_for_status()
    except requests.HTTPError as exc:
        body = None
        try:
            body = resp.json()
        except Exception:
            body = resp.text
        raise EudicError(str(exc), status_code=resp.status_code, response_body=body) from exc

    if resp.status_code == 204:
        return {"success": True}
    try:
        return resp.json()
    except Exception:
        return {"raw": resp.text}


# ---------------------------------------------------------------------------
# 生词本分组管理
# ---------------------------------------------------------------------------

def list_categories(language: str = DEFAULT_LANGUAGE, token: str | None = None) -> dict[str, Any]:
    """获取所有生词本分组。"""
    return _request("GET", "/studylist/category", token=token, params={"language": language})


def create_category(
    name: str, language: str = DEFAULT_LANGUAGE, token: str | None = None
) -> dict[str, Any]:
    """创建新的生词本分组，返回包含 id 的分组信息。"""
    return _request(
        "POST",
        "/studylist/category",
        token=token,
        payload={"language": language, "name": name},
    )


def rename_category(
    category_id: str | int,
    name: str,
    language: str = DEFAULT_LANGUAGE,
    token: str | None = None,
) -> dict[str, Any]:
    """重命名生词本分组。"""
    return _request(
        "PATCH",
        "/studylist/category",
        token=token,
        payload={"id": category_id, "language": language, "name": name},
    )


def delete_category(
    category_id: str | int,
    name: str,
    language: str = DEFAULT_LANGUAGE,
    token: str | None = None,
) -> dict[str, Any]:
    """删除生词本分组。"""
    return _request(
        "DELETE",
        "/studylist/category",
        token=token,
        payload={"id": category_id, "language": language, "name": name},
    )


# ---------------------------------------------------------------------------
# 单词操作
# ---------------------------------------------------------------------------

def list_words(
    category_id: str | int = 0,
    language: str = DEFAULT_LANGUAGE,
    page: int = 0,
    page_size: int = 100,
    token: str | None = None,
) -> dict[str, Any]:
    """获取指定生词本中的单词列表。"""
    return _request(
        "GET",
        "/studylist/words",
        token=token,
        params={
            "language": language,
            "category_id": category_id,
            "page": page,
            "page_size": page_size,
        },
    )


def add_word(
    word: str,
    category_ids: list[str | int] | None = None,
    star: int = 2,
    context_line: str | None = None,
    language: str = DEFAULT_LANGUAGE,
    token: str | None = None,
) -> dict[str, Any]:
    """添加单个单词到生词本。"""
    payload: dict[str, Any] = {
        "language": language,
        "word": word,
        "star": star,
    }
    if category_ids is not None:
        payload["category_ids"] = category_ids
    if context_line is not None:
        payload["context_line"] = context_line
    return _request("POST", "/studylist/word", token=token, payload=payload)


def add_words_bulk(
    words: list[str],
    category_id: str | int = 0,
    language: str = DEFAULT_LANGUAGE,
    token: str | None = None,
) -> dict[str, Any]:
    """批量导入单词到指定生词本（重复单词不会重复添加）。"""
    return _request(
        "POST",
        "/studylist/words",
        token=token,
        payload={
            "language": language,
            "category_id": category_id,
            "words": words,
        },
    )


def delete_words(
    words: list[str],
    category_id: str | int = 0,
    language: str = DEFAULT_LANGUAGE,
    token: str | None = None,
) -> dict[str, Any]:
    """从指定生词本中删除单词。"""
    return _request(
        "DELETE",
        "/studylist/words",
        token=token,
        payload={
            "language": language,
            "category_id": category_id,
            "words": words,
        },
    )


def get_word(
    word: str, language: str = DEFAULT_LANGUAGE, token: str | None = None
) -> dict[str, Any]:
    """查询某个单词是否已在生词本中。"""
    return _request(
        "GET",
        "/studylist/word",
        token=token,
        params={"language": language, "word": word},
    )


def list_mastered_words(
    language: str = DEFAULT_LANGUAGE,
    category_id: str | int | None = None,
    page: int = 0,
    page_size: int = 100,
    token: str | None = None,
) -> dict[str, Any]:
    """查询已掌握单词列表。"""
    params: dict[str, Any] = {
        "language": language,
        "page": page,
        "page_size": page_size,
    }
    if category_id is not None:
        params["category_id"] = category_id
    return _request("GET", "/studylist/mastered_words", token=token, params=params)


# ---------------------------------------------------------------------------
# 笔记（note）管理
# ---------------------------------------------------------------------------


def list_notes(
    language: str = DEFAULT_LANGUAGE,
    page: int = 0,
    page_size: int = 100,
    token: str | None = None,
) -> dict[str, Any]:
    """获取所有单词笔记列表。"""
    return _request(
        "GET",
        "/studylist/notes",
        token=token,
        params={
            "language": language,
            "page": page,
            "page_size": page_size,
        },
    )


def get_note(
    word: str, language: str = DEFAULT_LANGUAGE, token: str | None = None
) -> dict[str, Any]:
    """获取某个单词的笔记。"""
    return _request(
        "GET",
        "/studylist/note",
        token=token,
        params={"language": language, "word": word},
    )


def add_note(
    word: str,
    note: str,
    language: str = DEFAULT_LANGUAGE,
    token: str | None = None,
) -> dict[str, Any]:
    """为某个单词添加或更新笔记。"""
    return _request(
        "POST",
        "/studylist/note",
        token=token,
        payload={"language": language, "word": word, "note": note},
    )


def delete_note(
    word: str, language: str = DEFAULT_LANGUAGE, token: str | None = None
) -> dict[str, Any]:
    """删除某个单词的笔记。"""
    return _request(
        "DELETE",
        "/studylist/note",
        token=token,
        payload={"language": language, "word": word},
    )


# ---------------------------------------------------------------------------
# 例句（sentence）管理
# ---------------------------------------------------------------------------


def list_sentences(
    language: str = DEFAULT_LANGUAGE,
    page: int = 0,
    page_size: int = 100,
    token: str | None = None,
) -> dict[str, Any]:
    """获取用户例句列表。"""
    return _request(
        "GET",
        "/studylist/sentences",
        token=token,
        params={
            "language": language,
            "page": page,
            "page_size": page_size,
        },
    )
