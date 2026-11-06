# langchain-brewpage

LangChain tools that publish HTML, Markdown, JSON, key-value stores and files to [BrewPage](https://brewpage.app) and return a shareable URL. Free, no account, no API key.

[![PyPI](https://img.shields.io/pypi/v/langchain-brewpage)](https://pypi.org/project/langchain-brewpage/)
[![License](https://img.shields.io/pypi/l/langchain-brewpage)](LICENSE)
[![CI](https://github.com/kochetkov-ma/langchain-brewpage/actions/workflows/ci.yml/badge.svg)](https://github.com/kochetkov-ma/langchain-brewpage/actions/workflows/ci.yml)

## Install

```bash
pip install langchain-brewpage
```

## Usage

```python
from langchain_brewpage import BrewPageToolkit

tools = BrewPageToolkit().get_tools()
page = tools[0].invoke({"content": "# Weekly report\n\nAll green.", "format": "markdown"})
print(page["url"])
```

With an agent (any tool-calling chat model):

```python
from langchain.agents import create_agent
from langchain_brewpage import BrewPageToolkit

agent = create_agent(model, tools=BrewPageToolkit().get_tools())
agent.invoke({"messages": [{"role": "user", "content": "Write a one-page HTML changelog and publish it."}]})
```

## Tools

| Tool | API | Result |
|---|---|---|
| `brewpage_publish_page` (`BrewPagePublishPageTool`) | `POST /api/html` | HTML or Markdown page URL |
| `brewpage_publish_json` (`BrewPagePublishJsonTool`) | `POST /api/json` | JSON document URL |
| `brewpage_create_kv_store` (`BrewPageCreateKvStoreTool`) | `POST /api/kv` | Key-value store URL, one initial key |
| `brewpage_upload_file` (`BrewPageUploadFileTool`) | `POST /api/files` | Download or page URL for a local file |

`BrewPageToolkit` returns all four with one shared client. Every tool also takes `ttl_days`, `password` and `namespace` and returns a dict with `url`, `id`, `namespace`, `owner_token`, `management_link`, `expires_at`. API errors (rate limits, refused content) reach the agent as tool messages, not exceptions.

The first call gets an owner token; the toolkit reuses it, so all publications share one owner. To keep it across runs, pass it in:

```python
from langchain_brewpage import BrewPageClient, BrewPageToolkit

toolkit = BrewPageToolkit(client=BrewPageClient(owner_token="..."))
```

Environment: `BREWPAGE_OWNER_TOKEN`, `BREWPAGE_NAMESPACE`, `BREWPAGE_BASE_URL` (default `https://brewpage.app`).

## Limits

- Hosting is temporary: publications expire after 15 days by default, `ttl_days` 1-30.
- Without `namespace` a publication is private: unlisted and not indexed, but anyone with the link can open it. Add `password` to restrict reads.
- `namespace="public"` lists pages in the public gallery and search engines. Never put secrets or personal data there.
- Size caps: HTML 5 MB, JSON 1 MB, KV value 1 MB, file 5 MB (video 20 MB). Current values: [brewpage.app/api/limits](https://brewpage.app/api/limits).

## Related

- [BrewPage](https://brewpage.app) and its [API](https://brewpage.app/api)
- [API reference](https://kochetkov-ma.github.io/brewpage-openapi/)
- [llama-index-tools-brewpage](https://github.com/kochetkov-ma/llama-index-tools-brewpage): the same tools for LlamaIndex
- [brewpage-publish-plugins](https://github.com/kochetkov-ma/brewpage-publish-plugins): other integrations
- [brewpage-mcp](https://www.npmjs.com/package/brewpage-mcp): MCP server on npm

## Development

```bash
uv sync --group test
uv run pytest
BREWPAGE_LIVE=1 uv run pytest -m live   # publishes one private page on production
```

## Support

info@brewpage.app or [GitHub issues](https://github.com/kochetkov-ma/langchain-brewpage/issues).

## License

[MIT](LICENSE)
