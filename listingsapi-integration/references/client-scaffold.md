# Client scaffold

Two complete minimal clients, Python and TypeScript, plus the SDK equivalents. Each does five things: reads the key from the environment, sends `Authorization: API <key>`, pages by following `endCursor`, stays under the plan limit and retries 429s after `retry_after_seconds`, and surfaces errors including `correlation_id`. Copy one, run the read flow at the bottom, then extend.

Set the key first. Never write it into a file that is committed.

```bash
export LISTINGSAPI_KEY="paste-from-dashboard"
```

## Prefer the SDK when the language matches

| Language | Install | Client | Reads env var |
| --- | --- | --- | --- |
| Python 3.9+ | `pip install listingsapi` | `listingsapi.ListingsAPI()` | `LISTINGSAPI_KEY` |
| Node 18+ | `npm install listingsapi-js` | `new ListingsAPI()` | `LISTINGSAPI_KEY` |

Both retry 429 and 5xx twice by default honoring `Retry-After`, raise typed errors for error payloads inside 200 bodies, and encode numeric location ids for you. Both retry reads only; a write that fails is surfaced immediately, because the API has no idempotency key.

```python
import listingsapi

client = listingsapi.ListingsAPI()  # reads LISTINGSAPI_KEY

for loc in client.locations.list(first=50).auto_paging_iter():
    print(loc.databaseId, loc.name, loc.city)

reviews = client.reviews.list(1800289, first=20, rating_filters=[1, 2])
insights = client.analytics.google(1800289, from_date="2026-08-01", to_date="2026-08-31")
```

```ts
import { ListingsAPI, APIError, RateLimitError } from 'listingsapi-js';

const client = new ListingsAPI(); // reads LISTINGSAPI_KEY

const all = await client.fetchAllLocations({ fetchAll: true, pageSize: 100 });
for (const loc of all) console.log(loc.databaseId, loc.name, loc.city);

const insights = await client.fetchGoogleAnalytics(1800289, { fromDate: '2026-08-01', toDate: '2026-08-31' });
```

Use the raw client below when the language has no SDK, when the app already has an HTTP layer to reuse, or when you need control over the rate limiter across many workers.

## Python (standard library plus `requests`)

```python
"""listingsapi_client.py: minimal Listings API client.

Reads LISTINGSAPI_KEY from the environment. Pages cursor endpoints, stays
under the plan's per-minute limit, retries reads on 429/5xx, never retries
writes, and raises ListingsAPIError with the SY code and correlation_id.
"""
from __future__ import annotations

import base64
import json
import os
import random
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Iterator

import requests

BASE_URL = "https://listingsapi.com/api/v4"


class ListingsAPIError(Exception):
    def __init__(self, message: str, *, status: int, code: str | None,
                 errors: list[dict], correlation_id: str | None, body: Any):
        super().__init__(message)
        self.status = status
        self.code = code            # leading SYxxxxx code when present
        self.errors = errors
        self.correlation_id = correlation_id
        self.body = body


class RateLimitedError(ListingsAPIError):
    def __init__(self, retry_after: float, **kw):
        super().__init__(f"rate limited, retry after {retry_after}s", **kw)
        self.retry_after = retry_after


def location_gid(database_id: int | str) -> str:
    """Body parameters need the base64 Relay id; path parameters accept either."""
    s = str(database_id)
    return s if not s.isdigit() else base64.b64encode(f"Location:{s}".encode()).decode()


class MinuteLimiter:
    """Token bucket shared by every thread in the process. Size it under the plan:
    Launch is 10/min, Growth 50/min. Leave headroom for retries and other processes."""

    def __init__(self, per_minute: int):
        self.capacity = per_minute
        self.tokens = float(per_minute)
        self.refill_per_sec = per_minute / 60.0
        self.updated = time.monotonic()
        self.lock = threading.Lock()

    def acquire(self) -> None:
        while True:
            with self.lock:
                now = time.monotonic()
                self.tokens = min(self.capacity, self.tokens + (now - self.updated) * self.refill_per_sec)
                self.updated = now
                if self.tokens >= 1:
                    self.tokens -= 1
                    return
                wait = (1 - self.tokens) / self.refill_per_sec
            time.sleep(wait)


def _sy_code(message: str | None) -> str | None:
    if message and message[:2] == "SY" and message[2:7].isdigit():
        return message[:7]
    return None


def _collect_errors(body: Any) -> list[dict]:
    """Shape 1 (top level errors[]) and shape 2 (data.<op>.errors[])."""
    found: list[dict] = []
    if isinstance(body, dict):
        if isinstance(body.get("errors"), list):
            found.extend(e for e in body["errors"] if isinstance(e, dict))
        data = body.get("data")
        if isinstance(data, dict):
            for op in data.values():
                if isinstance(op, dict) and isinstance(op.get("errors"), list):
                    found.extend(e for e in op["errors"] if isinstance(e, dict))
    # de-duplicate: the gateway copies nested errors to the top level
    seen, unique = set(), []
    for e in found:
        key = json.dumps(e, sort_keys=True)
        if key not in seen:
            seen.add(key)
            unique.append(e)
    return unique


@dataclass
class ListingsAPI:
    api_key: str = field(default_factory=lambda: os.environ["LISTINGSAPI_KEY"])
    per_minute: int = 8              # Launch plan is 10; keep headroom
    max_read_retries: int = 4
    timeout: float = 30.0
    limiter: MinuteLimiter = field(init=False)
    session: requests.Session = field(init=False)

    def __post_init__(self):
        self.limiter = MinuteLimiter(self.per_minute)
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"API {self.api_key}",
            "Accept": "application/json",
        })

    # ---- transport -----------------------------------------------------

    def request(self, method: str, path: str, *, params: dict | None = None,
                body: dict | None = None) -> dict:
        is_read = method.upper() == "GET"
        attempts = self.max_read_retries if is_read else 1   # writes: one attempt, no idempotency key
        for attempt in range(attempts):
            self.limiter.acquire()
            resp = self.session.request(method, f"{BASE_URL}{path}", params=params,
                                        json=body, timeout=self.timeout)
            try:
                payload = resp.json()
            except ValueError:
                payload = {"raw": resp.text}

            if resp.status_code == 429:
                err = payload.get("error", {}) if isinstance(payload, dict) else {}
                wait = err.get("retry_after_seconds") or resp.headers.get("Retry-After")
                wait = float(wait) if wait else min(2 ** attempt, 30) + random.random()
                if attempt + 1 < attempts:
                    time.sleep(wait)
                    continue
                raise RateLimitedError(wait, status=429, code="RATE_LIMITED", errors=[],
                                       correlation_id=err.get("correlation_id"), body=payload)

            if resp.status_code >= 500 and is_read and attempt + 1 < attempts:
                time.sleep(min(2 ** attempt, 30) + random.random())
                continue

            return self._check(resp.status_code, payload)
        raise AssertionError("unreachable")

    def _check(self, status: int, payload: Any) -> dict:
        # Shape 3: gateway-level single error object (carries correlation_id).
        if isinstance(payload, dict) and isinstance(payload.get("error"), dict):
            e = payload["error"]
            raise ListingsAPIError(e.get("message", "gateway error"), status=status, code=e.get("code"),
                                   errors=[e], correlation_id=e.get("correlation_id"), body=payload)
        errors = _collect_errors(payload)
        if status >= 400 or errors:
            first = errors[0].get("message") if errors else f"HTTP {status}"
            raise ListingsAPIError(first, status=status, code=_sy_code(first), errors=errors,
                                   correlation_id=None, body=payload)
        return payload

    # ---- pagination ------------------------------------------------------

    def cursor_pages(self, path: str, data_key: str, *, params: dict | None = None,
                     page_size: int = 50) -> Iterator[dict]:
        """Yield nodes from a Relay-style endpoint, one page at a time, never in parallel."""
        after = None
        while True:
            q = dict(params or {}, first=page_size)
            if after:
                q["after"] = after
            conn = self.request("GET", path, params=q)["data"][data_key]
            edges = conn.get("edges") or []
            for edge in edges:
                yield edge["node"]
            info = conn.get("pageInfo") or {}
            if not edges or not info.get("hasNextPage") or not info.get("endCursor"):
                return
            after = info["endCursor"]

    def offset_pages(self, path: str, data_key: str, *, params: dict | None = None,
                     per_page: int = 20) -> Iterator[dict]:
        page = 1
        while True:
            q = dict(params or {}, page=page, perPage=per_page)
            conn = self.request("GET", path, params=q)["data"][data_key]
            for rec in conn.get("records") or []:
                yield rec
            if not (conn.get("pageInfo") or {}).get("hasNextPage"):
                return
            page += 1

    # ---- a few typed calls -------------------------------------------------

    def list_locations(self, page_size: int = 50) -> Iterator[dict]:
        return self.cursor_pages("/locations", "allLocations", page_size=page_size)

    def locations_by_store_codes(self, codes: list[str]) -> list[dict]:
        out = self.request("GET", "/locations-by-store-codes",
                           params={"storeCodes": json.dumps(codes)})
        return out["data"].get("getLocationsByStoreCodes") or []

    def create_location(self, input: dict) -> dict:
        """Raises on nested validation errors even though the status is 200."""
        return self.request("POST", "/locations", body={"input": input})["data"]["createLocation"]["location"]

    def reviews(self, location_id: int | str, page_size: int = 20, **filters) -> Iterator[dict]:
        params = {k: (json.dumps(v) if isinstance(v, (list, dict)) else v) for k, v in filters.items()}
        return self.cursor_pages(f"/locations/{location_id}/reviews", "interactions",
                                 params=params, page_size=page_size)

    def google_analytics(self, location_id: int | str, from_date: str, to_date: str) -> dict:
        out = self.request("GET", f"/locations/{location_id}/google-analytics",
                           params={"fromDate": from_date, "toDate": to_date})
        return out["data"].get("googleInsights") or {}


if __name__ == "__main__":
    # First read flow. Run this before adding anything else.
    api = ListingsAPI()
    try:
        for loc in api.list_locations():
            print(loc["databaseId"], loc["name"], loc.get("city"), loc.get("storeId"))
    except RateLimitedError as e:
        print("rate limited; retry after", e.retry_after, "correlation_id", e.correlation_id)
    except ListingsAPIError as e:
        print("failed:", e.status, e.code, e.errors, "correlation_id", e.correlation_id)
```

## TypeScript (Node 18+, no dependencies)

```ts
// listingsapi-client.ts: minimal Listings API client.
// Reads LISTINGSAPI_KEY from the environment. Pages cursor endpoints, stays
// under the plan's per-minute limit, retries reads on 429/5xx, never retries
// writes, and throws ListingsAPIError with the SY code and correlation_id.

const BASE_URL = 'https://listingsapi.com/api/v4';

export interface ApiErrorEntry { message?: string; code?: string; [k: string]: unknown }

export class ListingsAPIError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly code: string | null,       // leading SYxxxxx when present
    public readonly errors: ApiErrorEntry[],
    public readonly correlationId: string | null,
    public readonly body: unknown,
  ) { super(message); this.name = 'ListingsAPIError'; }
}

export class RateLimitedError extends ListingsAPIError {
  constructor(public readonly retryAfter: number, status: number, correlationId: string | null, body: unknown) {
    super(`rate limited, retry after ${retryAfter}s`, status, 'RATE_LIMITED', [], correlationId, body);
    this.name = 'RateLimitedError';
  }
}

/** Body parameters need the base64 Relay id; path parameters accept either form. */
export const locationGid = (id: number | string): string =>
  /^\d+$/.test(String(id)) ? Buffer.from(`Location:${id}`).toString('base64') : String(id);

/** Token bucket shared by everything in the process. Launch is 10/min, Growth 50/min; leave headroom. */
class MinuteLimiter {
  private tokens: number;
  private updated = Date.now();
  constructor(private readonly perMinute: number) { this.tokens = perMinute; }
  async acquire(): Promise<void> {
    for (;;) {
      const now = Date.now();
      this.tokens = Math.min(this.perMinute, this.tokens + ((now - this.updated) / 60000) * this.perMinute);
      this.updated = now;
      if (this.tokens >= 1) { this.tokens -= 1; return; }
      const waitMs = ((1 - this.tokens) / this.perMinute) * 60000;
      await new Promise((r) => setTimeout(r, waitMs));
    }
  }
}

const sleep = (s: number) => new Promise((r) => setTimeout(r, s * 1000));
const syCode = (m?: string) => (m && /^SY\d{5}/.test(m) ? m.slice(0, 7) : null);

/** Shape 1 (top level errors[]) plus shape 2 (data.<op>.errors[]), de-duplicated. */
function collectErrors(body: any): ApiErrorEntry[] {
  const out: ApiErrorEntry[] = [];
  if (body && typeof body === 'object') {
    if (Array.isArray(body.errors)) out.push(...body.errors);
    if (body.data && typeof body.data === 'object') {
      for (const op of Object.values<any>(body.data)) {
        if (op && Array.isArray(op.errors)) out.push(...op.errors);
      }
    }
  }
  const seen = new Set<string>();
  return out.filter((e) => { const k = JSON.stringify(e); if (seen.has(k)) return false; seen.add(k); return true; });
}

export interface ClientOptions { apiKey?: string; perMinute?: number; maxReadRetries?: number; timeoutMs?: number }

export class ListingsAPI {
  private readonly apiKey: string;
  private readonly limiter: MinuteLimiter;
  private readonly maxReadRetries: number;
  private readonly timeoutMs: number;

  constructor(opts: ClientOptions = {}) {
    const key = opts.apiKey ?? process.env.LISTINGSAPI_KEY;
    if (!key) throw new Error('LISTINGSAPI_KEY is not set');
    this.apiKey = key;
    this.limiter = new MinuteLimiter(opts.perMinute ?? 8);   // Launch plan is 10; keep headroom
    this.maxReadRetries = opts.maxReadRetries ?? 4;
    this.timeoutMs = opts.timeoutMs ?? 30_000;
  }

  // ---- transport ---------------------------------------------------------

  async request<T = any>(method: 'GET' | 'POST', path: string, opts: { params?: Record<string, string | number>; body?: unknown } = {}): Promise<T> {
    const isRead = method === 'GET';
    const attempts = isRead ? this.maxReadRetries : 1;      // writes: one attempt, no idempotency key
    const url = new URL(BASE_URL + path);
    for (const [k, v] of Object.entries(opts.params ?? {})) url.searchParams.set(k, String(v));

    for (let attempt = 0; attempt < attempts; attempt++) {
      await this.limiter.acquire();
      const res = await fetch(url, {
        method,
        headers: { Authorization: `API ${this.apiKey}`, Accept: 'application/json', ...(opts.body ? { 'Content-Type': 'application/json' } : {}) },
        body: opts.body ? JSON.stringify(opts.body) : undefined,
        signal: AbortSignal.timeout(this.timeoutMs),
      });
      const text = await res.text();
      let payload: any; try { payload = JSON.parse(text); } catch { payload = { raw: text }; }

      if (res.status === 429) {
        const err = payload?.error ?? {};
        const wait = Number(err.retry_after_seconds ?? res.headers.get('retry-after')) || Math.min(2 ** attempt, 30) + Math.random();
        if (attempt + 1 < attempts) { await sleep(wait); continue; }
        throw new RateLimitedError(wait, 429, err.correlation_id ?? null, payload);
      }
      if (res.status >= 500 && isRead && attempt + 1 < attempts) { await sleep(Math.min(2 ** attempt, 30) + Math.random()); continue; }
      return this.check(res.status, payload) as T;
    }
    throw new Error('unreachable');
  }

  private check(status: number, payload: any) {
    if (payload?.error && typeof payload.error === 'object') {       // shape 3: gateway error, has correlation_id
      const e = payload.error;
      throw new ListingsAPIError(e.message ?? 'gateway error', status, e.code ?? null, [e], e.correlation_id ?? null, payload);
    }
    const errors = collectErrors(payload);
    if (status >= 400 || errors.length) {
      const first = errors[0]?.message ?? `HTTP ${status}`;
      throw new ListingsAPIError(first, status, syCode(first), errors, null, payload);
    }
    return payload;
  }

  // ---- pagination -----------------------------------------------------------

  /** Yields nodes from a Relay-style endpoint, one page at a time, never in parallel. */
  async *cursorPages<T = any>(path: string, dataKey: string, params: Record<string, string | number> = {}, pageSize = 50): AsyncGenerator<T> {
    let after: string | undefined;
    for (;;) {
      const conn = (await this.request('GET', path, { params: { ...params, first: pageSize, ...(after ? { after } : {}) } })).data[dataKey];
      const edges: any[] = conn?.edges ?? [];
      for (const edge of edges) yield edge.node as T;
      const info = conn?.pageInfo ?? {};
      if (!edges.length || !info.hasNextPage || !info.endCursor) return;
      after = info.endCursor;
    }
  }

  async *offsetPages<T = any>(path: string, dataKey: string, params: Record<string, string | number> = {}, perPage = 20): AsyncGenerator<T> {
    for (let page = 1; ; page++) {
      const conn = (await this.request('GET', path, { params: { ...params, page, perPage } })).data[dataKey];
      for (const rec of conn?.records ?? []) yield rec as T;
      if (!conn?.pageInfo?.hasNextPage) return;
    }
  }

  // ---- a few typed calls -----------------------------------------------------

  listLocations(pageSize = 50) { return this.cursorPages('/locations', 'allLocations', {}, pageSize); }

  async locationsByStoreCodes(codes: string[]): Promise<any[]> {
    const out = await this.request('GET', '/locations-by-store-codes', { params: { storeCodes: JSON.stringify(codes) } });
    return out.data.getLocationsByStoreCodes ?? [];
  }

  /** Throws on nested validation errors even though the status is 200. */
  async createLocation(input: Record<string, unknown>) {
    const out = await this.request('POST', '/locations', { body: { input } });
    return out.data.createLocation.location;
  }

  reviews(locationId: number | string, filters: Record<string, unknown> = {}, pageSize = 20) {
    const params = Object.fromEntries(Object.entries(filters).map(([k, v]) => [k, typeof v === 'object' ? JSON.stringify(v) : String(v)]));
    return this.cursorPages(`/locations/${locationId}/reviews`, 'interactions', params, pageSize);
  }

  async googleAnalytics(locationId: number | string, fromDate: string, toDate: string) {
    const out = await this.request('GET', `/locations/${locationId}/google-analytics`, { params: { fromDate, toDate } });
    return out.data.googleInsights ?? {};
  }
}

// First read flow. Run this before adding anything else.
if (require.main === module) {
  (async () => {
    const api = new ListingsAPI();
    try {
      for await (const loc of api.listLocations()) console.log(loc.databaseId, loc.name, loc.city, loc.storeId);
    } catch (e) {
      if (e instanceof RateLimitedError) console.error('rate limited; retry after', e.retryAfter, 'correlation_id', e.correlationId);
      else if (e instanceof ListingsAPIError) console.error('failed:', e.status, e.code, e.errors, 'correlation_id', e.correlationId);
      else throw e;
    }
  })();
}
```

## Fitting it into an existing app

Keep the five responsibilities but swap the parts:

- Transport: replace `requests` or `fetch` with the app's HTTP client and its existing timeout, logging and tracing hooks.
- Config: read `LISTINGSAPI_KEY` from wherever the app already reads secrets. For per tenant keys, pass the key into the constructor per request and never cache a client across tenants.
- Limiter: if the app already has a shared rate limiter or a job queue with concurrency controls, use that. The bucket must be shared by every worker that talks to the same account; a per process bucket in a fleet of ten workers is ten times the plan.
- Errors: map `ListingsAPIError` onto the app's error type and make sure `code`, `errors` and `correlationId` reach the logs.
- Tests: record one real response for each shape (cursor page, offset page, plain array, nested validation failure, 429) and replay them. Do not hand write fixtures from memory.
