#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eudic MCP Server

通过 Model Context Protocol 暴露欧路词典生词本 API。
支持 stdio 传输，可被 Claude Desktop、Cursor 等 MCP 客户端调用。
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .client import (
    EudicError,
    add_word,
    add_words_bulk,
    create_category,
    delete_category,
    delete_words,
    get_word,
    list_categories,
    list_mastered_words,
    list_words,
    rename_category,
)

server = Server("eudic-mcp")


TOOLS: list[Tool] = [
    Tool(
        name="eudic_list_categories",
        description="获取所有生词本分组（category）列表。",
        inputSchema={
            "type": "object",
            "properties": {
                "language": {
                    "type": "string",
                    "description": "语言代码，例如 en/fr/de/es，默认 en",
                    "default": "en",
                }
            },
        },
    ),
    Tool(
        name="eudic_create_category",
        description="创建新的生词本分组。",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "新分组名称，例如 wfd",
                },
                "language": {
                    "type": "string",
                    "description": "语言代码，默认 en",
                    "default": "en",
                },
            },
            "required": ["name"],
        },
    ),
    Tool(
        name="eudic_rename_category",
        description="重命名生词本分组。",
        inputSchema={
            "type": "object",
            "properties": {
                "category_id": {
                    "type": ["string", "integer"],
                    "description": "分组 id",
                },
                "name": {"type": "string", "description": "新名称"},
                "language": {"type": "string", "default": "en"},
            },
            "required": ["category_id", "name"],
        },
    ),
    Tool(
        name="eudic_delete_category",
        description="删除生词本分组。",
        inputSchema={
            "type": "object",
            "properties": {
                "category_id": {
                    "type": ["string", "integer"],
                    "description": "分组 id",
                },
                "name": {"type": "string", "description": "分组名称"},
                "language": {"type": "string", "default": "en"},
            },
            "required": ["category_id", "name"],
        },
    ),
    Tool(
        name="eudic_list_words",
        description="获取指定生词本中的单词列表。",
        inputSchema={
            "type": "object",
            "properties": {
                "category_id": {
                    "type": ["string", "integer"],
                    "description": "分组 id，默认 0（默认生词本）",
                    "default": 0,
                },
                "language": {"type": "string", "default": "en"},
                "page": {"type": "integer", "default": 0},
                "page_size": {"type": "integer", "default": 100},
            },
        },
    ),
    Tool(
        name="eudic_add_word",
        description="添加单个单词到生词本。",
        inputSchema={
            "type": "object",
            "properties": {
                "word": {"type": "string", "description": "要添加的单词"},
                "category_ids": {
                    "type": "array",
                    "items": {"type": ["string", "integer"]},
                    "description": "分组 id 列表，为空则进入默认分组",
                },
                "star": {"type": "integer", "default": 2, "description": "星级 1-5"},
                "context_line": {
                    "type": ["string", "null"],
                    "description": "单词所在语境例句",
                },
                "language": {"type": "string", "default": "en"},
            },
            "required": ["word"],
        },
    ),
    Tool(
        name="eudic_add_words_bulk",
        description="批量导入单词到指定生词本（已存在不会重复添加）。",
        inputSchema={
            "type": "object",
            "properties": {
                "words": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "单词列表",
                },
                "category_id": {
                    "type": ["string", "integer"],
                    "description": "目标分组 id",
                    "default": 0,
                },
                "language": {"type": "string", "default": "en"},
            },
            "required": ["words"],
        },
    ),
    Tool(
        name="eudic_delete_words",
        description="从指定生词本中删除单词。",
        inputSchema={
            "type": "object",
            "properties": {
                "words": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "要删除的单词列表",
                },
                "category_id": {
                    "type": ["string", "integer"],
                    "default": 0,
                },
                "language": {"type": "string", "default": "en"},
            },
            "required": ["words"],
        },
    ),
    Tool(
        name="eudic_get_word",
        description="查询某个单词是否已在生词本中。",
        inputSchema={
            "type": "object",
            "properties": {
                "word": {"type": "string"},
                "language": {"type": "string", "default": "en"},
            },
            "required": ["word"],
        },
    ),
    Tool(
        name="eudic_list_mastered_words",
        description="查询已掌握单词列表。",
        inputSchema={
            "type": "object",
            "properties": {
                "language": {"type": "string", "default": "en"},
                "category_id": {
                    "type": ["string", "integer", "null"],
                    "description": "可选：只返回该分组与已掌握列表的交集",
                },
                "page": {"type": "integer", "default": 0},
                "page_size": {"type": "integer", "default": 100},
            },
        },
    ),
]


@server.list_tools()
async def list_tools() -> list[Tool]:
    return TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    try:
        if name == "eudic_list_categories":
            result = list_categories(**arguments)
        elif name == "eudic_create_category":
            result = create_category(**arguments)
        elif name == "eudic_rename_category":
            result = rename_category(**arguments)
        elif name == "eudic_delete_category":
            result = delete_category(**arguments)
        elif name == "eudic_list_words":
            result = list_words(**arguments)
        elif name == "eudic_add_word":
            result = add_word(**arguments)
        elif name == "eudic_add_words_bulk":
            result = add_words_bulk(**arguments)
        elif name == "eudic_delete_words":
            result = delete_words(**arguments)
        elif name == "eudic_get_word":
            result = get_word(**arguments)
        elif name == "eudic_list_mastered_words":
            result = list_mastered_words(**arguments)
        else:
            return [TextContent(type="text", text=f"未知工具: {name}")]
    except EudicError as exc:
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {"error": str(exc), "status_code": exc.status_code, "body": exc.response_body},
                    ensure_ascii=False,
                ),
            )
        ]
    except Exception as exc:
        return [TextContent(type="text", text=json.dumps({"error": str(exc)}, ensure_ascii=False))]

    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
