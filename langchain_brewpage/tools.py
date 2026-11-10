"""LangChain tools and toolkit for BrewPage publishing."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Literal, Optional, Type

from langchain_core.tools import BaseTool, BaseToolkit, ToolException
from pydantic import BaseModel, ConfigDict, Field

from langchain_brewpage.client import BrewPageClient, BrewPageError

_NS = ("Namespace: omit for a private unlisted link; 'public' lists pages in the public gallery and search. "
       "Never put secrets or personal data in 'public'.")
_TTL = "Lifetime in days (1-30); omit for the 15-day default."
_PASSWORD = "Optional password readers must enter."
_HANDOFF = (" Give the user 'url' and 'management_link' (private: anyone who has it can edit or delete the "
            "publication). Keep 'owner_token' for later updates; show it when asked. Never post either publicly.")


class _CommonInput(BaseModel):
    ttl_days: Optional[int] = Field(default=None, description=_TTL)
    password: Optional[str] = Field(default=None, description=_PASSWORD)
    namespace: Optional[str] = Field(default=None, description=_NS)


class PublishPageInput(_CommonInput):
    content: str = Field(description="HTML document or Markdown text to publish.")
    format: Literal["html", "markdown"] = Field(default="html", description="'html' or 'markdown'.")


class PublishJsonInput(_CommonInput):
    json_text: str = Field(description="A valid JSON document as text.")


class CreateKvStoreInput(_CommonInput):
    key: str = Field(description="Initial key name.")
    value: str = Field(description="Value for the initial key (max 1 MB).")


class UploadFileInput(_CommonInput):
    path: str = Field(description="Local path of the file to upload.")


class _BrewPageTool(BaseTool):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    client: BrewPageClient = Field(default_factory=BrewPageClient, exclude=True)
    handle_tool_error: bool = True

    def _call(self, method: str, **kwargs: Any) -> Dict[str, Any]:
        try:
            return getattr(self.client, method)(**kwargs)
        except (BrewPageError, OSError, ValueError) as error:
            raise ToolException(str(error)) from error


class BrewPagePublishPageTool(_BrewPageTool):
    name: str = "brewpage_publish_page"
    description: str = ("Publish an HTML page or Markdown document on brewpage.app and get a shareable URL. "
                        "No account needed." + _HANDOFF)
    args_schema: Type[BaseModel] = PublishPageInput

    def _run(self, content: str, format: str = "html", ttl_days: Optional[int] = None,
             password: Optional[str] = None, namespace: Optional[str] = None, **_: Any) -> Dict[str, Any]:
        return self._call("publish_page", content=content, format=format, ttl_days=ttl_days,
                          password=password, namespace=namespace)


class BrewPagePublishJsonTool(_BrewPageTool):
    name: str = "brewpage_publish_json"
    description: str = "Host a JSON document on brewpage.app and get a URL that serves it." + _HANDOFF
    args_schema: Type[BaseModel] = PublishJsonInput

    def _run(self, json_text: str, ttl_days: Optional[int] = None, password: Optional[str] = None,
             namespace: Optional[str] = None, **_: Any) -> Dict[str, Any]:
        try:
            data = json.loads(json_text)
        except ValueError as error:
            raise ToolException(f"json_text is not valid JSON: {error}") from error
        return self._call("publish_json", data=data, ttl_days=ttl_days, password=password, namespace=namespace)


class BrewPageCreateKvStoreTool(_BrewPageTool):
    name: str = "brewpage_create_kv_store"
    description: str = "Create a key-value store on brewpage.app with one initial key; returns its URL." + _HANDOFF
    args_schema: Type[BaseModel] = CreateKvStoreInput

    def _run(self, key: str, value: str, ttl_days: Optional[int] = None, password: Optional[str] = None,
             namespace: Optional[str] = None, **_: Any) -> Dict[str, Any]:
        return self._call("create_kv_store", key=key, value=value, ttl_days=ttl_days,
                          password=password, namespace=namespace)


class BrewPageUploadFileTool(_BrewPageTool):
    name: str = "brewpage_upload_file"
    description: str = ("Upload a local file (image, PDF, archive, document, HTML or Markdown) to brewpage.app "
                        "and get a download or page URL." + _HANDOFF)
    args_schema: Type[BaseModel] = UploadFileInput

    def _run(self, path: str, ttl_days: Optional[int] = None, password: Optional[str] = None,
             namespace: Optional[str] = None, **_: Any) -> Dict[str, Any]:
        return self._call("upload_file", path=path, ttl_days=ttl_days, password=password, namespace=namespace)


class BrewPageToolkit(BaseToolkit):
    """All BrewPage tools sharing one client, so every publication groups under one owner token."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    client: BrewPageClient = Field(default_factory=BrewPageClient)

    def get_tools(self) -> List[BaseTool]:
        return [
            BrewPagePublishPageTool(client=self.client),
            BrewPagePublishJsonTool(client=self.client),
            BrewPageCreateKvStoreTool(client=self.client),
            BrewPageUploadFileTool(client=self.client),
        ]
