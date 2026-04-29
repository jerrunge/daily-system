#!/usr/bin/env python3
"""
Build all 22 Webflow CMS Essay item payloads.

Inputs hardcoded from Wix API responses. Why hardcoded: each Wix call requires
JR's UI approval, and once we have the data we don't want to call again.

Outputs:
  /home/claude/wix-essays/manifest.json - Final list of 22 items, ready for Webflow

Editorial decisions baked in:
  1. Title prefix "Note to self — " stripped from Name field per JR option 1.
  2. Display titles match the JER-169 handoff archive table where they differ
     from raw Wix titles (truncated for readability).
  3. The "Note to self..." opener line and duplicate-title line are stripped
     from body text (Wix scaffolding, redundant when title is rendered above).
  4. Em dashes and ellipses in body text are PRESERVED. They are JR's voice.
     SURFACING THIS DECISION FOR CONFIRMATION before publishing.
  5. Wix FG color inline styles are dropped. BOLD and ITALIC preserved.
  6. Slugs rewritten to short forms (Plan B, with redirects from old paths).
"""
import json
import sys
sys.path.insert(0, "/home/claude/wix-essays")
from converter import draftjs_to_html

# Title -> short slug mapping (Plan B, JR confirmed)
SLUG_MAP = {
    "Letter-size paper is the 40-hour work week. Everyone uses it. Nobody chose it.": "letter-size-paper",
    "F\u2019IT to Begin: Vision to reckoning, and building something that lasts.": "f-it-to-begin",
    "F'IT to Begin: Vision to reckoning, and building something that lasts.": "f-it-to-begin",
    "Team not performing? More metrics.": "team-not-performing",
    "All you built now rubble? Perfect. Rebuild your best yet.": "all-you-built-now-rubble",
    "Note to self \u2014 Remove the layers": "remove-the-layers",
    "Note to self \u2014 Each circle leads to the next": "each-circle-leads-to-the-next",
    "Note to self \u2014 Yosemite's glory remains": "yosemites-glory-remains",
    "Note to self \u2014 The Grand Canyon, Ooh Aah": "grand-canyon-ooh-aah",
    "Note to self \u2014 Own your natural beautiful": "own-your-natural-beautiful",
    "Note to self \u2014 Queenstown goofiness": "queenstown-goofiness",
    "Note to self \u2014 Learning is a gift": "learning-is-a-gift",
    "Note to self \u2014 The grandeur of the canyon": "grandeur-of-the-canyon",
    "Note to self \u2014 Love prevails": "love-prevails",
    "Note to self \u2014 Love in every season": "love-in-every-season",
    "Let the voices in": "let-the-voices-in",
    "Enable and choose": "enable-and-choose",
    "Note to self \u2014 Love, oh Love": "love-oh-love",
    "Note to self \u2014 Keep the joy, buddy": "keep-the-joy-buddy",
    "Walk together into the beautiful unknown": "walk-together-into-the-beautiful-unknown",
    "The power was the empathy": "the-power-was-the-empathy",
    "Love and discomfort": "love-and-discomfort",
}

# Display titles (Name field). Match JER-169 archive table where it differs from Wix raw.
DISPLAY_TITLE_MAP = {
    "Letter-size paper is the 40-hour work week. Everyone uses it. Nobody chose it.": "Letter-size paper is the 40-hour work week",
    "F'IT to Begin: Vision to reckoning, and building something that lasts.": "F'IT to Begin",
    "Team not performing? More metrics.": "Team not performing? More metrics.",
    "All you built now rubble? Perfect. Rebuild your best yet.": "All you built now rubble? Perfect.",
    # Note-to-self prefix stripped:
    "Remove the layers": "Remove the layers",
    "Each circle leads to the next": "Each circle leads to the next",
    "Yosemite's glory remains": "Yosemite's glory remains",
    "The Grand Canyon, Ooh Aah": "The Grand Canyon, Ooh Aah",
    "Own your natural beautiful": "Own your natural beautiful",
    "Queenstown goofiness": "Queenstown goofiness",
    "Learning is a gift": "Learning is a gift",
    "The grandeur of the canyon": "The grandeur of the canyon",
    "Love prevails": "Love prevails",
    "Love in every season": "Love in every season",
    "Love, oh Love": "Love, oh Love",
    "Keep the joy, buddy": "Keep the joy, buddy",
    # Plain titles:
    "Let the voices in": "Let the voices in",
    "Enable and choose": "Enable and choose",
    "Walk together into the beautiful unknown": "Walk together into the beautiful unknown",
    "The power was the empathy": "The power was the empathy",
    "Love and discomfort": "Love and discomfort",
}

def strip_prefix(title):
    """Remove 'Note to self — ' prefix if present."""
    for prefix in ("Note to self \u2014 ", "Note to self - ", "Note to self - "):
        if title.startswith(prefix):
            return title[len(prefix):]
    return title

def clean_body_blocks(blocks, original_title):
    """
    Strip Wix scaffolding from the start of body:
      - Leading 'Note to self...' opener paragraph (Wix structural artifact).
      - Duplicate-of-title paragraph (e.g. body opens with the title text).
    Keep all author voice that follows.
    """
    if not blocks:
        return blocks
    cleaned = list(blocks)
    # Drop leading 'Note to self...' opener
    while cleaned and cleaned[0].get("text", "").strip().lower().startswith("note to self"):
        cleaned.pop(0)
    # Drop a leading paragraph that is essentially the title repeated
    if cleaned:
        first_text = cleaned[0].get("text", "").strip().lower().rstrip(".:?!")
        title_norm = strip_prefix(original_title).strip().lower().rstrip(".:?!")
        # exact match or near-match (allow minor variants)
        if first_text == title_norm:
            cleaned.pop(0)
        elif title_norm in first_text and len(first_text) <= len(title_norm) + 20:
            cleaned.pop(0)
    # Also drop any blank leading blocks
    while cleaned and not cleaned[0].get("text", "").strip():
        cleaned.pop(0)
    return cleaned

# All 21 Wix essays (raw Draft.js content from API), plus The Undoing built separately.
# Format: list of dicts in archive display order (newest first per JER-169 archive table).
WIX_ESSAYS = [
    {
        "wix_title": "Letter-size paper is the 40-hour work week. Everyone uses it. Nobody chose it.",
        "wix_excerpt": "Everything you inherited, you can question. I noticed I only ever use two paper formats \u2014 and my daughter taught me why that matters.",
        "first_published": "2026-04-14T22:17:58.988Z",
        "category": "Change it Up",
        "pin_position": 0,
        "wix_old_slug": "letter-size-paper-is-the-40-hour-work-week-everyone-uses-it-nobody-chose-it",
        "content_json": {"blocks":[{"key":"egkmz367","type":"unstyled","text":"My daughter Maddy is 21, has AuDHD, and is frankly one of the most capable humans I've ever met. She could book herself a flight to London, navigate the Tube solo, and find me at my hotel. But some daily-living routines that most of us run on autopilot still need real structure for her. After the rollercoaster of trying everything (IYKYK), we landed on printed 5x7 cards \u2014 her morning routine, emojis and all. Simple. Tactile. Sized for a human.","inlineStyleRanges":[{"style":"{\"FG\":\"rgb(0, 0, 0)\"}","offset":0,"length":447}],"entityRanges":[]},{"key":"gw585369","type":"unstyled","text":"The cards were already in the printer. I didn't feel like switching the paper. So I printed a work doc on them instead.","inlineStyleRanges":[],"entityRanges":[]},{"key":"vsily371","type":"unstyled","text":"That was it. That was the whole awakening.","inlineStyleRanges":[],"entityRanges":[]},{"key":"uxvx3373","type":"unstyled","text":"Suddenly I had a quick, tactile doc I actually wanted to carry around and use. Not file somewhere and forget. The format changed my relationship to the content. I started printing everything that way.","inlineStyleRanges":[],"entityRanges":[]},{"key":"29nus375","type":"unstyled","text":"Then I hit the roadmaps \u2014 systems-level, visual, text-heavy. The 5x7 card wasn't the move. Letter-size was cramped and miserable. I grabbed some 11x17, tried again, and could suddenly see the whole picture at once. No toggling. No mental assembly. Just \u2014 there it is.","inlineStyleRanges":[],"entityRanges":[]},{"key":"emuic377","type":"unstyled","text":"I may have shed a tear. I'm not joking.","inlineStyleRanges":[],"entityRanges":[]},{"key":"di5wc379","type":"unstyled","text":"Turns out there's research behind why this works. Cognitive load theory says the wrong container creates friction before you've thought a single thought. Affordance theory says objects signal how they want to be used \u2014 a card says one thing, briefly, a big sheet says show me everything. Letter-size doesn't say anything. It's just... there. Like the 40-hour week. A compromise that outlived the problem it solved.","inlineStyleRanges":[],"entityRanges":[]},{"key":"byapu381","type":"unstyled","text":"What Maddy keeps showing me \u2014 without trying to \u2014 is that neurodivergent people don't quietly tolerate formats that don't work. They find what actually works, or the gap becomes visible. What we call accommodation is usually just good design that the rest of us were too comfortable to question.","inlineStyleRanges":[],"entityRanges":[]},{"key":"6uiq7383","type":"unstyled","text":"Try the big paper. Try the cards.","inlineStyleRanges":[],"entityRanges":[]},{"key":"gxp2g552","type":"unstyled","text":"Notice what the format is doing to your thinking before you blame your focus.","inlineStyleRanges":[],"entityRanges":[]},{"key":"5eugk385","type":"unstyled","text":"And if you're asking these questions \u2014 you're already ahead.","inlineStyleRanges":[],"entityRanges":[]},{"key":"5jb4p387","type":"unstyled","text":"\u2014 J.","inlineStyleRanges":[],"entityRanges":[]}],"entityMap":{}},
    },
    {
        "wix_title": "F'IT to Begin: Vision to reckoning, and building something that lasts.",
        "wix_excerpt": "Born out of the moment I stripped every layer off my body, slipped into the cold rushing water, and felt my entire being come alive \u2014 F'IT became a way to start sharing with the world a different path.",
        "first_published": "2026-04-13T15:50:42.616Z",
        "category": "Foundation First",
        "pin_position": 2,
        "wix_old_slug": "f-it-to-begin-vision-to-reckoning-and-building-something-that-lasts",
        "content_json": {"blocks":[{"key":"v09vp192","type":"unstyled","text":"I thought it was the final outcome of the story\u2026 I didn't know it was actually the beginning. Born out of the moment I stripped every layer off my body, slipped into the cold rushing water, and felt my entire being come alive, F'IT became a way to start sharing with the world a different path \u2014 a whole-person way to be alive\u2026 and real. To say F'IT to the mirrors we judge ourselves by because those aren't us \u2014 they are a manufactured collective of soulless aspirations.","inlineStyleRanges":[],"entityRanges":[]},{"key":"ja5w6194","type":"unstyled","text":"I thought F'IT was it, but true to my ADHD form, it was simply the vision\u2026 the belief. Now it is time to make it real, lasting, scaffolded, strong foundation\u2026 Fortified. Just like what's happening for me, my soul.","inlineStyleRanges":[],"entityRanges":[]},{"key":"dxskv196","type":"unstyled","text":"I knew, after years of performing in every room, in every way, and sometimes thriving on the applause, that it was time to simply enter every facet of life as Jeremy Runge. A person that walks through the reckoning and will join you through it, too.","inlineStyleRanges":[],"entityRanges":[]},{"key":"b74bz198","type":"unstyled","text":"My heart is full, beating hard, and admittedly anxious as I look at the road ahead, sharing the truths and bridging the gaps on the most beautiful rebuild.","inlineStyleRanges":[],"entityRanges":[]}],"entityMap":{}},
    },
    {
        "wix_title": "Team not performing? More metrics.",
        "wix_excerpt": "It's incredible how many organizations and leaders are still trying to define the perfect set of metrics, rules, and rewards to produce next-level performance.",
        "first_published": "2026-04-10T22:02:29.767Z",
        "category": "Real Leadership",
        "pin_position": 0,
        "wix_old_slug": "team-not-performing-more-metrics",
        "content_json": {"blocks":[{"key":"ember1453","type":"unstyled","text":"It's incredible how many organizations and leaders are still trying to define the perfect set of metrics, rules, and rewards to produce next-level performance.","inlineStyleRanges":[],"entityRanges":[]},{"key":"1pn0e962","type":"unstyled","text":"What's even more incredible is how many times this continues to fail, yet we try and try again.","inlineStyleRanges":[],"entityRanges":[]},{"key":"0kekb95","type":"unordered-list-item","text":"Interviewing for a job. It's a definite question.","inlineStyleRanges":[],"entityRanges":[]},{"key":"nqxoy98","type":"unordered-list-item","text":"Asked for organizational advice. It comes up quickly.","inlineStyleRanges":[],"entityRanges":[]},{"key":"a6j7z101","type":"unordered-list-item","text":"And yes, I've made the mistake myself.","inlineStyleRanges":[],"entityRanges":[]},{"key":"ember1456","type":"unstyled","text":"Yet, it is well-documented that this rarely works, particularly in the type of complex work many of us do today.","inlineStyleRanges":[],"entityRanges":[]},{"key":"i5kmm334","type":"unstyled","text":"I have seen plenty of examples over the years of how this approach can degrade culture, reduce motivation, and drive behaviors that hurt the business. Yet, we still return to it. Why?","inlineStyleRanges":[],"entityRanges":[]},{"key":"i4kdo368","type":"unstyled","text":"Because people are complicated, and leading by posting that red, yellow, green scorecard is easier. But, the hard truth is this:","inlineStyleRanges":[],"entityRanges":[]},{"key":"c4pui402","type":"unstyled","text":"The employee dashboard often reflects the quality of leadership, not the quality of the team.","inlineStyleRanges":[{"style":"BOLD","offset":0,"length":93}],"entityRanges":[]},{"key":"2lih4436","type":"unstyled","text":"Positively guiding the direction of the company and coaching individuals on how to best deliver to that guidance is the responsibility of leadership.","inlineStyleRanges":[],"entityRanges":[]},{"key":"u6rh2470","type":"unstyled","text":"Working around that model might make results look good for a quarter, even two, but watch it over time... the truth has always and will always show up... it will fail.","inlineStyleRanges":[],"entityRanges":[]},{"key":"bgxa9504","type":"unstyled","text":"When I work with leaders on this, what is most interesting, is that they all WANT to be stronger coaches for their teams, not the metrics manager.","inlineStyleRanges":[],"entityRanges":[]},{"key":"0h0ak243","type":"unstyled","text":"So why isn't this the way they DO lead?","inlineStyleRanges":[{"style":"BOLD","offset":0,"length":39},{"style":"ITALIC","offset":0,"length":39}],"entityRanges":[]},{"key":"hts23539","type":"unstyled","text":"Time. Leaders consistently speak of needing more time to connect with (earn the right) and coach (exemplify and teach) each individual on their team.","inlineStyleRanges":[{"style":"BOLD","offset":0,"length":4}],"entityRanges":[]},{"key":"id6pi574","type":"unstyled","text":"Executive Expectations. Many leaders feel pressure to prove they are managing people to the numbers (and numbers = winning). Coaching is harder to track and feels like it takes longer to get results.","inlineStyleRanges":[{"style":"BOLD","offset":0,"length":22}],"entityRanges":[]},{"key":"uo81y609","type":"unstyled","text":"Capability. Many leaders need to be taught how to lead differently than they were led.","inlineStyleRanges":[{"style":"BOLD","offset":0,"length":10}],"entityRanges":[]},{"key":"ek6ll644","type":"unstyled","text":"Connecting data to a person's capabilities, and guiding them to improve without having a psychology degree is a real leadership skill. It needs taught, practiced, and refined before becoming innate.","inlineStyleRanges":[],"entityRanges":[]},{"key":"s1jon678","type":"unstyled","text":"This is now the calling of organizations that want to be considered the greats. To do so they will need to solve for:","inlineStyleRanges":[{"style":"BOLD","offset":0,"length":80}],"entityRanges":[]},{"key":"16t2e712","type":"unstyled","text":"Leader bandwidth. In increasingly competitive landscapes, providing critical coaching time.","inlineStyleRanges":[{"style":"BOLD","offset":0,"length":16}],"entityRanges":[]},{"key":"bw3hl781","type":"unstyled","text":"Organizational culture. With finance teams more and more in the driver's seat, CEOs and COOs have to work harder to separate financial performance from individual aptitude.","inlineStyleRanges":[{"style":"BOLD","offset":0,"length":22}],"entityRanges":[]},{"key":"betri817","type":"unstyled","text":"Training (everyone's favorite). Resources being scarce, smartly investing in the leadership capability of diagnosing metrics and shifting their own behaviors to improve individual and collective performance of the team.","inlineStyleRanges":[{"style":"BOLD","offset":0,"length":8}],"entityRanges":[]},{"key":"1898n853","type":"unstyled","text":"In a world enabled by automation, the uniquely human work of leadership is all the more critical.","inlineStyleRanges":[{"style":"BOLD","offset":0,"length":97}],"entityRanges":[]},{"key":"9sppo889","type":"unstyled","text":"Consider how you are leading or being led in your work today.","inlineStyleRanges":[],"entityRanges":[]},{"key":"4zyw3924","type":"unstyled","text":"Are we truly using data and skill to coach people to be at their best, or are we just adding more metrics? The choice defines leadership.","inlineStyleRanges":[],"entityRanges":[]},{"key":"emex2959","type":"unstyled","text":"I'm excited to see who will take the lead.","inlineStyleRanges":[],"entityRanges":[]}],"entityMap":{}},
    },
    {
        "wix_title": "All you built now rubble? Perfect. Rebuild your best yet.",
        "wix_excerpt": "Those who rise are often the ones that do something truly great. You are not diminished by the rejection. You are emboldened.",
        "first_published": "2026-04-08T22:54:51.468Z",
        "category": "Foundation First",
        "pin_position": 0,
        "wix_old_slug": "all-you-built-now-rubble-perfect-rebuild-your-best-yet",
        "content_json": {"blocks":[{"key":"p1","type":"unstyled","text":"Can you relate?","inlineStyleRanges":[],"entityRanges":[]},{"key":"p2","type":"unstyled","text":"You started strong.","inlineStyleRanges":[],"entityRanges":[]},{"key":"p3","type":"unstyled","text":"Learned who you are. What you're made of. What you stand for.","inlineStyleRanges":[],"entityRanges":[]},{"key":"p4","type":"unstyled","text":"You reached new horizons. Built the future with the best.","inlineStyleRanges":[],"entityRanges":[]},{"key":"p5","type":"unstyled","text":"But the rug got pulled. And the leap became the great fall.","inlineStyleRanges":[],"entityRanges":[]},{"key":"p6","type":"unstyled","text":"It happens.","inlineStyleRanges":[],"entityRanges":[]},{"key":"p7","type":"unstyled","text":"My friend: Do not lower your standards. Raise them.","inlineStyleRanges":[],"entityRanges":[]},{"key":"p8","type":"unstyled","text":"You are not diminished by the rejection. You are emboldened.","inlineStyleRanges":[],"entityRanges":[]},{"key":"p9","type":"unstyled","text":"Not every culture is ready for what you bring. You now know that.","inlineStyleRanges":[],"entityRanges":[]},{"key":"p10","type":"unstyled","text":"Do not give up. Your work is not done.","inlineStyleRanges":[],"entityRanges":[]},{"key":"p11","type":"unstyled","text":"See the light. Refocus. Recalibrate. Lean on another. But move.","inlineStyleRanges":[],"entityRanges":[]},{"key":"p12","type":"unstyled","text":"Now, rebuild. Foundation to studs. Wiring to walls. Whatever it takes.","inlineStyleRanges":[],"entityRanges":[]},{"key":"p13","type":"unstyled","text":"Those who rise are often the ones that do something truly great.","inlineStyleRanges":[],"entityRanges":[]},{"key":"p14","type":"unstyled","text":"This is you.","inlineStyleRanges":[],"entityRanges":[]},{"key":"p15","type":"unstyled","text":"Rise.","inlineStyleRanges":[],"entityRanges":[]}],"entityMap":{}},
    },
    {
        "wix_title": "Note to self \u2014 Remove the layers",
        "wix_excerpt": "You fight to keep the layers. Those pieces that protect your heart. Keep you warm. Feeling safe. But some layers need to come off.",
        "first_published": "2026-04-08T22:54:29.016Z",
        "category": "Change it Up",
        "pin_position": 0,
        "wix_old_slug": "note-to-self-remove-the-layers",
        "content_json": {"blocks":[{"key":"p1","type":"unstyled","text":"Note to self...","inlineStyleRanges":[],"entityRanges":[]},{"key":"p2","type":"unstyled","text":"Remove the layers","inlineStyleRanges":[],"entityRanges":[]},{"key":"p3","type":"unstyled","text":"You fight to keep the layers","inlineStyleRanges":[],"entityRanges":[]},{"key":"p4","type":"unstyled","text":"Those pieces that protect your heart","inlineStyleRanges":[],"entityRanges":[]},{"key":"p5","type":"unstyled","text":"Keep you warm","inlineStyleRanges":[],"entityRanges":[]},{"key":"p6","type":"unstyled","text":"Feeling safe","inlineStyleRanges":[],"entityRanges":[]},{"key":"p7","type":"unstyled","text":"But some layers need to come off","inlineStyleRanges":[],"entityRanges":[]},{"key":"p8","type":"unstyled","text":"So the real you can breathe","inlineStyleRanges":[],"entityRanges":[]},{"key":"p9","type":"unstyled","text":"(but shackets are cool)","inlineStyleRanges":[],"entityRanges":[]},{"key":"p10","type":"unstyled","text":"Love","inlineStyleRanges":[],"entityRanges":[]}],"entityMap":{}},
    },
    {
        "wix_title": "Note to self \u2014 Each circle leads to the next",
        "wix_excerpt": "Each circle leads to the next before ever fully closing. The space between what was and what will be.",
        "first_published": "2026-04-08T22:54:13.222Z",
        "category": "On Healing",
        "pin_position": 0,
        "wix_old_slug": "note-to-self-each-circle-leads-to-the-next",
        "content_json": {"blocks":[{"key":"p1","type":"unstyled","text":"Note to self...","inlineStyleRanges":[],"entityRanges":[]},{"key":"p2","type":"unstyled","text":"Each circle leads to the next before ever fully closing","inlineStyleRanges":[],"entityRanges":[]},{"key":"p3","type":"unstyled","text":"The space between what was","inlineStyleRanges":[],"entityRanges":[]},{"key":"p4","type":"unstyled","text":"What will be","inlineStyleRanges":[],"entityRanges":[]},{"key":"p5","type":"unstyled","text":"The first incomplete","inlineStyleRanges":[],"entityRanges":[]},{"key":"p6","type":"unstyled","text":"The second a blank canvas","inlineStyleRanges":[],"entityRanges":[]},{"key":"p7","type":"unstyled","text":"Both beautiful","inlineStyleRanges":[],"entityRanges":[]},{"key":"p8","type":"unstyled","text":"Love","inlineStyleRanges":[],"entityRanges":[]}],"entityMap":{}},
    },
    {
        "wix_title": "Note to self \u2014 Yosemite's glory remains",
        "wix_excerpt": "When the glass is already shattered, even the tiniest grain sends the shards crashing. So we hold on so tightly. Yosemite teaches you to let go.",
        "first_published": "2026-04-08T22:53:59.908Z",
        "category": "On Nature",
        "pin_position": 0,
        "wix_old_slug": "note-to-self-yosemite-s-glory-remains",
        "content_json": {"blocks":[{"key":"p1","type":"unstyled","text":"Note to self...","inlineStyleRanges":[],"entityRanges":[]},{"key":"p2","type":"unstyled","text":"Yosemite's glory remains","inlineStyleRanges":[],"entityRanges":[]},{"key":"p3","type":"unstyled","text":"When the glass is already shattered","inlineStyleRanges":[],"entityRanges":[]},{"key":"p4","type":"unstyled","text":"Even the tiniest grain","inlineStyleRanges":[],"entityRanges":[]},{"key":"p5","type":"unstyled","text":"Sends the shards crashing","inlineStyleRanges":[],"entityRanges":[]},{"key":"p6","type":"unstyled","text":"So we hold on so tightly","inlineStyleRanges":[],"entityRanges":[]},{"key":"p7","type":"unstyled","text":"But Yosemite's glory remains","inlineStyleRanges":[],"entityRanges":[]},{"key":"p8","type":"unstyled","text":"Whether you hold on or let go","inlineStyleRanges":[],"entityRanges":[]},{"key":"p9","type":"unstyled","text":"Love","inlineStyleRanges":[],"entityRanges":[]}],"entityMap":{}},
    },
    {
        "wix_title": "Note to self \u2014 The Grand Canyon, Ooh Aah",
        "wix_excerpt": "Coming back to the heart, the core, home. Stories speak of this over the ages, across religions and cultures. The Grand Canyon shows you what that means.",
        "first_published": "2026-04-08T22:53:45.613Z",
        "category": "On Nature",
        "pin_position": 0,
        "wix_old_slug": "note-to-self-the-grand-canyon-ooh-aah",
        "content_json": {"blocks":[{"key":"p1","type":"unstyled","text":"Note to self...","inlineStyleRanges":[],"entityRanges":[]},{"key":"p2","type":"unstyled","text":"The Grand Canyon... Ooh Aah","inlineStyleRanges":[],"entityRanges":[]},{"key":"p3","type":"unstyled","text":"Coming back to the heart, the core, home","inlineStyleRanges":[],"entityRanges":[]},{"key":"p4","type":"unstyled","text":"Stories speak of this over the ages","inlineStyleRanges":[],"entityRanges":[]},{"key":"p5","type":"unstyled","text":"Across religions and cultures","inlineStyleRanges":[],"entityRanges":[]},{"key":"p6","type":"unstyled","text":"The return to what matters most","inlineStyleRanges":[],"entityRanges":[]},{"key":"p7","type":"unstyled","text":"Love","inlineStyleRanges":[],"entityRanges":[]}],"entityMap":{}},
    },
    {
        "wix_title": "Note to self \u2014 Own your natural beautiful",
        "wix_excerpt": "The choice we face every day. Does the fear decide the way? Or is this a time to experiment and let play, fun, and your natural beautiful lead?",
        "first_published": "2026-04-08T22:53:31.988Z",
        "category": "On Love",
        "pin_position": 0,
        "wix_old_slug": "note-to-self-own-your-natural-beautiful",
        "content_json": {"blocks":[{"key":"p1","type":"unstyled","text":"Note to self...","inlineStyleRanges":[],"entityRanges":[]},{"key":"p2","type":"unstyled","text":"Own your natural beautiful","inlineStyleRanges":[],"entityRanges":[]},{"key":"p3","type":"unstyled","text":"The choice we face every day","inlineStyleRanges":[],"entityRanges":[]},{"key":"p4","type":"unstyled","text":"Does the fear decide the way","inlineStyleRanges":[],"entityRanges":[]},{"key":"p5","type":"unstyled","text":"Or is this a time to experiment","inlineStyleRanges":[],"entityRanges":[]},{"key":"p6","type":"unstyled","text":"And let play, fun, and your natural beautiful lead","inlineStyleRanges":[],"entityRanges":[]},{"key":"p7","type":"unstyled","text":"Love","inlineStyleRanges":[],"entityRanges":[]}],"entityMap":{}},
    },
    {
        "wix_title": "Note to self \u2014 Queenstown goofiness",
        "wix_excerpt": "It's actually ok to be a big goofball. A little nerdy. To have the high-pitched giggle and sing sentences in response to things.",
        "first_published": "2026-04-08T22:53:19.047Z",
        "category": "On Joy",
        "pin_position": 0,
        "wix_old_slug": "note-to-self-queenstown-goofiness",
        "content_json": {"blocks":[{"key":"p1","type":"unstyled","text":"Note to self...","inlineStyleRanges":[],"entityRanges":[]},{"key":"p2","type":"unstyled","text":"Queenstown goofiness","inlineStyleRanges":[],"entityRanges":[]},{"key":"p3","type":"unstyled","text":"It's actually ok to be a big goofball","inlineStyleRanges":[],"entityRanges":[]},{"key":"p4","type":"unstyled","text":"A little nerdy","inlineStyleRanges":[],"entityRanges":[]},{"key":"p5","type":"unstyled","text":"To have the high-pitched giggle","inlineStyleRanges":[],"entityRanges":[]},{"key":"p6","type":"unstyled","text":"And sing sentences in response to things","inlineStyleRanges":[],"entityRanges":[]},{"key":"p7","type":"unstyled","text":"The world needs more of your joy","inlineStyleRanges":[],"entityRanges":[]},{"key":"p8","type":"unstyled","text":"Love","inlineStyleRanges":[],"entityRanges":[]}],"entityMap":{}},
    },
    {
        "wix_title": "Note to self \u2014 Learning is a gift",
        "wix_excerpt": "Learning is a gift. The joy shows that you are still there. The you that was gifted to the world. The pain shows that things still matter.",
        "first_published": "2026-04-08T22:53:05.994Z",
        "category": "Work of Being",
        "pin_position": 0,
        "wix_old_slug": "note-to-self-learning-is-a-gift",
        "content_json": {"blocks":[{"key":"p1","type":"unstyled","text":"Note to self...","inlineStyleRanges":[],"entityRanges":[]},{"key":"p2","type":"unstyled","text":"Love","inlineStyleRanges":[],"entityRanges":[]},{"key":"p3","type":"unstyled","text":"Learning, it is all a gift","inlineStyleRanges":[],"entityRanges":[]},{"key":"p4","type":"unstyled","text":"The joy shows that you are still there","inlineStyleRanges":[],"entityRanges":[]},{"key":"p5","type":"unstyled","text":"The you that was gifted to the world","inlineStyleRanges":[],"entityRanges":[]},{"key":"p6","type":"unstyled","text":"The pain shows that things still matter","inlineStyleRanges":[],"entityRanges":[]},{"key":"p7","type":"unstyled","text":"That you still matter","inlineStyleRanges":[],"entityRanges":[]},{"key":"p8","type":"unstyled","text":"Love","inlineStyleRanges":[],"entityRanges":[]}],"entityMap":{}},
    },
    {
        "wix_title": "Note to self \u2014 The grandeur of the canyon",
        "wix_excerpt": "On two rim to rim hikes through the Grand Canyon, I had the honor of helping another. The grandeur of that place teaches you what actually matters.",
        "first_published": "2026-04-08T22:50:23.754Z",
        "category": "On Nature",
        "pin_position": 0,
        "wix_old_slug": "note-to-self-the-grandeur-of-the-canyon",
        "content_json": {"blocks":[{"key":"p1","type":"unstyled","text":"Note to self...","inlineStyleRanges":[],"entityRanges":[]},{"key":"p2","type":"unstyled","text":"The Grandeur of the Canyon","inlineStyleRanges":[],"entityRanges":[]},{"key":"p3","type":"unstyled","text":"On two rim to rim hikes through the Grand Canyon, I had the honor of helping another by carrying more than my share","inlineStyleRanges":[],"entityRanges":[]},{"key":"p4","type":"unstyled","text":"What the canyon teaches you is that the grandeur is not the scenery","inlineStyleRanges":[],"entityRanges":[]},{"key":"p5","type":"unstyled","text":"It's the people you carry and who carry you","inlineStyleRanges":[],"entityRanges":[]},{"key":"p6","type":"unstyled","text":"Love","inlineStyleRanges":[],"entityRanges":[]}],"entityMap":{}},
    },
    {
        "wix_title": "Note to self \u2014 Love prevails",
        "wix_excerpt": "Love prevails. You focused on the work? That's ok. You put up some walls? That's ok too. Real love finds a way.",
        "first_published": "2026-04-08T22:50:08.782Z",
        "category": "On Love",
        "pin_position": 0,
        "wix_old_slug": "note-to-self-love-prevails",
        "content_json": {"blocks":[{"key":"p1","type":"unstyled","text":"Note to self...","inlineStyleRanges":[],"entityRanges":[]},{"key":"p2","type":"unstyled","text":"Love Prevails","inlineStyleRanges":[],"entityRanges":[]},{"key":"p3","type":"unstyled","text":"You focused on the work? That's ok","inlineStyleRanges":[],"entityRanges":[]},{"key":"p4","type":"unstyled","text":"You put up some walls? That's ok, too","inlineStyleRanges":[],"entityRanges":[]},{"key":"p5","type":"unstyled","text":"You shut people out? Real love stays","inlineStyleRanges":[],"entityRanges":[]},{"key":"p6","type":"unstyled","text":"Love prevails","inlineStyleRanges":[],"entityRanges":[]},{"key":"p7","type":"unstyled","text":"Love","inlineStyleRanges":[],"entityRanges":[]}],"entityMap":{}},
    },
    {
        "wix_title": "Note to self \u2014 Love in every season",
        "wix_excerpt": "Love, in every season of life. Flowers bound to bloom. Leaves' red reward of great work. Water's beautiful form falls.",
        "first_published": "2026-04-08T22:49:54.445Z",
        "category": "On Love",
        "pin_position": 0,
        "wix_old_slug": "note-to-self-love-in-every-season",
        "content_json": {"blocks":[{"key":"p1","type":"unstyled","text":"Note to self...","inlineStyleRanges":[],"entityRanges":[]},{"key":"p2","type":"unstyled","text":"Love, in every season of life","inlineStyleRanges":[],"entityRanges":[]},{"key":"p3","type":"unstyled","text":"Flowers bound to bloom","inlineStyleRanges":[],"entityRanges":[]},{"key":"p4","type":"unstyled","text":"Leaves' red reward of great work","inlineStyleRanges":[],"entityRanges":[]},{"key":"p5","type":"unstyled","text":"Water's beautiful form falls","inlineStyleRanges":[],"entityRanges":[]},{"key":"p6","type":"unstyled","text":"Tiniest bud breaks through the cold","inlineStyleRanges":[],"entityRanges":[]},{"key":"p7","type":"unstyled","text":"Love, in every season","inlineStyleRanges":[],"entityRanges":[]},{"key":"p8","type":"unstyled","text":"Love","inlineStyleRanges":[],"entityRanges":[]}],"entityMap":{}},
    },
    {
        "wix_title": "Let the voices in",
        "wix_excerpt": "There's more, better thoughts behind that first one. The first voice, yes, needs heard. Sometimes quick and right. Sometimes keeps you safe.",
        "first_published": "2026-04-08T22:49:41.106Z",
        "category": "On Healing",
        "pin_position": 0,
        "wix_old_slug": "let-the-voices-in",
        "content_json": {"blocks":[{"key":"p1","type":"unstyled","text":"There's more, better thoughts behind that first one","inlineStyleRanges":[],"entityRanges":[]},{"key":"p2","type":"unstyled","text":"The first voice, yes, needs heard","inlineStyleRanges":[],"entityRanges":[]},{"key":"p3","type":"unstyled","text":"Sometimes quick and right","inlineStyleRanges":[],"entityRanges":[]},{"key":"p4","type":"unstyled","text":"Sometimes keeps you safe","inlineStyleRanges":[],"entityRanges":[]},{"key":"p5","type":"unstyled","text":"But the second, third, fourth voice","inlineStyleRanges":[],"entityRanges":[]},{"key":"p6","type":"unstyled","text":"Those are the ones that lead to truth","inlineStyleRanges":[],"entityRanges":[]},{"key":"p7","type":"unstyled","text":"Let the voices in","inlineStyleRanges":[],"entityRanges":[]},{"key":"p8","type":"unstyled","text":"Love","inlineStyleRanges":[],"entityRanges":[]}],"entityMap":{}},
    },
    {
        "wix_title": "Enable and choose",
        "wix_excerpt": "Choose Love. Enable people to live their best lives. Choose wisely what does the same for you.",
        "first_published": "2026-04-08T22:49:25.763Z",
        "category": "On People",
        "pin_position": 0,
        "wix_old_slug": "enable-and-choose",
        "content_json": {"blocks":[{"key":"p1","type":"unstyled","text":"Choose Love","inlineStyleRanges":[],"entityRanges":[]},{"key":"p2","type":"unstyled","text":"Enable people","inlineStyleRanges":[],"entityRanges":[]},{"key":"p3","type":"unstyled","text":"To live their best lives","inlineStyleRanges":[],"entityRanges":[]},{"key":"p4","type":"unstyled","text":"Choose wisely","inlineStyleRanges":[],"entityRanges":[]},{"key":"p5","type":"unstyled","text":"What does the same for you","inlineStyleRanges":[],"entityRanges":[]},{"key":"p6","type":"unstyled","text":"Live it in your","inlineStyleRanges":[],"entityRanges":[]},{"key":"p7","type":"unstyled","text":"Words","inlineStyleRanges":[],"entityRanges":[]},{"key":"p8","type":"unstyled","text":"Actions","inlineStyleRanges":[],"entityRanges":[]},{"key":"p9","type":"unstyled","text":"Beliefs","inlineStyleRanges":[],"entityRanges":[]},{"key":"p10","type":"unstyled","text":"Love","inlineStyleRanges":[],"entityRanges":[]}],"entityMap":{}},
    },
    {
        "wix_title": "Note to self \u2014 Love, oh Love",
        "wix_excerpt": "Love, oh Love. You are a wild one. Ever-changing. Opening new eyes, new doors. Repairing what was broken.",
        "first_published": "2026-04-08T22:49:12.103Z",
        "category": "On Love",
        "pin_position": 0,
        "wix_old_slug": "note-to-self-love-oh-love",
        "content_json": {"blocks":[{"key":"p1","type":"unstyled","text":"Love, oh Love","inlineStyleRanges":[],"entityRanges":[]},{"key":"p2","type":"unstyled","text":"You are a wild one","inlineStyleRanges":[],"entityRanges":[]},{"key":"p3","type":"unstyled","text":"Ever-changing","inlineStyleRanges":[],"entityRanges":[]},{"key":"p4","type":"unstyled","text":"Opening new eyes, new doors","inlineStyleRanges":[],"entityRanges":[]},{"key":"p5","type":"unstyled","text":"Repairing what was broken","inlineStyleRanges":[],"entityRanges":[]},{"key":"p6","type":"unstyled","text":"Fortifying for the road ahead","inlineStyleRanges":[],"entityRanges":[]},{"key":"p7","type":"unstyled","text":"Showing up as the subtle whisper and a shock to the soul","inlineStyleRanges":[],"entityRanges":[]},{"key":"p8","type":"unstyled","text":"You are ever-present, yes","inlineStyleRanges":[],"entityRanges":[]},{"key":"p9","type":"unstyled","text":"Yet so elusive","inlineStyleRanges":[],"entityRanges":[]},{"key":"p10","type":"unstyled","text":"Except when I pause, breathe","inlineStyleRanges":[],"entityRanges":[]},{"key":"p11","type":"unstyled","text":"Becoming aware and open","inlineStyleRanges":[],"entityRanges":[]},{"key":"p12","type":"unstyled","text":"I notice, feel, see","inlineStyleRanges":[],"entityRanges":[]},{"key":"p13","type":"unstyled","text":"You are here, you are here","inlineStyleRanges":[],"entityRanges":[]},{"key":"p14","type":"unstyled","text":"To be accepted as you are","inlineStyleRanges":[],"entityRanges":[]},{"key":"p15","type":"unstyled","text":"Love, oh Love","inlineStyleRanges":[],"entityRanges":[]},{"key":"p16","type":"unstyled","text":"You are a wild one","inlineStyleRanges":[],"entityRanges":[]},{"key":"p17","type":"unstyled","text":"(And, of course, coffee...)","inlineStyleRanges":[],"entityRanges":[]}],"entityMap":{}},
    },
    {
        "wix_title": "Note to self \u2014 Keep the joy, buddy",
        "wix_excerpt": "We the children who were hurt beyond healing. We are still whole. The walls our minds and bodies built protect us from the possibility of pain surprising us again.",
        "first_published": "2026-04-08T22:48:53.679Z",
        "category": "On Healing",
        "pin_position": 0,
        "wix_old_slug": "note-to-self-keep-the-joy-buddy",
        "content_json": {"blocks":[{"key":"p1","type":"unstyled","text":"Note to self...","inlineStyleRanges":[],"entityRanges":[]},{"key":"p2","type":"unstyled","text":"We the children","inlineStyleRanges":[],"entityRanges":[]},{"key":"p3","type":"unstyled","text":"Who were hurt beyond healing","inlineStyleRanges":[],"entityRanges":[]},{"key":"p4","type":"unstyled","text":"We are still whole","inlineStyleRanges":[],"entityRanges":[]},{"key":"p5","type":"unstyled","text":"The walls our minds and bodies built","inlineStyleRanges":[],"entityRanges":[]},{"key":"p6","type":"unstyled","text":"Protect us from the possibility","inlineStyleRanges":[],"entityRanges":[]},{"key":"p7","type":"unstyled","text":"Of pain surprising us again","inlineStyleRanges":[],"entityRanges":[]},{"key":"p8","type":"unstyled","text":"We the children","inlineStyleRanges":[],"entityRanges":[]},{"key":"p9","type":"unstyled","text":"Whose frailty became our strength","inlineStyleRanges":[],"entityRanges":[]},{"key":"p10","type":"unstyled","text":"We are still whole","inlineStyleRanges":[],"entityRanges":[]},{"key":"p11","type":"unstyled","text":"And step by step","inlineStyleRanges":[],"entityRanges":[]},{"key":"p12","type":"unstyled","text":"Learn by learn","inlineStyleRanges":[],"entityRanges":[]},{"key":"p13","type":"unstyled","text":"Love self","inlineStyleRanges":[],"entityRanges":[]},{"key":"p14","type":"unstyled","text":"Love others","inlineStyleRanges":[],"entityRanges":[]},{"key":"p15","type":"unstyled","text":"Let love in","inlineStyleRanges":[],"entityRanges":[]},{"key":"p16","type":"unstyled","text":"We the children","inlineStyleRanges":[],"entityRanges":[]},{"key":"p17","type":"unstyled","text":"Incredible","inlineStyleRanges":[],"entityRanges":[]},{"key":"p18","type":"unstyled","text":"Resilient","inlineStyleRanges":[],"entityRanges":[]},{"key":"p19","type":"unstyled","text":"Beautiful","inlineStyleRanges":[],"entityRanges":[]},{"key":"p20","type":"unstyled","text":"Real","inlineStyleRanges":[],"entityRanges":[]},{"key":"p21","type":"unstyled","text":"Love","inlineStyleRanges":[],"entityRanges":[]}],"entityMap":{}},
    },
    {
        "wix_title": "Walk together into the beautiful unknown",
        "wix_excerpt": "I tried to push it away. The need to be the hero, not the rescued. Silent, distant, inward I traveled.",
        "first_published": "2026-04-08T22:48:34.212Z",
        "category": "On Healing",
        "pin_position": 0,
        "wix_old_slug": "walk-together-into-the-beautiful-unknown",
        "content_json": {"blocks":[{"key":"p1","type":"unstyled","text":"I tried to push it away","inlineStyleRanges":[],"entityRanges":[]},{"key":"p2","type":"unstyled","text":"The need to be the hero, not the rescued","inlineStyleRanges":[],"entityRanges":[]},{"key":"p3","type":"unstyled","text":"Silent, distant, inward I traveled","inlineStyleRanges":[],"entityRanges":[]},{"key":"p4","type":"unstyled","text":"The doorbell kept ringing","inlineStyleRanges":[],"entityRanges":[]},{"key":"p5","type":"unstyled","text":"It was patient but persistent","inlineStyleRanges":[],"entityRanges":[]},{"key":"p6","type":"unstyled","text":"The stories I told myself","inlineStyleRanges":[],"entityRanges":[]},{"key":"p7","type":"unstyled","text":"They didn't break through","inlineStyleRanges":[],"entityRanges":[]},{"key":"p8","type":"unstyled","text":"Another knock, another ring, another ding","inlineStyleRanges":[],"entityRanges":[]},{"key":"p9","type":"unstyled","text":"Giving in, no longer the hero, I said yes","inlineStyleRanges":[],"entityRanges":[]},{"key":"p10","type":"unstyled","text":"You are not broken, you are human","inlineStyleRanges":[],"entityRanges":[]},{"key":"p11","type":"unstyled","text":"Not a glitch, you are who you need","inlineStyleRanges":[],"entityRanges":[]},{"key":"p12","type":"unstyled","text":"Please join us, walk with us, talk with us","inlineStyleRanges":[],"entityRanges":[]},{"key":"p13","type":"unstyled","text":"Let's take this road together","inlineStyleRanges":[],"entityRanges":[]},{"key":"p14","type":"unstyled","text":"And I did, I am","inlineStyleRanges":[],"entityRanges":[]},{"key":"p15","type":"unstyled","text":"Love","inlineStyleRanges":[],"entityRanges":[]}],"entityMap":{}},
    },
    {
        "wix_title": "The power was the empathy",
        "wix_excerpt": "Silence for those who would've been wept for. Blind eye to those who would've been seen. The power was the empathy.",
        "first_published": "2026-04-08T22:48:15.033Z",
        "category": "Real Leadership",
        "pin_position": 3,
        "wix_old_slug": "the-power-was-the-empathy",
        "content_json": {"blocks":[{"key":"p1","type":"unstyled","text":"Silence for those would've been wept for","inlineStyleRanges":[],"entityRanges":[]},{"key":"p2","type":"unstyled","text":"Blind eye to those would've been seen","inlineStyleRanges":[],"entityRanges":[]},{"key":"p3","type":"unstyled","text":"Deaf ear for those would've been heard","inlineStyleRanges":[],"entityRanges":[]},{"key":"p4","type":"unstyled","text":"Arms folded for those would've been embraced","inlineStyleRanges":[],"entityRanges":[]},{"key":"p5","type":"unstyled","text":"The power was the empathy","inlineStyleRanges":[],"entityRanges":[]},{"key":"p6","type":"unstyled","text":"The quiet amongst the screams","inlineStyleRanges":[],"entityRanges":[]},{"key":"p7","type":"unstyled","text":"The power was to feel, see, hear, embrace","inlineStyleRanges":[],"entityRanges":[]},{"key":"p8","type":"unstyled","text":"To know their pain is shared pain","inlineStyleRanges":[],"entityRanges":[]},{"key":"p9","type":"unstyled","text":"Is the world's pain","inlineStyleRanges":[],"entityRanges":[]},{"key":"p10","type":"unstyled","text":"Yet Love seems so distant","inlineStyleRanges":[],"entityRanges":[]},{"key":"p11","type":"unstyled","text":"Seek Love, Speak Love","inlineStyleRanges":[],"entityRanges":[]},{"key":"p12","type":"unstyled","text":"Simply Love","inlineStyleRanges":[],"entityRanges":[]}],"entityMap":{}},
    },
    {
        "wix_title": "Love and discomfort",
        "wix_excerpt": "Karston and my therapist agree on many things. One of them is to seek and thrive in discomfort \u2014 discomfort being the places that push us towards truth.",
        "first_published": "2026-04-08T22:47:58.094Z",
        "category": "Change it Up",
        "pin_position": 0,
        "wix_old_slug": "love-and-discomfort",
        "content_json": {"blocks":[{"key":"p1","type":"unstyled","text":"Karston and my therapist agree on many things","inlineStyleRanges":[],"entityRanges":[]},{"key":"p2","type":"unstyled","text":"One of them is to seek and thrive in discomfort","inlineStyleRanges":[],"entityRanges":[]},{"key":"p3","type":"unstyled","text":"Discomfort being the places that push us towards truth","inlineStyleRanges":[],"entityRanges":[]},{"key":"p4","type":"unstyled","text":"For ourselves, for others, for the world","inlineStyleRanges":[],"entityRanges":[]},{"key":"p5","type":"unstyled","text":"We sit in our places of comfort","inlineStyleRanges":[],"entityRanges":[]},{"key":"p6","type":"unstyled","text":"Where instant judgment is easy","inlineStyleRanges":[],"entityRanges":[]},{"key":"p7","type":"unstyled","text":"Quarterbacking without living","inlineStyleRanges":[],"entityRanges":[]},{"key":"p8","type":"unstyled","text":"Without doing the work","inlineStyleRanges":[],"entityRanges":[]},{"key":"p9","type":"unstyled","text":"Without experiencing the discomfort","inlineStyleRanges":[],"entityRanges":[]},{"key":"p10","type":"unstyled","text":"That may actually lead to more Love","inlineStyleRanges":[],"entityRanges":[]},{"key":"p11","type":"unstyled","text":"Seek, experience, ask, thrive","inlineStyleRanges":[],"entityRanges":[]},{"key":"p12","type":"unstyled","text":"Love","inlineStyleRanges":[],"entityRanges":[]}],"entityMap":{}},
    },
]

# Build manifest
manifest = []

# 1. The Undoing (typed manually, not in Wix)
with open("/home/claude/wix-essays/the-undoing.html") as f:
    undoing_html = f.read()
manifest.append({
    "name": "The Undoing",
    "slug": "the-undoing",
    "category": "Work of Being",
    "published_date": "2026-04-19T12:00:00.000Z",
    "excerpt": "I stepped into the shower as quickly as the water was warming. Hair wet, soap on my face, back in the water. Check, done.",
    "body_html": undoing_html,
    "pin_position": 1,
    "wix_old_slug": None,  # Never published on Wix
})

# 2-22. Wix essays
for essay in WIX_ESSAYS:
    title = essay["wix_title"]
    display_title = strip_prefix(title)
    # Map to canonical display title from JER-169 archive table where applicable
    canonical = DISPLAY_TITLE_MAP.get(display_title) or DISPLAY_TITLE_MAP.get(title) or display_title
    cleaned_blocks = clean_body_blocks(essay["content_json"]["blocks"], title)
    cleaned_content = {"blocks": cleaned_blocks, "entityMap": essay["content_json"].get("entityMap", {})}
    body_html = draftjs_to_html(cleaned_content)
    manifest.append({
        "name": canonical,
        "slug": SLUG_MAP[title],
        "category": essay["category"],
        "published_date": essay["first_published"],
        "excerpt": essay["wix_excerpt"],
        "body_html": body_html,
        "pin_position": essay.get("pin_position", 0),
        "wix_old_slug": essay["wix_old_slug"],
    })

# Save manifest
with open("/home/claude/wix-essays/manifest.json", "w") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

# Quick preflight summary
print(f"Total items: {len(manifest)}")
print()
print("Pinned items:")
for item in manifest:
    if item["pin_position"] > 0:
        print(f"  {item['pin_position']}: {item['name']} ({item['category']})")
print()
print("Items by category:")
cats = {}
for item in manifest:
    cats.setdefault(item["category"], []).append(item["name"])
for cat in ["Work of Being", "Foundation First", "Real Leadership", "Change it Up", "On Healing", "On Love", "On Nature", "On Joy", "On People"]:
    items = cats.get(cat, [])
    print(f"  {cat}: {len(items)}")
    for n in items:
        print(f"    - {n}")
print()
print("Slug -> Old Slug Redirect Map:")
for item in manifest:
    if item["wix_old_slug"]:
        print(f"  /post/{item['wix_old_slug']} -> /writing/{item['slug']}")

# Body HTML sanity checks
print()
print("Body HTML samples (first 3 items):")
for item in manifest[:3]:
    print(f"\n--- {item['name']} ---")
    print(item["body_html"][:500] + ("..." if len(item["body_html"]) > 500 else ""))

# Em dash inventory
print()
print("Em dash inventory in body HTML (per JR rule preserved by default):")
for item in manifest:
    em_count = item["body_html"].count("\u2014")
    if em_count > 0:
        print(f"  {item['name']}: {em_count} em dash{'es' if em_count != 1 else ''}")
