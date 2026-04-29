#!/usr/bin/env python3
"""
Draft.js -> Webflow Rich Text HTML converter.

Wix Blog stores post bodies as Draft.js block JSON. Webflow Rich Text accepts HTML.
This converter handles everything used in JR's essays:
  - unstyled paragraphs -> <p>
  - unordered-list-item -> <ul><li>
  - ordered-list-item -> <ol><li>
  - blockquote -> <blockquote>
  - inline styles BOLD -> <strong>, ITALIC -> <em>
  - entity ranges of type LINK -> <a href="...">
  - Strips Wix FG color inline styles (they're all just default black)
  - Preserves apostrophes, ellipses, em dashes (em dashes only present in current Wix titles, will be stripped before this runs)
  - Empty paragraphs are dropped (Wix uses them as visual spacing; HTML <p> margins handle that natively)

Usage:
  from converter import draftjs_to_html
  html = draftjs_to_html(body_json_str)
"""
import json
import html as htmllib

def _escape(s):
    return htmllib.escape(s, quote=False)

def _is_semantic_style(style):
    """Only BOLD and ITALIC are kept. Wix FG color styles are dropped."""
    return style in ("BOLD", "ITALIC")

def _wrap_inline(text, style_ranges, entity_ranges, entity_map):
    """
    Apply inline styles and entity ranges character-by-character.
    Returns HTML string with proper tags.
    """
    if not text:
        return ""
    # Build per-char style sets
    n = len(text)
    char_styles = [set() for _ in range(n)]
    char_entity = [None] * n
    for r in style_ranges or []:
        style = r.get("style", "")
        if not _is_semantic_style(style):
            continue
        start = r["offset"]
        end = start + r["length"]
        for i in range(start, min(end, n)):
            char_styles[i].add(style)
    for r in entity_ranges or []:
        key = str(r.get("key", ""))
        ent = (entity_map or {}).get(key)
        if not ent:
            continue
        if ent.get("type") != "LINK":
            continue
        url = (ent.get("data") or {}).get("url") or (ent.get("data") or {}).get("href")
        if not url:
            continue
        start = r["offset"]
        end = start + r["length"]
        for i in range(start, min(end, n)):
            char_entity[i] = url
    # Walk and emit
    out = []
    open_styles = []  # stack: "STRONG", "EM"
    open_link = None
    def style_to_tag(s):
        return {"BOLD": "strong", "ITALIC": "em"}[s]
    for i, ch in enumerate(text):
        # Resolve transitions: close any tags whose state ended; open new ones.
        desired_link = char_entity[i]
        desired_styles = char_styles[i]
        # Close link if needed
        if open_link is not None and desired_link != open_link:
            # Close all open inline styles first (they nest inside <a>)
            while open_styles:
                out.append(f"</{style_to_tag(open_styles.pop())}>")
            out.append("</a>")
            open_link = None
        # Open link if needed
        if desired_link is not None and open_link is None:
            out.append(f'<a href="{_escape(desired_link)}">')
            open_link = desired_link
        # Close styles no longer desired (LIFO)
        while open_styles and open_styles[-1] not in desired_styles:
            out.append(f"</{style_to_tag(open_styles.pop())}>")
        # Open styles newly desired (consistent BOLD-then-ITALIC ordering)
        for s in ("BOLD", "ITALIC"):
            if s in desired_styles and s not in open_styles:
                out.append(f"<{style_to_tag(s)}>")
                open_styles.append(s)
        out.append(_escape(ch))
    # Close any remaining tags
    while open_styles:
        out.append(f"</{style_to_tag(open_styles.pop())}>")
    if open_link is not None:
        out.append("</a>")
    return "".join(out)

def draftjs_to_html(body_json):
    """
    Convert a Draft.js content state (JSON string or dict) to HTML.
    Returns a string of HTML suitable for Webflow Rich Text.
    """
    if isinstance(body_json, str):
        data = json.loads(body_json)
    else:
        data = body_json
    blocks = data.get("blocks", [])
    entity_map = data.get("entityMap", {}) or {}
    out = []
    list_open = None  # "ul" or "ol" if currently inside a list, else None
    for b in blocks:
        btype = b.get("type", "unstyled")
        text = b.get("text", "") or ""
        styles = b.get("inlineStyleRanges", []) or []
        ents = b.get("entityRanges", []) or []
        # Close list if leaving list context
        if list_open and btype not in ("unordered-list-item", "ordered-list-item"):
            out.append(f"</{list_open}>")
            list_open = None
        # Skip purely empty unstyled blocks; <p> margins handle spacing.
        if btype == "unstyled" and not text.strip():
            continue
        if btype == "unstyled":
            inner = _wrap_inline(text, styles, ents, entity_map)
            out.append(f"<p>{inner}</p>")
        elif btype == "blockquote":
            inner = _wrap_inline(text, styles, ents, entity_map)
            out.append(f"<blockquote><p>{inner}</p></blockquote>")
        elif btype == "unordered-list-item":
            if list_open != "ul":
                if list_open:
                    out.append(f"</{list_open}>")
                out.append("<ul>")
                list_open = "ul"
            inner = _wrap_inline(text, styles, ents, entity_map)
            out.append(f"<li>{inner}</li>")
        elif btype == "ordered-list-item":
            if list_open != "ol":
                if list_open:
                    out.append(f"</{list_open}>")
                out.append("<ol>")
                list_open = "ol"
            inner = _wrap_inline(text, styles, ents, entity_map)
            out.append(f"<li>{inner}</li>")
        elif btype.startswith("header-"):
            level = btype.replace("header-", "")
            level_map = {"one": "h2", "two": "h3", "three": "h4", "four": "h5", "five": "h6", "six": "h6"}
            tag = level_map.get(level, "h3")
            inner = _wrap_inline(text, styles, ents, entity_map)
            out.append(f"<{tag}>{inner}</{tag}>")
        else:
            # Unknown type: render as paragraph
            inner = _wrap_inline(text, styles, ents, entity_map)
            out.append(f"<p>{inner}</p>")
    if list_open:
        out.append(f"</{list_open}>")
    return "\n".join(out)


if __name__ == "__main__":
    # Quick self-test
    sample = {
        "blocks": [
            {"key": "p1", "type": "unstyled", "text": "Hello world.", "inlineStyleRanges": [{"style": "BOLD", "offset": 0, "length": 5}], "entityRanges": []},
            {"key": "p2", "type": "unstyled", "text": "", "inlineStyleRanges": [], "entityRanges": []},
            {"key": "p3", "type": "unordered-list-item", "text": "First", "inlineStyleRanges": [], "entityRanges": []},
            {"key": "p4", "type": "unordered-list-item", "text": "Second", "inlineStyleRanges": [{"style": "ITALIC", "offset": 0, "length": 6}], "entityRanges": []},
            {"key": "p5", "type": "unstyled", "text": "After list.", "inlineStyleRanges": [], "entityRanges": []},
        ],
        "entityMap": {}
    }
    print(draftjs_to_html(sample))
