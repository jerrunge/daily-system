# JER-169 Phase 2 — Wix to Webflow Essay Migration

**Date:** Wednesday April 29, 2026, 1:25pm PT
**Status:** Phase A complete (CMS migration). Phase B remaining (Designer template build, archive Collection Lists, redirects, publish).

---

## What lives here

- `converter.py` — Draft.js to Webflow Rich Text HTML converter. Strips Wix FG color inline styles, preserves BOLD/ITALIC/links, normalizes whitespace.
- `build-manifest.py` — One-shot build of all 22 essay item payloads from Wix inputs and JR's editorial decisions. Produces `manifest.json`.
- `manifest.json` — Final list of 22 Webflow CMS Essay items ready for import. This is the source of truth.
- `inventory.json` — Inventory of 21 Wix essays with categories per JER-169 archive table, plus The Undoing (typed by JR, not on Wix).
- `the-undoing.txt` — JR's raw text for The Undoing (April 19, 2026, Work of Being, pin position 1).
- `the-undoing.html` — Webflow Rich Text body for The Undoing.

## Migration decisions

1. **CMS over static pages** — single Webflow Essays collection, slug `writing`, URL pattern `/writing/{slug}`.
2. **Single Pin Position field** — 0/empty = not pinned, 1/2/3 = pin slot. Replaces a Switch + Order pair.
3. **Option field for Category** — 9 categories baked in: Work of Being, Foundation First, Real Leadership, Change it Up, On Healing, On Love, On Nature, On Joy, On People.
4. **Note to self prefix stripped** from titles per JR option 1.
5. **Note to self... opening line and duplicate-title line stripped from body** as Wix scaffolding artifacts (Webflow renders the title above, so they're redundant).
6. **Em dashes preserved in body text** per JR option A. Two essays carry them: Letter-size paper (8) and F'IT to Begin (2).
7. **Slugs Plan B** — short, hand-curated forms with redirects from old `/post/[long-slug]` to `/writing/[short-slug]`. Redirects pending Phase B.
8. **Pinned items** — The Undoing (1), F'IT to Begin (2), The power was the empathy (3).

## Webflow site identifiers

- Site ID: `69ea499cb31e121eb849ed15`
- Essays collection ID: `69f263baff78af7d19b90c93`
- Collection slug: `writing`

## Field IDs

| Field | Type | ID |
|-------|------|-----|
| Name (auto) | PlainText | `12f290449a49aef43b3e707d361425b6` |
| Slug (auto) | PlainText | `fd80763aff5aba0a8b68f275d87cce49` |
| Category | Option (9 values) | `166e2dd87f73db017e65f0895a74658b` |
| Published Date | DateTime | `f460f38e820057098f46501b8f553d1e` |
| Excerpt | PlainText | `2094c7549c2900929c56f764da188c7a` |
| Body | RichText | `d65135847945c79ff71e537b421418cb` |
| Pin Position | Number | `cd39a04ba861616063d321c2ded6ddce` |
| External URL | Link | `09418a839755f680c947f61d3df4a54f` |
| SEO Title | PlainText | `b062398fbb5262fd9469d3b0e44df906` |
| SEO Description | PlainText | `1d88d896879c9a9c37d8ee7814f85f9b` |
| OG Image | Image | `c952d127445f02f8898db655ca8c6ab4` |

## Migration audit

22 of 22 items created as drafts. Internal audit caught 1 transcription error (missing paragraph in "All you built now rubble?") and corrected it. All other paragraph counts match the manifest source.

## Phase B remaining

1. Build `/writing/{slug}` template page in Webflow Designer with Palette B.
2. Replace static archive on `/writing` with two Collection Lists (3 pinned, then full archive sorted by Published Date desc).
3. Replace homepage 3 pinned essay cards with Collection List filtered by Pin Position > 0.
4. Verify existing `filterCat()` JS works against rendered DOM with `data-cat` attribute bound to Category.
5. Set up 21 redirects from `/post/[old-long-slug]` to `/writing/[short-slug]` in Webflow project settings.
6. Publish all 22 items live.
7. Publish site.

## Two items flagged for JR review

1. **"Learning is a gift"** opens with a standalone "Love" line as the first paragraph (Wix had it that way, possibly accidental). Easy to remove if not intended.
2. **"The Grand Canyon, Ooh Aah"** body opens with "The Grand Canyon... Ooh Aah" which restates the title. The de-duplication pass missed it because the strings differed enough. Easy to remove.

Both are one-call updates if JR wants them cleaned.
