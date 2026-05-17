"""
@title
    clean_tabs

@description
    Clean and dedupe a Chrome tab dump (markdown-formatted) into a
    deduplicated markdown bullet list. Pipeline: parse -> normalize -> dedupe ->
    emit. Each stage is a pure function so sort/group can slot in later without
    restructuring.

"""

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode


# ---------------------------------------------------------------- data model

@dataclass(frozen=True)
class Tab:
    title: str
    url: str  # original at parse time; normalized (canonical) after dedupe


# ---------------------------------------------------------------- parse

# Matches [title](url) or [title](url "hover"). The url can contain
# backslash-escaped parens (Wikipedia disambiguators like Silo_\(series\)),
# so we match either an escaped paren OR a non-space-non-paren char.
# noinspection RegExpRedundantEscape
_MD_LINK = re.compile(
    r'\[(?P<title>[^\]]*)\]'
    r'\((?P<url>(?:\\[()]|[^\s()])+)'
    r'(?:\s+"[^"]*")?\)'
)

# Bare URL fallback for lines that aren't markdown.
_BARE_URL = re.compile(r'^\s*(https?://\S+)\s*$')


def parse(text: str) -> list[Tab]:
    """Extract Tabs from raw text. Skips anything that isn't a link."""
    tabs: list[Tab] = []

    # Try markdown links first -- they may appear several per line.
    for m in _MD_LINK.finditer(text):
        title = m.group("title").strip()
        url = m.group("url").strip()
        # Markdown escapes \( and \) inside URLs; the actual URL has bare parens.
        url = url.replace(r"\(", "(").replace(r"\)", ")")
        if not url.startswith(("http://", "https://")):
            continue
        # If title is empty or just the URL itself, use the URL.
        tabs.append(Tab(title=title or url, url=url))

    # Then bare URLs on their own line. We do this in addition, and let dedupe
    # handle any overlap with markdown-captured links.
    for line in text.splitlines():
        m = _BARE_URL.match(line)
        if m:
            url = m.group(1)
            tabs.append(Tab(title=url, url=url))

    return tabs


# ---------------------------------------------------------------- normalize

# Tracking params we strip when building the dedupe key. Conservative list --
# we don't try to strip anything that might be load-bearing for the page.
_TRACKING_PARAMS = {
    # Google / generic UTM
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "utm_id", "utm_name", "utm_brand", "utm_social", "utm_social-type",
    # Click IDs
    "gclid", "gclsrc", "dclid", "fbclid", "msclkid", "yclid",
    "gbraid", "wbraid", "_gl",
    # Misc affiliate / analytics
    "mc_eid", "mc_cid", "mkt_tok", "vero_id", "vero_conv",
    "icid", "ncid", "ref", "ref_src", "ref_url", "referrer",
    "hsa_acc", "hsa_cam", "hsa_grp", "hsa_ad", "hsa_src",
    "hsa_tgt", "hsa_kw", "hsa_mt", "hsa_net", "hsa_ver",
    # LinkedIn-flavored
    "trk", "trkCampaign", "li_fat_id", "li_ed", "c99_c", "c99_s",
    "mcid", "src", "veh", "tblci",
    # Taboola / Outbrain
    "tblci", "obOrigUrl",
    # Google search internals that don't change the result
    "sca_esv", "sxsrf", "ei", "ved", "uact", "sa", "sqi",
    "biw", "bih", "dpr", "iflsig", "source", "sourceid",
    "ie", "oe", "client", "hs", "zx", "no_sw_cr",
    "gs_lcrp", "gs_lp", "gs_ssp", "gs_lcp", "sclient",
    "rlz", "ved2", "psig", "psig_h", "psig_o",
}


def normalize_for_dedupe(url: str) -> str:
    """Return the canonical key used to detect dupes. Not for display."""
    try:
        parts = urlsplit(url)
    except ValueError:
        return url  # malformed; treat as opaque

    scheme = parts.scheme.lower()
    # Treat http/https as the same destination -- they almost always are.
    if scheme == "http":
        scheme = "https"

    # Lowercase host, then strip subdomain prefixes that point at the same
    # underlying site: "www.", a leading "m." or "mobile.", and an interior
    # ".m." (e.g. en.m.wikipedia.org -> en.wikipedia.org).
    host = parts.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    if host.startswith("m."):
        host = host[2:]
    elif host.startswith("mobile."):
        host = host[7:]
    host = host.replace(".m.", ".", 1)

    # Strip tracking params; keep the rest in their original order.
    kept = [
        (k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
        if k.lower() not in _TRACKING_PARAMS
    ]
    query = urlencode(kept, doseq=True)

    # Trim trailing slash on path (but not on bare "/").
    path = parts.path
    if len(path) > 1 and path.endswith("/"):
        path = path[:-1]

    # Drop fragment entirely -- it's client-side, never a different resource
    # for our purposes.
    return urlunsplit((scheme, host, path, query, ""))


# ---------------------------------------------------------------- dedupe

def _title_is_bare_url(title: str) -> bool:
    """True if the title is just a URL (the fallback we use when parsing a
    bare-URL line or a markdown link with an empty title)."""
    return title.startswith(("http://", "https://"))


def dedupe(tabs: list[Tab]) -> list[Tab]:
    """Collapse duplicate destinations and store the canonical URL.

    For each group of tabs sharing a normalized URL, we keep one entry:
    the URL is the normalized form (https, www/mobile stripped, no tracking
    params, no fragment, no trailing slash), and the title is the best one
    we saw -- the first non-URL title, or the first title if they were all
    just bare URLs.

    Preserves the order of first appearance.
    """
    # Map normalized URL -> index into `out`, so we can update the title in
    # place if a later occurrence has a better one.
    index: dict[str, int] = {}
    out: list[Tab] = []

    for t in tabs:
        key = normalize_for_dedupe(t.url)
        if key in index:
            # We've seen this destination. If the stored title is a bare URL
            # and this one is a real title, upgrade it.
            existing = out[index[key]]
            if _title_is_bare_url(existing.title) and not _title_is_bare_url(t.title):
                out[index[key]] = Tab(title=t.title, url=existing.url)
            continue
        index[key] = len(out)
        out.append(Tab(title=t.title, url=key))

    return out


# ---------------------------------------------------------------- emit

def to_markdown(tabs: list[Tab]) -> str:
    """Render as a markdown bullet list."""
    lines: list[str] = []
    for t in tabs:
        # Escape ] in title so the markdown stays valid.
        title = t.title.replace("]", r"\]")
        lines.append(f"- [{title}]({t.url})")
    return "\n".join(lines) + ("\n" if lines else "")


# ---------------------------------------------------------------- main

def main(main_args: dict) -> str:
    """Run the pipeline. `main_args` is a dict (e.g. vars(argparse.Namespace)).

    Expected keys:
        input  (str | Path)         path to the raw tab dump
        output (str | Path | None)  where to write; None -> stdout
        stats  (bool)               if True, write stats to stderr

    Returns the rendered markdown string so callers can use it directly.
    """
    input_path: str | Path = Path(main_args["input"])
    output_path: str | Path | None = main_args.get("output")
    show_stats: bool = main_args.get("stats", False)

    raw = input_path.read_text(encoding="utf-8", errors="replace")
    parsed = parse(raw)
    cleaned = dedupe(parsed)
    rendered = to_markdown(cleaned)

    input_name = input_path.stem
    content_text = f'{input_name.title()}\n=====\n\n{rendered}'
    if output_path:
        Path(output_path).write_text(content_text, encoding="utf-8")
    else:
        sys.stdout.write(content_text)

    if show_stats:
        sys.stderr.write(
            f"parsed={len(parsed)} unique={len(cleaned)} "
            f"removed={len(parsed) - len(cleaned)}\n"
        )

    return rendered


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Clean and dedupe a Chrome tab dump.'
    )
    parser.add_argument(
        'input',
        help='path to the raw tab dump',
    )
    parser.add_argument(
        '-o', '--output',
        default=None,
        help='output file (default: stdout)',
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='print parse/dedupe stats to stderr',
    )

    args = parser.parse_args()
    main(vars(args))
