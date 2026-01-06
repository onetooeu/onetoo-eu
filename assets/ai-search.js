/* ONETOO AI Search — thin UI client (TFWS-style)
 * Decade-stable: no framework, no build, no deps.
 */
(function () {
  // Primary recommended endpoint (Worker on subdomain)
  const API_BASE = "https://search.onetoo.eu";

  const form = document.getElementById("aiSearchForm");
  const input = document.getElementById("aiSearchQuery");
  const out = document.getElementById("aiSearchResults");
  const meta = document.getElementById("aiSearchMeta");

  if (!form || !input || !out || !meta) return;

  function esc(s){ return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }

  async function run(q) {
    out.innerHTML = "";
    meta.textContent = "Searching…";

    const url = API_BASE + "/search/v1?q=" + encodeURIComponent(q);
    let r;
    try {
      r = await fetch(url, { method: "GET", headers: { "Accept": "application/json" } });
    } catch (e) {
      meta.textContent = "Search failed (network).";
      return;
    }

    if (!r.ok) {
      meta.textContent = "Search API unavailable (" + r.status + ").";
      out.innerHTML = '<p class="muted">Try later. Trust entrypoints: <a href="/.well-known/ai-trust-hub.json">ai-trust-hub</a> · <a href="/.well-known/ai-search.json">ai-search</a></p>';
      return;
    }

    const data = await r.json();

    const results = Array.isArray(data.results) ? data.results : [];
    const took = data.took_ms != null ? (" · " + data.took_ms + "ms") : "";
    meta.textContent = "OK · " + results.length + " results" + took;

    const items = results.slice(0, 12).map(it => {
      const title = esc(it.title || it.url || "result");
      const url2 = esc(it.url || "#");
      const snippet = esc(it.snippet || "");
      return (
        '<div class="ai-result">' +
          '<div class="ai-title"><a href="' + url2 + '" rel="noopener noreferrer">' + title + '</a></div>' +
          (snippet ? '<div class="ai-snippet">' + snippet + '</div>' : '') +
        '</div>'
      );
    }).join("");

    out.innerHTML = items || "<p class=\"muted\">No results.</p>";

    // Optional: show proof pointer if present
    if (data.proof && typeof data.proof === "object") {
      const proofUrl = data.proof.url ? esc(data.proof.url) : "";
      if (proofUrl) {
        const p = document.createElement("p");
        p.className = "ai-proof muted";
        p.innerHTML = 'Proof: <a href="' + proofUrl + '">' + proofUrl + '</a>';
        out.appendChild(p);
      }
    }
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    const q = (input.value || "").trim();
    if (!q) return;
    run(q);
  });
})();
