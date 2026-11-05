# langchain-brewpage

LangChain tools for [BrewPage](https://brewpage.app): let an agent publish an HTML page, a Markdown document, a JSON document, a key-value store or a file and get back a shareable URL. No account and no API key are needed.

Each call returns the URL plus an owner token. The toolkit reuses that token for later publications, so everything the agent creates belongs to one owner. Publications are private and unlisted by default and expire after 15 days unless you set `ttl_days` (1-30).

## Install

```bash
pip install langchain-brewpage
```

## Tools

| Tool | API | Use |
|---|---|---|
| `BrewPagePublishPageTool` (`brewpage_publish_page`) | `POST /api/html` | HTML or Markdown page -> URL |
| `BrewPagePublishJsonTool` (`brewpage_publish_json`) | `POST /api/json` | JSON document -> URL |
| `BrewPageCreateKvStoreTool` (`brewpage_create_kv_store`) | `POST /api/kv` | Key-value store with one initial key -> URL |
| `BrewPageUploadFileTool` (`brewpage_upload_file`) | `POST /api/files` | Local file -> download or page URL |

`BrewPageToolkit` returns all four tools, sharing one client.

Every tool also accepts `ttl_days`, `password` and `namespace`. Leave `namespace` empty for a private link. `public` lists pages in the public gallery and search engines, so never put secrets or personal data there.

## Usage

```python
from langchain_brewpage import BrewPageToolkit

tools = BrewPageToolkit().get_tools()
page = tools[0].invoke({"content": "# Weekly report\n\nAll green.", "format": "markdown"})
print(page["url"], page["owner_token"])
```

With an agent:

```python
from langchain.agents import create_agent
from langchain_brewpage import BrewPageToolkit

agent = create_agent(model, tools=BrewPageToolkit().get_tools())  # any tool-calling chat model
agent.invoke({"messages": [{"role": "user", "content": "Write a one-page HTML changelog and publish it."}]})
```

The result of each tool is a dict: `url`, `id`, `namespace`, `owner_token`, `management_link`, `expires_at`.

## Configuration

| Setting | Constructor | Environment |
|---|---|---|
| API base URL | `BrewPageClient(base_url=...)` | `BREWPAGE_BASE_URL` (default `https://brewpage.app`) |
| Owner token to reuse | `BrewPageClient(owner_token=...)` | `BREWPAGE_OWNER_TOKEN` |
| Default namespace | `BrewPageClient(namespace=...)` | `BREWPAGE_NAMESPACE` |

```python
from langchain_brewpage import BrewPageClient, BrewPageToolkit

toolkit = BrewPageToolkit(client=BrewPageClient(owner_token="..."))
```

API errors (rate limits, refused content) come back to the agent as tool messages instead of exceptions.

## Links

- API reference: https://kochetkov-ma.github.io/brewpage-openapi/
- OpenAPI contract: https://github.com/kochetkov-ma/brewpage-openapi
- Limits and terms: https://brewpage.app

## Development

```bash
uv sync --group test
uv run pytest
BREWPAGE_LIVE=1 uv run pytest -m live   # one private page on production
```

## License

MIT
