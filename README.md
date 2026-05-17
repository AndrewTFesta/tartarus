Tartarus
=====

# Tartarus

A personal knowledge base for humans and the AI agents working alongside
them. Pulls in the streams of information you already deal with — open
browser tabs, bookmarks, newsletter emails, saved articles — and grows a
durable, searchable store that you and your agents can both query over
long time horizons.

> Tartarus, in Greek myth, is the abyss beneath the underworld where the
> Titans were kept. The name nods at scale (titanic amounts of
> information) and time (extended horizons), not at darkness — this is a
> place where things are kept, not lost.

**Status:** early. The tab-ingest utility (`open_tabs.py`) is the first
working piece. Bookmark ingest, email ingest, semantic chunking and
grouping, and an MCP/OpenAPI surface are planned. See [Roadmap](#roadmap).

## Why

The information you encounter daily is *already structured* — it arrives
as URLs, emails, bookmarks, papers, conversations. Most of it gets lost
not because it's hard to capture but because the capture surfaces are
fragmented and what's captured never gets re-touched.

Tartarus exists to fix two things at once:

1. **Ingestion** that meets you where your data already is. You shouldn't
   have to manually copy a URL into a notes app to remember it. Export
   what you have, point Tartarus at it, get a clean record.
2. **Re-use** by both you and your agents. Once a piece of information is
   in the store, it should be queryable, groupable by topic, and
   composable into context for whatever question comes up next — whether
   that's "what did I read about retrieval evaluation last fall" or an
   agent asking "what does this user already know about X."

The lineage is roughly: Karpathy's personal wiki for the
keep-everything-and-search-later instinct; Open Brain ([OB1](https://github.com/NateBJones-Projects/OB1))
for the "shared persistent memory across many AI tools" framing; and
years of doing literature reviews where the slow part is never the
reading, it's the grouping.

## Design principles

These are commitments, not aspirations. Anything claiming to be Tartarus
should hold to them.

- **Pure-Python core, stdlib first.** External dependencies need to earn
  their place. Embedding models and vector stores will need them; the
  ingestion and dedup layer doesn't.
- **Application *and* library.** Every utility is callable from a CLI
  *and* importable as a module. `main()` takes a dict, so other code
  can drive it without going through argparse.
- **Lossless ingestion.** Raw input is preserved. Normalization,
  deduplication, and enrichment happen in derived layers, not by
  modifying source data in place.
- **Staged pipelines.** Parse → normalize → dedupe → enrich → store →
  query. Each stage is a pure function; new stages slot in without
  rewriting old ones.
- **Local-first, optionally networked.** Tartarus should run end-to-end
  on your laptop with no API keys. Cloud embeddings and remote stores
  are upgrades, not prerequisites.

## Architecture

```
                ┌─────────────────────────────────────┐
                │            INGESTION                │
                │                                     │
   tabs.md ────▶│  open_tabs        (✓ implemented)   │──▶ Record
   bookmarks ──▶│  ingest_bookmarks (planned)         │──▶ Record
   emails ─────▶│  ingest_emails    (planned)         │──▶ Record
                │                                     │
                └────────────────────┬────────────────┘
                                     │
                ┌────────────────────▼────────────────┐
                │            NORMALIZATION            │
                │  URL canonicalization, dedupe,      │
                │  title resolution, content fetch    │
                └────────────────────┬────────────────┘
                                     │
                ┌────────────────────▼────────────────┐
                │             ENRICHMENT              │
                │  embed, chunk, tag, semantic group  │
                │  (planned)                          │
                └────────────────────┬────────────────┘
                                     │
                ┌────────────────────▼────────────────┐
                │               STORE                 │
                │  flat files now, vector store later │
                └────────────────────┬────────────────┘
                                     │
                ┌────────────────────▼────────────────┐
                │             INTERFACES              │
                │  CLI ✓  │  Python lib ✓             │
                │  MCP (planned)  │  OpenAPI (planned)│
                └─────────────────────────────────────┘
```

Each band is a separate, swappable concern. You can use the ingestion
utilities standalone (this is what's shipped today), or wire them into a
larger pipeline once enrichment and store exist.

## Quickstart

Tartarus works both as a command-line tool and as a Python library. The
same example, shown both ways:

### As an application

```bash
# Clean and dedupe a dump of open browser tabs
python -m scripts.open_tabs my_tabs.md -o cleaned.md --stats
```

Output is a markdown bullet list, deduped against URL canonicalization
rules (tracking params stripped, mobile/desktop variants collapsed,
fragments dropped). See [`open_tabs.md`](scripts/open_tabs.py) for the design.

### As a library

```python
from scripts.open_tabs import parse, dedupe, to_markdown

raw = open("my_tabs.md").read()
tabs = parse(raw)  # list[Tab]
unique = dedupe(tabs)  # canonical URLs, best-available titles
print(to_markdown(unique))
```

Or drive the full pipeline:

```python
from scripts.open_tabs import main

result = main({
    "input": "my_tabs.md",
    "output": "cleaned.md",
    "stats": False,
})
```

Every utility in Tartarus follows the same shape: pure pipeline
functions you can compose, plus a `main(dict)` entry point for end-to-end
runs.

## Repository layout

```
tartarus/
├── README.md                  # you are here
├── scripts
│   ├── open_tabs.py           # ✓ browser tab dumps
│   ├── bookmarks.py           # planned
│   └── newsletters.py         # planned
├── tartarus/
│   ├── normalize/             # cross-source canonicalization (planned)
│   ├── enrich/                # embedding, chunking, tagging (planned)
│   ├── store/                 # persistence layer (planned)
│   └── interfaces/            # MCP, OpenAPI, etc. (planned)
└── docs/
    ├──style_guide.md         # ✓ contributor conventions
    └── scripts
        └── open_tabs.md   # ✓ design notes for the tab ingester
```

The directory structure is aspirational where modules don't yet exist;
the goal is for the layout to be obvious enough that new contributions
have an obvious home.

## Extending Tartarus

### Add a new ingestion source

A new source goes in `scripts/<source>.py` and follows the same
pipeline shape as `open_tabs.py`:

1. **Parse** — turn raw input into a list of records (a dataclass, one
   per item).
2. **Normalize** — canonicalize fields that will be used for dedup or
   grouping (URLs, dates, identifiers).
3. **Dedupe** — collapse duplicates against the canonical form.
4. **Emit** — render to markdown, JSON, or hand off to the store.

Each step is a pure function. The `main(main_args)` entry point wires
them together. See `open_tabs.py` for the reference implementation
and `open_tabs.md` for the design rationale.

### Use Tartarus's primitives in your own code

Tartarus is built so individual functions are useful in isolation. URL
canonicalization, in particular, tends to be reinvented poorly in every
project that touches links. You can use ours directly:

```python
from scripts.open_tabs import normalize_for_dedupe

normalize_for_dedupe("https://www.example.com/article?utm_source=x#top")
# 'https://example.com/article'
```

The same pattern will apply to email-thread normalization, bookmark
deduplication across browsers, and so on as those modules land.

## Roadmap

| Stage | Status | Notes |
|-------|--------|-------|
| Tab dump ingestion | ✓ shipped | `open_tabs.py`; markdown in/out |
| Bookmark ingestion | planned | Chrome/Firefox/Safari export formats |
| Newsletter ingestion | planned | TLDR.ai and similar; .mbox or IMAP |
| Cross-source dedup | planned | Unified record schema, content-hash fallback |
| Content fetching | planned | Pull article text for ingested URLs |
| Embedding + chunking | planned | Local models first; cloud as upgrade |
| Semantic grouping | planned | Cluster records by topic for fast browsing |
| Persistent store | planned | SQLite + vector extension to start |
| MCP server | planned | Expose query/insert to agent tools |
| OpenAPI surface | planned | For non-MCP integrations |
| Claude skills | planned | Capture and query patterns for Claude users |

Order isn't fixed; what gets built next depends on which gap is most
painful to leave open.

## Contributing

Tartarus is single-maintainer right now, but the code is structured for
contributions when they arrive. Conventions live in
[`docs/style_guide.md`](./docs/style_guide.md) — the short version:

- Pure functions, stdlib-first, type hints with builtins (no
  `from __future__`).
- Every CLI utility also works as a library; argparse lives only inside
  `if __name__ == '__main__'`.
- Design decisions get documented alongside the code that implements
  them (see `open_tabs.md` as the template).
- Honesty about what's tested vs. believed-to-work vs. unverified.

## Related work

Tartarus is one point in a design space that several others occupy. If
you're evaluating options, these are worth looking at:

- **[Open Brain (OB1)](https://github.com/NateBJones-Projects/OB1)** —
  Supabase-backed personal memory layer with MCP. More opinionated about
  storage stack (PostgreSQL + pgvector); less focused on multi-source
  ingestion pipelines.
- **Karpathy's personal wiki** — the spiritual ancestor of "keep
  everything, search later" personal knowledge tools.
- **[Obsidian](https://obsidian.md/)** with community plugins for vector
  search — strong if you want a human-first UI; Tartarus is more
  agent-first.
- **[mem0](https://github.com/mem0ai/mem0)** — memory layer for LLM
  applications. Tartarus is broader-scope (the source-of-truth store,
  not the conversation memory).

Tartarus's distinctive bet is on **multi-source ingestion as a
first-class concern** and on being usable as both an application and a
library so you can adopt as much or as little as you need.

## License

TBD.

## Utilities

A move in-depth overview of the available utilities exists in the [scripts folder in the docs](docs/scripts). Here is a brief outline of these utilities below.

### `open_tabs`

Clean and dedupe a Chrome tab dump (markdown-formatted) into a deduplicated markdown bullet list.

Pipeline: `parse -> normalize -> dedupe -> emit`

### `bookmarks`
