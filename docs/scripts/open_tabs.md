---
title: Parse Open Tabs
author: Andrew Festa
date: 5/17/2026
---

Parse Open Tabs
=====

A reference for developers (human or AI) who need to debug, extend, or
reason about `open_tabs.py`. Pairs with the source; doesn't replace
reading it.

## What it does

Takes a markdown-formatted Chrome tab dump (lines of `[title](url "hover")`
plus occasional bare URLs), produces a deduplicated markdown bullet list.
Stdlib only.

## Architecture

Four pure functions wired together in `main`, each owning one stage:

```
raw text  ──parse──▶  list[Tab]  ──dedupe──▶  list[Tab]  ──to_markdown──▶  str
                                  (uses normalize_for_dedupe internally)
```

- **`parse(text)`** — regex-extract `Tab` objects from raw input. Output
  may contain duplicates; output URLs are exactly as captured.
- **`normalize_for_dedupe(url)`** — pure function from URL string to
  canonical key string. The canonical form is what we both deduplicate
  on and store. There is no separate "original URL" stored anywhere
  past this stage.
- **`dedupe(tabs)`** — collapse tabs sharing a canonical URL. Returns
  `Tab` objects whose `url` field is the canonical form and whose
  `title` is the best-available title from the group.
- **`to_markdown(tabs)`** — render to `- [title](url)` lines.

`main` takes a dict (typically `vars(argparse.Namespace)`) so it's
callable from other scripts without going through the CLI. Argparse
is confined to the `if __name__ == '__main__'` block.

### Why these seams

Each function is independently testable and replaceable. The two
extensions we expect — sorting and semantic grouping — slot in between
`dedupe` and `to_markdown` without touching either:

```python
# future:
sorted_tabs = sort_by_something(cleaned)
grouped = group_semantically(sorted_tabs)
rendered = to_markdown_grouped(grouped)
```

`Tab` being a `@dataclass(frozen=True)` means it's hashable and
immutable; any stage that needs to enrich a `Tab` (add a group label,
a score, a timestamp) should produce new `Tab` instances rather than
mutating, or extend the dataclass with optional fields.

## Design decisions

### Canonical URLs are stored, not original URLs

After `dedupe`, the `url` on each `Tab` is the normalized form
(`https://`, no `www.`, no `m.`, no tracking params, no fragment, no
trailing slash). This was a deliberate flip from earlier versions.

Rationale: the output is meant to be a clean archive. If we ever sort,
group, or feed these URLs into a downstream tool, having one canonical
form per destination is simpler than carrying around an arbitrary
representative.

Consequence: the output URL may not byte-match anything in the input.
Browsers will redirect appropriately (`https://reddit.com/r/python`
loads fine on mobile and desktop), so this is invisible in practice,
but it's worth knowing if you're diffing input against output.

### Normalization is "safe by omission"

`normalize_for_dedupe` only strips things on explicit allowlists. A
query parameter that isn't in `_TRACKING_PARAMS` is kept. A host that
doesn't match the `www./m./mobile.` patterns is kept. This makes the
risk surface predictable: errors are over-keeping (two entries when
one would do), not under-keeping (wrong destinations).

### Title selection: "first non-bare-URL title wins"

When multiple tabs collapse into one, we want a real title rather than
a raw URL string. The rule:

- If the first occurrence has a real title, keep it.
- If the first occurrence's title is a bare URL but a later one has a
  real title, upgrade.
- If everything is a bare URL, keep the first.

"Bare URL title" is detected structurally by `_title_is_bare_url`:
does it start with `http://` or `https://`. This is more robust than
the earlier check (`title == url`), which broke when we started
storing the *normalized* URL — bare-URL titles never match the
normalized URL because of `www.`/`m.` stripping.

### Two-pass parser

`parse` runs the markdown-link regex over the full text, then makes a
second pass for line-anchored bare URLs. This is intentional: the
user's data contains both forms, sometimes interleaved. We don't try
to be clever about distinguishing them — we extract everything, let
`dedupe` collapse the overlaps. Performance is fine at the scale of a
few thousand tabs.

## Known edge cases

### URL parsing

- **Escaped parens in URLs.** The regex captures URLs containing
  `\(` and `\)` (Wikipedia disambiguators like `Silo_\(series\)`) and
  the parser unescapes them. URLs with literal unescaped parens
  followed by markdown closer `)` will truncate — but Chrome's
  markdown export escapes them, so this hasn't bitten in practice.
- **`urlsplit` is permissive.** Malformed URLs that `urlsplit` accepts
  but `urlencode` later chokes on will raise. The only place we catch
  this is around `urlsplit` itself; a downstream failure would
  propagate. If you see crashes on weird URLs, that's the first place
  to look.
- **Bare-URL regex requires whole-line match.** `_BARE_URL` uses `^`
  and `$` anchors, so a bare URL embedded mid-line (with surrounding
  text) won't be captured. The markdown-link regex picks up
  link-formatted URLs anywhere, so this only matters for genuinely
  unformatted URLs in prose.

### Host normalization

- **Mobile/desktop collapsing.** `m.example.com`, `mobile.example.com`,
  and `en.m.wikipedia.org` all collapse to their desktop equivalents.
  The interior `.m.` strip uses `replace(".m.", ".", 1)` with a count
  of 1, so we never over-collapse hosts that happen to contain `.m.`
  more than once (none exist in practice; the cap is defensive).
- **Hosts we don't normalize.** Country-code subdomains
  (`uk.example.com` vs `example.com`), language subdomains
  (`en.wikipedia.org` vs `de.wikipedia.org`), and protocol-specific
  subdomains are all kept distinct. If a user wants those collapsed,
  it's a deliberate new rule, not an oversight.
- **Port and userinfo.** `parts.netloc` includes any `:port` or
  `user:pass@` prefix and we preserve them verbatim after lowercasing.
  This is correct but means `example.com:443` and `example.com` won't
  dedupe, even though they're the same destination. Not seen in
  practice for browser tabs.

### Query-param stripping

- **`_TRACKING_PARAMS` is hand-curated and conservative.** When in
  doubt, leave it out. The set lives at module scope as a constant —
  if a user reports "these two URLs should have deduplicated but
  didn't," look for a tracking param not yet on the list. If they
  report "these URLs deduplicated but shouldn't have," look for a
  load-bearing param that's on the list (the most suspicious entries
  are `ref`, `src`, `source`, and `client` — short generic names that
  could be either analytics or routing depending on the site).
- **Param key matching is case-insensitive** (`k.lower() not in ...`).
  Param values are never touched — we strip whole pairs, never
  rewrite values.
- **Param order within the kept set is preserved.** Two URLs with the
  same params in different orders will *not* dedupe. This is by
  design (params can be order-sensitive on some APIs) but if it
  becomes a problem, sorting `kept` before `urlencode` is the fix.

### Title handling

- **HTML entities and unicode in titles** are passed through unchanged.
  We don't try to decode or normalize them; whatever came in goes out.
- **Bracket escaping at emit time.** `to_markdown` escapes `]` in
  titles so the output is valid markdown. No other characters are
  escaped — `[`, parens, and pipes pass through. This has been fine
  for Chrome's exports; aggressive markdown processors might choke on
  edge cases.

## CLI

```
python3 open_tabs.py input.md [-o output.md] [--stats]
```

- `input` (positional, required) — path to raw tab dump
- `-o/--output` — destination file; omit for stdout
- `--stats` — write `parsed=N unique=M removed=K` to stderr

## Modifying common things

- **Add/remove a tracking param.** Edit `_TRACKING_PARAMS` at module
  scope. Set membership is case-insensitive, so add lowercase only.
- **Change mobile-host handling.** Edit the host block in
  `normalize_for_dedupe` (the section between scheme and query-param
  filtering). All host transforms live there.
- **Change "best title" rule.** Edit `_title_is_bare_url` (what counts
  as a placeholder) and/or the upgrade condition inside `dedupe`. The
  rule is intentionally simple; if it grows beyond two conditions,
  consider extracting a `_pick_better_title(a, b)` function.
- **Emit something other than markdown.** Add a new emit function
  (e.g. `to_json(tabs)`) and let `main` dispatch on a `--format` flag.
  Don't generalize `to_markdown`; keep one function per output format.
- **Drive the pipeline programmatically.** `import open_tabs` and
  call `main({'input': ..., 'output': None, 'stats': False})` for the
  full pipeline, or compose `parse`/`dedupe`/`to_markdown` directly
  for finer control.

## Things that are deliberately not here

- No tests. The pipeline is short enough to eyeball; add tests when
  the next feature (sort, group) lands.
- No config file. Tracking params and host rules are code, not data,
  because changing them is a decision that warrants a diff.
- No logging framework. `--stats` to stderr is the only diagnostic
  output; anything more would be premature.
- No async, no streaming. Inputs are small enough to fit in memory
  comfortably.