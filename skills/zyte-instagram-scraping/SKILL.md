---
name: zyte-instagram-scraping
description: Use when needing to extract data from Instagram (profiles, posts, comments) using Zyte API to bypass blocks.
---

# Zyte Instagram Scraping

## Overview
Scraping Instagram is challenging due to aggressive anti-bot measures. Zyte API provides high-quality proxies and browser rendering to bypass these blocks. This skill covers how to use Zyte to fetch Instagram data reliably.

## When to Use
- Standard Playwright/Selenium scrapers are getting blocked.
- Instagram session cookies expire too quickly.
- Need to scale collection across many profiles without IP bans.
- Encountering "useragent mismatch" or login redirects.

## Core Patterns

### 1. JSON API Access (Bypassing Headers)
When calling Instagram's internal API (`/api/v1/...`), you must sync `X-IG-App-ID` with a matching `User-Agent`. Zyte API requires these in `customHttpRequestHeaders`.

```python
payload = {
    "url": "https://www.instagram.com/api/v1/users/web_profile_info/?username=target",
    "httpResponseBody": True,
    "customHttpRequestHeaders": [
        {"name": "X-IG-App-ID", "value": "936619743392459"},
        {"name": "User-Agent", "value": "Mozilla/5.0 ..."}
    ]
}
```

### 2. Browser Rendering (Parsing DOM)
If JSON API is blocked, use `browserHtml` and parse the window state.

```python
payload = {
    "url": "https://www.instagram.com/target/",
    "browserHtml": True,
    "javascript": True
}
```

### 3. Proxy Mode (Smart Proxy Manager)
Para bibliotecas síncronas como `requests`, o Zyte pode ser usado como um proxy HTTP padrão. **Nota:** O Zyte API está substituindo este modo, mas ele ainda é útil para integrações legadas.

```python
import requests

proxy_host = "proxy.zyte.com"
proxy_port = "8011"
proxy_auth = "<ZYTE_API_KEY>:" # Importante incluir o ':' no final
proxies = {
    "https": f"http://{proxy_auth}@{proxy_host}:{proxy_port}/",
    "http": f"http://{proxy_auth}@{proxy_host}:{proxy_port}/"
}

response = requests.get("https://www.instagram.com/target/", proxies=proxies)
```

## Implementation Steps
1. **Sync Headers**: Ensure `User-Agent` and `X-IG-App-ID` are consistent.
2. **Session Cookies**: If possible, pass `Cookie` header with a valid `sessionid` in `customHttpRequestHeaders`.
3. **Retry Strategy**: Use Zyte's built-in retries and fallback to `browserHtml` if `httpResponseBody` fails.

## Common Mistakes
- **UA Mismatch**: Sending an `X-IG-App-ID` without a matching `User-Agent` header.
- **Datacenter IPs**: Instagram blocks many Zyte IPs. Ensure you are using residential proxies if the plan allows.
- **Login Redirects**: Happens when no cookies are provided. Always try to inject a valid session cookie.

## Verification
- Test with a public profile (e.g., `cironogueira`).
- Confirm that the response is valid JSON and contains the `data.user` object.
