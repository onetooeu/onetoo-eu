/* ONETOO.eu – Trust Hub runtime "defragmentation" layer.
 * Injects a consistent header/nav/footer across all static pages,
 * without rewriting hundreds of localized HTML files.
 */

function ocpDetectLocale(pathname) {
  // Locale folders are 2-letter ISO codes at the first segment.
  const seg = (pathname || "").split("/").filter(Boolean)[0] || "";
  if (/^[a-z]{2}$/i.test(seg)) return seg.toLowerCase();
  return "";
}

function ocpPrefix(pathname) {
  const loc = ocpDetectLocale(pathname);
  return loc ? `/${loc}` : "";
}

function el(tag, attrs = {}, children = []) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") n.className = v;
    else if (k === "html") n.innerHTML = v;
    else if (k.startsWith("on") && typeof v === "function") n.addEventListener(k.slice(2), v);
    else n.setAttribute(k, v);
  }
  for (const c of children) n.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
  return n;
}

function ensureSkipLink() {
  if (document.querySelector('.skip-link')) return;
  const skip = el('a', { class: 'skip-link', href: '#content' }, ['Skip to content']);
  document.body.prepend(skip);
}

function ensureMainId() {
  const main = document.querySelector('main') || document.querySelector('#main') || document.querySelector('.main');
  if (main) {
    if (!main.id) main.id = 'content';
    return;
  }
  // Wrap loose content into a <main> if needed
  const wrapper = el('main', { id: 'content' });
  const bodyChildren = Array.from(document.body.childNodes);
  for (const node of bodyChildren) {
    // Keep header/footer injected later at top/bottom, move everything else.
    if (node.nodeType === 1 && (node.matches('.site-header') || node.matches('.site-footer') || node.matches('.skip-link'))) continue;
    wrapper.appendChild(node);
  }
  document.body.appendChild(wrapper);
}

function injectHeaderFooter() {
  if (document.querySelector('.site-header')) return;

  const prefix = ocpPrefix(location.pathname);
  const baseLinks = [
    { href: `${prefix}/`, label: 'Home' },
    { href: `${prefix}/ai-trust-hub.html`, label: 'AI Trust' },
    { href: `${prefix}/verify.html`, label: 'Verify' },
    { href: `${prefix}/incidents/`, label: 'Incidents' },
    { href: `${prefix}/changelog/`, label: 'Changelog' },
    { href: `${prefix}/api/v1/`, label: 'API' },
  ];

  const nav = el('nav', { class: 'site-nav', 'aria-label': 'Primary' },
    baseLinks.map(l => el('a', { href: l.href }, [l.label]))
  );

  // Small utility links on the right
  const meta = el('div', { class: 'site-meta' }, [
    el('a', { href: '/.well-known/ai-trust-hub.json', title: 'Trust manifest (JSON)' }, ['manifest']),
    el('a', { href: '/.well-known/minisign.pub', title: 'Minisign public key' }, ['minisign']),
    el('a', { href: '/.well-known/llms.txt', title: 'LLM entrypoint' }, ['llms.txt']),
  ]);

  const brand = el('div', { class: 'site-brand' }, [
    el('a', { href: `${prefix}/`, class: 'brand' }, ['ONETOO']),
    el('span', { class: 'brand-sub' }, ['AI Trust Hub']),
  ]);

  const header = el('header', { class: 'site-header' }, [
    el('div', { class: 'site-header-inner' }, [brand, nav, meta])
  ]);

  const footer = el('footer', { class: 'site-footer' }, [
    el('div', { class: 'site-footer-inner' }, [
      el('div', {}, ['© ', String(new Date().getFullYear()), ' onetoo.eu · ']),
      el('div', { class: 'site-footer-links' }, [
        el('a', { href: `${prefix}/security/` }, ['Security']),
        el('a', { href: `${prefix}/privacy/` }, ['Privacy']),
        el('a', { href: `${prefix}/transparency/` }, ['Transparency']),
        el('a', { href: `${prefix}/accessibility/` }, ['Accessibility']),
      ])
    ])
  ]);

  document.body.prepend(header);
  document.body.appendChild(footer);
}

function highlightActiveNav() {
  const links = Array.from(document.querySelectorAll('.site-nav a'));
  if (!links.length) return;
  const here = location.pathname.replace(/index\.html$/, '');
  let best = null;
  for (const a of links) {
    const href = new URL(a.getAttribute('href'), location.origin).pathname.replace(/index\.html$/, '');
    if (here === href || (href !== '/' && here.startsWith(href))) {
      if (!best || href.length > best.href.length) best = { a, href };
    }
  }
  if (best) best.a.setAttribute('aria-current', 'page');
}

document.addEventListener('DOMContentLoaded', () => {
  try {
    ensureSkipLink();
    injectHeaderFooter();
    ensureMainId();
    highlightActiveNav();
  } catch (e) {
    // Never block rendering.
    console.warn('onetoo trust hub enhancer failed:', e);
  }
});
