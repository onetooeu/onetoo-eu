export interface Env {
  TRUST_ROOT_BASE: string;
  SEARCH_NOT_READY_MESSAGE: string;
  CORS_ALLOW_ORIGIN: string;
  // MAINTAINER_HEADER?: string;
}

type Json = Record<string, unknown>;

const JSON_HEADERS = {
  "content-type": "application/json; charset=utf-8",
  "cache-control": "no-store",
  "x-content-type-options": "nosniff",
};

const TEXT_HEADERS = {
  "content-type": "text/plain; charset=utf-8",
  "cache-control": "no-store",
  "x-content-type-options": "nosniff",
};

function corsHeaders(env: Env) {
  return {
    "access-control-allow-origin": env.CORS_ALLOW_ORIGIN || "*",
    "access-control-allow-methods": "GET, OPTIONS",
    "access-control-allow-headers": "content-type",
  };
}

function json(env: Env, status: number, body: Json): Response {
  return new Response(JSON.stringify(body, null, 2) + "\n", {
    status,
    headers: { ...JSON_HEADERS, ...corsHeaders(env) },
  });
}

function text(env: Env, status: number, body: string): Response {
  return new Response(body.endsWith("\n") ? body : body + "\n", {
    status,
    headers: { ...TEXT_HEADERS, ...corsHeaders(env) },
  });
}

function normalizeBase(url: string): string {
  if (!url) return "";
  return url.endsWith("/") ? url.slice(0, -1) : url;
}

function buildOpenApi(env: Env): Json {
  return {
    openapi: "3.0.3",
    info: {
      title: "ONETOO Universal Backend",
      version: "1.0.0",
      description:
        "Universal backend runtime for ONETOO. Provides non-404 endpoints for search.onetoo.eu and trust-root helpers.",
    },
    servers: [{ url: "https://search.onetoo.eu" }],
    paths: {
      "/": {
        get: {
          summary: "Info",
          responses: { "200": { description: "OK" } },
        },
      },
      "/health": {
        get: {
          summary: "Healthcheck",
          responses: { "200": { description: "OK" } },
        },
      },
      "/openapi.json": {
        get: {
          summary: "OpenAPI spec",
          responses: { "200": { description: "JSON spec" } },
        },
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
        get: {
          summary: "Proxy deploy.txt",
          responses: { "200": { description: "deploy.txt" } },
        },
      },
      "/trust/v1/sha256": {
        get: {
          summary: "Proxy sha256.json",
          responses: { "200": { description: "sha256.json" } },
        },
      },
    },
  };
}

async function proxyTrust(env: Env, path: string, accept: string): Promise<Response> {
  const base = normalizeBase(env.TRUST_ROOT_BASE || "https://www.onetoo.eu");
  const target = base + path;

  const resp = await fetch(target, {
    method: "GET",
    headers: { accept },
    cf: { cacheTtl: 0, cacheEverything: false },
  });

  // Pass through status + content-type, but enforce no-store + CORS.
  const ct = resp.headers.get("content-type") || (accept.includes("json") ? "application/json" : "text/plain");
  const headers = new Headers(resp.headers);

  headers.set("content-type", ct);
  headers.set("cache-control", "no-store");
  headers.set("x-content-type-options", "nosniff");
  headers.set("access-control-allow-origin", env.CORS_ALLOW_ORIGIN || "*");
  headers.set("access-control-allow-methods", "GET, OPTIONS");
  headers.set("access-control-allow-headers", "content-type");

  return new Response(resp.body, { status: resp.status, headers });
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const pathname = url.pathname;

    // CORS preflight (minimal)
    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: {
          ...corsHeaders(env),
          "cache-control": "no-store",
          "x-content-type-options": "nosniff",
        },
      });
    }

    if (request.method !== "GET") {
      return json(env, 405, {
        ok: false,
        error: "method_not_allowed",
        allowed: ["GET", "OPTIONS"],
      });
    }

    if (pathname === "/" || pathname === "") {
      return json(env, 200, {
        ok: true,
        service: "onetoo-universal",
        hint: "Try /health or /openapi.json",
      });
    }

    if (pathname === "/health") {
      return json(env, 200, { ok: true, status: "ok" });
    }

    if (pathname === "/openapi.json") {
      return json(env, 200, buildOpenApi(env));
    }

    if (pathname === "/search/v1") {
      const q = url.searchParams.get("q") || "";
      return json(env, 501, {
        ok: false,
        implemented: false,
        error: "not_implemented",
        message:
          env.SEARCH_NOT_READY_MESSAGE ||
          "search.onetoo.eu runtime is deployed, but search index is not enabled yet.",
        query: q,
        results: [],
      });
    }

    if (pathname === "/trust/v1/deploy") {
      return proxyTrust(env, "/.well-known/deploy.txt", "text/plain");
    }

    if (pathname === "/trust/v1/sha256") {
      return proxyTrust(env, "/.well-known/sha256.json", "application/json");
    }

    // Stable 404 (ours, not Cloudflare default)
    return json(env, 404, {
      ok: false,
      error: "not_found",
      path: pathname,
      hint: "Try /openapi.json",
    });
  },
};
