# Eudic MCP Server

欧路词典（Eudic）生词本 API 的 [Model Context Protocol](https://modelcontextprotocol.io/) 封装。

支持 Claude Desktop、Cursor 等兼容 MCP 的客户端直接管理 Eudic 生词本分组与单词。

## 功能

- 列出/创建/重命名/删除生词本分组
- 列出/添加/删除生词本中的单词
- 批量导入单词
- 查询已掌握单词

## 安装

```bash
pip install eudic-mcp
```

或从源码安装：

```bash
git clone https://github.com/YOUR_USERNAME/eudic-mcp.git
cd eudic-mcp
pip install -e .
```

## 配置

需要欧路词典 OpenAPI Token。获取方式见 [Eudic OpenAPI 文档](https://my.eudic.net/OpenAPI/doc_api_study)。

设置环境变量：

```bash
export EUDIC_API_TOKEN="NIS xxxx"
```

Windows PowerShell：

```powershell
$env:EUDIC_API_TOKEN="NIS xxxx"
```

## 在 Claude Desktop 中使用

编辑 `claude_desktop_config.json`：

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "eudic": {
      "command": "eudic-mcp",
      "env": {
        "EUDIC_API_TOKEN": "NIS xxxx"
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

## 作为 Python 库使用

```python
from eudic_mcp import create_category, add_words_bulk

cat = create_category("wfd")
cat_id = cat["data"]["id"]

add_words_bulk(["hypothesis", "methodology"], category_id=cat_id)
```

## 依赖

- Python >= 3.10
- `mcp>=1.0.0`
- `requests>=2.28.0`

## License

MIT
