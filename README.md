# Eudic MCP Server

欧路词典（Eudic）生词本 API 的 [Model Context Protocol](https://modelcontextprotocol.io/) 封装。

支持 Claude Desktop、Cursor、Kimi Code 等兼容 MCP 的客户端直接管理 Eudic 生词本分组与单词。

## 功能

- 列出/创建/重命名/删除生词本分组
- 列出/添加/删除生词本中的单词
- 批量导入单词
- 查询已掌握单词
- 管理单词笔记（增删改查）
- 获取用户例句列表

## 安装

### 从 PyPI 安装（暂未发布）

```bash
pip install eudic-mcp
```

### 从源码安装

```bash
git clone https://github.com/safeblood/eudic-mcp.git
cd eudic-mcp
pip install -e .
```

### 不安装，直接运行源码

如果你不想安装到系统 Python，可以设置 `PYTHONPATH` 指向项目目录：

```bash
export PYTHONPATH="/path/to/eudic-mcp"
python -m eudic_mcp.server
```

## 配置

需要欧路词典 OpenAPI Token。获取方式见 [Eudic OpenAPI 文档](https://my.eudic.net/OpenAPI/doc_api_study)。

**注意**：Token 只填 `NIS` 后面的字符串部分，不要带 `NIS ` 前缀。本客户端会自动拼上 `NIS `。

```bash
# 错误
export EUDIC_API_TOKEN="NIS xxxx"

# 正确
export EUDIC_API_TOKEN="xxxx"
```

Windows PowerShell：

```powershell
$env:EUDIC_API_TOKEN="xxxx"
```

## 在 Kimi Code 中使用

编辑 Kimi Code 的 MCP 配置文件：

- Windows: `C:\Users\<用户名>\.kimi-code\mcp.json`
- macOS/Linux: `~/.kimi-code/mcp.json`

添加或替换 `eudic` server：

```json
{
  "mcpServers": {
    "eudic": {
      "command": "python",
      "args": [
        "-m",
        "eudic_mcp.server"
      ],
      "env": {
        "PYTHONPATH": "C:/Users/83773/Downloads/pte/eudic-mcp",
        "EUDIC_API_TOKEN": "你的token"
      }
    }
  }
}
```

修改后**重启 Kimi Code** 生效。

## 在 Claude Desktop 中使用

编辑 `claude_desktop_config.json`：

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

### 已安装包

```json
{
  "mcpServers": {
    "eudic": {
      "command": "eudic-mcp",
      "env": {
        "EUDIC_API_TOKEN": "你的token"
      }
    }
  }
}
```

### 直接运行源码

```json
{
  "mcpServers": {
    "eudic": {
      "command": "python",
      "args": [
        "-m",
        "eudic_mcp.server"
      ],
      "env": {
        "PYTHONPATH": "C:/Users/83773/Downloads/pte/eudic-mcp",
        "EUDIC_API_TOKEN": "你的token"
      }
    }
  }
}
```

## 可用工具

| 工具名 | 说明 |
| --- | --- |
| `eudic_list_categories` | 列出所有生词本分组 |
| `eudic_create_category` | 创建分组 |
| `eudic_rename_category` | 重命名分组 |
| `eudic_delete_category` | 删除分组 |
| `eudic_list_words` | 列出分组单词 |
| `eudic_add_word` | 添加单个单词 |
| `eudic_add_words_bulk` | 批量导入单词 |
| `eudic_delete_words` | 批量删除单词 |
| `eudic_get_word` | 查询单个单词 |
| `eudic_list_mastered_words` | 查询已掌握单词 |
| `eudic_list_notes` | 获取所有单词笔记 |
| `eudic_get_note` | 获取某个单词的笔记 |
| `eudic_add_note` | 添加或更新单词笔记 |
| `eudic_delete_note` | 删除单词笔记 |
| `eudic_list_sentences` | 获取用户例句列表 |

## 工具调用示例

### 创建生词本分组

```json
{
  "name": "wfd",
  "language": "en"
}
```

返回示例：

```json
{
  "data": {
    "id": "132314173819830130",
    "language": "en",
    "name": "wfd"
  },
  "message": ""
}
```

### 批量导入单词

```json
{
  "words": ["hypothesis", "methodology", "empirical"],
  "category_id": "132314173819830130",
  "language": "en"
}
```

### 添加单个单词（带语境）

```json
{
  "word": "hypothesis",
  "category_ids": ["132314173819830130"],
  "star": 3,
  "context_line": "This hypothesis needs more evidence.",
  "language": "en"
}
```

### 列出分组单词

```json
{
  "category_id": "132314173819830130",
  "page": 0,
  "page_size": 100,
  "language": "en"
}
```

### 添加/更新单词笔记

```json
{
  "word": "hypothesis",
  "note": "假设；假说。注意与 assumption 区分。",
  "language": "en"
}
```

### 获取单词笔记

```json
{
  "word": "hypothesis",
  "language": "en"
}
```

### 删除单词笔记

```json
{
  "word": "hypothesis",
  "language": "en"
}
```

### 列出用户例句

```json
{
  "language": "en",
  "page": 0,
  "page_size": 100
}
```

## 作为 Python 库使用

```python
from eudic_mcp import create_category, add_words_bulk

cat = create_category("wfd")
cat_id = cat["data"]["id"]

add_words_bulk(["hypothesis", "methodology"], category_id=cat_id)
```

## 开发

```bash
cd eudic-mcp
pip install -e .

# 手动启动 server
EUDIC_API_TOKEN="你的token" eudic-mcp
```

## 依赖

- Python >= 3.10
- `mcp>=1.0.0`
- `requests>=2.28.0`

## License

MIT
