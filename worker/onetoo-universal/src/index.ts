/**
 * ONETOO Universal Backend Worker
 * - makes search.onetoo.eu non-404
 * - provides stable contracts for AI agents
 *
 * Endpoints:
 *   GET  /health
 *   GET  /openapi.json
 *   GET  /search/v1?q=...
 *   GET  /trust/v1/deploy
 *   GET  /trust/v1/sha256
 *
 * Design notes:
 * - Deterministic outputs
 * - No external dependencies
 * - Safe defaults (no secrets required)
 */

export interface Env {
  TRUST_ROOT_BASE: string;
  SEARCH_NOT_READY_MESSAGE: string;
  CORS_ALLOW_ORIGIN: string;
  // MAINTAINER_HEADER?: string;
}

function json(data: unknown, status = 200, env?: Env): Response {
  const headers = new Headers({
    "content-type": "application/json; charset=utf-8",
    "x-content-type-options": "nosniff",
    "cache-control": "no-store",
  });

  // Minimal CORS (GET-only use cases)
  const origin = env?.CORS_ALLOW_ORIGIN ?? "*";
  headers.set("access-control-allow-origin", origin);
  headers.set("access-control-allow-methods", "GET, OPTIONS");
  headers.set("access-control-allow-headers", "content-type");

  return new Response(JSON.stringify(data, null, 2) + "\n", { status, headers });
}

function text(body: string, status = 200, env?: Env): Response {
  const headers = new Headers({
    "content-type": "text/plain; charset=utf-8",
    "x-content-type-options": "nosniff",
    "cache-control": "no-store",
  });

  const origin = env?.CORS_ALLOW_ORIGIN ?? "*";
  headers.set("access-control-allow-origin", origin);
  headers.set("access-control-allow-methods", "GET, OPTIONS");
  headers.set("access-control-allow-headers", "content-type");

  return new Response(body, { status, headers });
}

function notFound(env?: Env): Response {
  return json(
    {
      ok: false,
      error: "not_found",
      message: "Unknown endpoint.",
      hint: "Try /health or /openapi.json",
    },
    404,
    env
  );
}

async function proxyWellKnown(path: string, env: Env): Promise<Response> {
  // Strictly proxy only these two stable artifacts (reduces attack surface).
  const allow = new Set(["/\.well-known/deploy.txt", "/\.well-known/sha256.json"]);
  const key = path.startsWith("/") ? path : `/${path}`;
  if (!allow.has(key)) {
    return json(
      { ok: false, error: "forbidden", message: "Only deploy.txt and sha256.json are proxy-allowed." },
      403,
      env
    );
  }

  const url = new URL(env.TRUST_ROOT_BASE);
  url.pathname = key;

  const res = await fetch(url.toString(), {
    method: "GET",
    headers: { "accept": "application/json,text/plain;q=0.9,*/*;q=0.1" },
  });

  // Pass through body but normalize caching for safety.
  const headers = new Headers(res.headers);
  headers.set("cache-control", "no-store");
  headers.set("x-content-type-options", "nosniff");
  headers.set("access-control-allow-origin", env.CORS_ALLOW_ORIGIN ?? "*");
  headers.set("access-control-allow-methods", "GET, OPTIONS");
  headers.set("access-control-allow-headers", "content-type");

  return new Response(res.body, { status: res.status, headers });
}

function openapi(env: Env): Response {
  const spec = {
    openapi: "3.0.3",
    info: {
      title: "ONETOO Universal Backend",
      version: "1.0.0",
      description:
        "Universal backend runtime for ONETOO. Provides non-404 endpoints for search.onetoo.eu and trust-root helpers.",
    },
    servers: [{ url: "https://search.onetoo.eu" }],
    paths: {
      "/health": {
        get: {
          summary: "Healthcheck",
          responses: { "200": { description: "OK" } },
        },
      },
      "/openapi.json": {
        get: { summary: "OpenAPI spec", responses: { "200": { description: "JSON spec" } } },
      },
      "/search/v1": {
        get: {
          summary: "Search (v1)",
          description:
            "Stable placeholder endpoint. Returns 501 until search index is enabled.",
          parameters: [
            { name: "q", in: "query", required: false, schema: { type: "string" } },
          ],
          responses: {
            "200": { description: "Search results" },
            "501": { description: "Not implemented (index not enabled)" },
          },
        },
      },
      "/trust/v1/deploy": {
        get: { summary: "Proxy deploy.txt", responses: { "200": { description: "deploy.txt" } } },
      },
      "/trust/v1/sha256": {
        get: { summary: "Proxy sha256.json", responses: { "200": { description: "sha256.json" } } },
      },
    },
  };

  return json(spec, 200, env);
}

function searchPlaceholder(req: Request, env: Env): Response {
  const u = new URL(req.url);
  const q = u.searchParams.get("q") ?? "";

  // Deterministic placeholder response so clients can integrate now.
  return json(
    {
      ok: false,
      implemented: false,
      error: "not_implemented",
      message: env.SEARCH_NOT_READY_MESSAGE || "Search index not enabled.",
      query: q,
      results: [],
    },
    501,
    env
  );
}

export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    if (req.method === "OPTIONS") {
      // Simple CORS preflight
      return new Response(null, {
        status: 204,
        headers: {
          "access-control-allow-origin": env.CORS_ALLOW_ORIGIN ?? "*",
          "access-control-allow-methods": "GET, OPTIONS",
          "access-control-allow-headers": "content-type",
          "cache-control": "no-store",
        },
      });
    }

    const url = new URL(req.url);
    const path = url.pathname;

    if (req.method !== "GET") {
      return json({ ok: false, error: "method_not_allowed" }, 405, env);
    }

    if (path === "/" ) {
      return json(
        {
          ok: true,
          service: "onetoo-universal",
          hint: "Try /health or /openapi.json",
        },
        200,
        env
      );
    }

    if (path === "/health") {
      return json({ ok: true, status: "ok" }, 200, env);
    }

    if (path === "/openapi.json") {
      return openapi(env);
    }

    if (path === "/search/v1") {
      return searchPlaceholder(req, env);
    }

    if (path === "/trust/v1/deploy") {
      return proxyWellKnown("/.well-known/deploy.txt", env);
    }

    if (path === "/trust/v1/sha256") {
      return proxyWellKnown("/.well-known/sha256.json", env);
    }

    return notFound(env);
  },
};
