export async function onRequestGet(context) {
  const full = context.env.CF_PAGES_COMMIT_SHA || "";
  const short = full ? full.slice(0, 7) : "unknown";
  const ts = new Date().toISOString().replace(/\.\d+Z$/, "Z");

  const body =
`DEPLOY-MARKER ROOT
commit: ${short}
time: ${ts}
nonce: cf-pages-${short}-${ts}
`;

  return new Response(body, {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "no-store, max-age=0"
    }
  });
}
